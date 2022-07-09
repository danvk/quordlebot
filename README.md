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

[Working Notes][1]

[1]: https://docs.google.com/document/d/13_2rYdk_wc9q1g63sxNLUNoaaDAN1mMkgg7rSFWU3CY/edit