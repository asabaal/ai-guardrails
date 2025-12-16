"""
Integration tests for the complete AI Guardrails system
DMT Protocol: Done Means Taught - Full system integration testing
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core_logic.parser import StatementParser
from core_logic.reasoner import SimpleLogicEngine

class TestSystemIntegration:
    """Test complete system integration"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.parser = StatementParser()
        self.engine = SimpleLogicEngine()
    
    def test_end_to_end_contradiction_detection(self):
        """Test full pipeline: parse -> reason -> detect contradiction"""
        statements = [
            "The sky is blue",
            "The grass is green",
            "The sky is not blue"  # Should trigger contradiction
        ]
        
        results = []
        for stmt in statements:
            parsed = self.parser.parse(stmt)
            if parsed:
                # Convert to text format for reasoner
                text_form = f"{parsed['subject']} is {'not ' if parsed['negated'] else ''}{parsed['object']}"
                # Capture reasoner output
                import io
                import sys
                captured_output = io.StringIO()
                sys.stdout = captured_output
                self.engine.process_statement(text_form)
                sys.stdout = sys.__stdout__
                
                results.append({
                    'original': stmt,
                    'parsed': parsed,
                    'processed': text_form,
                    'output': captured_output.getvalue()
                })
        
        # Verify contradiction was detected
        contradiction_found = False
        for result in results:
            if "CONTRADICTION DETECTED" in result['output']:
                contradiction_found = True
                break
        
        assert contradiction_found, "No contradiction detected in integration test"
        assert len(self.engine.knowledge_base) == 2, "Knowledge base should have 2 facts (contradiction rejected)"
    
    def test_multiple_facts_integration(self):
        """Test processing multiple related facts"""
        statements = [
            "The cat is black",
            "The cat is hungry", 
            "The dog is brown",
            "The cat is thirsty"
        ]
        
        for stmt in statements:
            parsed = self.parser.parse(stmt)
            if parsed:
                text_form = f"{parsed['subject']} is {'not ' if parsed['negated'] else ''}{parsed['object']}"
                self.engine.process_statement(text_form)
        
        # Should have 4 facts (no contradictions)
        assert len(self.engine.knowledge_base) == 4
        
        # Verify specific facts exist
        subjects = [fact['subject'] for fact in self.engine.knowledge_base]
        assert 'the cat' in subjects
        assert 'the dog' in subjects
    
    def test_parser_reasoner_compatibility(self):
        """Test that parser output is compatible with reasoner input"""
        test_statements = [
            "The cat is black",
            "The cat is not black",
            "John is tall",
            "The weather is good"
        ]
        
        for stmt in test_statements:
            parsed = self.parser.parse(stmt)
            if parsed:
                # Verify parser output has required keys
                assert 'subject' in parsed
                assert 'object' in parsed
                assert 'negated' in parsed
                assert isinstance(parsed['negated'], bool)
                
                # Verify reasoner can process the converted format
                text_form = f"{parsed['subject']} is {'not ' if parsed['negated'] else ''}{parsed['object']}"
                try:
                    self.engine.process_statement(text_form)
                except Exception as e:
                    assert False, f"Reasoner failed to process parser output: {e}"
    
    def test_error_handling_integration(self):
        """Test error handling across the integrated system"""
        problematic_inputs = [
            "",  # Empty string
            "   ",  # Whitespace only
            "Running quickly",  # Unparseable
            "Is the cat black?",  # Question form
        ]
        
        for input_text in problematic_inputs:
            parsed = self.parser.parse(input_text)
            # System should handle gracefully without crashing
            if parsed:
                text_form = f"{parsed['subject']} is {'not ' if parsed['negated'] else ''}{parsed['object']}"
                try:
                    self.engine.process_statement(text_form)
                except Exception as e:
                    assert False, f"System crashed on input '{input_text}': {e}"
    
    def test_case_consistency_integration(self):
        """Test case handling across integrated system"""
        case_variations = [
            "THE CAT IS BLACK",
            "the cat is black", 
            "The Cat Is Black"
        ]
        
        results = []
        for stmt in case_variations:
            parsed = self.parser.parse(stmt)
            if parsed:
                text_form = f"{parsed['subject']} is {'not ' if parsed['negated'] else ''}{parsed['object']}"
                self.engine.process_statement(text_form)
                results.append(parsed)
        
        # All should parse to the same normalized form
        if len(results) > 1:
            for result in results[1:]:
                assert result['subject'] == results[0]['subject']
                assert result['object'] == results[0]['object']
                assert result['negated'] == results[0]['negated']

class TestPerformanceAndScalability:
    """Test system performance and basic scalability"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.parser = StatementParser()
        self.engine = SimpleLogicEngine()
    
    def test_batch_processing_performance(self):
        """Test processing multiple statements efficiently"""
        import time
        
        statements = [
            f"The item{i} is value{i}" 
            for i in range(100)
        ]
        
        start_time = time.time()
        
        for stmt in statements:
            parsed = self.parser.parse(stmt)
            if parsed:
                text_form = f"{parsed['subject']} is {'not ' if parsed['negated'] else ''}{parsed['object']}"
                self.engine.process_statement(text_form)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should process most statements in reasonable time (< 5 seconds)
        assert processing_time < 5.0, f"Processing too slow: {processing_time:.2f}s"
        # Some statements might not parse, which is acceptable
        assert len(self.engine.knowledge_base) >= 80, f"Too few statements processed: {len(self.engine.knowledge_base)}"
    
    def test_memory_usage_basic(self):
        """Test basic memory usage patterns"""
        # Process many statements and check knowledge base growth
        for i in range(50):
            stmt = f"The item{i} is value{i}"
            parsed = self.parser.parse(stmt)
            if parsed:
                text_form = f"{parsed['subject']} is {'not ' if parsed['negated'] else ''}{parsed['object']}"
                self.engine.process_statement(text_form)
        
        # Knowledge base should have most facts (some might not parse)
        assert len(self.engine.knowledge_base) >= 40, f"Too few statements processed: {len(self.engine.knowledge_base)}"
        
        # Each fact should have correct structure
        for fact in self.engine.knowledge_base:
            assert 'subject' in fact
            assert 'object' in fact
            assert 'negated' in fact

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])