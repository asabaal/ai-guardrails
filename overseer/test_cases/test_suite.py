#!/usr/bin/env python3
"""
Overseer Test Suite - Ground Truth Data
Machine-readable format for all test cases with expected outputs
"""

import json
from typing import Dict, List, Any

# Test case structure schema:
# {
#   "id": "A",
#   "category": "simple_logic",
#   "input_text": "...",
#   "expected_segments": [...],
#   "expected_logic_objects": [...],
#   "expected_evaluation": {...},
#   "metadata": {...}
# }

TEST_CASES = {
    # CATEGORY 1: Clean, Simple Reasoning (Baseline Tests)
    "A": {
        "id": "A",
        "category": "simple_logic",
        "description": "Valid simple reasoning - apples and fiber",
        "input_text": "Apples contain fiber. Foods that contain fiber support digestion. Therefore, apples support digestion.",
        "expected_segments": [
            "Apples contain fiber.",
            "Foods that contain fiber support digestion.",
            "Therefore, apples support digestion."
        ],
        "expected_logic_objects": [
            {
                "text": "Apples contain fiber.",
                "type": "atomic_assertion",
                "entities": ["apples", "fiber"],
                "relationship": "has_property"
            },
            {
                "text": "Foods that contain fiber support digestion.",
                "type": "generalization",
                "entities": ["foods", "fiber", "digestion"],
                "relationship": "supports"
            },
            {
                "text": "Therefore, apples support digestion.",
                "type": "conclusion",
                "entities": ["apples", "digestion"],
                "relationship": "supports"
            }
        ],
        "expected_evaluation": {
            "valid_reasoning": True,
            "fallacies": [],
            "contradictions": [],
            "unsupported_inferences": [],
            "severity": "none"
        },
        "metadata": {
            "test_purpose": "baseline_valid_reasoning",
            "complexity": "simple",
            "logical_steps": 3
        }
    },

    "B": {
        "id": "B",
        "category": "simple_logic",
        "description": "Invalid reasoning - triangle with wrong sides",
        "input_text": "Triangles have three sides. This shape has four sides. Therefore, this shape is a triangle.",
        "expected_segments": [
            "Triangles have three sides.",
            "This shape has four sides.",
            "Therefore, this shape is a triangle."
        ],
        "expected_logic_objects": [
            {
                "text": "Triangles have three sides.",
                "type": "generalization",
                "entities": ["triangles", "sides"],
                "relationship": "has_property"
            },
            {
                "text": "This shape has four sides.",
                "type": "atomic_assertion",
                "entities": ["shape", "sides"],
                "relationship": "has_property"
            },
            {
                "text": "Therefore, this shape is a triangle.",
                "type": "conclusion",
                "entities": ["shape", "triangle"],
                "relationship": "is_a"
            }
        ],
        "expected_evaluation": {
            "valid_reasoning": False,
            "fallacies": ["non_sequitur"],
            "contradictions": [],
            "unsupported_inferences": ["step_3_from_step_2"],
            "severity": "major"
        },
        "metadata": {
            "test_purpose": "detect_invalid_conclusion",
            "complexity": "simple",
            "logical_steps": 3
        }
    },

    "C": {
        "id": "C",
        "category": "simple_logic",
        "description": "Valid reasoning with implicit assumption - snakes and eggs",
        "input_text": "If an animal lays eggs, it is an oviparous animal. A snake lays eggs. Therefore, a snake is oviparous.",
        "expected_segments": [
            "If an animal lays eggs, it is an oviparous animal.",
            "A snake lays eggs.",
            "Therefore, a snake is oviparous."
        ],
        "expected_logic_objects": [
            {
                "text": "If an animal lays eggs, it is an oviparous animal.",
                "type": "conditional",
                "antecedent": "an animal lays eggs",
                "consequent": "it is an oviparous animal"
            },
            {
                "text": "A snake lays eggs.",
                "type": "atomic_assertion",
                "entities": ["snake", "eggs"],
                "relationship": "lays"
            },
            {
                "text": "Therefore, a snake is oviparous.",
                "type": "conclusion",
                "entities": ["snake", "oviparous"],
                "relationship": "is_a"
            }
        ],
        "expected_evaluation": {
            "valid_reasoning": True,
            "fallacies": [],
            "contradictions": [],
            "unsupported_inferences": [],
            "hidden_assumptions": ["all_snakes_lay_eggs"],
            "severity": "minor"
        },
        "metadata": {
            "test_purpose": "detect_hidden_assumptions",
            "complexity": "simple",
            "logical_steps": 3
        }
    },

    # CATEGORY 2: Logical Fallacy Tests
    "D": {
        "id": "D",
        "category": "fallacies",
        "description": "False cause fallacy - rooster and sunrise",
        "input_text": "The rooster crows before sunrise. Therefore, the rooster causes the sun to rise.",
        "expected_segments": [
            "The rooster crows before sunrise.",
            "Therefore, the rooster causes the sun to rise."
        ],
        "expected_logic_objects": [
            {
                "text": "The rooster crows before sunrise.",
                "type": "atomic_assertion",
                "entities": ["rooster", "sunrise"],
                "relationship": "temporal_precedence"
            },
            {
                "text": "Therefore, the rooster causes the sun to rise.",
                "type": "conclusion",
                "entities": ["rooster", "sunrise"],
                "relationship": "causes"
            }
        ],
        "expected_evaluation": {
            "valid_reasoning": False,
            "fallacies": ["false_cause", "post_hoc_ergo_propter_hoc"],
            "contradictions": [],
            "unsupported_inferences": ["causation_from_correlation"],
            "severity": "major"
        },
        "metadata": {
            "test_purpose": "detect_false_cause_fallacy",
            "complexity": "simple",
            "logical_steps": 2
        }
    },

    "E": {
        "id": "E",
        "category": "fallacies",
        "description": "Equivocation fallacy - man/mankind",
        "input_text": "Only man is rational. No woman is a man. Therefore, no woman is rational.",
        "expected_segments": [
            "Only man is rational.",
            "No woman is a man.",
            "Therefore, no woman is rational."
        ],
        "expected_logic_objects": [
            {
                "text": "Only man is rational.",
                "type": "generalization",
                "entities": ["man", "rational"],
                "relationship": "exclusively_has_property"
            },
            {
                "text": "No woman is a man.",
                "type": "atomic_assertion",
                "entities": ["woman", "man"],
                "relationship": "is_not"
            },
            {
                "text": "Therefore, no woman is rational.",
                "type": "conclusion",
                "entities": ["woman", "rational"],
                "relationship": "is_not"
            }
        ],
        "expected_evaluation": {
            "valid_reasoning": False,
            "fallacies": ["equivocation"],
            "contradictions": [],
            "unsupported_inferences": ["step_3_from_step_1_and_2"],
            "severity": "major"
        },
        "metadata": {
            "test_purpose": "detect_equivocation_fallacy",
            "complexity": "simple",
            "logical_steps": 3
        }
    },

    "F": {
        "id": "F",
        "category": "fallacies",
        "description": "Circular reasoning - trustworthy book",
        "input_text": "I know the book is trustworthy because it says it is trustworthy. Therefore, we should trust it.",
        "expected_segments": [
            "I know the book is trustworthy because it says it is trustworthy.",
            "Therefore, we should trust it."
        ],
        "expected_logic_objects": [
            {
                "text": "I know the book is trustworthy because it says it is trustworthy.",
                "type": "circular_reasoning",
                "entities": ["book", "trustworthy"],
                "relationship": "self_referential"
            },
            {
                "text": "Therefore, we should trust it.",
                "type": "conclusion",
                "entities": ["we", "book"],
                "relationship": "should_trust"
            }
        ],
        "expected_evaluation": {
            "valid_reasoning": False,
            "fallacies": ["circular_reasoning", "begging_the_question"],
            "contradictions": [],
            "unsupported_inferences": [],
            "severity": "major"
        },
        "metadata": {
            "test_purpose": "detect_circular_reasoning",
            "complexity": "simple",
            "logical_steps": 2
        }
    }
}

def save_test_cases():
    """Save test cases to JSON files for each category"""
    import os
    
    # Group test cases by category
    by_category = {}
    for case_id, case_data in TEST_CASES.items():
        category = case_data["category"]
        if category not in by_category:
            by_category[category] = {}
        by_category[category][case_id] = case_data
    
    # Save each category to its own file
    for category, cases in by_category.items():
        filename = f"test_cases/{category}/test_cases.json"
        with open(filename, 'w') as f:
            json.dump(cases, f, indent=2)
        print(f"Saved {len(cases)} test cases to {filename}")

if __name__ == "__main__":
    save_test_cases()