import pytest
import json
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

import ironclad_ai_guardrails.ironclad as ironclad


class TestRepairCandidate:
    """Test the repair_candidate function"""
    
    @patch('ironclad_ai_guardrails.ironclad.ollama.chat')
    def test_repair_candidate_success(self, mock_chat):
        """Test successful repair of candidate"""
        mock_response = {
            'message': {
                'content': '{"filename": "fixed_func", "code": "def fixed_func(): return \'fixed\'", "test": "def test_fixed_func(): assert fixed_func() == \'fixed\'"}'
            }
        }
        mock_chat.return_value = mock_response
        
        candidate = {
            "filename": "broken_func",
            "code": "def broken_func(): return 'broken'",
            "test": "def test_broken_func(): assert broken_func() == 'broken'"
        }
        traceback_log = "NameError: name 'broken_func' is not defined"
        
        result = ironclad.repair_candidate(candidate, traceback_log)
        
        assert result is not None
        assert result['filename'] == "fixed_func"
        assert "def fixed_func()" in result['code']
        assert "test_fixed_func" in result['test']
        mock_chat.assert_called_once()
    
    @patch('ironclad_ai_guardrails.ironclad.ollama.chat')
    def test_repair_candidate_with_custom_model(self, mock_chat):
        """Test repair with custom model and system prompt"""
        mock_response = {
            'message': {
                'content': '{"filename": "repaired_func", "code": "def repaired_func(): pass", "test": "def test_repaired_func(): pass"}'
            }
        }
        mock_chat.return_value = mock_response
        
        candidate = {"filename": "func", "code": "broken", "test": "broken"}
        traceback = "error"
        
        result = ironclad.repair_candidate(
            candidate, 
            traceback, 
            model_name="custom_model",
            system_prompt="custom prompt"
        )
        
        assert result is not None
        # Check that custom model and prompt were used
        call_args = mock_chat.call_args
        assert call_args[1]['model'] == "custom_model"
        system_message = call_args[1]['messages'][0]['content']
        assert "custom prompt" in system_message
    
    @patch('ironclad_ai_guardrails.ironclad.ollama.chat')
    def test_repair_candidate_json_decode_error(self, mock_chat):
        """Test repair when AI returns invalid JSON"""
        mock_chat.return_value = {
            'message': {
                'content': 'invalid json content'
            }
        }
        
        with patch('builtins.print') as mock_print:
            result = ironclad.repair_candidate(
                {"filename": "func", "code": "broken", "test": "broken"}, 
                "error"
            )
            assert result is None
            # Check that any repair error message was printed
            error_calls = [call for call in mock_print.call_args_list if "[!] Repair Error:" in str(call)]
            assert len(error_calls) > 0
    
    @patch('ironclad_ai_guardrails.ironclad.ollama.chat')
    def test_repair_candidate_ollama_error(self, mock_chat):
        """Test repair when ollama connection fails"""
        mock_chat.side_effect = Exception("Connection error")
        
        with patch('builtins.print') as mock_print:
            result = ironclad.repair_candidate(
                {"filename": "func", "code": "broken", "test": "broken"}, 
                "error"
            )
            assert result is None
            mock_print.assert_any_call("[!] Repair Error: Connection error")
    
    def test_repair_candidate_prints_attempt_message(self):
        """Test that repair prints attempt message"""
        candidate = {"filename": "func", "code": "def func(): pass", "test": "def test_func(): pass"}
        
        with patch('ironclad_ai_guardrails.ironclad.ollama.chat') as mock_chat:
            mock_chat.return_value = {
                'message': {'content': '{"filename": "func", "code": "def func(): pass", "test": "def test_func(): pass"}'}
            }
            with patch('builtins.print') as mock_print:
                ironclad.repair_candidate(candidate, "error")
                mock_print.assert_any_call("[*] Attempting repair...")


class TestRepairIntegration:
    """Test repair functionality integration with other ironclad functions"""
    
    @patch('ironclad_ai_guardrails.ironclad.ollama.chat')
    @patch('ironclad.validate_candidate')
    def test_repair_workflow_integration(self, mock_validate, mock_chat):
        """Test repair in context of validation failure"""
        # Setup validation to fail first time
        mock_validate.return_value = (False, "Test failed")
        
        # Setup repair to succeed
        mock_chat.return_value = {
            'message': {
                'content': '{"filename": "fixed_func", "code": "def fixed_func(): return \'success\'", "test": "def test_fixed_func(): assert fixed_func() == \'success\'"}'
            }
        }
        
        candidate = {
            "filename": "test_func",
            "code": "def test_func(): return 'broken'",
            "test": "def test_test_func(): assert test_func() == 'broken'"
        }
        
        # Initial generation
        initial_candidate = ironclad.generate_candidate("test request")
        
        # Validation fails
        is_valid, logs = ironclad.validate_candidate(initial_candidate)
        assert not is_valid
        
        # Repair succeeds
        repaired_candidate = ironclad.repair_candidate(initial_candidate, logs)
        assert repaired_candidate is not None
        assert repaired_candidate['filename'] == "fixed_func"
        assert "success" in repaired_candidate['code']
    
    def test_repair_prompt_formatting(self):
        """Test that repair prompt is correctly formatted"""
        candidate = {
            "filename": "broken_func",
            "code": "def broken_func():\n    return undefined_var",
            "test": "def test_broken_func(): assert broken_func() == 'value'"
        }
        traceback = "NameError: name 'undefined_var' is not defined"
        
        with patch('ironclad_ai_guardrails.ironclad.ollama.chat') as mock_chat:
            mock_chat.return_value = {
                'message': {
                    'content': '{"filename": "fixed_func", "code": "def fixed_func(): return \'value\'", "test": "def test_fixed_func(): assert fixed_func() == \'value\'"}'
                }
            }
            
            ironclad.repair_candidate(candidate, traceback)
            
            # Check that the prompt was formatted correctly
            call_args = mock_chat.call_args
            user_message = call_args[1]['messages'][1]['content']
            
            # Should contain the original code
            assert "def broken_func():" in user_message
            # Should contain the traceback
            assert "NameError: name 'undefined_var' is not defined" in user_message
            # Should contain repair instruction
            assert "Fix the code" in user_message