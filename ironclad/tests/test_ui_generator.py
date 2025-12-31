#!/usr/bin/env python3
"""
Test suite for UI Generator module
Tests the UI generation engines for different target platforms
"""

import pytest
import json
import os
import tempfile
from typing import Dict, Any
import sys

from ironclad_ai_guardrails.ui_generator import UIGenerator, UIGenerationError, save_ui_artifacts, generate_ui_from_module_spec
from ironclad_ai_guardrails.ui_spec import UIType, ComponentType, UIComponent, UILayout, UIStyling, UISpec, transform_module_spec_to_ui_spec, UIInteraction


class TestUIGenerator:
    """Test UIGenerator class functionality"""
    
    def create_sample_ui_spec(self, ui_type: UIType = UIType.WEB) -> UISpec:
        """Create a sample UI spec for testing"""
        return UISpec(
            ui_type=ui_type,
            title="Test Interface",
            components=[
                UIComponent(
                    name="text_input",
                    type=ComponentType.FORM_INPUT,
                    data_binding="main.text_param",
                    label="Text Parameter",
                    placeholder="Enter text here",
                    validation={"type": "text", "min_length": 1}
                ),
                UIComponent(
                    name="number_input",
                    type=ComponentType.FORM_INPUT,
                    data_binding="main.number_param",
                    label="Number Parameter",
                    placeholder="Enter a number",
                    validation={"type": "integer", "min": 0}
                ),
                UIComponent(
                    name="select_choice",
                    type=ComponentType.SELECT,
                    data_binding="main.choice",
                    label="Choice",
                    options=["Option 1", "Option 2", "Option 3"]
                ),
                UIComponent(
                    name="checkbox_option",
                    type=ComponentType.CHECKBOX,
                    data_binding="main.enabled",
                    label="Enable Feature"
                )
            ],
            layout=UILayout(type="grid", columns=2, spacing="medium"),
            styling=UIStyling(theme="modern", color_scheme="blue"),
            metadata={"version": "1.0"}
        )
    
    def test_generator_creation(self):
        """Test creating a UI generator"""
        ui_spec = self.create_sample_ui_spec()
        generator = UIGenerator(ui_spec)
        
        assert generator.ui_spec == ui_spec
        assert generator.ui_spec.ui_type == UIType.WEB
    
    def test_generate_web_ui(self):
        """Test generating web UI"""
        ui_spec = self.create_sample_ui_spec(UIType.WEB)
        generator = UIGenerator(ui_spec)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            files = generator.generate(temp_dir)
            
            # Should generate web UI files
            assert "index.html" in files
            assert "styles.css" in files
            assert "app.js" in files
            assert "package.json" in files
            
            # Check HTML content
            html_content = files["index.html"]
            assert "Test Interface" in html_content
            assert "text_input" in html_content
            assert "number_input" in html_content
            assert "select_choice" in html_content
            assert "checkbox_option" in html_content
            assert '<form id="mainForm"' in html_content
            
            # Check CSS content
            css_content = files["styles.css"]
            assert "container" in css_content
            assert "form-control" in css_content
            assert "#3498db" in css_content  # Blue color scheme
            
            # Check JavaScript content
            js_content = files["app.js"]
            assert "validateForm" in js_content
            assert "executeModule" in js_content
            assert "main.text_param" in js_content
    
    def test_generate_cli_gui(self):
        """Test generating CLI GUI (Tkinter)"""
        ui_spec = self.create_sample_ui_spec(UIType.CLI_GUI)
        generator = UIGenerator(ui_spec)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            files = generator.generate(temp_dir)
            
            # Should generate CLI GUI files
            assert "gui.py" in files
            assert "requirements.txt" in files
            
            # Check GUI content
            gui_content = files["gui.py"]
            assert "import tkinter as tk" in gui_content
            assert "TestInterfaceGUI" in gui_content
            assert "text_input_var = tk.StringVar()" in gui_content
            assert "execute_module" in gui_content
            
            # Check requirements
            req_content = files["requirements.txt"]
            assert "tkinter" in req_content
    
    def test_generate_desktop_ui(self):
        """Test generating desktop UI (Electron)"""
        ui_spec = self.create_sample_ui_spec(UIType.DESKTOP)
        generator = UIGenerator(ui_spec)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            files = generator.generate(temp_dir)
            
            # Should generate desktop UI files
            assert "main.js" in files
            assert "preload.js" in files
            assert "index.html" in files
            assert "package.json" in files
            
            # Check Electron main file
            main_content = files["main.js"]
            assert "const { app, BrowserWindow } = require('electron')" in main_content
            assert "createWindow" in main_content
            
            # Check package.json
            package_content = files["package.json"]
            package_data = json.loads(package_content)
            assert package_data["main"] == "main.js"
            assert "electron" in package_data["devDependencies"]
    
    def test_generate_api_docs(self):
        """Test generating API documentation"""
        ui_spec = self.create_sample_ui_spec(UIType.API_DOCS)
        generator = UIGenerator(ui_spec)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            files = generator.generate(temp_dir)
            
            # Should generate API docs files
            assert "openapi.json" in files
            assert "swagger.html" in files
            
            # Check OpenAPI spec
            openapi_content = files["openapi.json"]
            openapi_data = json.loads(openapi_content)
            assert openapi_data["openapi"] == "3.0.0"
            assert openapi_data["info"]["title"] == "Test Interface"
            assert "/execute" in openapi_data["paths"]
            
            # Check Swagger HTML
            swagger_content = files["swagger.html"]
            assert "swagger-ui" in swagger_content
            assert "openapi.json" in swagger_content
    
    def test_generate_cli_tui(self):
        """Test generating CLI TUI (Rich/Textual)"""
        ui_spec = self.create_sample_ui_spec(UIType.CLI_TUI)
        generator = UIGenerator(ui_spec)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            files = generator.generate(temp_dir)
            
            # Should generate TUI files
            assert "tui.py" in files
            assert "requirements.txt" in files
            
            # Check TUI content
            tui_content = files["tui.py"]
            assert "from rich.console import Console" in tui_content
            assert "from rich.prompt import Prompt" in tui_content
            assert "TestInterfaceTUI" in tui_content
            assert "Text Parameter" in tui_content
            
            # Check requirements
            req_content = files["requirements.txt"]
            assert "rich" in req_content
            assert "textual" in req_content
    
    def test_unsupported_ui_type(self):
        """Test handling of unsupported UI type"""
        # Create an invalid UI spec
        ui_spec = UISpec(
            ui_type=None,  # This will be invalid
            title="Test",
            components=[],
            layout=UILayout(type="vertical")
        )
        
        generator = UIGenerator(ui_spec)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(UIGenerationError) as exc_info:
                generator.generate(temp_dir)
            
            assert "Unsupported UI type" in str(exc_info.value)


