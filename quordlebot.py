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

    gains = [(information_gain(wordbank, guess), guess) for guess in allowed]
    gains.sort(reverse=True)
    print(gains[:10])
    print(gains[-10:])

    # guesses_str = sys.argv[1:]
    # guesses = [
    #     Guess(guess.split(",")[0], guess.split(",")[1])
    #     for guess in guesses_str
    # ]
    # words = get_valid_solutions(wordbank, guesses)

    # print("\n".join(words))
