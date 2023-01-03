# QuordleBot

Like WordleBot, but for Quordle. How can I get it in six?

## Usage

Install / generate lookup tables:

    python3 -m venv venv
    pip install -r requirements.txt

    ./generate_lookup_table.py  # takes ~4 minutes
    ./generate_array.py
    ls -lh words/map.pickle words/array.pickle

Find the best next play:

    ./quordlebot.py NYLON,SHELF,VIRAL,BUDGE ROAST
    ROAST ['.y...', '...y.', 'y.y..', '.....'] -> [76, 94, 73, 266] = 138722192 +17.66 bits
    Best next plays based on expected information gain:
    CLINE -> +20.00 bits
    INCLE -> +19.36 bits
    CLIPE -> +19.29 bits
    CLIME -> +19.26 bits

Find the best plays absent any feedback:

    ./priors.py
    # (takes many hours to run!)

## Notes

The word list is inlined into the Quordle JS:

```json
{
  "blacklist": "GYPSY GIPSY MAMMY AGORA SLAVE HUSSY JUNTA JUNTO WELCH MORON",
  "wordBank": "ABACK ABASE ABATE...",
  "allowed": "AAHED AALII AARGH..."
}
```

- blacklist: 10 words
- wordBank: 2,315 words
- allowed: 10,657 words

I assume "wordBank" is the words that can be answers and "allowed" is the words you're allowed to guess. Unclear to me exactly how "blacklist" works, these words appear in "wordBank" but not "allowed".

Assuming there are never dupes, that means there are

    2314 * 2314 * 2313 * 2312 = 28634537426976 solutions
    log2(28634537426976) = 44.7 bits of entropy

So maybe a good start is to look at which guesses maximize information gain for any given state.

Best and worst first words according to pure information gain:

```
[(5.885960110378853, 'SOARE'), (5.882779324291968, 'ROATE'), (5.865709709951878, 'RAILE'), (5.865457142861989, 'REAST'), (5.834581525865644, 'SALET'), (5.817161175806047, 'ORATE'), (5.792668103557574, 'CARTE'), (5.786709827456228, 'RAINE'), (5.775166510376183, 'ARIEL'), (5.774382034176954, 'CARET')]
[(2.2851367360614, 'GYPPY'), (2.267954317843193, 'KUDZU'), (2.2436395107418843, 'FUFFY'), (2.2341699553948438, 'JAFFA'), (2.2141711564276, 'PZAZZ'), (2.206893724562269, 'YUKKY'), (2.192000567958077, 'XYLYL'), (2.0525999694165993, 'IMMIX'), (2.0383091074888515, 'JUJUS'), (1.8918361327315534, 'QAJAQ')]
```

I remember `ROATE`!

I see no reason to use a different first word for Quordle. What about as a second word? Presumably it depends on the patterns you get out.

With optimal information gain play, my quordlebot solves today's in seven, which is the same number of guesses that I used.

Here's its sequence:

    ./quordlebot.py SOARE,y..y.,..y..,..g..,g.yy. CLIPT,....y,.....,.g...,...yy STRAP,yyy..,...y.,...y.,ggggg DUNGY,.y...,...y.,.....,.....
    SOARE [16, 138, 40, 8]
    CLIPT [2, 20, 6, 1]
    STRAP [2, 17, 6, 1]
    DUNGY [1, 2, 1, 1]
    Quad 0 must be TRUSS
    Quad 1 is one of ['GAMMA', 'MAGMA']
    Quad 2 must be LLAMA

If your goal were to get a six, I wonder if there's a better strategy than maximizing information gain?

The lists are actually disjoint! So I need to add the wordbank words to the allowed guess list.

    $ two-stats words/wordbank.txt words/allowed.txt
    A: words/wordbank.txt
    B: words/allowed.txt
    |A|: 2315
    |B|: 10657
    |A ∪ B|: 12972
    |A ∩ B|: 0
    |A - B|: 2315
    |B - A|: 10657

So 12,972 guessable words total.

