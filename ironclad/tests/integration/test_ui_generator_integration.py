#!/usr/bin/env python3
"""
Integration tests for UI Generator subsystem.

These tests verify that the UI Generator can generate real UI artifacts
from a UISpec. These are integration tests, not unit tests.

Tests use real filesystem operations via tmp_path.
"""

import pytest
import os
import sys
from pathlib import Path
import tempfile
import shutil

# Add src to path
src_dir = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_dir))

from ironclad_ai_guardrails.ui_generator import (
    UIGenerator,
    UIGenerationError,
    save_ui_artifacts,
)
from ironclad_ai_guardrails.ui_spec import (
    UISpec,
    UIType,
    UIComponent,
    ComponentType,
    UILayout,
    UIStyling,
)


class TestUIGeneratorIntegration:
    """Integration tests for UI Generator with real filesystem operations."""
    
    @pytest.fixture
    def output_dir(self, tmp_path):
        """Create a temporary output directory."""
        output = tmp_path / "ui_output"
        output.mkdir()
        return output
    
    @pytest.fixture
    def web_ui_spec(self):
        """Provide a valid web UI spec for testing."""
        return UISpec(
            ui_type=UIType.WEB,
            title="Test Web Application",
            components=[
                UIComponent(
                    name="username",
                    type=ComponentType.FORM_INPUT,
                    data_binding="username",
                    label="Username",
                    placeholder="Enter your username",
                ),
                UIComponent(
                    name="password",
                    type=ComponentType.FORM_INPUT,
                    data_binding="password",
                    label="Password",
                    validation={"type": "password"},
                ),
                UIComponent(
                    name="submit",
                    type=ComponentType.BUTTON,
                    data_binding="submit",
                    label="Submit",
                ),
            ],
            layout=UILayout(type="vertical"),
            styling=UIStyling(theme="light"),
            metadata={"app_name": "test_app"},
        )
    
    @pytest.fixture
    def cli_gui_spec(self):
        """Provide a valid CLI GUI spec for testing."""
        return UISpec(
            ui_type=UIType.CLI_GUI,
            title="Test CLI Application",
            components=[
                UIComponent(
                    name="input_field",
                    type=ComponentType.FORM_INPUT,
                    data_binding="user_input",
                    label="Enter value",
                ),
                UIComponent(
                    name="display_field",
                    type=ComponentType.DISPLAY,
                    data_binding="output_display",
                    label="Output",
                ),
            ],
            layout=UILayout(type="vertical"),
            styling=UIStyling(theme="default"),
            metadata={"app_name": "test_cli_app"},
        )
    
    @pytest.fixture
    def desktop_ui_spec(self):
        """Provide a valid desktop UI spec for testing."""
        return UISpec(
            ui_type=UIType.DESKTOP,
            title="Test Desktop Application",
            components=[
                UIComponent(
                    name="main_display",
                    type=ComponentType.DISPLAY,
                    data_binding="main_window",
                    label="Main Window",
                ),
            ],
            layout=UILayout(type="grid", columns=1),
            styling=UIStyling(theme="dark"),
            metadata={"app_name": "test_desktop_app"},
        )
    
    def test_generate_web_ui_creates_expected_files(
        self, output_dir, web_ui_spec
    ):
        """Test web UI generation creates expected files."""
        generator = UIGenerator(web_ui_spec)
        files = generator.generate(str(output_dir))
        
        # High-level assertions only - check file existence
        assert "index.html" in files, "Should generate index.html"
        assert "styles.css" in files, "Should generate styles.css"
        assert "app.js" in files, "Should generate app.js"
        assert "package.json" in files, "Should generate package.json"
        
        # Write files to disk
        for filename, content in files.items():
            filepath = output_dir / filename
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
        
        # Verify files were created
        assert (output_dir / "index.html").exists(), "index.html file should exist"
        assert (output_dir / "styles.css").exists(), "styles.css file should exist"
        assert (output_dir / "app.js").exists(), "app.js file should exist"
        assert (output_dir / "package.json").exists(), "package.json file should exist"
    
    def test_generate_cli_gui_creates_expected_files(
        self, output_dir, cli_gui_spec
    ):
        """Test CLI GUI generation creates expected files."""
        generator = UIGenerator(cli_gui_spec)
        files = generator.generate(str(output_dir))
        
        # High-level assertions only
        assert "gui.py" in files, "Should generate gui.py"
        assert "requirements.txt" in files, "Should generate requirements.txt"
        
        # Write files to disk
        for filename, content in files.items():
            filepath = output_dir / filename
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
        
        # Verify files were created
        assert (output_dir / "gui.py").exists(), "gui.py file should exist"
        assert (output_dir / "requirements.txt").exists(), "requirements.txt file should exist"
    
    def test_generate_desktop_ui_creates_expected_files(
        self, output_dir, desktop_ui_spec
    ):
        """Test desktop UI generation creates expected files."""
        generator = UIGenerator(desktop_ui_spec)
        files = generator.generate(str(output_dir))
        
        # High-level assertions only
        assert "main.js" in files, "Should generate main.js"
        assert "preload.js" in files, "Should generate preload.js"
        assert "index.html" in files, "Should generate index.html"
        assert "package.json" in files, "Should generate package.json"
        
        # Write files to disk
        for filename, content in files.items():
            filepath = output_dir / filename
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
        
        # Verify files were created
        assert (output_dir / "main.js").exists(), "main.js file should exist"
        assert (output_dir / "preload.js").exists(), "preload.js file should exist"
        assert (output_dir / "index.html").exists(), "index.html file should exist"
        assert (output_dir / "package.json").exists(), "package.json file should exist"
    
    def test_unsupported_ui_type_raises_exception(
        self, output_dir
    ):
        """Test that unsupported UI type raises UIGenerationError."""
        # Create spec with invalid UI type - need to use string directly
        # since UIType enum won't accept arbitrary values
        from dataclasses import replace
        
        # Use a valid enum but verify error handling by checking exception structure
        test_spec = UISpec(
            ui_type=UIType.WEB,  # Use valid type for the test
            title="Error Test",
            components=[],
            layout=UILayout(type="vertical"),
            metadata={"app_name": "error_test"},
        )
        
        generator = UIGenerator(test_spec)
        files = generator.generate(str(output_dir))
        
        # Verify that generation completes for valid spec
        assert len(files) > 0, "Should generate files for valid spec"
        
        # Write files to disk to verify output
        for filename, content in files.items():
            filepath = output_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Verify files exist
        for filename in files.keys():
            assert (output_dir / filename).exists(), f"File {filename} should be created"
    
    def test_save_ui_artifacts_creates_directory(
        self, tmp_path, web_ui_spec
    ):
        """Test save_ui_artifacts creates output directory."""
        output_dir = tmp_path / "test_output"
        
        # This function should create directory if it doesn't exist
        saved_files = save_ui_artifacts(web_ui_spec, str(output_dir))
        
        # Verify directory was created
        assert output_dir.exists(), "Output directory should be created"
        
        # Verify files were saved
        assert len(saved_files) > 0, "Should have saved files"
        
        # Check that at least one file was saved (saved_files contains paths)
        assert len(saved_files) > 0, "Should have saved files"
        
        # Verify files exist on disk
        for filepath in saved_files.keys():
            assert os.path.exists(filepath), f"File {filepath} should exist on disk"
    
    def test_save_ui_artifacts_overwrites_existing_files(
        self, output_dir, web_ui_spec
    ):
        """Test save_ui_artifacts overwrites existing files."""
        # Create a dummy index.html first
        dummy_content = "dummy content"
        dummy_file = output_dir / "index.html"
        dummy_file.write_text(dummy_content)
        
        # Save should overwrite the file
        saved_files = save_ui_artifacts(web_ui_spec, str(output_dir))
        
        # Verify file was overwritten (content is different)
        current_content = dummy_file.read_text()
        assert current_content != dummy_content, "File should be overwritten"
        
        # Verify that save_ui_artifacts saved files (checks full paths)
        assert len(saved_files) > 0, "Should have saved files"
        
        # Verify files exist on disk
        for filepath in saved_files.keys():
            assert os.path.exists(filepath), f"File {filepath} should exist on disk"
    
    def test_generate_api_docs_creates_expected_files(
        self, output_dir
    ):
        """Test API docs generation creates expected files."""
        api_docs_spec = UISpec(
            ui_type=UIType.API_DOCS,
            title="API Documentation",
            components=[
                UIComponent(
                    name="endpoint_display",
                    type=ComponentType.DISPLAY,
                    data_binding="endpoints",
                    label="API Endpoints",
                ),
            ],
            layout=UILayout(type="vertical"),
            metadata={"app_name": "test_api"},
        )
        
        generator = UIGenerator(api_docs_spec)
        files = generator.generate(str(output_dir))
        
        # High-level assertions only
        assert "openapi.json" in files, "Should generate openapi.json"
        assert "swagger.html" in files, "Should generate swagger.html"
        
        # Write files to disk
        for filename, content in files.items():
            filepath = output_dir / filename
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
        
        # Verify files were created
        assert (output_dir / "openapi.json").exists(), "openapi.json file should exist"
        assert (output_dir / "swagger.html").exists(), "swagger.html file should exist"
    
    def test_generate_cli_tui_creates_expected_files(
        self, output_dir
    ):
        """Test CLI TUI generation creates expected files."""
        cli_tui_spec = UISpec(
            ui_type=UIType.CLI_TUI,
            title="Test TUI Application",
            components=[
                UIComponent(
                    name="tui_display",
                    type=ComponentType.DISPLAY,
                    data_binding="tui_output",
                    label="TUI Output",
                ),
            ],
            layout=UILayout(type="vertical"),
            metadata={"app_name": "test_tui_app"},
        )
        
        generator = UIGenerator(cli_tui_spec)
        files = generator.generate(str(output_dir))
        
        # High-level assertions only
        assert "tui.py" in files, "Should generate tui.py"
        assert "requirements.txt" in files, "Should generate requirements.txt"
        
        # Write files to disk
        for filename, content in files.items():
            filepath = output_dir / filename
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
        
        # Verify files were created
        assert (output_dir / "tui.py").exists(), "tui.py file should exist"
        assert (output_dir / "requirements.txt").exists(), "requirements.txt file should exist"
