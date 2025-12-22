import pytest
import json
import os
import sys
import tempfile
import subprocess
from unittest.mock import patch, MagicMock, mock_open

# Add src to path for importing
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
import factory_manager
import code_utils


class TestBuildComponents:
    """Test the build_components function"""
    
    @patch('factory_manager.ironclad.generate_candidate')
    @patch('factory_manager.ironclad.validate_candidate')
    @patch('factory_manager.ironclad.repair_candidate')
    @patch('os.makedirs')
    @patch('builtins.print')
    @patch('builtins.open', create=True)  # Mock file creation
    def test_build_components_success(self, mock_open, mock_print, mock_makedirs, mock_repair, mock_validate, mock_generate):
        """Test successful component building"""
        # Setup mocks
        mock_generate.return_value = {
            'filename': 'test_func',
            'code': 'def test_func(): return "test"',
            'test': 'def test_test_func(): assert test_func() == "test"'
        }
        mock_validate.return_value = (True, "Tests passed")
        
        blueprint = {
            'module_name': 'test_module',
            'functions': [
                {
                    'name': 'test_func',
                    'signature': 'def test_func() -> str',
                    'description': 'A test function'
                }
            ]
        }
        
        # Execute
        partial_success, module_dir, successful_components, failed_components, status_report = factory_manager.build_components(blueprint)
        
        # Assertions
        assert partial_success is True
        assert 'test_module' in module_dir
        assert successful_components == ['test_func']
        assert failed_components == []
        assert status_report['test_func']['status'] == 'success'
        mock_makedirs.assert_called_once()
        mock_generate.assert_called_once()
        mock_validate.assert_called_once()
        mock_repair.assert_not_called()  # Should not need repair
    
    @patch('factory_manager.ironclad.generate_candidate')
    @patch('factory_manager.ironclad.validate_candidate')
    @patch('factory_manager.ironclad.repair_candidate')
    @patch('os.makedirs')
    @patch('shutil.rmtree')
    @patch('os.path.exists')
    @patch('builtins.print')
    @patch('builtins.open', create=True)
    def test_build_components_smart_mode_existing_dir(self, mock_open, mock_print, mock_exists, mock_rmtree, mock_makedirs, mock_repair, mock_validate, mock_generate):
        """Test build_components in smart mode when directory already exists"""
        # Setup mocks
        mock_exists.return_value = True  # Directory exists
        mock_generate.return_value = {
            'code': 'def test_func(): pass',
            'explanation': 'Generated function'
        }
        mock_validate.return_value = {
            'status': 'success',
            'message': 'Component is valid'
        }
        
        blueprint = {
            'module_name': 'test_module',
            'functions': [
                {'name': 'test_func', 'signature': 'def test_func()', 'description': 'Test function'}
            ]
        }
        
        # Execute in smart mode
        partial_success, module_dir, successful_components, failed_components, status_report = factory_manager.build_components(blueprint, "smart")
        
        # Assertions
        assert partial_success is True
        assert successful_components == ['test_func']
        assert failed_components == []
        
        # Verify existing directory was removed (line 25)
        mock_rmtree.assert_called_once()
        mock_makedirs.assert_not_called()  # makedirs only called in else branch
    
    @patch('factory_manager.ironclad.generate_candidate')
    @patch('factory_manager.ironclad.validate_candidate')
    @patch('factory_manager.ironclad.repair_candidate')
    @patch('os.makedirs')
    @patch('builtins.print')
    @patch('builtins.open', create=True)
    def test_build_components_with_repair(self, mock_open, mock_print, mock_makedirs, mock_repair, mock_validate, mock_generate):
        """Test component building that requires repair"""
        # Setup mocks - validation fails first time
        mock_generate.return_value = {
            'filename': 'broken_func',
            'code': 'def broken_func(): return "broken"',
            'test': 'def test_broken_func(): assert broken_func() == "test"'
        }
        mock_validate.side_effect = [
            (False, "Test failed"),  # First attempt fails
            (True, "Tests passed")    # Second attempt succeeds
        ]
        mock_repair.return_value = {
            'filename': 'fixed_func',
            'code': 'def fixed_func(): return "fixed"',
            'test': 'def test_fixed_func(): assert fixed_func() == "fixed"'
        }
        
        blueprint = {
            'module_name': 'test_module',
            'functions': [
                {
                    'name': 'broken_func',
                    'signature': 'def broken_func() -> str',
                    'description': 'A broken function'
                }
            ]
        }
        
        # Execute
        partial_success, module_dir, successful_components, failed_components, status_report = factory_manager.build_components(blueprint)
        
        # Assertions
        assert partial_success is True
        assert 'test_module' in module_dir
        assert successful_components == ['broken_func']
        assert failed_components == []
        assert status_report['broken_func']['status'] == 'success'
        assert status_report['broken_func']['attempts'] == 2
        mock_generate.assert_called_once()
        assert mock_validate.call_count == 2  # Called twice (initial + after repair)
        mock_repair.assert_called_once()
    
    @patch('factory_manager.ironclad.generate_candidate')
    @patch('factory_manager.ironclad.validate_candidate')
    @patch('factory_manager.ironclad.repair_candidate')
    @patch('os.makedirs')
    @patch('builtins.print')
    def test_build_components_max_retries_exceeded(self, mock_print, mock_makedirs, mock_repair, mock_validate, mock_generate):
        """Test component building when max retries exceeded"""
        # Setup mocks - validation always fails
        mock_generate.return_value = {
            'filename': 'broken_func',
            'code': 'def broken_func(): return "broken"',
            'test': 'def test_broken_func(): assert broken_func() == "test"'
        }
        mock_validate.return_value = (False, "Test failed")
        mock_repair.return_value = None  # Repair also fails
        
        blueprint = {
            'module_name': 'test_module',
            'functions': [
                {
                    'name': 'broken_func',
                    'signature': 'def broken_func() -> str',
                    'description': 'A broken function'
                }
            ]
        }
        
        # Execute
        partial_success, module_dir, successful_components, failed_components, status_report = factory_manager.build_components(blueprint)
        
        # Assertions
        assert partial_success is False
        assert 'test_module' in module_dir
        assert successful_components == []
        assert failed_components == ['broken_func']
        assert status_report['broken_func']['status'] == 'failed'
        assert status_report['broken_func']['attempts'] == 3
        mock_generate.assert_called_once()
        assert mock_validate.call_count == 3  # Called 3 times (initial + 2 repairs)
        assert mock_repair.call_count == 2  # Called 2 times


