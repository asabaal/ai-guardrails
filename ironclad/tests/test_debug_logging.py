import os
import tempfile
import shutil
import pytest
from io import StringIO
from unittest.mock import patch

from ironclad_ai_guardrails.code_utils import is_debug_enabled, log_debug_raw


class TestDebugAPIPresence:
    """Test that the required API functions exist"""
    
    def test_is_debug_enabled_exists(self):
        """Test is_debug_enabled function exists and is callable"""
        assert callable(is_debug_enabled)
        assert is_debug_enabled() is not None
        
    def test_log_debug_raw_exists(self):
        """Test log_debug_raw function exists and is callable"""
        assert callable(log_debug_raw)


class TestDebugDisabledBehavior:
    """Test behavior when debug mode is disabled"""
    
    def setup_method(self):
        """Clear IRONCLAD_DEBUG before each test"""
        if 'IRONCLAD_DEBUG' in os.environ:
            del os.environ['IRONCLAD_DEBUG']
    
    def teardown_method(self):
        """Clear IRONCLAD_DEBUG after each test"""
        if 'IRONCLAD_DEBUG' in os.environ:
            del os.environ['IRONCLAD_DEBUG']
    
    def test_is_debug_enabled_returns_false_when_not_set(self):
        """Test is_debug_enabled returns False when env var not set"""
        assert is_debug_enabled() is False
    
    def test_is_debug_enabled_returns_false_when_zero(self):
        """Test is_debug_enabled returns False when env var is '0'"""
        os.environ['IRONCLAD_DEBUG'] = '0'
        assert is_debug_enabled() is False
    
    def test_is_debug_enabled_returns_false_when_any_other_value(self):
        """Test is_debug_enabled returns False for non-'1' values"""
        for value in ['true', 'yes', 'enabled', '2', '']:
            os.environ['IRONCLAD_DEBUG'] = value
            assert is_debug_enabled() is False
    
    def test_log_debug_raw_no_op_when_disabled(self):
        """Test log_debug_raw is a no-op when debug is disabled"""
        with patch('os.makedirs') as mock_makedirs:
            with patch('builtins.open', create=True) as mock_open:
                log_debug_raw(
                    phase='test_phase',
                    message='test message',
                    data='test data',
                    component='test_component',
                    attempt=1
                )
                mock_makedirs.assert_not_called()
                mock_open.assert_not_called()
    
    def test_log_debug_raw_no_exception_when_disabled(self):
        """Test log_debug_raw never raises exceptions when disabled"""
        try:
            log_debug_raw(
                phase='test_phase',
                message='test message',
                data='test data',
                component='test_component',
                attempt=1
            )
        except Exception as e:
            pytest.fail(f"log_debug_raw raised exception: {e}")
    
    def test_log_debug_raw_does_not_create_files_when_disabled(self, tmp_path):
        """Test no files are created when debug is disabled"""
        os.chdir(tmp_path)
        log_debug_raw(
            phase='test_phase',
            message='test message',
            data='test data',
            component='test_component',
            attempt=1
        )
        debug_dir = tmp_path / 'build' / '.ironclad_debug'
        assert not debug_dir.exists()


