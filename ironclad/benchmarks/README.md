# Ironclad Benchmark System

## Overview

This benchmarking system treats Ironclad as a black-box function: it receives a single instruction string as input and produces an outcome with artifacts. The system is designed to measure reliability, sensitivity to perturbations, and capability boundaries under controlled, repeatable conditions.

## Core Principles

### Ironclad as Black Box

Ironclad is invoked as:
```
python -m ironclad_ai_guardrails.ironclad "<instruction>"
```

The system only sees:
- **Single instruction string** - no hidden parameters, no metadata
- Nothing else - no prompts, no descriptions, no capabilities, no test requirements

### Harness Responsibilities

The benchmark harness is responsible for:
- Generating instruction variants (via deterministic transforms or AI rewrites)
- Invoking Ironclad with each variant
- Capturing outcomes and artifacts
- Providing analysis and aggregation
- The harness owns all repetition, comparison, and reporting

Ironclad is responsible for:
- Generating code and tests from the instruction
- Running validation and repair cycles
- Creating debug logs (if enabled)
- Saving successful bricks

### Single-String Contract

**Rule**: Every benchmark case contains ONLY an instruction string.

- `id`: Unique identifier
- `instruction`: The EXACT string passed to Ironclad CLI

The instruction string must NOT mention:
- Tests, testing, pytest
- Coverage, code coverage
- Validation
- Performance, optimization
- Tooling, harnessing, benchmarking, logging

Everything else belongs to the harness, not Ironclad.

## Directory Structure

```
benchmarks/
  README.md                    # This file
  suites/
    baseline.yaml           # Baseline consistency benchmarks
    adversarial.yaml        # Adversarial sensitivity benchmarks
    stress.yaml             # Stress and ambiguity benchmarks
  generators/
    README.md               # Generator catalog and contracts
  outputs/
    .gitkeep
    run_YYYYMMDD_HHMMSS/
      metadata.json         # Whole-run metadata
      baseline/
        <case_id>/
          run_001/
            summary.json          # Per-invocation results
            instruction.txt      # Exact string passed
            debug_ref.txt       # Pointer to Ironclad's debug dir
          run_002/
            aggregate.json       # Post-hoc aggregate
      adversarial/
        <case_id>/
          <generator_name>/
            variant_000X/
              run_001/
                summary.json
                instruction.txt
                debug_ref.txt
                ai_generation_failure.json  # Only if AI generator fails
            aggregate.json
      stress/
        <case_id>/
          level_1/
            aggregate.json
          level_2/
            aggregate.json
          level_3/
            aggregate.json
```

## Benchmark Suite Schema

### Suite Configuration

```yaml
suite_id: string              # Unique suite identifier
mode: baseline|adversarial|stress
runs_per_variant: integer      # How many times to run each case (adversarial/stress)
timeout_seconds: integer         # Per-run timeout
repair_enabled: boolean          # Whether to allow Ironclad's repair cycle
debug_enabled: boolean           # Whether IRONCLAD_DEBUG=1 should be set
```

### Base Case Schema

```yaml
id: string                      # Stable identifier
instruction: string                # EXACT string for Ironclad
runs: integer                     # How many times to replay (baseline only)
timeout_seconds: integer
```

### Adversarial Suite Schema

```yaml
category: adversarial

base_case: string                # References a baseline case id

cases:
  - id: string                    # Variant identifier
    base_instruction: string       # The baseline instruction to transform
    variants:
      - generator: string          # Generator function name
        params: dict
        count: int
        intensity_min: float    # 0.0-1.0 proportion affected
        intensity_max: float
        seed: int
```

### Stress Suite Schema

```yaml
category: stress

base_case: string

cases:
  - id: string
    base_instruction: string
    stress_ladder:
      - level: int
        generator: string          # Generator function name
        params:
          additions: list[str]  # Strings to append
        seed: int
```

## Output Record Format

### Per-Run Summary (summary.json)

One file per Ironclad invocation.

