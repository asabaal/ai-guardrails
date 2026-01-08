"""
Unit tests for Pyright daemon - get_definition function

Tests follow verified brick commissioning protocol with 100% statement coverage.
"""

import pytest
from unittest.mock import Mock, patch
from semantic_agent.oracle.pyright_daemon import PyrightProcess, get_definition


class TestGetDefinition:
    """Test suite for get_definition function."""

    @pytest.fixture
    def mock_process(self):
        """Create a mock PyrightProcess."""
        process = PyrightProcess(
            process=Mock(),
            port=55440,
            pid=12345
        )
        return process

    def test_gets_definition_location(self, mock_process):
        """
        Test that get_definition returns definition location.

        This is a normal case test - successful query.
        """
        expected_result = {
            "uri": "file:///test/definitions.py",
            "range": {
                "start": {"line": 5, "character": 0},
                "end": {"line": 10, "character": 0}
            }
        }

        with patch('semantic_agent.oracle.pyright_daemon._send_jsonrpc_request') as mock_send:
            mock_send.return_value = expected_result

            result = get_definition(
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
            assert call_args[0][1] == "textDocument/definition"

            # Verify LSP params
            params = call_args[0][2]
            assert params["textDocument"]["uri"] == "file:///test/source.py"
            assert params["position"]["line"] == 2  # 0-indexed
            assert params["position"]["character"] == 10

    def test_raises_value_error_for_relative_path(self, mock_process):
        """
        Test that get_definition raises ValueError for relative path.

        This is a failure case test - invalid input.
        """
        with pytest.raises(ValueError) as exc_info:
            get_definition(mock_process, "relative/path.py", 1, 0)

        assert "file_path must be absolute path" in str(exc_info.value)

    def test_raises_value_error_for_line_zero(self, mock_process):
        """
        Test that get_definition raises ValueError for line 0.

        This is a failure case test - invalid input.
        """
        with pytest.raises(ValueError) as exc_info:
            get_definition(mock_process, "/test.py", 0, 0)

        assert "line must be >= 1" in str(exc_info.value)

    def test_raises_value_error_for_negative_line(self, mock_process):
        """
        Test that get_definition raises ValueError for negative line.

        This is a failure case test - invalid input.
        """
        with pytest.raises(ValueError) as exc_info:
            get_definition(mock_process, "/test.py", -1, 0)

        assert "line must be >= 1" in str(exc_info.value)

    def test_raises_value_error_for_negative_character(self, mock_process):
        """
        Test that get_definition raises ValueError for negative character.

        This is a failure case test - invalid input.
        """
        with pytest.raises(ValueError) as exc_info:
            get_definition(mock_process, "/test.py", 1, -1)

        assert "character must be >= 0" in str(exc_info.value)

    def test_raises_runtime_error_on_communication_failure(self, mock_process):
        """
        Test that get_definition raises RuntimeError on communication failure.

        This is a failure case test - LSP communication error.
        """
        with patch('semantic_agent.oracle.pyright_daemon._send_jsonrpc_request') as mock_send:
            mock_send.side_effect = RuntimeError("Connection lost")

            with pytest.raises(RuntimeError) as exc_info:
                get_definition(mock_process, "/test.py", 1, 0)

            assert "Failed to get definition" in str(exc_info.value)
            assert "Connection lost" in str(exc_info.value)

    def test_converts_line_to_zero_indexed(self, mock_process):
        """
        Test that get_definition converts 1-indexed line to 0-indexed.

        This is a normal case test - verify LSP indexing.
        """
        with patch('semantic_agent.oracle.pyright_daemon._send_jsonrpc_request') as mock_send:
            mock_send.return_value = {}

            # Call with 1-indexed line
            get_definition(mock_process, "/test.py", line=5, character=10)

            # Verify LSP received 0-indexed line
            params = mock_send.call_args[0][2]
            assert params["position"]["line"] == 4  # 5 - 1
            assert params["position"]["character"] == 10  # character unchanged

    def test_passes_absolute_path_correctly(self, mock_process):
        """
        Test that get_definition passes absolute path correctly.

        This is a normal case test - verify path handling.
        """
        with patch('semantic_agent.oracle.pyright_daemon._send_jsonrpc_request') as mock_send:
            mock_send.return_value = {}

            get_definition(mock_process, "/abs/path/test.py", 1, 0)

            # Verify URI format
            params = mock_send.call_args[0][2]
            assert params["textDocument"]["uri"] == "file:///abs/path/test.py"
