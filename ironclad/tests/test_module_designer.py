#!/usr/bin/env python3
"""
Tests for module_designer
"""

import pytest
import sys
import os
import json
from unittest.mock import patch, MagicMock

import ironclad_ai_guardrails.module_designer as module_designer


class TestCleanJson:
    """Test the clean_json function"""
    
    def test_clean_json_normal(self):
        """Test cleaning normal JSON (lines 32-35)"""
        input_text = '{"key": "value"}'
        result = module_designer.clean_json(input_text)
        assert result == '{"key": "value"}'
    
    def test_clean_json_with_whitespace(self):
        """Test cleaning JSON with extra whitespace (lines 32-35)"""
        input_text = '   {"key": "value"}   '
        result = module_designer.clean_json(input_text)
        assert result == '{"key": "value"}'
    
    def test_clean_json_with_markdown_fences(self):
        """Test cleaning JSON with markdown fences (lines 33-34)"""
        input_text = '```json\n{"key": "value"}\n```'
        result = module_designer.clean_json(input_text)
        assert result == '{"key": "value"}'
    
    def test_clean_json_with_simple_fences(self):
        """Test cleaning JSON with simple fences (line 34)"""
        input_text = '```\n{"key": "value"}\n```'
        result = module_designer.clean_json(input_text)
        assert result == '{"key": "value"}'
    
    def test_clean_json_with_json_keyword(self):
        """Test cleaning JSON with json keyword (line 33)"""
        input_text = '```json\n{"name": "test"}\n```'
        result = module_designer.clean_json(input_text)
        assert result == '{"name": "test"}'


class TestDraftBlueprint:
    """Test the draft_blueprint function"""
    
    @patch('ironclad_ai_guardrails.module_designer.ollama.chat')
    def test_draft_blueprint_success(self, mock_chat):
        """Test successful blueprint drafting"""
        mock_response = {
            'message': {
                'content': '{"module_name": "test_module", "functions": [], "main_logic_description": "test"}'
            }
        }
        mock_chat.return_value = mock_response
        
        result = module_designer.draft_blueprint("test request")
        
        assert result is not None
        assert result['module_name'] == 'test_module'
        mock_chat.assert_called_once()
    
    @patch('ironclad_ai_guardrails.module_designer.ollama.chat')
    def test_draft_blueprint_no_retry_on_valid_json(self, mock_chat):
        """Test no retry occurs when first attempt returns valid JSON"""
        mock_response = {
            'message': {'content': '{"module_name": "test_module", "functions": [], "main_logic_description": "test"}'}
        }
        mock_chat.return_value = mock_response
        
        result = module_designer.draft_blueprint("test request")
        
        assert result is not None
        assert result['module_name'] == 'test_module'
        assert mock_chat.call_count == 1
    
    @patch('ironclad_ai_guardrails.module_designer.ollama.chat')
    def test_draft_blueprint_retry_success_on_second_attempt(self, mock_chat):
        """Test retry succeeds on second attempt after initial JSON decode error"""
        malformed_json = '{"module_name": "test", "functions": '
        valid_json = '{"module_name": "test", "functions": [], "main_logic_description": "test"}'
        mock_chat.side_effect = [
            {'message': {'content': malformed_json}},
            {'message': {'content': valid_json}}
        ]
        
        result = module_designer.draft_blueprint("test request")
        
        assert result is not None
        assert result['module_name'] == 'test'
        assert mock_chat.call_count == 2
    
    @patch('ironclad_ai_guardrails.module_designer.ollama.chat')
    def test_draft_blueprint_retry_exhaustion(self, mock_chat):
        """Test retry exhaustion returns None after all attempts fail"""
        malformed_json = '{"module_name": "test", "functions": '
        mock_chat.return_value = {'message': {'content': malformed_json}}
        
        result = module_designer.draft_blueprint("test request")
        
        assert result is None
        assert mock_chat.call_count == 3
    
    @patch('ironclad_ai_guardrails.module_designer.ollama.chat')
    def test_draft_blueprint_json_error(self, mock_chat):
        """Test blueprint drafting with JSON error"""
        mock_chat.return_value = {
            'message': {'content': 'invalid json response'}
        }
        
        result = module_designer.draft_blueprint("test request")
        
        assert result is None
        assert mock_chat.call_count == 3
    
    @patch('ironclad_ai_guardrails.module_designer.ollama.chat')
    def test_draft_blueprint_ollama_error(self, mock_chat):
        """Test blueprint drafting with ollama error"""
        mock_chat.side_effect = Exception("Ollama error")
        
        result = module_designer.draft_blueprint("test request")
        
        assert result is None
        assert mock_chat.call_count == 1


class TestModuleDesignerMain:
    """Test module_designer main() function"""
    
    @patch('ironclad_ai_guardrails.module_designer.draft_blueprint')
    @patch('builtins.open', create=True)
    @patch('json.dump')
    @patch('builtins.print')
    def test_main_success(self, mock_print, mock_dump, mock_open, mock_draft):
        """Test successful main execution (lines 54-61)"""
        mock_draft.return_value = {
            'module_name': 'test_module',
            'functions': [],
            'main_logic_description': 'test'
        }
        
        with patch('sys.argv', ['module_designer.py', 'test request']):
            module_designer.main()
        
        mock_draft.assert_called_once_with('test request')
        mock_dump.assert_called_once()
        mock_print.assert_any_call('[+] Blueprint saved to blueprint.json')
    
    @patch('ironclad_ai_guardrails.module_designer.draft_blueprint')
    @patch('builtins.print')
    def test_main_no_arguments(self, mock_print, mock_draft):
        """Test main with no arguments (lines 50-52)"""
        with patch('sys.argv', ['module_designer.py']):
            with pytest.raises(SystemExit) as exc_info:
                module_designer.main()
            
            assert exc_info.value.code == 1
            mock_print.assert_any_call("Usage: python module_designer.py 'I want a tool that...'")
    
    @patch('ironclad_ai_guardrails.module_designer.draft_blueprint')
    @patch('builtins.print')
    def test_main_blueprint_failure(self, mock_print, mock_draft):
        """Test main when blueprint drafting fails"""
        mock_draft.return_value = None
        
        with patch('sys.argv', ['module_designer.py', 'test request']):
            module_designer.main()
        
        # Should not print success message or save file when blueprint fails
        success_calls = [call for call in mock_print.call_args_list 
                        if '[+] Blueprint saved' in str(call)]
        assert len(success_calls) == 0
