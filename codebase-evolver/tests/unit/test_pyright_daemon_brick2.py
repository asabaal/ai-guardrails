"""
Unit tests for Pyright daemon - stop_daemon function

Tests follow verified brick commissioning protocol with 100% statement coverage.
"""

import pytest
import subprocess
import time
import shutil
from semantic_agent.oracle.pyright_daemon import (
    start_daemon,
    stop_daemon,
    PyrightProcess,
)


class TestStopDaemon:
    """Test suite for stop_daemon function."""

    @pytest.fixture
    def temp_repo(self, tmp_path):
        """Create a temporary Python repository for testing."""
        repo_dir = tmp_path / "test_repo"
        repo_dir.mkdir()
        (repo_dir / "test.py").write_text("x = 1\n")

        return str(repo_dir)

    @pytest.fixture
    def running_daemon(self, temp_repo):
        """
        Fixture that starts a daemon and provides it for testing.
        Automatically stops it after test.
        """
        _skip_if_pyright_not_installed()

        port = 55490
        process = start_daemon(temp_repo, port)

        yield process

        # Cleanup after test
        if process.process.poll() is None:
            process.process.kill()
            process.process.wait()

    def test_stops_running_daemon_gracefully(self, running_daemon):
        """
        Test that stop_daemon gracefully terminates a running daemon.

        This is a normal case test - successful graceful stop.
        """
        # Verify daemon is running
        assert running_daemon.process.poll() is None

        # Stop daemon
        stop_daemon(running_daemon)

        # Verify daemon is stopped
        assert running_daemon.process.poll() is not None

    def test_handles_already_stopped_daemon(self, temp_repo):
        """
        Test that stop_daemon handles already stopped daemon gracefully.

        This is an edge case test - daemon already stopped.
        """
        _skip_if_pyright_not_installed()

        port = 55491
        process = start_daemon(temp_repo, port)

        # Stop daemon manually
        process.process.kill()
        process.process.wait()

        # Verify daemon is stopped
        assert process.process.poll() is not None

        # Try to stop again (should not raise error)
        stop_daemon(process)

    def test_raises_value_error_for_none_process(self):
        """
        Test that stop_daemon raises ValueError for None process.

        This is a failure case test - invalid input.
        """
        with pytest.raises(ValueError) as exc_info:
            stop_daemon(None)

        assert "process cannot be None" in str(exc_info.value)

    def test_raises_value_error_for_invalid_type(self):
        """
        Test that stop_daemon raises ValueError for non-PyrightProcess.

        This is a failure case test - invalid input type.
        """
        with pytest.raises(ValueError) as exc_info:
            stop_daemon("not a process")

        assert "process must be PyrightProcess" in str(exc_info.value)

        with pytest.raises(ValueError) as exc_info:
            stop_daemon({"process": "fake", "port": 8080})

        assert "process must be PyrightProcess" in str(exc_info.value)

    def test_force_kills_unresponsive_daemon(self, temp_repo, monkeypatch):
        """
        Test that stop_daemon force kills daemon that won't stop gracefully.

        This is an edge case test - unresponsive process.
        """
        _skip_if_pyright_not_installed()

        port = 55492
        process = start_daemon(temp_repo, port)

        # Track calls to verify behavior
        terminate_called = [False]
        kill_called = [False]
        wait_call_count = [0]

        # Mock terminate() and kill() to track calls
        def mock_terminate():
            terminate_called[0] = True

        def mock_kill():
            kill_called[0] = True

        # Mock wait() to timeout on first call, succeed on second
        original_wait = process.process.wait
        wait_count = 0

        def mock_wait(*args, **kwargs):
            nonlocal wait_count
            wait_count += 1
            wait_call_count[0] = wait_count

            if wait_count == 1:
                # First wait() call - timeout (simulate unresponsive)
                raise subprocess.TimeoutExpired("pyright", 5)
            else:
                # Second wait() call - succeed (after kill)
                return 0

        # Mock poll() to return exit code after kill
        def mock_poll():
            if kill_called[0]:
                return 0  # Process exited after kill
            return None  # Still running

        monkeypatch.setattr(process.process, "terminate", mock_terminate)
        monkeypatch.setattr(process.process, "kill", mock_kill)
        monkeypatch.setattr(process.process, "wait", mock_wait)
        monkeypatch.setattr(process.process, "poll", mock_poll)

        # Stop daemon - should call terminate, then kill after timeout
        stop_daemon(process)

        # Verify terminate was called
        assert terminate_called[0], "terminate() should be called"

        # Verify kill was called
        assert kill_called[0], "kill() should be called after timeout"

        # Verify wait() was called twice (once for graceful, once after kill)
        assert wait_call_count[0] == 2, f"wait() should be called twice, got {wait_call_count[0]}"

    def test_raises_runtime_error_on_exception(self, temp_repo, monkeypatch):
        """
        Test that stop_daemon raises RuntimeError on unexpected exception.

        This is a failure case test - unexpected error during stop.
        """
        _skip_if_pyright_not_installed()

        port = 55493
        process = start_daemon(temp_repo, port)

        # Monkeypatch terminate() to raise exception
        def mock_terminate():
            raise OSError("Permission denied")

        monkeypatch.setattr(process.process, "terminate", mock_terminate)

        with pytest.raises(RuntimeError) as exc_info:
            stop_daemon(process)

        assert "Failed to stop Pyright daemon" in str(exc_info.value)
        assert "Permission denied" in str(exc_info.value)

        # Cleanup
        process.process.kill()
        process.process.wait()


def _skip_if_pyright_not_installed():
    """Helper to skip tests if pyright command is not available."""
    if not shutil.which("pyright"):
        pytest.skip("Pyright command not found (install with: npm install -g pyright)")