```json
{
  "run_id": "run_001",
  "suite": "baseline|adversarial|stress",
  "case_id": "compile_email_regex",
  "variant_id": "whitespace_noise_0007",
  "instruction_hash": "sha256:ab12cd...",
  "instruction_length": 56,
  "success": false|true,
  "failure_stage": "generation|validation|repair|unknown",
  "attempts": 3,
  "repairs_triggered": 3,
  "duration_ms": 4123,
  "debug_enabled": true,
  "debug_artifacts_present": true,
  "debug_path": "build/.ironclad_debug/run_20260110_091533",
  "timestamp_utc": "2026-01-10T15:15:33Z",
  "ironclad_version": "git:3fa91bc"
}
```

### Fields

- `run_id`: Sequential run number
- `suite`: Suite category
- `case_id`: Base case identifier
- `variant_id`: For adversarial/stress
- `instruction_hash`: SHA256 of instruction (deduplication)
- `instruction_length`: Character count
- `success`: True only if Ironclad exits cleanly with saved brick
- `failure_stage`: generation, validation, repair, or unknown
- `attempts`: How many validation cycles
- `repairs_triggered`: How many repair_candidate() calls
- `duration_ms`: Wall-clock time
- `debug_enabled`: Whether IRONCLAD_DEBUG=1
- `debug_artifacts_present`: Whether debug dir exists
- `debug_path`: Path to Ironclad's debug directory
- `timestamp_utc`: ISO 8601 timestamp
- `ironclad_version`: Git commit hash

### Aggregate Output (aggregate.json)

Written once per logical grouping (baseline, adversarial variant, stress level).

```json
{
  "suite": "adversarial",
  "case_id": "compile_email_regex",
  "variant": "whitespace_noise",
  "total_runs": 200,
  "successes": 142,
  "failures": 58,
  "success_rate": 0.71,
  "failure_breakdown": {
    "generation": 3,
    "validation": 49,
    "repair": 6
  },
  "attempts_distribution": {
    "1": 61,
    "2": 47,
    "3": 92
  },
  "avg_duration_ms": 3892,
  "p95_duration_ms": 6210,
  "debug_coverage": 1.0
}
```

### Instruction.txt

Plain text file containing the exact instruction string passed to Ironclad.

Purpose:
- Human inspection
- Diffing adversarial variants
- Post-mortem clarity
- Reproducibility verification

### debug_ref.txt

Plain text file containing a path reference.

Format:
```
build/.ironclad_debug/run_20260110_091533
```

The benchmark harness never copies debug artifacts. It records only the path. Actual files are created by Ironclad when debug mode is enabled.

### AI Generation Failure Metadata (ai_generation_failure.json)

Created ONLY when an AI generator produces invalid output (e.g., empty string, too long, forbidden tokens).

```json
{
  "generator": "ambiguity_injection_light",
  "attempt": 2,
  "base_instruction": "Compile a list of email patterns into regex objects.",
  "ai_output": "Compile email patterns into regex objects and test them thoroughly.",
  "failure_reasons": [
    "forbidden_token: test",
    "adds_requirement"
  ],
  "timestamp_utc": "2026-01-10T17:42:09Z"
}
```

## Generator Catalog

### Deterministic Generators

Pure instruction transformers. Given same inputs, always produce same outputs.

#### 1. whitespace_noise

**Purpose**: Test robustness to superficial formatting noise (copy-paste artifacts, line wrapping, irregular spacing).

**Transform**: Random insertion of extra spaces, line breaks, and tabs.

**Parameters**:
- `count`: Number of variants to produce
- `intensity_min`: 0.0-1.0 (minimum proportion of characters affected)
- `intensity_max`: 0.0-1.0 (maximum proportion)
- `seed`: Reproducibility seed

**Guarantees**:
- All original tokens preserved
- Semantic content unchanged
- No token reordering

**Expected Effects**:
- Usually no outcome change
- Occasionally increases attempts or repair depth

#### 2. punctuation_noise

**Purpose**: Test sensitivity to punctuation irregularities (informal writing, email/chat phrasing, missing/excessive punctuation).

**Transform**: Insert or remove commas, periods, colons randomly.

**Parameters**:
- `count`: Number of variants
- `intensity_min`: 0.05-0.20
- `intensity_max`: 0.05-0.20
- `seed`: Reproducibility seed

**Guarantees**:
- Word order preserved
- Instruction remains grammatical or near-grammatical

**Expected Effects**:
- Occasionally changes interpretation slightly

#### 3. lexical_shuffle

**Purpose**: Test robustness to light syntactic reordering (non-native phrasing, alternate sentence constructions).

