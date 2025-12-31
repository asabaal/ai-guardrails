"""
Evidence gathering tools for agentic search.
Provides LLM with tools to search log and files for evidence.
"""

import re
import textwrap
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .config import (
    AGENTIC_SEARCH_CONFIG,
    EVIDENCE_SEARCH_CONTINUE_PROMPT_TEMPLATE,
    EVIDENCE_SEARCH_PROMPT_TEMPLATE,
)


class EvidenceSearchTools:
    """Search tools for LLM-driven evidence gathering."""

    def __init__(
        self,
        log_path: Path,
        repo_root: Optional[Path],
        artifacts: Set[str],
    ):
        self.log_path = log_path
        self.repo_root = repo_root or log_path.parent
        self.artifacts = artifacts
        self.log_lines = log_path.read_text().splitlines()
        self.search_count = 0
        self.max_searches = AGENTIC_SEARCH_CONFIG['max_searches']
        self.context_lines = AGENTIC_SEARCH_CONFIG['search_context_lines']

    def search_log(self, pattern: str) -> str:
        """Search raw log for pattern, return matches with context."""

        if len(pattern) > AGENTIC_SEARCH_CONFIG['pattern_max_length']:
            return f"Error: Search pattern too long (max {AGENTIC_SEARCH_CONFIG['pattern_max_length']} chars)"

        try:
            regex = re.compile(pattern, re.IGNORECASE)
        except re.error as e:
            return f"Error: Invalid regex pattern - {e}"

        matches = []
        for i, line in enumerate(self.log_lines):
            match = regex.search(line)
            if match:
                start = max(0, i - self.context_lines)
                end = min(len(self.log_lines), i + self.context_lines + 1)
                context = self.log_lines[start:end]
                matches.append(f"Line {i}: {chr(10).join(context)}")

        if not matches:
            return f"No matches found for pattern: {pattern}"

        return f"Found {len(matches)} matches:\n" + "\n".join(matches[:20])

    def search_file(self, file_path: str, pattern: str) -> str:
        """Search specific file for pattern."""

        full_path = self.repo_root / file_path

        if not full_path.exists():
            return f"Error: File not found: {file_path}"

        if len(pattern) > AGENTIC_SEARCH_CONFIG['pattern_max_length']:
            return f"Error: Search pattern too long (max {AGENTIC_SEARCH_CONFIG['pattern_max_length']} chars)"

        try:
            regex = re.compile(pattern, re.IGNORECASE)
        except re.error as e:
            return f"Error: Invalid regex pattern - {e}"

        try:
            lines = full_path.read_text().splitlines()
        except Exception as e:
            return f"Error: Could not read file - {e}"

        matches = []
        for i, line in enumerate(lines):
            match = regex.search(line)
            if match:
                start = max(0, i - self.context_lines)
                end = min(len(lines), i + self.context_lines + 1)
                context = lines[start:end]
                matches.append(f"Line {i}: {chr(10).join(context)}")

        if not matches:
            return f"No matches found for pattern: {pattern} in {file_path}"

        return f"Found {len(matches)} matches in {file_path}:\n" + "\n".join(matches[:20])

    def read_file(self, file_path: str, line_range: Optional[str] = None) -> str:
        """Read file content (full or with line range)."""

        full_path = self.repo_root / file_path

        if not full_path.exists():
            return f"Error: File not found: {file_path}"

        try:
            lines = full_path.read_text().splitlines()
        except Exception as e:
            return f"Error: Could not read file - {e}"

        if line_range is None:
            if len(lines) > 200:
                return f"File {file_path} ({len(lines)} lines): First 200 lines:\n" + "\n".join(lines[:200]) + f"\n... and {len(lines) - 200} more lines"
            return f"File {file_path} ({len(lines)} lines):\n" + "\n".join(lines)

        try:
            parts = line_range.replace('(', '').replace(')', '').split('-')
            start = int(parts[0]) if len(parts) > 0 else 0
            end = int(parts[1]) if len(parts) > 1 else len(lines)

            start = max(0, start - 1)
            end = min(len(lines), end)

            if start >= len(lines):
                return f"Error: Line {start} is beyond file length ({len(lines)})"
        except (ValueError, IndexError) as e:
            return f"Error: Invalid line range format - {e}"

        content = lines[start:end]
        return f"File {file_path} lines {start+1}-{end}:\n" + "\n".join(content)

    def list_artifacts(self) -> str:
        """List all tracked artifacts from session."""

        if not self.artifacts:
            return "No artifacts tracked for this session."

        sorted_artifacts = sorted(self.artifacts)
        return f"Artifacts tracked ({len(sorted_artifacts)} files):\n" + "\n".join(f"  - {a}" for a in sorted_artifacts)

    def should_continue_search(self) -> bool:
        """Check if search limit reached."""

        return self.search_count < self.max_searches

    def increment_search_count(self) -> None:
        """Increment search iteration counter."""

        self.search_count += 1

    def get_tool_descriptions(self) -> str:
        """Get formatted tool descriptions for LLM."""

        return """
AVAILABLE TOOLS:
- [SEARCH_LOG: "pattern"] - Search raw log file for matching lines (case-insensitive, supports regex)
  Example: [SEARCH_LOG: "def main"]
  Example: [SEARCH_LOG: "import.*requests"]

- [SEARCH_FILE: "path" "pattern"] - Search a specific file for pattern
  Example: [SEARCH_FILE: "src/main.py" "class User"]
  Example: [SEARCH_FILE: "config.yaml" "timeout"]

- [READ_FILE: "path"] - Read file contents (full or with line range)
  Example: [READ_FILE: "src/main.py"]
  Example: [READ_FILE: "src/main.py" (10-20)]

- [LIST_ARTIFACTS] - List all files mentioned/edited/created in session

When you have sufficient evidence, output: [COMPLETE_EVIDENCE_SEARCH]
"""


