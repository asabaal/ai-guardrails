from process_numbers import process_numbers

def test_process_numbers_normal():
    result = process_numbers([1,2,3])
    assert result == {"count":3, "sum":6, "mean":2}

def test_process_numbers_single():
    result = process_numbers([5])
    assert result == {"count":1, "sum":5, "mean":5}

def test_process_numbers_empty():
    result = process_numbers([])
    assert result == {"count":0, "sum":0, "mean":None}

def test_process_numbers_negative():
    result = process_numbers([-1,-2])
    assert result == {"count":2, "sum":-3, "mean":-1.5}

def test_process_numbers_float():
    result = process_numbers([1.5, 2.5])
    assert result == {"count":2, "sum":4.0, "mean":2.0}
