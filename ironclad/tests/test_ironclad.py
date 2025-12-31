import pytest
import json
import os
import sys
import tempfile
import subprocess
from unittest.mock import patch, MagicMock, mock_open

import ironclad_ai_guardrails.ironclad as ironclad


class TestCleanJsonResponse:
    """Test the clean_json_response function"""
    
    def test_clean_normal_json(self):
        """Test cleaning normal JSON without markdown"""
        input_text = '{"filename": "test", "code": "def test(): pass"}'
        result = ironclad.clean_json_response(input_text)
        assert result == '{"filename": "test", "code": "def test(): pass"}'
    
    def test_clean_json_with_markdown_fences(self):
        """Test cleaning JSON with ```json fences"""
        input_text = '```json\n{"filename": "test", "code": "def test(): pass"}\n```'
        result = ironclad.clean_json_response(input_text)
        assert result == '{"filename": "test", "code": "def test(): pass"}'
    
    def test_clean_json_with_simple_fences(self):
        """Test cleaning JSON with simple ``` fences"""
        input_text = '```\n{"filename": "test", "code": "def test(): pass"}\n```'
        result = ironclad.clean_json_response(input_text)
        assert result == '{"filename": "test", "code": "def test(): pass"}'
    
    def test_clean_json_with_extra_whitespace(self):
        """Test cleaning JSON with extra whitespace"""
        input_text = '   ```json\n   {"filename": "test", "code": "def test(): pass"}\n   ```   '
        result = ironclad.clean_json_response(input_text)
        assert result == '{"filename": "test", "code": "def test(): pass"}'
    
    def test_clean_empty_string(self):
        """Test cleaning empty string"""
        result = ironclad.clean_json_response("")
        assert result == ""
    
    def test_clean_only_fences(self):
        """Test cleaning string with only fences"""
        input_text = '```json\n```'
        result = ironclad.clean_json_response(input_text)
        assert result == ""


class TestGenerateCandidate:
    """Test the generate_candidate function"""
    
    @patch('ironclad_ai_guardrails.ironclad.ollama.chat')
    def test_generate_candidate_success(self, mock_chat):
        """Test successful candidate generation"""
        mock_response = {
            'message': {
                'content': '{"filename": "test_func", "code": "def test_func(): pass", "test": "def test_test_func(): assert test_func() is None"}'
            }
        }
        mock_chat.return_value = mock_response
        
        result = ironclad.generate_candidate("test request")
        
        assert result is not None
        assert result['filename'] == "test_func"
        assert 'def test_func(): pass' in result['code']
        assert 'test_test_func' in result['test']
        mock_chat.assert_called_once()
    
    @patch('ironclad_ai_guardrails.ironclad.ollama.chat')
    def test_generate_candidate_json_decode_error(self, mock_chat):
        """Test handling of JSON decode error"""
        mock_response = {
            'message': {
                'content': 'invalid json content'
            }
        }
        mock_chat.return_value = mock_response
        
        with patch('builtins.print') as mock_print:
            result = ironclad.generate_candidate("test request")
            assert result is None
            mock_print.assert_any_call("[!] Validation Failed: Model output was not valid JSON.")
    
    @patch('ironclad_ai_guardrails.ironclad.ollama.chat')
    def test_generate_candidate_ollama_error(self, mock_chat):
        """Test handling of ollama connection error"""
        mock_chat.side_effect = Exception("Connection error")
        
        with patch('builtins.print') as mock_print:
            result = ironclad.generate_candidate("test request")
            assert result is None
            mock_print.assert_any_call("[!] Error connecting to Ollama: Connection error")
    
    @patch('ironclad_ai_guardrails.ironclad.ollama.chat')
    def test_generate_candidate_with_markdown_response(self, mock_chat):
        """Test candidate generation when AI returns markdown-wrapped JSON"""
        mock_response = {
            'message': {
                'content': '```json\n{"filename": "test_func", "code": "def test_func(): pass", "test": "def test_test_func(): pass"}\n```'
            }
        }
        mock_chat.return_value = mock_response
        
        result = ironclad.generate_candidate("test request")
        
        assert result is not None
        assert result['filename'] == "test_func"


