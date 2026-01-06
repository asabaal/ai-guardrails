#!/usr/bin/env python3
"""
Integration tests for Ironclad CLI.

These tests verify that Ironclad CLI correctly routes user commands to the system.
Tests use real filesystem operations via tmp_path.
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

from ironclad_ai_guardrails.ui_cli import main as ui_cli_main
from ironclad_ai_guardrails.ui_spec import UIType, transform_module_spec_to_ui_spec
from ironclad_ai_guardrails.ui_generator import save_ui_artifacts


class TestCLIIntegration:
    """Integration tests for CLI functionality."""

    @pytest.fixture
    def valid_web_ui_dir(self, tmp_path):
        """Create a valid Web UI directory for testing."""
        web_dir = tmp_path / "web_ui"
        web_dir.mkdir()
        
        # Create valid web UI files
        module_spec = {
            "module_name": "test_module",
            "main_logic_description": "Test module",
            "functions": [
                {
                    "name": "main",
                    "signature": "def main() -> None:",
                    "description": "Main function"
                }
            ]
        }
        
        ui_spec = transform_module_spec_to_ui_spec(module_spec, UIType.WEB)
        save_ui_artifacts(ui_spec, str(web_dir))
        
        return web_dir

    @pytest.fixture
    def web_ui_with_minor_issues(self, tmp_path):
        """Create a Web UI directory with minor issues."""
        web_dir = tmp_path / "web_ui_issues"
        web_dir.mkdir()
        
        # Create minimal HTML (missing some recommended elements)
        (web_dir / "index.html").write_text("""<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body></body>
