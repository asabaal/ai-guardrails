"""
CLI interface for opencode-restore.
"""

import argparse
import sys
import textwrap
from pathlib import Path

from .config import (
    DEFAULT_MODEL,
    DEFAULT_MAX_LINES,
    DEFAULT_OUTPUT_FORMAT,
    get_default_output_path,
)
from .parser import LogParser
from .summarizer import create_ollama_summarizer
from .turn_parser import TurnParser
from .turn_summarizer import process_turns_incrementally
from .evidence_gatherer import run_agentic_evidence_gathering, EvidenceSearchTools


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""

    parser = argparse.ArgumentParser(
        description="Summarize an OpenCode .raw.log transcript into a session rehydration document",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          %(prog)s session.raw.log
          %(prog)s session.raw.log --model llama3
          %(prog)s session.raw.log --max-lines 800 --output custom_summary.md
        """)
    )

    parser.add_argument(
        "log_file",
        type=Path,
        help="Path to OpenCode .raw.log transcript file",
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
        help="Max number of transcript lines to include from the tail (default: %(default)s)",
    )

    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output file path (default: SUMMARY_<session>.md)",
    )

    parser.add_argument(
        "--format",
        choices=["md", "json"],
        default=DEFAULT_OUTPUT_FORMAT,
        help="Output format (default: %(default)s)",
    )

    parser.add_argument(
        "--dedupe",
        action="store_true",
        help="Remove consecutive duplicate lines from transcript",
    )

    parser.add_argument(
        "--include-header",
        action="store_true",
        help="Include script header info in summary",
    )

    parser.add_argument(
        "--max-turns",
        type=int,
        default=None,
        help="Limit number of turns to process",
    )

    parser.add_argument(
        "--skip-evidence-search",
        action="store_true",
        help="Skip agentic evidence gathering phase",
    )

    parser.add_argument(
        "--max-searches",
        type=int,
        default=None,
        help="Max evidence search iterations (default: 8)",
    )

    parser.add_argument(
        "--dump-turns",
        action="store_true",
        help="Output turn-by-turn summaries instead of aggregated",
    )

    return parser


def main() -> int:
    """Main CLI entry point."""

    parser = create_parser()
    args = parser.parse_args()

    if not args.log_file.exists():
        print(f"[!] Error: Log file not found: {args.log_file}", file=sys.stderr)
        return 1

    session_name = args.session_name or args.log_file.stem.replace(".raw", "")
    out_path = Path(args.out or get_default_output_path(session_name, args.format)).absolute()

    try:
        print(f"[opencode-restore] Parsing log file: {args.log_file}")
        log_parser = LogParser()
        parsed = log_parser.parse_file(args.log_file)

        if args.dedupe:
            parsed.content = log_parser.deduplicate_content(parsed.content)

        turn_parser = TurnParser()
        turns = turn_parser.parse_turns(parsed.content)

        if args.max_turns:
            turns = turns[:args.max_turns]

        print(f"[opencode-restore] Found {len(turns)} turns in transcript")
        print(f"[opencode-restore] Running model: {args.model}")
        summarizer = create_ollama_summarizer(args.model)

        turn_summaries, accumulated_state = process_turns_incrementally(
            turns=turns,
            backend=summarizer.backend,
            session_name=session_name,
        )

        if args.dump_turns:
            dump_path = out_path.parent / f"TURNS_{out_path.name}"
            dump_turns_to_file(turn_summaries, dump_path)
            print(f"[opencode-restore] Wrote turn summaries to: {dump_path}")

        if not args.skip_evidence_search:
            print(f"[opencode-restore] Running agentic evidence gathering...")
            search_tools = EvidenceSearchTools(
                log_path=args.log_file,
                repo_root=args.log_file.parent,
                artifacts=accumulated_state.get('artifacts', set()),
            )

            if args.max_searches:
                search_tools.max_searches = args.max_searches

            final_summary = run_agentic_evidence_gathering(
                turn_summaries=turn_summaries,
                accumulated_state=accumulated_state,
                backend=summarizer.backend,
                search_tools=search_tools,
                session_name=session_name,
            )

            if args.include_header and parsed.header:
                header_info = textwrap.dedent(f"""
                <!-- Script Header -->
                - Timestamp: {parsed.header.timestamp}
                - Command: {parsed.header.command}
                - Working Directory: {parsed.header.tty}

                """)
                final_summary = header_info + final_summary

            out_path.write_text(final_summary + "\n", encoding="utf-8")
            print(f"[opencode-restore] Wrote final session summary to: {out_path}")
        else:
            summary = synthesize_summary_from_accumulated_state(
                accumulated_state=accumulated_state,
                session_name=session_name,
            )

            if args.include_header and parsed.header:
                header_info = textwrap.dedent(f"""
                <!-- Script Header -->
                - Timestamp: {parsed.header.timestamp}
                - Command: {parsed.header.command}
                - Working Directory: {parsed.header.tty}

                """)
                summary = header_info + summary

            out_path.write_text(summary + "\n", encoding="utf-8")
            print(f"[opencode-restore] Wrote session summary to: {out_path}")

        return 0

    except FileNotFoundError as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        return 1
    except RuntimeError as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[!] Unexpected error: {e}", file=sys.stderr)
        return 1


def dump_turns_to_file(turn_summaries, output_path):
    """Dump turn summaries to a separate file."""

    content = "TURN-BY-TURN SUMMARIES\n\n"

    for summary in turn_summaries:
        content += f"""
Turn {summary.get('turn_number', 'N/A')}
─────────────────────────────────
User request: {summary.get('user_request_summary', 'N/A')}
Agent response: {summary.get('agent_response_summary', 'N/A')}
Key outcomes: {summary.get('key_outcomes', 'N/A')}
State changes: {summary.get('state_changes', 'N/A')}
Artifacts modified: {', '.join(summary.get('artifacts_modified', []))}
Constraints/assumptions: {', '.join(summary.get('constraints_added', []))}
Open questions: {', '.join(summary.get('open_questions', []))}
─────────────────────────────────
"""

    output_path.write_text(content, encoding="utf-8")


def synthesize_summary_from_accumulated_state(accumulated_state, session_name):
    """Synthesize final session summary from accumulated state."""

    high_level_goal = accumulated_state.get('high_level_goal', 'Not established')
    primary_task = accumulated_state.get('key_decisions', ['Not established'])[-1] if accumulated_state.get('key_decisions') else 'Not established'

    key_decisions_text = accumulated_state.get('key_decisions', ['Not explicitly stated'])
    constraints_text = accumulated_state.get('constraints', ['Not explicitly stated'])
    artifacts_text = list(accumulated_state.get('artifacts', set())) or ['Not explicitly stated']
    questions_text = accumulated_state.get('open_questions', ['Not explicitly stated'])

    if not artifacts_text or artifacts_text == ['Not explicitly stated']:
        artifacts_text = ['Not explicitly stated']
    else:
        artifacts_text = [str(a) for a in artifacts_text]

    return textwrap.dedent(f"""
SESSION SUMMARY

Session name:
- {session_name}

High-level goal:
- {high_level_goal}

Primary task in progress:
- {primary_task}

Key decisions already made:
{chr(10).join(f'- {d}' for d in key_decisions_text)}

Constraints and assumptions:
{chr(10).join(f'- {c}' for c in constraints_text)}

Artifacts referenced or created:
{chr(10).join(f'- {a}' for a in artifacts_text)}

Open questions:
{chr(10).join(f'- {q}' for q in questions_text)}

Next concrete steps:
- Continue from last turn with resolved open questions
""")
