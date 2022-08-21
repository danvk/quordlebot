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

Avoiding a copy of the lookup table in the restricted search was a big performance win. Before that optimization, I didn't have the patience to let this command finish:

    $ ./quordlebot.py TOUGH,DYING,PLUME,DOUGH ROAST CLINE
    Best play by expected number of steps to complete:
     1. 7.270 DUMPY (+5.270 plays, +8.88 bits)
     2. 7.370 MOODY (is solution, +5.370 plays, +8.78 bits)
     3. 7.410 DYING (is solution, +5.410 plays, +6.76 bits)
     4. 7.436 FLUME (is solution, +5.436 plays, +5.25 bits)
     5. 7.452 DEPTH (+5.452 plays, +7.75 bits)
     6. 7.457 PUDGY (+5.457 plays, +8.50 bits)
     7. 7.464 EMBED (+5.464 plays, +6.36 bits)
     8. 7.473 HUMID (+5.473 plays, +8.08 bits)
     9. 7.476 DOGMA (+5.476 plays, +7.40 bits)
    10.  7.479 APHID (+5.479 plays, +6.80 bits)
    ./quordlebot.py TOUGH,DYING,PLUME,DOUGH ROAST CLINE  270.39s user 1.37s system 99% cpu 4:32.10 total