class TestAssembleMain:
    """Test the assemble_main function"""
    
    @patch('factory_manager.validate_main_candidate')
    @patch('factory_manager.generate_main_candidate')
    @patch('factory_manager.ollama.chat')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    @patch('builtins.print')
    def test_assemble_main_success(self, mock_print, mock_makedirs, mock_file, mock_chat, mock_generate, mock_validate):
        """Test successful main assembly"""
        # Setup mocks
        mock_generate.return_value = 'def main(): print("Hello World")'
        mock_validate.return_value = (True, "Valid")
        
        blueprint = {
            'module_name': 'test_module',
            'main_logic_description': 'Print Hello World'
        }
        module_dir = '/tmp/test_module'
        components = ['func1', 'func2']
        
        # Execute
        factory_manager.assemble_main(blueprint, module_dir, components)
        
        # Assertions
        mock_generate.assert_called_once_with(blueprint, components)
        mock_validate.assert_called_once()
        mock_file.assert_called()  # File should be written
        # Check that main.py was written
        mock_file.assert_any_call(os.path.join(module_dir, "main.py"), "w")
        # Check that __init__.py was created
        mock_file.assert_any_call(os.path.join(module_dir, "__init__.py"), "w")
    
    @patch('factory_manager.ollama.chat')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    @patch('builtins.print')
    def test_assemble_main_json_error(self, mock_print, mock_makedirs, mock_file, mock_chat):
        """Test main assembly with JSON error"""
        # Setup mock to return invalid JSON
        mock_chat.return_value = {
            'message': {
                'content': 'invalid json content'
            }
        }
        
        blueprint = {
            'module_name': 'test_module',
            'main_logic_description': 'Test logic'
        }
        module_dir = '/tmp/test_module'
        components = ['func1']
        
        # Execute - should not raise exception
        with pytest.raises(Exception):
            factory_manager.assemble_main(blueprint, module_dir, components)


