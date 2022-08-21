# Game tree for Quordle

- [IDIOM, OPIUM], [HORDE], [CYNIC]
  - HORDE (3)
    - [.y...: OPIUM, .y.y.: IDIOM], ✓, .....
    - win in three either way
  - CYNIC (3)
    - [...y.: OPIUM,IDIOM], ....., ✓
    - HORDE (3)
      - [.y...: OPIUM, .y.y.: IDIOM], ✓
      - win in three either way
    - OPIUM (3.5)
    - IDIOM (3.5)
    - any other guess must be 4+
  - IDIOM (3.5)
  - OPIUM (3.5)
  - Any other guess must be 4+

If there's any sequence with expected plays < 1 + words left, then you only need to consider guessing possible words.

So one approach might be to have a distinct code path with a restricted vocabulary that you try first. This should speed up the search closer to the leaf nodes.

I wonder whether memoization would be helpful here. Guessing A then B is always the same as guessing B then A, at least.

A "cheap" minimum plays to solve when there are N words left and no word is fully-determined is N + 0.5.

Another constraint is that depth 10+ is death. May as well stop.

Once you've gotten an expected value based on one non-solution word, that can be a powerful filter. It's likely that most boards have a guaranteed seven? And it's unlikely you'll ever need to do more than two full searches of all possible words.

As you iterate through possible g/y/. patterns, there's a cheap minimum expected number of plays for each of N + (M-1)/M where N=number of words left and M=smallest set of possible words for a quad (reduces to just N when M=1, i.e. a word is fully-determined). As you iterate through, you can count how much in excess you are. This would provide a way to bail out of the loop early given a decent upper bound on the number of expected plays. This would work best if the iteration were in order of the most likely patterns (which make the greatest contribution to the expected value).

This one runs into a case where there's 15 possible words for one quad and five for another. Running through all these first produces a very deep and mostly pointless search tree.

    ./quordlebot.py ASCOT,FEIGN,CHALK,EAGER TRAIN CLOSE ASCOT CHALK

    find_best_play(2315, [['DEIGN', 'FEIGN', 'GIVEN', 'VIXEN', 'WIDEN'], ['DEBAR', 'EAGER', 'GAMER', 'GAYER', 'GAZER', 'PAPER', 'PARER', 'PAYER', 'RARER', 'REBAR', 'REPAY', 'WAFER', 'WAGER', 'WAVER', 'ZEBRA']])

Adding a max depth filter is pretty effective at cutting this off. I set it at 10, but this could be even more aggressive based on the number of plays already done.
