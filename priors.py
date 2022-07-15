#!/usr/bin/env python
"""Find best first Quordle guesses."""

import pickle
import multiprocessing
from pathos.multiprocessing import ProcessingPool as Pool
import time
import sys
from typing import List, Tuple
from quordlebot import ResultDict, ArrayWordle


def top_second_guesses(wordler: ArrayWordle, guess1: int, guessables: List[int]) -> List[Tuple[float, int, int]]:
    gains = [
        (wordler.information_gain2(guess1, guess2), guess1, guess2)
        for guess2 in guessables
    ]
    gains.sort(reverse=True)
    return gains[:20]


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def flatten(xss):
    return [x for xs in xss for x in xs]


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
    guessables = [*range(len(wordler.guessable))]

    cpus = multiprocessing.cpu_count()
    tops = []
    num_processed = 0
    with Pool(cpus) as pool:
        for chunk in chunks(candidates, cpus):
            chunk_tops = pool.map(
                lambda gi: top_second_guesses(wordler, gi[1], guessables),
                chunk
            )
            flat_tops = flatten(chunk_tops)
            tops += flat_tops
            tops.sort(reverse=True)
            tops = tops[:100]
            num_processed += len(chunk)
            for gain, guess1 in chunk:
                del guessables[guessables.index(guess1)]

            print(f'Completed {num_processed} / {len(candidates)}: {chunk} @ {time.ctime()}')
            for gain, i, j in tops[:40]:
                g1 = wordler.guessable[i]
                g2 = wordler.guessable[j]
                print(f'  {g1} {g2} -> +{gain:.2f} bits')
            sys.stdout.flush()