class TestCleanJson:
    """Test the clean_json helper function"""
    
    def test_clean_json_normal(self):
        """Test cleaning normal JSON"""
        input_text = '{"key": "value"}'
        result = factory_manager.clean_json(input_text)
        assert result == '{"key": "value"}'
    
    def test_clean_json_with_markdown(self):
        """Test cleaning JSON with markdown fences"""
        input_text = '```json\n{"key": "value"}\n```'
        result = factory_manager.clean_json(input_text)
        assert result == '{"key": "value"}'
    
    def test_clean_json_with_simple_fences(self):
        """Test cleaning JSON with simple fences"""
        input_text = '```\n{"key": "value"}\n```'
        result = factory_manager.clean_json(input_text)
        assert result == '{"key": "value"}'
    
    def test_clean_json_with_whitespace(self):
        """Test cleaning JSON with extra whitespace"""
        input_text = '   ```json\n   {"key": "value"}\n   ```   '
        result = factory_manager.clean_json(input_text)
        assert result == '{"key": "value"}'


class TestAssembleMainRepair:
    """Test assemble_main repair functionality"""
    
    @patch('factory_manager.repair_main_candidate')
    @patch('factory_manager.validate_main_candidate')
    @patch('factory_manager.generate_main_candidate')
    @patch('factory_manager.ollama.chat')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    @patch('builtins.print')
    def test_assemble_main_with_repair_loop(self, mock_print, mock_makedirs, mock_file, mock_chat, mock_generate, mock_validate, mock_repair):
        """Test assemble_main with repair loop (lines 243-247)"""
        blueprint = {
            'module_name': 'test_module',
            'main_logic_description': 'Test main logic'
        }
        module_dir = '/tmp/test_module'
        components = ['test_func']
        
        # Setup mocks for repair scenario
        mock_generate.return_value = 'def main(): pass'
        # First validation fails, second succeeds
        mock_validate.side_effect = [
            (False, "Syntax error: invalid syntax"),
            (True, "Valid")
        ]
        mock_repair.return_value = 'def main(): pass  # fixed'
        mock_chat.return_value = '{"response": "repaired"}'
        
        factory_manager.assemble_main(blueprint, module_dir, components)
        
        # Verify repair loop was executed (lines 243-247)
        assert mock_validate.call_count == 2
        mock_repair.assert_called_once()
        
        # Verify repair messages were printed (lines 244-245)
        mock_print.assert_any_call("   [-] Repairing main.py (Attempt 1)...")
        mock_print.assert_any_call("       Issues: Syntax error: invalid syntax")
    
    @patch('factory_manager.repair_main_candidate')
    @patch('factory_manager.validate_main_candidate')
    @patch('factory_manager.generate_main_candidate')
    @patch('factory_manager.ollama.chat')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    @patch('builtins.print')
    def test_assemble_main_max_attempts_exceeded(self, mock_print, mock_makedirs, mock_file, mock_chat, mock_generate, mock_validate, mock_repair):
        """Test assemble_main when max attempts are exceeded (line 255)"""
        blueprint = {
            'module_name': 'test_module',
            'main_logic_description': 'Test main logic'
        }
        module_dir = '/tmp/test_module'
        components = ['test_func']
        
        # Setup mocks for persistent failure
        mock_generate.return_value = 'def main(): pass'
        # All validation attempts fail
        mock_validate.return_value = (False, "Persistent syntax error")
        mock_repair.return_value = 'def main(): pass  # still broken'
        mock_chat.return_value = '{"response": "failed repair"}'
        
        # Should raise exception after 3 failed attempts
        with pytest.raises(Exception) as exc_info:
            factory_manager.assemble_main(blueprint, module_dir, components)
        
        # Verify the exception message (line 255)
        assert "Failed to generate valid main.py after 3 attempts" in str(exc_info.value)
        assert "Persistent syntax error" in str(exc_info.value)
        
        # Verify repair was attempted 2 times (3 total attempts, first doesn't count as repair)
        assert mock_validate.call_count == 3
        assert mock_repair.call_count == 2


