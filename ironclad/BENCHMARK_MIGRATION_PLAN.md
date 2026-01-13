# Canonical Workload Migration Plan

## Executive Summary

Transforms benchmarking system from a three-mode architecture (baseline/adversarial/stress) to a single **canonical workload** focused on function-level reliability validation.

## Goal

Establish a statistically defensible **≥99% reliability claim** for the function constructor layer using a frozen corpus of 30 realistic function-level instructions, organized by complexity class.

---

## Canonical Workload - Understanding

### What It Is

A **frozen corpus of 30 function-level instructions** representing a realistic complexity class of coding tasks. These instructions:

- Are concrete, specific commands (not placeholder examples)
- Describe exactly ONE function responsibility each
- Are written as natural-language instructions (how a user would phrase it)
- Execute via: `python -m ironclad_ai_guardrails.ironclad "<instruction>"`

### Structure: 3 Complexity Classes

```
30 total instructions
  ├── 6 small complexity functions (target: 100% reliability)
  ├── 10 mid complexity functions (target: 99% reliability)
  └── 14 large complexity functions (target: 98% reliability)

**Note for test version:** The canonical workload is being implemented with 2 representative functions (1 small, 1 mid) for validation purposes. Expand to full 30 instructions after confirming system functionality.

### Phase Scope: Function Constructor Layer Only

**Active:**
- Function implementation from instructions
- Unit test generation and validation
- Repair logic
- Brick file creation

**NOT Active Yet:**
- Module definer layer (designing function sets)
- Supervisor layer (orchestration and decision making)
- Adversarial testing (instruction perturbations)
- Stress testing (synthetic difficulty progression)

**Note:** For code testing purposes, this migration will use a **minimal canonical workload of 2 functions, each run 2 times** to validate benchmark system functionality without requiring full 300 trial execution.

### Benchmarking Protocol

```
For each of 30 instructions:
    Run 10 times → Total: 300 trials
    Each trial = Bernoulli (pass/fail)
    Aggregate results → Compute success rate + 95% CI
    Target: Prove ≥99% reliability with statistical confidence
```

### Reliability Calculation

If we run 300 trials and get:
- **0 failures** → 100% success rate → Can claim ≥99% reliability
- **1 failure** → 99.67% success rate → Near threshold
- **2 failures** → 99.33% success rate → Near threshold
- **≥3 failures** → 98% success rate → Below 99% threshold

### What Replaces Current System

| Current | New | Reason |
|----------|-------|---------|
| 3 modes (baseline/adversarial/stress) | 1 mode (canonical) | Simplify before calcifying |
| Stress suite (synthetic ladder) | Large complexity class (14 instructions) | Complexity scales naturally |
| Adversarial suite (perturbations) | Disabled for now | Redefine when all 3 layers functional |
| Baseline (3 examples) | Canonical (30 instructions) | Full workload, not examples |

### Key Insight

The canonical workload concept **preserves the same underlying benchmark corpus** (the 30 functions) but changes how we measure them:

- **Before:** Same 3 functions, tested 3 ways (baseline, adversarial variants, stress ladder)
- **After:** 30 functions, tested 1 way (repetition for statistical confidence)

This aligns with the directive: "Freeze a realistic 30-function workload and use it to statistically prove function constructor layer reliability."

---

## PART 1: Core Architecture Changes

### 1.1 Simplify run.py Mode Handling

**Current state:** Three separate modes (baseline, adversarial, stress) with different code paths

**New state:** Single mode `canonical` with optional complexity filtering

**Changes required:**

1. **Remove mode switching logic** (`benchmarks/run.py:307-314`)
   - Delete `if mode == 'baseline':`, `elif mode == 'adversarial':`, `elif mode == 'stress':`
   - Replace with single execution path

2. **Simplify suite runner** - Remove `run_adversarial_suite()` and `run_stress_suite()` functions
   - Keep only `run_baseline_suite()` (rename to `run_canonical_suite()`)
   - Remove adversarial-specific code (lines 160-220)
   - Remove stress-specific code (lines 222-267)

3. **Update dry-run logic** (lines 282-301)
   - Remove adversarial and stress suite processing
   - Only process canonical suite files

### 1.2 Update Suite Schema

**Current schema:** Three separate schemas for baseline, adversarial, stress

**New schema:** Single unified schema with complexity metadata

```yaml
suite_id: string
mode: canonical
runs_per_case: integer      # How many times to run each instruction (default: 10)
timeout_seconds: integer         # Per-run timeout (default: 300)
repair_enabled: boolean          # Whether to allow Ironclad's repair cycle (default: true)
debug_enabled: boolean           # Whether IRONCLAD_DEBUG=1 should be set (default: true)

