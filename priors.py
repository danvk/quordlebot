#!/usr/bin/env python
"""Find best first Quordle guesses."""

import pickle
from quordlebot import information_gain


if __name__ == "__main__":
    lookup = pickle.load(open('words/map.pickle', 'rb'))
    wordbank = [*lookup.keys()]
    allowed = [*lookup[wordbank[0]].keys()]
    gains = [(information_gain(lookup, wordbank, guess), guess) for guess in allowed]

    gains.sort(reverse=True)
    print(gains[:10])
    print(gains[-10:])

    # print("\n".join(words))
