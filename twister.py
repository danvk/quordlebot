# See https://github.com/yinengy/Mersenne-Twister-in-Python/blob/master/MT19937.py

import datetime
from typing import List, Set


# coefficients for MT19937
(w, n, m, r) = (32, 624, 397, 31)
a = 0x9908B0DF
(u, d) = (11, 0xFFFFFFFF)
(s, b) = (7, 0x9D2C5680)
(t, c) = (15, 0xEFC60000)
l = 18
f = 1812433253


# make a arry to store the state of the generator
MT = [0 for i in range(n)]
index = n+1
lower_mask = 0x7FFFFFFF #(1 << r) - 1 // That is, the binary number of r 1's
upper_mask = 0x80000000 #lowest w bits of (not lower_mask)


# initialize the generator from a seed
def mt_seed(seed):
    # global index
    # index = n
    MT[0] = seed
    for i in range(1, n):
        temp = f * (MT[i-1] ^ (MT[i-1] >> (w-2))) + i
        MT[i] = temp & 0xffffffff


# Extract a tempered value based on MT[index]
# calling twist() every n numbers
def extract_number():
    global index
    if index >= n:
        twist()
        index = 0

    y = MT[index]
    y = y ^ ((y >> u) & d)
    y = y ^ ((y << s) & b)
    y = y ^ ((y << t) & c)
    y = y ^ (y >> l)

    index += 1
    y = y & 0xffffffff
    if y > 2 ** 31:
        y = y - 2 ** 32
    return y

def rand_int31():
    y = extract_number()
    if y < 0:
        y = y + 2 ** 32
    y = y >> 1
    # print(y)
    return y

# Generate the next n values from the series x_i
def twist():
    for i in range(0, n):
        x = (MT[i] & upper_mask) + (MT[(i+1) % n] & lower_mask)
        xA = x >> 1
        if (x % 2) != 0:
            xA = xA ^ a
        MT[i] = MT[(i + m) % n] ^ xA


def get_seed(d: datetime.date):
    elapsed = d - datetime.date(2022, 1, 24)
    return elapsed.days


def generate_words(seed: int, wordbank: List[str], blacklist: Set[str]) -> List[str]:
    mt_seed(seed)
    rand_int31()
    rand_int31()
    rand_int31()
    rand_int31()
    while True:
        words = [
            wordbank[rand_int31() % len(wordbank)],
            wordbank[rand_int31() % len(wordbank)],
            wordbank[rand_int31() % len(wordbank)],
            wordbank[rand_int31() % len(wordbank)],
        ]

        if (
            words[0] == words[1] or
            words[0] == words[2] or
            words[0] == words[3] or
            words[1] == words[2] or
            words[1] == words[3] or
            words[2] == words[3] or
            words[0] in blacklist or
            words[1] in blacklist or
            words[2] in blacklist or
            words[3] in blacklist
        ):
            continue
        else:
            break

    return words



if __name__ == '__main__':
    words = [word.strip() for word in open('words/wordbank.txt')]
    blacklist = {word.strip() for word in open('words/blacklist.txt')}
    print(len(words))
    print(len(blacklist))
    s = get_seed(datetime.date.today())
    print(s)
    mt_seed(10)
    for i in range(10):
        print(i, rand_int31())
    # print(generate_words(s, words, blacklist))
