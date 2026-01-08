"""
Unit tests for Pyright daemon - get_references function

Tests follow verified brick commissioning protocol with 100% statement coverage.
"""

import pytest
from unittest.mock import Mock, patch
from semantic_agent.oracle.pyright_daemon import PyrightProcess, get_references


class TestGetReferences:
    """Test suite for get_references function."""

    @pytest.fixture
    def mock_process(self):
        """Create a mock PyrightProcess."""
        process = PyrightProcess(
            process=Mock(),
            port=55440,
            pid=12345
        )
        return process

    def test_gets_all_references(self, mock_process):
        """
        Test that get_references returns list of reference locations.

        This is a normal case test - successful query.
        """
        expected_result = [
            {
                "uri": "file:///test/source.py",
                "range": {"start": {"line": 0, "character": 5}, "end": {"line": 0, "character": 10}}
            },
            {
                "uri": "file:///test/other.py",
                "range": {"start": {"line": 15, "character": 0}, "end": {"line": 15, "character": 5}}
            }
        ]

        with patch('semantic_agent.oracle.pyright_daemon._send_jsonrpc_request') as mock_send:
            mock_send.return_value = expected_result

            result = get_references(
                mock_process,
                "/test/source.py",
                line=3,
                character=10
            )

            # Verify result
            assert result == expected_result

            # Verify RPC call
            assert mock_send.called
            call_args = mock_send.call_args
            assert call_args[0][0] == mock_process
            assert call_args[0][1] == "textDocument/references"

            # Verify LSP params
            params = call_args[0][2]
            assert params["textDocument"]["uri"] == "file:///test/source.py"
            assert params["position"]["line"] == 2  # 0-indexed
            assert params["position"]["character"] == 10

    def test_raises_value_error_for_relative_path(self, mock_process):
        """
        Test that get_references raises ValueError for relative path.

        This is a failure case test - invalid input.
        """
        with pytest.raises(ValueError) as exc_info:
            get_references(mock_process, "relative/path.py", 1, 0)

        assert "file_path must be absolute path" in str(exc_info.value)

    def test_raises_value_error_for_line_zero(self, mock_process):
        """
        Test that get_references raises ValueError for line 0.

        This is a failure case test - invalid input.
        """
        with pytest.raises(ValueError) as exc_info:
            get_references(mock_process, "/test.py", 0, 0)

        assert "line must be >= 1" in str(exc_info.value)

    def test_raises_value_error_for_negative_line(self, mock_process):
        """
        Test that get_references raises ValueError for negative line.

        This is a failure case test - invalid input.
        """
        with pytest.raises(ValueError) as exc_info:
            get_references(mock_process, "/test.py", -1, 0)

        assert "line must be >= 1" in str(exc_info.value)

    def test_raises_value_error_for_negative_character(self, mock_process):
        """
        Test that get_references raises ValueError for negative character.

        This is a failure case test - invalid input.
        """
        with pytest.raises(ValueError) as exc_info:
            get_references(mock_process, "/test.py", 1, -1)

        assert "character must be >= 0" in str(exc_info.value)

    def test_raises_runtime_error_on_communication_failure(self, mock_process):
        """
        Test that get_references raises RuntimeError on communication failure.

        This is a failure case test - LSP communication error.
        """
        with patch('semantic_agent.oracle.pyright_daemon._send_jsonrpc_request') as mock_send:
            mock_send.side_effect = RuntimeError("Connection lost")

            with pytest.raises(RuntimeError) as exc_info:
                get_references(mock_process, "/test.py", 1, 0)

            assert "Failed to get references" in str(exc_info.value)
            assert "Connection lost" in str(exc_info.value)

    def test_converts_line_to_zero_indexed(self, mock_process):
        """
        Test that get_references converts 1-indexed line to 0-indexed.

        This is a normal case test - verify LSP indexing.
        """
        with patch('semantic_agent.oracle.pyright_daemon._send_jsonrpc_request') as mock_send:
            mock_send.return_value = []

            # Call with 1-indexed line
            get_references(mock_process, "/test.py", line=7, character=15)

            # Verify LSP received 0-indexed line
            params = mock_send.call_args[0][2]
            assert params["position"]["line"] == 6  # 7 - 1
            assert params["position"]["character"] == 15  # character unchanged

    def test_passes_absolute_path_correctly(self, mock_process):
        """
        Test that get_references passes absolute path correctly.

        This is a normal case test - verify path handling.
        """
        with patch('semantic_agent.oracle.pyright_daemon._send_jsonrpc_request') as mock_send:
            mock_send.return_value = []

            get_references(mock_process, "/abs/path/test.py", 1, 0)

            # Verify URI format
            params = mock_send.call_args[0][2]
            assert params["textDocument"]["uri"] == "file:///abs/path/test.py"

    def test_returns_empty_list_when_no_references(self, mock_process):
        """
        Test that get_references returns empty list when no references.

        This is a normal case test - symbol not used elsewhere.
        """
        with patch('semantic_agent.oracle.pyright_daemon._send_jsonrpc_request') as mock_send:
            mock_send.return_value = []

            result = get_references(mock_process, "/test.py", 1, 0)

            assert result == []

    def test_handles_multiple_references(self, mock_process):
        """
        Test that get_references handles multiple references correctly.

        This is a normal case test - verify list handling.
        """
        expected_result = [
            {"uri": "file:///test/a.py", "range": {"start": {"line": 1, "character": 0}, "end": {"line": 1, "character": 5}}},
            {"uri": "file:///test/b.py", "range": {"start": {"line": 3, "character": 0}, "end": {"line": 3, "character": 10}}},
            {"uri": "file:///test/c.py", "range": {"start": {"line": 7, "character": 2}, "end": {"line": 7, "character": 12}}},
        ]

        with patch('semantic_agent.oracle.pyright_daemon._send_jsonrpc_request') as mock_send:
            mock_send.return_value = expected_result

            result = get_references(mock_process, "/test/symbol.py", 1, 0)

            assert len(result) == 3
            assert result[0]["uri"] == "file:///test/a.py"
            assert result[1]["uri"] == "file:///test/b.py"
            assert result[2]["uri"] == "file:///test/c.py"