class TestDebugEnabledBehavior:
    """Test behavior when debug mode is enabled"""
    
    def setup_method(self):
        """Enable debug mode before each test"""
        os.environ['IRONCLAD_DEBUG'] = '1'
    
    def teardown_method(self):
        """Disable debug mode and cleanup after each test"""
        if 'IRONCLAD_DEBUG' in os.environ:
            del os.environ['IRONCLAD_DEBUG']
        if os.path.exists('build/.ironclad_debug'):
            shutil.rmtree('build')
    
    def test_is_debug_enabled_returns_true_when_set_to_one(self):
        """Test is_debug_enabled returns True when IRONCLAD_DEBUG=1"""
        assert is_debug_enabled() is True
    
    def test_log_debug_raw_creates_debug_directory(self, tmp_path):
        """Test log_debug_raw creates debug directory"""
        os.chdir(tmp_path)
        log_debug_raw(
            phase='test_phase',
            message='test message'
        )
        debug_dir = tmp_path / 'build' / '.ironclad_debug'
        assert debug_dir.exists()
        assert debug_dir.is_dir()
    
    def test_log_debug_raw_creates_file_with_phase_only(self, tmp_path):
        """Test file creation with only phase parameter"""
        os.chdir(tmp_path)
        log_debug_raw(
            phase='generate',
            message='test message',
            data='raw data content'
        )
        
        filepath = tmp_path / 'build' / '.ironclad_debug' / 'generate.txt'
        assert filepath.exists()
        
        content = filepath.read_text()
        assert 'Phase: generate' in content
        assert 'Message: test message' in content
        assert 'RAW DATA:' in content
        assert 'raw data content' in content
    
    def test_log_debug_raw_creates_file_with_component(self, tmp_path):
        """Test file creation with phase and component"""
        os.chdir(tmp_path)
        log_debug_raw(
            phase='generate',
            message='test message',
            data='raw data',
            component='test_func'
        )
        
        filepath = tmp_path / 'build' / '.ironclad_debug' / 'generate_test_func.txt'
        assert filepath.exists()
        
        content = filepath.read_text()
        assert 'Phase: generate' in content
        assert 'Component: test_func' in content
        assert 'Message: test message' in content
        assert 'RAW DATA:' in content
    
    def test_log_debug_raw_creates_file_with_attempt(self, tmp_path):
        """Test file creation with phase and attempt"""
        os.chdir(tmp_path)
        log_debug_raw(
            phase='generate',
            message='test message',
            data='raw data',
            attempt=3
        )
        
        filepath = tmp_path / 'build' / '.ironclad_debug' / 'generate_attempt3.txt'
        assert filepath.exists()
        
        content = filepath.read_text()
        assert 'Phase: generate' in content
        assert 'Attempt: 3' in content
    
    def test_log_debug_raw_creates_file_with_all_parameters(self, tmp_path):
        """Test file creation with all parameters"""
        os.chdir(tmp_path)
        log_debug_raw(
            phase='generate',
            message='test message',
            data='raw data content\nmultiple lines',
            component='test_func',
            attempt=2
        )
        
        filepath = tmp_path / 'build' / '.ironclad_debug' / 'generate_test_func_attempt2.txt'
        assert filepath.exists()
        
        content = filepath.read_text()
        assert 'Phase: generate' in content
        assert 'Component: test_func' in content
        assert 'Attempt: 2' in content
        assert 'Message: test message' in content
        assert 'RAW DATA:' in content
        assert 'raw data content' in content
        assert 'multiple lines' in content
    
    def test_log_debug_raw_without_data(self, tmp_path):
        """Test file creation without data parameter"""
        os.chdir(tmp_path)
        log_debug_raw(
            phase='test_phase',
            message='test message',
            component='test_component'
        )
        
        filepath = tmp_path / 'build' / '.ironclad_debug' / 'test_phase_test_component.txt'
        assert filepath.exists()
        
        content = filepath.read_text()
        assert 'Phase: test_phase' in content
        assert 'Component: test_component' in content
        assert 'Message: test message' in content
        assert 'RAW DATA:' not in content
    
    def test_log_debug_raw_directory_idempotent(self, tmp_path):
        """Test debug directory creation is idempotent"""
        os.chdir(tmp_path)
        log_debug_raw(phase='test1', message='msg1')
        log_debug_raw(phase='test2', message='msg2')
        log_debug_raw(phase='test3', message='msg3')
        
        debug_dir = tmp_path / 'build' / '.ironclad_debug'
        assert debug_dir.exists()
        assert len(list(debug_dir.glob('*.txt'))) == 3


