import math

def format_result(result) -> str:
    try:
        f = float(result)
    except Exception:
        return str(result)
    if math.isnan(f):
        return 'nan'
    if math.isinf(f):
        return 'inf' if f > 0 else '-inf'
    if f.is_integer():
        return str(int(f))
    return str(f)
