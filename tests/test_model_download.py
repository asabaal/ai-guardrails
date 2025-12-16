"""
Test Suite for Model Download Error Handling

Tests the model download functionality to achieve 100% coverage
"""

import pytest
import spacy
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_logic.enhanced_parser import EnhancedParser


class TestModelDownload:
    """Test model download error handling"""
    
    @patch('spacy.load')
    @patch('subprocess.check_call')
    def test_model_download_when_missing(self, mock_subprocess, mock_spacy_load):
        """Test model download when spaCy model is missing"""
        # First call raises OSError (model not found), second call succeeds
        mock_spacy_load.side_effect = [OSError("Model not found"), MagicMock()]
        
        # Should attempt to download the model
        parser = EnhancedParser("en_core_web_sm")
        
        # Verify subprocess was called to download model
        mock_subprocess.assert_called_once()
        assert parser.nlp is not None
    
    @patch('spacy.load')
    @patch('subprocess.check_call')
    @patch('builtins.print')
    def test_model_download_prints_messages(self, mock_print, mock_subprocess, mock_spacy_load):
        """Test that model download prints appropriate messages"""
        # First call raises OSError, second call succeeds
        mock_spacy_load.side_effect = [OSError("Model not found"), MagicMock()]
        
        parser = EnhancedParser("en_core_web_sm")
        
        # Check that download message was printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        download_message_found = any("Downloading spaCy model" in call for call in print_calls)
        init_message_found = any("Enhanced Parser initialized" in call for call in print_calls)
        
        assert download_message_found
        assert init_message_found
    
    @patch('spacy.load')
    def test_model_already_exists(self, mock_spacy_load):
        """Test initialization when model already exists"""
        mock_spacy_load.return_value = MagicMock()
        
        parser = EnhancedParser("en_core_web_sm")
        
        # Should not attempt to download
        mock_spacy_load.assert_called_once_with("en_core_web_sm")
        assert parser.nlp is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])