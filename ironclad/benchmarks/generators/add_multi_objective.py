"""Add Multi-Objective generator."""
import random
from typing import List


def add_multi_objective(base_instruction: str, params: dict, seed: int) -> List[str]:
    """Generate instruction variants."""
    random.seed(seed)
    return [base_instruction]
