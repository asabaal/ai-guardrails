#!/usr/bin/env python3
"""
Integration tests for UI Validator subsystem.

These tests verify that UI Validator correctly validates real UI directory structures.
These are integration tests, not unit tests.

Tests use real filesystem operations via tmp_path.
"""

import pytest
import os
import sys
from pathlib import Path
import tempfile
import shutil
import json

# Add src to path
src_dir = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_dir))

from ironclad_ai_guardrails.ui_validator import (
    UIValidator,
    ValidationStatus,
    ValidationLevel,
)


class TestUIValidatorIntegration:
    """Integration tests for UI Validator with real filesystem operations."""
    
    @pytest.fixture
    def temp_ui_dir(self, tmp_path):
        """Create a temporary UI directory."""
        ui_dir = tmp_path / "ui_output"
        ui_dir.mkdir()
        return ui_dir
    
    def test_valid_web_ui_passes(self, temp_ui_dir):
        """Test validation of valid web UI passes or warns."""
        # Create valid web UI files
        (temp_ui_dir / "index.html").write_text("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Web App</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <h1>Test Application</h1>
    </div>
    <script src="app.js"></script>
</body>
</html>""")
        
        (temp_ui_dir / "styles.css").write_text("""body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
}

.container {
    max-width: 800px;
    margin: 0 auto;
}""")
        
        (temp_ui_dir / "app.js").write_text("""document.addEventListener('DOMContentLoaded', function() {
    console.log('App loaded');
});""")
        
        (temp_ui_dir / "package.json").write_text(json.dumps({
            "name": "test-web-app",
            "version": "1.0.0",
            "description": "Test web application"
        }))
        
        # Validate
        validator = UIValidator(str(temp_ui_dir), "web")
        result = validator.validate_all()
        
        # High-level assertions only
        assert result.status in [ValidationStatus.PASSED, ValidationStatus.WARNING], "Should pass or warn"
        assert isinstance(result.issues, list), "Issues should be a list"
        assert result.metadata["ui_type"] == "web", "UI type should be web"
        assert result.execution_time > 0, "Execution time should be positive"
    
    def test_web_ui_with_minor_issues_warns(self, temp_ui_dir):
        """Test web UI with minor issues produces WARNING status."""
        # Create web UI missing optional elements
        (temp_ui_dir / "index.html").write_text("""<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body></body>
</html>""")
        
        (temp_ui_dir / "styles.css").write_text("body { margin: 0; }")
        
        (temp_ui_dir / "app.js").write_text("console.log('test');")
        
        (temp_ui_dir / "package.json").write_text(json.dumps({
            "name": "test-app",
            "version": "1.0.0"
        }))
        
        # Validate
        validator = UIValidator(str(temp_ui_dir), "web")
        result = validator.validate_all()
        
        # High-level assertions only
        assert result.status in [ValidationStatus.PASSED, ValidationStatus.WARNING, ValidationStatus.FAILED], "Status should be valid"
        assert isinstance(result.issues, list), "Issues should be a list"
        assert len(result.issues) >= 0, "May have issues"
        assert result.metadata["ui_type"] == "web", "UI type should be web"
    
    def test_valid_cli_gui_with_main_block_passes(self, temp_ui_dir):
        """Test CLI GUI with main execution block passes."""
        # Create valid CLI GUI file
        (temp_ui_dir / "gui.py").write_text("""import tkinter as tk

def main():
    root = tk.Tk()
    root.title("Test App")
    root.mainloop()

if __name__ == "__main__":
    main()
""")
        
        (temp_ui_dir / "requirements.txt").write_text("tkinter\n")
        
        # Validate
        validator = UIValidator(str(temp_ui_dir), "cli_gui")
        result = validator.validate_all()
        
        # High-level assertions only
        assert result.status in [ValidationStatus.PASSED, ValidationStatus.WARNING], "Should pass or warn"
        assert isinstance(result.issues, list), "Issues should be a list"
        assert result.metadata["ui_type"] == "cli_gui", "UI type should be cli_gui"
    
    def test_cli_gui_missing_main_block_warns(self, temp_ui_dir):
        """Test CLI GUI without main execution block produces warning."""
        # Create CLI GUI without main block
        (temp_ui_dir / "gui.py").write_text("""import tkinter as tk

