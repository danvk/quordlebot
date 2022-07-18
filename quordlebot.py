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
from typing import List, Dict, Tuple, Union
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
        next_guesses = find_best_plays(lookup, new_quads, depth=1+depth)
        guesses_needed = next_guesses[0][0]
        # print(f'  {guesses_needed:.2f} {new_quads}')
        num += guesses_needed * num_for_this
        den += num_for_this
    if DEBUG:
        print('  ' * depth, f'--> {num} / {den} = {num / den}')
    return num / den


def find_best_plays(
    lookup: Dict[str, Dict[str, str]], quads: List[List[str]], depth=0
) -> List[Tuple[float, str]]:
    """Return the bets next plays based on expected of remaining plays."""
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
    wordbank = [*lookup.keys()]
    allowed = [*lookup[wordbank[0]].keys()]
    plays = [
        (expected_plays_for_guess(lookup, quads, guess, bail_bad=True, depth=1+depth), guess) for guess in allowed
    ]

    plays = [(1+n, guess) for n, guess in plays if n is not None]
    plays.sort()
    return plays[:10]


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
        elif len(quad) <= 5:
            print(f"Quad {i} is one of {quad}")

    quads = [w for w in words if w is not None]
    if poss < 200:
        # with few possibilities, game out remaining guesses
        print(quads)
        plays = find_best_plays(lookup, quads)
        print("Best next plays by expected number of steps to complete:")
        for steps, guess in plays:
            print(f"  {steps:.2f} {guess}")
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