class TestRunFactoryManagerWorkflow:
    """Test run_factory_manager_workflow function"""
    
    @patch('factory_manager.assemble_main')
    @patch('factory_manager.build_components')
    @patch('json.load')
    @patch('builtins.open', create=True)
    @patch('os.path.exists')
    @patch('builtins.print')
    def test_workflow_success_with_failures(self, mock_print, mock_exists, mock_open, mock_load, mock_build, mock_assemble):
        """Test successful workflow with some failed components (lines 282-287)"""
        # Setup mocks
        mock_exists.return_value = True
        mock_load.return_value = {
            'module_name': 'test_module',
            'functions': ['func1', 'func2', 'func3']
        }
        mock_build.return_value = (
            True,  # partial_success
            '/tmp/test_module',  # directory
            ['func1', 'func2'],  # successful_components
            ['func3'],  # failed_components
            {}  # status_report
        )
        
        with patch('sys.exit') as mock_exit:
            factory_manager.run_factory_manager_workflow()
        
        # Verify workflow was called
        mock_build.assert_called_once()
        mock_assemble.assert_called_once()
        
        # Verify success with failures message (lines 282-285)
        mock_print.assert_any_call("\n[⚠️]  Module completed with 1 failed components:")
        mock_print.assert_any_call("     [❌] func3")
        mock_exit.assert_not_called()  # Should not exit on partial success
    
    @patch('factory_manager.assemble_main')
    @patch('factory_manager.build_components')
    @patch('json.load')
    @patch('builtins.open', create=True)
    @patch('os.path.exists')
    @patch('builtins.print')
    def test_workflow_complete_success(self, mock_print, mock_exists, mock_open, mock_load, mock_build, mock_assemble):
        """Test completely successful workflow (lines 286-287)"""
        # Setup mocks
        mock_exists.return_value = True
        mock_load.return_value = {
            'module_name': 'test_module',
            'functions': ['func1', 'func2']
        }
        mock_build.return_value = (
            True,  # partial_success
            '/tmp/test_module',  # directory
            ['func1', 'func2'],  # successful_components
            [],  # failed_components
            {}  # status_report
        )
        
        with patch('sys.exit') as mock_exit:
            factory_manager.run_factory_manager_workflow()
        
        # Verify complete success message (lines 286-287)
        mock_print.assert_any_call("\n[✅] All 2 components built successfully!")
        mock_exit.assert_not_called()
    
    @patch('factory_manager.build_components')
    @patch('os.path.exists')
    @patch('builtins.print')
    def test_workflow_no_blueprint_file(self, mock_print, mock_exists, mock_build):
        """Test workflow when blueprint.json doesn't exist (lines 269-271)"""
        mock_exists.return_value = False
        
        with patch('sys.exit') as mock_exit:
            factory_manager.run_factory_manager_workflow()
        
        # Verify missing file error (lines 269-271)
        mock_print.assert_any_call("Run module_designer.py first!")
        mock_exit.assert_called_once_with(1)
        # build_components should not be called when blueprint file doesn't exist
        mock_build.assert_not_called()
    
    @patch('factory_manager.assemble_main')
    @patch('factory_manager.build_components')
    @patch('json.load')
    @patch('builtins.open', create=True)
    @patch('os.path.exists')
    @patch('builtins.print')
    def test_workflow_no_components_built(self, mock_print, mock_exists, mock_open, mock_load, mock_build, mock_assemble):
        """Test workflow when no components could be built (lines 288-290)"""
        # Setup mocks
        mock_exists.return_value = True
        mock_load.return_value = {
            'module_name': 'test_module',
            'functions': ['func1', 'func2']
        }
        mock_build.return_value = (
            False,  # partial_success
            '/tmp/test_module',  # directory
            [],  # successful_components
            ['func1', 'func2'],  # failed_components
            {}  # status_report
        )
        
        with patch('sys.exit') as mock_exit:
            factory_manager.run_factory_manager_workflow()
        
        # Verify no components built error (lines 288-290)
        mock_print.assert_any_call("\n[❌] No components could be built successfully.")
        mock_exit.assert_called_once_with(1)
        mock_assemble.assert_not_called()  # Should not assemble if no success


