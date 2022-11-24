#!/usr/bin/env python
"""When will a word next be an answer?"""

import sys
import datetime

import twister

if __name__ == '__main__':
    word = sys.argv[1]
    d = datetime.date.today()
    while True:
        words = twister.words_for_date(d)
        if word in words:
            print(d)
            break
        d += datetime.timedelta(days=1)
