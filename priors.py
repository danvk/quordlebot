#!/usr/bin/env python
"""Find best first Quordle guesses."""

import pickle
from quordlebot import ResultDict, ArrayWordle


if __name__ == "__main__":
    # lookup = pickle.load(open('words/map.pickle', 'rb'))
    result_dict = pickle.load(open('words/array.pickle', 'rb'))
    wordler = ArrayWordle(result_dict)

    gains = [
        (
            wordler.information_gain(i),
            i
        )
        for i in range(len(wordler.guessable))
    ]

    gains.sort(reverse=True)
    print([(wordler.guessable[i], gain) for gain, i in gains[:10]])
    print([(wordler.guessable[i], gain) for gain, i in gains[-10:]])

    # print("\n".join(words))
