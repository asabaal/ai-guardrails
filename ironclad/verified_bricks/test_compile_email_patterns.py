import re
import pytest
from compile_email_patterns import compile_email_patterns

def test_compile_email_patterns_basic():
    patterns = [r"^\w+@example\.com$", r"^user@\w+\.org$"]
    compiled = compile_email_patterns(patterns)
    assert isinstance(compiled, list)
    assert len(compiled) == 2
    # Ensure each element is a compiled pattern
    for pat_obj in compiled:
        assert isinstance(pat_obj, re.Pattern)
    # Test matching
    assert compiled[0].match("test@example.com")
    assert not compiled[0].match("test@example.org")
    assert compiled[1].match("user@example.org")
    assert not compiled[1].match("admin@example.org")

def test_compile_email_patterns_empty():
    assert compile_email_patterns([]) == []

def test_compile_email_patterns_invalid():
    # Pattern with unbalanced parenthesis should raise re.error
    with pytest.raises(re.error):
        compile_email_patterns(["(unbalanced"])  # noqa: W605

def test_compile_email_patterns_case_insensitive():
    patterns = [r"^Admin@Example\.Com$"]
    compiled = compile_email_patterns(patterns)
    # Should match different case variations
    assert compiled[0].match("admin@example.com")
    assert compiled[0].match("ADMIN@EXAMPLE.COM")