class TestFactoryManagerIntegration:
    """Integration tests for factory manager workflow"""
    
    @patch('factory_manager.validate_main_candidate')
    @patch('factory_manager.generate_main_candidate')
    @patch('factory_manager.ironclad.generate_candidate')
    @patch('factory_manager.ironclad.validate_candidate')
    @patch('factory_manager.ironclad.repair_candidate')
    @patch('factory_manager.os.makedirs')
    @patch('factory_manager.os.path.exists')
    @patch('factory_manager.os.path.join')
    @patch('builtins.open')
    @patch('builtins.print')
    @patch('factory_manager.ollama.chat')
    def test_full_workflow_integration(self, mock_chat, mock_print, mock_open, mock_join, mock_exists, mock_makedirs, mock_repair, mock_validate, mock_generate_ironclad, mock_generate_main, mock_validate_main):
        """Test complete workflow from blueprint to assembled module"""
        # Setup mocks
        mock_generate_ironclad.return_value = {
            'filename': 'test_func',
            'code': 'def test_func(): return "success"',
            'test': 'def test_test_func(): assert test_func() == "success"'
        }
        mock_validate.return_value = (True, "Tests passed")
        mock_generate_main.return_value = 'def main(): test_func()'
        mock_validate_main.return_value = (True, "Valid")
        mock_chat.return_value = {
            'message': {
                'content': '{"filename": "main.py", "code": "def main(): test_func()"}'
            }
        }
        # Mock exists to return True for blueprint.json, False for module directory
        def exists_side_effect(path):
            if 'blueprint.json' in path:
                return True
            elif 'build/integration_test' in path:
                return False  # Directory doesn't exist, so no rmtree error
            return True
        
        mock_exists.side_effect = exists_side_effect
        
        blueprint = {
            'module_name': 'integration_test',
            'functions': [
                {
                    'name': 'test_func',
                    'signature': 'def test_func() -> str',
                    'description': 'Test function'
                }
            ],
            'main_logic_description': 'Call test_func'
        }
        
        # Mock os.path.join to return predictable paths
        mock_join.side_effect = lambda *args: '/'.join(args)
        
        # Execute workflow
        with patch('factory_manager.ollama.chat') as mock_chat:
            mock_chat.return_value = {
                'message': {
                    'content': '{"filename": "main.py", "code": "def main(): test_func()"}'
                }
            }
            
            partial_success, directory, successful_components, failed_components, status_report = factory_manager.build_components(blueprint)
            
            if partial_success and successful_components:
                factory_manager.assemble_main(blueprint, directory, successful_components)
        
        # Verify workflow completed
        assert partial_success is True
        assert 'integration_test' in directory
        assert successful_components == ['test_func']
        assert failed_components == []


class TestBuildComponentsResume:
    """Test resume functionality in build_components"""
    
    @patch('factory_manager.ironclad.generate_candidate')
    @patch('factory_manager.ironclad.validate_candidate')
    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('os.makedirs')
    @patch('builtins.print')
    @patch('builtins.open', create=True)
    def test_resume_mode_existing_components(self, mock_open, mock_print, mock_makedirs, mock_listdir, mock_exists, mock_validate, mock_generate):
        """Test resume mode with existing components"""
        # Setup mocks - mock exists to return True for existing_func.py, False for new_func.py
        def exists_side_effect(path):
            if 'existing_func.py' in path:
                return True
            elif 'new_func.py' in path:
                return False
            else:
                return True  # For module directory
        
        mock_exists.side_effect = exists_side_effect
        mock_listdir.return_value = ['existing_func.py', '__init__.py']
        mock_generate.return_value = {
            'filename': 'new_func',
            'code': 'def new_func(): return "new"',
            'test': 'def test_new_func(): assert new_func() == "new"'
        }
        mock_validate.return_value = (True, "Tests passed")
        
        blueprint = {
            'module_name': 'test_module',
            'functions': [
                {
                    'name': 'existing_func',
                    'signature': 'def existing_func() -> str',
                    'description': 'Existing function'
                },
                {
                    'name': 'new_func',
                    'signature': 'def new_func() -> str',
                    'description': 'New function'
                }
            ]
        }
        
        # Execute with resume mode
        partial_success, module_dir, successful_components, failed_components, status_report = factory_manager.build_components(blueprint, "resume")
        
        # Assertions
        assert partial_success is True
        assert 'existing_func' in successful_components
        assert 'new_func' in successful_components
        assert len(failed_components) == 0
        # Should only generate new_func, not existing_func
        mock_generate.assert_called_once()


