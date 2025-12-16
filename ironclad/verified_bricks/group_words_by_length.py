def group_words_by_length(words: list[str]) -> dict[int, list[str]]:
    result = {}
    for word in words:
        if not isinstance(word, str):
            raise TypeError("All items must be strings")
        result.setdefault(len(word), []).append(word)
    return result