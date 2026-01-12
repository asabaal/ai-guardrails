"""Add Constraints Tension generator."""
import random
from typing import List


def add_constraints_tension(base_instruction: str, params: dict, seed: int) -> List[str]:
    """Generate instruction variants."""
    random.seed(seed)
    return [base_instruction]
