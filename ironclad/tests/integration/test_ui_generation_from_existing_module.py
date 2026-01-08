#!/usr/bin/env python3
"""
Integration tests for UI generation from existing modules.

These tests validate that Ironclad can generate UIs from already-generated modules,
exactly as a real user would do after module generation.

Tests use subprocess to invoke the CLI exactly as a user would.
Tests use pytest marker @pytest.mark.live_ai to enable gating.
"""

import pytest
import os
import sys
import subprocess
import json
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


@pytest.fixture(scope="module")
def generated_module(tmp_path_factory):
    """
    Generate a single module and reuse it for all UI generation tests.
    This is more efficient and avoids timeouts.
    """
    output_dir = tmp_path_factory.mktemp("shared_module")
    module_request = "Create a simple calculator with add and subtract functions"

    result = subprocess.run(
        [sys.executable, "-m", "ironclad_ai_guardrails.module_forge", module_request],
        capture_output=True,
        text=True,
        cwd=str(output_dir),
        timeout=LIVE_AI_TIMEOUT
    )

    assert result.returncode == 0, f"Module generation failed. Output: {result.stdout}\nError: {result.stderr}"

    build_dir = output_dir / "build"
    assert build_dir.exists(), "Build directory should be created"

    module_dirs = list(build_dir.iterdir())
    assert len(module_dirs) > 0, "At least one module directory should be created"

    module_dir = module_dirs[0]
    blueprint_file = output_dir / "blueprint.json"
    assert blueprint_file.exists(), "Blueprint file should exist"

    return {
        "module_dir": module_dir,
        "blueprint_file": blueprint_file,
        "output_dir": output_dir
    }


