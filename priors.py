#!/usr/bin/env python
"""Find best first Quordle guesses."""

import pickle
import multiprocessing
from pathos.multiprocessing import ProcessingPool as Pool
import json
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
    guess1_str = wordler.guessable[guess1]
    best = gains[:20]
    with open(f'priors/{guess1_str}.txt', 'w') as out:
        json.dump({
            wordler.guessable[g2]: gain
            for gain, g1, g2 in best
        }, out)
    return best


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

    guessable = [
        wordler.to_guessable_idx(wordbank_idx)
        for wordbank_idx in wordler.all_wordbank_words()
    ]

    gains = [
        (
            wordler.information_gain(i),
            i
        )
        for i in guessable
    ]

    gains.sort(reverse=True)
    print([(wordler.guessable[i], gain) for gain, i in gains[:10]])
    print([(wordler.guessable[i], gain) for gain, i in gains[-10:]])
    maxgain = gains[0][0]
    # goodpair = 9.5
    print(f'Max gain for one word: {maxgain}')

    candidates = [(gain, i) for gain, i in gains]

    cpus = multiprocessing.cpu_count()
    tops = []
    num_processed = 0
    with Pool(cpus) as pool:
        for chunk in chunks(candidates, cpus):
            chunk_tops = pool.map(
                lambda gi: top_second_guesses(wordler, gi[1], guessable),
                chunk
            )
            flat_tops = flatten(chunk_tops)
            tops += flat_tops
            tops.sort(reverse=True)
            tops = tops[:100]
            num_processed += len(chunk)
            # for gain, guess1 in chunk:
            #     del guessables[guessables.index(guess1)]

            print(f'Completed {num_processed} / {len(candidates)}: {chunk} @ {time.ctime()}')
            for gain, i, j in tops[:40]:
                g1 = wordler.guessable[i]
                g2 = wordler.guessable[j]
                print(f'  {g1} {g2} -> +{gain:.2f} bits')
            sys.stdout.flush()
