#!/usr/bin/env python
"""Find optimal Quordle guesses.

Usage:

    ./quordlebot.py GUESS,..gy.,gy...,.....,...ygy GUESS,...

Finds the plays that maximize information gain.
"""

from collections import Counter
from dataclasses import dataclass
import math
import json
from typing import List, Dict
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


def filter_by_guess_lookup(lookup: Dict[str, Dict[str, str]], words: List[str], guess: Guess) -> List[str]:
    return [word for word in words if lookup[word][guess.word] == guess.result]


def information_gain(lookup: Dict[str, Dict[str, str]], words: List[str], guess: str) -> float:
    base_entropy = math.log2(len(words))
    nexts = Counter(lookup[word][guess] for word in words)
    entropy = sum(n * math.log2(n) for n in nexts.values()) / sum(nexts.values())
    return base_entropy - entropy


if __name__ == "__main__":
    lookup = json.load(open('words/map.json'))
    wordbank = [*lookup.keys()]
    allowed = [*lookup[wordbank[0]].keys()]

    guesses = [g.split(',') for g in sys.argv[1:]]
    words = [wordbank, wordbank, wordbank, wordbank]
    pposs = len(wordbank) ** 4
    for (guess, *results) in guesses:
        assert len(results) == 4
        for i in (0, 1, 2, 3):
            result = results[i]
            if result == 'ggggg':
                # we got it!
                words[i] = None
            elif words[i]:
                words[i] = filter_by_guess_lookup(lookup, words[i], Guess(guess, results[i]))
        counts = [len(w) if w else 1 for w in words]
        poss = math.prod(counts)
        print(guess, counts, poss, math.log2(pposs) - math.log2(poss))
        pposs = poss

    # Always guess a word if we've got it nailed
    for i, quad in enumerate(words):
        if not quad:
            continue
        if len(quad) == 1:
            print(f'Quad {i} must be {quad[0]}')
        elif len(quad) <= 5:
            print(f'Quad {i} is one of {quad}')

    # ignore words that we've already gotten correct
    quads = [w for w in words if w is not None]
    gains = []
    for guess in allowed:
        gain = sum(information_gain(lookup, words, guess) for words in quads)
        gains.append((gain, guess))

    gains.sort(reverse=True)
    print(gains[:10])
    print(gains[-10:])

    # print("\n".join(words))
