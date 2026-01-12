"""Whitespace Noise generator."""
import random
from typing import List


def whitespace_noise(base_instruction: str, params: dict, seed: int) -> List[str]:
    """Generate instruction variants."""
    random.seed(seed)
    return [base_instruction]
