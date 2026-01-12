def test_compile_email_patterns():
    import pytest
    import re
    from compile_email_patterns import compile_email_patterns
    patterns = ['test@example.com', 'user*@domain.com', '*@*.com']
    compiled = compile_email_patterns(patterns)
    assert len(compiled) == 3
    assert compiled[0].fullmatch('test@example.com')
    assert compiled[1].fullmatch('user123@domain.com')
    assert not compiled[1].fullmatch('admin@domain.com')
    assert compiled[2].fullmatch('foo@bar.com')
    assert not compiled[2].fullmatch('foo@bar.org')
    assert compile_email_patterns([]) == []
    with pytest.raises(ValueError):
        compile_email_patterns(['user(.*@example.com'])
