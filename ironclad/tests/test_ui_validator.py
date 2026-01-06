#!/usr/bin/env python3
"""
Test suite for UI Validator module
Tests the validation framework for generated UI artifacts
"""

import pytest
import json
import tempfile
import os
from typing import Dict, Any
import sys

from ironclad_ai_guardrails.ui_validator import (
    UIValidator, ValidationStatus, ValidationLevel, ValidationIssue, ValidationResult,
    validate_ui_directory, print_validation_report
)


class TestValidationIssue:
    """Test ValidationIssue dataclass"""
    
    def test_validation_issue_creation(self):
        """Test creating a validation issue"""
        issue = ValidationIssue(
            level=ValidationLevel.ERROR,
            message="Test error message",
            file_path="/test/file.html",
            line_number=10,
            suggestion="Fix this issue"
        )
        
        assert issue.level == ValidationLevel.ERROR
        assert issue.message == "Test error message"
        assert issue.file_path == "/test/file.html"
        assert issue.line_number == 10
        assert issue.suggestion == "Fix this issue"
    
    def test_validation_issue_minimal(self):
        """Test creating a minimal validation issue"""
        issue = ValidationIssue(
            level=ValidationLevel.WARNING,
            message="Test warning"
        )
        
        assert issue.level == ValidationLevel.WARNING
        assert issue.message == "Test warning"
        assert issue.file_path is None
        assert issue.line_number is None
        assert issue.suggestion is None


class TestValidationResult:
    """Test ValidationResult dataclass"""
    
    def test_validation_result_creation(self):
        """Test creating a validation result"""
        issues = [
            ValidationIssue(ValidationLevel.ERROR, "Error 1"),
            ValidationIssue(ValidationLevel.WARNING, "Warning 1")
        ]
        
        result = ValidationResult(
            status=ValidationStatus.WARNING,
            issues=issues,
            execution_time=1.5,
            metadata={"total_files": 5}
        )
        
        assert result.status == ValidationStatus.WARNING
        assert len(result.issues) == 2
        assert result.execution_time == 1.5
        assert result.metadata["total_files"] == 5