cases:
  - id: string
    complexity: small|mid|large
    category: string         # Optional: grouping for reporting
    instruction: string
```

### 1.3 Update Output Directory Structure

**Current structure:**
```
benchmarks/outputs/run_YYYYMMDD_HHMMSS/
  baseline/
    <case_id>/...
  adversarial/
    <case_id>/<generator_name>/...
  stress/
    <case_id>/level_<N>/...
```

**New structure:**
```
benchmarks/outputs/run_YYYYMMDD_HHMMSS/
  canonical/
    small/
      <case_id>/
        run_001/summary.json
        run_002/summary.json
        ...
        aggregate.json
    mid/
      <case_id>/...
    large/
      <case_id>/...
  metadata.json
```

### 1.4 Add Complexity Filtering (Optimized Execution)

**Purpose:** Allow faster development iteration by testing subset of workload

**Implementation:**

Add to argparse in `benchmarks/run.py`:

```python
parser.add_argument(
    "--filter",
    choices=["small", "mid", "large", "all"],
    default="all",
    help="Filter by complexity class (default: all)"
)
```

Handle in `run_canonical_suite()`:

```python
complexity_filter = args.filter  # 'all' or 'small' or 'mid' or 'large'

if complexity_filter != 'all':
    all_cases = (
        suite.get('small', []) +
        suite.get('mid', []) +
        suite.get('large', [])
    )
    filtered_cases = [c for c in all_cases if c.get('complexity') == complexity_filter]
    suite['cases'] = filtered_cases
```

---

## PART 2: Minimal Canonical Workload Definition

### 2.1 Create canonical.yaml Suite File (Test Version)

**Location:** `benchmarks/suites/canonical.yaml`

**Purpose:** Minimal workload for code testing (2 functions, each run 2 times)

**Content:** 2 representative instructions from different complexity classes

```yaml
suite_id: canonical_test_v1
mode: canonical
runs_per_case: 2
timeout_seconds: 300
repair_enabled: true
debug_enabled: true

small:
  - id: compile_email_regex
    complexity: small
    instruction: "Compile a list of email patterns into regex objects."

mid:
  - id: convert_list_to_dict
    complexity: mid
    instruction: "Convert a list of dictionaries into a dictionary keyed by id."
```

  **Note:** This is a minimal test workload. Replace with full 30-instruction canonical.yaml when system is validated.

### 2.2 Test Workload (Current)

**For production:** Use the following structure with all 30 instructions

[This section is reserved for full 30-function canonical.yaml - to be implemented after validation]

### 2.3 Full Canonical Workload Reference (Production)

**For production:** Use the following structure with all 30 instructions

```yaml
suite_id: canonical_v1
mode: canonical
runs_per_case: 10
timeout_seconds: 300
repair_enabled: true
debug_enabled: true

small:
  - id: compile_email_regex
    complexity: small
    instruction: "Compile a list of email patterns into regex objects."

  - id: parse_user_input
    complexity: small
    instruction: "Parse raw user input into a normalized dictionary with consistent key names and types."

  - id: validate_required_fields
    complexity: small
    instruction: "Validate that required fields are present in a configuration object and return structured errors if they are missing."

  - id: coerce_config_values
    complexity: small
    instruction: "Coerce configuration values into expected data types where possible and report conversion failures."

  - id: normalize_user_identifiers
    complexity: small
    instruction: "Normalize user identifiers into a canonical lowercase format with invalid characters removed."

  - id: build_error_report
    complexity: small
    instruction: "Build a structured error report from a list of validation errors."

