"""Add Scope Detail generator."""
import random
from typing import List


def add_scope_detail(base_instruction: str, params: dict, seed: int) -> List[str]:
    """Generate instruction variants."""
    random.seed(seed)
    return [base_instruction]
