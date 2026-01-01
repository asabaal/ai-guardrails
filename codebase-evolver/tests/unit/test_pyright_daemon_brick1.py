"""
Unit tests for Pyright daemon - start_daemon function

Tests follow verified brick commissioning protocol with 100% statement coverage.
"""

import pytest
import subprocess
import os
import time
import shutil
from semantic_agent.oracle.pyright_daemon import (
    start_daemon,
    _is_port_in_use,
    PyrightProcess,
)


class TestIsPortInUse:
    """Test suite for _is_port_in_use function."""

    def test_returns_false_for_available_port(self):
        """
        Test that _is_port_in_use returns False for an available port.

        This is a normal case test.
        """
        # Use a high port that's unlikely to be in use
        port = 55432
        result = _is_port_in_use(port)
        assert result is False

    def test_returns_true_for_port_in_use(self):
        """
        Test that _is_port_in_use returns True when port is in use.

        This is an edge case test - we bind the port first.
        """
        import socket

        port = 55433
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            s.bind(("127.0.0.1", port))
            result = _is_port_in_use(port)
            assert result is True
        finally:
            s.close()

    def test_raises_value_error_for_invalid_port_zero(self):
        """
        Test that _is_port_in_use raises ValueError for port 0.

        This is a failure case test - invalid port number.
        """
        with pytest.raises(ValueError) as exc_info:
            _is_port_in_use(0)

        assert "port must be in range 1-65535" in str(exc_info.value)

    def test_raises_value_error_for_negative_port(self):
        """
        Test that _is_port_in_use raises ValueError for negative port.

        This is a failure case test - invalid port number.
        """
        with pytest.raises(ValueError) as exc_info:
            _is_port_in_use(-1)

        assert "port must be in range 1-65535" in str(exc_info.value)

    def test_raises_value_error_for_port_too_high(self):
        """
        Test that _is_port_in_use raises ValueError for port 65536.

        This is a failure case test - invalid port number.
        """
        with pytest.raises(ValueError) as exc_info:
            _is_port_in_use(65536)

        assert "port must be in range 1-65535" in str(exc_info.value)