class TestValidateCandidate:
    """Test the validate_candidate function"""
    
    def test_validate_candidate_none_candidate(self):
        """Test validation with None candidate - should raise AttributeError"""
        with pytest.raises(AttributeError):
            ironclad.validate_candidate(None)
    
    def test_validate_candidate_invalid_structure(self):
        """Test validation with invalid candidate structure - still runs pytest"""
        candidate = {"invalid": "structure"}
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stdout = "no tests collected"
            mock_run.return_value = mock_result
            
            with patch('builtins.print'):
                is_valid, logs = ironclad.validate_candidate(candidate)
            
            assert is_valid is False
            # Should still try to run pytest even with invalid structure
    
    @patch('subprocess.run')
    def test_validate_candidate_success(self, mock_run):
        """Test successful validation with passing tests"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "=== test session starts ===\n1 passed in 0.001s"
        mock_run.return_value = mock_result
        
        candidate = {
            "filename": "test_func",
            "code": "def test_func(): return 'test'",
            "test": "def test_test_func(): assert test_func() == 'test'"
        }
        
        with patch('builtins.print'):
            is_valid, logs = ironclad.validate_candidate(candidate)
        
        assert is_valid is True
        assert "1 passed" in logs
    
    @patch('subprocess.run')
    def test_validate_candidate_test_failure(self, mock_run):
        """Test validation with failing tests"""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "=== test session starts ===\n1 failed in 0.001s\nAssertionError"
        mock_run.return_value = mock_result
        
        candidate = {
            "filename": "test_func",
            "code": "def test_func(): return 'wrong'",
            "test": "def test_test_func(): assert test_func() == 'test'"
        }
        
        with patch('builtins.print'):
            is_valid, logs = ironclad.validate_candidate(candidate)
        
        assert is_valid is False
        assert "1 failed" in logs
    
    @patch('subprocess.run')
    def test_validate_candidate_file_creation(self, mock_run):
        """Test that files are created correctly in temp directory"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "1 passed"
        mock_run.return_value = mock_result
        
        candidate = {
            "filename": "test_func",
            "code": "def test_func(): return 'test'",
            "test": "def test_test_func(): assert test_func() == 'test'"
        }
        
        with patch('builtins.print'):
            is_valid, logs = ironclad.validate_candidate(candidate)
        
        # Verify subprocess was called with correct parameters
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert args[0][0] == sys.executable
        assert args[0][1] == "-m"
        assert args[0][2] == "pytest"
        assert "test_test_func.py" in args[0][3]
        assert kwargs['cwd'] is not None  # Should be a temp directory


