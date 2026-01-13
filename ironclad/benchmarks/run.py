#!/usr/bin/env python3
"""
Benchmark runner CLI entry point.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import subprocess
import json
import time
import hashlib
import math
from datetime import datetime, timezone
import yaml

from benchmarks import generators

run_counter = 0

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

def run_ironclad(instruction: str, timeout: int = 60, debug: bool = False) -> dict:
    """Run Ironclad with the given instruction."""
    global run_counter
    run_counter += 1
    run_id = f"run_{run_counter:03d}"

    # Clean up existing brick files (Ironclad bug workaround)
    clean_verified_bricks()

    env = None
    if debug:
        import os
        env = os.environ.copy()
        env["IRONCLAD_DEBUG"] = "1"

    start_time = time.time()
    result = subprocess.run(
        ["python", "-m", "ironclad_ai_guardrails.ironclad", instruction],
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env
    )
    duration_ms = int((time.time() - start_time) * 1000)

    instruction_hash = hashlib.sha256(instruction.encode()).hexdigest()[:12]

    summary = {
        "run_id": run_id,
        "instruction_hash": f"sha256:{instruction_hash}",
        "instruction_length": len(instruction),
        "success": result.returncode == 0,
        "failure_stage": "unknown",
        "attempts": 1,
        "repairs_triggered": 0,
        "duration_ms": duration_ms,
        "debug_enabled": debug,
        "debug_artifacts_present": False,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "stdout": result.stdout,
        "stderr": result.stderr,
    }

    if result.returncode != 0:
        if "FAIL" in result.stderr:
            summary["failure_stage"] = "generation"
        elif "repair" in result.stderr:
            summary["failure_stage"] = "repair"
        else:
            summary["failure_stage"] = "validation"

    return summary

def load_suite(suite_path: str) -> dict:
    """Load YAML suite configuration."""
    with open(suite_path, 'r') as f:
        return yaml.safe_load(f)

def run_canonical_suite(suite: dict, output_dir: Path, args: argparse.Namespace):
    """Run canonical suite - consistent instructions multiple times."""
    print(f"[*] Running canonical suite: {suite['suite_id']}")
    print(f"[*] Mode: canonical, Runs per case: {suite.get('runs_per_case', 10)}")

    complexity_filter = args.filter
    runs = suite.get('runs_per_case', 10)
    timeout = args.timeout or suite.get('timeout_seconds', 60)
    repair = suite.get('repair_enabled', True)

    all_cases = []
    if complexity_filter == 'all':
        all_cases = (
            suite.get('small', []) +
            suite.get('mid', []) +
            suite.get('large', [])
        )
    else:
        all_cases = suite.get(complexity_filter, [])

    for case in all_cases:
        case_id = case['id']
        complexity = case.get('complexity', 'unknown')
        instruction = case.get('instruction', '').strip()
        print(f"\n[*] Case: {case_id} ({complexity})")
        print(f"[*] Instruction: \"{instruction}\"")

        case_dir = output_dir / suite['suite_id'] / complexity / case_id
        case_dir.mkdir(parents=True, exist_ok=True)

        for i in range(runs):
            print(f"    [*] Run {i+1}/{runs}...", end='', flush=True)
            summary = run_ironclad(instruction, timeout, repair)
            summary['complexity'] = complexity

            run_dir = case_dir / summary['run_id']
            run_dir.mkdir(exist_ok=True)

            with open(run_dir / 'summary.json', 'w') as f:
                json.dump(summary, f, indent=2)
            with open(run_dir / 'instruction.txt', 'w') as f:
                f.write(instruction)

            print(f" {summary['duration_ms']}ms, Success={summary['success']}")

def compute_wilson_ci(successes: int, total: int, confidence: float = 0.95) -> list:
    """Compute Wilson score interval for binomial proportion."""
    p = successes / total
    z = 1.96  # For 95% CI
    denominator = 1 + (z ** 2) / total
    center = (p + (z ** 2) / (2 * total)) / denominator
    margin = z * math.sqrt(p * (1 - p) / total + (z ** 2) / (4 * total ** 2)) / denominator
    return [center - margin, center + margin]

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run Ironclad benchmark suites",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--suite",
        help="Suite file to run (default: run canonical suite)",
    )
    parser.add_argument(
        "--output-dir",
        default="benchmarks/outputs",
        help="Output directory for benchmark results",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate instruction variants but don't run Ironclad",
    )
    parser.add_argument(
        "--model",
        default="ollama",
        help="AI model to use for AI-based generators",
    )
    parser.add_argument(
        "--max-failures",
        type=int,
        default=None,
        help="Stop benchmark after N AI generation failures (default: unlimited)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=None,
        help="Override suite timeout in seconds (default: use suite value)",
    )
    parser.add_argument(
        "--filter",
        choices=["small", "mid", "large", "all"],
        default="all",
        help="Filter by complexity class (default: all)",
    )

    args = parser.parse_args()

    output_path = Path(args.output_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = output_path / f"run_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    metadata = {
        "run_id": f"run_{timestamp}",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "output_dir": str(run_dir),
        "dry_run": args.dry_run,
        "model": args.model,
    }

    if args.dry_run:
        print("[!] DRY RUN MODE - generating variants but not running Ironclad")
        if args.suite:
            suite = load_suite(args.suite)
            print(f"[*] Suite: {suite['suite_id']}")
            print(f"[*] Mode: {suite['mode']}")
            complexity_filter = args.filter
            all_cases = []
            if complexity_filter == 'all':
                all_cases = (
                    suite.get('small', []) +
                    suite.get('mid', []) +
                    suite.get('large', [])
                )
            else:
                all_cases = suite.get(complexity_filter, [])

            for case in all_cases:
                print(f"[*] Case: {case.get('id', 'unknown')}")
        else:
            print("[*] Running canonical suite in dry run mode...")
            canonical_suite_file = "benchmarks/suites/canonical.yaml"
            if Path(canonical_suite_file).exists():
                suite = load_suite(canonical_suite_file)
                print(f"[*] Suite: {suite['suite_id']}")
                print(f"[*] Total cases: {len(suite.get('small', [])) + len(suite.get('mid', [])) + len(suite.get('large', []))}")
            else:
                print(f"[!] Canonical suite file not found: {canonical_suite_file}")
        with open(run_dir / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"[*] Dry run complete. Metadata saved to: {run_dir / 'metadata.json'}")
        return

    if args.suite:
        suite = load_suite(args.suite)
        mode = suite.get('mode', 'baseline')

        if mode == 'canonical':
            run_canonical_suite(suite, run_dir, args)
        else:
            print(f"[!] Unknown mode: {mode}")

        metadata['suite_id'] = suite['suite_id']
        metadata['mode'] = mode
    else:
        print("[*] Running canonical suite...")
        canonical_suite_file = "benchmarks/suites/canonical.yaml"
        if Path(canonical_suite_file).exists():
            suite = load_suite(canonical_suite_file)
            run_canonical_suite(suite, run_dir, args)
        else:
            print(f"[!] Canonical suite file not found: {canonical_suite_file}")

        with open(run_dir / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        metadata['total_runs'] = run_counter

    print(f"\n[*] Benchmark complete. {run_counter} total runs executed.")
    print(f"[*] Results saved to: {run_dir}")


if __name__ == "__main__":
    main()
