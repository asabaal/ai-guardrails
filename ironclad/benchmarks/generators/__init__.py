"""
Benchmark generators for Ironclad instruction transformations.

This module provides both deterministic and AI-based instruction generators
that are used by benchmark harness to probe Ironclad's behavior.
"""

from .whitespace_noise import whitespace_noise
from .punctuation_noise import punctuation_noise
from .lexical_shuffle import lexical_shuffle
from .synonym_substitution import synonym_substitution
from .ambiguity_injection_light import ambiguity_injection_light
from .constraint_injection_light import constraint_injection_light
from .add_scope_detail import add_scope_detail
from .add_constraints_tension import add_constraints_tension
from .add_ambiguity import add_ambiguity
from .add_multi_objective import add_multi_objective

__all__ = [
    "whitespace_noise",
    "punctuation_noise",
    "lexical_shuffle",
    "synonym_substitution",
    "ambiguity_injection_light",
    "constraint_injection_light",
    "add_scope_detail",
    "add_constraints_tension",
    "add_ambiguity",
    "add_multi_objective",
]
