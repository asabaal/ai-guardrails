"""
Integration and E2E tests for opencode-restore.
"""

import pytest
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

from opencode_restore import LogParser, create_ollama_summarizer
from opencode_restore.config import DEFAULT_MAX_LINES


class TestLogParserIntegration:
    """Integration tests for LogParser with real log files."""

    def test_parse_fixture_raw_log(self, tmp_path):
        fixture_path = Path(__file__).parent / "fixtures" / "sample_raw.log"
        if not fixture_path.exists():
            pytest.skip("Fixture file not found")

        parser = LogParser()
        result = parser.parse_file(fixture_path)

        assert result.session_name is not None
        assert result.header is not None
        assert "opencode" in result.header.command
        assert len(result.content) > 0

    def test_parse_and_clean_real_log(self, tmp_path):
        log_file = tmp_path / "integration_test.raw.log"
        log_file.write_text(
            'Script started on 2025-12-22 14:19:12-06:00 [COMMAND="opencode" TERM="xterm-256color" TTY="/dev/pts/7" COLUMNS="219" LINES="52"]\n'
            '[38;2;238;238;238mUser message[39m\n'
            '┃  ┃\n'
            '[38;2;92;156;245mAI response[39m\n'
            '────────────────\n'
            'Valid content\n'
        )

        parser = LogParser()
        result = parser.parse_file(log_file)

        assert "User message" in result.content
        assert "AI response" in result.content
        assert "Valid content" in result.content

    def test_parse_with_large_file(self, tmp_path):
        log_file = tmp_path / "large.raw.log"
        lines = ['Script started on 2025-12-22 14:19:12-06:00 [COMMAND="opencode" TERM="xterm-256color" TTY="/dev/pts/7" COLUMNS="219" LINES="52"]']
        for i in range(1000):
            lines.append(f'[38;2;238;238;238mContent line {i}[39m')
            lines.append('┃  ┃')
        log_file.write_text('\n'.join(lines))

        parser = LogParser()
        result = parser.parse_file(log_file)

        assert len(result.content) == 1000
        assert len(result.raw_lines) == 2001


class TestSummarizerIntegration:
    """Integration tests for Summarizer with mocked LLM."""

    @patch('opencode_restore.summarizer.subprocess.run')
    def test_full_summarization_flow(self, mock_run, tmp_path):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "SESSION SUMMARY\n\nSession name: test\nHigh-level goal: Test summary"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        log_file = tmp_path / "e2e_test.raw.log"
        log_file.write_text(
            'Script started on 2025-12-22 14:19:12-06:00 [COMMAND="opencode" TERM="xterm-256color" TTY="/dev/pts/7" COLUMNS="219" LINES="52"]\n'
            '[38;2;238;238;238mUser: Create a test function[39m\n'
            '[38;2;92;156;245mAI: I will help create the function[39m\n'
        )

        parser = LogParser()
        parsed = parser.parse_file(log_file)
        transcript = parser.get_tail_content(parsed.content, DEFAULT_MAX_LINES)

        summarizer = create_ollama_summarizer("test-model")
        summary = summarizer.summarize(parsed.session_name, transcript)

        assert "SESSION SUMMARY" in summary

    @patch('opencode_restore.summarizer.subprocess.run')
    def test_summarize_with_long_transcript(self, mock_run, tmp_path):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Summary content"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        log_file = tmp_path / "long_transcript.raw.log"
        lines = ['Script started on 2025-12-22 14:19:12-06:00 [COMMAND="opencode" TERM="xterm-256color" TTY="/dev/pts/7" COLUMNS="219" LINES="52"]']
        for i in range(1000):
            lines.append(f'Content line {i}')
        log_file.write_text('\n'.join(lines))

        parser = LogParser()
        parsed = parser.parse_file(log_file)
        transcript = parser.get_tail_content(parsed.content, 100)

        summarizer = create_ollama_summarizer("test-model")
        summary = summarizer.summarize(parsed.session_name, transcript)

        assert summary == "Summary content"
        mock_run.assert_called_once()


