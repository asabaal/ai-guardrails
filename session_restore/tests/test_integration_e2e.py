"""
Integration test for turn-by-turn session restoration workflow.
Tests that complete flow works end-to-end.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from opencode_restore import cli
from opencode_restore.parser import LogParser
from opencode_restore.turn_parser import TurnParser
from opencode_restore.turn_summarizer import process_turns_incrementally


@pytest.fixture
def sample_raw_log_with_turns(tmp_path):
    """Create a sample raw log with multiple turns for testing."""
    log_file = tmp_path / "test_session.raw.log"
    log_file.write_text(
        'Script started on 2025-12-22 14:19:12-06:00 [COMMAND="opencode" TERM="xterm-256color" TTY="/dev/pts/7" COLUMNS="219" LINES="52"]\n'
        '┃  First user request to implement feature X ┃\n'
        'asabaal (01:36 PM)\n'
        'I will help you implement feature X.\n'
        'Read src/feature_x.py\n'
        'Found it.\n'
        '┃  Second user request to fix bug in feature X ┃\n'
        'asabaal (01:37 PM)\n'
        'I will fix the bug.\n'
        'Edit src/feature_x.py line 42\n'
        'Bug fixed at line 42.\n'
        'Complete!\n'
        '┃  Third user request to add tests ┃\n'
        'asabaal (01:38 PM)\n'
        'Sure, I will add tests now.\n'
        'Added tests for feature_x.py.\n'
        'All tests passing.\n'
    )
    return log_file


class TestTurnByTurnIntegration:
    """Test that turn-by-turn restoration workflow works correctly."""

    def test_turns_are_parsed_correctly(self, sample_raw_log_with_turns):
        """Test that turns are parsed from log file."""
        log_parser = LogParser()
        turn_parser = TurnParser()

        parsed = log_parser.parse_file(sample_raw_log_with_turns)

        turns = turn_parser.parse_turns(parsed.content)

        assert len(turns) == 3

    def test_turns_with_accumulated_state_are_processed(self, sample_raw_log_with_turns):
        """Test that turn processing builds accumulated state correctly."""
        log_parser = LogParser()
        turn_parser = TurnParser()
        mock_backend = MagicMock()
        mock_backend.generate.return_value = "Summary turn N"

        parsed = log_parser.parse_file(sample_raw_log_with_turns)
        turns = turn_parser.parse_turns(parsed.content)

        turn_summaries, _ = process_turns_incrementally(
            turns=turns,
            backend=mock_backend,
            session_name="test_session",
        )

        assert len(turn_summaries) == 3
        assert mock_backend.generate.call_count == 3
        mock_backend.generate.assert_called()

    def test_cli_integration(self, sample_raw_log_with_turns, tmp_path, monkeypatch):
        """Test CLI works end-to-end with turn-based workflow."""
        from opencode_restore import cli as restore_cli

        with patch('sys.argv', ['restore', str(sample_raw_log_with_turns), '--max-turns', '2', '--dump-turns']):
            result = restore_cli.main()
            assert result == 0

        out_file = tmp_path / "output.md"
        assert out_file.exists()
        out_content = out_file.read_text()
        assert "SESSION SUMMARY" in out_content
        assert "test_session" in out_content
