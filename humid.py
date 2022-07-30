#!/usr/bin/env python
"""Given that you start with ROAST / PRIOR, what's the next best play?

My sense is that most of the time it's HUMID.
And if you guess ROAST / PRIOR / HUMID, how often can you get a guaranteed seven?
"""

import math
import pickle
import random
from collections import Counter
from quordlebot import ResultDict, ArrayWordle
from typing import List

def roast_cline(wordler, four: List[int]) -> List[List[int]]:
    """Possibilities after playing ROAST / CLINE"""
    wordbank = wordler.all_wordbank_words()
    roast = wordler.guessable_to_idx['ROAST']
    cline = wordler.guessable_to_idx['CLINE']
    candidates1 = [
        wordler.filter_by_guess(wordbank, roast, word)
        for word in four
    ]
    # print([len(quad) for quad in candidates1])

    candidates2 = [
        wordler.filter_by_guess(possibilities, cline, word)
        for word, possibilities in zip(four, candidates1)
    ]
    # print([len(quad) for quad in candidates2])
    return candidates2


def fraction_with_determined_word(wordler):
    """If you open ROAST/CLINE, how often is there a fully-determined word?"""
    wordbank = wordler.all_wordbank_words()

    num = 0
    for i in range(1000):
        four = random.choices(wordbank, k=4)
        possibilities = roast_cline(wordler, four)
        has_soln = any(len(x) == 1 for x in possibilities)
        print([wordler.wordbank[i] for i in four], has_soln)
        if has_soln:
            num += 1

    # It's ~70% of the time.
    print(f'There is a fully-determined word {num / 10:.2}% of the time after opening ROAST/CLINE.')


def next_after_roast(wordler: ArrayWordle):
    """If you open ROAST, what's the best next word to play?"""
    wordbank = wordler.all_wordbank_words()
    roast = wordler.guessable_to_idx['ROAST']

    num = 100
    next_best = Counter()
    for i in range(num):
        four = random.choices(wordbank, k=4)
        candidates = [
            wordler.filter_by_guess(wordbank, roast, word)
            for word in four
        ]
        gains = []
        for guess, guess_str in enumerate(wordler.guessable):
            gain = sum(wordler.information_gain_for_play(words, guess) for words in candidates)
            gains.append((gain, guess_str))

        gains.sort(reverse=True)
        gain, guess_str = max(gains)
        next_best[guess_str] += 1
        cline = next((gain, guess) for gain, guess in gains if guess == 'CLINE')
        print(','.join(wordler.wordbank[i] for i in four), guess_str, gain, cline, gain - cline[0])

    # CLINE is the best next play ~40% of the time
    print('Best next plays after ROAST:')
    for word, freq in next_best.most_common():
        print(f'  {100 * freq / num:.3}%: {word}')


if __name__ == '__main__':
    result_dict = pickle.load(open('words/array.pickle', 'rb'))
    wordler = ArrayWordle(result_dict)

    # fraction_with_determined_word(wordler)
    next_after_roast(wordler)