**Transform**: Swap adjacent phrases or reorder clauses where semantically safe.

**Parameters**:
- `count`: Number of variants
- `max_swaps`: Maximum phrase swaps per variant
- `seed`: Reproducibility seed

**Guarantees**:
- Same words, different order
- Same instruction intent

**Expected Effects**:
- Sometimes changes interpretation slightly
- Good detector of brittle parsing logic

#### 4. synonym_substitution

**Purpose**: Test semantic invariance under vocabulary changes (different user vocabulary, style variation).

**Transform**: Replace words with close synonyms using a controlled synonym map.

**Parameters**:
- `count`: Number of variants
- `max_replacements`: Maximum word replacements per variant
- `seed`: Reproducibility seed

**Guarantees**:
- No domain-specific terms replaced (unless whitelisted)
- Meaning preserved

**Expected Effects**:
- Usually no change to outcome

#### 5. ambiguity_injection_light

**Purpose**: Probe ambiguity tolerance without changing task class (simulating real user underspecification).

**Transform**: Append or integrate mild ambiguity phrases (e.g., "where appropriate", "in common cases", "using reasonable assumptions").

**Parameters**:
- `count`: Number of variants

**Guarantees**:
- Does not introduce conflicting goals
- Does not increase task scope

**Expected Effects**:
- Occasional extra repair attempts due to interpretation ambiguity

#### 6. constraint_injection_light

**Purpose**: Test soft constraint handling (simulating user adding preferences without creating hard conflicts).

**Transform**: Add soft preference or guiding principle phrases (e.g., "prefer clarity over cleverness", "keep solution simple").

**Parameters**:
- `count`: Number of variants

**Guarantees**:
- No explicit tradeoff conflicts
- No mention of tests, performance, tooling

**Expected Effects**:
- No mention of tests, coverage, pytest in instruction

### AI-Based Generators

Controlled transformations using an AI model. These are non-deterministic by nature but have explicit guardrails.

#### Universal Contract

**Inputs**:
- `base_instruction`: The baseline instruction to transform
- `params`: Generator-specific parameters
- `seed`: Reproducibility seed
- `model_config`: Optional model configuration

**Outputs**:
- `List[str]`: Mutated instruction strings

**Hard Guarantees**:
- Output strings must be valid UTF-8
- Core task intent must be preserved
- No references to tests, tooling, or harness behavior
- Deterministic given (base_instruction, params, seed) unless explicitly AI-based

**Invariants to Preserve**:
- Single sentence or single instruction block (AI rewrite must not combine multiple instructions)
- No new requirements
- No removed requirements
- No mention of tests, coverage, pytest, validation, benchmarking, harness, logs
- Output ONLY rewritten instruction, no explanation, no meta-commentary

#### 7. ai_rewrite (Style Transform)

**Purpose**: Test sensitivity to stylistic reframing (different communication styles, user personalities).

**Transform**: AI rewrites instruction in a specified style.

**Parameters**:
- `count`: Number of variants
- `styles`: List of style types

**Available Styles**:
- `concise_directive`: Short, direct, imperative
- `verbose_formal`: Formal, complete language
- `casual_request`: Conversational, question format
- `specification_tone`: As if part of technical specification

**Hard Rules**:
- AI prompt must say: "Preserve the task exactly. Change wording only."
- Harness stores the rewrite prompt used (metadata), not passed to Ironclad
- Output reviewed by harness for length and intent drift

**Expected Effects**:
- Most likely to surface semantic brittleness

**Validation Rules (Harness-Enforced)**:

Reject and discard rewrite if any of these conditions are violated:
- Instruction length differs by more than ±200 percent from baseline
- New verbs appear that imply extra work (e.g., "validate", "test", "optimize")
- Multiple sentences introduce additional goals
- References to format, performance, or tooling appear
- Forbidden tokens appear: test, tests, coverage, pytest, benchmark, harness, log, debug, performance, optimize

**Example**:

```
Base instruction:
Compile a list of email patterns into regex objects.

concise_directive output:
Compile common email patterns into regex objects.

Acceptable:
- shorter
- directive
- same task

Reject if:
- removes "list"
- adds validation/tests/examples
```

#### 8. ai_rephrase_with_focus_shift

