import pytest
import json
import os
import sys
import tempfile
import subprocess
from unittest.mock import patch, MagicMock, mock_open

import ironclad_ai_guardrails.factory_manager as factory_manager
import ironclad_ai_guardrails.code_utils as code_utils


class TestBuildComponents:
    """Test the build_components function"""
    
    @patch('ironclad_ai_guardrails.ironclad.generate_candidate')
    @patch('ironclad_ai_guardrails.ironclad.validate_candidate')
    @patch('ironclad_ai_guardrails.ironclad.repair_candidate')
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
        mock_validate.return_value = (True, "Component is valid")
        
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
        
        # Verify existing directory was removed and recreated (FAILURE MODE A fix)
        mock_rmtree.assert_called_once()
        mock_makedirs.assert_called_once()  # Should be called after rmtree
    
    @patch('ironclad_ai_guardrails.ironclad.generate_candidate')
    @patch('ironclad_ai_guardrails.ironclad.validate_candidate')
    @patch('ironclad_ai_guardrails.ironclad.repair_candidate')
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
    
    @patch('ironclad_ai_guardrails.ironclad.generate_candidate')
    @patch('ironclad_ai_guardrails.ironclad.validate_candidate')
    @patch('ironclad_ai_guardrails.ironclad.repair_candidate')
    @patch('os.makedirs')
    @patch('builtins.print')
    @patch('builtins.open', create=True)
    def test_build_components_max_retries_exceeded(self, mock_open, mock_print, mock_makedirs, mock_repair, mock_validate, mock_generate):
        """Test component building when max retries exceeded"""
        # Setup mocks - validation always fails, but repair returns a candidate (not None)
        mock_generate.return_value = {
            'filename': 'broken_func',
            'code': 'def broken_func(): return "broken"',
            'test': 'def test_broken_func(): assert broken_func() == "test"'
        }
        mock_validate.side_effect = [
            (False, "Test failed"),  # Initial attempt
            (False, "Test failed"),  # After first repair
            (False, "Test failed")    # After second repair
        ]
        # Return candidates (not None) so validation continues
        mock_repair.side_effect = [
            {'filename': 'broken_func', 'code': 'def broken_func(): return "broken"', 'test': 'def test_broken_func(): assert broken_func() == "test"'},
            {'filename': 'broken_func', 'code': 'def broken_func(): return "broken"', 'test': 'def test_broken_func(): assert broken_func() == "test"'}
        ]
        
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
    
    @patch('ironclad_ai_guardrails.factory_manager.validate_main_candidate')
    @patch('ironclad_ai_guardrails.factory_manager.generate_main_candidate')
    @patch('ironclad_ai_guardrails.factory_manager.ollama.chat')
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
    
    @patch('ironclad_ai_guardrails.factory_manager.ollama.chat')
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
    
    @patch('ironclad_ai_guardrails.factory_manager.validate_main_candidate')
    @patch('ironclad_ai_guardrails.factory_manager.generate_main_candidate')
    @patch('ironclad_ai_guardrails.ironclad.generate_candidate')
    @patch('ironclad_ai_guardrails.ironclad.validate_candidate')
    @patch('ironclad_ai_guardrails.factory_manager.repair_main_candidate')
    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('os.path.join')
    @patch('builtins.open', create=True)
    @patch('builtins.print')
    @patch('ironclad_ai_guardrails.factory_manager.ollama.chat')
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
        with patch('ironclad_ai_guardrails.factory_manager.ollama.chat') as mock_chat:
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
    
    @patch('ironclad_ai_guardrails.ironclad.generate_candidate')
    @patch('ironclad_ai_guardrails.ironclad.validate_candidate')
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
    
    @patch('ironclad_ai_guardrails.factory_manager.subprocess.run')
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
    
    @patch('ironclad_ai_guardrails.factory_manager.subprocess.run')
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
    
    @patch('ironclad_ai_guardrails.factory_manager.subprocess.run')
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
    
    @patch('ironclad_ai_guardrails.factory_manager.subprocess.run')
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
    
    @patch('ironclad_ai_guardrails.factory_manager.subprocess.run')
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
    
    @patch('ironclad_ai_guardrails.factory_manager.subprocess.run')
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
    
    @patch('ironclad_ai_guardrails.factory_manager.subprocess.run')
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
    
    @patch('ironclad_ai_guardrails.factory_manager.subprocess.run')
    def test_validate_main_candidate_syntax_error(self, mock_run):
        """Test main.py validation with syntax error"""
        candidate_code = "def main(: pass"  # Invalid syntax
        components = ['test_func']
        module_dir = '/tmp/test'
        
        is_valid, logs = factory_manager.validate_main_candidate(candidate_code, components, module_dir)
        
        assert is_valid is False
        assert "Syntax error" in logs
        mock_run.assert_not_called()
    
    @patch('ironclad_ai_guardrails.factory_manager.ollama.chat')
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
    
    @patch('ironclad_ai_guardrails.factory_manager.ollama.chat')
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
    
    @patch('ironclad_ai_guardrails.factory_manager.ollama.chat')
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
    
    @patch('ironclad_ai_guardrails.factory_manager.ollama.chat')
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
    
    @patch('ironclad_ai_guardrails.ironclad.validate_candidate')
    @patch('ironclad_ai_guardrails.ironclad.generate_candidate')
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


