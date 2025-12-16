import pytest
from extract_phones import extract_phones


def test_empty_string():
    assert extract_phones("") == []


def test_no_match():
    assert extract_phones("No numbers here") == []


def test_single_number_variations():
    cases = [
        ("123-456-7890", ["1234567890"]),
        ("(123) 456-7890", ["1234567890"]),
        ("123.456.7890", ["1234567890"]),
        ("123 456 7890", ["1234567890"]),
        ("+1 123-456-7890", ["1234567890"]),
        ("1 123 456 7890", ["1234567890"]),
        ("1234567890", ["1234567890"]),
    ]
    for text, expected in cases:
        assert extract_phones(text) == expected


def test_multiple_numbers():
    text = "Call 123-456-7890 or (987) 654-3210, or 555.555.5555 now."
    assert extract_phones(text) == ["1234567890", "9876543210", "5555555555"]


def test_ignore_invalid_lengths():
    # Numbers that do not resolve to 10 digits after stripping should be ignored
    text = "Short: 123-45, Too long: 1-123-456-789012, Proper: 321-654-0987"
    assert extract_phones(text) == ["3216540987"]


def test_non_numeric_characters():
    text = "Call me at 1(234)567-8900 or at 555-000-0000!!!"
    assert extract_phones(text) == ["2345678900", "5550000000"]


def test_whitespace_and_boundary():
    text = "  555 123 4567  "
    assert extract_phones(text) == ["5551234567"]


if __name__ == "__main__":
    pytest.main([__file__])