**Purpose**: Test sensitivity to emphasis changes without scope change (simulating user highlighting different aspects of same task).

**Transform**: AI rewrites instruction to emphasize a specific focus dimension.

**Parameters**:
- `count`: Number of variants
- `focus_values`: List of focus dimensions

**Available Focus Dimensions**:
- `simplicity`
- `clarity`
- `maintainability`
- `correctness_emphasis_soft`

**Hard Rules**:
- Focus must be adjective emphasis only
- No new features implied
- No changes to task scope

**Acceptance Criteria**:
- Adjective emphasis only
- No eviction, concurrency, or performance constraints mentioned
- Core task unchanged

**Example**:

```
Base instruction:
Design a simple in-memory cache with get and set operations.

Focus: simplicity
Output:
Design a straightforward in-memory cache with get and set operations.

Acceptable.

Focus: maintainability
Output:
Design an in-memory cache with get and set operations that is easy to understand and maintain.

Reject if:
- introduces eviction
- introduces concurrency
- introduces performance constraints
```

#### 9. ai_semantic_restatement

**Purpose**: Test semantic invariance under deeper paraphrasing (different wording while preserving meaning).

**Transform**: AI rephrases instruction using substantially different wording while preserving the task exactly.

**Parameters**:
- `count`: Number of variants

**Hard Rules**:
- No mention of tests, coverage, pytest, validation, benchmarking, harness, logs
- No change to task scope or domain
- No implementation language unless present in base instruction
- No mention of requirements removal

**Acceptance Criteria**:
- Core task unchanged
- Task remains solvable in principle

**Example**:

```
Base instruction:
Convert a list of dictionaries into a dictionary keyed by id.

Output:
Take a list of dictionaries and return a single dictionary indexed by each element's id.

Acceptable: Meaning preserved, no new requirements added.

Reject if: introduces new objectives beyond "convert to dictionary indexed by id".
```

#### 10. ai_register_shift

**Purpose**: Test sensitivity to "register" changes (planner voice vs. executive voice vs. peer engineer voice) without just tone changes.

**Transform**: AI rewrites instruction in a specified register: {register}.

**Available Registers**:
- `planner_voice`: Step-oriented but still single instruction
- `executive_voice`: High-level but explicit
- `peer_engineer_voice`: Technical but not adding requirements

**Hard Rules**:
- AI must not turn single instruction into multiple steps or introduce extra deliverables

**Acceptance Criteria**:
- Same meaning
- Same number of deliverables

**Reject if**: It turns into multiple steps or introduces extra deliverables (like "compile", "validate", "deliver").

**Example**:

```
Base instruction:
Compile a list of email patterns into regex objects.

Register: planner_voice
Output:
Produce regex objects for a set of common email patterns.

Register: executive_voice
Output:
Deliver compiled regex objects that capture common email patterns.

Acceptable.

Register: peer_engineer_voice
Output:
Build compiled regex objects representing a list of common email address patterns.

Reject if: Multiple steps or extra deliverables appear.
```

### Stress Ladder Generators

Ordered generators that increase task complexity and ambiguity. These are NOT adversarial - they explore capability boundaries.

#### 11. add_scope_detail

**Purpose**: Increase task specificity without changing scope.

**Transform**: Append concrete clarifications to instruction.

**Parameters**:
- `additions`: List of strings to append (e.g., "Include plus addressing.", "Handle common edge cases.")
- `seed`: Reproducibility seed

**Guarantees**:
- Scope expands linearly
- No conflicting goals
- No mention of tests, coverage, pytest, validation, benchmarking, harness, logs

**Example**:

```
Base instruction:
Compile a list of email patterns into regex objects.

Additions:
- "Include plus addressing and subdomains."
- "Include clear examples of what each pattern is intended to match."

Output:
Compile a list of email patterns into regex objects, including support for plus addressing and subdomains.
```

#### 12. add_constraints_tension

**Purpose**: Introduce soft tradeoffs (competing preferences).

**Transform**: Add preference conflicts like simplicity vs. correctness, strictness vs. practicality.

**Parameters**:
- `additions`: List of preference conflict strings (e.g., "Prefer maintainable patterns over extreme strictness.", "Follow RFC standards but keep implementation simple.")
- `seed`: Reproducibility seed