TOOL_PATTERNS = [
    (r'\[SEARCH_LOG:\s*"([^"]+)"\]', 'search_log', 1),
    (r'\[SEARCH_FILE:\s*"([^"]+)"\s*"([^"]+)"\]', 'search_file', 2),
    (r'\[READ_FILE:\s*"([^"]+)"\s*(?:\((\d+)-(\d+)\))?', 'read_file', 3),
    (r'\[LIST_ARTIFACTS\]', 'list_artifacts', 0),
]


def extract_tool_calls(llm_response: str) -> List[Dict]:
    """Extract tool calls from LLM response."""

    tool_calls = []

    for pattern, tool_name, param_count in TOOL_PATTERNS:
        for match in re.finditer(pattern, llm_response):
            full_match = match.group(0)
            groups = match.groups()

            if param_count == 0:
                args = []
            else:
                args = [g for g in groups[:param_count] if g]

            tool_calls.append({
                'tool': tool_name,
                'args': args,
                'raw': full_match,
            })

    return tool_calls


def execute_tool_calls(tool_calls: List[Dict], tools: EvidenceSearchTools) -> List[str]:
    """Execute tool calls and return results."""

    results = []
    for call in tool_calls:
        tool_name = call['tool']
        args = call['args']

        try:
            if tool_name == 'search_log':
                result = tools.search_log(args[0])
            elif tool_name == 'search_file':
                result = tools.search_file(args[0], args[1])
            elif tool_name == 'read_file':
                line_range = args[1] if len(args) > 1 else None
                result = tools.read_file(args[0], line_range)
            elif tool_name == 'list_artifacts':
                result = tools.list_artifacts()
            else:
                result = f"Error: Unknown tool - {tool_name}"

            results.append(f"{tool_name.upper()}({call['raw']}): {result}")
        except Exception as e:
            results.append(f"{tool_name.upper()}({call['raw']}): Error - {e}")

    return results


