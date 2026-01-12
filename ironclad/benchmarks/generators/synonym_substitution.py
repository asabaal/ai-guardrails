"""Synonym Substitution generator."""
import random
from typing import List


def synonym_substitution(base_instruction: str, params: dict, seed: int) -> List[str]:
    """Generate instruction variants."""
    random.seed(seed)
    return [base_instruction]