**Guarantees**:
- Tension is implicit, not contradictory
- No new requirements introduced (only preferences, not hard constraints)

**Example**:

```
Base instruction:
Compile a list of email patterns into regex objects.

Additions:
- "Prefer maintainable patterns over extreme strictness."
- "Prefer clarity over cleverness."

Output:
Compile a list of email patterns into regex objects, balancing clarity and completeness.
```

#### 13. add_ambiguity

**Purpose**: Push interpretive burden onto the model (add judgment calls).

**Transform**: Add ambiguity that requires interpretation but keeps task solvable in principle.

**Parameters**:
- `additions`: List of ambiguous phrases (e.g., "where appropriate", "in common cases", "using reasonable assumptions")
- `seed`: Reproducibility seed

**Guarantees**:
- Task remains solvable in principle
- No impossible requirements
- No mention of tests, coverage, pytest, validation, benchmarking, harness, logs

**Example**:

```
Base instruction:
Compile a list of email patterns into regex objects.

Additions:
- "where appropriate"
- "in common cases"

Output:
Compile a list of email patterns into regex objects, where appropriate.
```

#### 14. add_multi_objective

**Purpose**: Add multiple deliverables (probe fragility).

**Transform**: Add additional objectives or tasks.

**Parameters**:
- `additions`: List of new requirement phrases (e.g., "Return both compiled regex objects and a brief explanation.", "Keep public API small and clean.")

**Reject if**: Introduces tasks like "also provide documentation", "add error handling", "create test suite" beyond base instruction.

**Example**:

```
Base instruction:
Compile a list of email patterns into regex objects.

Additions:
- "Return both compiled regex objects and a brief explanation of each pattern."
- "Keep public API small and clean."

Output:
Compile a list of email patterns into regex objects. Return both compiled regex objects and a brief explanation of each pattern. Keep public API small and clean.
```

## Benchmark Execution Strategy

### Baseline Consistency

**Goal**: Measure pure stochastic stability.

**Process**:
1. Run base case instruction repeatedly (3-10 times)
2. Record all outcomes
3. Declare case stable if last 3 runs are identical

**Early Stop Condition**:
Stop base-case repetition if ALL of these are true across the last 3 runs:
- Same outcome (success or failure)
- Same failure stage (if failing)
- Same attempts count
- Same repair count

**Purpose**: Avoid wasting runs when system is clearly deterministic for that prompt.

### Adversarial Sensitivity

**Goal**: Measure brittleness to semantic and syntactic perturbations.

**Process**:
For each adversarial generator:
1. Generate up to N variants (default N=5, hard cap N=10)
2. For each variant:
   - Run Ironclad once
   - If outcome differs materially from baseline, run it up to 3 times
     - To determine whether deviation is stochastic or structural
3. Discard variant if none of the following change:
   - success vs. failure
   - failure_stage
   - attempts required
   - repair depth

**Material Difference Criteria**:
A variant is "interesting" (worth repeating 3×) if it changes ANY of:
- Success ↔ failure
- Failure_stage
- Attempts count
- Repairs triggered

If none of those change: Do not repeat that variant.

### Stress and Ambiguity

**Goal**: Find capability boundaries and determine where failure becomes structural rather than stochastic.

**Process**:
For each stress level:
1. Minimum 2 runs, maximum 5 runs
2. Stop early if:
   - Failure rate ≥ 80% after 3 runs (systematic failure), OR
   - Success rate = 100% after 3 runs (clear beyond boundary)

**Interpretation Rule**:
- Level 1 should succeed reliably
- Level 2 may succeed with repair
- Level 3 may legitimately fail
- Level 4 defines your capability boundary (expected high failure rate)

**Purpose**: You don't need 10 runs to know you've crossed a boundary.

## Adaptive Stopping Logic

### Base Case Stability Heuristic

```
runs = []
while len(runs) < 10:
    run Ironclad
    record summary
    append to runs

    if len(runs) >= 3:
        if last_3_runs_are_identical(runs):
            break  # Declare case stable and stop
```

### Run Equivalence Definition

Two runs are **equivalent** if ALL of these fields match:
- `success`
- `failure_stage`
- `attempts`
- `repairs_triggered`

