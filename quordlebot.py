#!/usr/bin/env python
"""Find optimal Quordle guesses.

Usage:

    ./quordlebot.py ANSWER1,ANSWER2,ANSWER3,ANSWER4 GUESS1 GUESS2

Finds the plays that maximize information gain.
"""

from collections import Counter
from dataclasses import dataclass
import math
import pickle
import itertools
from typing import List, Dict, Iterable, Set, Tuple, Union
import sys


@dataclass
class Guess:
    word: str
    """The word that you guessed."""
    result: str
    """Five letters, /(g|y|\.){5}/"""


def result_for_guess(word_str: str, guess_str: str) -> str:
    result = [".", ".", ".", ".", "."]
    word = [*word_str]
    guess = [*guess_str]
    # pass 1: greens
    for i, (w, g) in enumerate(zip(word, guess)):
        if w == g:
            result[i] = "g"
            guess[i] = None
            word[i] = None
    # pass 2: yellows
    for i, g in enumerate(guess):
        if g is None:
            continue
        try:
            j = word.index(g)
            result[i] = "y"
            word[j] = None
        except ValueError:
            pass
    return "".join(result)


def is_valid_for_guess(word: str, guess: Guess) -> bool:
    return result_for_guess(word, guess.word) == guess.result


def is_valid_for_guesses(word: str, guesses: List[Guess]) -> bool:
    return all(is_valid_for_guess(word, guess) for guess in guesses)


def get_valid_solutions(words: List[str], guesses: List[Guess]) -> List[str]:
    return [word for word in words if is_valid_for_guesses(word, guesses)]


def filter_by_guess(words: List[str], guess: Guess) -> List[str]:
    return [word for word in words if is_valid_for_guess(word, guess)]


def filter_by_guess_lookup(
    lookup: Dict[str, Dict[str, str]], words: List[str], guess: Guess
) -> List[str]:
    return [word for word in words if lookup[word][guess.word] == guess.result]


def build_lookup(wordbank: List[str], allowed: List[str]) -> Dict[str, Dict[str, str]]:
    out = {}
    combined = [*sorted([*wordbank, *allowed])]
    for word in enumerate(wordbank):
        out[word] = {}
        for guess in combined:
            out[word][guess] = result_for_guess(word, guess)
    return out


def information_gain(
    lookup: Dict[str, Dict[str, str]], words: List[str], guess: str
) -> float:
    base_entropy = math.log2(len(words))
    nexts = Counter(lookup[word][guess] for word in words)
    entropy = sum(n * math.log2(n) for n in nexts.values()) / sum(nexts.values())
    return base_entropy - entropy


def encode_result(result: str) -> int:
    out = 0
    for char in result:
        out *= 4
        if char == "y":
            out += 1
        elif char == "g":
            out += 2
        elif char == ".":
            pass
        else:
            raise ValueError(f"Invalid char {char} in result: {result}")
    return out


def decode_result(result: int) -> str:
    out = [".", ".", ".", ".", "."]
    i = 4
    while result:
        x = result % 4
        if x == 1:
            out[i] = "y"
        elif x == 2:
            out[i] = "g"
        elif x == 0:
            pass
        else:
            raise ValueError(f"Invalid encoded result: {result}")
        i -= 1
        result //= 4
    return "".join(out)


@dataclass
class ResultDict:
    wordbank: List[str]
    guessable: List[str]
    results: List[List[int]]


class ArrayWordle:
    wordbank: List[str]
    guessable: List[str]
    results: List[List[int]]

    def __init__(self, result_dict: ResultDict):
        self.wordbank = result_dict.wordbank
        self.guessable = result_dict.guessable
        self.results = result_dict.results
        self.wordbank_to_idx = {word: i for i, word in enumerate(self.wordbank)}
        self.guessable_to_idx = {word: i for i, word in enumerate(self.guessable)}

    def all_wordbank_words(self):
        return [*range(len(self.wordbank))]

    def information_gain(self, guess: int) -> List[int]:
        base_entropy = math.log2(len(self.wordbank))
        nexts = Counter(result[guess] for result in self.results)
        entropy = sum(n * math.log2(n) for n in nexts.values()) / sum(nexts.values())
        return base_entropy - entropy

    def information_gain2(self, guess1: int, guess2: int) -> List[int]:
        num = len(self.wordbank)
        base_entropy = math.log2(num)
        nexts = Counter(
            result[guess1] * 65536 + result[guess2] for result in self.results
        )
        entropy = sum(n * math.log2(n) for n in nexts.values()) / num
        return base_entropy - entropy

    def filter_by_guess(self, candidates: Iterable[int], guess: int, solution: int) -> List[int]:
        """Filter a set of candidate words based on a guess and the solution."""
        result = self.results[solution][guess]
        return [
            i
            for i in candidates
            if self.results[i][guess] == result
        ]

    def information_gain_for_play(self, candidates: List[int], guess: int) -> float:
        base_entropy = math.log2(len(candidates))
        nexts = Counter(self.results[word][guess] for word in candidates)
        entropy = sum(n * math.log2(n) for n in nexts.values()) / sum(nexts.values())
        return base_entropy - entropy

    def to_guessable_idx(self, wordbank_idx):
        return self.guessable_to_idx[self.wordbank[wordbank_idx]]


