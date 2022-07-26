#!/usr/bin/env python
"""Given that you start with ROAST / PRIOR, what's the next best play?

My sense is that most of the time it's HUMID.
And if you guess ROAST / PRIOR / HUMID, how often can you get a guaranteed seven?
"""

import pickle
import random
from quordlebot import ResultDict, ArrayWordle
from typing import List

def roast_cline(four: List[int]) -> List[List[int]]:
    """Possibilities after playing ROAST / CLINE"""
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


if __name__ == '__main__':
    result_dict = pickle.load(open('words/array.pickle', 'rb'))
    wordler = ArrayWordle(result_dict)

    roast = wordler.guessable_to_idx['ROAST']
    cline = wordler.guessable_to_idx['CLINE']
    wordbank = wordler.all_wordbank_words()

    num = 0
    for i in range(1000):
        four = random.choices(wordbank, k=4)
        possibilities = roast_cline(four)
        has_soln = any(len(x) == 1 for x in possibilities)
        print([wordler.wordbank[i] for i in four], has_soln)
        if has_soln:
            num += 1

    print(num)
