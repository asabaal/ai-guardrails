"""
Unit tests for parser.py.
"""

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

from opencode_restore.parser import (
    LogParser,
    ParsedTranscript,
    ScriptHeader,
)


class TestScriptHeader:
    """Test ScriptHeader dataclass."""

    def test_create_script_header(self):
        header = ScriptHeader(
            timestamp=datetime(2025, 12, 22, 14, 19, 12),
            command="opencode",
            term="xterm-256color",
            tty="/dev/pts/7",
            columns=219,
            lines=52,
        )

        assert header.command == "opencode"
        assert header.term == "xterm-256color"
        assert header.tty == "/dev/pts/7"
        assert header.columns == 219
        assert header.lines == 52


class TestParsedTranscript:
    """Test ParsedTranscript dataclass."""

    def test_create_parsed_transcript(self):
        transcript = ParsedTranscript(
            header=None,
            content=["line1", "line2"],
            raw_lines=["raw1", "raw2"],
            session_name="test_session",
        )

        assert transcript.content == ["line1", "line2"]
        assert transcript.raw_lines == ["raw1", "raw2"]
        assert transcript.session_name == "test_session"


class TestLogParser:
    """Test LogParser class."""

    @pytest.fixture
    def parser(self):
        return LogParser()

    def test_strip_ansi_color_codes(self, parser):
        text = "[38;2;238;238;238mHello[39m World"
        result = parser.strip_ansi(text)
        assert result == "Hello World"

    def test_strip_ansi_cursor_movement(self, parser):
        text = "\x1b[?25l\x1b[?25h[48;7H"
        result = parser.strip_ansi(text)
        assert result == ""

    def test_is_ui_artifact_cursor_sequences(self, parser):
        line = "\x1b[?25h"
        assert parser.is_ui_artifact(line) is True

    def test_is_ui_artifact_border_chars(self, parser):
        line = "──────────────────────────"
        assert parser.is_ui_artifact(line) is True

    def test_is_ui_artifact_decorative_chars(self, parser):
        line = "▀▀▄░░█"
        assert parser.is_ui_artifact(line) is True

    def test_is_ui_artifact_position_sequences(self, parser):
        line = "[48;7H"
        assert parser.is_ui_artifact(line) is True

    def test_is_ui_artifact_not_ui_content(self, parser):
        line = "This is actual user content"
        assert parser.is_ui_artifact(line) is False

    def test_is_ui_artifact_whitespace_line(self, parser):
        line = "   "
        result = parser.is_ui_artifact(line)
        assert result is False

    def test_parse_header_valid(self, parser):
        line = 'Script started on 2025-12-22 14:19:12-06:00 [COMMAND="opencode" TERM="xterm-256color" TTY="/dev/pts/7" COLUMNS="219" LINES="52"]'
        header = parser.parse_header(line)

        assert header is not None
        assert header.command == "opencode"
        assert header.term == "xterm-256color"
        assert header.tty == "/dev/pts/7"
        assert header.columns == 219
        assert header.lines == 52

    def test_parse_header_invalid(self, parser):
        line = "Not a valid header line"
        header = parser.parse_header(line)
        assert header is None

    def test_extract_session_name_simple(self, parser):
        log_path = Path("/path/to/session.raw.log")
        name = parser.extract_session_name(log_path)
        assert name == "session"

    def test_extract_session_name_no_extension(self, parser):
        log_path = Path("/path/to/session")
        name = parser.extract_session_name(log_path)
        assert name == "session"

    def test_extract_session_name_with_date(self, parser):
        log_path = Path("/path/to/forge-e2e-test_2025-12-22_141912.raw.log")
        name = parser.extract_session_name(log_path)
        assert name == "forge-e2e-test_2025-12-22_141912"

    def test_parse_file_not_found(self, parser, tmp_path):
        log_file = tmp_path / "nonexistent.log"

        with pytest.raises(FileNotFoundError):
            parser.parse_file(log_file)

    def test_parse_file_success(self, parser, tmp_path):
        log_file = tmp_path / "test.log"
        log_file.write_text(
            'Script started on 2025-12-22 14:19:12-06:00 [COMMAND="opencode" TERM="xterm-256color" TTY="/dev/pts/7" COLUMNS="219" LINES="52"]\n'
            "[38;2;238;238;238mHello[39m\n"
            "World\n"
            "┃  ┃\n"
            "Content line\n"
        )

        result = parser.parse_file(log_file)

        assert result.header is not None
        assert result.header.command == "opencode"
        assert len(result.raw_lines) == 5
        assert "Content line" in result.content
        assert "Hello" in result.content
        assert "World" in result.content

    def test_parse_file_filters_ui_artifacts(self, parser, tmp_path):
        log_file = tmp_path / "test.log"
        log_file.write_text(
            "Valid content 1\n"
            "┃  ┃\n"
            "Valid content 2\n"
            "────────────\n"
            "Valid content 3\n"
        )

        result = parser.parse_file(log_file)

        assert result.content == [
            "Valid content 1",
            "Valid content 2",
            "Valid content 3",
        ]

    def test_get_tail_content_under_limit(self, parser):
        content = ["line1", "line2", "line3"]
        result = parser.get_tail_content(content, max_lines=10)
        assert result == "line1\nline2\nline3"

    def test_get_tail_content_over_limit(self, parser):
        content = ["line1", "line2", "line3", "line4", "line5"]
        result = parser.get_tail_content(content, max_lines=3)
        assert result == "line3\nline4\nline5"

    def test_get_tail_content_empty(self, parser):
        content = []
        result = parser.get_tail_content(content, max_lines=10)
        assert result == ""

    def test_get_tail_content_exact_limit(self, parser):
        content = ["line1", "line2", "line3"]
        result = parser.get_tail_content(content, max_lines=3)
        assert result == "line1\nline2\nline3"

    def test_deduplicate_content_empty(self, parser):
        content = []
        result = parser.deduplicate_content(content)
        assert result == []

    def test_deduplicate_content_single(self, parser):
        content = ["line1"]
        result = parser.deduplicate_content(content)
        assert result == ["line1"]

    def test_deduplicate_content_no_duplicates(self, parser):
        content = ["line1", "line2", "line3"]
        result = parser.deduplicate_content(content)
        assert result == ["line1", "line2", "line3"]

    def test_deduplicate_content_with_duplicates(self, parser):
        content = ["line1", "line1", "line2", "line2", "line3", "line1"]
        result = parser.deduplicate_content(content)
        assert result == ["line1", "line2", "line3", "line1"]

    def test_deduplicate_content_all_duplicates(self, parser):
        content = ["same", "same", "same", "same"]
        result = parser.deduplicate_content(content)
        assert result == ["same"]
