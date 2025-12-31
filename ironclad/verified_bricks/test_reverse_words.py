from reverse_words import reverse_words

def test_reverse_words():
    # Basic case
    assert reverse_words("Hello world") == "world Hello"

    # Multiple spaces between words
    assert reverse_words("  one   two  ") == "two one"

    # Empty string
    assert reverse_words("") == ""

    # String with only spaces
    assert reverse_words("   ") == ""

    # Single word
    assert reverse_words("Python") == "Python"

    # Punctuation and mixed characters
    assert reverse_words("Hello, world! This is fun.") == "fun. is This world! Hello,"
