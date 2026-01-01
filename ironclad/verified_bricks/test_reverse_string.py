from reverse_string import reverse_string

def test_reverse_string():
    assert reverse_string('abc') == 'cba'
    assert reverse_string('') == ''
    assert reverse_string('a') == 'a'
    assert reverse_string(None) is None
    # test with unicode
    assert reverse_string('こんにちは') == 'はちにんこ'
