#!/usr/bin/env python

from collections import Counter
import pickle
import sys
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


if __name__ == "__main__":
    lookup = pickle.load(open("words/map.pickle", "rb"))
    wordbank = [*lookup.keys()]
    allowed = [*lookup[wordbank[0]].keys()]

    for guess in sys.argv[1:]:
        print(guess + ':')
        examine_guess(guess, lookup)
        print('')