class TestBuildComponentsGenerationFailure:
    """Test build_components when generation returns None (lines 69-72)"""
    
    @patch('ironclad_ai_guardrails.ironclad.generate_candidate')
    @patch('os.makedirs')
    @patch('builtins.print')
    @patch('builtins.open', create=True)
    def test_build_components_generation_returns_none(self, mock_open, mock_print, mock_makedirs, mock_generate):
        """Test when generate_candidate returns None (lines 69-72)"""
        # Setup mock - generate returns None (failure)
        mock_generate.return_value = None
        
        blueprint = {
            'module_name': 'test_module',
            'functions': [
                {
                    'name': 'failed_func',
                    'signature': 'def failed_func()',
                    'description': 'A function that fails to generate'
                }
            ]
        }
        
        # Execute
        partial_success, module_dir, successful_components, failed_components, status_report = factory_manager.build_components(blueprint)
        
        # Assertions
        assert partial_success is False
        assert successful_components == []
        assert failed_components == ['failed_func']
        assert status_report['failed_func'] == "Generation failed"
        mock_generate.assert_called_once()


class TestAssembleMainRepairAndFailure:
    """Test assemble_main repair and failure paths (lines 247-251, 259)"""
    
    @patch('ironclad_ai_guardrails.factory_manager.validate_main_candidate')
    @patch('ironclad_ai_guardrails.factory_manager.generate_main_candidate')
    @patch('ironclad_ai_guardrails.factory_manager.ollama.chat')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    @patch('builtins.print')
    def test_assemble_main_with_repairs(self, mock_print, mock_makedirs, mock_file, mock_chat, mock_generate, mock_validate):
        """Test assemble_main requiring repairs (lines 247-251)"""
        # Setup mocks - validation fails first two times
        mock_generate.return_value = 'def main(): print("Hello")'
        mock_validate.side_effect = [
            (False, "Syntax error"),
            (False, "Import error"),
            (True, "Valid")
        ]
        mock_chat.return_value = {
            'message': {
                'content': '{"code": "def main(): print(\"Hello\")"}'
            }
        }
        
        blueprint = {
            'module_name': 'test_module',
            'main_logic_description': 'Print Hello'
        }
        module_dir = '/tmp/test_module'
        components = ['func1']
        
        # Execute
        factory_manager.assemble_main(blueprint, module_dir, components)
        
        # Assertions
        assert mock_validate.call_count == 3  # Initial + 2 repairs
        mock_file.assert_called()  # File should be written
        mock_file.assert_any_call(os.path.join(module_dir, "main.py"), "w")
        mock_file.assert_any_call(os.path.join(module_dir, "__init__.py"), "w")
    
    @patch('ironclad_ai_guardrails.factory_manager.validate_main_candidate')
    @patch('ironclad_ai_guardrails.factory_manager.generate_main_candidate')
    @patch('ironclad_ai_guardrails.factory_manager.ollama.chat')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    @patch('builtins.print')
    def test_assemble_main_max_retries_exceeded(self, mock_print, mock_makedirs, mock_file, mock_chat, mock_generate, mock_validate):
        """Test assemble_main failing after max retries (line 259)"""
        # Setup mocks - validation always fails
        mock_generate.return_value = 'def main(): print("Hello")'
        mock_validate.return_value = (False, "Persistent error")
        mock_chat.return_value = {
            'message': {
                'content': '{"code": "def main(): print(\"Hello\")"}'
            }
        }
        
        blueprint = {
            'module_name': 'test_module',
            'main_logic_description': 'Print Hello'
        }
        module_dir = '/tmp/test_module'
        components = ['func1']
        
        # Execute - should raise exception after 3 attempts
        with pytest.raises(Exception) as exc_info:
            factory_manager.assemble_main(blueprint, module_dir, components)
        
        assert "Failed to generate valid main.py after 3 attempts" in str(exc_info.value)
        assert mock_validate.call_count == 3


