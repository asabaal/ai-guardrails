from __future__ import annotations

import os
import subprocess
import sys
import time

import pytest


@pytest.fixture
def watchdog_bin():
    return [sys.executable, "-m", "ai_guardrails.operational_safety.ai_watchdog"]


class TestSmokeRun:
    def test_sleep_5_exits_zero(self, watchdog_bin, tmp_path):
        log_dir = tmp_path / "logs"
        result = subprocess.run(
            watchdog_bin + ["run", "--log-dir", str(log_dir), "--", "sleep", "2"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"

    def test_log_file_created(self, watchdog_bin, tmp_path):
        log_dir = tmp_path / "logs"
        subprocess.run(
            watchdog_bin + ["run", "--log-dir", str(log_dir), "--", "sleep", "1"],
            capture_output=True,
            text=True,
            timeout=20,
        )
        log_files = list(log_dir.glob("*.jsonl"))
        assert len(log_files) >= 1, f"No log files in {log_dir}"

    def test_log_file_contains_poll_data(self, watchdog_bin, tmp_path):
        import json

        log_dir = tmp_path / "logs"
        subprocess.run(
            watchdog_bin + ["run", "--log-dir", str(log_dir), "--", "sleep", "3"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        log_files = list(log_dir.glob("*.jsonl"))
        assert log_files
        with open(log_files[0]) as f:
            lines = f.readlines()
        poll_lines = [json.loads(l) for l in lines if l.strip()]
        assert any(entry.get("action") == "none" for entry in poll_lines)
        assert any(entry.get("action") == "summary" for entry in poll_lines)

    def test_exit_code_forwarded(self, watchdog_bin, tmp_path):
        log_dir = tmp_path / "logs"
        result = subprocess.run(
            watchdog_bin + ["run", "--log-dir", str(log_dir), "--", "bash", "-c", "exit 42"],
            capture_output=True,
            text=True,
            timeout=20,
        )
        assert result.returncode == 42

    def test_show_sensors_runs(self, watchdog_bin):
        result = subprocess.run(
            watchdog_bin + ["show-sensors"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0

    def test_dump_config_runs(self, watchdog_bin):
        result = subprocess.run(
            watchdog_bin + ["dump-config"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "cpu_temp" in result.stdout
