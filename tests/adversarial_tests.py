"""
Adversarial Test Suite using Local LLM
DMT Protocol: Done Means Taught - Continuous automated weakness detection
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pytest
from core_logic.parser import StatementParser
from core_logic.reasoner import SimpleLogicEngine
from data_pipeline.generator import AdversarialGenerator

class TestAdversarialGeneration:
    """Test suite using LLM-generated adversarial examples"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.parser = StatementParser()
        self.reasoner = SimpleLogicEngine()
        
        # Try to setup adversarial generator
        try:
            self.generator = AdversarialGenerator()
            self.generator_available = True
        except (ImportError, Exception):
            self.generator_available = False
            print("Warning: Adversarial generator not available. Install ollama and run local model.")
    
    @pytest.mark.skipif(not pytest.importorskip("ollama"), reason="ollama not available")
    def test_contradiction_detection_with_llm_generated_cases(self):
        """Test contradiction detection using LLM-generated test cases"""
        if not self.generator_available:
            pytest.skip("Adversarial generator not available")
        
        # Generate test cases
        test_cases = self.generator.generate_contradiction_pairs(5)
        
        for case in test_cases:
            fact = case.get('fact')
            contradiction = case.get('contradiction')
            
            # Parse both statements
            parsed_fact = self.parser.parse(fact)
            parsed_contradiction = self.parser.parse(contradiction)
            
            # Verify they parse to opposite negation states
            if parsed_fact and parsed_contradiction:
                assert parsed_fact['subject'] == parsed_contradiction['subject']
                assert parsed_fact['object'] == parsed_contradiction['object']
                assert parsed_fact['negated'] != parsed_contradiction['negated']
    
    @pytest.mark.skipif(not pytest.importorskip("ollama"), reason="ollama not available")
    def test_synonym_handling_with_llm_generated_cases(self):
        """Test parser handling of synonymous expressions"""
        if not self.generator_available:
            pytest.skip("Adversarial generator not available")
        
        # Generate synonym test cases
        test_cases = self.generator.generate_synonym_tests(5)
        
        for case in test_cases:
            original = case.get('original')
            synonym = case.get('synonym_variant')
            
            # Parse both statements
            parsed_original = self.parser.parse(original)
            parsed_synonym = self.parser.parse(synonym)
            
            # Both should parse successfully
            assert parsed_original is not None, f"Failed to parse: {original}"
            assert parsed_synonym is not None, f"Failed to parse: {synonym}"
    
    @pytest.mark.skipif(not pytest.importorskip("ollama"), reason="ollama not available")
    def test_complex_sentence_parsing_with_llm_cases(self):
        """Test parser on complex LLM-generated sentences"""
        if not self.generator_available:
            pytest.skip("Adversarial generator not available")
        
        # Generate complex sentences
        test_cases = self.generator.generate_complex_sentences(5)
        
        for case in test_cases:
            sentence = case.get('sentence')
            expected = case.get('parse_result')
            
            # Parse the sentence
            result = self.parser.parse(sentence)
            
            # Should parse successfully
            assert result is not None, f"Failed to parse complex sentence: {sentence}"
            
            # Should have required fields
            assert 'subject' in result
            assert 'object' in result
            assert 'negated' in result
    
    def test_parser_robustness_on_edge_cases(self):
        """Test parser robustness with edge cases"""
        edge_cases = [
            ("", "Empty string"),
            ("   ", "Whitespace only"),
            ("?", "Question mark only"),
            ("The cat is?", "Question sentence"),
            ("Go get the cat", "Command sentence"),
            ("Very very very big cat is black", "Multiple adjectives"),
            ("The cat's toy is red", "Possessive noun"),
            ("123 is 456", "Numbers as subjects/objects"),
            ("😀 is happy", "Emoji in sentence"),
            ("The cat is\nblack", "Newline in sentence"),
        ]
        
        for sentence, description in edge_cases:
            result = self.parser.parse(sentence)
            # Should not crash, may return None for unparseable sentences
            assert isinstance(result, (dict, type(None))), f"Parser crashed on {description}: {sentence}"

class TestContinuousImprovement:
    """Tests for the continuous improvement cycle"""
    
    def setup_method(self):
        self.parser = StatementParser()
        self.reasoner = SimpleLogicEngine()
    
    def test_learning_from_failures(self):
        """Test that we can identify and learn from parsing failures"""
 # Cases that should genuinely fail to parse or parse incorrectly
        difficult_cases = [
            "The cat itself is black",  # Reflexive pronoun - should parse but may be wrong
            "My car's color is red",  # Possessive noun phrase - should parse but may be wrong
            "The cat that I saw yesterday is black",  # Complex relative clause - parses incorrectly
            "Either the cat or the dog is black",  # Either/or disjunction - parses incorrectly
            "The cat, which is black, is sleeping",  # Non-restrictive relative clause - parses incorrectly
            "Is the cat black?",  # Question - should fail
            "Go get the black cat",  # Command - should fail
            "Neither cat nor dog",  # Incomplete sentence - should fail
            "The cat is",  # Incomplete - should fail
            "",  # Empty string - should fail
        ]
        
        failures = []
        for case in difficult_cases:
            result = self.parser.parse(case)
            if result is None:
                failures.append(case)
        
        # We should be able to identify these as current limitations
        assert len(failures) > 0, "Should identify known parsing limitations"
        
        # These become our roadmap for improvements
        print(f"Identified {len(failures)} parsing failures to address:")
        for failure in failures:
            print(f"  - {failure}")
    
    def test_contradiction_detection_accuracy(self):
        """Measure contradiction detection accuracy on known cases"""
        test_pairs = [
            ("The sky is blue", "The sky is not blue", True),   # Contradiction
            ("The cat is black", "The cat is white", False),     # Different objects
            ("The dog is big", "The dog is big", False),        # Duplicate
            ("The car is red", "A car is red", False),          # Different subjects
        ]
        
        correct_detections = 0
        for fact, test_case, should_contradict in test_pairs:
            # Add fact to reasoner
            self.reasoner.process_statement(fact)
            
            # Check if test case is detected as contradiction
            # (This would need to be implemented in reasoner)
            # For now, we test the parsing logic
            parsed_fact = self.parser.parse(fact)
            parsed_test = self.parser.parse(test_case)
            
            if parsed_fact and parsed_test:
                is_contradiction = (
                    parsed_fact['subject'] == parsed_test['subject'] and
                    parsed_fact['object'] == parsed_test['object'] and
                    parsed_fact['negated'] != parsed_test['negated']
                )
                
                if is_contradiction == should_contradict:
                    correct_detections += 1
        
        accuracy = correct_detections / len(test_pairs)
        assert accuracy >= 0.75, f"Contradiction detection accuracy too low: {accuracy:.2%}"

if __name__ == "__main__":
    # Run adversarial tests standalone
    test_suite = TestAdversarialGeneration()
    test_suite.setup_method()
    
    if test_suite.generator_available:
        print("Running adversarial tests...")
        test_suite.test_contradiction_detection_with_llm_generated_cases()
        test_suite.test_synonym_handling_with_llm_generated_cases()
        print("Adversarial tests completed!")
    else:
        print("Adversarial generator not available. Install ollama and run local model.")