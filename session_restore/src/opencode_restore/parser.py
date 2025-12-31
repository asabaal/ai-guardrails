"""
Parser for OpenCode raw log files.
Handles ANSI escape code stripping and content extraction.
"""

import re
import textwrap
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from .config import (
    ANSI_ESCAPE_PATTERN,
    SCRIPT_HEADER_PATTERN,
    UI_ARTIFACT_PATTERNS,
    DEFAULT_ENCODING,
)


@dataclass
class ScriptHeader:
    """Parsed script header information."""

    timestamp: datetime
    command: str
    term: str
    tty: str
    columns: int
    lines: int


@dataclass
class ParsedTranscript:
    """Parsed transcript content with metadata."""

    header: Optional[ScriptHeader]
    content: List[str]
    raw_lines: List[str]
    session_name: Optional[str] = None


class LogParser:
    """Parser for OpenCode raw log files."""

    def __init__(self):
        self.ansi_pattern = re.compile(ANSI_ESCAPE_PATTERN)
        self.header_pattern = re.compile(SCRIPT_HEADER_PATTERN)
        self.ui_patterns = [re.compile(p) for p in UI_ARTIFACT_PATTERNS]

    def strip_ansi(self, text: str) -> str:
        """Remove ANSI escape sequences from text."""

        return self.ansi_pattern.sub('', text)

    def is_ui_artifact(self, line: str) -> bool:
        """Check if line is a UI artifact."""

        for pattern in self.ui_patterns:
            if pattern.search(line) or pattern.match(line) or pattern.search(line.strip()):
                return True
        return False

    def parse_header(self, line: str) -> Optional[ScriptHeader]:
        """Parse script header line."""

        match = self.header_pattern.match(line)
        if not match:
            return None

        timestamp_str = match.group(1)
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S%z")

        return ScriptHeader(
            timestamp=timestamp,
            command=match.group(2),
            term=match.group(3),
            tty=match.group(4),
            columns=int(match.group(5)),
            lines=int(match.group(6)),
        )

    def extract_session_name(self, log_path: Path) -> str:
        """Extract session name from log file path."""

        stem = log_path.stem
        if stem.endswith('.raw'):
            stem = stem[:-4]
        return stem

    def parse_file(self, log_path: Path) -> ParsedTranscript:
        """Parse raw log file and extract clean content."""

        if not log_path.exists():
            raise FileNotFoundError(f"Log file not found: {log_path}")

        raw_lines = log_path.read_text(encoding=DEFAULT_ENCODING, errors="ignore").splitlines()
        content_lines = []
        header = None

        for line in raw_lines:
            stripped_line = self.strip_ansi(line)

            if header is None:
                parsed_header = self.parse_header(stripped_line)
                if parsed_header:
                    header = parsed_header
                    continue

            if self.is_ui_artifact(stripped_line):
                continue

            clean_line = stripped_line.strip()
            if clean_line:
                content_lines.append(clean_line)

        session_name = self.extract_session_name(log_path)

        return ParsedTranscript(
            header=header,
            content=content_lines,
            raw_lines=raw_lines,
            session_name=session_name,
        )

    def get_tail_content(self, content: List[str], max_lines: int) -> str:
        """Get tail of content up to max_lines."""

        if len(content) <= max_lines:
            return "\n".join(content)
        return "\n".join(content[-max_lines:])

    def deduplicate_content(self, content: List[str]) -> List[str]:
        """Remove consecutive duplicate lines."""

        if not content:
            return []

        deduped = [content[0]]
        for line in content[1:]:
            if line != deduped[-1]:
                deduped.append(line)
        return deduped
