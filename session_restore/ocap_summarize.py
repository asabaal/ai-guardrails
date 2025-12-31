#!/usr/bin/env python3
"""
ocap_summarize.py

Parse an OpenCode .clean.txt transcript and produce a structured
session-state summary suitable for rehydrating a fresh agent.

Intended to be used with local Ollama models (default: gpt-oss20b).

First-draft bootstrap version.
"""

import argparse
import subprocess
import textwrap
from pathlib import Path

DEFAULT_MODEL = "gpt-oss20b"
DEFAULT_MAX_LINES = 600


SUMMARY_SCHEMA = """
You must produce a structured SESSION SUMMARY using the exact format below.

If information is missing or unclear, write: "Not explicitly stated".

FORMAT (do not add extra sections):

SESSION SUMMARY

Session name:
- <string>

High-level goal:
- <bullet>

Primary task in progress:
- <bullet>

Key decisions already made:
- <bullet list>

Constraints and assumptions:
- <bullet list>

Artifacts referenced or created:
- <bullet list>

Open questions:
- <bullet list>

Next concrete steps:
- <bullet list>
"""


def load_transcript(path: Path, max_lines: int) -> str:
    lines = path.read_text(errors="ignore").splitlines()
    if len(lines) > max_lines:
        lines = lines[-max_lines:]
    return "\n".join(lines)


def build_prompt(session_name: str, transcript: str) -> str:
    return textwrap.dedent(f"""
    You are a session recovery assistant.

    Your job is to reconstruct the CURRENT STATE of an interrupted
    OpenCode session from a transcript.

    Focus on intent, decisions, constraints, and next steps.
    Ignore UI noise, repetition, and dead ends.

    Session name: {session_name}

    {SUMMARY_SCHEMA}

    TRANSCRIPT (most recent portion):
    ----------------
    {transcript}
    ----------------
    """)


def run_ollama(model: str, prompt: str) -> str:
    proc = subprocess.run(
        ["ollama", "run", model],
        input=prompt,
        text=True,
        capture_output=True,
    )

    if proc.returncode != 0:
        raise RuntimeError(
            f"Ollama failed (exit {proc.returncode}):\n{proc.stderr}"
        )

    return proc.stdout.strip()


def main():
    parser = argparse.ArgumentParser(
        description="Summarize an OpenCode .clean.txt log into a session rehydration document"
    )
    parser.add_argument(
        "clean_log",
        type=Path,
        help="Path to OpenCode .clean.txt transcript",
    )
    parser.add_argument(
        "--session-name",
        type=str,
        default=None,
        help="Logical session name (defaults to filename stem)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"Ollama model to use (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--max-lines",
        type=int,
        default=DEFAULT_MAX_LINES,
        help="Max number of transcript lines to include from the tail",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output markdown file (default: SUMMARY_<session>.md)",
    )

    args = parser.parse_args()

    if not args.clean_log.exists():
        raise FileNotFoundError(args.clean_log)

    session_name = (
        args.session_name
        or args.clean_log.stem.replace(".clean", "")
    )

    out_path = args.out or Path(f"SUMMARY_{session_name}.md")

    transcript = load_transcript(args.clean_log, args.max_lines)
    prompt = build_prompt(session_name, transcript)

    print(f"[ocap-summarize] Running model: {args.model}")
    summary = run_ollama(args.model, prompt)

    out_path.write_text(summary + "\n")
    print(f"[ocap-summarize] Wrote session summary to: {out_path}")


if __name__ == "__main__":
    main()
