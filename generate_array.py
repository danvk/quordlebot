#!/usr/bin/env python

from dataclasses import dataclass
from typing import List
import pickle

from quordlebot import encode_result


@dataclass
class ResultDict:
    wordbank: List[str]
    guessable: List[str]
    results: List[List[int]]


if __name__ == '__main__':
    lookup = pickle.load(open('words/map.pickle', 'rb'))
    wordbank = [*lookup.keys()]
    allowed = [*lookup[wordbank[0]].keys()]

    results = [
        [
            encode_result(lookup[word][guess])
            for guess in allowed
        ]
        for word in wordbank
    ]

    out = ResultDict(wordbank=wordbank, guessable=allowed, results=results)
    with open('words/array.pickle', 'wb') as out_file:
        pickle.dump(out, out_file)
