# QuordleBot

Like WordleBot, but for Quordle. How can I get it in six?

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
- [ ] Look for the best static pair of initial plays
  - [x] Remove first word from list of seconds after examing
  - [x] Parallelize the search
  - [ ] Is sorting the list and then doing counts faster?
  - [ ] Does factoring out the `result[guess1]` lookup matter?
- [x] See if using pickle is faster/more compact than JSON (it is: 7.468s->5.060s for quordlebot.py)
- [x] Print how many bits of information were gained by your actual guesses
- [ ] Explore the game tree to find strategies to minimize expected remaining guesses
- [x] Add a mode that takes the four words and your guesses, rather than .yg
- [ ] Factor out a Quordle class

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