class TestUIValidator:
    """Test UIValidator class functionality"""
    
    def create_temp_ui_dir(self, ui_type: str = "web", files: Dict[str, str] = None) -> str:
        """Create a temporary UI directory with specified files"""
        temp_dir = tempfile.mkdtemp()
        
        # Default files based on UI type
        default_files = {}
        
        if ui_type == "web":
            default_files = {
                "index.html": """<!DOCTYPE html>
<html>
<head>
    <title>Test UI</title>
</head>
<body>
    <form id="mainForm">
        <input type="text" name="test" id="test" required>
        <button type="submit">Submit</button>
    </form>
    <script src="app.js"></script>
</body>
</html>""",
                "styles.css": """body {
    font-family: Arial, sans-serif;
    margin: 20px;
}
.form-control {
    width: 100%;
    padding: 8px;
    border: 1px solid #ccc;
}""",
                "app.js": """document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('mainForm');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        console.log('Form submitted');
    });
});""",
                "package.json": json.dumps({
                    "name": "test-ui",
                    "version": "1.0.0",
                    "scripts": {
                        "start": "python -m http.server 8000"
                    }
                })
            }
        elif ui_type == "cli_gui":
            default_files = {
                "gui.py": """#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk

class TestGUI:
    def __init__(self, master=None):
        self.master = master
        self.master.title("Test GUI")
        self.create_widgets()
    
    def create_widgets(self):
        frame = ttk.Frame(self.master, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(frame, text="Test:").grid(row=0, column=0)
        self.test_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.test_var).grid(row=0, column=1)

if __name__ == "__main__":
    root = tk.Tk()
    app = TestGUI(root)
    root.mainloop()""",
                "requirements.txt": "tkinter\n"
            }
        
        # Use provided files or defaults
        files_to_create = files or default_files
        
        for filename, content in files_to_create.items():
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, 'w') as f:
                f.write(content)
        
        return temp_dir
    
    def test_validator_creation(self):
        """Test creating a UI validator"""
        temp_dir = self.create_temp_ui_dir()
        
        try:
            validator = UIValidator(temp_dir, "web")
            assert validator.ui_dir.name == os.path.basename(temp_dir)
            assert validator.ui_type == "web"
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_validator_nonexistent_directory(self):
        """Test validator with nonexistent directory"""
        with pytest.raises(ValueError) as exc_info:
            UIValidator("/nonexistent/directory", "web")
        
        assert "UI directory does not exist" in str(exc_info.value)
    
    def test_validate_web_ui_success(self):
        """Test successful web UI validation"""
        temp_dir = self.create_temp_ui_dir("web")
        
        try:
            validator = UIValidator(temp_dir, "web")
            result = validator.validate_all()
            
            assert result.status == ValidationStatus.WARNING
            assert result.execution_time > 0
            assert "ui_type" in result.metadata
            assert result.metadata["ui_type"] == "web"
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_validate_web_ui_missing_files(self):
        """Test web UI validation with missing files"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create empty directory
            validator = UIValidator(temp_dir, "web")
            result = validator.validate_all()
            
            assert result.status == ValidationStatus.FAILED
            
            # Should have critical issues for missing files
            critical_issues = [i for i in result.issues if i.level == ValidationLevel.CRITICAL]
            assert len(critical_issues) >= 3  # index.html, styles.css, app.js
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_validate_cli_gui_success(self):
        """Test successful CLI GUI validation"""
        temp_dir = self.create_temp_ui_dir("cli_gui")
        
        try:
            validator = UIValidator(temp_dir, "cli_gui")
            result = validator.validate_all()
            
            assert result.status == ValidationStatus.WARNING
            assert result.execution_time > 0
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_validate_desktop_ui_missing_main(self):
        """Test desktop UI validation with missing main.js"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create only package.json
            package_data = {
                "name": "test-desktop",
                "version": "1.0.0",
                "main": "main.js"
            }
            
            with open(os.path.join(temp_dir, "package.json"), 'w') as f:
                json.dump(package_data, f)
            
            validator = UIValidator(temp_dir, "desktop")
            result = validator.validate_all()
            
            assert result.status == ValidationStatus.FAILED
            
            # Should have critical issue for missing main.js
            main_issue = next(
                (i for i in result.issues if "main.js" in str(i.file_path)),
                None
            )
            assert main_issue is not None
            assert main_issue.level == ValidationLevel.CRITICAL
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_validate_api_docs_success(self):
        """Test successful API docs validation"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create API docs files
            openapi_data = {
                "openapi": "3.0.0",
                "info": {"title": "Test API", "version": "1.0.0"},
                "paths": {
                    "/test": {
                        "get": {
                            "summary": "Test endpoint",
                            "responses": {"200": {"description": "Success"}}
                        }
                    }
                }
            }
            
            swagger_html = """<!DOCTYPE html>
<html>
<head>
    <title>API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui.css">
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-bundle.js"></script>
    <script>
        SwaggerUIBundle({
            url: './openapi.json',
            dom_id: '#swagger-ui'
        });
    </script>
</body>
</html>"""
            
            with open(os.path.join(temp_dir, "openapi.json"), 'w') as f:
                json.dump(openapi_data, f)
            
            with open(os.path.join(temp_dir, "swagger.html"), 'w') as f:
                f.write(swagger_html)
            
            validator = UIValidator(temp_dir, "api_docs")
            result = validator.validate_all()
            
            assert result.status == ValidationStatus.PASSED
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_validate_broken_html(self):
        """Test validation with broken HTML"""
        temp_dir = self.create_temp_ui_dir("web", {
            "index.html": """<html>
<head><title>Broken</title></head>
<body>
<!-- Missing DOCTYPE and proper structure -->
<form>
<input name="test">
</form>
""",
            "styles.css": "body { color: red; }",
            "app.js": "// No validation functions"
        })
        
        try:
            validator = UIValidator(temp_dir, "web")
            result = validator.validate_all()
            
            # Should have errors for missing DOCTYPE and other structure issues
            error_issues = [i for i in result.issues if i.level == ValidationLevel.ERROR]
            assert len(error_issues) >= 2  # DOCTYPE and other structure issues
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_validate_invalid_json(self):
        """Test validation with invalid JSON files"""
        temp_dir = self.create_temp_ui_dir("web", {
            "index.html": "<!DOCTYPE html><html><head><title>Test</title></head></html>",
            "styles.css": "body { margin: 0; }",
            "app.js": "console.log('test');",
            "package.json": "{ invalid json content"
        })
        
        try:
            validator = UIValidator(temp_dir, "web")
            result = validator.validate_all()
            
            # Should have critical issue for invalid JSON
            critical_issues = [i for i in result.issues if i.level == ValidationLevel.CRITICAL]
            assert any("Invalid JSON" in issue.message for issue in critical_issues)
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_validate_missing_css_properties(self):
        """Test validation with minimal CSS"""
        temp_dir = self.create_temp_ui_dir("web", {
            "index.html": """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
