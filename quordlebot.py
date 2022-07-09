#!/usr/bin/env python
"""Find optimal Quordle guesses.

Usage:

    ./quordlebot.py GUESS,..gy.,gy...,.....,...ygy GUESS,...

Finds the plays that maximize information gain.
"""

from dataclasses import dataclass
from typing import List
from collections import Counter

@dataclass
class Guess:
    word: str
    """The word that you guessed."""
    result: str
    """Five letters, /(g|y|\.){5}/"""


def result_for_guess(word_str: str, guess_str: str) -> str:
    result = ['.', '.', '.', '.', '.']
    word = [*word_str]
    guess = [*guess_str]
    # pass 1: greens
    for i, (w, g) in enumerate(zip(word, guess)):
        if w == g:
            result[i] = 'g'
            guess[i] = None
            word[i] = None
    # pass 2: yellows
    for i, g in enumerate(guess):
        if g is None:
            continue
        try:
            j = word.index(g)
            result[i] = 'y'
            word[j] = None
        except ValueError:
            pass
    return ''.join(result)


def is_valid_for_guess(word: str, guess: Guess) -> bool:
    letters = Counter(word)
    for i, (letter, result) in enumerate(zip(guess.word, guess.result)):
        if result == '.':
            if letter in letters:
                return False
        if result == 'y':
            if letter not in letters or word[i] == letter:
                return False
        if result == 'g':
            if word[i] != letter:
                return False
    # TODO: handle repeat letters
    return True


def find_solutions(words: List[str], guesses: List[Guess]) -> List[str]:
    pass
