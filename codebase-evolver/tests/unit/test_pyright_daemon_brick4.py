"""
Unit tests for Pyright daemon - initialize function

Tests follow verified brick commissioning protocol with 100% statement coverage.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from semantic_agent.oracle.pyright_daemon import PyrightProcess, initialize


class TestInitialize:
    """Test suite for initialize function."""

    @pytest.fixture
    def mock_process(self):
        """Create a mock PyrightProcess."""
        process = PyrightProcess(
            process=Mock(),
            port=55440,
            pid=12345
        )
        return process

    @pytest.fixture
    def test_repo(self, tmp_path):
        """Create a test repository."""
        repo_dir = tmp_path / "test_repo"
        repo_dir.mkdir()
        return str(repo_dir)

    def test_initializes_pyright_with_valid_inputs(self, mock_process, test_repo):
        """
        Test that initialize sends valid LSP initialize request.

        This is a normal case test - successful initialization.
        """
        with patch('semantic_agent.oracle.pyright_daemon._send_jsonrpc_request') as mock_send:
            mock_send.return_value = {
                "capabilities": {
                    "textDocument": {
                        "hover": {"contentFormat": ["markdown"]},
                        "definition": {},
                        "references": {}
                    }
                }
            }

            result = initialize(mock_process, test_repo)

            # Verify send was called correctly
            assert mock_send.called
            call_args = mock_send.call_args
            assert call_args[0][0] == mock_process
            assert call_args[0][1] == "initialize"
            assert call_args[0][2]["processId"] == 1
            assert "rootUri" in call_args[0][2]
            assert call_args[0][2]["rootUri"] == f"file://{test_repo}"
            assert "capabilities" in call_args[0][2]

            # Verify result is returned
            assert result["capabilities"] is not None

    def test_raises_value_error_for_relative_path(self, mock_process):
        """
        Test that initialize raises ValueError for relative path.

        This is a failure case test - invalid input.
        """
        with pytest.raises(ValueError) as exc_info:
            initialize(mock_process, "relative/path")

        assert "root_path must be absolute path" in str(exc_info.value)

    def test_raises_value_error_for_nonexistent_path(self, mock_process):
        """
        Test that initialize raises ValueError for nonexistent path.

        This is a failure case test - invalid input.
        """
        with patch('os.path.isdir', return_value=False):
            with pytest.raises(ValueError) as exc_info:
                initialize(mock_process, "/nonexistent/path/12345")

            assert "root_path does not exist or is not a directory" in str(exc_info.value)

    def test_raises_value_error_for_file_not_directory(self, tmp_path, mock_process):
        """
        Test that initialize raises ValueError when path is a file.

        This is a failure case test - path is a file, not directory.
        """
        # Create a file instead of directory
        file_path = tmp_path / "not_a_dir.txt"
        file_path.write_text("test")

        with pytest.raises(ValueError) as exc_info:
            initialize(mock_process, str(file_path))

        assert "root_path does not exist or is not a directory" in str(exc_info.value)

    def test_raises_runtime_error_on_communication_failure(self, mock_process):
        """
        Test that initialize raises RuntimeError on communication failure.

        This is a failure case test - LSP communication error.
        """
        with patch('semantic_agent.oracle.pyright_daemon._send_jsonrpc_request') as mock_send:
            mock_send.side_effect = RuntimeError("Connection lost")

            # Create actual test directory
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdir:
                with pytest.raises(RuntimeError) as exc_info:
                    initialize(mock_process, tmpdir)

                assert "Failed to initialize Pyright" in str(exc_info.value)
                assert "Connection lost" in str(exc_info.value)

    def test_passes_root_uri_with_triple_slash(self, mock_process, test_repo):
        """
        Test that initialize passes correct rootUri format.

        This is a normal case test - verify URI format.
        """
        with patch('semantic_agent.oracle.pyright_daemon._send_jsonrpc_request') as mock_send:
            mock_send.return_value = {"capabilities": {}}

            result = initialize(mock_process, test_repo)

            # Verify URI format
            call_args = mock_send.call_args[0][2]
            assert call_args["rootUri"] == f"file://{test_repo}"

    def test_sends_expected_capabilities(self, mock_process, test_repo):
        """
        Test that initialize sends expected client capabilities.

        This is a normal case test - verify capability structure.
        """
        with patch('semantic_agent.oracle.pyright_daemon._send_jsonrpc_request') as mock_send:
            mock_send.return_value = {"capabilities": {}}

            result = initialize(mock_process, test_repo)

            # Verify capabilities structure
            call_args = mock_send.call_args[0][2]
            caps = call_args["capabilities"]
            assert "textDocument" in caps
            assert "hover" in caps["textDocument"]
            assert "definition" in caps["textDocument"]
            assert "references" in caps["textDocument"]
            assert "typeDefinition" in caps["textDocument"]
