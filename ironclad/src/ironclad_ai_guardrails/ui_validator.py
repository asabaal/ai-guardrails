#!/usr/bin/env python3
"""
UI Validator Framework

Provides comprehensive testing and validation for generated UI artifacts.
Supports smoke testing, functional validation, and cross-platform compatibility checks.
"""

import os
import json
import subprocess
import tempfile
import time
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import re
from pathlib import Path


class ValidationStatus(Enum):
    """Validation result status"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


class ValidationLevel(Enum):
    """Validation severity levels"""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Represents a validation issue found during testing"""
    level: ValidationLevel
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of UI validation"""
    status: ValidationStatus
    issues: List[ValidationIssue]
    execution_time: float
    metadata: Dict[str, Any]


class UIValidator:
    """Main UI validator class for testing generated UI artifacts"""
    
    def __init__(self, ui_dir: str, ui_type: str = "web"):
        """
        Initialize UI validator
        
        Args:
            ui_dir: Directory containing generated UI files
            ui_type: Type of UI ('web', 'cli_gui', 'desktop', 'api_docs', 'cli_tui')
        """
        self.ui_dir = Path(ui_dir)
        self.ui_type = ui_type
        self.issues = []
        
        if not self.ui_dir.exists():
            raise ValueError(f"UI directory does not exist: {ui_dir}")
    
    def validate_all(self) -> ValidationResult:
        """Run comprehensive validation suite"""
        start_time = time.time()
        
        self.issues.clear()
        
        # Run different validation checks based on UI type
        if self.ui_type == "web":
            self._validate_web_ui()
        elif self.ui_type == "cli_gui":
            self._validate_cli_gui()
        elif self.ui_type == "desktop":
            self._validate_desktop_ui()
        elif self.ui_type == "api_docs":
            self._validate_api_docs()
        elif self.ui_type == "cli_tui":
            self._validate_cli_tui()
        
        # Run common validations
        self._validate_file_structure()
        self._validate_dependencies()
        self._validate_security()
        
        execution_time = time.time() - start_time
        
        # Determine overall status
        critical_issues = [i for i in self.issues if i.level == ValidationLevel.CRITICAL]
        error_issues = [i for i in self.issues if i.level == ValidationLevel.ERROR]
        warning_issues = [i for i in self.issues if i.level == ValidationLevel.WARNING]
        
        if critical_issues or error_issues:
            status = ValidationStatus.FAILED
        elif warning_issues:
            status = ValidationStatus.WARNING
        else:
            status = ValidationStatus.PASSED
        
        return ValidationResult(
            status=status,
            issues=self.issues.copy(),
            execution_time=execution_time,
            metadata={
                "ui_type": self.ui_type,
                "total_issues": len(self.issues),
                "critical_issues": len(critical_issues),
                "error_issues": len(error_issues),
                "warning_issues": len(warning_issues)
            }
        )
    
    def _validate_web_ui(self):
        """Validate web UI files"""
        html_file = self.ui_dir / "index.html"
        css_file = self.ui_dir / "styles.css"
        js_file = self.ui_dir / "app.js"
        package_file = self.ui_dir / "package.json"
        
        # Validate HTML structure
        if html_file.exists():
            self._validate_html_file(html_file)
        else:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.CRITICAL,
                message="Missing index.html file",
                file_path=str(html_file)
            ))
        
        # Validate CSS
        if css_file.exists():
            self._validate_css_file(css_file)
        else:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message="Missing styles.css file",
                file_path=str(css_file)
            ))
        
        # Validate JavaScript
        if js_file.exists():
            self._validate_js_file(js_file)
        else:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message="Missing app.js file",
                file_path=str(js_file)
            ))
        
        # Validate package.json
        if package_file.exists():
            self._validate_package_json(package_file)
        else:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                message="Missing package.json file",
                file_path=str(package_file),
                suggestion="Add package.json for proper project management"
            ))
    
    def _validate_cli_gui(self):
        """Validate CLI GUI files"""
        gui_file = self.ui_dir / "gui.py"
        requirements_file = self.ui_dir / "requirements.txt"
        
        # Validate GUI script
        if gui_file.exists():
            self._validate_python_file(gui_file, check_tkinter=True)
        else:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.CRITICAL,
                message="Missing gui.py file",
                file_path=str(gui_file)
            ))
        
        # Validate requirements
        if requirements_file.exists():
            self._validate_requirements_file(requirements_file)
        else:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                message="Missing requirements.txt file",
                file_path=str(requirements_file)
            ))
    
    def _validate_desktop_ui(self):
        """Validate desktop UI files"""
        main_file = self.ui_dir / "main.js"
        preload_file = self.ui_dir / "preload.js"
        html_file = self.ui_dir / "index.html"
        package_file = self.ui_dir / "package.json"
        
        # Validate Electron files
        if main_file.exists():
            self._validate_electron_main(main_file)
        else:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.CRITICAL,
                message="Missing main.js file for Electron",
                file_path=str(main_file)
            ))
        
        if preload_file.exists():
            self._validate_electron_preload(preload_file)
        
        if html_file.exists():
            self._validate_html_file(html_file)
        
        if package_file.exists():
            self._validate_electron_package(package_file)
    
    def _validate_api_docs(self):
        """Validate API documentation files"""
        openapi_file = self.ui_dir / "openapi.json"
        swagger_file = self.ui_dir / "swagger.html"
        
        # Validate OpenAPI spec
        if openapi_file.exists():
            self._validate_openapi_spec(openapi_file)
        else:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.CRITICAL,
                message="Missing openapi.json file",
                file_path=str(openapi_file)
            ))
        
        # Validate Swagger HTML
        if swagger_file.exists():
            self._validate_swagger_html(swagger_file)
        
        # Test API endpoints if possible
        self._validate_api_endpoints()
    
    def _validate_cli_tui(self):
        """Validate CLI TUI files"""
        tui_file = self.ui_dir / "tui.py"
        requirements_file = self.ui_dir / "requirements.txt"
        
        # Validate TUI script
        if tui_file.exists():
            self._validate_python_file(tui_file, check_rich=True)
        else:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.CRITICAL,
                message="Missing tui.py file",
                file_path=str(tui_file)
            ))
        
        # Validate requirements
        if requirements_file.exists():
            self._validate_requirements_file(requirements_file)
        else:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                message="Missing requirements.txt file",
                file_path=str(requirements_file)
            ))
    
    def _validate_file_structure(self):
        """Validate basic file structure"""
        required_files = []
        
        if self.ui_type == "web":
            required_files = ["index.html", "styles.css", "app.js"]
        elif self.ui_type == "cli_gui":
            required_files = ["gui.py"]
        elif self.ui_type == "desktop":
            required_files = ["main.js", "package.json"]
        elif self.ui_type == "api_docs":
            required_files = ["openapi.json"]
        elif self.ui_type == "cli_tui":
            required_files = ["tui.py"]
        
        for filename in required_files:
            file_path = self.ui_dir / filename
            if not file_path.exists():
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.CRITICAL,
                    message=f"Missing required file: {filename}",
                    file_path=str(file_path)
                ))
    
    def _validate_dependencies(self):
        """Validate dependency files"""
        if self.ui_type in ["web", "desktop"]:
            package_file = self.ui_dir / "package.json"
            if package_file.exists():
                self._validate_package_json(package_file)
        
        if self.ui_type in ["cli_gui", "cli_tui"]:
            requirements_file = self.ui_dir / "requirements.txt"
            if requirements_file.exists():
                self._validate_requirements_file(requirements_file)
    
    def _validate_security(self):
        """Validate security aspects"""
        # Check for sensitive data exposure
        for file_path in self.ui_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix in [".js", ".html", ".json"]:
                self._check_sensitive_data(file_path)
        
        # Check for unsafe practices
        if self.ui_type == "web":
            self._validate_web_security()
    
    def _validate_html_file(self, file_path: Path):
        """Validate HTML file structure and content"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Check for basic HTML structure
            if not re.search(r'<!DOCTYPE html>', content, re.IGNORECASE):
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message="Missing DOCTYPE declaration",
                    file_path=str(file_path),
                    suggestion="Add <!DOCTYPE html> at the beginning"
                ))
            
            if not re.search(r'<html[^>]*>', content, re.IGNORECASE):
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message="Missing <html> tag",
                    file_path=str(file_path)
                ))
            
            if not re.search(r'<head[^>]*>', content, re.IGNORECASE):
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message="Missing <head> tag",
                    file_path=str(file_path)
                ))
            
            if not re.search(r'<body[^>]*>', content, re.IGNORECASE):
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message="Missing <body> tag",
                    file_path=str(file_path)
                ))
            
            # Check for form elements
            if not re.search(r'<form[^>]*>', content, re.IGNORECASE):
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    message="No form elements found",
                    file_path=str(file_path),
                    suggestion="Add forms for user input if needed"
                ))
            
            # Check for script references
            if not re.search(r'<script[^>]*src=.*\.js[^>]*>', content, re.IGNORECASE):
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message="No external JavaScript files referenced",
                    file_path=str(file_path)
                ))
            
            # Check for CSS references
            if not re.search(r'<link[^>]*rel=.*stylesheet[^>]*>', content, re.IGNORECASE):
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message="No external CSS files referenced",
                    file_path=str(file_path)
                ))
                
        except Exception as e:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message=f"Error reading HTML file: {str(e)}",
                file_path=str(file_path)
            ))
    
    def _validate_css_file(self, file_path: Path):
        """Validate CSS file structure and content"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Check for basic CSS structure
            if not re.search(r'\.[a-zA-Z][a-zA-Z0-9_-]*\s*{', content):
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    message="No CSS class selectors found",
                    file_path=str(file_path),
                    suggestion="Add CSS classes for styling"
                ))
            
            # Check for basic styling properties
            required_properties = ['color', 'background', 'font-size', 'margin', 'padding']
            missing_properties = []
            
            for prop in required_properties:
                # Check for property as word boundary or at start of line
                if not re.search(rf'(^|[^a-zA-Z0-9_-]){prop}\s*:', content, re.IGNORECASE):
                    missing_properties.append(prop)
            
            if missing_properties and len(missing_properties) >= 3:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.INFO,
                    message=f"Missing common CSS properties: {', '.join(missing_properties)}",
                    file_path=str(file_path),
                    suggestion="Consider adding these properties for better styling"
                ))
            
            # Check for responsive design
            if not re.search(r'@media', content, re.IGNORECASE):
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.INFO,
                    message="No responsive design media queries found",
                    file_path=str(file_path),
                    suggestion="Consider adding responsive design for mobile devices"
                ))
                
        except Exception as e:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message=f"Error reading CSS file: {str(e)}",
                file_path=str(file_path)
            ))
    
    def _validate_js_file(self, file_path: Path):
        """Validate JavaScript file structure and content"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Check for form validation
            if not re.search(r'validate', content, re.IGNORECASE):
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    message="No form validation functions found",
                    file_path=str(file_path),
                    suggestion="Add client-side validation for better UX"
                ))
            
            # Check for error handling
            if not re.search(r'try\s*{', content, re.IGNORECASE):
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    message="No try-catch error handling found",
                    file_path=str(file_path),
                    suggestion="Add error handling for robust code"
                ))
            
            # Check for API calls
            if not re.search(r'fetch\s*\(', content, re.IGNORECASE):
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.INFO,
                    message="No fetch API calls found",
                    file_path=str(file_path),
                    suggestion="Add API integration if backend communication is needed"
                ))
            
            # Check for DOM manipulation
            if not re.search(r'getElementById|querySelector', content, re.IGNORECASE):
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    message="No DOM manipulation found",
                    file_path=str(file_path),
                    suggestion="Add DOM interactions for dynamic content"
                ))
                
        except Exception as e:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message=f"Error reading JavaScript file: {str(e)}",
                file_path=str(file_path)
            ))
    
    def _validate_python_file(self, file_path: Path, check_tkinter: bool = False, check_rich: bool = False):
        """Validate Python file structure and content"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Check for main execution block
            if not re.search(r'if __name__ == ["\']__main__["\']:', content):
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    message="Missing main execution block",
                    file_path=str(file_path),
                    suggestion="Add if __name__ == '__main__': block"
                ))
            
            # Check for required imports
            if check_tkinter and not re.search(r'import tkinter|from tkinter', content):
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message="Missing tkinter import for GUI",
                    file_path=str(file_path),
                    suggestion="Add: import tkinter as tk"
                ))
            
            if check_rich and not re.search(r'from rich|import rich', content):
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message="Missing rich library import for TUI",
                    file_path=str(file_path),
                    suggestion="Add: from rich.console import Console"
                ))
            
            # Check for error handling
            if not re.search(r'try\s*:', content, re.IGNORECASE):
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    message="No try-except error handling found",
                    file_path=str(file_path),
                    suggestion="Add error handling for robust code"
                ))
            
            # Check for function definitions
            if not re.search(r'def\s+\w+\s*\(', content):
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    message="No function definitions found",
                    file_path=str(file_path),
                    suggestion="Organize code into functions"
                ))
                
        except Exception as e:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message=f"Error reading Python file: {str(e)}",
                file_path=str(file_path)
            ))
    
    def _validate_package_json(self, file_path: Path):
        """Validate package.json file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            data = json.loads(content)
            
            # Check required fields
            required_fields = ['name', 'version']
            for field in required_fields:
                if field not in data:
                    self.issues.append(ValidationIssue(
                        level=ValidationLevel.ERROR,
                        message=f"Missing required field in package.json: {field}",
                        file_path=str(file_path),
                        suggestion=f"Add \"{field}\": \"value\" to package.json"
                    ))
            
            # Check for scripts
            if 'scripts' not in data or not data['scripts']:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    message="No scripts defined in package.json",
                    file_path=str(file_path),
                    suggestion="Add start, build, or test scripts"
                ))
            
            # Check for dependencies
            if 'dependencies' not in data:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.INFO,
                    message="No dependencies defined",
                    file_path=str(file_path),
                    suggestion="Add required dependencies"
                ))
                
        except json.JSONDecodeError as e:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.CRITICAL,
                message=f"Invalid JSON in package.json: {str(e)}",
                file_path=str(file_path)
            ))
        except Exception as e:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message=f"Error reading package.json: {str(e)}",
                file_path=str(file_path)
            ))
    
    def _validate_requirements_file(self, file_path: Path):
        """Validate requirements.txt file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = [line.strip() for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
            
            if not lines:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    message="Empty requirements.txt file",
                    file_path=str(file_path),
                    suggestion="Add required Python packages"
                ))
            
            # Check for version specifications
            for line in lines:
                if not re.search(r'[<>=!]', line) and '==' not in line:
                    self.issues.append(ValidationIssue(
                        level=ValidationLevel.INFO,
                        message=f"No version specification for: {line}",
                        file_path=str(file_path),
                        suggestion=f"Consider pinning version: {line}==1.0.0"
                    ))
                    
        except Exception as e:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message=f"Error reading requirements.txt: {str(e)}",
                file_path=str(file_path)
            ))
    
    def _validate_electron_main(self, file_path: Path):
        """Validate Electron main.js file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Check for Electron imports
            if not re.search(r'require\([\'"]electron[\'"]\)', content):
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.CRITICAL,
                    message="Missing Electron import",
                    file_path=str(file_path),
                    suggestion="Add: const { app, BrowserWindow } = require('electron');"
                ))
            
            # Check for window creation
            if not re.search(r'new BrowserWindow', content):
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message="No BrowserWindow creation found",
                    file_path=str(file_path),
                    suggestion="Add window creation code"
                ))
            
            # Check for app events
            if not re.search(r'app\.whenReady', content):
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message="No app.whenReady handler found",
                    file_path=str(file_path),
                    suggestion="Add app event handlers"
                ))
                
        except Exception as e:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message=f"Error reading Electron main.js: {str(e)}",
                file_path=str(file_path)
            ))
    
    def _validate_electron_preload(self, file_path: Path):
        """Validate Electron preload script"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Check for contextBridge usage
            if not re.search(r'contextBridge', content):
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    message="No contextBridge usage found",
                    file_path=str(file_path),
                    suggestion="Use contextBridge for secure communication"
                ))
                
        except Exception as e:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message=f"Error reading preload.js: {str(e)}",
                file_path=str(file_path)
            ))
    
    def _validate_electron_package(self, file_path: Path):
        """Validate Electron package.json"""
        try:
            content = file_path.read_text(encoding='utf-8')
            data = json.loads(content)
            
            # Check for Electron-specific fields
            if 'main' not in data:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.CRITICAL,
                    message="Missing 'main' field in package.json",
                    file_path=str(file_path),
                    suggestion="Add \"main\": \"main.js\""
                ))
            
            # Check for Electron in devDependencies
            dev_deps = data.get('devDependencies', {})
            if 'electron' not in dev_deps:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message="Missing Electron in devDependencies",
                    file_path=str(file_path),
                    suggestion="Add \"electron\": \"^22.0.0\" to devDependencies"
                ))
                
        except Exception as e:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message=f"Error validating Electron package.json: {str(e)}",
                file_path=str(file_path)
            ))
    
    def _validate_openapi_spec(self, file_path: Path):
        """Validate OpenAPI specification"""
        try:
            content = file_path.read_text(encoding='utf-8')
            data = json.loads(content)
            
            # Check required OpenAPI fields
            if 'openapi' not in data:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.CRITICAL,
                    message="Missing 'openapi' version field",
                    file_path=str(file_path)
                ))
            
            if 'info' not in data:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.CRITICAL,
                    message="Missing 'info' field",
                    file_path=str(file_path)
                ))
            
            if 'paths' not in data:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message="Missing 'paths' field",
                    file_path=str(file_path)
                ))
            else:
                # Check for at least one path
                if not data['paths']:
                    self.issues.append(ValidationIssue(
                        level=ValidationLevel.WARNING,
                        message="No API paths defined",
                        file_path=str(file_path)
                    ))
                
        except json.JSONDecodeError as e:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.CRITICAL,
                message=f"Invalid JSON in OpenAPI spec: {str(e)}",
                file_path=str(file_path)
            ))
        except Exception as e:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message=f"Error reading OpenAPI spec: {str(e)}",
                file_path=str(file_path)
            ))
    
    def _validate_swagger_html(self, file_path: Path):
        """Validate Swagger UI HTML"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Check for Swagger UI references
            if not re.search(r'swagger-ui', content, re.IGNORECASE):
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message="No Swagger UI references found",
                    file_path=str(file_path),
                    suggestion="Add Swagger UI CDN links or local files"
                ))
            
            # Check for OpenAPI spec reference
            if not re.search(r'openapi\.json', content):
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    message="No OpenAPI spec reference found",
                    file_path=str(file_path),
                    suggestion="Reference the generated openapi.json file"
                ))
                
        except Exception as e:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message=f"Error reading Swagger HTML: {str(e)}",
                file_path=str(file_path)
            ))
    
    def _validate_api_endpoints(self):
        """Test API endpoints if possible"""
        # This would require starting a server and making actual requests
        # For now, just check if there are any endpoints defined
        openapi_file = self.ui_dir / "openapi.json"
        
        if openapi_file.exists():
            try:
                content = openapi_file.read_text(encoding='utf-8')
                data = json.loads(content)
                
                if 'paths' in data:
                    endpoint_count = len(data['paths'])
                    if endpoint_count == 0:
                        self.issues.append(ValidationIssue(
                            level=ValidationLevel.WARNING,
                            message="No API endpoints defined",
                            file_path=str(openapi_file)
                        ))
                    else:
                        self.issues.append(ValidationIssue(
                            level=ValidationLevel.INFO,
                            message=f"Found {endpoint_count} API endpoints",
                            suggestion="Consider running integration tests"
                        ))
                        
            except Exception as e:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    message=f"Could not analyze API endpoints: {str(e)}",
                    file_path=str(openapi_file)
                ))
    
    def _check_sensitive_data(self, file_path: Path):
        """Check for sensitive data exposure"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Check for common sensitive patterns
            sensitive_patterns = [
                (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
                (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key"),
                (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret"),
                (r'token\s*=\s*["\'][^"\']+["\']', "Hardcoded token"),
                (r'-----BEGIN [A-Z]+ KEY-----', "Private key detected"),
            ]
            
            for pattern, description in sensitive_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    self.issues.append(ValidationIssue(
                        level=ValidationLevel.CRITICAL,
                        message=f"Sensitive data found: {description}",
                        file_path=str(file_path),
                        suggestion="Remove sensitive data and use environment variables"
                    ))
                    
        except Exception as e:
            # Don't fail validation for file reading errors in security check
            pass
    
    def _validate_web_security(self):
        """Validate web security aspects"""
        html_file = self.ui_dir / "index.html"
        
        if html_file.exists():
            try:
                content = html_file.read_text(encoding='utf-8')
                
                # Check for Content Security Policy
                if not re.search(r'content-security-policy', content, re.IGNORECASE):
                    self.issues.append(ValidationIssue(
                        level=ValidationLevel.INFO,
                        message="Missing Content Security Policy",
                        file_path=str(html_file),
                        suggestion="Add CSP meta tag for better security"
                    ))
                
                # Check for external script sources
                if re.search(r'<script[^>]*src=["\']http', content, re.IGNORECASE):
                    self.issues.append(ValidationIssue(
                        level=ValidationLevel.WARNING,
                        message="External script sources detected",
                        file_path=str(html_file),
                        suggestion="Use HTTPS and consider hosting scripts locally"
                    ))
                    
            except Exception:
                pass


def validate_ui_directory(ui_dir: str, ui_type: str = "web") -> ValidationResult:
    """
    Convenience function to validate a UI directory
    
    Args:
        ui_dir: Directory containing generated UI files
        ui_type: Type of UI ('web', 'cli_gui', 'desktop', 'api_docs', 'cli_tui')
    
    Returns:
        ValidationResult with validation issues and status
    """
    validator = UIValidator(ui_dir, ui_type)
    return validator.validate_all()


def print_validation_report(result: ValidationResult):
    """Print a formatted validation report"""
    print(f"\n{'='*60}")
    print(f"UI VALIDATION REPORT")
    print(f"{'='*60}")
    print(f"Status: {result.status.value.upper()}")
    print(f"Execution Time: {result.execution_time:.2f}s")
    print(f"Total Issues: {result.metadata['total_issues']}")
    if 'critical_issues' in result.metadata:
        print(f"Critical: {result.metadata['critical_issues']}")
    if 'error_issues' in result.metadata:
        print(f"Errors: {result.metadata['error_issues']}")
    if 'warning_issues' in result.metadata:
        print(f"Warnings: {result.metadata['warning_issues']}")
    
    if result.issues:
        print(f"\n{'-'*60}")
        print("ISSUES DETECTED:")
        print(f"{'-'*60}")
        
        # Group issues by level
        issues_by_level = {
            ValidationLevel.CRITICAL: [],
            ValidationLevel.ERROR: [],
            ValidationLevel.WARNING: [],
            ValidationLevel.INFO: []
        }
        
        for issue in result.issues:
            issues_by_level[issue.level].append(issue)
        
        for level in [ValidationLevel.CRITICAL, ValidationLevel.ERROR, ValidationLevel.WARNING, ValidationLevel.INFO]:
            level_issues = issues_by_level[level]
            if level_issues:
                print(f"\n{level.value.upper()} ({len(level_issues)}):")
                for issue in level_issues:
                    location = f" ({issue.file_path})" if issue.file_path else ""
                    print(f"  • {issue.message}{location}")
                    if issue.suggestion:
                        print(f"    Suggestion: {issue.suggestion}")
    
    print(f"\n{'='*60}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python ui_validator.py <ui_directory> [ui_type]")
        sys.exit(1)
    
    ui_dir = sys.argv[1]
    ui_type = sys.argv[2] if len(sys.argv) > 2 else "web"
    
    result = validate_ui_directory(ui_dir, ui_type)
    print_validation_report(result)
    
    # Exit with appropriate code
    if result.status == ValidationStatus.FAILED:
        sys.exit(1)
    elif result.status == ValidationStatus.WARNING:
        sys.exit(2)
    else:
        sys.exit(0)