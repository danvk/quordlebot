#!/usr/bin/env python
"""Find best first Quordle guesses."""

import pickle
import time
import sys
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
    maxgain = gains[0][0]
    goodpair = 9.5
    print(f'Max gain for one word: {maxgain}')

    candidates = [(gain, i) for gain, i in gains if gain + maxgain >= goodpair]

    tops = []
    for n, (gain1, guess1) in enumerate(candidates):
        g1str = wordler.guessable[guess1]
        # this = []
        for guess2 in range(len(wordler.guessable)):
            gain = wordler.information_gain2(guess1, guess2)
            tops.append((gain, guess1, guess2))
            # this.append((gain, guess2))
        print(f'Completed {n} / {len(candidates)}: {guess1} {g1str} initial gain {gain1:.2f} @ {time.ctime()}')
        tops.sort(reverse=True)
        tops = tops[:100]
        # this.sort(reverse=True)
        # this = this[:10]
        # print([(wordler.guessable[j], gain) for gain, j in this[:10]])
        for gain, i, j in tops[:40]:
            g1 = wordler.guessable[i]
            g2 = wordler.guessable[j]
            print(f'  {g1} {g2} -> +{gain:.2f} bits')
        sys.stdout.flush()

    # print("\n".join(words))
