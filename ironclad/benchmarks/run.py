#!/usr/bin/env python3
"""
Benchmark runner CLI entry point.
"""

import argparse
import sys
from pathlib import Path




def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run Ironclad benchmark suites",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--suite",
        help="Suite file to run (default: run all suites)",
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

    args = parser.parse_args()

    if args.suite:
        pass
    else:
        print("[*] No suite specified, running all suites...")
        for suite_file in ["suites/baseline.yaml", "suites/adversarial.yaml", "suites/stress.yaml"]:
            if Path(suite_file).exists():
                pass
            else:
                print(f"[!] Suite file not found: {suite_file}")


if __name__ == "__main__":
    main()
