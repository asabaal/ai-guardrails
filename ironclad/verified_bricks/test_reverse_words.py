def test_reverse_words():
    from reverse_words import reverse_words
    # Basic reversal
    assert reverse_words('hello world') == 'world hello'
    # Multiple spaces
    assert reverse_words('  a   b  c   ') == 'c b a'
    # Punctuation
    assert reverse_words('Hello, world!') == 'world! Hello,'
    # Empty string
    assert reverse_words('') == ''
    # Single word
    assert reverse_words('single') == 'single'