</html>""")
        
        (web_dir / "styles.css").write_text("body { margin: 0; }")
        (web_dir / "app.js").write_text("console.log('test');")
        (web_dir / "package.json").write_text('{"name": "test"}')
        
        return web_dir

    def test_validate_valid_web_ui_success(self, valid_web_ui_dir, capsys):
        """Test validating a valid Web UI returns success."""
        # Prepare CLI arguments
        sys.argv = [
            "ironclad-ui",
            "validate",
            "--ui-dir", str(valid_web_ui_dir),
            "--ui-type", "web"
        ]
        
        # Invoke CLI and capture exit
        with pytest.raises(SystemExit) as exc_info:
            ui_cli_main()
        
        # Assertions - success (0) or warning (2) are both acceptable
        assert exc_info.value.code in [0, 2], \
            f"Exit code should indicate success or warning, got {exc_info.value.code}"
        
        # Check output
        captured = capsys.readouterr()
        assert captured.out, "Output should exist"
        assert "validation" in captured.out.lower(), "Output should mention validation"
        assert "status" in captured.out.lower(), "Output should show status"

    def test_validate_web_ui_with_minor_issues_warning(self, web_ui_with_minor_issues, capsys):
        """Test validating Web UI with minor issues returns warning."""
        # Prepare CLI arguments
        sys.argv = [
            "ironclad-ui",
            "validate",
            "--ui-dir", str(web_ui_with_minor_issues),
            "--ui-type", "web"
        ]
        
        # Invoke CLI and capture exit
        with pytest.raises(SystemExit) as exc_info:
            ui_cli_main()
        
        # Assertions - warning should exit with code 2
        assert exc_info.value.code in [1, 2], f"Exit code should indicate warning or failure, got {exc_info.value.code}"
        
        # Check output exists
        captured = capsys.readouterr()
        assert captured.out, "Output should not be empty"

    def test_validate_invalid_directory_fails(self, tmp_path, capsys):
        """Test validating non-existent directory fails."""
        non_existent_dir = tmp_path / "does_not_exist"
        
        # Prepare CLI arguments
        sys.argv = [
            "ironclad-ui",
            "validate",
            "--ui-dir", str(non_existent_dir),
            "--ui-type", "web"
        ]
        
        # Invoke CLI and capture exit
        with pytest.raises(SystemExit) as exc_info:
            ui_cli_main()
        
        # Assertions
        assert exc_info.value.code != 0, "Exit code should indicate failure"
        
        # Check error output
        captured = capsys.readouterr()
        assert captured.out, "Error output should exist"

    def test_invalid_cli_arguments_exits_cleanly(self, capsys):
        """Test invalid CLI arguments exits cleanly with error."""
        # Prepare invalid CLI arguments (missing required args)
        sys.argv = ["ironclad-ui", "validate"]
        
        # Invoke CLI and capture exit
        with pytest.raises(SystemExit) as exc_info:
            ui_cli_main()
        
        # Assertions
        assert exc_info.value.code != 0, "Exit code should indicate error"
        
        # Check error output (can be in stdout or stderr)
        captured = capsys.readouterr()
        assert captured.out or captured.err, "Help/error output should exist"

    def test_help_command_displays_help(self, capsys):
        """Test help command displays help text."""
        # Prepare CLI arguments for help
        sys.argv = ["ironclad-ui", "--help"]
        
        # Invoke CLI and capture exit
        with pytest.raises(SystemExit) as exc_info:
            ui_cli_main()
        
        # Help command exits with 0
        assert exc_info.value.code == 0, "Help command should exit with 0"
        
        # Check help output
        captured = capsys.readouterr()
        assert captured.out, "Help text should be displayed"
        assert len(captured.out) > 50, "Help text should have substantial content"

    def test_validate_command_with_invalid_ui_type(self, tmp_path, capsys):
        """Test validate command with invalid UI type exits cleanly."""
        # Create a temporary directory
        web_dir = tmp_path / "test_ui"
        web_dir.mkdir()
        
        # Prepare CLI arguments with invalid UI type
        sys.argv = [
            "ironclad-ui",
            "validate",
            "--ui-dir", str(web_dir),
            "--ui-type", "invalid_type"
        ]
        
        # Invoke CLI and capture exit
        with pytest.raises(SystemExit) as exc_info:
            ui_cli_main()
        
        # Assertions
        assert exc_info.value.code != 0, "Exit code should indicate error"
        
        # Check error output (can be in stdout or stderr)
        captured = capsys.readouterr()
        assert captured.out or captured.err, "Error output should exist"
        # Check both stdout and stderr for error message
        output_text = (captured.out or "") + (captured.err or "")
        assert "invalid" in output_text.lower(), "Error should mention invalid type"

    def test_generate_command_creates_ui_files(self, tmp_path):
        """Test generate command creates UI files via CLI."""
        # Create a sample module spec file
        module_spec = {
            "module_name": "test_cli_module",
            "main_logic_description": "Test module for CLI",
            "functions": [
                {
                    "name": "process",
                    "signature": "def process(data: str) -> str:",
                    "description": "Process data"
                }
            ]
        }
        
        spec_file = tmp_path / "module_spec.json"
        with open(spec_file, 'w') as f:
            json.dump(module_spec, f)
        
        output_dir = tmp_path / "cli_generated_ui"
        
        # Prepare CLI arguments
        sys.argv = [
            "ironclad-ui",
            "generate",
            "--spec", str(spec_file),
            "--type", "web",
            "--output", str(output_dir)
        ]
        
        # Invoke CLI (may not raise SystemExit on success)
        try:
            ui_cli_main()
        except SystemExit as exc_info:
            # If SystemExit is raised, check exit code
            assert exc_info.code == 0, "Generate command should succeed"
        
        # Assertions - files should be created regardless of exit behavior
        
        # Check files were created
        assert output_dir.exists(), "Output directory should be created"
        assert (output_dir / "index.html").exists(), "index.html should be created"
        assert (output_dir / "styles.css").exists(), "styles.css should be created"

    def test_no_command_displays_help(self, capsys):
        """Test no command displays help."""
        # Prepare CLI arguments without command
        sys.argv = ["ironclad-ui"]
        
        # Invoke CLI and capture exit
        with pytest.raises(SystemExit) as exc_info:
            ui_cli_main()
        
        # Assertions
        assert exc_info.value.code != 0, "No command should exit with error"
        
        # Check help output
        captured = capsys.readouterr()
        assert captured.out, "Help text should be displayed"
        assert "usage" in captured.out.lower() or "help" in captured.out.lower(), \
            "Output should contain usage or help"

    def test_subprocess_validate_valid_ui_smoke_test(self, valid_web_ui_dir):
        """Smoke test: validate valid Web UI via subprocess."""
        # Run CLI validation via subprocess
        result = subprocess.run(
            [sys.executable, "-m", "ironclad_ai_guardrails.ui_cli",
             "validate", "--ui-dir", str(valid_web_ui_dir), "--ui-type", "web"],
            capture_output=True,
            text=True,
            cwd=str(src_dir.parent)
        )
        
        # Assertions - success (0) or warning (2) are both acceptable
        assert result.returncode in [0, 2], \
            f"Exit code should be 0 or 2, got {result.returncode}"
        assert result.stdout, "Output should exist"
        assert "validation" in result.stdout.lower(), "Output should mention validation"