mid:
  - id: convert_list_to_dict
    complexity: mid
    instruction: "Convert a list of dictionaries into a dictionary keyed by id."

  - id: enqueue_task
    complexity: mid
    instruction: "Enqueue a task with metadata into an in-memory queue structure."

  - id: dequeue_task
    complexity: mid
    instruction: "Dequeue next eligible task from an in-memory queue."

  - id: inspect_queue
    complexity: mid
    instruction: "Inspect current state of a task queue without modifying it."

  - id: clear_queue
    complexity: mid
    instruction: "Clear all entries from an in-memory queue safely."

  - id: record_timestamp
    complexity: mid
    instruction: "Record an action timestamp for rate limiting purposes."

  - id: check_rate_limit
    complexity: mid
    instruction: "Determine whether an action should be rate limited based on recent activity."

  - id: remove_expired_records
    complexity: mid
    instruction: "Remove expired rate limit records from in-memory state."

  - id: execute_task
    complexity: mid
    instruction: "Execute a queued task with basic error handling and status reporting."

  - id: retry_failed_task
    complexity: mid
    instruction: "Retry a failed task according to a retry policy and requeue it if appropriate."

large:
  - id: load_config
    complexity: large
    instruction: "Load configuration data from a file path or dictionary source."

  - id: apply_env_overrides
    complexity: large
    instruction: "Apply environment variable overrides to configuration values."

  - id: validate_config
    complexity: large
    instruction: "Validate that a configuration object is internally consistent and complete."

  - id: ingest_records
    complexity: large
    instruction: "Ingest input records from a provided data source."

  - id: filter_records
    complexity: large
    instruction: "Filter input records according to configurable rules."

  - id: group_records
    complexity: large
    instruction: "Group input records into batches for processing."

  - id: transform_record
    complexity: large
    instruction: "Transform a single record according to transformation rules."

  - id: enrich_record
    complexity: large
    instruction: "Enrich a record with derived or computed fields."

  - id: process_batch
    complexity: large
    instruction: "Process a batch of records and collect processing results."

  - id: handle_errors
    complexity: large
    instruction: "Handle and classify processing errors consistently."

  - id: write_records
    complexity: large
    instruction: "Write processed records to an output destination."

  - id: generate_statistics
    complexity: large
    instruction: "Summarize processing results into aggregate statistics."

  - id: run_pipeline
    complexity: large
    instruction: "Run full data processing pipeline from ingestion through output."

  - id: generate_report
    complexity: large
    instruction: "Generate a structured report describing the results of a pipeline run."
```

### 2.3 Complexity Categories

**Small (6):** Simple functions, single responsibility
- Characteristic: < 5 lines of logic typically
- Target: 100% reliability

**Mid (10):** Moderate complexity, some state management
- Characteristic: 5-15 lines of logic
- Target: 99% reliability

**Large (14):** Complex functions, multiple responsibilities
- Characteristic: > 15 lines of logic
- Target: 98% reliability

**Test Workload (Current):** 2 functions (1 small, 1 mid) × 2 runs = 4 total trials

---

## PART 3: File Cleanup Actions

### 3.1 Remove Suite Files

**Delete:**
- `benchmarks/suites/stress.yaml` → Delete entirely
- `benchmarks/suites/adversarial.yaml` → Archive (not delete conceptually)
- `benchmarks/suites/baseline.yaml` → Keep temporarily, replace with canonical.yaml

### 3.2 Archive Adversarial Logic

**Action:** Move adversarial suite to archive location (preserve for future redefinition)

```bash
mkdir -p benchmarks/suites/.archived
mv benchmarks/suites/adversarial.yaml benchmarks/suites/.archived/
```

**Rationale:** Preserve hooks for future redefinition when all three AI layers are functional

### 3.3 Clean up run.py

**Remove functions:**
- `run_adversarial_suite()` (lines ~160-220)
- `run_stress_suite()` (lines ~222-267)

**Remove imports:**
- Any references to adversarial/stress-specific logic if isolated

---

## PART 4: Brick Cleanup Strategy (Ironclad Bug Workaround)

### 4.1 Permanent Workaround for Ironclad Hanging Bug

**Issue:** Ironclad hangs when `verified_bricks/<name>.py` file already exists from a previous run with same instruction.

**Solution:** Implement permanent cleanup function called before each Ironclad invocation.

**Implementation in `benchmarks/run.py`:**

```python
def clean_verified_bricks():
    """Clean up brick files to avoid Ironclad hanging on existing files.

    This works around an Ironclad bug where it hangs if a brick file
    from a previous run with the same instruction already exists.
    """
    verified_bricks_path = Path("verified_bricks")
    if verified_bricks_path.exists():
        deleted_count = 0
        for brick_file in verified_bricks_path.glob("*.py"):
            try:
                brick_file.unlink()
                deleted_count += 1
            except Exception as e:
                print(f"    [!] Warning: could not delete {brick_file}: {e}")
        if deleted_count > 0:
            print(f"    [*] Cleaned up {deleted_count} existing brick files")