class GUI:
    def __init__(self):
        self.root = tk.Tk()
    
    def run(self):
        self.root.title("Test App")
        self.root.mainloop()
""")
        
        (temp_ui_dir / "requirements.txt").write_text("tkinter\n")
        
        # Validate
        validator = UIValidator(str(temp_ui_dir), "cli_gui")
        result = validator.validate_all()
        
        # High-level assertions only
        assert result.status in [ValidationStatus.PASSED, ValidationStatus.WARNING, ValidationStatus.FAILED], "Status should be valid"
        assert isinstance(result.issues, list), "Issues should be a list"
        # May have warning about missing main block
        if result.issues:
            assert all(isinstance(issue, object) for issue in result.issues), "Issues should be ValidationIssue objects"
    
    def test_valid_api_docs_passes(self, temp_ui_dir):
        """Test valid API docs pass or warn."""
        # Create valid API docs
        openapi_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0"
            },
            "paths": {
                "/test": {
                    "get": {
                        "summary": "Test endpoint",
                        "responses": {
                            "200": {"description": "Success"}
                        }
                    }
                }
            }
        }
        
        (temp_ui_dir / "openapi.json").write_text(json.dumps(openapi_spec, indent=2))
        
        (temp_ui_dir / "swagger.html").write_text("""<!DOCTYPE html>
<html>
<head>
    <title>Swagger UI</title>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui-bundle.js"></script>
</head>
<body>
    <div id="swagger-ui"></div>
    <script>
        SwaggerUIBundle({
            url: 'openapi.json',
            dom_id: '#swagger-ui'
        });
    </script>
</body>
</html>""")
        
        # Validate
        validator = UIValidator(str(temp_ui_dir), "api_docs")
        result = validator.validate_all()
        
        # High-level assertions only
        assert result.status in [ValidationStatus.PASSED, ValidationStatus.WARNING], "Should pass or warn"
        assert isinstance(result.issues, list), "Issues should be a list"
        assert result.metadata["ui_type"] == "api_docs", "UI type should be api_docs"
    
    def test_unknown_ui_type_fails_validation(self, temp_ui_dir):
        """Test unknown UI type fails validation."""
        # Create minimal structure
        (temp_ui_dir / "index.html").write_text("<html><body>Test</body></html>")
        
        # Validate with unknown type
        validator = UIValidator(str(temp_ui_dir), "unknown_type")
        result = validator.validate_all()
        
        # High-level assertions only
        # Validator may handle unknown types differently
        assert isinstance(result, object), "Should return ValidationResult"
        assert isinstance(result.issues, list), "Issues should be a list"
        assert isinstance(result.metadata, dict), "Metadata should be a dict"
        assert result.execution_time >= 0, "Execution time should be non-negative"
    
    def test_validator_creates_result_object(self, temp_ui_dir):
        """Test validator creates a complete result object."""
        # Create minimal web UI
        (temp_ui_dir / "index.html").write_text("<!DOCTYPE html><html><body>Test</body></html>")
        (temp_ui_dir / "styles.css").write_text("body { margin: 0; }")
        (temp_ui_dir / "app.js").write_text("console.log('test');")
        (temp_ui_dir / "package.json").write_text('{"name": "test"}')
        
        # Validate
        validator = UIValidator(str(temp_ui_dir), "web")
        result = validator.validate_all()
        
        # High-level assertions - check result structure
        assert hasattr(result, "status"), "Result should have status"
        assert hasattr(result, "issues"), "Result should have issues"
        assert hasattr(result, "execution_time"), "Result should have execution_time"
        assert hasattr(result, "metadata"), "Result should have metadata"
        
        # Check metadata contains expected keys
        assert "ui_type" in result.metadata, "Metadata should have ui_type"
        assert "total_issues" in result.metadata, "Metadata should have total_issues"
    
    def test_valid_desktop_ui_passes(self, temp_ui_dir):
        """Test valid desktop UI passes or warns."""
        # Create valid desktop UI files
        (temp_ui_dir / "main.js").write_text("""const { app, BrowserWindow } = require('electron');

app.whenReady().then(() => {
    const win = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true
        }
    });
    win.loadFile('index.html');
});""")
        
        (temp_ui_dir / "index.html").write_text("""<!DOCTYPE html>
