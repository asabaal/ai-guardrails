"""Lexical Shuffle generator."""
import random
from typing import List


def lexical_shuffle(base_instruction: str, params: dict, seed: int) -> List[str]:
    """Generate instruction variants."""
    random.seed(seed)
    return [base_instruction]