class TestMainValidation:
    """Test main.py validation and repair functions"""
    
    @patch('factory_manager.subprocess.run')
    def test_validate_main_candidate_success(self, mock_run):
        """Test successful main.py validation"""
        # Mock successful subprocess calls
        mock_run.side_effect = [
            MagicMock(returncode=0),  # Import test
            MagicMock(returncode=0)   # CLI test (only if argparse present)
        ]
        
        candidate_code = "def main(): pass\nimport argparse"
        components = ['test_func']
        module_dir = '/tmp/test'
        
        is_valid, logs = factory_manager.validate_main_candidate(candidate_code, components, module_dir)
        
        assert is_valid is True
        assert logs == "Valid"
        assert mock_run.call_count == 2
    
    def test_validate_main_candidate_empty_code(self):
        """Test validate_main_candidate with empty candidate code"""
        candidate_code = ""
        components = ['test_func']
        module_dir = '/tmp/test'
        
        is_valid, logs = factory_manager.validate_main_candidate(candidate_code, components, module_dir)
        
        assert is_valid is False
        assert logs == "No candidate code provided"
    
    @patch('factory_manager.subprocess.run')
    @patch('os.path.exists')
    @patch('shutil.copy')
    @patch('tempfile.TemporaryDirectory')
    @patch('builtins.open', create=True)
    def test_validate_main_candidate_copy_components(self, mock_open, mock_temp_dir, mock_copy, mock_exists, mock_run):
        """Test validate_main_candidate copies existing component files"""
        # Setup mocks
        mock_temp_dir.return_value.__enter__.return_value = '/tmp/test_temp'
        # Mock os.path.exists to return True only for component files
        mock_exists.side_effect = lambda path: path.endswith('.py') and 'test_func' in path or 'another_func' in path
        mock_run.side_effect = [
            MagicMock(returncode=0),  # Import test
            MagicMock(returncode=0)   # CLI test
        ]
        
        candidate_code = "def main(): pass\nimport argparse"
        components = ['test_func', 'another_func']
        module_dir = '/tmp/test'
        
        is_valid, logs = factory_manager.validate_main_candidate(candidate_code, components, module_dir)
        
        assert is_valid is True
        # Verify shutil.copy was called for component files (line 147)
        assert mock_copy.call_count >= 2  # At least called for each component
        mock_copy.assert_any_call('/tmp/test/test_func.py', '/tmp/test_temp')
        mock_copy.assert_any_call('/tmp/test/another_func.py', '/tmp/test_temp')
    
    @patch('factory_manager.subprocess.run')
    @patch('os.path.exists')
    @patch('shutil.copy')
    @patch('tempfile.TemporaryDirectory')
    @patch('builtins.open', create=True)
    def test_validate_main_candidate_import_errors(self, mock_open, mock_temp_dir, mock_copy, mock_exists, mock_run):
        """Test validate_main_candidate handles import errors"""
        # Setup mocks
        mock_temp_dir.return_value.__enter__.return_value = '/tmp/test_temp'
        mock_exists.return_value = False  # No component files exist
        mock_run.return_value = MagicMock(returncode=1, stderr="Import failed: module not found")
        
        candidate_code = "def main(): pass\nimport argparse"
        components = ['test_func']
        module_dir = '/tmp/test'
        
        is_valid, logs = factory_manager.validate_main_candidate(candidate_code, components, module_dir)
        
        assert is_valid is False
        # Verify import error was captured (line 163)
        assert "Import error: Import failed: module not found" in logs
    
    @patch('factory_manager.subprocess.run')
    @patch('os.path.exists')
    @patch('shutil.copy')
    @patch('tempfile.TemporaryDirectory')
    @patch('builtins.open', create=True)
    def test_validate_main_candidate_import_timeout(self, mock_open, mock_temp_dir, mock_copy, mock_exists, mock_run):
        """Test validate_main_candidate handles import timeout"""
        # Setup mocks
        mock_temp_dir.return_value.__enter__.return_value = '/tmp/test_temp'
        mock_exists.return_value = False
        mock_run.side_effect = subprocess.TimeoutExpired('cmd', 10)
        
        candidate_code = "def main(): pass"
        components = ['test_func']
        module_dir = '/tmp/test'
        
        is_valid, logs = factory_manager.validate_main_candidate(candidate_code, components, module_dir)
        
        assert is_valid is False
        # Verify timeout error was captured (line 165)
        assert "Import timeout" in logs
    
    @patch('factory_manager.subprocess.run')
    @patch('os.path.exists')
    @patch('shutil.copy')
    @patch('tempfile.TemporaryDirectory')
    @patch('builtins.open', create=True)
    def test_validate_main_candidate_import_exception(self, mock_open, mock_temp_dir, mock_copy, mock_exists, mock_run):
        """Test validate_main_candidate handles general import exceptions"""
        # Setup mocks
        mock_temp_dir.return_value.__enter__.return_value = '/tmp/test_temp'
        mock_exists.return_value = False
        mock_run.side_effect = Exception("General error")
        
        candidate_code = "def main(): pass"
        components = ['test_func']
        module_dir = '/tmp/test'
        
        is_valid, logs = factory_manager.validate_main_candidate(candidate_code, components, module_dir)
        
        assert is_valid is False
        # Verify general exception was captured (line 167)
        assert "Import test failed: General error" in logs
    
    @patch('factory_manager.subprocess.run')
    @patch('os.path.exists')
    @patch('shutil.copy')
    @patch('tempfile.TemporaryDirectory')
    @patch('builtins.open', create=True)
    def test_validate_main_candidate_cli_error(self, mock_open, mock_temp_dir, mock_copy, mock_exists, mock_run):
        """Test validate_main_candidate handles CLI test errors"""
        # Setup mocks
        mock_temp_dir.return_value.__enter__.return_value = '/tmp/test_temp'
        mock_exists.return_value = False
        mock_run.side_effect = [
            MagicMock(returncode=0),  # Import test succeeds
            MagicMock(returncode=2, stderr="Error: Invalid arguments")  # CLI test fails
        ]
        
        candidate_code = "def main(): pass\nimport argparse"
        components = ['test_func']
        module_dir = '/tmp/test'
        
        is_valid, logs = factory_manager.validate_main_candidate(candidate_code, components, module_dir)
        
        assert is_valid is False
        # Verify CLI error was captured (line 189)
        assert "CLI test failed: Error: Invalid arguments" in logs
    
    @patch('factory_manager.subprocess.run')
    @patch('os.path.exists')
    @patch('shutil.copy')
    @patch('tempfile.TemporaryDirectory')
    @patch('builtins.open', create=True)
    def test_validate_main_candidate_cli_exception(self, mock_open, mock_temp_dir, mock_copy, mock_exists, mock_run):
        """Test validate_main_candidate handles CLI test exceptions"""
        # Setup mocks
        mock_temp_dir.return_value.__enter__.return_value = '/tmp/test_temp'
        mock_exists.return_value = False
        mock_run.side_effect = [
            MagicMock(returncode=0),  # Import test succeeds
            Exception("CLI exception")  # CLI test throws exception
        ]
        
        candidate_code = "def main(): pass\nimport argparse"
        components = ['test_func']
        module_dir = '/tmp/test'
        
        is_valid, logs = factory_manager.validate_main_candidate(candidate_code, components, module_dir)
        
        assert is_valid is False
        # Verify CLI exception was captured (line 191)
        assert "CLI test error: CLI exception" in logs
    
    @patch('factory_manager.subprocess.run')
    def test_validate_main_candidate_syntax_error(self, mock_run):
        """Test main.py validation with syntax error"""
        candidate_code = "def main(: pass"  # Invalid syntax
        components = ['test_func']
        module_dir = '/tmp/test'
        
        is_valid, logs = factory_manager.validate_main_candidate(candidate_code, components, module_dir)
        
        assert is_valid is False
        assert "Syntax error" in logs
        mock_run.assert_not_called()
    
    @patch('factory_manager.ollama.chat')
    def test_repair_main_candidate(self, mock_chat):
        """Test main.py repair functionality"""
        mock_chat.return_value = {
            'message': {
                'content': 'def main(): pass  # Fixed'
            }
        }
        
        candidate_code = "def main(: pass"  # Broken code
        error_logs = "Syntax error: invalid syntax"
        components = ['test_func']
        module_dir = '/tmp/test'
        
        repaired_code = factory_manager.repair_main_candidate(candidate_code, error_logs, components, module_dir)
        
        assert "def main():" in repaired_code
        mock_chat.assert_called_once()
    
    @patch('factory_manager.ollama.chat')
    def test_generate_main_candidate(self, mock_chat):
        """Test main.py generation"""
        mock_chat.return_value = {
            'message': {
                'content': '{"filename": "main.py", "code": "def main(): pass"}'
            }
        }
        
        blueprint = {
            'module_name': 'test_module',
            'main_logic_description': 'Test main logic'
        }
        components = ['test_func']
        
        code = factory_manager.generate_main_candidate(blueprint, components)
        
        assert code == "def main(): pass"
        mock_chat.assert_called_once()