class TestRunFactoryManagerWorkflow:
    """Test run_factory_manager_workflow function (lines 276-298)"""
    
    @patch('ironclad_ai_guardrails.factory_manager.assemble_main')
    @patch('ironclad_ai_guardrails.factory_manager.build_components')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    @patch('builtins.print')
    @patch('sys.exit')
    def test_run_workflow_no_blueprint_file(self, mock_exit, mock_print, mock_json_load, mock_file, mock_exists, mock_build, mock_assemble):
        """Test workflow when blueprint.json doesn't exist (lines 276-279)"""
        # Setup mocks
        mock_exists.return_value = False  # blueprint.json doesn't exist
        
        # Execute
        factory_manager.run_factory_manager_workflow()
        
        # Assertions
        mock_print.assert_called_with("Run module_designer.py first!")
        mock_exit.assert_called_once_with(1)
        mock_build.assert_not_called()
    
    @patch('ironclad_ai_guardrails.factory_manager.assemble_main')
    @patch('ironclad_ai_guardrails.factory_manager.build_components')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    @patch('builtins.print')
    @patch('sys.exit')
    def test_run_workflow_partial_success_with_failures(self, mock_exit, mock_print, mock_json_load, mock_file, mock_exists, mock_build, mock_assemble):
        """Test workflow with partial success and some failures (lines 290-293)"""
        # Setup mocks
        mock_exists.side_effect = [True, False]  # blueprint.json exists, module dir doesn't
        mock_json_load.return_value = {
            'module_name': 'test_module',
            'main_logic_description': 'Test'
        }
        mock_build.return_value = (
            True,  # partial_success
            '/tmp/test_module',
            ['func1', 'func2'],  # successful_components
            ['func3'],  # failed_components
            {'func1': 'success', 'func2': 'success', 'func3': 'failed'}  # status_report
        )
        
        # Execute
        factory_manager.run_factory_manager_workflow()
        
        # Assertions
        mock_assemble.assert_called_once()
        mock_print.assert_any_call(f"\n[⚠️]  Module completed with {len(['func3'])} failed components:")
        mock_print.assert_any_call(f"     [❌] func3")
        mock_exit.assert_not_called()
    
    @patch('ironclad_ai_guardrails.factory_manager.assemble_main')
    @patch('ironclad_ai_guardrails.factory_manager.build_components')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    @patch('builtins.print')
    @patch('sys.exit')
    def test_run_workflow_all_components_failed(self, mock_exit, mock_print, mock_json_load, mock_file, mock_exists, mock_build, mock_assemble):
        """Test workflow when no components could be built (lines 297-298)"""
        # Setup mocks
        mock_exists.side_effect = [True, False]
        mock_json_load.return_value = {
            'module_name': 'test_module',
            'main_logic_description': 'Test'
        }
        mock_build.return_value = (
            False,  # partial_success=False
            '/tmp/test_module',
            [],  # no successful components
            ['func1', 'func2'],  # all failed
            {'func1': 'failed', 'func2': 'failed'}  # status_report
        )
        
        # Execute
        factory_manager.run_factory_manager_workflow()
        
        # Assertions
        mock_assemble.assert_not_called()  # Don't assemble if no success
        mock_print.assert_called_with("\n[❌] No components could be built successfully.")
        mock_exit.assert_called_once_with(1)
    
    @patch('ironclad_ai_guardrails.factory_manager.assemble_main')
    @patch('ironclad_ai_guardrails.factory_manager.build_components')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    @patch('builtins.print')
    @patch('sys.exit')
    def test_run_workflow_all_successful_no_failures(self, mock_exit, mock_print, mock_json_load, mock_file, mock_exists, mock_build, mock_assemble):
        """Test workflow when all components successful with no failures (to cover line 295)"""
        # Setup mocks
        mock_exists.side_effect = [True, False]
        mock_json_load.return_value = {
            'module_name': 'test_module',
            'main_logic_description': 'Test'
        }
        mock_build.return_value = (
            True,  # partial_success
            '/tmp/test_module',
            ['func1', 'func2'],  # successful_components
            [],  # NO failed_components
            {'func1': 'success', 'func2': 'success'}  # status_report
        )
        
        # Execute
        factory_manager.run_factory_manager_workflow()
        
        # Assertions
        mock_assemble.assert_called_once()
        mock_print.assert_called_with("\n[✅] All 2 components built successfully!")