class TestDebugLoggingRobustness:
    """Test robustness and error handling"""
    
    def setup_method(self):
        """Enable debug mode before each test"""
        os.environ['IRONCLAD_DEBUG'] = '1'
    
    def teardown_method(self):
        """Disable debug mode and cleanup after each test"""
        if 'IRONCLAD_DEBUG' in os.environ:
            del os.environ['IRONCLAD_DEBUG']
        if os.path.exists('build/.ironclad_debug'):
            shutil.rmtree('build')
    
    def test_log_debug_raw_handles_makedirs_exception(self):
        """Test log_debug_raw handles makedirs exceptions gracefully"""
        with patch('os.makedirs') as mock_makedirs:
            mock_makedirs.side_effect = Exception("Permission denied")
            
            try:
                log_debug_raw(phase='test', message='msg', data='data')
            except Exception:
                pytest.fail("log_debug_raw raised exception on makedirs failure")
    
    def test_log_debug_raw_handles_file_write_exception(self):
        """Test log_debug_raw handles file write exceptions gracefully"""
        with patch('builtins.open', side_effect=Exception("Disk full")):
            try:
                log_debug_raw(phase='test', message='msg', data='data')
            except Exception:
                pytest.fail("log_debug_raw raised exception on file write failure")
    
    def test_log_debug_raw_never_raises(self, tmp_path):
        """Test log_debug_raw never raises exceptions"""
        os.chdir(tmp_path)
        
        test_cases = [
            {'phase': 'test', 'message': 'msg'},
            {'phase': '', 'message': ''},
            {'phase': 'test', 'message': 'msg', 'data': None},
            {'phase': 'test', 'message': 'msg', 'component': None},
            {'phase': 'test', 'message': 'msg', 'attempt': None},
            {'phase': 'test', 'message': 'msg', 'data': 'x' * 1000000},
        ]
        
        for kwargs in test_cases:
            try:
                log_debug_raw(**kwargs)
            except Exception as e:
                pytest.fail(f"log_debug_raw raised exception for {kwargs}: {e}")


class TestDebugOutputFormat:
    """Test debug output format and content"""
    
    def setup_method(self):
        """Enable debug mode before each test"""
        os.environ['IRONCLAD_DEBUG'] = '1'
    
    def teardown_method(self):
        """Disable debug mode and cleanup after each test"""
        if 'IRONCLAD_DEBUG' in os.environ:
            del os.environ['IRONCLAD_DEBUG']
        if os.path.exists('build/.ironclad_debug'):
            shutil.rmtree('build')
    
    def test_file_format_structure(self, tmp_path):
        """Test file follows correct format structure"""
        os.chdir(tmp_path)
        log_debug_raw(
            phase='test_phase',
            message='test message',
            data='test data',
            component='test_component',
            attempt=1
        )
        
        filepath = tmp_path / 'build' / '.ironclad_debug' / 'test_phase_test_component_attempt1.txt'
        content = filepath.read_text()
        
        lines = content.split('\n')
        assert lines[0] == 'Phase: test_phase'
        assert lines[1] == 'Component: test_component'
        assert lines[2] == 'Attempt: 1'
        assert lines[3] == 'Message: test message'
        assert lines[4] == ''
        assert lines[5] == 'RAW DATA:'
    
    def test_data_preserved_exactly(self, tmp_path):
        """Test raw data is preserved exactly as provided"""
        os.chdir(tmp_path)
        raw_data = '''def test():
    """Multi-line
    with special chars: \\"\\'\\t\\n"""
    return True'''
        
        log_debug_raw(phase='test', message='msg', data=raw_data)
        
        filepath = tmp_path / 'build' / '.ironclad_debug' / 'test.txt'
        content = filepath.read_text()
        
        assert raw_data in content
    
    def test_filename_encoding(self, tmp_path):
        """Test filename encoding for various component names"""
        os.chdir(tmp_path)
        log_debug_raw(
            phase='generate',
            message='msg',
            component='test-func_name',
            attempt=1
        )
        
        filepath = tmp_path / 'build' / '.ironclad_debug' / 'generate_test-func_name_attempt1.txt'
        assert filepath.exists()
