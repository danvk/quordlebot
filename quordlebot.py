#!/usr/bin/env python
"""Find optimal Quordle guesses.

Usage:

    ./quordlebot.py GUESS,..gy.,gy...,.....,...ygy GUESS,...

Finds the plays that maximize information gain.
"""

from collections import Counter
from dataclasses import dataclass
import math
import pickle
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


def encode_result(result: str) -> int:
    out = 0
    for char in result:
        out *= 4
        if char == 'y':
            out += 1
        elif char == 'g':
            out += 2
        elif char == '.':
            pass
        else:
            raise ValueError(f'Invalid char {char} in result: {result}')
    return out


def decode_result(result: int) -> str:
    out = ['.', '.', '.', '.', '.']
    i = 4
    while result:
        x = result % 4
        if x == 1:
            out[i] = 'y'
        elif x == 2:
            out[i] = 'g'
        elif x == 0:
            pass
        else:
            raise ValueError(f'Invalid encoded result: {result}')
        i -= 1
        result //= 4
    return ''.join(out)


if __name__ == "__main__":
    # lookup = json.load(open('words/map.json'))
    lookup = pickle.load(open('words/map.pickle', 'rb'))
    wordbank = [*lookup.keys()]
    allowed = [*lookup[wordbank[0]].keys()]

    (correct_raw, *guesses) = sys.argv[1:]
    correct = correct_raw.split(',')
    assert len(correct) == 4

    words = [wordbank, wordbank, wordbank, wordbank]
    pposs = len(wordbank) ** 4
    for guess in guesses:
        results = [lookup[w][guess] for w in correct]
        for i in (0, 1, 2, 3):
            result = results[i]
            if result == 'ggggg':
                # we got it!
                words[i] = None
            elif words[i]:
                words[i] = filter_by_guess_lookup(lookup, words[i], Guess(guess, results[i]))
        counts = [len(w) if w else 1 for w in words]
        poss = math.prod(counts)
        gain = math.log2(pposs) - math.log2(poss)
        print(f'{guess} {results} -> {counts} = {poss} +{gain:.2f} bits')
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