class TestWebUIGeneration:
    """Test specific aspects of Web UI generation"""
    
    def test_html_component_generation(self):
        """Test HTML generation for different component types"""
        ui_spec = UISpec(
            ui_type=UIType.WEB,
            title="Component Test",
            components=[
                UIComponent(
                    name="email_field",
                    type=ComponentType.FORM_INPUT,
                    data_binding="main.email",
                    label="Email",
                    validation={"type": "email"}
                ),
                UIComponent(
                    name="description",
                    type=ComponentType.TEXT_AREA,
                    data_binding="main.desc",
                    label="Description"
                ),
                UIComponent(
                    name="priority",
                    type=ComponentType.RADIO,
                    data_binding="main.priority",
                    label="Priority",
                    options=["Low", "Medium", "High"],
                    default_value="Medium"
                )
            ],
            layout=UILayout(type="vertical")
        )
        
        generator = UIGenerator(ui_spec)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            files = generator.generate(temp_dir)
            html_content = files["index.html"]
            
            # Check email input
            assert 'type="email"' in html_content
            assert 'name="email_field"' in html_content
            assert 'id="email_field"' in html_content
            
            # Check textarea
            assert '<textarea' in html_content
            assert 'name="description"' in html_content
            assert 'id="description"' in html_content
            
            # Check radio buttons
            assert 'type="radio"' in html_content
            assert 'name="priority"' in html_content
            assert 'value="Medium"' in html_content
            assert 'checked' in html_content  # Default value
    
    def test_css_theme_generation(self):
        """Test CSS generation for different themes"""
        # Test modern theme with blue color scheme
        ui_spec_modern = UISpec(
            ui_type=UIType.WEB,
            title="Modern UI",
            components=[
                UIComponent(
                    name="test",
                    type=ComponentType.FORM_INPUT,
                    data_binding="main.test",
                    label="Test"
                )
            ],
            layout=UILayout(type="vertical"),
            styling=UIStyling(theme="modern", color_scheme="blue")
        )
        
        # Test terminal theme
        ui_spec_terminal = UISpec(
            ui_type=UIType.WEB,
            title="Terminal UI",
            components=[
                UIComponent(
                    name="test",
                    type=ComponentType.FORM_INPUT,
                    data_binding="main.test",
                    label="Test"
                )
            ],
            layout=UILayout(type="vertical"),
            styling=UIStyling(theme="terminal")
        )
        
        generator_modern = UIGenerator(ui_spec_modern)
        generator_terminal = UIGenerator(ui_spec_terminal)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            files_modern = generator_modern.generate(temp_dir)
            files_terminal = generator_terminal.generate(temp_dir)
            
            css_modern = files_modern["styles.css"]
            css_terminal = files_terminal["styles.css"]
            
            # Modern CSS should have modern styling
            assert "border-radius" in css_modern
            assert "box-shadow" in css_modern
            
            # Terminal CSS should have terminal styling
            assert "#1a1a1a" in css_terminal  # Dark background
            assert "#00ff00" in css_terminal  # Green text
            assert "monospace" in css_terminal
    
    def test_javascript_validation_generation(self):
        """Test JavaScript validation generation"""
        ui_spec = UISpec(
            ui_type=UIType.WEB,
            title="Validation Test",
            components=[
                UIComponent(
                    name="email_field",
                    type=ComponentType.FORM_INPUT,
                    data_binding="main.email",
                    label="Email",
                    validation={"type": "email"}
                ),
                UIComponent(
                    name="age_field",
                    type=ComponentType.FORM_INPUT,
                    data_binding="main.age",
                    label="Age",
                    validation={"type": "integer", "min": 18}
                )
            ],
            layout=UILayout(type="vertical")
        )
        
        generator = UIGenerator(ui_spec)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            files = generator.generate(temp_dir)
            js_content = files["app.js"]
            
            # Should have validation functions
            assert "function validate_email_field()" in js_content
            assert "function validate_age_field()" in js_content
            
            # Email validation regex
            assert "emailRegex" in js_content
            assert "/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/" in js_content
            
            # Integer validation with minimum
            assert "parseInt(value)" in js_content
            assert "num >= 18" in js_content
    
    def test_javascript_interaction_generation(self):
        """Test JavaScript interaction generation"""
        ui_spec = UISpec(
            ui_type=UIType.WEB,
            title="Interaction Test",
            components=[
                UIComponent(
                    name="test_field",
                    type=ComponentType.FORM_INPUT,
                    data_binding="main.test",
                    label="Test"
                )
            ],
            layout=UILayout(type="vertical"),
            interactions=[
                UIInteraction(
                    trigger="on_change",
                    action="validate_input",
                    target="test"
                )
            ]
        )
        
        generator = UIGenerator(ui_spec)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            files = generator.generate(temp_dir)
            js_content = files["app.js"]
            
            # Should have change handler
            assert "addEventListener('change'" in js_content
            assert "test" in js_content
            assert "validate_input" in js_content


