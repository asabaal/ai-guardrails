"""
Common fixtures for opencode-restore tests.
"""

import pytest
from pathlib import Path


@pytest.fixture
def tmp_path(tmp_path_factory):
    """Create a temporary directory for tests."""
    return tmp_path_factory.mktemp("test_dir")


@pytest.fixture
def sample_raw_log(tmp_path):
    """Create a sample raw log file for testing."""
    log_file = tmp_path / "sample.raw.log"
    log_file.write_text(
        'Script started on 2025-12-22 14:19:12-06:00 [COMMAND="opencode" TERM="xterm-256color" TTY="/dev/pts/7" COLUMNS="219" LINES="52"]\n'
        '[38;2;238;238;238mopen[38;2;238;238;238;1mcode[38;2;238;238;238;22m v0.13.5[39m\n'
        '┃  ┃\n'
        '[38;2;238;238;238mUser: Create a function to add two numbers[39m\n'
        '[38;2;92;156;245mAI: I will create a function to add two numbers[39m\n'
        '────────────────\n'
        'def add(a, b):\n'
        '    return a + b\n'
    )
    return log_file
