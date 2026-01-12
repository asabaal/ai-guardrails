"""Constraint Injection Light generator."""
import random
from typing import List


def constraint_injection_light(base_instruction: str, params: dict, seed: int) -> List[str]:
    """Generate instruction variants."""
    random.seed(seed)
    return [base_instruction]
