#!/usr/bin/env python
"""Find optimal Quordle guesses.

Usage:

    ./quordlebot.py GUESS,..gy.,gy...,.....,...ygy GUESS,...

Finds the plays that maximize information gain.
"""

from collections import Counter
from dataclasses import dataclass
import math
from typing import List
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


def information_gain(words: List[str], guess: str) -> float:
    if guess.endswith('E'):
        print(guess)
    base_entropy = math.log2(len(words))
    nexts = Counter(result_for_guess(word, guess) for word in words)
    entropy = sum(n * math.log2(n) for n in nexts.values()) / sum(nexts.values())
    return base_entropy - entropy


if __name__ == "__main__":
    wordbank = [word.strip() for word in open("words/wordbank.txt")]
    allowed = [word.strip() for word in open("words/allowed.txt")]

    guesses = [g.split(',') for g in sys.argv[1:]]
    words = [wordbank, wordbank, wordbank, wordbank]
    for (guess, *results) in guesses:
        assert len(results) == 4
        for i in (0, 1, 2, 3):
            words[i] = filter_by_guess(words[i], Guess(guess, results[i]))
        print(guess, [len(w) for w in words])

    # print("\n".join(words))
