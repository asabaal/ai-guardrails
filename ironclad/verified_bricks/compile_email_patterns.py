def compile_email_patterns(patterns):
    import re
    compiled = []
    meta_chars = {'.', '^', '$', '+', '{', '[', '|', ')'}
    # '*' and '?' are treated as wildcards; '(' and ')' are left as regex meta characters
    for pat in patterns:
        escaped = ''
        for ch in pat:
            if ch in '*?':
                escaped += ch
            elif ch in meta_chars:
                escaped += '\\' + ch
            else:
                escaped += ch
        # Replace wildcards with regex equivalents
        regex_pat = escaped.replace('*', '.*').replace('?', '.')
        try:
            compiled.append(re.compile(regex_pat))
        except re.error as e:
            raise ValueError(f"Invalid pattern '{pat}': {e}") from e
    return compiled