def build_evidence_search_prompt(
    turn_summaries: List[Dict],
    accumulated_state: Dict,
    tools: EvidenceSearchTools,
    session_name: str,
) -> str:
    """Build initial evidence search prompt."""

    turn_summaries_text = ""
    for summary in turn_summaries[:5]:
        turn_summaries_text += f"""
Turn {summary.get('turn_number', 'N/A')}:
  User: {summary.get('user_request_summary', 'N/A')}
  Agent: {summary.get('agent_response_summary', 'N/A')}
  Outcomes: {summary.get('key_outcomes', 'N/A')}
  State change: {summary.get('state_changes', 'N/A')}
  Artifacts: {summary.get('artifacts_modified', [])}
  Constraints: {summary.get('constraints_added', [])}
  Questions: {summary.get('open_questions', [])}
"""

    if len(turn_summaries) > 5:
        turn_summaries_text += f"\n... and {len(turn_summaries) - 5} more turns"

    accumulated_state_text = f"""
High-level goal: {accumulated_state.get('high_level_goal', 'Not established')}
Key decisions: {accumulated_state.get('key_decisions', [])}
Constraints: {accumulated_state.get('constraints', [])}
Open questions: {accumulated_state.get('open_questions', [])}
Artifacts tracked: {list(accumulated_state.get('artifacts', set()))}
"""

    return EVIDENCE_SEARCH_PROMPT_TEMPLATE.format(
        turn_summaries=turn_summaries_text,
        accumulated_state=accumulated_state_text,
        max_searches=tools.max_searches,
        session_name=session_name,
    )


def build_continuation_prompt(
    previous_results: List[str],
    iteration: int,
    max_searches: int,
) -> str:
    """Build continuation prompt for agentic search loop."""

    results_text = "\n".join(previous_results)

    return EVIDENCE_SEARCH_CONTINUE_PROMPT_TEMPLATE.format(
        previous_results=results_text,
        iteration=iteration,
        max_searches=max_searches,
    )


def run_agentic_evidence_gathering(
    turn_summaries: List[Dict],
    accumulated_state: Dict,
    backend,
    search_tools: EvidenceSearchTools,
    session_name: str,
) -> str:
    """Run LLM-driven search loop to gather evidence for final summary."""

    prompt = build_evidence_search_prompt(
        turn_summaries=turn_summaries,
        accumulated_state=accumulated_state,
        tools=search_tools,
        session_name=session_name,
    )

    search_iterations = 0
    all_results = []

    while search_iterations < search_tools.max_searches:
        response = backend.generate(prompt)

        if "[COMPLETE_EVIDENCE_SEARCH]" in response:
            break

        tool_calls = extract_tool_calls(response)

        if tool_calls:
            for call in tool_calls:
                search_tools.increment_search_count()

            tool_results = execute_tool_calls(tool_calls, search_tools)
            all_results.extend(tool_results)
        else:
            all_results.append(f"No tool calls in iteration {search_iterations + 1}")

        search_iterations += 1

        if search_iterations >= search_tools.max_searches:
            break

        prompt = build_continuation_prompt(
            previous_results=all_results[-5:] if len(all_results) > 5 else all_results,
            iteration=search_iterations + 1,
            max_searches=search_tools.max_searches,
        )

    final_prompt = textwrap.dedent(f"""
    You have gathered evidence through agentic search.

    FINAL SESSION SUMMARY REQUEST:

    Using all turn summaries and evidence gathered, produce a final
    SESSION SUMMARY in this format:

    SESSION SUMMARY

    Session name:
    - {session_name}

    High-level goal:
    - <from accumulated state>

    Primary task in progress:
    - <based on last turn>

    Key decisions already made:
    - <bullet list>

    Constraints and assumptions:
    - <from accumulated state>

    Artifacts referenced or created:
    - <from accumulated state>

    Open questions:
    - <from accumulated state>

    Next concrete steps:
    - <based on last turn and evidence>
    """)

    return backend.generate(final_prompt)
