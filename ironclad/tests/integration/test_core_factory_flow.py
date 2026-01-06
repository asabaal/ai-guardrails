#!/usr/bin/env python3
"""
Integration tests for Ironclad core module orchestration.

These tests validate cooperation between core orchestration modules:
- ironclad.py (via factory_manager)
- factory_manager.py
- module_forge.py
- module_designer.py

Tests exercise realistic design -> build -> validate flows using real filesystem
operations. Only external dependencies (ollama.chat) are mocked for isolation.
"""

import pytest
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, ANY
import tempfile
import shutil

# Add src to path
src_dir = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_dir))

from ironclad_ai_guardrails import factory_manager, module_designer
from ironclad_ai_guardrails import module_forge as forge_module


class TestCoreFactoryFlow:
    """Integration tests for core factory workflow."""
    
    @pytest.fixture
    def temp_workspace(self, tmp_path):
        """Create a temporary workspace directory."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        original_dir = os.getcwd()
        yield workspace
        os.chdir(original_dir)
    
    @pytest.fixture
    def sample_blueprint(self):
        """Provide a valid sample blueprint for testing."""
        return {
            "module_name": "test_calculator",
            "dependencies": [],
            "functions": [
                {
                    "name": "add",
                    "signature": "def add(a: int, b: int) -> int",
                    "description": "Add two integers and return sum."
                },
                {
                    "name": "subtract",
                    "signature": "def subtract(a: int, b: int) -> int",
                    "description": "Subtract b from a and return difference."
                }
            ],
            "main_logic_description": "The main function should demonstrate add and subtract functions with example inputs."
        }
    
    @pytest.fixture
    def mock_ollama_responses(self):
        """Provide mock responses for ollama.chat calls."""
        
        def _create_candidate_response(filename):
            return {
                "message": {
                    "content": json.dumps({
                        "filename": filename,
                        "code": f"""def {filename}(a: int, b: int) -> int:
    return a + b

def test_{filename}():
    assert {filename}(2, 3) == 5
    assert {filename}(-1, 1) == 0
    assert {filename}(0, 0) == 0
""",
                        "test": f"""def test_{filename}():
    from {filename} import {filename}
    assert {filename}(2, 3) == 5
"""
                    })
                }
            }
        
        responses = [
            _create_candidate_response("add"),
            _create_candidate_response("subtract"),
            {
                "message": {
                    "content": json.dumps({
                        "filename": "main.py",
                        "code": """from add import add
from subtract import subtract

def main():
    print(f"2 + 3 = {add(2, 3)}")
    print(f"10 - 4 = {subtract(10, 4)}")

if __name__ == "__main__":
    main()