class TestNewlineHandlingIntegration:
    """Integration tests for newline handling in factory_manager"""
    
    @patch('factory_manager.ollama.chat')
    def test_main_candidate_with_escaped_newlines(self, mock_chat):
        """Test main candidate generation with escaped newlines"""
        # Mock response with escaped newlines
        mock_response = {
            'message': {
                'content': '''```json
                {
                    "filename": "main.py",
                    "code": "import sys\\nfrom utils import helper\\n\\ndef main():\\n    helper()\\n    print(\\"done\\")\\n\\nif __name__ == \\"__main__\\":\\n    main()"
                }
                ```'''
            }
        }
        mock_chat.return_value = mock_response
        
        blueprint = {
            'module_name': 'test_module',
            'main_logic_description': 'Test main logic'
        }
        components = ['helper']
        
        code = factory_manager.generate_main_candidate(blueprint, components)
        
        # Verify escaped newlines are converted to actual newlines
        assert '\n' in code
        assert '\\n' not in code
        assert 'import sys\nfrom utils import helper' in code
        assert 'print("done")' in code
        assert 'if __name__ == "__main__":\n    main()' in code
    
    @patch('factory_manager.ollama.chat')
    def test_repair_main_candidate_with_newlines(self, mock_chat):
        """Test main candidate repair with newline handling"""
        # Mock repair response
        mock_chat.return_value = {
            'message': {
                'content': 'def main():\\n    print(\\"fixed\\")\\n    return True'
            }
        }
        
        broken_code = 'def main():\\n    print("broken"\\n    return False'
        error_logs = 'Syntax error'
        components = ['helper']
        module_dir = '/tmp/test'
        
        repaired_code = factory_manager.repair_main_candidate(
            broken_code, error_logs, components, module_dir
        )
        
        # Verify newlines are properly handled
        assert '\n' in repaired_code
        assert '\\n' not in repaired_code
        assert 'print("fixed")' in repaired_code
    
    @patch('factory_manager.ironclad.validate_candidate')
    @patch('factory_manager.ironclad.generate_candidate')
    @patch('os.makedirs')
    @patch('builtins.open', create=True)
    @patch('builtins.print')
    def test_component_saving_with_cleaned_code(self, mock_print, mock_open, mock_makedirs, 
                                               mock_generate, mock_validate):
        """Test that components are saved with cleaned code"""
        # Mock candidate with escaped newlines
        mock_candidate = {
            'filename': 'test_func',
            'code': 'def test_func():\\n    print(\\"hello\\")\\n    return True',
            'test': 'def test():\\n    assert test_func() == True'
        }
        mock_generate.return_value = mock_candidate
        mock_validate.return_value = (True, "Tests passed")
        
        blueprint = {
            'module_name': 'test_module',
            'functions': [
                {
                    'name': 'test_func',
                    'signature': 'def test_func()',
                    'description': 'Test function'
                }
            ]
        }
        
        # Mock file writing
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        partial_success, module_dir, successful, failed, status = factory_manager.build_components(blueprint)
        
        # Verify file was written with cleaned code (actual newlines)
        mock_file.write.assert_called()
        written_code = mock_file.write.call_args[0][0]
        assert '\n' in written_code
        assert '\\n' not in written_code
        assert 'print("hello")' in written_code
        
        assert partial_success is True
        assert successful == ['test_func']
        assert failed == []