```

**Integration:** Call `clean_verified_bricks()` at the start of `run_ironclad()` function:

```python
def run_ironclad(instruction: str, timeout: int = 60, debug: bool = False) -> dict:
    """Run Ironclad with the given instruction."""
    nonlocal run_counter
    run_counter += 1
    run_id = f"run_{run_counter:03d}"

    # Clean up existing brick files (Ironclad bug workaround)
    clean_verified_bricks()

    # ... rest of function ...
```

**Rationale:** This is a permanent workaround to the Ironclad bug. It ensures clean state for each run.

---

## PART 5: Documentation Updates

### 5.1 Rewrite benchmarks/README.md

**New structure:**

```markdown
# Ironclad Benchmark System (Canonical Workload)

## Overview

This benchmark system treats Ironclad as a black-box function: it receives a single instruction string as input and produces an outcome with artifacts.

**Current Phase:** Function Constructor Layer Benchmarking

The system is focused on validating reliability for a **canonical workload of 30 function-level instructions** that represent a realistic complexity class of coding tasks.

### Phase Goal

Establish, with statistical confidence, that the function constructor layer achieves **≥99% reliability** for this workload class.

## Canonical Workload

The canonical workload consists of 30 concrete function-level instructions, organized by complexity:

- **Small complexity (6 instructions):** Simple functions with single responsibility
- **Mid complexity (10 instructions):** Moderate complexity with state management
- **Large complexity (14 instructions):** Complex functions with multiple responsibilities

These instructions are **frozen and versioned**. They define the entire benchmark corpus for this phase.

## Execution Protocol

### Single-String Contract

**Rule:** Every benchmark case contains ONLY an instruction string.

- `id`: Unique identifier
- `complexity`: small|mid|large
- `instruction`: The EXACT string passed to Ironclad CLI

The instruction string must NOT mention:
- Tests, testing, pytest
- Coverage, code coverage
- Validation, performance, optimization
- Tooling, harnessing, benchmarking, logging

### Benchmark Execution

For each canonical instruction:

1. Run the instruction 10 times
2. Treat each run as a Bernoulli trial (pass/fail)
3. Aggregate results for statistical analysis
4. Target: ≥99% reliability with 95% statistical confidence

### CLI Usage

```bash
# Run full canonical workload (30 instructions × 10 runs = 300 total)
python benchmarks/run.py --suite benchmarks/suites/canonical.yaml

# Run specific complexity class for faster development iteration
python benchmarks/run.py --suite benchmarks/suites/canonical.yaml --filter small
python benchmarks/run.py --suite benchmarks/suites/canonical.yaml --filter mid
python benchmarks/run.py --suite benchmarks/suites/canonical.yaml --filter large

# Dry run (no Ironclad execution)
python benchmarks/run.py --dry-run

# Override timeout
python benchmarks/run.py --timeout 600
```

### Optimized Development Workflow

Use `--filter` flag during development to iterate faster:

- `--filter small`: 6 cases × 10 runs = 60 runs (~1 hour)
- `--filter mid`: 10 cases × 10 runs = 100 runs (~1.5 hours)
- `--filter large`: 14 cases × 10 runs = 140 runs (~2.5 hours)

Full validation (no filter): 300 runs (~5 hours)

## Output Format

### Per-Run Summary (summary.json)

```json
{
  "run_id": "run_001",
  "complexity": "small",
  "case_id": "compile_email_regex",
  "instruction": "Compile a list of email patterns into regex objects.",
  "instruction_hash": "sha256:...",
  "instruction_length": 56,
  "success": true|false,
  "failure_stage": "generation|validation|repair|unknown",
  "attempts": 1,
  "repairs_triggered": 0,
  "duration_ms": 4123,
  "timestamp_utc": "2026-01-12T...",
  "ironclad_version": "git:..."
}
```

### Aggregate by Complexity (aggregate.json)

```json
{
  "complexity": "small",
  "total_cases": 6,
  "total_runs": 60,
  "successes": 59,
  "failures": 1,
  "success_rate": 0.9833,
  "confidence_interval_95": [0.920, 0.999],
  "avg_duration_ms": 3892,
  "p95_duration_ms": 6210
}
```

### Confidence Interval Calculation

Uses Wilson score interval for binomial proportions (95% confidence):

```python
def compute_wilson_ci(successes, total, confidence=0.95):
    """Compute Wilson score interval for binomial proportion."""
    p = successes / total
    z = 1.96  # For 95% CI
    denominator = 1 + z**2 / total
    center = (p + z**2 / (2 * total)) / denominator
    margin = z * math.sqrt(p * (1 - p) / total + z**2 / (4 * total**2)) / denominator
    return [center - margin, center + margin]
```

## Future Phases (Not Yet Active)

### Module Definer Layer
Will use the same 30 function capabilities to elicit module design decisions.

### Supervisor Layer
Will use large project definitions to test orchestration and decision making.

### Adversarial Testing
Will be redefined when all three AI decision layers are functional to test cross-layer robustness.

## Directory Structure

```
benchmarks/
  README.md                    # This file
  suites/
    canonical.yaml           # Canonical workload (30 instructions)
    baseline.yaml            # Legacy (to be removed)
    .archived/
      adversarial.yaml      # Archived for future redefinition
  outputs/
    run_YYYYMMDD_HHMMSS/
      metadata.json
      canonical/
        small/
          <case_id>/
            run_001/summary.json
            aggregate.json
        mid/
          <case_id>/...
        large/
          <case_id>/...
  generators/
    README.md
    *.py                    # Kept for future adversarial redefinition
```

## Generator Catalog

> **NOTE:** The following generators are temporarily disabled during the canonical workload phase.
> They will be re-enabled when all three AI decision layers are functional.

### Deterministic Generators (Currently Disabled)

[Keep existing documentation but add disabled note...]

### AI-Based Generators (Currently Disabled)

[Keep existing documentation but add disabled note...]
```

### 5.2 Update Generators Documentation

Add note to `benchmarks/generators/README.md`:

> **NOTE:** AI-based generators are temporarily disabled during canonical workload phase.
> They will be re-enabled when all three AI decision layers (functional, module, supervisor) are operational.

---

## PART 6: Statistical Analysis Implementation

### 6.1 Confidence Interval Calculation

**Function:** `compute_wilson_ci(successes, total, confidence=0.95)`

**Location:** Add to `benchmarks/run.py` imports section:

```python
import math
```

**Rationale:** Wilson score interval provides accurate confidence bounds for binomial proportions, especially important for small sample sizes.

### 6.2 Aggregate Statistics Generation

Update `run_canonical_suite()` to generate `aggregate.json`:

```python
def generate_aggregate_stats(cases: list, complexity: str) -> dict:
    """Generate aggregate statistics for a complexity class."""
    total_runs = 0
    total_successes = 0
    durations = []

    for case in cases:
        for run_id in sorted(Path(case_dir).glob("run_*")):
            with open(run_dir / 'summary.json') as f:
                summary = json.load(f)
                total_runs += 1
                total_successes += 1 if summary['success'] else 0
                durations.append(summary['duration_ms'])

    if total_runs == 0:
        return {"error": "No runs found"}

    success_rate = total_successes / total_runs
    ci = compute_wilson_ci(total_successes, total_runs, confidence=0.95)

    return {
        "complexity": complexity,
        "total_cases": len(cases),
        "total_runs": total_runs,
        "successes": total_successes,
        "failures": total_runs - total_successes,
        "success_rate": success_rate,
        "confidence_interval_95": ci,
        "avg_duration_ms": sum(durations) / len(durations),
        "p95_duration_ms": sorted(durations)[int(len(durations) * 0.95)]
    }
