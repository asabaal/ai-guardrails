def parse_log_line(line):
    import re
    pattern = r'^\[(?P<timestamp>[^\]]+)\] \[(?P<level>[^\]]+)\] (?P<message>.*)$'
    match = re.match(pattern, line)
    if not match:
        raise ValueError(f'Invalid log line format: {line}')
    return match.groupdict()