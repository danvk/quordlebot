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

[Working Notes][1]

[1]: https://docs.google.com/document/d/13_2rYdk_wc9q1g63sxNLUNoaaDAN1mMkgg7rSFWU3CY/edit