class TestCleanJsonFunction:
    """Test the enhanced clean_json function"""
    
    def test_clean_json_with_escaped_newlines(self):
        """Test clean_json function with escaped newlines"""
        json_text = '{"code": "def hello():\\n    print(\\"world\\")"}'
        result = factory_manager.clean_json(json_text)
        
        # Should be parseable JSON with decoded newlines
        parsed = json.loads(result)
        assert parsed['code'] == 'def hello():\n    print("world")'
    
    def test_clean_json_with_markdown_fences(self):
        """Test clean_json function with markdown fences"""
        json_text = '```json\n{"code": "line1\\\\nline2"}\n```'
        result = factory_manager.clean_json(json_text)
        
        parsed = json.loads(result)
        assert parsed['code'] == 'line1\nline2'
    
    def test_clean_json_with_nested_structure(self):
        """Test clean_json with nested structures containing escaped newlines"""
        json_text = '''{
            "functions": [
                {"name": "func1", "code": "def f1():\\n    pass"},
                {"name": "func2", "code": "def f2():\\n    return True"}
            ],
            "main": "main_code\\nwith newlines"
        }'''
        result = factory_manager.clean_json(json_text)
        
        parsed = json.loads(result)
        assert parsed['functions'][0]['code'] == 'def f1():\n    pass'
        assert parsed['functions'][1]['code'] == 'def f2():\n    return True'
        assert parsed['main'] == 'main_code\nwith newlines'