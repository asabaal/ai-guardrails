import pytest
from parse_log_line import parse_log_line

def test_parse_standard():
    line = '[2023-01-01 10:00:00] [ERROR] User [admin] failed login'
    result = parse_log_line(line)
    assert result['timestamp'] == '2023-01-01 10:00:00'
    assert result['level'] == 'ERROR'
    assert result['message'] == 'User [admin] failed login'

def test_parse_with_additional_brackets():
    line = '[2023-02-15 12:30:00] [WARN] Disk [root] space low [2% remaining]'
    result = parse_log_line(line)
    assert result['timestamp'] == '2023-02-15 12:30:00'
    assert result['level'] == 'WARN'
    assert result['message'] == 'Disk [root] space low [2% remaining]'

def test_invalid_format():
    line = '[2023-01-01 10:00:00] ERROR] User [admin] failed login'
    with pytest.raises(ValueError):
        parse_log_line(line)