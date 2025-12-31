"""
Unit tests for cli.py.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO

from opencode_restore.cli import create_parser, main

class TestCreateParser:
    """Test create_parser function."""

    @pytest.fixture
    def parser(self):
        return create_parser()

    def test_parser_exists(self, parser):
        assert parser is not None

    def test_parser_has_log_file_argument(self, parser):
        args = parser.parse_args(["test.log"])
        assert args.log_file == Path("test.log")

    def test_parser_has_session_name_argument(self, parser):
        args = parser.parse_args(["test.log", "--session-name", "custom"])
        assert args.session_name == "custom"

    def test_parser_session_name_default(self, parser):
        args = parser.parse_args(["test.log"])
        assert args.session_name is None

    def test_parser_has_model_argument(self, parser):
        args = parser.parse_args(["test.log", "--model", "llama3"])
        assert args.model == "llama3"

    def test_parser_model_default(self, parser):
        args = parser.parse_args(["test.log"])
        assert args.model == "gpt-oss20b"

    def test_parser_has_max_lines_argument(self, parser):
        args = parser.parse_args(["test.log", "--max-lines", "800"])
        assert args.max_lines == 800

    def test_parser_max_lines_default(self, parser):
        args = parser.parse_args(["test.log"])
        assert args.max_lines == 600

    def test_parser_has_output_argument(self, parser):
        args = parser.parse_args(["test.log", "--out", "custom.md"])
        assert args.out == Path("custom.md")

    def test_parser_output_default(self, parser):
        args = parser.parse_args(["test.log"])
        assert args.out is None

    def test_parser_has_format_argument(self, parser):
        args = parser.parse_args(["test.log", "--format", "json"])
        assert args.format == "json"

    def test_parser_format_default(self, parser):
        args = parser.parse_args(["test.log"])
        assert args.format == "md"

    def test_parser_format_invalid_choice(self, parser):
        with pytest.raises(SystemExit):
            parser.parse_args(["test.log", "--format", "invalid"])

    def test_parser_has_dedupe_flag(self, parser):
        args = parser.parse_args(["test.log", "--dedupe"])
        assert args.dedupe is True

    def test_parser_dedupe_default(self, parser):
        args = parser.parse_args(["test.log"])
        assert args.dedupe is False

    def test_parser_has_include_header_flag(self, parser):
        args = parser.parse_args(["test.log", "--include-header"])
        assert args.include_header is True

    def test_parser_include_header_default(self, parser):
        args = parser.parse_args(["test.log"])
        assert args.include_header is False


class TestMain:
    """Test main CLI function."""

    @pytest.fixture
    def sample_log(self, tmp_path):
        log_file = tmp_path / "test.raw.log"
        log_file.write_text(
            'Script started on 2025-12-22 14:19:12-06:00 [COMMAND="opencode" TERM="xterm-256color" TTY="/dev/pts/7" COLUMNS="219" LINES="52"]\n'
            'Test content line 1\n'
            'Test content line 2\n'
        )
        return log_file

    @patch('sys.stderr', new_callable=StringIO)
    @patch('opencode_restore.cli.LogParser')
    @patch('opencode_restore.cli.create_ollama_summarizer')
    def test_main_file_not_found(self, mock_summarizer, mock_parser_class, mock_stderr):
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        mock_parser.parse_file.side_effect = FileNotFoundError("File not found")

        with patch('sys.argv', ['opencode-restore', 'nonexistent.log']):
            result = main()

        assert result == 1

    @patch('sys.stdout', new_callable=StringIO)
    @patch('sys.stderr', new_callable=StringIO)
    @patch('sys.argv', ['opencode-restore', 'nonexistent.log'])
    def test_main_log_file_not_exists(self, mock_stderr, mock_stdout):
        result = main()

        assert result == 1
        assert "Log file not found" in mock_stderr.getvalue()

    @patch('sys.stdout', new_callable=StringIO)
    @patch('sys.stderr', new_callable=StringIO)
    @patch('opencode_restore.cli.LogParser')
    @patch('opencode_restore.cli.TurnParser')
    @patch('opencode_restore.cli.create_ollama_summarizer')
    @patch('opencode_restore.cli.process_turns_incrementally')
    @patch('opencode_restore.cli.synthesize_summary_from_accumulated_state')
    def test_main_with_session_name(self, mock_synth, mock_process, mock_turn, mock_summarizer, mock_parser_class, sample_log):
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        mock_parsed = MagicMock()
        mock_parsed.header = None
        mock_parsed.content = ["Content"]
        mock_parser.parse_file.return_value = mock_parsed
        mock_parser.get_tail_content.return_value = "Content"

        mock_turn.return_value = ([], {})
        mock_turn_parser = MagicMock()
        mock_turn_parser.parse_turns.return_value = []

        mock_summarizer_obj = MagicMock()
        mock_summarizer.return_value = mock_summarizer_obj
        mock_summarizer_obj.backend.generate.return_value = "Summary"

        with patch('sys.argv', ['opencode-restore', str(sample_log), '--session-name', 'custom', '--skip-evidence-search']):
            result = main()

        assert result == 0

    @patch('sys.stdout', new_callable=StringIO)
    @patch('sys.stderr', new_callable=StringIO)
    @patch('opencode_restore.cli.LogParser')
    @patch('opencode_restore.cli.TurnParser')
    @patch('opencode_restore.cli.create_ollama_summarizer')
    @patch('opencode_restore.cli.process_turns_incrementally')
    @patch('opencode_restore.cli.synthesize_summary_from_accumulated_state')
    def test_main_with_dedupe(self, mock_synth, mock_process, mock_turn, mock_summarizer, mock_parser_class, sample_log):
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        mock_parsed = MagicMock()
        mock_parsed.header = None
        mock_parsed.content = ["line1", "line2"]
        mock_parser.parse_file.return_value = mock_parsed
        mock_parser.deduplicate_content.return_value = ["line1", "line2"]

        mock_turn.return_value = ([], {})
        mock_turn_parser = MagicMock()
        mock_turn_parser.parse_turns.return_value = []

        mock_summarizer_obj = MagicMock()
        mock_summarizer.return_value = mock_summarizer_obj
        mock_summarizer_obj.backend.generate.return_value = "Summary"

        with patch('sys.argv', ['opencode-restore', str(sample_log), '--dedupe', '--skip-evidence-search']):
            result = main()

        assert result == 0

    @patch('sys.stdout', new_callable=StringIO)
    @patch('sys.stderr', new_callable=StringIO)
    @patch('sys.argv', ['opencode-restore', 'nonexistent.log'])
    def test_main_log_file_not_found_duplicate(self, mock_stderr, mock_stdout):
        result = main()

        assert result == 1
        assert "Log file not found" in mock_stderr.getvalue()

    @patch('sys.stdout', new_callable=StringIO)
    @patch('sys.stderr', new_callable=StringIO)
    @patch('opencode_restore.cli.LogParser')
    @patch('opencode_restore.cli.TurnParser')
    @patch('opencode_restore.cli.create_ollama_summarizer')
    @patch('opencode_restore.cli.process_turns_incrementally')
    @patch('opencode_restore.cli.synthesize_summary_from_accumulated_state')
    def test_main_with_custom_output(self, mock_synth, mock_process, mock_turn, mock_summarizer, mock_parser_class, sample_log, tmp_path):
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        mock_parsed = MagicMock()
        mock_parsed.header = None
        mock_parsed.content = ["Content"]
        mock_parser.parse_file.return_value = mock_parsed
        mock_parser.get_tail_content.return_value = "Content"

        mock_turn.return_value = ([], {})
        mock_turn_parser = MagicMock()
        mock_turn_parser.parse_turns.return_value = []

        mock_summarizer_obj = MagicMock()
        mock_summarizer.return_value = mock_summarizer_obj
        mock_summarizer_obj.backend.generate.return_value = "Summary"

        custom_output = tmp_path / "custom.md"

        with patch('sys.argv', ['opencode-restore', str(sample_log), '--out', str(custom_output), '--skip-evidence-search']):
            result = main()

        assert result == 0
        assert custom_output.exists()

    @patch('sys.stdout', new_callable=StringIO)
    @patch('sys.stderr', new_callable=StringIO)
    @patch('opencode_restore.cli.LogParser')
    @patch('opencode_restore.cli.TurnParser')
    @patch('opencode_restore.cli.create_ollama_summarizer')
    @patch('opencode_restore.cli.process_turns_incrementally')
    @patch('opencode_restore.cli.synthesize_summary_from_accumulated_state')
    def test_main_with_include_header(self, mock_synth, mock_process, mock_turn, mock_summarizer, sample_log, tmp_path):
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        mock_parsed = MagicMock()
        from datetime import datetime
        mock_parsed.header = MagicMock()
        mock_parsed.header.timestamp = datetime(2025, 12, 22, 14, 19, 12)
        mock_parsed.header.command = "opencode"
        mock_parsed.header.tty = "/dev/pts/7"
        mock_parsed.content = ["Content"]
        mock_parser.parse_file.return_value = mock_parsed
        mock_parser.get_tail_content.return_value = "Content"

        mock_turn.return_value = ([], {})

        with patch('sys.argv', ['opencode-restore', str(sample_log), '--include-header', '--skip-evidence-search']):
            result = main()

        assert result == 0
        output_content = (sample_log.parent / "SUMMARY_test.md").read_text()
        assert "<!-- Script Header -->" in output_content

    @patch('sys.stdout', new_callable=StringIO)
    @patch('sys.stderr', new_callable=StringIO)
    @patch('opencode_restore.cli.create_ollama_summarizer')
    @patch('opencode_restore.cli.LogParser')
    @patch('opencode_restore.cli.TurnParser')
    @patch('opencode_restore.cli.process_turns_incrementally')
    def test_main_runtime_error(self, mock_process, mock_turn, mock_summarizer, mock_parser_class, sample_log):
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        mock_parsed = MagicMock()
        mock_parsed.header = None
        mock_parsed.content = ["Content"]
        mock_parser.parse_file.return_value = mock_parsed

        mock_turn.side_effect = RuntimeError("Processing error")
        mock_turn_parser = MagicMock()
        mock_turn_parser.parse_turns.return_value = []

        with patch('sys.argv', ['opencode-restore', str(sample_log)]):
            result = main()

        assert result == 1

    @patch('sys.stdout', new_callable=StringIO)
    @patch('sys.stderr', new_callable=StringIO)
    @patch('opencode_restore.cli.LogParser')
    @patch('opencode_restore.cli.TurnParser')
    @patch('opencode_restore.cli.create_ollama_summarizer')
    @patch('opencode_restore.cli.process_turns_incrementally')
    @patch('opencode_restore.cli.synthesize_summary_from_accumulated_state')
    def test_main_with_max_lines(self, mock_synth, mock_process, mock_turn, mock_summarizer, mock_parser_class, sample_log):
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        mock_parsed = MagicMock()
        mock_parsed.header = None
        mock_parsed.content = ["Content"]
        mock_parser.parse_file.return_value = mock_parsed
        mock_parser.get_tail_content.return_value = "Content"

        mock_turn.return_value = ([], {})
        mock_turn_parser = MagicMock()
        mock_turn_parser.parse_turns.return_value = []

        mock_summarizer_obj = MagicMock()
        mock_summarizer.return_value = mock_summarizer_obj
        mock_summarizer_obj.backend.generate.return_value = "Summary"

        with patch('sys.argv', ['opencode-restore', str(sample_log), '--max-lines', '800', '--skip-evidence-search']):
            result = main()

        assert result == 0
        mock_parser.get_tail_content.assert_called_once_with(
            ["Content"],
            800
        )
