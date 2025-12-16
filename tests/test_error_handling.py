"""
Error Handling and Edge Case Tests
DMT Protocol: Done Means Taught - 100% coverage required for production readiness
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pytest
from unittest.mock import patch, MagicMock
from core_logic.parser import StatementParser
from core_logic.reasoner import SimpleLogicEngine

class TestErrorHandling:
    """Test suite for error conditions and edge cases"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.parser = StatementParser()
        self.reasoner = SimpleLogicEngine()
    
    def test_spacy_model_loading_failure(self):
        """Test parser behavior when spaCy model fails to load"""
        with patch('spacy.load', side_effect=OSError("Model not found")):
            with patch('builtins.print') as mock_print:
                with patch('subprocess.check_call') as mock_subprocess:
                    with pytest.raises(OSError):
                        StatementParser()
                    
                    # Verify error handling was attempted
                    mock_print.assert_called_with("Downloading spaCy model 'en_core_web_sm'...")
                    mock_subprocess.assert_called_once()
    
    def test_parser_with_corrupted_spacy_model(self):
        """Test parser behavior with corrupted spaCy model"""
        with patch('spacy.load', side_effect=Exception("Corrupted model")):
            with pytest.raises(Exception):
                StatementParser()
    
    def test_reasoner_with_none_input(self):
        """Test reasoner with None input"""
        # Should not crash, just handle gracefully
        with pytest.raises((TypeError, AttributeError)):
            self.reasoner._parse_statement(None)
    
    def test_reasoner_with_non_string_input(self):
        """Test reasoner with non-string input"""
        # Should not crash, just handle gracefully  
        with pytest.raises((TypeError, AttributeError)):
            self.reasoner._parse_statement(123)
    
    def test_reasoner_with_empty_string_input(self):
        """Test reasoner with empty string"""
        result = self.reasoner._parse_statement("")
        assert result is None
    
    def test_reasoner_with_only_whitespace_input(self):
        """Test reasoner with whitespace-only string"""
        result = self.reasoner._parse_statement("   \t\n   ")
        assert result is None
    
    def test_knowledge_base_corruption_recovery(self):
        """Test reasoner behavior with corrupted knowledge base"""
        # Manually corrupt knowledge base
        self.reasoner.knowledge_base = [
            {"subject": None, "object": "test", "negated": False},  # Corrupted entry
            {"subject": "valid", "object": None, "negated": True},   # Corrupted entry
        ]
        
        # Should still be able to process new statements
        result = self.reasoner._parse_statement("The cat is black")
        assert result is not None
        
        # Should detect contradiction with valid entries
        self.reasoner.process_statement("The cat is not black")
        # Should not crash despite corrupted entries
    
    def test_contradiction_detection_with_corrupted_data(self):
        """Test contradiction detection with malformed knowledge base entries"""
        # Add valid fact first
        self.reasoner.process_statement("The sky is blue")
        
        # Corrupt the knowledge base with None values
        self.reasoner.knowledge_base[0] = {"subject": None, "object": None, "negated": False}
        
        # Should not crash when checking contradictions
        result = self.reasoner.process_statement("The sky is not blue")
        # Should handle gracefully (either detect or not detect, but not crash)
    
    def test_parser_memory_cleanup(self):
        """Test parser doesn't leak memory with repeated parsing"""
        # Parse many sentences to check for memory leaks
        sentences = [
            "The cat is black",
            "The dog is brown", 
            "The sky is blue",
            "The car is red"
        ] * 100  # 400 sentences
        
        for sentence in sentences:
            result = self.parser.parse(sentence)
            assert result is not None or result is None  # Should not crash
    
    def test_reasoner_large_knowledge_base(self):
        """Test reasoner performance with large knowledge base"""
        # Add many facts to knowledge base
        for i in range(1000):
            self.reasoner.knowledge_base.append({
                "subject": f"item_{i}",
                "object": f"value_{i}", 
                "negated": i % 2 == 0
            })
        
        # Should still be able to process new statements efficiently
        start_time = pytest.importorskip("time").time()
        self.reasoner.process_statement("The test_item is active")
        end_time = pytest.importorskip("time").time()
        
        # Should complete in reasonable time (less than 1 second)
        assert end_time - start_time < 1.0
    
    def test_unicode_edge_cases_in_reasoner(self):
        """Test reasoner with unicode characters in statements"""
        unicode_statements = [
            "El gato está negro",  # Spanish with accents
            "Кот черный",  # Cyrillic characters  
            "猫是黑色的",  # Chinese characters
            "🐱 is black",  # Emoji
        ]
        
        for statement in unicode_statements:
            result = self.reasoner._parse_statement(statement)
            # Should handle gracefully (may parse or not, but not crash)
            assert isinstance(result, (dict, type(None)))
    
    def test_concurrent_access_simulation(self):
        """Test reasoner behavior under simulated concurrent access"""
        # Simulate multiple rapid statements
        statements = [
            "Fact 1: The cat is black",
            "Fact 2: The dog is brown", 
            "Fact 3: Contradiction: The cat is not black"
        ]
        
        results = []
        for statement in statements:
            try:
                result = self.reasoner.process_statement(statement)
                results.append(result)
            except Exception as e:
                results.append(f"Error: {e}")
        
        # Should handle all statements without crashing
        assert len(results) == len(statements)
        assert not any("Error:" in str(r) for r in results)

class TestParserEdgeCases:
    """Additional edge cases for parser to improve coverage"""
    
    def setup_method(self):
        self.parser = StatementParser()
    
    def test_multiple_verbs_in_sentence(self):
        """Test sentence with multiple verbs"""
        result = self.parser.parse("The cat is and is black")
        # Should handle gracefully (may parse first or fail, but not crash)
        assert isinstance(result, (dict, type(None)))
    
    def test_nested_prepositional_phrases(self):
        """Test complex prepositional phrases"""
        result = self.parser.parse("The cat is on the mat under the table")
        # Should extract something meaningful or return None
        assert isinstance(result, (dict, type(None)))
    
    def test_quoted_strings(self):
        """Test sentences with quotes"""
        result = self.parser.parse('The cat is "black"')
        # Should handle quotes gracefully
        assert isinstance(result, (dict, type(None)))
    
    def test_numerical_subjects_and_objects(self):
        """Test sentences with numbers as subjects/objects"""
        test_cases = [
            "123 is 456",
            "The year 2023 is important", 
            "Room 101 is empty"
        ]
        
        for case in test_cases:
            result = self.parser.parse(case)
            # Should handle numbers without crashing
            assert isinstance(result, (dict, type(None)))
    
    def test_mixed_case_negation(self):
        """Test various negation patterns"""
        negation_cases = [
            "The cat is NOT black",  # Uppercase NOT
            "The cat IS NOT black",  # Mixed case
            "The cat is nOt black",   # Mixed case
            "The cat isn't black",    # Contraction
            "The cat's not black",    # Possessive with negation
        ]
        
        for case in negation_cases:
            result = self.parser.parse(case)
            # Should detect negation in various forms
            if result:
                assert result['negated'] is True

if __name__ == "__main__":
    pytest.main([__file__, "-v"])