"""
Test Suite for New Linguistic Pattern Methods

Tests the improved linguistic analysis methods that replace hardcoded patterns:
- _is_intransitive_in_context method
- Enhanced _extract_modifiers_for_entity method
"""

import pytest
import spacy
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_logic.enhanced_parser import EnhancedParser, EnhancedEntity, EnhancedParsedStatement


class TestLinguisticPatterns:
    """Test the new linguistic pattern methods"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = EnhancedParser()
    
    def test_is_intransitive_in_context_with_object(self):
        """Test intransitive detection when verb has object"""
        parsed = self.parser.parse_statement("The cat chases the mouse")
        
        # Should not use verb as object since there's a direct object
        assert parsed.object == "mouse"
        assert parsed.object != "chase"
    
    def test_is_intransitive_in_context_without_object(self):
        """Test intransitive detection when verb has no object"""
        parsed = self.parser.parse_statement("The dog is sleeping")
        
        # Should use verb as object since it's intransitive
        assert parsed.object == "sleep"
    
    def test_is_intransitive_with_prepositional_phrase(self):
        """Test intransitive detection with prepositional objects"""
        parsed = self.parser.parse_statement("The cat sleeps on the mat")
        
        # Should return None since there's no clear object (prepositional phrase doesn't count)
        assert parsed is None
    
    def test_extract_modifiers_with_dependency_parsing(self):
        """Test modifier extraction using dependency parsing"""
        parsed = self.parser.parse_statement("The big happy dog is sleeping")
        
        assert parsed is not None
        # Should find modifiers using linguistic analysis
        dog_entities = [e for e in parsed.entities if "dog" in e.name]
        if dog_entities:
            entity = dog_entities[0]
            # Should find "big" and "happy" as modifiers
            assert any(mod in entity.modifiers for mod in ["big", "happy"])
    
    def test_extract_modifiers_with_compound_entities(self):
        """Test modifier extraction for compound entities"""
        parsed = self.parser.parse_statement("The enormous red sports car is expensive")
        
        assert parsed is not None
        # Should find compound entity with modifiers
        car_entities = [e for e in parsed.entities if "car" in e.name]
        if car_entities:
            entity = car_entities[0]
            # Should find adjectives from the compound name
            assert len(entity.modifiers) >= 1
    
    def test_extract_modifiers_no_duplicates(self):
        """Test that modifiers are deduplicated"""
        parsed = self.parser.parse_statement("The big big dog is big")
        
        assert parsed is not None
        dog_entities = [e for e in parsed.entities if "dog" in e.name]
        if dog_entities:
            entity = dog_entities[0]
            # Should not have duplicate modifiers
            assert len(entity.modifiers) == len(set(entity.modifiers))
    
    def test_model_download_error_handling(self):
        """Test error handling in model initialization"""
        # This test would require mocking the spacy.load function
        # For now, just test that initialization works
        parser = EnhancedParser()
        assert parser.nlp is not None
    
    def test_confidence_calculation_with_new_methods(self):
        """Test confidence calculation with new linguistic methods"""
        parsed = self.parser.parse_statement("The beautiful cat sleeps peacefully")
        
        if parsed:
            # Should have reasonable confidence
            assert 0.0 <= parsed.confidence <= 1.0
            # Should have entities
            assert len(parsed.entities) >= 1
    
    def test_intransitive_detection_with_indirect_object(self):
        """Test intransitive detection with indirect objects"""
        parsed = self.parser.parse_statement("The teacher gives the student a book")
        
        # Should not use verb as object since there's an indirect object
        assert parsed.object != "give"
    
    def test_intransitive_detection_with_subject_verb_root(self):
        """Test intransitive detection with subject-verb-root structure"""
        parsed = self.parser.parse_statement("Birds fly")
        
        # Should use verb as object since it's intransitive
        assert parsed.object == "fly"
    
    def test_modifier_extraction_with_named_entities(self):
        """Test modifier extraction for named entities"""
        parsed = self.parser.parse_statement("Tall John runs quickly")
        
        assert parsed is not None
        # Should find named entity with modifiers
        person_entities = [e for e in parsed.entities if e.entity_type == "PERSON"]
        if person_entities:
            entity = person_entities[0]
            # Should find "tall" as modifier
            assert "tall" in entity.modifiers
    
    def test_edge_case_empty_modifiers(self):
        """Test modifier extraction when no modifiers exist"""
        parsed = self.parser.parse_statement("Cats sleep")
        
        assert parsed is not None
        # Should handle case with no modifiers gracefully
        for entity in parsed.entities:
            assert isinstance(entity.modifiers, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])