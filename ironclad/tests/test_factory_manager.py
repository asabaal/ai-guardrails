import pytest
import json
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock, mock_open

# Add src to path for importing
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
import factory_manager


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
        success, module_dir, verified_files = factory_manager.build_components(blueprint)
        
        # Assertions
        assert success is True
        assert 'test_module' in module_dir
        assert verified_files == ['test_func']
        mock_makedirs.assert_called_once()
        mock_generate.assert_called_once()
        mock_validate.assert_called_once()
        mock_repair.assert_not_called()  # Should not need repair
    
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
        success, module_dir, verified_files = factory_manager.build_components(blueprint)
        
        # Assertions
        assert success is True
        assert 'test_module' in module_dir
        assert verified_files == ['broken_func']
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
        success, module_dir, verified_files = factory_manager.build_components(blueprint)
        
        # Assertions
        assert success is False
        assert 'test_module' in module_dir
        assert verified_files == []
        mock_generate.assert_called_once()
        assert mock_validate.call_count == 3  # Called 3 times (initial + 2 repairs)
        assert mock_repair.call_count == 2  # Called 2 times


class TestAssembleMain:
    """Test the assemble_main function"""
    
    @patch('factory_manager.ollama.chat')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    @patch('builtins.print')
    def test_assemble_main_success(self, mock_print, mock_makedirs, mock_file, mock_chat):
        """Test successful main assembly"""
        # Setup mock
        mock_chat.return_value = {
            'message': {
                'content': '{"filename": "main.py", "code": "def main(): print(\\"Hello World\\")"}'
            }
        }
        
        blueprint = {
            'module_name': 'test_module',
            'main_logic_description': 'Print Hello World'
        }
        module_dir = '/tmp/test_module'
        components = ['func1', 'func2']
        
        # Execute
        factory_manager.assemble_main(blueprint, module_dir, components)
        
        # Assertions
        mock_chat.assert_called_once()
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


class TestFactoryManagerIntegration:
    """Integration tests for factory manager workflow"""
    
    @patch('factory_manager.ironclad.generate_candidate')
    @patch('factory_manager.ironclad.validate_candidate')
    @patch('factory_manager.ironclad.repair_candidate')
    @patch('factory_manager.os.makedirs')
    @patch('factory_manager.os.path.exists')
    @patch('factory_manager.os.path.join')
    @patch('builtins.open')
    @patch('builtins.print')
    @patch('factory_manager.ollama.chat')
    def test_full_workflow_integration(self, mock_chat, mock_print, mock_open, mock_join, mock_exists, mock_makedirs, mock_repair, mock_validate, mock_generate):
        """Test complete workflow from blueprint to assembled module"""
        # Setup mocks
        mock_generate.return_value = {
            'filename': 'test_func',
            'code': 'def test_func(): return "success"',
            'test': 'def test_test_func(): assert test_func() == "success"'
        }
        mock_validate.return_value = (True, "Tests passed")
        mock_chat.return_value = {
            'message': {
                'content': '{"filename": "main.py", "code": "def main(): test_func()"}'
            }
        }
        mock_exists.return_value = True  # blueprint.json exists
        
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
            
            success, directory, components = factory_manager.build_components(blueprint)
            
            if success:
                factory_manager.assemble_main(blueprint, directory, components)
        
        # Verify workflow completed
        assert success is True
        assert 'integration_test' in directory
        assert components == ['test_func']