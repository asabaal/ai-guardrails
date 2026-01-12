import pytest
from multiply_list import multiply_list

@pytest.mark.parametrize(
    "nums,expected",
    [
        ([1, 2, 3], 6),
        ([5, 0, 2], 0),
        ([-1, -2, -3], -6),
        ([], 1),
        ([10**5, 10**5], 10**10),
    ],
)
def test_multiply_list(nums, expected):
    assert multiply_list(nums) == expected