class TestBuildComponentsDirectoryInvariant:
    """Test directory invariant in build_components (FAILURE MODE A)"""
    
    @patch('ironclad_ai_guardrails.ironclad.generate_candidate')
    @patch('ironclad_ai_guardrails.ironclad.validate_candidate')
    @patch('os.makedirs')
    @patch('shutil.rmtree')
    @patch('os.path.exists')
    @patch('builtins.print')
    @patch('builtins.open', create=True)
    def test_smart_mode_recreates_directory(self, mock_open, mock_print, mock_exists, mock_rmtree, mock_makedirs, mock_validate, mock_generate):
        """Test that smart mode recreates directory after deletion (FAILURE MODE A fix)"""
        # Setup mocks - directory exists, gets deleted, then recreated
        mock_exists.return_value = True
        mock_generate.return_value = {
            'filename': 'test_func',
            'code': 'def test_func(): return "success"',
            'test': 'def test_test_func(): assert test_func() == "success"'
        }
        mock_validate.return_value = (True, "Tests passed")
        
        blueprint = {
            'module_name': 'test_module',
            'functions': [
                {'name': 'test_func', 'signature': 'def test_func()', 'description': 'Test function'}
            ]
        }
        
        # Execute in smart mode
        factory_manager.build_components(blueprint, "smart")
        
        # Verify directory was deleted and then recreated
        mock_rmtree.assert_called_once()
        mock_makedirs.assert_called_once()  # NEW: Should be called after rmtree
    
    @patch('ironclad_ai_guardrails.ironclad.generate_candidate')
    @patch('ironclad_ai_guardrails.ironclad.validate_candidate')
    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('os.makedirs')
    @patch('builtins.print')
    @patch('builtins.open', create=True)
    def test_resume_mode_preserves_directory(self, mock_open, mock_print, mock_makedirs, mock_listdir, mock_exists, mock_validate, mock_generate):
        """Test that resume mode does NOT delete directory (FAILURE MODE A prevention)"""
        # Setup mocks - directory exists but not deleted in resume mode
        def exists_side_effect(path):
            if 'existing_func.py' in path:
                return True
            return True  # Directory exists
        
        mock_exists.side_effect = exists_side_effect
        mock_listdir.return_value = ['existing_func.py', '__init__.py']
        mock_generate.return_value = {
            'filename': 'test_func',
            'code': 'def test_func(): return "success"',
            'test': 'def test_test_func(): assert test_func() == "success"'
        }
        mock_validate.return_value = (True, "Tests passed")
        
        blueprint = {
            'module_name': 'test_module',
            'functions': [
                {'name': 'existing_func', 'signature': 'def existing_func()', 'description': 'Existing function'}
            ]
        }
        
        # Execute in resume mode
        factory_manager.build_components(blueprint, "resume")
        
        # Verify directory was NOT deleted
        assert not any('rmtree' in str(call) for call in mock_makedirs.call_args_list)
        # Verify makedirs was NOT called (directory preserved)
        mock_makedirs.assert_not_called()


