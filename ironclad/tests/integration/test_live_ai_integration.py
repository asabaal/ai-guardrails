#!/usr/bin/env python3
"""
Integration tests for Live AI model interactions.

These tests perform REAL network calls to configured AI provider(s).
Tests are skipped by default unless explicitly enabled via environment variables.

Tests use pytest marker @pytest.mark.live_ai to enable gating.
"""

import pytest
import os
import sys
import json
import signal
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_dir))

from ironclad_ai_guardrails.ironclad import (
    generate_candidate,
    repair_candidate,
    DEFAULT_MODEL_NAME
)
from ironclad_ai_guardrails.module_designer import (
    draft_blueprint,
    MODEL_NAME as DESIGNER_MODEL_NAME,
    ARCHITECT_PROMPT
)
from ironclad_ai_guardrails.factory_manager import (
    generate_main_candidate,
    repair_main_candidate,
    MODEL_NAME as FACTORY_MODEL_NAME
)


# Check if live tests are enabled
LIVE_AI_ENABLED = os.getenv("IRONCLAD_LIVE_AI_TESTS", "0") == "1"
LIVE_AI_TIMEOUT = int(os.getenv("IRONCLAD_LIVE_AI_TIMEOUT", "60"))


def timeout_handler(signum, frame):
    """Handle timeout for live AI calls."""
    raise TimeoutError(f"Live AI test exceeded {LIVE_AI_TIMEOUT} second timeout")


@pytest.fixture(scope="module", autouse=True)
def check_live_ai_enabled():
    """Skip live AI tests unless explicitly enabled."""
    if not LIVE_AI_ENABLED:
        pytest.skip(
            "Live AI tests are skipped by default. "
            "Enable with IRONCLAD_LIVE_AI_TESTS=1 environment variable."
        )


@pytest.mark.live_ai
def test_draft_blueprint_real_call(check_live_ai_enabled):
    """Test module_designer.draft_blueprint() makes real AI call and returns parseable output."""
    # Test with a simple, realistic request
    request = "I want a calculator that can add and subtract two numbers"
    
    # Set up timeout handler
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(LIVE_AI_TIMEOUT)
    
    try:
        # Call the actual AI function
        blueprint = draft_blueprint(request)
    finally:
        signal.alarm(0)  # Disable alarm
        signal.signal(signal.SIGALRM, old_handler)  # Restore old handler
    
    # Structural assertions - blueprint should exist and have expected keys
    assert blueprint is not None, "Blueprint should not be None"
    
    # Should be parseable as dict
    assert isinstance(blueprint, dict), "Blueprint should be a dict"
    
    # Required fields should exist
    required_keys = ["module_name", "functions", "main_logic_description"]
    for key in required_keys:
        assert key in blueprint, f"Blueprint should contain '{key}' field"
    
    # functions should be a list
    assert "functions" in blueprint, "Blueprint should have 'functions' field"
    assert isinstance(blueprint["functions"], list), "Functions should be a list"
    
    # Downstream consumption should not raise JSON errors
    try:
        json_str = json.dumps(blueprint)
        parsed = json.loads(json_str)
        assert parsed == blueprint, "Blueprint should be JSON serializable"
    except (TypeError, ValueError) as e:
        pytest.fail(f"Blueprint should be JSON serializable: {e}")


@pytest.mark.live_ai
def test_ironclad_generate_candidate_real_call(check_live_ai_enabled):
    """Test ironclad.generate_candidate() makes real AI call and returns parseable output."""
    # Test with a simple, realistic request
    request = "Create a function that adds two numbers"
    
    # Set up timeout handler
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(LIVE_AI_TIMEOUT)
    
    try:
        # Call the actual AI function
        candidate = generate_candidate(request)
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)
    
    # The live AI contract allows returning None for parse failures
    # This is acceptable behavior when model returns non-JSON output
    if candidate is None:
        return  # Test passes - None is valid per live AI contract
    
    # When candidate is not None, validate structural properties
    # Should be parseable as dict
    assert isinstance(candidate, dict), "Candidate should be a dict"
    
    # Required fields should exist
    required_keys = ["filename", "code", "test"]
    for key in required_keys:
        assert key in candidate, f"Candidate should contain '{key}' field"
    
    # code should be a string
    assert isinstance(candidate["code"], str), "Code should be a string"
    assert len(candidate["code"]) > 0, "Code should not be empty"
    
    # test should be a string
    assert isinstance(candidate["test"], str), "Test should be a string"
    assert len(candidate["test"]) > 0, "Test should not be empty"
    
    # Downstream parsing should work
    try:
        code = candidate["code"]
        compile(code, "<string>", "exec")
    except SyntaxError as e:
        pytest.fail(f"Generated code should be valid Python: {e}")