@pytest.mark.live_ai
def test_generate_web_ui_from_existing_module(generated_module, tmp_path):
    """
    Test that a web UI can be generated from an existing module.

    Workflow:
    1. Generate a module using ModuleForge
    2. Verify module directory exists
    3. Invoke UI generation for web
    4. Verify UI output directory exists
    5. Assertions on HTML files, entry HTML file, and non-empty files
    """
    module_dir = generated_module["module_dir"]
    module_output_dir = generated_module["output_dir"]

    assert module_dir.exists(), "Module directory should exist"
    assert (module_dir / "main.py").exists(), "main.py should exist in module directory"

    ui_output_dir = tmp_path / "web_ui_output"
    ui_output_dir.mkdir()

    spec_file = module_output_dir / "blueprint.json"

    result = subprocess.run(
        [
            sys.executable, "-m", "ironclad_ai_guardrails.ui_cli",
            "generate",
            "--spec", str(spec_file),
            "--type", "web",
            "--output", str(ui_output_dir)
        ],
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, f"UI generation failed. Output: {result.stdout}\nError: {result.stderr}"

    assert ui_output_dir.exists(), "UI output directory should exist"

    html_files = list(ui_output_dir.glob("*.html"))
    assert len(html_files) > 0, "At least one HTML file should exist"

    entry_html = ui_output_dir / "index.html"
    assert entry_html.exists(), "Entry HTML file (index.html) should exist"

    for html_file in html_files:
        assert html_file.stat().st_size > 0, f"HTML file {html_file.name} should not be empty"

    css_files = list(ui_output_dir.glob("*.css"))
    if css_files:
        for css_file in css_files:
            assert css_file.stat().st_size > 0, f"CSS file {css_file.name} should not be empty"

    js_files = list(ui_output_dir.glob("*.js"))
    if js_files:
        for js_file in js_files:
            assert js_file.stat().st_size > 0, f"JS file {js_file.name} should not be empty"


@pytest.mark.live_ai
def test_generate_cli_gui_from_existing_module(generated_module, tmp_path):
    """
    Test that a CLI GUI can be generated from an existing module.

    Workflow:
    1. Use an existing generated module
    2. Invoke UI generation for cli_gui
    3. Assertions on gui.py and requirements.txt existence and non-empty files
    """
    module_dir = generated_module["module_dir"]
    module_output_dir = generated_module["output_dir"]

    assert module_dir.exists(), "Module directory should exist"

    ui_output_dir = tmp_path / "cli_gui_output"
    ui_output_dir.mkdir()

    spec_file = module_output_dir / "blueprint.json"

    result = subprocess.run(
        [
            sys.executable, "-m", "ironclad_ai_guardrails.ui_cli",
            "generate",
            "--spec", str(spec_file),
            "--type", "cli_gui",
            "--output", str(ui_output_dir)
        ],
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, f"CLI GUI generation failed. Output: {result.stdout}\nError: {result.stderr}"

    gui_py = ui_output_dir / "gui.py"
    assert gui_py.exists(), "gui.py should exist"
    assert gui_py.stat().st_size > 0, "gui.py should not be empty"

    requirements_txt = ui_output_dir / "requirements.txt"
    assert requirements_txt.exists(), "requirements.txt should exist"
    assert requirements_txt.stat().st_size > 0, "requirements.txt should not be empty"


@pytest.mark.skip(reason="Desktop UI generation is not yet a supported system capability")
@pytest.mark.live_ai
def test_generate_desktop_ui_from_existing_module(generated_module, tmp_path):
    """
    Test that a desktop UI can be generated from an existing module.

    Workflow:
    1. Generate a module
    2. Invoke UI generation for desktop
    3. Assertions on desktop UI entry file existence, supporting files, and no empty critical files
    """
    module_dir = generated_module["module_dir"]
    module_output_dir = generated_module["output_dir"]

    assert module_dir.exists(), "Module directory should exist"

    ui_output_dir = tmp_path / "desktop_ui_output"
    ui_output_dir.mkdir()

    spec_file = module_output_dir / "blueprint.json"

    result = subprocess.run(
        [
            sys.executable, "-m", "ironclad_ai_guardrails.ui_cli",
            "generate",
            "--spec", str(spec_file),
            "--type", "desktop",
            "--output", str(ui_output_dir)
        ],
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, f"Desktop UI generation failed. Output: {result.stdout}\nError: {result.stderr}"

    main_js = ui_output_dir / "main.js"
    assert main_js.exists(), "Desktop UI entry file (main.js) should exist"
    assert main_js.stat().st_size > 0, "main.js should not be empty"

    index_html = ui_output_dir / "index.html"
    assert index_html.exists(), "index.html should exist"
    assert index_html.stat().st_size > 0, "index.html should not be empty"

    package_json = ui_output_dir / "package.json"
    assert package_json.exists(), "package.json should exist"
    assert package_json.stat().st_size > 0, "package.json should not be empty"

    preload_js = ui_output_dir / "preload.js"
    if preload_js.exists():
        assert preload_js.stat().st_size > 0, "preload.js should not be empty"


@pytest.mark.skip(reason="API docs generation from existing modules is not yet stable")
@pytest.mark.live_ai
def test_generate_api_docs_from_existing_module(generated_module, tmp_path):
    """
    Test that API documentation can be generated from an existing module.

    Workflow:
    1. Generate a module
    2. Invoke UI generation for api_docs
    3. Assertions on OpenAPI spec existence, Swagger/HTML docs, and parseable files
    """
    module_dir = generated_module["module_dir"]
    module_output_dir = generated_module["output_dir"]

    assert module_dir.exists(), "Module directory should exist"

    ui_output_dir = tmp_path / "api_docs_output"
    ui_output_dir.mkdir()

    spec_file = module_output_dir / "blueprint.json"

    result = subprocess.run(
        [
            sys.executable, "-m", "ironclad_ai_guardrails.ui_cli",
            "generate",
            "--spec", str(spec_file),
            "--type", "api_docs",
            "--output", str(ui_output_dir)
        ],
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, f"API docs generation failed. Output: {result.stdout}\nError: {result.stderr}"

    openapi_json = ui_output_dir / "openapi.json"
    assert openapi_json.exists(), "OpenAPI spec (openapi.json) should exist"
    assert openapi_json.stat().st_size > 0, "openapi.json should not be empty"

    with open(openapi_json, 'r') as f:
        openapi_content = json.load(f)

    assert "openapi" in openapi_content or "swagger" in openapi_content, "OpenAPI spec should have 'openapi' or 'swagger' field"
    assert "info" in openapi_content, "OpenAPI spec should have 'info' field"

    swagger_html = ui_output_dir / "swagger.html"
    assert swagger_html.exists(), "Swagger HTML should exist"
    assert swagger_html.stat().st_size > 0, "swagger.html should not be empty"

    html_content = swagger_html.read_text()
    assert "<html" in html_content.lower() or "<!doctype" in html_content.lower(), "swagger.html should contain valid HTML markup"