class TestBuildComponentsRepairSafety:
    """Test repair safety in build_components (FAILURE MODE B)"""
    
    @patch('ironclad_ai_guardrails.ironclad.generate_candidate')
    @patch('ironclad_ai_guardrails.ironclad.validate_candidate')
    @patch('ironclad_ai_guardrails.ironclad.repair_candidate')
    @patch('os.makedirs')
    @patch('builtins.print')
    @patch('builtins.open', create=True)
    def test_repair_returns_none_is_handled(self, mock_open, mock_print, mock_makedirs, mock_repair, mock_validate, mock_generate):
        """Test that repair returning None is handled gracefully (FAILURE MODE B fix)"""
        # Setup mocks - repair returns None (simulating failure mode B)
        mock_generate.return_value = {
            'filename': 'broken_func',
            'code': 'def broken_func(): return "broken"',
            'test': 'def test_broken_func(): assert broken_func() == "test"'
        }
        mock_validate.return_value = (False, "Test failed")  # Initial validation fails
        mock_repair.return_value = None  # Repair returns None
        
        blueprint = {
            'module_name': 'test_module',
            'functions': [
                {'name': 'broken_func', 'signature': 'def broken_func()', 'description': 'Broken function'}
            ]
        }
        
        # Execute - should NOT crash, should mark as failed
        partial_success, module_dir, successful_components, failed_components, status_report = factory_manager.build_components(blueprint)
        
        # Assertions
        assert partial_success is False
        assert successful_components == []
        assert failed_components == ['broken_func']
        # Handle both formats: string "Generation failed" or dict with status
        if isinstance(status_report['broken_func'], str):
            assert status_report['broken_func'] == "Generation failed"
        else:
            assert status_report['broken_func']['status'] == 'failed'
            # attempts is 0 because repair returns None before increment
            assert status_report['broken_func']['attempts'] == 0
        # Verify validate was called once before repair failed
        assert mock_validate.call_count == 1
    
    @patch('ironclad_ai_guardrails.ironclad.generate_candidate')
    @patch('ironclad_ai_guardrails.ironclad.validate_candidate')
    @patch('ironclad_ai_guardrails.ironclad.repair_candidate')
    @patch('os.makedirs')
    @patch('builtins.print')
    @patch('builtins.open', create=True)
    def test_validation_with_none_candidate_is_handled(self, mock_open, mock_print, mock_makedirs, mock_repair, mock_validate, mock_generate):
        """Test that None candidate before validation is handled (FAILURE MODE B fix)"""
        # Setup mocks - initial candidate is None
        mock_generate.return_value = None  # Generation fails
        
        blueprint = {
            'module_name': 'test_module',
            'functions': [
                {'name': 'failed_func', 'signature': 'def failed_func()', 'description': 'Failed function'}
            ]
        }
        
        # Execute - should NOT pass None to validate
        partial_success, module_dir, successful_components, failed_components, status_report = factory_manager.build_components(blueprint)
        
        # Assertions
        assert partial_success is False
        assert successful_components == []
        assert failed_components == ['failed_func']
        assert status_report['failed_func'] == "Generation failed"
        # Validate should NOT have been called since candidate is None
        mock_validate.assert_not_called()
    
    @patch('ironclad_ai_guardrails.ironclad.generate_candidate')
    @patch('ironclad_ai_guardrails.ironclad.validate_candidate')
    @patch('ironclad_ai_guardrails.ironclad.repair_candidate')
    @patch('os.makedirs')
    @patch('builtins.print')
    @patch('builtins.open', create=True)
    def test_partial_success_with_mixed_components(self, mock_open, mock_print, mock_makedirs, mock_repair, mock_validate, mock_generate):
        """Test partial success with some components failing due to None repair"""
        # Setup mocks - first function succeeds, second fails with None repair
        def generate_side_effect(*args, **kwargs):
            func_name = args[2] if len(args) > 2 else ''
            if func_name == 'success_func':
                return {
                    'filename': 'success_func',
                    'code': 'def success_func(): return "success"',
                    'test': 'def test_success_func(): assert success_func() == "success"'
                }
            else:
                return {
                    'filename': 'failed_func',
                    'code': 'def failed_func(): return "broken"',
                    'test': 'def test_failed_func(): assert failed_func() == "test"'
                }
        
        mock_generate.side_effect = generate_side_effect
        mock_validate.side_effect = [
            (True, "Tests passed"),  # First function passes
            (False, "Test failed"),  # Second function fails
            (False, "Test failed"),
            (False, "Test failed")
        ]
        mock_repair.return_value = None  # Second function's repair fails
        
        blueprint = {
            'module_name': 'test_module',
            'functions': [
                {'name': 'success_func', 'signature': 'def success_func()', 'description': 'Success function'},
                {'name': 'failed_func', 'signature': 'def failed_func()', 'description': 'Failed function'}
            ]
        }
        
        # Execute
        partial_success, module_dir, successful_components, failed_components, status_report = factory_manager.build_components(blueprint)
        
        # Assertions
        assert partial_success is True  # Partial success
        assert 'success_func' in successful_components
        assert 'failed_func' in failed_components
        assert status_report['success_func']['status'] == 'success'
        assert status_report['failed_func']['status'] == 'failed'
