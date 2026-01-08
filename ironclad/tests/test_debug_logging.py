import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from ironclad_ai_guardrails.code_utils import is_debug_enabled, log_debug_raw


class TestDebugMode:
    """Test debug mode functionality"""
    
    def setup_method(self):
        """Clear IRONCLAD_DEBUG before each test"""
        if 'IRONCLAD_DEBUG' in os.environ:
            del os.environ['IRONCLAD_DEBUG']
    
    def teardown_method(self):
        """Clear IRONCLAD_DEBUG after each test"""
        if 'IRONCLAD_DEBUG' in os.environ:
            del os.environ['IRONCLAD_DEBUG']
    
    def test_is_debug_enabled_returns_false_by_default(self):
        """Test is_debug_enabled returns False when env var not set"""
        assert is_debug_enabled() is False
    
    def test_is_debug_enabled_returns_true_when_set(self):
        """Test is_debug_enabled returns True when env var is '1'"""
        os.environ['IRONCLAD_DEBUG'] = '1'
        try:
            assert is_debug_enabled() is True
        finally:
            del os.environ['IRONCLAD_DEBUG']
    
    def test_is_debug_enabled_returns_false_when_zero(self):
        """Test is_debug_enabled returns False when env var is '0'"""
        os.environ['IRONCLAD_DEBUG'] = '0'
        try:
            assert is_debug_enabled() is False
        finally:
            del os.environ['IRONCLAD_DEBUG']
    
    @patch('os.makedirs')
    @patch('builtins.open', create=True)
    def test_log_debug_raw_writes_file_when_enabled(self, mock_open, mock_makedirs):
        """Test log_debug_raw writes debug file when IRONCLAD_DEBUG=1"""
        os.environ['IRONCLAD_DEBUG'] = '1'
        try:
            log_debug_raw("generate", "test_func", 1, "gpt-oss:20b", "raw output", None)
            
            # Verify debug directory was created
            mock_makedirs.assert_called_once_with('build/.ironclad_debug', exist_ok=True)
            
            # Verify file was written with correct content
            assert mock_open.call_count >= 1
            write_call = mock_open.call_args
            filepath = write_call[0][0]
            content = write_call[0][1][0]
            
            assert filepath == 'build/.ironclad_debug/generate_test_func_attempt1_gpt-oss:20b.txt'
            assert 'Phase: generate' in content
            assert 'Component: test_func' in content
            assert 'Attempt: 1' in content
            assert 'Model: gpt-oss:20b' in content
            assert 'RAW OUTPUT:' in content
            assert 'raw output' in content
        finally:
            del os.environ['IRONCLAD_DEBUG']
    
    @patch('os.makedirs')
    @patch('builtins.open', create=True)
    def test_log_debug_raw_does_not_write_file_when_disabled(self, mock_open, mock_makedirs):
        """Test log_debug_raw does not write file when IRONCLAD_DEBUG is not '1'"""
        os.environ['IRONCLAD_DEBUG'] = '0'
        try:
            log_debug_raw("generate", "test_func", 1, "gpt-oss:20b", "raw output", None)
            
            # Verify debug directory was NOT created
            mock_makedirs.assert_not_called()
            
            # Verify file was NOT written
            mock_open.assert_not_called()
        finally:
            del os.environ['IRONCLAD_DEBUG']
    
    @patch('os.makedirs')
    @patch('builtins.open', create=True)
    def test_log_debug_raw_includes_error_when_provided(self, mock_open, mock_makedirs):
        """Test log_debug_raw includes error message when provided"""
        os.environ['IRONCLAD_DEBUG'] = '1'
        try:
            error_msg = "JSONDecodeError: Expecting value"
            log_debug_raw("generate", "test_func", 1, "gpt-oss:20b", "raw output", error_msg)
            
            # Verify error was included in file
            write_call = mock_open.call_args
            content = write_call[0][1][0]
            assert 'Error: JSONDecodeError: Expecting value' in content
        finally:
            del os.environ['IRONCLAD_DEBUG']
    
    @patch('os.makedirs')
    @patch('builtins.open', create=True)
    def test_log_debug_raw_handles_makedirs_exception_gracefully(self, mock_open, mock_makedirs):
        """Test log_debug_raw handles makedirs exceptions without crashing"""
        os.environ['IRONCLAD_DEBUG'] = '1'
        mock_makedirs.side_effect = Exception("Permission denied")
        
        try:
            # Should not crash even if makedirs fails
            log_debug_raw("generate", "test_func", 1, "gpt-oss:20b", "raw output", None)
        finally:
            del os.environ['IRONCLAD_DEBUG']
        
        # Should not crash, just silently fail
        assert True
    
    @patch('os.makedirs')
    @patch('builtins.open', create=True)
    def test_log_debug_raw_handles_open_exception_gracefully(self, mock_open, mock_makedirs):
        """Test log_debug_raw handles open exceptions without crashing"""
        os.environ['IRONCLAD_DEBUG'] = '1'
        mock_open.side_effect = Exception("Disk full")
        
        try:
            # Should not crash even if open fails
            log_debug_raw("generate", "test_func", 1, "gpt-oss:20b", "raw output", None)
        finally:
            del os.environ['IRONCLAD_DEBUG']
        
        # Should not crash, just silently fail
        assert True