<form><input name="test"></form>
</body>
</html>""",
            "styles.css": ".minimal { color: blue; }",
            "app.js": "console.log('test');",
            "package.json": json.dumps({"name": "test", "version": "1.0.0"})
        })
        
        try:
            validator = UIValidator(temp_dir, "web")
            result = validator.validate_all()
            
            # Should have info level issues for missing CSS properties
            info_issues = [i for i in result.issues if i.level == ValidationLevel.INFO]
            assert any("missing common CSS properties" in issue.message for issue in info_issues)
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_validate_python_no_main_block(self):
        """Test Python validation without main block"""
        temp_dir = self.create_temp_ui_dir("cli_gui", {
            "gui.py": """import tkinter as tk

class TestGUI:
    def __init__(self):
        pass

# No if __name__ == '__main__' block
""",
            "requirements.txt": "tkinter"
        })
        
        try:
            validator = UIValidator(temp_dir, "cli_gui")
            result = validator.validate_all()
            
            # Should have warning for missing main block
            warning_issues = [i for i in result.issues if i.level == ValidationLevel.WARNING]
            assert any("Missing main execution block" in issue.message for issue in warning_issues)
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_validate_security_sensitive_data(self):
        """Test security validation with sensitive data"""
        temp_dir = self.create_temp_ui_dir("web", {
            "index.html": """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
<script>
    const apiKey = 'sk-1234567890abcdef';
    const password = 'secret123';
</script>
</body>
</html>""",
            "styles.css": "body { margin: 0; }",
            "app.js": "// JavaScript",
            "package.json": json.dumps({"name": "test", "version": "1.0.0"})
        })
        
        try:
            validator = UIValidator(temp_dir, "web")
            result = validator.validate_all()
            
            # Should have critical issues for sensitive data
            critical_issues = [i for i in result.issues if i.level == ValidationLevel.CRITICAL]
            sensitive_issues = [i for i in critical_issues if "Sensitive data found" in i.message]
            assert len(sensitive_issues) >= 2  # API key and password
        finally:
            import shutil
            shutil.rmtree(temp_dir)


class TestConvenienceFunctions:
    """Test convenience functions"""
    
    def test_validate_ui_directory_function(self):
        """Test validate_ui_directory convenience function"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create minimal web UI
            with open(os.path.join(temp_dir, "index.html"), 'w') as f:
                f.write("<!DOCTYPE html><html><head><title>Test</title></head><body></body></html>")
            
            with open(os.path.join(temp_dir, "styles.css"), 'w') as f:
                f.write("body { margin: 0; }")
            
            with open(os.path.join(temp_dir, "app.js"), 'w') as f:
                f.write("console.log('test');")
            
            result = validate_ui_directory(temp_dir, "web")
            
            assert isinstance(result, ValidationResult)
            assert result.status == ValidationStatus.FAILED
            assert "total_issues" in result.metadata
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_print_validation_report_function(self, capsys):
        """Test print_validation_report function"""
        issues = [
            ValidationIssue(ValidationLevel.ERROR, "Test error", "/test/file.html"),
            ValidationIssue(ValidationLevel.WARNING, "Test warning", suggestion="Fix it")
        ]
        
        result = ValidationResult(
            status=ValidationStatus.WARNING,
            issues=issues,
            execution_time=0.5,
            metadata={"total_issues": 2, "error_issues": 1, "warning_issues": 1}
        )
        
        print_validation_report(result)
        captured = capsys.readouterr()
        
        assert "UI VALIDATION REPORT" in captured.out
        assert "WARNING" in captured.out
        assert "Total Issues: 2" in captured.out
        assert "Test error" in captured.out
        assert "Test warning" in captured.out


