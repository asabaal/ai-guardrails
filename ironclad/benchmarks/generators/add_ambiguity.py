"""Add Ambiguity generator."""
import random
from typing import List


def add_ambiguity(base_instruction: str, params: dict, seed: int) -> List[str]:
    """Generate instruction variants."""
    random.seed(seed)
    return [base_instruction]