```

---

## PART 7: Test Updates

### 7.1 Update Test Suite

**File:** `tests/test_benchmarks/test_run_cli.py`

**Changes:**

1. Remove skipped tests (lines 11-68)
2. Add new test for canonical mode:

```python
@patch('benchmarks.run.load_suite')
@patch('benchmarks.run.argparse.ArgumentParser')
def test_main_canonical_mode(self, mock_parser_class, mock_load_suite):
    """Test main() with canonical suite."""
    mock_parser = MagicMock()
    mock_parser.parse_args.return_value = MagicMock(
        suite='benchmarks/suites/canonical.yaml',
        output_dir='benchmarks/outputs',
        dry_run=True,
        model='ollama',
        max_failures=None,
        timeout=None,
        filter='all'
    )
    mock_parser_class.return_value = mock_parser
    mock_load_suite.return_value = {
        'suite_id': 'canonical_v1',
        'mode': 'canonical',
        'small': [...],
        'mid': [...],
        'large': [...]
    }

    benchmarks.run.main()
```

3. Test complexity filtering:

```python
def test_main_with_complexity_filter(self):
    """Test --filter flag for complexity class."""
    # Test filtering by small/mid/large
```

### 7.2 Integration Test

**Create:** `tests/test_benchmarks/test_canonical_workload.py`

```python
class TestCanonicalWorkload(unittest.TestCase):
    """Test canonical workload definition."""

    def test_all_30_instructions_defined(self):
        """Verify all 30 instructions are in canonical.yaml (full version)."""
        # This tests the full 30-instruction workload
        pass

    def test_minimal_2_instructions_defined(self):
        """Verify minimal 2 instructions are in canonical.yaml (test version)."""
        with open('benchmarks/suites/canonical.yaml', 'r') as f:
            suite = yaml.safe_load(f)
        total_cases = (
            len(suite.get('small', [])) +
            len(suite.get('mid', [])) +
            len(suite.get('large', []))
        )
        self.assertEqual(total_cases, 2)

    def test_no_references_to_deleted_suites(self):
        """Ensure adversarial and stress are not referenced."""
        # Verify canonical.yaml doesn't reference deleted concepts
