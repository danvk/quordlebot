from quordlebot import result_for_guess


def test_result_for_guess_simple():
    assert result_for_guess('MAVEN', 'DEALT') == '.yy..'
    assert result_for_guess('STERN', 'DEALT') == '.y..y'
    assert result_for_guess('HAVEN', 'MAVEN') == '.gggg'
    assert result_for_guess('MAVEN', 'MAVEN') == 'ggggg'
    assert result_for_guess('STERN', 'CLAMP') == '.....'
