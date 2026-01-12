# Benchmark Generators

This module provides instruction transformation generators for Ironclad benchmarking.

## Generator Contract

All generators accept the same inputs and return the same output format.

### Inputs

- `base_instruction`: string - The baseline instruction to transform
- `params`: dict - Generator-specific parameters
- `seed`: int - Reproducibility seed

### Outputs

- `List[str]` - Mutated instruction strings

### Guarantees

- Output strings must be valid UTF-8
- Core task intent must be preserved
- No references to tests, tooling, or harness behavior
- Deterministic given same inputs (except for AI-based generators)

## Deterministic Generators

These generators always produce the same output given the same inputs.

## Available Generators

1. `whitespace_noise` - Random insertion of spaces, line breaks, and tabs
2. `punctuation_noise` - Insert or remove punctuation characters
3. `lexical_shuffle` - Swap adjacent phrases or reorder clauses
4. `synonym_substitution` - Replace words with close synonyms
5. `ambiguity_injection_light` - Add mild ambiguity phrases
6. `constraint_injection_light` - Add soft preference phrases

## AI-Based Generators

These generators use an AI model to transform instructions. They are non-deterministic but have explicit guardrails.

## Available AI Generators

1. `ai_rewrite_style` - Rewrite in a specified style (concise_directive, verbose_formal, casual_request, specification_tone)
2. `ai_rephrase_with_focus_shift` - Emphasize a specific dimension (simplicity, clarity, maintainability, correctness_emphasis_soft)
3. `ai_semantic_restatement` - Deeper paraphrase while preserving meaning
4. `ai_register_shift` - Change register (planner_voice, executive_voice, peer_engineer_voice)
5. `ai_constraint_surface_without_adding` - Make implicit assumptions explicit
6. `ai_minimalism_pass` - Compress to minimal form
7. `ai_elaboration_pass` - Expand slightly with more detail
8. `ai_adversarial_style_mismatch` - Rewrite in very informal/messy style
9. `ai_ambiguity_preserving_rewrite` - Keep same ambiguity level, different wording

## Stress Ladder Generators

These are ordered generators that increase task complexity and ambiguity.

## Available Stress Ladder Generators

1. `add_scope_detail` - Add concrete clarifications
2. `add_constraints_tension` - Introduce soft tradeoffs
3. `add_ambiguity` - Add ambiguous judgment phrases
4. `add_multi_objective` - Add multiple deliverables

## Usage

```python
from benchmarks.generators import whitespace_noise, ai_rewrite_style

# Deterministic generator
variants = whitespace_noise(
    base_instruction="Compile a list of email patterns into regex objects.",
    params={"count": 10, "intensity_min": 0.05, "intensity_max": 0.35},
    seed=1337
)

# AI-based generator
variants = ai_rewrite_style(
    base_instruction="Compile a list of email patterns into regex objects.",
    params={"count": 5, "styles": ["concise_directive", "verbose_formal"]},
    seed=1340
)
```
