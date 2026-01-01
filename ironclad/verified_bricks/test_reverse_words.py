from reverse_words import reverse_words

def test_reverse_words():
    assert reverse_words('hello world') == 'world hello'
    assert reverse_words('') == ''
    try:
        reverse_words(123)
    except TypeError:
        pass
    else:
        raise AssertionError('TypeError not raised')
