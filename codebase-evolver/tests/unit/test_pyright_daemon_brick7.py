"""
Unit tests for Pyright daemon - get_type_info function

Tests follow verified brick commissioning protocol with 100% statement coverage.
"""

import pytest
from unittest.mock import Mock, patch
from semantic_agent.oracle.pyright_daemon import PyrightProcess, get_type_info


class TestGetTypeInfo:
    """Test suite for get_type_info function."""

    @pytest.fixture
    def mock_process(self):
        """Create a mock PyrightProcess."""
        process = PyrightProcess(
            process=Mock(),
            port=55440,
            pid=12345
        )
        return process

    def test_gets_type_information(self, mock_process):
        """
        Test that get_type_info returns type information.

        This is a normal case test - successful query.
        """
        expected_result = {
            "type": "int",
            "name": "MyClass",
            "definition": {"uri": "file:///test/definitions.py", "range": {"start": {"line": 0, "character": 0}, "end": {"line": 10, "character": 0}}}
        }

        with patch('semantic_agent.oracle.pyright_daemon._send_jsonrpc_request') as mock_send:
            mock_send.return_value = expected_result

            result = get_type_info(
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
            assert call_args[0][1] == "textDocument/typeDefinition"

            # Verify LSP params
            params = call_args[0][2]
            assert params["textDocument"]["uri"] == "file:///test/source.py"
            assert params["position"]["line"] == 2  # 0-indexed
            assert params["position"]["character"] == 10

    def test_raises_value_error_for_relative_path(self, mock_process):
        """
        Test that get_type_info raises ValueError for relative path.

        This is a failure case test - invalid input.
        """
        with pytest.raises(ValueError) as exc_info:
            get_type_info(mock_process, "relative/path.py", 1, 0)

        assert "file_path must be absolute path" in str(exc_info.value)

    def test_raises_value_error_for_line_zero(self, mock_process):
        """
        Test that get_type_info raises ValueError for line 0.

        This is a failure case test - invalid input.
        """
        with pytest.raises(ValueError) as exc_info:
            get_type_info(mock_process, "/test.py", 0, 0)

        assert "line must be >= 1" in str(exc_info.value)

    def test_raises_value_error_for_negative_line(self, mock_process):
        """
        Test that get_type_info raises ValueError for negative line.

        This is a failure case test - invalid input.
        """
        with pytest.raises(ValueError) as exc_info:
            get_type_info(mock_process, "/test.py", -1, 0)

        assert "line must be >= 1" in str(exc_info.value)

    def test_raises_value_error_for_negative_character(self, mock_process):
        """
        Test that get_type_info raises ValueError for negative character.

        This is a failure case test - invalid input.
        """
        with pytest.raises(ValueError) as exc_info:
            get_type_info(mock_process, "/test.py", 1, -1)

        assert "character must be >= 0" in str(exc_info.value)

    def test_raises_runtime_error_on_communication_failure(self, mock_process):
        """
        Test that get_type_info raises RuntimeError on communication failure.

        This is a failure case test - LSP communication error.
        """
        with patch('semantic_agent.oracle.pyright_daemon._send_jsonrpc_request') as mock_send:
            mock_send.side_effect = RuntimeError("Connection lost")

            with pytest.raises(RuntimeError) as exc_info:
                get_type_info(mock_process, "/test.py", 1, 0)

            assert "Failed to get type info" in str(exc_info.value)
            assert "Connection lost" in str(exc_info.value)

    def test_converts_line_to_zero_indexed(self, mock_process):
        """
        Test that get_type_info converts 1-indexed line to 0-indexed.

        This is a normal case test - verify LSP indexing.
        """
        with patch('semantic_agent.oracle.pyright_daemon._send_jsonrpc_request') as mock_send:
            mock_send.return_value = {}

            # Call with 1-indexed line
            get_type_info(mock_process, "/test.py", line=5, character=10)

            # Verify LSP received 0-indexed line
            params = mock_send.call_args[0][2]
            assert params["position"]["line"] == 4  # 5 - 1
            assert params["position"]["character"] == 10  # character unchanged

    def test_passes_absolute_path_correctly(self, mock_process):
        """
        Test that get_type_info passes absolute path correctly.

        This is a normal case test - verify path handling.
        """
        with patch('semantic_agent.oracle.pyright_daemon._send_jsonrpc_request') as mock_send:
            mock_send.return_value = {}

            get_type_info(mock_process, "/abs/path/test.py", 1, 0)

            # Verify URI format
            params = mock_send.call_args[0][2]
            assert params["textDocument"]["uri"] == "file:///abs/path/test.py"

    def test_handles_complex_type_definitions(self, mock_process):
        """
        Test that get_type_info handles complex type definitions.

        This is a normal case test - verify complex types.
        """
        expected_result = {
            "type": "Dict[str, List[int]]",
            "name": "ComplexType",
            "definition": {"uri": "file:///test/types.py", "range": {"start": {"line": 0, "character": 0}, "end": {"line": 20, "character": 0}}}
        }

        with patch('semantic_agent.oracle.pyright_daemon._send_jsonrpc_request') as mock_send:
            mock_send.return_value = expected_result

            result = get_type_info(mock_process, "/test/types.py", 1, 0)

            # Verify complex type is returned
            assert result["type"] == "Dict[str, List[int]]"
            assert result["definition"]["uri"] == "file:///test/types.py"

    def test_handles_union_types(self, mock_process):
        """
        Test that get_type_info handles union types correctly.

        This is a normal case test - verify union types.
        """
        expected_result = {
            "type": "str | int | None",
            "name": "UnionType",
            "definition": {"uri": "file:///test/union.py", "range": {"start": {"line": 0, "character": 0}, "end": {"line": 5, "character": 0}}}
        }

        with patch('semantic_agent.oracle.pyright_daemon._send_jsonrpc_request') as mock_send:
            mock_send.return_value = expected_result

            result = get_type_info(mock_process, "/test/union.py", 1, 0)

            assert result["type"] == "str | int | None"