class TestSaveBrick:
    """Test the save_brick function"""
    
    def test_save_brick_new_directory(self):
        """Test saving brick when directory doesn't exist"""
        candidate = {
            "filename": "test_func",
            "code": "def test_func(): return 'test'",
            "test": "def test_test_func(): assert test_func() == 'test'"
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('builtins.print'):
                ironclad.save_brick(candidate, temp_dir)
            
            # Check files were created directly in output_dir (not in subdirectory)
            assert os.path.exists(os.path.join(temp_dir, "test_func.py"))
            assert os.path.exists(os.path.join(temp_dir, "test_test_func.py"))
            
            # Check file contents
            with open(os.path.join(temp_dir, "test_func.py"), 'r') as f:
                code_content = f.read()
                assert "def test_func(): return 'test'" in code_content
            
            with open(os.path.join(temp_dir, "test_test_func.py"), 'r') as f:
                test_content = f.read()
                assert "def test_test_func(): assert test_func() == 'test'" in test_content
    
    def test_save_brick_creates_directory(self):
        """Test that save_brick creates output_dir if it doesn't exist"""
        candidate = {
            "filename": "test_func",
            "code": "def test_func(): return 'test'",
            "test": "def test_test_func(): assert test_func() == 'test'"
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set output_dir to a non-existent subdirectory
            non_existent_dir = os.path.join(temp_dir, "new_dir")
            
            with patch('builtins.print'):
                ironclad.save_brick(candidate, non_existent_dir)
            
            # Check directory was created
            assert os.path.exists(non_existent_dir)
            assert os.path.exists(os.path.join(non_existent_dir, "test_func.py"))
    
    def test_save_brick_existing_directory(self):
        """Test saving brick when files already exist"""
        candidate = {
            "filename": "test_func",
            "code": "def test_func(): return 'test'",
            "test": "def test_test_func(): assert test_func() == 'test'"
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create existing files
            with open(os.path.join(temp_dir, "old_file.py"), 'w') as f:
                f.write("old content")
            
            with patch('builtins.print'):
                ironclad.save_brick(candidate, temp_dir)
            
            # Check new files exist and old file is still there
            assert os.path.exists(os.path.join(temp_dir, "test_func.py"))
            assert os.path.exists(os.path.join(temp_dir, "test_test_func.py"))
            assert os.path.exists(os.path.join(temp_dir, "old_file.py"))  # save_brick doesn't clean directory


class TestMain:
    """Test the main function"""
    
    @patch('sys.argv', ['ironclad.py'])
    def test_main_no_arguments(self):
        """Test main function with no command line arguments"""
        with patch('builtins.print') as mock_print:
            with pytest.raises(SystemExit) as exc_info:
                ironclad.main()
            assert exc_info.value.code == 1
            mock_print.assert_any_call("Usage: python ironclad.py 'Your request here'")
    
    @patch('sys.argv', ['ironclad.py', 'test request'])
    @patch('ironclad.generate_candidate')
    @patch('ironclad.validate_candidate')
    @patch('ironclad.save_brick')
    def test_main_success_flow(self, mock_save, mock_validate, mock_generate):
        """Test main function with successful flow"""
        mock_generate.return_value = {
            "filename": "test_func",
            "code": "def test_func(): return 'test'",
            "test": "def test_test_func(): assert test_func() == 'test'"
        }
        mock_validate.return_value = (True, "Tests passed")
        
        with patch('builtins.print'):
            ironclad.main()
        
        mock_generate.assert_called_once_with("test request", "gpt-oss:20b", ironclad.DEFAULT_SYSTEM_PROMPT)
        mock_validate.assert_called_once()
        mock_save.assert_called_once()
    
    @patch('sys.argv', ['ironclad.py', 'test request'])
    @patch('ironclad.generate_candidate')
    def test_main_generation_failure(self, mock_generate):
        """Test main function when generation fails"""
        mock_generate.return_value = None
        
        with patch('builtins.print') as mock_print:
            with pytest.raises(SystemExit) as exc_info:
                ironclad.main()
            assert exc_info.value.code == 1
            mock_print.assert_any_call("[X] INCINERATED: Output invalid.")
    
    @patch('sys.argv', ['ironclad.py', 'test request'])
    @patch('ironclad.generate_candidate')
    @patch('ironclad.validate_candidate')
    @patch('ironclad.repair_candidate')
    def test_main_validation_failure(self, mock_repair, mock_validate, mock_generate):
        """Test main function when validation fails and repair also fails"""
        mock_generate.return_value = {
            "filename": "test_func",
            "code": "def test_func(): return 'test'",
            "test": "def test_test_func(): assert test_func() == 'test'"
        }
        mock_validate.return_value = (False, "Tests failed")
        mock_repair.return_value = None  # Repair fails
        
        with patch('builtins.print') as mock_print:
            with pytest.raises(SystemExit) as exc_info:
                ironclad.main()
            assert exc_info.value.code == 1
            mock_print.assert_any_call("[!] Repair produced invalid JSON. Aborting.")
    
    @patch('sys.argv', ['ironclad.py', 'test request'])
    @patch('ironclad.generate_candidate')
    @patch('ironclad.validate_candidate')
    @patch('ironclad.repair_candidate')
    @patch('ironclad.save_brick')
    def test_main_repair_success(self, mock_save, mock_repair, mock_validate, mock_generate):
        """Test main function when validation fails but repair succeeds"""
        mock_generate.return_value = {
            "filename": "test_func",
            "code": "def test_func(): return 'test'",
            "test": "def test_test_func(): assert test_func() == 'test'"
        }
        # First validation fails, second succeeds after repair
        mock_validate.side_effect = [
            (False, "Tests failed"),
            (True, "Tests passed")
        ]
        mock_repair.return_value = {
            "filename": "test_func",
            "code": "def test_func(): return 'fixed'",
            "test": "def test_test_func(): assert test_func() == 'fixed'"
        }
        
        with patch('builtins.print') as mock_print:
            ironclad.main()
            
        mock_generate.assert_called_once()
        assert mock_validate.call_count == 2
        mock_repair.assert_called_once()
        mock_save.assert_called_once()
        mock_print.assert_any_call("[+] Verified after 1 repairs.")
    
    @patch('sys.argv', ['ironclad.py', 'test request'])
    @patch('ironclad.generate_candidate')
    @patch('ironclad.validate_candidate')
    @patch('ironclad.repair_candidate')
    def test_main_max_retries_exceeded(self, mock_repair, mock_validate, mock_generate):
        """Test main function when max retries are exceeded"""
        mock_generate.return_value = {
            "filename": "test_func",
            "code": "def test_func(): return 'test'",
            "test": "def test_test_func(): assert test_func() == 'test'"
        }
        # Always fails validation
        mock_validate.return_value = (False, "Tests failed")
        mock_repair.return_value = {
            "filename": "test_func",
            "code": "def test_func(): return 'still broken'",
            "test": "def test_test_func(): assert test_func() == 'still broken'"
        }
        
        with patch('builtins.print') as mock_print:
            with pytest.raises(SystemExit) as exc_info:
                ironclad.main()
            assert exc_info.value.code == 1
            
        mock_generate.assert_called_once()
        assert mock_validate.call_count == 4  # 1 initial + 3 repairs
        assert mock_repair.call_count == 3
        mock_print.assert_any_call("[-] FINAL FAILURE.")
    
    @patch('sys.argv', ['ironclad.py', 'test request'])
    @patch('ironclad.generate_candidate')
    @patch('ironclad.validate_candidate')
    @patch('ironclad.repair_candidate')
    def test_main_repair_json_error(self, mock_repair, mock_validate, mock_generate):
        """Test main function when repair returns invalid JSON"""
        mock_generate.return_value = {
            "filename": "test_func",
            "code": "def test_func(): return 'test'",
            "test": "def test_test_func(): assert test_func() == 'test'"
        }
        mock_validate.return_value = (False, "Tests failed")
        mock_repair.return_value = None  # Invalid JSON
        
        with patch('builtins.print') as mock_print:
            with pytest.raises(SystemExit) as exc_info:
                ironclad.main()
            assert exc_info.value.code == 1
            
        mock_generate.assert_called_once()
        mock_validate.assert_called_once()
        mock_repair.assert_called_once()
        mock_print.assert_any_call("[!] Repair produced invalid JSON. Aborting.")


class TestMainExecution:
    """Test main execution when run as __main__"""
    
    @patch('sys.argv', ['ironclad.py', 'test request'])
    @patch('ironclad.generate_candidate')
    @patch('ironclad.validate_candidate')
    @patch('ironclad.save_brick')
    def test_main_as_script(self, mock_save, mock_validate, mock_generate):
        """Test main function when called as script"""
        mock_generate.return_value = {
            "filename": "test_func",
            "code": "def test_func(): return 'test'",
            "test": "def test_test_func(): assert test_func() == 'test'"
        }
        mock_validate.return_value = (True, "Tests passed")
        
        with patch('builtins.print'):
            # Test calling main directly (simulates __main__ execution)
            ironclad.main()
        
        mock_generate.assert_called_once_with("test request", "gpt-oss:20b", ironclad.DEFAULT_SYSTEM_PROMPT)
        mock_validate.assert_called_once()
        mock_save.assert_called_once()
    
    def test_main_execution_via_main_block(self):
        """Test that main() is called when __name__ == '__main__'"""
        # This is a simple test to verify the __main__ block calls main()
        # We can't easily test the actual __main__ execution without complex mocking
        # But we can verify the structure is correct by checking the source
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'ironclad.py'), 'r') as f:
            content = f.read()
            assert "if __name__ == \"__main__\":" in content
            assert "main()" in content
    
    @patch('ironclad.generate_candidate')
    @patch('ironclad.validate_candidate')
    @patch('ironclad.save_brick')
    def test_main_with_custom_parameters(self, mock_save, mock_validate, mock_generate):
        """Test main function with custom parameters"""
        mock_generate.return_value = {
            "filename": "test_func",
            "code": "def test_func(): return 'test'",
            "test": "def test_test_func(): assert test_func() == 'test'"
        }
        mock_validate.return_value = (True, "Tests passed")
        
        with patch('builtins.print'):
            ironclad.main(
                request="custom request",
                model_name="custom_model",
                output_dir="custom_output",
                system_prompt="custom prompt"
            )
        
        mock_generate.assert_called_once_with("custom request", "custom_model", "custom prompt")
        mock_validate.assert_called_once()
        mock_save.assert_called_once()


class TestIntegration:
    """Integration tests for the complete workflow"""
    
    @patch('ironclad_ai_guardrails.ironclad.ollama.chat')
    @patch('subprocess.run')
    def test_full_workflow_success(self, mock_run, mock_chat):
        """Test complete workflow from generation to saving"""
        # Mock ollama response
        mock_response = {
            'message': {
                'content': '{"filename": "test_func", "code": "def test_func(): return \\"test\\"", "test": "def test_test_func(): assert test_func() == \\"test\\""}'
            }
        }
        mock_chat.return_value = mock_response
        
        # Mock successful test execution
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "1 passed"
        mock_run.return_value = mock_result
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('builtins.print'):
                # Test generate_candidate
                candidate = ironclad.generate_candidate("test request")
                assert candidate is not None
                
                # Test validate_candidate
                is_valid, logs = ironclad.validate_candidate(candidate)
                assert is_valid is True
                
                # Test save_brick
                ironclad.save_brick(candidate, temp_dir)
                
                # Verify files exist directly in output_dir
                assert os.path.exists(os.path.join(temp_dir, "test_func.py"))
                assert os.path.exists(os.path.join(temp_dir, "test_test_func.py"))