# TODO(danvk): figure out how to type this generically
def groupby(xs, fn):
    out = {}
    for x in xs:
        v = fn(x)
        out.setdefault(v, []).append(x)
    return out


DEBUG = False
max_depth = 0


def expected_plays_for_guess(
    lookup: Dict[str, Dict[str, str]], quads: List[List[str]], guess: str, bail_bad: bool, depth=0
) -> Union[float, None]:
    """Return the number of expected plays to win _after_ this guess."""
    if DEBUG:
        print('  ' * depth, 'expected_plays_for_guess', quads, guess, bail_bad)

    global max_depth
    if depth > max_depth:
        max_depth = depth
        print(f'new max depth: {max_depth} for guess {guess}')

    # group the remaining quads by what this guess would produce
    groups = []
    poss = 1
    for quad in quads:
        # assert len(quad) > 1
        g = groupby(quad, lambda word: lookup[word][guess])
        if DEBUG:
            print('  ' * depth, g)
        poss *= len(g)
        groups.append([*g.values()])
    # print(groups)

    if bail_bad and poss == 1 and not(any(quad == [guess] for quad in quads)):
        # This was a bad guess; bail out
        # print(f'Bailing on bad guess: {guess} {groups}')
        if DEBUG:
            print('  ' * depth, '--> None (bail_bad)')
        return None

    # print(f'Considering guess: {guess} {groups}')

    # print(groups)
    # form a weighted average of steps to solve
    num = 0.0
    den = 0
    for new_quads in itertools.product(*groups):
        # print(new_quads)
        num_for_this = math.prod(len(q) for q in new_quads)
        if any(quad == [guess] for quad in new_quads):
            # As a special case, if we guessed right, then remove this quad from the recursion.
            nnq = [quad for quad in new_quads if quad != [guess]]
            # print(f'{new_quads} --> {nnq}')
            new_quads = nnq

        # This isn't quite right, there must be some correlation between new_quads
        # print('possible quad', new_quads)
        next_guesses = find_best_plays(lookup, new_quads, depth=1+depth, num_needed=1)
        guesses_needed = next_guesses[0][0]
        # print(f'  {guesses_needed:.2f} {new_quads}')
        num += guesses_needed * num_for_this
        den += num_for_this
    if DEBUG:
        print('  ' * depth, f'--> {num} / {den} = {num / den}')
    return num / den


def find_best_plays(
    lookup: Dict[str, Dict[str, str]], quads: List[List[str]], depth=0, num_needed=10
) -> List[Tuple[float, str]]:
    """Return the best next plays based on expected of remaining plays."""
    if DEBUG:
        print('  ' * depth, f'find_best_plays {quads}')
    if not quads:
        return [(0, '')]  # we won!

    # if any quad is fully-determined, guess that
    for i, quad in enumerate(quads):
        if len(quad) == 1:
            guess = quad[0]
            others = [q for j, q in enumerate(quads) if i != j]
            if not others:
                # we're done!
                return [(1, guess)]

            return [(1 + expected_plays_for_guess(lookup, others, guess, bail_bad=False, depth=1+depth), guess)]

    # Try everything
    # TODO: only keep the best one if num_needed=1
    # TODO: pass along a max depth option to bail out
    wordbank = [*lookup.keys()]
    allowed = [*lookup[wordbank[0]].keys()]

    # Only consider words that gain information
    by_gain = []
    for guess in allowed:
        gain = sum(information_gain(lookup, words, guess) for words in quads)
        if gain > 0:
            by_gain.append((gain, guess))
    by_gain.sort(reverse=True)
    reasonable = [guess for gain, guess in by_gain]

    plays = []
    for i, guess in enumerate(reasonable):
        n = expected_plays_for_guess(lookup, quads, guess, bail_bad=True, depth=1+depth)
        if depth == 0:
            print(f'{i} / {len(reasonable)}: {guess} --> {n} plays to win')
        plays.append((n, guess))

    plays = [(1+n, guess) for n, guess in plays if n is not None]
    plays.sort()
    return plays[:num_needed]