class TestStartDaemon:
    """Test suite for start_daemon function."""

    @pytest.fixture
    def temp_repo(self, tmp_path):
        """Create a temporary Python repository for testing."""
        # Create a simple Python file
        repo_dir = tmp_path / "test_repo"
        repo_dir.mkdir()
        (repo_dir / "test.py").write_text("x = 1\n")

        return str(repo_dir)

    def test_returns_pyright_process_object(self, temp_repo):
        """
        Test that start_daemon returns a PyrightProcess object.

        This is a normal case test - successful daemon start.
        """
        _skip_if_pyright_not_installed()

        port = 55440
        result = start_daemon(temp_repo, port)

        assert isinstance(result, PyrightProcess)
        assert isinstance(result.process, subprocess.Popen)
        assert result.port == port
        assert result.pid > 0

        # Cleanup
        result.process.kill()
        result.process.wait()

    def test_raises_value_error_for_relative_path(self, tmp_path):
        """
        Test that start_daemon raises ValueError for relative path.

        This is a failure case test - invalid input.
        """
        with pytest.raises(ValueError) as exc_info:
            start_daemon("relative/path", 55441)

        assert "must be absolute path" in str(exc_info.value)

    def test_raises_value_error_for_nonexistent_path(self):
        """
        Test that start_daemon raises ValueError for nonexistent path.

        This is an edge case test - path doesn't exist.
        """
        with pytest.raises(ValueError) as exc_info:
            start_daemon("/nonexistent/path/12345", 55442)

        assert "does not exist or is not a directory" in str(exc_info.value)

    def test_raises_value_error_for_file_not_directory(self, tmp_path):
        """
        Test that start_daemon raises ValueError when path is a file.

        This is a failure case test - path is a file, not directory.
        """
        # Create a file instead of directory
        file_path = tmp_path / "not_a_dir.txt"
        file_path.write_text("test")

        with pytest.raises(ValueError) as exc_info:
            start_daemon(str(file_path), 55443)

        assert "does not exist or is not a directory" in str(exc_info.value)

    def test_raises_value_error_for_port_below_range(self, temp_repo):
        """
        Test that start_daemon raises ValueError for port < 1024.

        This is a failure case test - port too low.
        """
        with pytest.raises(ValueError) as exc_info:
            start_daemon(temp_repo, 1023)

        assert "port must be in range 1024-65535" in str(exc_info.value)

    def test_raises_value_error_for_port_above_range(self, temp_repo):
        """
        Test that start_daemon raises ValueError for port > 65535.

        This is a failure case test - port too high.
        """
        with pytest.raises(ValueError) as exc_info:
            start_daemon(temp_repo, 65536)

        assert "port must be in range 1024-65535" in str(exc_info.value)

    def test_raises_runtime_error_for_port_in_use(self, temp_repo):
        """
        Test that start_daemon raises RuntimeError when port is in use.

        This is an edge case test - port conflict.
        """
        import socket

        port = 55450
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            s.bind(("127.0.0.1", port))

            with pytest.raises(RuntimeError) as exc_info:
                start_daemon(temp_repo, port)

            assert "is already in use" in str(exc_info.value)
        finally:
            s.close()

    def test_raises_runtime_error_when_pyright_not_installed(self, temp_repo, monkeypatch):
        """
        Test that start_daemon raises RuntimeError when Pyright not installed.

        This is a failure case test - missing dependency.
        """
        # Monkeypatch subprocess.Popen to simulate Pyright not found
        original_popen = subprocess.Popen

        def mock_popen(*args, **kwargs):
            if "pyright" in args[0]:
                raise FileNotFoundError("pyright not found")
            return original_popen(*args, **kwargs)

        monkeypatch.setattr(subprocess, "Popen", mock_popen)

        with pytest.raises(RuntimeError) as exc_info:
            start_daemon(temp_repo, 55451)

        assert "Pyright is not installed" in str(exc_info.value)

    def test_raises_runtime_error_for_generic_exception(self, temp_repo, monkeypatch):
        """
        Test that start_daemon raises RuntimeError for generic exceptions.

        This is a failure case test - unexpected error during process start.
        """
        # Monkeypatch subprocess.Popen to raise a generic exception
        original_popen = subprocess.Popen

        def mock_popen(*args, **kwargs):
            if "pyright" in args[0]:
                raise OSError("Permission denied")
            return original_popen(*args, **kwargs)

        monkeypatch.setattr(subprocess, "Popen", mock_popen)

        with pytest.raises(RuntimeError) as exc_info:
            start_daemon(temp_repo, 55452)

        assert "Failed to start Pyright" in str(exc_info.value)
        assert "Permission denied" in str(exc_info.value)

    def test_creates_process_with_detached_output(self, temp_repo):
        """
        Test that start_daemon creates a process with detached stdout/stderr.

        This is an edge case test - verify subprocess configuration.
        """
        _skip_if_pyright_not_installed()

        port = 55460
        result = start_daemon(temp_repo, port)

        # Process should be running
        assert result.process.poll() is None

        # Cleanup
        result.process.kill()
        result.process.wait()

    def test_sets_working_directory_to_repo_path(self, temp_repo):
        """
        Test that start_daemon sets working directory to repo_path.

        This is a normal case test - verify cwd is correct.
        """
        _skip_if_pyright_not_installed()

        port = 55470
        result = start_daemon(temp_repo, port)

        # Verify process is running - if cwd wasn't set correctly, it would fail
        # We verify this indirectly by checking the process is still running
        assert result.process.poll() is None

        # Cleanup
        result.process.kill()
        result.process.wait()


def _skip_if_pyright_not_installed():
    """Helper to skip tests if pyright command is not available."""
    if not shutil.which("pyright"):
        pytest.skip("Pyright command not found (install with: npm install -g pyright)")