class TestCliE2E:
    """End-to-end tests for CLI."""

    @patch('opencode_restore.cli.create_ollama_summarizer')
    def test_cli_full_workflow(self, mock_summarizer_factory, tmp_path):
        mock_summarizer = MagicMock()
        mock_summarizer.backend.generate.return_value = "SESSION SUMMARY\n\nSession name: test\n\nHigh-level goal: Test E2E\n\nPrimary task in progress: None"
        mock_summarizer_factory.return_value = mock_summarizer

        log_file = tmp_path / "e2e.raw.log"
        log_file.write_text(
            'Script started on 2025-12-22 14:19:12-06:00 [COMMAND="opencode" TERM="xterm-256color" TTY="/dev/pts/7" COLUMNS="219" LINES="52"]\n'
            '[38;2;238;238;238mUser: Create CLI tool[39m\n'
            '[38;2;92;156;245mAI: I will help you[39m\n'
        )

        output_file = tmp_path / "SUMMARY_e2e.md"

        result = subprocess.run(
            [
                "python", "-m", "opencode_restore.cli",
                str(log_file),
                "--out", str(output_file),
            ],
            capture_output=True,
            text=True,
            cwd="/mnt/storage/repos/ai-guardrails/session_restore"
        )

        assert result.returncode == 0
        assert output_file.exists()

        content = output_file.read_text()
        assert "SESSION SUMMARY" in content
        assert "Test E2E" in content

    @patch('opencode_restore.cli.create_ollama_summarizer')
    def test_cli_with_all_options(self, mock_summarizer_factory, tmp_path):
        mock_summarizer = MagicMock()
        mock_summarizer.backend.generate.return_value = "Summary with all options"
        mock_summarizer_factory.return_value = mock_summarizer

        log_file = tmp_path / "options.raw.log"
        log_file.write_text(
            'Script started on 2025-12-22 14:19:12-06:00 [COMMAND="opencode" TERM="xterm-256color" TTY="/dev/pts/7" COLUMNS="219" LINES="52"]\n'
            'Content\n'
        )

        result = subprocess.run(
            [
                "python", "-m", "opencode_restore.cli",
                str(log_file),
                "--session-name", "custom_session",
                "--model", "custom-model",
                "--max-lines", "100",
                "--dedupe",
                "--include-header",
            ],
            capture_output=True,
            text=True,
            cwd="/mnt/storage/repos/ai-guardrails/session_restore"
        )

        assert result.returncode == 0

    def test_cli_help(self):
        result = subprocess.run(
            ["python", "-m", "opencode_restore.cli", "--help"],
            capture_output=True,
            text=True,
            cwd="/mnt/storage/repos/ai-guardrails/session_restore"
        )

        assert result.returncode == 0
        assert "opencode-restore" in result.stdout
        assert "log_file" in result.stdout


class TestPackageIntegration:
    """Tests for package-level integration."""

    def test_package_exports(self):
        from opencode_restore import (
            LogParser,
            ParsedTranscript,
            ScriptHeader,
            Summarizer,
            OllamaBackend,
            create_ollama_summarizer,
            DEFAULT_MODEL,
            DEFAULT_MAX_LINES,
            SUMMARY_SCHEMA,
        )

        assert LogParser is not None
        assert ParsedTranscript is not None
        assert ScriptHeader is not None
        assert Summarizer is not None
        assert OllamaBackend is not None
        assert create_ollama_summarizer is not None
        assert DEFAULT_MODEL == "gpt-oss20b"
        assert DEFAULT_MAX_LINES == 600
        assert "SESSION SUMMARY" in SUMMARY_SCHEMA

    def test_version_attribute(self):
        from opencode_restore import __version__
        assert isinstance(__version__, str)
        assert __version__ == "2.0.0"
