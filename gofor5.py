#!/usr/bin/env python
"""Given an opening guess, what are the odds that you fully determine a word?

This is important for getting a five.
"""

from collections import Counter
import pickle
import sys
import time
from typing import Dict

from quordlebot import ResultDict


def groupby(xs, fn):
    out = {}
    for x in xs:
        v = fn(x)
        out.setdefault(v, []).append(x)
    return out


def examine_guess(guess: str, lookup: Dict[str, Dict[str, str]]):
    results = groupby(
        (
            (pattern, solution)
            for solution, guesses in lookup.items()
            for g, pattern in guesses.items()
            if g == guess
        ),
        lambda pair: pair[0]
    )
    for count in 1, 2:
        for pattern, possibilities in results.items():
            if len(possibilities) != count:
                continue
            words = [word for _pat, word in possibilities]
            print(f'  {pattern}: {words}')

    by_count = Counter()
    for pattern, possibilities in results.items():
        n = len(possibilities)
        by_count[n] += n
    for count in sorted([*by_count.keys()]):
        if count > 10:
            break
        print(f'  {count}: {by_count[count]}')


def score_for_opener(lookup: Dict[str, Dict[str, str]], guess: str):
    results = groupby(
        (
            (pattern, solution)
            for solution, guesses in lookup.items()
            for g, pattern in guesses.items()
            if g == guess
        ),
        lambda pair: pair[0]
    )
    score = 0
    for pattern, possibilities in results.items():
        n = len(possibilities)
        if pattern == 'ggggg':
            score += 5
        elif n == 1 or n == 2:
            # one point for a fully-determined word,
            # 0.5 points for each of the two words in a 50/50
            score += 1
    return score


def find_best_opener(lookup: Dict[str, Dict[str, str]]):
    wordbank = [*lookup.keys()]
    allowed = [*lookup[wordbank[0]].keys()]

    scores = []
    for i, guess in enumerate(allowed):
        scores.append((score_for_opener(lookup, guess), guess))
        if i % 100 == 0:
            print(i, guess, time.ctime())
            scores.sort(reverse=True)
            for i, (score, guess) in enumerate(scores[:100]):
                print(f'  {i+1}: {score} {guess}')

    scores.sort(reverse=True)
    for i, (score, guess) in enumerate(scores[:1000]):
        print(f'  {i+1}: {score} {guess}')


if __name__ == "__main__":
    lookup = pickle.load(open("words/map.pickle", "rb"))
    wordbank = [*lookup.keys()]
    allowed = [*lookup[wordbank[0]].keys()]

    if len(sys.argv) >= 2:
        for guess in sys.argv[1:]:
            print(guess + ':')
            examine_guess(guess, lookup)
            print('')

    else:
        # Try them all
        find_best_opener(lookup)
