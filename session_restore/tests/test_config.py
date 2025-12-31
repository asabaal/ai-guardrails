"""
Unit tests for config.py.
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch

from opencode_restore.config import (
    DEFAULT_MODEL,
    DEFAULT_MAX_LINES,
    DEFAULT_OUTPUT_FORMAT,
    DEFAULT_OLLAMA_BASE_URL,
    ANSI_ESCAPE_PATTERN,
    SCRIPT_HEADER_PATTERN,
    SUMMARY_SCHEMA,
    get_default_output_path,
)


class TestConfigConstants:
    """Test configuration constants."""

    def test_default_model(self):
        assert DEFAULT_MODEL == "gpt-oss20b"

    def test_default_max_lines(self):
        assert DEFAULT_MAX_LINES == 600

    def test_default_output_format(self):
        assert DEFAULT_OUTPUT_FORMAT == "md"

    def test_default_ollama_base_url(self):
        assert DEFAULT_OLLAMA_BASE_URL == "http://localhost:11434"

    def test_ansi_escape_pattern_is_string(self):
        assert isinstance(ANSI_ESCAPE_PATTERN, str)
        assert "\\x1b" in ANSI_ESCAPE_PATTERN

    def test_script_header_pattern_is_string(self):
        assert isinstance(SCRIPT_HEADER_PATTERN, str)
        assert "Script started on" in SCRIPT_HEADER_PATTERN

    def test_summary_schema_is_string(self):
        assert isinstance(SUMMARY_SCHEMA, str)
        assert "SESSION SUMMARY" in SUMMARY_SCHEMA


class TestGetDefaultOutputPath:
    """Test get_default_output_path function."""

    def test_md_format(self):
        result = get_default_output_path("test_session", "md")
        assert result == Path("SUMMARY_test_session.md")

    def test_json_format(self):
        result = get_default_output_path("test_session", "json")
        assert result == Path("SUMMARY_test_session.json")

    def test_default_format(self):
        result = get_default_output_path("test_session")
        assert result == Path("SUMMARY_test_session.md")

    def test_session_name_with_special_chars(self):
        result = get_default_output_path("my-test-session_123", "md")
        assert result == Path("SUMMARY_my-test-session_123.md")


class TestEnvironmentVariables:
    """Test environment variable handling."""

    @patch.dict(os.environ, {"OLLAMA_HOST": "http://custom-host:11435"}, clear=True)
    def test_ollama_host_from_env(self):
        from opencode_restore import config
        import importlib
        importlib.reload(config)

        assert config.DEFAULT_OLLAMA_BASE_URL == "http://custom-host:11435"

    @patch.dict(os.environ, {}, clear=True)
    def test_ollama_host_default_when_env_not_set(self):
        from opencode_restore import config
        import importlib
        importlib.reload(config)

        assert config.DEFAULT_OLLAMA_BASE_URL == "http://localhost:11434"