def expected_plays_after_guess(
    lookup: Dict[str, Dict[str, str]],
    quads: List[List[str]],
    guess: str,
    *,
    depth=0
) -> float:
    """After guessing guess, how many additional plays do we expect to need?

    Precondition: len(quads) > 0, none of the quads should be fully-determined.
    """
    # group the remaining quads by what this guess would produce
    # for q in quads:
    #    if len(q) <= 1:
    #        assert len(q) > 1

    if depth > 20:
        # This isn't exactly right but is quite effective!
        return 100

    if DEBUG:
        sp = ' ' * depth
        print(f'{sp}expected_plays_after_guess {guess}')

    # TODO: special case the situation where this was definitely a correct guess?
    #       In this case we can eliminate the itertools.product.
    for quad in quads:
        if len(quad) == 1 and quad[0] == guess:
            other_quads = [q for q in quads if q != quad]
            return expected_plays_after_guess(lookup, other_quads, guess, depth=depth)

    groups: List[List[List[str]]] = []
    for quad in quads:
        g: Dict[str, List[str]] = groupby(quad, lambda word: lookup[word][guess])
        groups.append([*g.values()])

    nums: List[float] = []
    dens: List[int] = []
    new_quads: List[List[str]]
    for new_quads in itertools.product(*groups):
        # This is one possible set of quads after playing guess.
        if any(quad == [guess] for quad in new_quads):
            # As a special case, if we guessed right, then remove this quad from the recursion.
            new_quads = [q for q in new_quads if q != [guess]]

        additional_plays, _ = find_best_play(lookup, new_quads, depth=1+depth)
        num = additional_plays
        den = math.prod(len(q) for q in new_quads)
        nums.append(num)
        dens.append(den)
        if DEBUG:
            print(f'{sp}+ {num} / {den} {new_quads}')

    # weighted average
    return sum(num * den for num, den in zip(nums, dens)) / sum(dens)


def find_best_play(
    lookup: Dict[str, Dict[str, str]], quads: List[List[str]], *, depth=0
) -> Tuple[float, str]:
    """Find the single best play based on expected number of plays.

    Returns (expected plays, best next play)
    """
    # 0. Base case -- no words left to guess means we win.
    if not quads:
        return 0, ''

    global max_depth
    if depth > max_depth:
        max_depth = depth
        print(f'New max depth {depth}')
    sp = ' ' * depth

    # 0.5. If all words are fully determined, we're done.
    if all(len(q) == 1 for q in quads):
        if DEBUG:
            print(f'{sp}find_best_play({len(lookup)}, {quads}) -> {len(quads)}, {quads[0][0]} (all determined)')
        return len(quads), quads[0][0]

    # 1. Always play a fully-determined word.
    for i, quad in enumerate(quads):
        if len(quad) == 1:
            guess = quad[0]
            other_quads = [q for j, q in enumerate(quads) if i != j]
            remaining_plays = expected_plays_after_guess(lookup, other_quads, guess, depth=1+depth)
            return 1 + remaining_plays, guess

    # print(f'{sp}find_best_play({len(lookup)}, {[len(q) for q in quads]})')

    # 1.5. With exactly two words left, the expected number of plays is 1.5.
    if len(quads) == 1 and len(quads[0]) == 2:
        if DEBUG:
            print(f'{sp}find_best_play({len(lookup)}, {quads}) -> 1.5, {quads[0][0]} (two case)')
        return 1.5, quads[0][0]

    if DEBUG:
        print(f'{sp}find_best_play({len(lookup)}, {quads})')

    # 2. Try playing each of the possible words.
    #    If the best expected plays < 1 + len(quads), then we're done.
    possible_words = {word for quad in sorted(quads, key=lambda q: len(q)) for word in quad}
    m = min(len(q) for q in quads)
    best_possible = len(quads) + (m - 1) / m
    # XXX constructing this explicitly may not be necessary
    restricted_lookup = filter_lookup(lookup, possible_words)
    restricted_plays, restricted_guess = 1000, None
    for i, guess in enumerate(possible_words):
        plays = 1 + expected_plays_after_guess(restricted_lookup, quads, guess, depth=1+depth)
        if plays < restricted_plays:
            restricted_plays = plays
            restricted_guess = guess
            if plays <= best_possible:
                # print(f'{sp}-> bailing after {1 + i} / {len(possible_words)} on restricted search')
                break

    if restricted_plays <= 1 + len(quads):
        if DEBUG or depth == 0:
            print(f'{sp}-> Restricted search yields {restricted_plays}, {restricted_guess}')
        return restricted_plays, restricted_guess
    if DEBUG or depth == 0:
        print(f'{sp}- Restricted check failed; best was {restricted_plays}, {restricted_guess} for {quads}')

    # 3. Try all possible plays ordered by IG; only consider the top 100.
    by_gain: List[Tuple[float, str]] = []
    for guess in lookup.keys():
        if guess in possible_words:
            continue  # already covered this in step 2.
        gain = sum(information_gain(lookup, words, guess) for words in quads)
        if gain > 0:
            by_gain.append((gain, guess))
    by_gain.sort(reverse=True)

    n = min(len(by_gain), 100)
    best_plays, best_word = restricted_plays, restricted_guess
    for i, (gain, guess) in enumerate(by_gain[:100]):
        num = 1 + expected_plays_after_guess(lookup, quads, guess, depth=1+depth)
        if DEBUG or depth == 0:
            print(f'{sp}- {i} / {n}: {guess} -> {num} plays to win')
        if num < best_plays:
            best_plays = num
            best_word = guess

    if DEBUG:
        print(f'{sp}-> {best_plays}, {best_word}')
    return best_plays, best_word


