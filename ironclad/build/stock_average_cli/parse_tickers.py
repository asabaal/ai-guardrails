def parse_tickers(args):
    """Return a list of unique, upper‑cased tickers.

    Parameters
    ----------
    args : object
        An object that should expose a ``tickers`` attribute.

    Returns
    -------
    list[str]
        A list of unique ticker symbols in upper‑case.

    Raises
    ------
    ValueError
        If ``args.tickers`` is missing, ``None`` or empty.
    TypeError
        If ``args.tickers`` is not a list or contains non‑string items.
    """
    if not hasattr(args, "tickers") or args.tickers is None:
        raise ValueError("No tickers provided")
    tickers = args.tickers
    if not isinstance(tickers, list):
        raise TypeError("tickers must be a list")
    normalized = []
    seen = set()
    for ticker in tickers:
        if not isinstance(ticker, str):
            raise TypeError("Each ticker must be a string")
        upper = ticker.upper()
        if upper not in seen:
            seen.add(upper)
            normalized.append(upper)
    if not normalized:
        raise ValueError("No tickers provided")
    return normalized