class TestSaveUIArtifacts:
    """Test the save_ui_artifacts function"""
    
    def test_save_artifacts_to_disk(self):
        """Test saving UI artifacts to disk"""
        ui_spec = UISpec(
            ui_type=UIType.WEB,
            title="Save Test",
            components=[
                UIComponent(
                    name="test",
                    type=ComponentType.FORM_INPUT,
                    data_binding="main.test",
                    label="Test"
                )
            ],
            layout=UILayout(type="vertical")
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = os.path.join(temp_dir, "test_output")
            saved_files = save_ui_artifacts(ui_spec, output_dir)
            
            # Should save files to disk
            assert os.path.exists(output_dir)
            assert os.path.exists(os.path.join(output_dir, "index.html"))
            assert os.path.exists(os.path.join(output_dir, "styles.css"))
            assert os.path.exists(os.path.join(output_dir, "app.js"))
            assert os.path.exists(os.path.join(output_dir, "package.json"))
            
            # Should return mapping of saved files
            assert len(saved_files) == 4
            assert os.path.join(output_dir, "index.html") in saved_files
            assert os.path.join(output_dir, "styles.css") in saved_files


class TestGenerateUIFromModuleSpec:
    """Test the convenience function for generating UI from module spec"""
    
    def test_generate_from_module_spec(self):
        """Test generating UI directly from module specification"""
        module_spec = {
            "module_name": "calculator",
            "main_logic_description": "Simple calculator",
            "functions": [
                {
                    "name": "add",
                    "signature": "def add(a: int, b: int) -> int:",
                    "description": "Add two numbers"
                },
                {
                    "name": "main",
                    "signature": "def main(operation: str, a: int, b: int) -> int:",
                    "description": "Main calculator function"
                }
            ]
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = os.path.join(temp_dir, "generated_ui")
            saved_files = generate_ui_from_module_spec(
                module_spec,
                ui_type="web",
                output_dir=output_dir
            )
            
            # Should generate and save web UI
            assert os.path.exists(output_dir)
            assert os.path.exists(os.path.join(output_dir, "index.html"))
            
            # Should return saved files mapping
            assert len(saved_files) > 0
            assert any("index.html" in path for path in saved_files.keys())
    
    def test_generate_from_module_spec_invalid_type(self):
        """Test handling of invalid UI type in convenience function"""
        module_spec = {
            "module_name": "test",
            "functions": []
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = os.path.join(temp_dir, "test")
            # Should default to WEB when invalid type provided
            saved_files = generate_ui_from_module_spec(
                module_spec,
                ui_type="invalid_type",
                output_dir=output_dir
            )
            
            # Should still generate files (with default WEB type)
            assert len(saved_files) > 0


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_empty_components_list(self):
        """Test UI generation with no components"""
        ui_spec = UISpec(
            ui_type=UIType.WEB,
            title="Empty UI",
            components=[],
            layout=UILayout(type="vertical")
        )
        
        generator = UIGenerator(ui_spec)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            files = generator.generate(temp_dir)
            
            # Should still generate files
            assert "index.html" in files
            assert "styles.css" in files
            assert "app.js" in files
            
            # HTML should have empty form
            html_content = files["index.html"]
            assert '<form id="mainForm"' in html_content
            assert '</form>' in html_content
    
    def test_component_without_validation(self):
        """Test component without validation rules"""
        ui_spec = UISpec(
            ui_type=UIType.WEB,
            title="No Validation",
            components=[
                UIComponent(
                    name="simple_field",
                    type=ComponentType.FORM_INPUT,
                    data_binding="main.simple",
                    label="Simple Field"
                    # No validation
                )
            ],
            layout=UILayout(type="vertical")
        )
        
        generator = UIGenerator(ui_spec)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            files = generator.generate(temp_dir)
            js_content = files["app.js"]
            
            # Should handle missing validation gracefully
            assert "validate_simple_field" not in js_content or "validateForm" in js_content
    
    def test_unsupported_component_type(self):
        """Test handling of unsupported component types in HTML generation"""
        # Create a component with an unsupported type (by manually creating the spec)
        ui_spec = UISpec(
            ui_type=UIType.WEB,
            title="Unsupported Component",
            components=[
                UIComponent(
                    name="unsupported",
                    type=ComponentType.DISPLAY,  # Not supported in HTML generation
                    data_binding="main.unsupported",
                    label="Unsupported"
                )
            ],
            layout=UILayout(type="vertical")
        )
        
        generator = UIGenerator(ui_spec)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            files = generator.generate(temp_dir)
            html_content = files["index.html"]
            
            # Should handle gracefully with fallback message
            assert "Unsupported component type" in html_content
    
    def test_custom_css_in_styling(self):
        """Test custom CSS in styling"""
        custom_css = "body { background: linear-gradient(45deg, #ff6b6b, #4ecdc4); }"
        
        ui_spec = UISpec(
            ui_type=UIType.WEB,
            title="Custom CSS",
            components=[
                UIComponent(
                    name="test",
                    type=ComponentType.FORM_INPUT,
                    data_binding="main.test",
                    label="Test"
                )
            ],
            layout=UILayout(type="vertical"),
            styling=UIStyling(custom_css=custom_css)
        )
        
        generator = UIGenerator(ui_spec)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            files = generator.generate(temp_dir)
            css_content = files["styles.css"]
            
            # Should include custom CSS
            assert custom_css in css_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])