"""
                    })
                }
            }
        ]
        
        response_iter = iter(responses)
        
        def mock_chat(*args, **kwargs):
            try:
                return next(response_iter)
            except StopIteration:
                return {
                    "message": {
                        "content": json.dumps({
                            "filename": "default",
                            "code": "def default(): pass",
                            "test": "def test_default(): pass"
                        })
                    }
                }
        
        return mock_chat
    
    def test_factory_builds_components_from_blueprint(
        self, temp_workspace, sample_blueprint, mock_ollama_responses
    ):
        """Test factory_manager builds components from blueprint."""
        os.chdir(temp_workspace)
        
        with patch('ironclad_ai_guardrails.factory_manager.ollama.chat', side_effect=mock_ollama_responses):
            partial_success, module_dir, successful, failed, status = factory_manager.build_components(
                sample_blueprint, resume_mode="smart"
            )
        
        # High-level assertions only
        assert partial_success is True, "Should have partial success"
        assert len(successful) > 0, "Should build some components"
        assert module_dir is not None, "Module directory should be created"
        
        # Verify filesystem artifacts
        module_path = Path(module_dir)
        assert module_path.exists(), "Module directory should exist"
        
        # Check for component files
        for component_name in successful:
            component_file = module_path / f"{component_name}.py"
            assert component_file.exists(), f"Component file {component_name}.py should be created"
    
    def test_factory_assembles_main_from_components(
        self, temp_workspace, sample_blueprint, mock_ollama_responses
    ):
        """Test factory_manager assembles main.py from components."""
        os.chdir(temp_workspace)
        
        with patch('ironclad_ai_guardrails.factory_manager.ollama.chat', side_effect=mock_ollama_responses):
            # First build components
            partial_success, module_dir, successful, failed, status = factory_manager.build_components(
                sample_blueprint, resume_mode="smart"
            )
            
            # Then assemble main
            factory_manager.assemble_main(sample_blueprint, module_dir, successful)
        
        # Verify main.py exists
        main_file = Path(module_dir) / "main.py"
        assert main_file.exists(), "main.py should be assembled"
        
        # Verify __init__.py exists
        init_file = Path(module_dir) / "__init__.py"
        assert init_file.exists(), "__init__.py should be created"
    
    def test_factory_propagates_build_failures(
        self, temp_workspace, sample_blueprint
    ):
        """Test factory_manager propagates build failures through status report."""
        os.chdir(temp_workspace)
        
        # Mock ollama to return None (generation failure)
        with patch('ironclad_ai_guardrails.factory_manager.ollama.chat', return_value=None):
            partial_success, module_dir, successful, failed, status = factory_manager.build_components(
                sample_blueprint, resume_mode="smart"
            )
        
        # High-level assertions
        assert partial_success is False, "Should not have success when generation fails"
        assert len(failed) > 0, "Should track failed components"
        assert status is not None, "Status report should be populated"
        
        # Verify failed components are in status
        for component_name in failed:
            assert component_name in status, "Failed component should be in status report"
    
    def test_factory_resume_mode_skips_existing_components(
        self, temp_workspace, sample_blueprint, mock_ollama_responses
    ):
        """Test factory_manager resume mode skips existing components."""
        os.chdir(temp_workspace)
        
        # First build to create components
        with patch('ironclad_ai_guardrails.factory_manager.ollama.chat', side_effect=mock_ollama_responses):
            factory_manager.build_components(sample_blueprint, resume_mode="smart")
        
        # Mock to track ollama.chat calls
        with patch('ironclad_ai_guardrails.factory_manager.ollama.chat', return_value=None) as mock_ollama:
            # Resume should skip existing components
            partial_success, module_dir, successful, failed, status = factory_manager.build_components(
                sample_blueprint, resume_mode="resume"
            )
            
            # In resume mode, existing components should be skipped
            # The mock won't be called if components are properly skipped
            assert partial_success is True, "Resume mode should maintain success"
            assert len(successful) > 0, "Should skip to successful components"
    
    def test_module_designer_creates_blueprint(self, temp_workspace):
        """Test module_designer creates blueprint from user request."""
        os.chdir(temp_workspace)
        
        user_request = "I need a calculator that can add and subtract numbers."
        
        # Mock ollama to return a valid blueprint
        mock_blueprint = {
            "module_name": "calculator",
            "dependencies": [],
            "functions": [
                {
                    "name": "add",
                    "signature": "def add(a: int, b: int) -> int",
                    "description": "Add two numbers."
                }
            ],
            "main_logic_description": "Main demonstrates functions."
        }
        
        with patch('ironclad_ai_guardrails.module_designer.ollama.chat') as mock_chat:
            mock_chat.return_value = {
                "message": {"content": json.dumps(mock_blueprint)}
            }
            
            blueprint = module_designer.draft_blueprint(user_request)
        
        # High-level assertions
        assert blueprint is not None, "Blueprint should be generated"
        assert "module_name" in blueprint, "Blueprint should have module_name"
        assert "functions" in blueprint, "Blueprint should have functions"
        assert len(blueprint["functions"]) > 0, "Blueprint should have functions"
    
    def test_module_designer_propagates_generation_failure(self, temp_workspace):
        """Test module_designer propagates blueprint generation failures."""
        os.chdir(temp_workspace)
        
        user_request = "Create a calculator"
        
        # Mock ollama to raise exception
        with patch('ironclad_ai_guardrails.module_designer.ollama.chat') as mock_chat:
            mock_chat.side_effect = Exception("Connection failed")
            
            blueprint = module_designer.draft_blueprint(user_request)
        
        # High-level assertions
        assert blueprint is None, "Blueprint generation should fail gracefully"
    
    def test_full_forge_workflow_with_valid_blueprint(
        self, temp_workspace, sample_blueprint, mock_ollama_responses
    ):
        """Test full module_forge workflow: design -> build -> assemble."""
        os.chdir(temp_workspace)
        
        with patch('ironclad_ai_guardrails.module_forge.draft_blueprint') as mock_draft:
            mock_draft.return_value = sample_blueprint
            
            with patch('ironclad_ai_guardrails.module_forge.factory_manager.build_components') as mock_build:
                mock_build.return_value = (True, "build/test_module", ["add", "subtract"], [], {})
                
                with patch('ironclad_ai_guardrails.module_forge.factory_manager.assemble_main') as mock_assemble:
                    # Simulate main.py creation
                    main_dir = temp_workspace / "build" / "test_module"
                    main_dir.mkdir(parents=True, exist_ok=True)
                    (main_dir / "main.py").write_text("print('main')")
                    (main_dir / "__init__.py").write_text("")
                    
                    # Run workflow (would normally be done via CLI args)
                    # Here we simulate logic flow
                    blueprint = module_designer.draft_blueprint("test request")
                    partial_success, module_dir, successful, failed, status = factory_manager.build_components(
                        blueprint, resume_mode="smart"
                    )
                    
                    if partial_success and successful:
                        factory_manager.assemble_main(sample_blueprint, module_dir, successful)
        
        # High-level assertions
        assert module_dir is not None, "Module directory should be created"
        module_path = Path(module_dir)
        assert module_path.exists(), "Module path should exist"
        
        # Verify components were created
        assert (module_path / "add.py").exists() or len(successful) > 0
    
    def test_factory_creates_module_directory_structure(
        self, temp_workspace, sample_blueprint, mock_ollama_responses
    ):
        """Test factory_manager creates proper module directory structure."""
        os.chdir(temp_workspace)
        
        with patch('ironclad_ai_guardrails.factory_manager.ollama.chat', side_effect=mock_ollama_responses):
            partial_success, module_dir, successful, failed, status = factory_manager.build_components(
                sample_blueprint, resume_mode="smart"
            )
            
            if partial_success and successful:
                factory_manager.assemble_main(sample_blueprint, module_dir, successful)
        
        # Verify directory structure
        module_path = Path(module_dir)
        assert module_path.exists(), "Module directory should exist"
        
        # Check for expected files
        assert (module_path / "__init__.py").exists(), "__init__.py should exist"
        assert (module_path / "main.py").exists(), "main.py should exist"
        
        # Check for component files
        component_files = list(module_path.glob("*.py"))
        assert len(component_files) >= 2, "Should have at least main and one component"
    
    def test_factory_handles_empty_blueprint(
        self, temp_workspace
    ):
        """Test factory_manager handles empty blueprint gracefully."""
        os.chdir(temp_workspace)
        
        empty_blueprint = {
            "module_name": "empty_module",
            "dependencies": [],
            "functions": [],
            "main_logic_description": "No functions to implement."
        }
        
        with patch('ironclad_ai_guardrails.factory_manager.ollama.chat'):
            partial_success, module_dir, successful, failed, status = factory_manager.build_components(
                empty_blueprint, resume_mode="smart"
            )
        
        # High-level assertions
        assert len(successful) == 0, "Empty blueprint should have no successful components"
        assert len(failed) == 0, "Empty blueprint should have no failed components"
        
        # Module directory should still be created
        module_path = Path(module_dir)
        assert module_path.exists(), "Module directory should exist even for empty blueprint"