def filter_lookup(lookup: Dict[str, Dict[str, str]], dictionary: Set[str]) -> Dict[str, Dict[str, str]]:
    """Shrink a lookup table to a fixed dictionary of guesses."""
    return {
        solution: {
            guess: lookup[solution][guess]
            for guess in dictionary
        }
        for solution in dictionary
    }


if __name__ == "__main__":
    # lookup = json.load(open('words/map.json'))
    lookup = pickle.load(open("words/map.pickle", "rb"))
    wordbank = [*lookup.keys()]
    allowed = [*lookup[wordbank[0]].keys()]

    (correct_raw, *guesses) = sys.argv[1:]
    correct = correct_raw.split(",")
    assert len(correct) == 4

    words = [wordbank, wordbank, wordbank, wordbank]
    pposs = len(wordbank) ** 4
    for guess in guesses:
        results = [
            lookup[w][guess] if words[i] is not None else "-----"
            for i, w in enumerate(correct)
        ]
        for i in (0, 1, 2, 3):
            if words[i] is None:
                continue  # already got this one
            result = results[i]
            if result == "ggggg":
                # we got it!
                words[i] = None
            elif words[i]:
                words[i] = filter_by_guess_lookup(
                    lookup, words[i], Guess(guess, results[i])
                )
        counts = [len(w) if w else 1 for w in words]
        poss = math.prod(counts)
        gain = math.log2(pposs) - math.log2(poss)
        print(f'{guess} {"  ".join(results)} -> {counts} = {poss} +{gain:.2f} bits')
        pposs = poss

    # Report fully- or nearly-determined words.
    for i, quad in enumerate(words):
        if not quad:
            continue
        if len(quad) == 1:
            print(f"Quad {i} must be {quad[0]}")
        elif len(quad) <= 10:
            print(f"Quad {i} is one of {quad}")

    quads = [w for w in words if w is not None]
    if poss < 200:
        # with few possibilities, game out remaining guesses
        print('All possibilities: ', quads)
        plays, guess = find_best_play(lookup, quads)
        print("Best play by expected number of steps to complete:")
        print(f"  +{plays:.2f} {guess} ({plays + len(guesses):.2f} total)")
    else:
        # with lots of possibilities, try to maximize information gain
        # ignore words that we've already gotten correct
        gains = []
        for guess in allowed:
            gain = sum(information_gain(lookup, words, guess) for words in quads)
            gains.append((gain, guess))

        print("Best next plays based on expected information gain:")
        gains.sort(reverse=True)
        for gain, word in gains[:10]:
            print(f"  {word} -> +{gain:.2f} bits")
        # print('Words with no information gain: ', len([w for gain, w in gains if gain == 0.0]))
