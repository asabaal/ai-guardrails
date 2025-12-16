"""
Comprehensive test suite for SimpleLogicEngine
DMT Protocol: Done Means Taught - 100% coverage required
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pytest
from core_logic.reasoner import SimpleLogicEngine

class TestSimpleLogicEngine:
    """Test suite for SimpleLogicEngine class"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.engine = SimpleLogicEngine()
    
    def test_init(self):
        """Test engine initialization"""
        assert self.engine.knowledge_base == []
        assert hasattr(self.engine, 'process_statement')
        assert hasattr(self.engine, '_parse_statement')
    
    def test_add_first_fact(self):
        """Test adding first fact to knowledge base"""
        self.engine.process_statement("The cat is black")
        assert len(self.engine.knowledge_base) == 1
        expected = {"subject": "the cat", "object": "black", "negated": False}
        assert self.engine.knowledge_base[0] == expected
    
    def test_add_duplicate_fact(self):
        """Test adding duplicate fact"""
        self.engine.process_statement("The cat is black")
        self.engine.process_statement("The cat is black")
        assert len(self.engine.knowledge_base) == 1  # Should not add duplicate
    
    def test_add_contradiction(self):
        """Test detecting contradiction"""
        self.engine.process_statement("The cat is black")
        # Capture print output to check for contradiction detection
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output
        self.engine.process_statement("The cat is not black")
        sys.stdout = sys.__stdout__
        
        output = captured_output.getvalue()
        assert "CONTRADICTION DETECTED" in output
        assert len(self.engine.knowledge_base) == 1  # Should not add contradiction
    
    def test_add_different_subjects(self):
        """Test adding facts with different subjects"""
        self.engine.process_statement("The cat is black")
        self.engine.process_statement("The dog is brown")
        assert len(self.engine.knowledge_base) == 2
    
    def test_add_different_objects(self):
        """Test adding facts with different objects for same subject"""
        self.engine.process_statement("The cat is black")
        self.engine.process_statement("The cat is hungry")
        assert len(self.engine.knowledge_base) == 2
    
    def test_parse_statement_valid(self):
        """Test _parse_statement with valid input"""
        result = self.engine._parse_statement("The cat is black")
        expected = {"subject": "the cat", "object": "black", "negated": False}
        assert result == expected
    
    def test_parse_statement_negative(self):
        """Test _parse_statement with negative input"""
        result = self.engine._parse_statement("The cat is not black")
        expected = {"subject": "the cat", "object": "black", "negated": True}
        assert result == expected
    
    def test_parse_statement_invalid(self):
        """Test _parse_statement with invalid input"""
        result = self.engine._parse_statement("Running quickly")
        assert result is None
    
    def test_parse_statement_empty(self):
        """Test _parse_statement with empty string"""
        result = self.engine._parse_statement("")
        assert result is None
    
    def test_case_insensitive_parsing(self):
        """Test case insensitive parsing in _parse_statement"""
        result1 = self.engine._parse_statement("THE CAT IS BLACK")
        result2 = self.engine._parse_statement("the cat is black")
        assert result1 == result2
    
    def test_whitespace_handling(self):
        """Test whitespace handling in _parse_statement"""
        result1 = self.engine._parse_statement("  The cat is black  ")
        result2 = self.engine._parse_statement("The cat is black")
        assert result1 == result2

class TestLogicEngineEdgeCases:
    """Test edge cases and complex scenarios"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.engine = SimpleLogicEngine()
    
    def test_multiple_contradictions(self):
        """Test multiple contradictions in sequence"""
        self.engine.process_statement("The cat is black")
        self.engine.process_statement("The dog is brown")
        
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output
        self.engine.process_statement("The cat is not black")
        self.engine.process_statement("The dog is not brown")
        sys.stdout = sys.__stdout__
        
        output = captured_output.getvalue()
        assert output.count("CONTRADICTION DETECTED") == 2
    
    def test_no_false_contradictions(self):
        """Test that different subjects/objects don't trigger false contradictions"""
        self.engine.process_statement("The cat is black")
        self.engine.process_statement("The dog is black")  # Same object, different subject
        self.engine.process_statement("The cat is brown")   # Same subject, different object
        
        assert len(self.engine.knowledge_base) == 3
    
    def test_complex_subjects(self):
        """Test parsing complex subjects"""
        self.engine.process_statement("The big black cat is hungry")
        assert len(self.engine.knowledge_base) == 1
    
    def test_special_characters_in_statements(self):
        """Test statements with special characters"""
        self.engine.process_statement("The email is test@example.com")
        assert len(self.engine.knowledge_base) == 1
    
    def test_unicode_in_statements(self):
        """Test statements with unicode characters"""
        self.engine.process_statement("The café is open")
        assert len(self.engine.knowledge_base) == 1
    
    def test_unparseable_statement_error_message(self):
        """Test error message for unparseable statements (lines 41-42)"""
        from unittest.mock import patch
        with patch('builtins.print') as mock_print:
            self.engine.process_statement("Random text without proper structure")
            mock_print.assert_called_with("  -> Could not understand: 'Random text without proper structure'")

if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])