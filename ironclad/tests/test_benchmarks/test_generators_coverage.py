"""
Test generators for coverage.
"""

import sys
import unittest

sys.path.insert(0, '/mnt/storage/repos/ai-guardrails/ironclad')
from benchmarks.generators import (
    whitespace_noise,
    punctuation_noise,
    lexical_shuffle,
    synonym_substitution,
    ambiguity_injection_light,
    constraint_injection_light,
    add_scope_detail,
    add_constraints_tension,
    add_ambiguity,
    add_multi_objective,
)


class TestGeneratorsCoverage(unittest.TestCase):
    """Test generators with actual code execution."""

    def test_whitespace_noise_execution(self):
        """Test whitespace_noise generator execution."""
        variants = whitespace_noise(
            base_instruction="Compile a list of email patterns.",
            params={"count": 2, "intensity_min": 0.1, "intensity_max": 0.2},
            seed=12345
        )

        self.assertEqual(len(variants), 1)
        self.assertTrue(all(isinstance(v, str) for v in variants))

    def test_punctuation_noise_execution(self):
        """Test punctuation_noise generator execution."""
        variants = punctuation_noise(
            base_instruction="Compile a list of email patterns.",
            params={"count": 2, "intensity_min": 0.1, "intensity_max": 0.15},
            seed=54321
        )

        self.assertEqual(len(variants), 1)
        self.assertTrue(all(isinstance(v, str) for v in variants))

    def test_lexical_shuffle_execution(self):
        """Test lexical_shuffle generator execution."""
        variants = lexical_shuffle(
            base_instruction="Design a simple in-memory cache with get and set operations.",
            params={"count": 2, "max_swaps": 2},
            seed=98765
        )

        self.assertEqual(len(variants), 1)
        self.assertTrue(all(isinstance(v, str) for v in variants))

    def test_synonym_substitution_execution(self):
        """Test synonym_substitution generator execution."""
        variants = synonym_substitution(
            base_instruction="Compile a list of email patterns.",
            params={"count": 2, "max_replacements": 2},
            seed=13579
        )

        self.assertEqual(len(variants), 1)
        self.assertTrue(all(isinstance(v, str) for v in variants))

    def test_ambiguity_injection_light_execution(self):
        """Test ambiguity_injection_light generator execution."""
        variants = ambiguity_injection_light(
            base_instruction="Design a simple in-memory cache.",
            params={"count": 2},
            seed=24680
        )

        self.assertEqual(len(variants), 1)
        self.assertTrue(all(isinstance(v, str) for v in variants))

    def test_constraint_injection_light_execution(self):
        """Test constraint_injection_light generator execution."""
        variants = constraint_injection_light(
            base_instruction="Design a simple in-memory cache.",
            params={"count": 2},
            seed=35791
        )

        self.assertEqual(len(variants), 1)
        self.assertTrue(all(isinstance(v, str) for v in variants))

    def test_add_scope_detail_execution(self):
        """Test add_scope_detail generator execution."""
        variants = add_scope_detail(
            base_instruction="Compile a list of email patterns.",
            params={"additions": ["Include plus addressing."]},
            seed=46802
        )

        self.assertEqual(len(variants), 1)
        self.assertTrue(isinstance(variants[0], str))

    def test_add_constraints_tension_execution(self):
        """Test add_constraints_tension generator execution."""
        variants = add_constraints_tension(
            base_instruction="Compile a list of email patterns.",
            params={"additions": ["Prefer clarity", "follow standards"]},
            seed=57913
        )

        self.assertEqual(len(variants), 1)
        self.assertTrue(isinstance(variants[0], str))

    def test_add_ambiguity_execution(self):
        """Test add_ambiguity generator execution."""
        variants = add_ambiguity(
            base_instruction="Compile a list of email patterns.",
            params={"additions": ["where appropriate"]},
            seed=68024
        )

        self.assertEqual(len(variants), 1)
        self.assertTrue(isinstance(variants[0], str))

    def test_add_multi_objective_execution(self):
        """Test add_multi_objective generator execution."""
        variants = add_multi_objective(
            base_instruction="Compile a list of email patterns.",
            params={"additions": ["Return explanation"]},
            seed=79135
        )

        self.assertEqual(len(variants), 1)
        self.assertTrue(isinstance(variants[0], str))


if __name__ == "__main__":
    unittest.main()