Next steps:

- [x] Rerun initial play analysis with larger list of guessable words
- [x] Look for the best static pair of initial plays
  - [x] Remove first word from list of seconds after examing
  - [x] Parallelize the search
  - [ ] Is sorting the list and then doing counts faster?
  - [ ] Does factoring out the `result[guess1]` lookup matter?
- [x] See if using pickle is faster/more compact than JSON (it is: 7.468s->5.060s for quordlebot.py)
- [x] Print how many bits of information were gained by your actual guesses
- [ ] Explore the game tree to find strategies to minimize expected remaining guesses
  - [x] Expected number of remaining guesses doesn't seem right?
  - [x] Sort un-forced guesses by information gain
  - [ ] Prune by "best so far"; but when can you bail out if you're looking for expected number of plays?
  - [x] Only keep track of optimal number in the cases where that's what we care about
- [x] Ignore subsequent guesses after you've gotten a word
- [ ] Switch `quordlebot.py` to use the array format
- [x] Add a mode that takes the four words and your guesses, rather than .yg
- [ ] Factor out a Quordle class
- [x] ROAST / CLINE seems to always result in far more bits of information gain than `priors.py` suggests should be expected (~35 bits vs. 9.6 bits). What's going on? (It's four boards vs. one!)
- [ ] How frequently does ROAST / CLINE / HUMID or ROAST / CLINE / DUMPY give you a guaranteed seven?
- [ ] How often is CLINE the best second guess after ROAST?
- [ ] Report the expected vs. actual information gain of each of your guesses
- [ ] What are the odds of getting a six if you go for it?
- [ ] Can Python distinguish guessable/wordbank indices via nominal types? (Sorta https://docs.python.org/3/library/typing.html#newtype)
- [ ] Why do I have to import ResultDict to unpickle `array.pickle`?
- [ ] Measure optimal performance
  - [ ] What's quordlebot's expected number of guesses / distribution?
  - [ ] How frequently does "go for 5" work? What does it cost you?
- [x] Add a `--today` (or default) option that mimics Quorlde's Mersenne Twister;
- [x] When's the next time that TRAIN / CLOSE / FILET / SONAR will be an answer?
- [x] Add a `--no-spoilers` option
- [ ] Improve the startup time for `quordle.py`

Updated best and worst first guesses:

[(5.885960110378853, 'SOARE'), (5.882779324291968, 'ROATE'), (5.877909690821479, 'RAISE'), (5.865709709951878, 'RAILE'), (5.865457142861989, 'REAST'), (5.855775376955964, 'SLATE'), (5.834581525865644, 'SALET'), (5.832589698902821, 'CRATE'), (5.831396980440786, 'IRATE'), (5.829323821643724, 'TRACE')]
[(2.2851367360614, 'GYPPY'), (2.267954317843193, 'KUDZU'), (2.2436395107418843, 'FUFFY'), (2.2341699553948438, 'JAFFA'), (2.2141711564276, 'PZAZZ'), (2.206893724562269, 'YUKKY'), (2.192000567958077, 'XYLYL'), (2.0525999694165993, 'IMMIX'), (2.0383091074888515, 'JUJUS'), (1.8918361327315534, 'QAJAQ')]

Best first two guesses:

    SOARE CLINT -> +9.63 bits
    ROAST CLINE -> +9.61 bits *
    SOCLE RIANT -> +9.61 bits
    RIANT CLOSE -> +9.61 bits
    LOAST CRINE -> +9.60 bits
    SAINT CEORL -> +9.60 bits
    TRAIL SONCE -> +9.59 bits
    ROIST LANCE -> +9.58 bits
    SONCE LIART -> +9.58 bits
    TRICE SALON -> +9.58 bits
    SARIN CLOTE -> +9.58 bits
    LIANE CROST -> +9.58 bits
    TORAN SLICE -> +9.58 bits
    TOILE CARNS -> +9.57 bits
    NOISE CLART -> +9.57 bits
    TRAIN SOCLE -> +9.57 bits
    TRINE COALS -> +9.57 bits
    TOILS CRANE -> +9.57 bits
    TOILE CRANS -> +9.57 bits
    CRANE TOILS -> +9.57 bits *
    DOILT CARSE -> +9.56 bits

ROAST/CLINE feels somewhat not made up; CRANE/TOILS are both clearly real words.

After playing ROAST/CLINE, there's a fully-determined word ~70% of the time.

If you only look at pairs of words from the wordbank, here are the top ones:

    TRICE SALON -> +9.58 bits
    STOLE CAIRN -> +9.56 bits
    TRAIN CLOSE -> +9.56 bits
    LINER COAST -> +9.55 bits
    SLANT CRIED -> +9.52 bits
    STAIR CLONE -> +9.52 bits
    TRAIL SCONE -> +9.52 bits
    SPILT CRANE -> +9.52 bits
    SLANT PRICE -> +9.51 bits

"TRICE" feels made-up, but TRAIN / CLOSE is great.

Here's a very slow run (~7h) with mixed solution / non-solution plays:

    ./quordlebot.py CHAFF,LOWLY,SWORE,PAPER TRAIN CLOSE  14292.83s user 38.97s system 58% cpu 6:45:06.09 total
    Best play by expected number of steps to complete:
    1. 7.535 PUDGY (+5.535 plays, +6.73 bits)
    2. 7.537 CHAMP (is solution, +5.537 plays, +5.72 bits)
    3. 7.558 DOGMA (+5.558 plays, +5.73 bits)
    4. 7.595 MOLDY (is solution, +5.595 plays, +5.76 bits)
    5. 7.619 PADDY (+5.619 plays, +6.59 bits)
    6. 7.619 GOLEM (+5.619 plays, +5.90 bits)
    7. 7.624 DOPEY (+5.624 plays, +6.45 bits)
    8. 7.639 GODLY (is solution, +5.639 plays, +5.06 bits)
    9. 7.645 PYGMY (+5.645 plays, +6.64 bits)
    10. 7.651 MADLY (+5.651 plays, +6.11 bits)
    11. 7.654 DUMPY (+5.654 plays, +6.60 bits)
    12. 7.663 MOGUL (is solution, +5.663 plays, +4.91 bits)

Another slow one:

    ./quordlebot.py HAREM,GAILY,TRITE,KNEAD TRAIN CLOSE
    Best play by expected number of steps to complete:
    1. 7.537 EMPTY (+5.537 plays, +7.26 bits)
    2. 7.600 PYGMY (+5.600 plays, +7.35 bits)
    3. 7.631 DEPTH (+5.631 plays, +6.53 bits)
    4. 7.641 DUMPY (+5.641 plays, +7.33 bits)
    5. 7.706 PARTY (+5.706 plays, +6.28 bits)
    6. 7.713 BLIMP (+5.713 plays, +6.49 bits)
    7. 7.725 APHID (+5.725 plays, +6.77 bits)
    8. 7.740 EMBED (+5.740 plays, +6.54 bits)
    9. 7.744 AMPLY (+5.744 plays, +7.18 bits)
    10. 7.749 GIPSY (+5.749 plays, +6.39 bits)

If you want to go for five, what's the best first word to play? For some of our standard openers, here's how many words are fully-determined by the opening play, or a 50/50:

- ROAST: 35 / 26
- CLINE: 30 / 28
- TRAIN: 32 / 32
- CLOSE: 21 / 26

So play ROAST before CLINE and TRAIN before CLOSE.

What if you want to go for five? Some variations:

- FILET / SONAR: 37 / 46, 9.276 information gain
- FLIRT / CANOE: 32 / 52, 9.286 IG
- SATIN / CRUEL: 35 / 38, 9.429 IG
- TRIED / SALON: 35 / 36, 9.444 IG
- ROAST / CLINE: 35 / 26, 9.61 IG
- TRAIN / CLOSE: 32 / 32, 9.558 IG

(Note: this only considered wordbank words for the second guess for IG.)
