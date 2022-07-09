from quordlebot import Guess, result_for_guess, is_valid_for_guess, is_valid_for_guesses, get_valid_solutions


def test_result_for_guess_simple():
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