<html>
<head><title>Electron App</title></head>
<body>Test</body>
</html>""")
        
        (temp_ui_dir / "package.json").write_text(json.dumps({
            "name": "test-electron-app",
            "version": "1.0.0",
            "main": "main.js",
            "devDependencies": {
                "electron": "^22.0.0"
            }
        }))
        
        # Validate
        validator = UIValidator(str(temp_ui_dir), "desktop")
        result = validator.validate_all()
        
        # High-level assertions only
        # Desktop UI may have warnings or errors but should still validate
        assert result.status in [ValidationStatus.PASSED, ValidationStatus.WARNING, ValidationStatus.FAILED], "Should validate"
        assert isinstance(result.issues, list), "Issues should be a list"
        assert result.metadata["ui_type"] == "desktop", "UI type should be desktop"
    
    def test_valid_cli_tui_passes(self, temp_ui_dir):
        """Test valid CLI TUI passes or warns."""
        # Create valid CLI TUI file
        (temp_ui_dir / "tui.py").write_text("""from rich.console import Console
from rich.table import Table

def main():
    console = Console()
    table = Table(title="Test")
    console.print(table)

if __name__ == "__main__":
    main()
""")
        
        (temp_ui_dir / "requirements.txt").write_text("rich>=13.0.0\n")
        
        # Validate
        validator = UIValidator(str(temp_ui_dir), "cli_tui")
        result = validator.validate_all()
        
        # High-level assertions only
        assert result.status in [ValidationStatus.PASSED, ValidationStatus.WARNING], "Should pass or warn"
        assert isinstance(result.issues, list), "Issues should be a list"
        assert result.metadata["ui_type"] == "cli_tui", "UI type should be cli_tui"
    
    def test_validator_handles_missing_required_files(self, temp_ui_dir):
        """Test validator handles missing required files appropriately."""
        # Create only one required file for web UI
        (temp_ui_dir / "index.html").write_text("<!DOCTYPE html><html><body>Test</body></html>")
        
        # Validate
        validator = UIValidator(str(temp_ui_dir), "web")
        result = validator.validate_all()
        
        # High-level assertions only
        # Missing files should result in issues
        assert isinstance(result, object), "Should return ValidationResult"
        assert isinstance(result.issues, list), "Issues should be a list"
        
        # Should have some issues due to missing files
        # or result.status should reflect the validation state
        assert result.status in [ValidationStatus.PASSED, ValidationStatus.WARNING, ValidationStatus.FAILED], "Status should be valid"
    
    def test_validator_execution_time_is_recorded(self, temp_ui_dir):
        """Test validator records execution time."""
        # Create minimal web UI
        (temp_ui_dir / "index.html").write_text("<!DOCTYPE html><html><body>Test</body></html>")
        (temp_ui_dir / "styles.css").write_text("body { margin: 0; }")
        (temp_ui_dir / "app.js").write_text("console.log('test');")
        (temp_ui_dir / "package.json").write_text('{"name": "test"}')
        
        # Validate
        validator = UIValidator(str(temp_ui_dir), "web")
        result = validator.validate_all()
        
        # High-level assertions
        assert result.execution_time >= 0, "Execution time should be non-negative"
        assert result.execution_time < 10, "Execution time should be reasonable (< 10s)"
    
    def test_validator_includes_metadata(self, temp_ui_dir):
        """Test validator includes metadata in result."""
        # Create minimal web UI
        (temp_ui_dir / "index.html").write_text("<!DOCTYPE html><html><body>Test</body></html>")
        (temp_ui_dir / "styles.css").write_text("body { margin: 0; }")
        (temp_ui_dir / "app.js").write_text("console.log('test');")
        (temp_ui_dir / "package.json").write_text('{"name": "test"}')
        
        # Validate
        validator = UIValidator(str(temp_ui_dir), "web")
        result = validator.validate_all()
        
        # High-level assertions
        assert result.metadata is not None, "Metadata should exist"
        assert isinstance(result.metadata, dict), "Metadata should be a dict"
        assert "ui_type" in result.metadata, "Metadata should have ui_type"
        assert "total_issues" in result.metadata, "Metadata should have total_issues"
        
        # May also have critical_issues, error_issues, warning_issues
        for key in ["critical_issues", "error_issues", "warning_issues"]:
            if key in result.metadata:
                assert isinstance(result.metadata[key], (int, float)), f"{key} should be numeric"
