from typing import Dict, List
from priors import flatten
from quordlebot import Guess, expected_plays_after_guess, expected_plays_for_guess, find_best_play, find_best_plays, result_for_guess, is_valid_for_guess, is_valid_for_guesses, get_valid_solutions, encode_result, decode_result


def test_result_for_guess_simple():
    assert result_for_guess('DEALT', 'MAVEN') == '.y.y.'
    assert result_for_guess('MAVEN', 'DEALT') == '.yy..'
    assert result_for_guess('STERN', 'DEALT') == '.y..y'
    assert result_for_guess('HAVEN', 'MAVEN') == '.gggg'
    assert result_for_guess('MAVEN', 'MAVEN') == 'ggggg'
    assert result_for_guess('STERN', 'CLAMP') == '.....'
    assert result_for_guess('TREAD', 'DEALT') == 'yyy.y'
    assert result_for_guess('STEAD', 'DEALT') == 'yyy.y'


def test_result_double_letters():
    assert result_for_guess('APPLE', 'APPLE') == 'ggggg'
    assert result_for_guess('APPLE', 'PLUMP') == 'yy..y'
    assert result_for_guess('APPLE', 'POPES') == 'y.gy.'
    assert result_for_guess('ROPES', 'POPES') == '.gggg'


def test_is_valid_for_guess():
    assert is_valid_for_guess('TREAD', Guess('DEALT', 'yyy.y'))
    assert is_valid_for_guess('STEAD', Guess('DEALT', 'yyy.y'))
    assert not is_valid_for_guess('TRADE', Guess('DEALT', 'yyy.y'))


def test_is_valid_for_guesses():
    assert is_valid_for_guesses('TREAD', [Guess('DEALT', 'yyy.y')])
    assert is_valid_for_guesses('STEAD', [Guess('DEALT', 'yyy.y')])
    assert not is_valid_for_guesses('TRADE', [Guess('DEALT', 'yyy.y')])


def test_get_valid_solutions():
    assert get_valid_solutions(['TREAD', 'STEAD', 'TRADE'], [Guess('DEALT', 'yyy.y')]) == ['TREAD', 'STEAD']
    assert get_valid_solutions(['TREAD', 'STEAD', 'TRADE'], [Guess('DEALT', 'yyy.y'), Guess('TREAD', 'y.ggg')]) == ['STEAD']


def test_encode_decode():
    assert decode_result(encode_result('.....')) == '.....'
    assert decode_result(encode_result('gy...')) == 'gy...'
    assert decode_result(encode_result('yy.g.')) == 'yy.g.'
    assert decode_result(encode_result('...gy')) == '...gy'


def build_lookup(words: List[str]) -> Dict[str, Dict[str, str]]:
    out = {}
    for word in words:
        out[word] = {}
        for guess in words:
            out[word][guess] = result_for_guess(word, guess)
    return out


def test_expected_plays_for_guess():
    lookup = build_lookup(['DOING', 'GOING', 'AAHED'])
    assert find_best_plays(lookup, []) == [(0, '')]
    assert find_best_play(lookup, []) == (0, '')

    # Guaranteed to win with this play, so 0.0 expected plays after to win.
    assert find_best_plays(lookup, [['DOING']]) == [(1.0, 'DOING')]
    assert find_best_play(lookup, [['DOING']]) == (1.0, 'DOING')

    # Play DOING:
    # 50% chance you win this play (0)
    # 50% chance you win next play (1)
    # -> 0.5
    assert expected_plays_for_guess(lookup, [['DOING', 'GOING']], 'DOING', False) == 0.5
    assert expected_plays_after_guess(lookup, [['DOING', 'GOING']], 'DOING') == 0.5

    assert find_best_plays(lookup, [['DOING', 'GOING']]) == [
        (1.5, 'DOING'),
        (1.5, 'GOING'),
        (2.0, 'AAHED'),  # the "D" at the end differentiates
    ]
    assert find_best_play(lookup, [['DOING', 'GOING']]) == (1.5, 'DOING')

    # we're going to hit DOING on this guess, so one remaining guess to get GOING.
    # assert expected_plays_after_guess(lookup, [['DOING'], ['GOING']], 'DOING') == 1.0
    # assert expected_plays_after_guess(lookup, [['DOING'], ['GOING']], 'DOING') == 1.0


def test_find_best_plays2():
    quads = [['FRANK'], ['FORGE', 'GORGE']]
    lookup = build_lookup(flatten(quads))

    assert find_best_plays(lookup, quads) == [(2, 'FRANK')]


def test_find_best_plays10():
    quads = [
        ['BLAND', 'BLANK', 'FLANK', 'GLAND', 'PLANK'],
        ['PALSY', 'SALSA'],
        ['BRAND', 'DRANK', 'FRANK', 'GRAND', 'PRANK'],
        ['FORGE', 'GORGE', 'HORDE']
    ]
    lookup = build_lookup(flatten(quads) + ['GAPED'])
    assert find_best_play(lookup, quads) == (5.2, 'GAPED')
    assert False


def test_dumpy():
    # ./quordlebot.py BERET,CATTY,PUFFY,SPUNK TRAIN CLOSE DUMPY
    quads = [
        ['BERET', 'BERTH', 'EGRET', 'ETHER', 'EXERT'],
        ['CATTY'],
        ['PUFFY'],
        ['SPUNK'],
    ]
    lookup = build_lookup(flatten(quads) + ['GAPED'])

    assert find_best_play(lookup, [['BERET', 'EGRET', 'ETHER', 'EXERT']]) == (1.75, 'BERET')

    assert find_best_play(lookup, quads) == (4.8, 'CATTY')

    # The forced plays are not informative.
    # With any, you have a 20% chance of guessing correctly: 20% / 4
    # If you're wrong, the answer is fully determined:       80% / 5