class TestEdgeCases(TestUIValidator):
    """Test edge cases and error conditions"""
    
    def test_validate_empty_directory(self):
        """Test validation of completely empty directory"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            validator = UIValidator(temp_dir, "web")
            result = validator.validate_all()
            
            assert result.status == ValidationStatus.FAILED
            assert len(result.issues) >= 3  # Missing required files
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_validate_unknown_ui_type(self):
        """Test validation with unknown UI type (should still run common validations)"""
        temp_dir = self.create_temp_ui_dir("web")
        
        try:
            validator = UIValidator(temp_dir, "unknown_type")
            result = validator.validate_all()
            
            # Should still run common validations
            assert result.execution_time > 0
            assert "ui_type" in result.metadata
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_validate_file_reading_errors(self):
        """Test handling of file reading errors"""
        temp_dir = self.create_temp_ui_dir("web")
        
        try:
            # Make a file unreadable by removing it after validator creation
            html_path = os.path.join(temp_dir, "index.html")
            
            validator = UIValidator(temp_dir, "web")
            os.remove(html_path)
            
            result = validator.validate_all()
            
            # Should handle missing file gracefully
            assert result.status == ValidationStatus.FAILED
            missing_file_issues = [i for i in result.issues if "Missing" in i.message]
            assert len(missing_file_issues) > 0
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_validate_malformed_requirements(self):
        """Test validation of malformed requirements.txt"""
        temp_dir = self.create_temp_ui_dir("cli_gui", {
            "gui.py": "#!/usr/bin/env python3\nprint('test')",
            "requirements.txt": "package_without_version\nanother_package"
        })
        
        try:
            validator = UIValidator(temp_dir, "cli_gui")
            result = validator.validate_all()
            
            # Should have info issues about missing version specifications
            info_issues = [i for i in result.issues if i.level == ValidationLevel.INFO]
            version_issues = [i for i in info_issues if "No version specification" in i.message]
            assert len(version_issues) >= 2
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_web_ui_css_read_error(self):
        """Test Web UI validation with CSS file read error (lines 424-425)"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create valid HTML, JS, and package.json
            with open(os.path.join(temp_dir, "index.html"), 'w') as f:
                f.write("<!DOCTYPE html><html><head></head><body></body></html>")
            
            with open(os.path.join(temp_dir, "app.js"), 'w') as f:
                f.write("console.log('test');")
            
            with open(os.path.join(temp_dir, "package.json"), 'w') as f:
                json.dump({"name": "test", "version": "1.0.0"}, f)
            
            # Create CSS file with restrictive permissions
            css_path = os.path.join(temp_dir, "styles.css")
            with open(css_path, 'w') as f:
                f.write("body { margin: 0; }")
            
            # Make CSS file unreadable by removing read permission
            os.chmod(css_path, 0o000)
            
            validator = UIValidator(temp_dir, "web")
            result = validator.validate_all()
            
            # Should have error for CSS read error
            css_errors = [i for i in result.issues if "Error reading CSS file" in i.message]
            assert len(css_errors) > 0
            
        finally:
            import shutil
            # Restore permissions before cleanup
            os.chmod(css_path, 0o644)
            shutil.rmtree(temp_dir)
    
    def test_web_ui_js_read_error(self):
        """Test Web UI validation with JS file read error (lines 472-473)"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create valid HTML, CSS, and package.json
            with open(os.path.join(temp_dir, "index.html"), 'w') as f:
                f.write("<!DOCTYPE html><html><head></head><body></body></html>")
            
            with open(os.path.join(temp_dir, "styles.css"), 'w') as f:
                f.write("body { margin: 0; }")
            
            with open(os.path.join(temp_dir, "package.json"), 'w') as f:
                json.dump({"name": "test", "version": "1.0.0"}, f)
            
            # Create JS file with restrictive permissions
            js_path = os.path.join(temp_dir, "app.js")
            with open(js_path, 'w') as f:
                f.write("console.log('test');")
            
            # Make JS file unreadable
            os.chmod(js_path, 0o000)
            
            validator = UIValidator(temp_dir, "web")
            result = validator.validate_all()
            
            # Should have error for JS read error
            js_errors = [i for i in result.issues if "Error reading JavaScript file" in i.message]
            assert len(js_errors) > 0
            
        finally:
            import shutil
            # Restore permissions before cleanup
            os.chmod(js_path, 0o644)
            shutil.rmtree(temp_dir)
    
    def test_web_ui_package_json_decode_error(self):
        """Test Web UI validation with package.json JSON decode error (lines 570-575)"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create valid HTML, CSS, and JS
            with open(os.path.join(temp_dir, "index.html"), 'w') as f:
                f.write("<!DOCTYPE html><html><head></head><body></body></html>")
            
            with open(os.path.join(temp_dir, "styles.css"), 'w') as f:
                f.write("body { margin: 0; }")
            
            with open(os.path.join(temp_dir, "app.js"), 'w') as f:
                f.write("console.log('test');")
            
            # Create package.json with invalid JSON
            with open(os.path.join(temp_dir, "package.json"), 'w') as f:
                f.write("{invalid json content")
            
            validator = UIValidator(temp_dir, "web")
            result = validator.validate_all()
            
            # Should have critical issue for invalid JSON
            critical_issues = [i for i in result.issues if i.level == ValidationLevel.CRITICAL]
            assert len(critical_issues) > 0
            assert any("Invalid JSON in package.json" in i.message for i in critical_issues)
            
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_web_ui_package_json_missing_scripts(self):
        """Test Web UI validation with package.json missing scripts (lines 552-559)"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create valid HTML, CSS, and JS
            with open(os.path.join(temp_dir, "index.html"), 'w') as f:
                f.write("<!DOCTYPE html><html><head></head><body></body></html>")
            
            with open(os.path.join(temp_dir, "styles.css"), 'w') as f:
                f.write("body { margin: 0; }")
            
            with open(os.path.join(temp_dir, "app.js"), 'w') as f:
                f.write("console.log('test');")
            
            # Create package.json without scripts or with empty scripts
            with open(os.path.join(temp_dir, "package.json"), 'w') as f:
                json.dump({"name": "test", "version": "1.0.0", "scripts": {}}, f)
            
            validator = UIValidator(temp_dir, "web")
            result = validator.validate_all()
            
            # Should have warning for missing scripts
            warning_issues = [i for i in result.issues if i.level == ValidationLevel.WARNING]
            assert len(warning_issues) > 0
            assert any("No scripts defined" in i.message for i in warning_issues)
            
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_web_ui_package_json_missing_dependencies(self):
        """Test Web UI validation with package.json missing dependencies (lines 561-568)"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create valid HTML, CSS, and JS
            with open(os.path.join(temp_dir, "index.html"), 'w') as f:
                f.write("<!DOCTYPE html><html><head></head><body></body></html>")
            
            with open(os.path.join(temp_dir, "styles.css"), 'w') as f:
                f.write("body { margin: 0; }")
            
            with open(os.path.join(temp_dir, "app.js"), 'w') as f:
                f.write("console.log('test');")
            
            # Create package.json without dependencies
            with open(os.path.join(temp_dir, "package.json"), 'w') as f:
                json.dump({"name": "test", "version": "1.0.0"}, f)
            
            validator = UIValidator(temp_dir, "web")
            result = validator.validate_all()
            
            # Should have info for missing dependencies
            info_issues = [i for i in result.issues if i.level == ValidationLevel.INFO]
            assert len(info_issues) > 0
            assert any("No dependencies defined" in i.message for i in info_issues)
            
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_web_ui_package_json_empty(self):
        """Test Web UI validation with empty package.json (line 545)"""
        temp_dir = self.create_temp_ui_dir("web")
        
        try:
            # Create valid HTML, CSS, and JS
            with open(os.path.join(temp_dir, "index.html"), 'w') as f:
                f.write("<!DOCTYPE html><html><head></head><body></body></html>")
            
            with open(os.path.join(temp_dir, "styles.css"), 'w') as f:
                f.write("body { margin: 0; }")
            
            with open(os.path.join(temp_dir, "app.js"), 'w') as f:
                f.write("console.log('test');")
            
            # Create package.json that's empty but valid
            with open(os.path.join(temp_dir, "package.json"), 'w') as f:
                json.dump({}, f)
            
            validator = UIValidator(temp_dir, "web")
            result = validator.validate_all()
            
            # Should have warning for missing required fields
            warning_issues = [i for i in result.issues if i.level == ValidationLevel.WARNING]
            assert len(warning_issues) >= 1
            
        finally:
            import shutil
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])