@pytest.mark.live_ai
def test_ironclad_repair_candidate_real_call(check_live_ai_enabled):
    """Test ironclad.repair_candidate() makes real AI call and returns parseable output."""
    # Create a simple candidate with an intentional error
    broken_code = """
def broken_function():
    x = 5
    y = 10
    return x + y  # Missing import or error trigger
""".strip()
    
    broken_candidate = {
        "filename": "broken_test",
        "code": broken_code,
        "test": "def test_broken(): pass"
    }
    
    traceback_log = "NameError: name 'x' is not defined"
    
    # Set up timeout handler
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(LIVE_AI_TIMEOUT)
    
    try:
        # Call the actual AI repair function
        repaired = repair_candidate(broken_candidate, traceback_log)
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)
    
    # Structural assertions - repair should either succeed or return None
    if repaired is not None:
        # Should be parseable as dict
        assert isinstance(repaired, dict), "Repaired candidate should be a dict"
        
        # Required fields should exist
        required_keys = ["filename", "code", "test"]
        for key in required_keys:
            assert key in repaired, f"Repaired candidate should contain '{key}' field"
        
        # Repaired code should be a string
        assert isinstance(repaired["code"], str), "Repaired code should be a string"
        assert len(repaired["code"]) > 0, "Repaired code should not be empty"
        
        # Downstream parsing should work
        try:
            code = repaired["code"]
            compile(code, "<string>", "exec")
        except SyntaxError as e:
            pytest.fail(f"Repaired code should be valid Python: {e}")


@pytest.mark.live_ai
def test_factory_generate_main_candidate_real_call(check_live_ai_enabled):
    """Test factory_manager.generate_main_candidate() makes real AI call and returns parseable output."""
    blueprint = {
        "module_name": "test_module",
        "main_logic_description": "Test module for integration",
        "functions": [
            {
                "name": "test_func",
                "signature": "def test_func(x: int) -> int:",
                "description": "Test function"
            }
        ]
    }
    
    components = ["test_func"]
    
    # Set up timeout handler
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(LIVE_AI_TIMEOUT)
    
    try:
        # Call the actual AI function
        main_code = generate_main_candidate(blueprint, components)
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)
    
    # Structural assertions - code should exist
    assert main_code is not None, "Main code should not be None"
    
    # Should be a string
    assert isinstance(main_code, str), "Main code should be a string"
    assert len(main_code) > 0, "Main code should not be empty"
    
    # Downstream parsing should work
    try:
        compile(main_code, "<string>", "exec")
    except SyntaxError as e:
        pytest.fail(f"Generated main code should be valid Python: {e}")


@pytest.mark.live_ai
def test_factory_repair_main_candidate_real_call(check_live_ai_enabled):
    """Test factory_manager.repair_main_candidate() makes real AI call and returns parseable output."""
    broken_code = """
def main():
    result = undefined_function()
    return result
""".strip()
    
    error_logs = "NameError: name 'undefined_function' is not defined"
    
    components = ["test_func"]
    
    # Set up timeout handler
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(LIVE_AI_TIMEOUT)
    
    try:
        # Call the actual AI repair function
        repaired_code = repair_main_candidate(broken_code, error_logs, components, ".")
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)
    
    # Structural assertions - repair should either succeed or return None
    if repaired_code is not None:
        # Should be a string
        assert isinstance(repaired_code, str), "Repaired code should be a string"
        assert len(repaired_code) > 0, "Repaired code should not be empty"
        
        # Downstream parsing should work
        try:
            compile(repaired_code, "<string>", "exec")
        except SyntaxError as e:
            pytest.fail(f"Repaired code should be valid Python: {e}")


@pytest.mark.live_ai
def test_multiple_ai_calls_sequential(check_live_ai_enabled):
    """Test sequential AI calls work correctly (simulate real workflow)."""
    # Step 1: Generate blueprint
    request = "Create a function that multiplies two numbers"
    
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(LIVE_AI_TIMEOUT)
    
    try:
        blueprint = draft_blueprint(request)
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)
    
    assert blueprint is not None, "Blueprint should be generated"
    
    # Step 2: Generate candidate code from blueprint
    signal.alarm(LIVE_AI_TIMEOUT)
    
    try:
        candidate = generate_candidate("create a multiplier function")
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)
    
    assert candidate is not None, "Candidate should be generated"
    
    # Step 3: Verify sequential calls produced parseable results
    assert isinstance(blueprint, dict), "Blueprint should be dict"
    assert isinstance(candidate, dict), "Candidate should be dict"
    
    # Both should be JSON serializable
    try:
        json.dumps(blueprint)
        json.dumps(candidate)
    except (TypeError, ValueError) as e:
        pytest.fail(f"Results should be JSON serializable: {e}")
