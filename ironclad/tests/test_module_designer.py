#!/usr/bin/env python3
"""
Tests for module_designer
"""

import pytest
import sys
import os
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
                'content': '{"module_name": "test_module", "functions": []}'
            }
        }
        mock_chat.return_value = mock_response
        
        result = module_designer.draft_blueprint("test request")
        
        assert result is not None
        assert result['module_name'] == 'test_module'
        mock_chat.assert_called_once()


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
            'functions': []
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
    
    @patch('ironclad_ai_guardrails.module_designer.ollama.chat')
    def test_draft_blueprint_json_error(self, mock_chat):
        """Test blueprint drafting with JSON error (lines 44-47)"""
        mock_chat.return_value = {
            'response': 'invalid json response'
        }
        
        result = module_designer.draft_blueprint("test request")
        
        assert result is None
    
    @patch('ironclad_ai_guardrails.module_designer.ollama.chat')
    def test_draft_blueprint_ollama_error(self, mock_chat):
        """Test blueprint drafting with ollama error (lines 50-61)"""
        mock_chat.side_effect = Exception("Ollama error")
        
        result = module_designer.draft_blueprint("test request")
        
        assert result is None