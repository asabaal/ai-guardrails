"""
Configuration constants and defaults for opencode-restore.
"""

import os
from pathlib import Path

DEFAULT_MODEL = "gpt-oss20b"
DEFAULT_MAX_LINES = 600
DEFAULT_OUTPUT_FORMAT = "md"
DEFAULT_ENCODING = "utf-8"

DEFAULT_OLLAMA_BASE_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434")

ANSI_ESCAPE_PATTERN = r'\x1b\[\?\d+[hl]|\x1b\[[0-9;]*[mGKHfJ]|\x1b\][0-9;]*;[0-9;]*;[0-9;]*[a-zA-Z]|\x1b\?\[[0-9;]*[hl]|\x1b\?\d+[hl]|\x1b\[[0-9;]*[a-zA-Z]|\x1b\([0-9AB]|\x1b\)[0-9AB]|\x1b=|\x07|\x1b\[?1034h|\[[0-9;]*m|\[[0-9;]*[Hm]|\[?\[[0-9;]*[hl]]|\[\?\[[0-9;]*[hl]]|\[\?25[hl]]|\[[0-9;]*[Hm]\]|\x1b\?\[?\d+\[hl]\]|\[\?\d+\[hl]\]|\[\?\d+[hl]\]'

UI_ARTIFACT_PATTERNS = [
    r'\x1b\[\?\d+[hl]',
    r'^\s*[┃└┌├│─]+\s*$',
    r'^\s*[█▀▄░]+\s*$',
    r'^\s*\[?\[?[0-9]+\]`?\s*$',
    r'^\s*\[?\[?[0-9]+\][A-Z]r?\s*[0-9;]*[Hm]?',
    r'^\s*\[?\[25[hl]\]?\s*$',
    r'^\s*\[?\[[0-9;]+[0-9;]*[Hm]\s*$',
    r'^\s*\[?\[\?\[[0-9;]*[hl]\]\s*$',
    r'^\s*\[?\[[0-9;]+;\s*[0-9]+\]r\s*$',
    r'^\s*\[?\[12[ST]\]\s*$',
    r'^\s*\[?\[2[KT]\]\s*$',
    r'^\s*\[?\[M\]\s*$',
    r'^\s*\[?\[7[hl]\]\s*$',
    r'\[[0-9]+\][a-z]?\]',
    r'\[[0-9]+;[0-9]+\][a-z]\]',
    r'^\s*[0-9]+\][a-z]+\s*$',
    r'^\s*\[?\[[0-9]+\]`\s*$',
    r'^\s*─+\s*$',
    r'\[\?25[hl]]',
    r'\[\?[0-9]+[hl]]',
    r'^\s*[┃]+\s*[┃]+\s*$',
    r'\[\?\d+\[hl]]',
    r'^\s*\[?\d+\[hl\]\s*$',
    r'^\s*\[?\d+\]\s*$',
]

TURN_DETECTION_PATTERNS = {
    'user_message': r'┃\s+(.+?)\s+┃',
    'username_timestamp': r'(\w+)\s+\(\d{1,2}:\s+\d{2}\s+[AP]M\)',
}

TOOL_PATTERNS = {
    'read_file': r'Read\s+(\S+)',
    'edit_file': r'Edit\s+(\S+)',
    'shell_cd': r'Shell\s+.*?(?:cd\s+)?(\S+)?',
}

AGENTIC_SEARCH_CONFIG = {
    'max_searches': 8,
    'search_context_lines': 3,
    'pattern_max_length': 200,
}

TURN_SUMMARY_SCHEMA = """
You must produce a structured TURN SUMMARY using the exact format below.

TURN SUMMARY

Turn number: <integer>
User request summary: <concise summary of what user asked>
Agent response summary: <what agent did/approached>
Key outcomes: <what was accomplished in this turn>
State changes: <what changed in overall session state>
Artifacts modified: <comma-separated list of files touched>
Constraints/assumptions added: <new constraints or assumptions from this turn>
Open questions after this turn: <unresolved issues or questions>
"""

EVIDENCE_SEARCH_PROMPT_TEMPLATE = """
You are an evidence gathering assistant for an interrupted OpenCode session.

Session name: {session_name}

You have access to turn-by-turn summaries and accumulated state from the session.
Your job is to search for specific evidence in of log and files to verify
and enhance the final session summary.

CURRENT TURN SUMMARIES:
{turn_summaries}

ACCUMULATED STATE:
{accumulated_state}

AVAILABLE TOOLS:
- [SEARCH_LOG: "pattern"] - Search the raw log file for matching lines
- [SEARCH_FILE: "path" "pattern"] - Search a specific file for pattern
- [READ_FILE: "path"] - Read file contents (full or with line range)
- [LIST_ARTIFACTS] - List all files mentioned/edited/created in session

TOOL RESULT FORMAT:
Results will include line numbers and context for easy reference.

Use tools to verify key claims, find missing details, and gather supporting evidence.
When you have sufficient evidence, output: [COMPLETE_EVIDENCE_SEARCH]

Maximum search iterations: {max_searches}
"""

EVIDENCE_SEARCH_CONTINUE_PROMPT_TEMPLATE = """
PREVIOUS SEARCH RESULTS:
{previous_results}

Use these results to continue your investigation or output [COMPLETE_EVIDENCE_SEARCH] if done.

Iteration {iteration}/{max_searches}:
"""

SCRIPT_HEADER_PATTERN = r'^Script started on (.+) \[COMMAND="(.+)" TERM="(.+)" TTY="(.+)" COLUMNS="(.+)" LINES="(.+)"\]$'

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


def get_default_output_path(session_name: str, output_format: str = DEFAULT_OUTPUT_FORMAT) -> Path:
    """Generate default output filename from session name."""
    ext = "md" if output_format == "md" else "json"
    return Path(f"SUMMARY_{session_name}.{ext}")
