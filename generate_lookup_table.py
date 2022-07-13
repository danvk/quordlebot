#!/usr/bin/env python
"""Generate a word pair -> green/yellow mapping."""

from quordlebot import result_for_guess
import json
import pickle

if __name__ == "__main__":
    wordbank = [word.strip() for word in open("words/wordbank.txt")]
    allowed = [word.strip() for word in open("words/allowed.txt")]
    combined = [*sorted([*wordbank, *allowed])]
    print('wordbank: ', len(wordbank))
    print('guessable:', len(combined))

    out = {}
    for i, word in enumerate(wordbank):
        out[word] = {}
        for guess in combined:
            out[word][guess] = result_for_guess(word, guess)

        if i % 100 == 0:
            print(word)
            with open('words/map.json', 'w') as out_file:
                json.dump(out, out_file)

    with open('words/map.json', 'w') as out_file:
        json.dump(out, out_file)

    with open('words/map.pickle', 'wb') as out_file:
        pickle.dump(out, out_file)
