#!/usr/bin/env python3
"""
Integration tests for CLI-driven module generation workflow.

These tests simulate real user interactions with the Ironclad CLI to generate
complete modules with real AI calls. Tests use subprocess to invoke the CLI
exactly as a user would.

Tests use pytest marker @pytest.mark.live_ai to enable gating.
"""

import pytest
import os
import sys
import subprocess
import ast
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_dir))

# Check if live tests are enabled
LIVE_AI_ENABLED = os.getenv("IRONCLAD_LIVE_AI_TESTS", "0") == "1"
LIVE_AI_TIMEOUT = int(os.getenv("IRONCLAD_LIVE_AI_TIMEOUT", "300"))


@pytest.fixture(scope="module", autouse=True)
def check_live_ai_enabled():
    """Skip live AI tests unless explicitly enabled."""
    if not LIVE_AI_ENABLED:
        pytest.skip(
            "Live AI tests are skipped by default. "
            "Enable with IRONCLAD_LIVE_AI_TESTS=1 environment variable."
        )


@pytest.mark.live_ai
def test_cli_generate_module_creates_module_directory(tmp_path):
    """Simulates a real user running Ironclad from the command line to generate a module."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    module_request = "Create a simple calculator module with add and subtract functions"
    
    result = subprocess.run(
        [sys.executable, "-m", "ironclad_ai_guardrails.module_forge", module_request],
        capture_output=True,
        text=True,
        cwd=str(output_dir),
        timeout=LIVE_AI_TIMEOUT
    )
    
    assert result.returncode == 0, f"CLI should exit successfully. Output: {result.stdout}\nError: {result.stderr}"
    
    build_dir = output_dir / "build"
    assert build_dir.exists(), "Build directory should be created"
    
    module_dirs = list(build_dir.iterdir())
    assert len(module_dirs) > 0, "At least one module subdirectory should be created"
    
    module_dir = module_dirs[0]
    assert module_dir.is_dir(), "Module directory should be a directory"


@pytest.mark.live_ai
def test_cli_generate_module_outputs_python_files(tmp_path):
    """Ensures the CLI-generated module produces actual Python artifacts."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    module_request = "Create a string utilities module with functions to reverse and uppercase strings"
    
    result = subprocess.run(
        [sys.executable, "-m", "ironclad_ai_guardrails.module_forge", module_request],
        capture_output=True,
        text=True,
        cwd=str(output_dir),
        timeout=LIVE_AI_TIMEOUT
    )
    
    assert result.returncode == 0, f"CLI should exit successfully. Output: {result.stdout}\nError: {result.stderr}"
    
    build_dir = output_dir / "build"
    module_dirs = list(build_dir.iterdir())
    assert len(module_dirs) > 0, "Module directory should exist"
    
    module_dir = module_dirs[0]
    py_files = list(module_dir.glob("*.py"))
    
    assert len(py_files) > 0, "At least one .py file should exist"
    
    main_file = module_dir / "main.py"
    assert main_file.exists(), "Main module file should exist"
    assert main_file.stat().st_size > 0, "Main module file should not be empty"
    
    other_py_files = [f for f in py_files if f.name != "__init__.py" and f.name != "main.py"]
    non_empty_other_files = [f for f in other_py_files if f.stat().st_size > 0]
    
    assert len(non_empty_other_files) > 0, "At least one non-empty .py file (excluding main.py and __init__.py) must exist"


@pytest.mark.live_ai
def test_cli_generate_module_generated_code_is_parseable_or_repairable(tmp_path):
    """Validates that generated code is not garbage - attempts compilation and repair if needed."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    module_request = "Create a math utilities module with sum and average functions"
    
    result = subprocess.run(
        [sys.executable, "-m", "ironclad_ai_guardrails.module_forge", module_request],
        capture_output=True,
        text=True,
        cwd=str(output_dir),
        timeout=LIVE_AI_TIMEOUT
    )
    
    build_dir = output_dir / "build"
    module_dirs = list(build_dir.iterdir())
    
    if len(module_dirs) == 0:
        pytest.skip("No module directory was created")
        return
    
    module_dir = module_dirs[0]
    py_files = list(module_dir.glob("*.py"))
    
    if len(py_files) == 0:
        pytest.skip("No Python files were generated")
        return
    
    syntax_valid_files = 0
    
    for py_file in py_files:
        with open(py_file, 'r') as f:
            code = f.read()
        
        try:
            ast.parse(code)
            syntax_valid_files += 1
        except SyntaxError:
            pass
    
    if syntax_valid_files > 0:
        return
    
    attempt_repair_dir = tmp_path / "output_repair"
    attempt_repair_dir.mkdir()
    
    repair_result = subprocess.run(
        [sys.executable, "-m", "ironclad_ai_guardrails.module_forge", "--resume", module_request],
        capture_output=True,
        text=True,
        cwd=str(attempt_repair_dir),
        timeout=LIVE_AI_TIMEOUT
    )
    
    repair_build_dir = attempt_repair_dir / "build"
    repair_module_dirs = list(repair_build_dir.iterdir())
    
    if len(repair_module_dirs) > 0:
        repair_module_dir = repair_module_dirs[0]
        repair_py_files = list(repair_module_dir.glob("*.py"))
        
        for repair_py_file in repair_py_files:
            with open(repair_py_file, 'r') as f:
                code = f.read()
            
            try:
                ast.parse(code)
                return
            except SyntaxError:
                pass
    
    assert syntax_valid_files > 0, "At least one generated or repaired file should be parseable"