```

---

## PART 8: Execution Checklist

### Phase 1: Cleanup
- [ ] Delete `benchmarks/suites/stress.yaml`
- [ ] Archive `benchmarks/suites/adversarial.yaml` to `.archived/`
- [ ] Remove `run_adversarial_suite()` from run.py
- [ ] Remove `run_stress_suite()` from run.py
- [ ] Update README.md to reflect new architecture

### Phase 2: Implementation (Test Version)
- [ ] Create `benchmarks/suites/canonical.yaml` with 2 test functions
- [ ] Implement `run_canonical_suite()` in run.py
- [ ] Add `clean_verified_bricks()` function for Ironclad bug workaround
- [ ] Update mode handling in main() to only support 'canonical' mode
- [ ] Update output directory structure to group by complexity
- [ ] Generate aggregate.json per complexity class
- [ ] Add `--filter` CLI argument for complexity filtering
- [ ] Implement `compute_wilson_ci()` for statistical confidence intervals
- [ ] Update dry-run logic to process only canonical suite

### Phase 3: Testing
- [ ] Update `test_run_cli.py` to remove skipped tests
- [ ] Add tests for canonical mode
- [ ] Add tests for complexity filtering
- [ ] Create `test_canonical_workload.py` integration test
- [ ] Run full test suite: `pytest tests/test_benchmarks/`

### Phase 4: Validation
- [ ] Run dry run: `python benchmarks/run.py --dry-run`
- [ ] Run small subset: `python benchmarks/run.py --filter small`
- [ ] Verify output structure matches new schema
- [ ] Check that 300 runs would execute (30 × 10)

---

## PART 9: Rollback Strategy

**If migration fails:**

1. Restore from git:
   ```bash
   git checkout benchmarks/suites/
   git checkout benchmarks/run.py
   git checkout benchmarks/README.md
   ```

2. Keep archived adversarial.yaml for future use

3. Tests should pass with original architecture

---

## PART 10: Success Criteria

**Migration complete when (Test Version):**

1. 2 canonical instructions defined in `benchmarks/suites/canonical.yaml`
2. No references to adversarial or stress modes in run.py
3. Single `run_canonical_suite()` function handles all execution
4. Output structure groups by complexity (small/mid/large)
5. `--filter` flag implemented for complexity filtering
6. Brick cleanup workaround implemented as permanent fix
7. Wilson confidence interval calculation implemented
8. All tests pass (including new canonical workload tests)
9. Dry run executes without errors
10. README.md reflects new canonical workload architecture
11. `stress.yaml` deleted and `adversarial.yaml` archived

**Migration complete when (Full Production Version):**

1. All 30 canonical instructions defined in `benchmarks/suites/canonical.yaml`
2. No references to adversarial or stress modes in run.py
3. Single `run_canonical_suite()` function handles all execution
4. Output structure groups by complexity (small/mid/large)
5. `--filter` flag implemented for complexity filtering
6. Brick cleanup workaround implemented as permanent fix
7. Wilson confidence interval calculation implemented
8. All tests pass (including new canonical workload tests)
9. Dry run executes without errors
10. README.md reflects new canonical workload architecture
11. `stress.yaml` deleted and `adversarial.yaml` archived

---

## Summary of Changes

| Component | Change | Lines Added | Lines Removed |
|------------|--------|---------------|----------------|
| `benchmarks/suites/` | Delete stress.yaml, archive adversarial.yaml, create canonical.yaml (test version) | ~60 | ~200 |
| `benchmarks/run.py` | Remove adversarial/stress logic, add canonical mode, add filtering, add CI calc | ~200 | ~150 |
| `benchmarks/README.md` | Rewrite for canonical workload | ~350 | ~600 |
| `tests/test_benchmarks/` | Update tests, add canonical tests | ~120 | ~50 |

**Net change (Test Version):** ~730 lines added, ~1000 lines removed

**Result:** Minimal test workload validates benchmark system functionality.

**Net change (Full Production Version):** ~920 lines added, ~1000 lines removed

**Result:** Simpler, focused architecture aligned with phase goal of proving function-level reliability.

---

## Open Questions for Future Phases

1. **Module definer benchmarking:** How will canonical instructions be used to test module design decisions?
2. **Supervisor benchmarking:** What orchestrations will be measured at this layer?
3. **Adversarial redefinition:** When all three AI layers are functional, what adversarial scenarios make sense?

These questions should be answered when those phases become active.

---

## Transition Timeline

**Estimated effort (Test Version - Current Work):**
- Phase 1-3 (Cleanup/Implementation): 2-3 hours
- Phase 4-5 (Testing/Validation): 1-2 hours
- Total: 3-5 hours

**Execution time (test version):**
- Test run (2 functions × 2 runs = 4 total): ~4 minutes

**Estimated effort (Full Production Version):**
- Phase 1-3 (Cleanup/Implementation): 4-6 hours
- Phase 4-5 (Testing/Validation): 2-3 hours
- Total: 6-9 hours

**Execution time (full production version):**
- Small filter: ~1 hour
- Mid filter: ~1.5 hours
- Large filter: ~2.5 hours
- Full run: ~5 hours

**Note:** This plan is structured for immediate implementation with a minimal 2-function test workload for validation. The full 30-function canonical workload should be implemented after confirming the system works correctly.