**Notes**:
- `duration_ms` is explicitly ignored (noise)
- `instruction_hash` is assumed identical for base-case runs
- `debug_path` is ignored (it changes every run)

### Stable Run Condition

A case is considered **stable** when the last 3 consecutive runs are equivalent by the above definition.

**Consequences**:
- Stop base-case repetition
- Proceed to adversarial generation (if applicable)

## Benchmark Categories and Interpretation

### Calibration Triad

The three base instruction examples form a calibration triad that helps interpret benchmark results:

1. **Regex Construction** (`compile_email_regex`)
   - **Task type**: Structural correctness under constraints
   - **Baseline behavior**: Likely stable after 3 runs, either success with low repair count OR consistent validation failure
   - **Expected adversarial sensitivities**:
     - Whitespace noise: Usually no change
     - Lexical shuffle: Occasional extra repair
     - AI rewrite: Possible success ↔ failure flip (tests model stylistic brittleness)

2. **Data Transformation** (`convert_list_to_dict`)
   - **Task type**: Pure determinism and repair efficiency
   - **Baseline behavior**: Very high stability. Likely success in 1 attempt. Rare stochastic variance.
   - **Expected adversarial sensitivities**:
     - Wording shifts: Minimal impact
     - Synonym substitution: Usually harmless
     - AI rewrite: Occasionally adds extra features but still succeeds
   - **Expected stress boundary**: Ambiguity around duplicate keys may cause divergence. Repair effectiveness usually high.

3. **API Design with Light Ambiguity** (`simple_cache`)
   - **Task type**: Ambiguity handling and repair limits
   - **Baseline behavior**: Moderate variance. Attempts may fluctuate. Repairs commonly triggered.
   - **Expected adversarial sensitivities**:
     - Lexical shuffle: Small changes can affect interpretation
     - AI rewrite: Style changes can materially change structure
     - AI rephrase with focus shift: Occasional extra features, behavior changes
   - **Expected stress boundary**: Adding eviction or concurrency language quickly destabilizes. Failure_stage often shifts from validation to repair exhaustion.

### Failure Attribution

Based on these three examples, you can correctly attribute failures:

| Observation                        | Most Likely Cause             | Interpretation                 |
|-----------------------------------+-----------------------------+-------------------------------|
| Example 2 → extra features     | Scope creep                | AI rephrase added deliverables  |
| Example 3 → different structure   | Ambiguity intolerance       | AI rephrase changed structure    |
| Example 1 → more repairs       | Brittle parsing logic       | Lexical shuffle detected fragility|

This prevents misattributing failures to modules when they're actually caused by:
- Generator configuration issues
- Inadequate heuristics
- Over-ambitious prompt scope

## Ironclad Debug System Integration

### Existing Debug Output

Ironclad already provides a debug system that creates:
- `build/.ironclad_debug/` directory on each run
- Debug logs for generation, validation, repair failures

### Leverage Strategy

**Principle**: The benchmark harness never copies debug artifacts. It records only references to enable post-hoc analysis.

**Implementation**:
- `debug_ref.txt` contains a path pointer like:
  ```
  build/.ironclad_debug/run_20260110_091533
  ```
- `summary.json` contains:
  ```json
  "debug_path": "build/.ironclad_debug/run_20260110_091533"
  ```
- The harness follows this pointer to inspect actual files created by Ironclad

**Benefits**:
- No duplicate storage
- Ability to diff instruction.txt across variants
- Ability to correlate AI generation failures with Ironclad behavior
- Clear separation: harness metadata vs. engine artifacts

## Summary

This benchmark system provides:

1. **Repeatable results**: Same instruction, same seeds, same outcomes
2. **Deterministic variants**: Predictable noise injection with known parameters
3. **Observable AI behavior**: AI rewrite generation with full logging of failures
4. **Adaptive execution**: Stop early when stable, repeat when interesting
5. **Evidence-based decisions**: Data to determine module scope limits, not guesswork
6. **Minimal coupling**: Harness respects Ironclad's single-string interface
7. **Future-proof**: Aggregates computed separately from immutable summaries

The system is designed to answer these questions:

- Does the same prompt converge consistently?
- How sensitive is the system to small changes?
- Where does repair stop helping?
- At what complexity does failure become structural rather than stochastic?
- Is failure stochastic or systematic?

Without ever needing to re-run Ironclad.