class TestDebugIntegration:
    """Test debug logging integration with actual pipeline"""
    
    def setup_method(self):
        """Clear IRONCLAD_DEBUG and clean up debug dir before each test"""
        if 'IRONCLAD_DEBUG' in os.environ:
            del os.environ['IRONCLAD_DEBUG']
        if os.path.exists('build/.ironclad_debug'):
            shutil.rmtree('build/.ironclad_debug')
    
    def teardown_method(self):
        """Clean up debug dir and IRONCLAD_DEBUG after each test"""
        if 'IRONCLAD_DEBUG' in os.environ:
            del os.environ['IRONCLAD_DEBUG']
        if os.path.exists('build/.ironclad_debug'):
            shutil.rmtree('build/.ironclad_debug')
    
    @patch('ironclad_ai_guardrails.module_designer.ollama.chat')
    def test_module_designer_writes_debug_files(self, mock_chat):
        """Test module_designer writes debug files when IRONCLAD_DEBUG=1"""
        os.environ['IRONCLAD_DEBUG'] = '1'
        
        # Mock valid response
        mock_chat.return_value = {
            'message': {
                'content': '{"module_name": "test"}'
            }
        }
        
        try:
            from ironclad_ai_guardrails import module_designer
            blueprint = module_designer.draft_blueprint("test request")
            
            # Verify debug files were created
            assert os.path.exists('build/.ironclad_debug')
            debug_files = os.listdir('build/.ironclad_debug')
            assert len(debug_files) > 0
            
            # Verify at least one file contains 'architect' in name
            architect_files = [f for f in debug_files if 'architect' in f]
            assert len(architect_files) > 0
        finally:
            del os.environ['IRONCLAD_DEBUG']
    
    @patch('ironclad_ai_guardrails.ironclad.generate_candidate')
    def test_ironclad_generate_writes_debug_files(self, mock_generate):
        """Test ironclad generate writes debug files when IRONCLAD_DEBUG=1"""
        os.environ['IRONCLAD_DEBUG'] = '1'
        
        # Mock valid response
        mock_generate.return_value = {
            'filename': 'test_func',
            'code': 'def test_func(): pass',
            'test': 'def test_test_func(): pass'
        }
        
        try:
            from ironclad_ai_guardrails import ironclad
            result = ironclad.generate_candidate("test request")
            
            # Verify result
            assert result is not None
            assert result['filename'] == 'test_func'
            
            # Verify debug files were created
            assert os.path.exists('build/.ironclad_debug')
            debug_files = os.listdir('build/.ironclad_debug')
            generate_files = [f for f in debug_files if 'generate' in f and 'test_func' in f]
            assert len(generate_files) > 0
        finally:
            del os.environ['IRONCLAD_DEBUG']
    
    @patch('ironclad_ai_guardrails.ironclad.repair_candidate')
    def test_ironclad_repair_writes_debug_files(self, mock_repair):
        """Test ironclad repair writes debug files when IRONCLAD_DEBUG=1"""
        os.environ['IRONCLAD_DEBUG'] = '1'
        
        # Mock valid response
        mock_repair.return_value = {
            'filename': 'test_func',
            'code': 'def test_func(): return "fixed"',
            'test': 'def test_test_func(): assert test_func() == "fixed"'
        }
        
        try:
            from ironclad_ai_guardrails import ironclad
            result = ironclad.repair_candidate({
                'filename': 'test_func',
                'code': 'def test_func(): return "broken"',
                'test': 'def test_test_func(): assert test_func() == "broken"'
            }, 'Test failed')
            
            # Verify result
            assert result is not None
            
            # Verify debug files were created
            assert os.path.exists('build/.ironclad_debug')
            debug_files = os.listdir('build/.ironclad_debug')
            repair_files = [f for f in debug_files if 'repair' in f and 'test_func' in f]
            assert len(repair_files) > 0
        finally:
            del os.environ['IRONCLAD_DEBUG']
    
    @patch('ironclad_ai_guardrails.factory_manager.ollama.chat')
    @patch('ironclad_ai_guardrails.factory_manager.validate_main_candidate')
    @patch('os.makedirs')
    @patch('builtins.open', create=True)
    def test_assemble_main_writes_debug_files(self, mock_chat, mock_validate, mock_makedirs, mock_open):
        """Test assemble_main writes debug files when IRONCLAD_DEBUG=1"""
        os.environ['IRONCLAD_DEBUG'] = '1'
        
        # Mock successful generation and validation
        mock_chat.return_value = {
            'message': {
                'content': '{"filename": "main.py", "code": "def main(): pass"}'
            }
        }
        mock_validate.return_value = (True, "Valid")
        
        # Mock open for file writing
        mock_file_handle = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file_handle
        
        try:
            from ironclad_ai_guardrails import factory_manager
            blueprint = {
                'module_name': 'test_module',
                'main_logic_description': 'Test logic'
            }
            factory_manager.assemble_main(blueprint, '/tmp/test_module', ['func1', 'func2'])
            
            # Verify debug files were created
            assert os.path.exists('build/.ironclad_debug')
            debug_files = os.listdir('build/.ironclad_debug')
            assemble_files = [f for f in debug_files if 'assemble' in f and 'main' in f]
            assert len(assemble_files) > 0
        finally:
            del os.environ['IRONCLAD_DEBUG']
    
    def test_no_debug_files_when_debug_disabled(self):
        """Test no debug files are created when IRONCLAD_DEBUG is not '1'"""
        # Ensure debug dir doesn't exist
        if os.path.exists('build/.ironclad_debug'):
            shutil.rmtree('build/.ironclad_debug')
        
        from ironclad_ai_guardrails import module_designer
        module_designer.draft_blueprint("test request")
        
        # Verify no debug files were created
        assert not os.path.exists('build/.ironclad_debug')
