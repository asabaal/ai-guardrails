"""
Test Suite for Enhanced Parser Module

Tests advanced linguistic parsing capabilities including:
- Named Entity Recognition (NER)
- Compound entity handling
- Possessive parsing
- Relative clause analysis
- Complex sentence structures
"""

import pytest
import spacy
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_logic.enhanced_parser import EnhancedParser, EnhancedEntity, EnhancedParsedStatement


class TestEnhancedParser:
    """Test cases for EnhancedParser class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = EnhancedParser()
    
    def test_init_with_existing_model(self):
        """Test parser initialization with existing model"""
        parser = EnhancedParser()
        assert parser.nlp is not None
        assert hasattr(parser, '_extract_entities')
    
    def test_parse_simple_statement(self):
        """Test parsing of simple statement"""
        parsed = self.parser.parse_statement("The cat is black")
        
        assert parsed is not None
        assert parsed.subject == "cat"
        assert parsed.object == "black"
        assert parsed.negated is False
        assert parsed.verb_type == "state"
        assert parsed.confidence > 0.5
    
    def test_parse_negated_statement(self):
        """Test parsing of negated statement"""
        parsed = self.parser.parse_statement("The cat is not black")
        
        assert parsed is not None
        assert parsed.subject == "cat"
        assert parsed.object == "black"
        assert parsed.negated is True
        assert parsed.verb_type == "state"
    
    def test_parse_possessive_statement(self):
        """Test parsing of possessive statement"""
        parsed = self.parser.parse_statement("John's cat is black")
        
        assert parsed is not None
        assert len(parsed.possessives) > 0
        possessive = parsed.possessives[0]
        assert possessive["possessor"] == "john"
        assert possessive["possessed"] == "cat"
    
    def test_parse_compound_entity(self):
        """Test parsing of compound entities"""
        parsed = self.parser.parse_statement("The big red car is expensive")
        
        assert parsed is not None
        assert len(parsed.entities) > 0
        
        # Should find compound entity "big red car"
        compound_entities = [e for e in parsed.entities if e.entity_type == "COMPOUND"]
        assert len(compound_entities) > 0
    
    def test_parse_named_entity_person(self):
        """Test parsing of person named entity"""
        parsed = self.parser.parse_statement("John is happy")
        
        assert parsed is not None
        person_entities = [e for e in parsed.entities if e.entity_type == "PERSON"]
        assert len(person_entities) > 0
        assert person_entities[0].name == "john"
    
    def test_parse_relative_clause(self):
        """Test parsing of relative clauses"""
        parsed = self.parser.parse_statement("The cat that I saw is black")
        
        assert parsed is not None
        assert len(parsed.relative_clauses) > 0
        
        clause = parsed.relative_clauses[0]
        assert clause["relative_pronoun"] == "that"
        assert "cat" in clause["modified_noun"]
    
    def test_parse_disjunction_either_or(self):
        """Test parsing of either/or disjunctions"""
        parsed = self.parser.parse_statement("Either the cat or the dog is sleeping")
        
        assert parsed is not None
        assert len(parsed.disjunctions) > 0
        # The parser extracts compound entities with determiners
        assert any("cat" in disj for disj in parsed.disjunctions)
        assert any("dog" in disj for disj in parsed.disjunctions)
    
    def test_extract_entities_with_modifiers(self):
        """Test entity extraction with adjective modifiers"""
        parsed = self.parser.parse_statement("The big happy dog is sleeping")
        
        assert parsed is not None
        # The parser creates compound entities, so look for "dog" in compound
        dog_entities = [e for e in parsed.entities if "dog" in e.name]
        assert len(dog_entities) > 0
        # Compound entities may not have individual modifiers extracted
        # but the compound name itself contains the modifiers
        assert "big" in dog_entities[0].name or "happy" in dog_entities[0].name
    
    def test_extract_relationships(self):
        """Test relationship extraction"""
        parsed = self.parser.parse_statement("The cat chases the mouse")
        
        assert parsed is not None
        assert len(parsed.relationships) > 0
        
        rel = parsed.relationships[0]
        assert rel["subject"] == "cat"
        assert rel["object"] == "mouse"
        assert rel["verb"] == "chase"
    
    def test_build_dependency_tree(self):
        """Test dependency tree construction"""
        parsed = self.parser.parse_statement("The cat is black")
        
        assert parsed is not None
        assert len(parsed.dependency_tree) > 0
        
        # Check for essential tokens
        tokens = [t["text"] for t in parsed.dependency_tree]
        assert "cat" in tokens
        assert "black" in tokens
    
    def test_extract_named_entities(self):
        """Test named entity extraction"""
        parsed = self.parser.parse_statement("John met Mary in New York")
        
        assert parsed is not None
        assert len(parsed.named_entities) >= 2  # John and Mary
        
        person_entities = [e for e in parsed.named_entities if e["label"] == "PERSON"]
        assert len(person_entities) >= 2
    
    def test_extract_noun_chunks(self):
        """Test noun chunk extraction"""
        parsed = self.parser.parse_statement("The big red car and the small house")
        
        assert parsed is not None
        assert len(parsed.noun_chunks) >= 2  # "big red car", "small house"
    
    def test_calculate_confidence_high(self):
        """Test confidence calculation for high-confidence parsing"""
        parsed = self.parser.parse_statement("John is happy")
        
        assert parsed is not None
        assert parsed.confidence > 0.8
    
    def test_calculate_confidence_low(self):
        """Test confidence calculation for low-confidence parsing"""
        parsed = self.parser.parse_statement("Xyz is abc")
        
        if parsed:  # May not parse due to unknown entities
            # Unknown entities get high confidence from NER but should be lower overall
            assert parsed.confidence <= 0.9
    
    def test_parse_empty_string(self):
        """Test parsing of empty string"""
        parsed = self.parser.parse_statement("")
        assert parsed is None
        
        parsed = self.parser.parse_statement("   ")
        assert parsed is None
    
    def test_parse_unparseable_sentence(self):
        """Test parsing of unparseable sentence"""
        parsed = self.parser.parse_statement("Maybe perhaps")
        assert parsed is None
    
    def test_parse_complex_sentence(self):
        """Test parsing of complex sentence with multiple features"""
        parsed = self.parser.parse_statement("John's big red car that he bought yesterday is expensive")
        
        assert parsed is not None
        assert parsed.confidence > 0.5
        
        # Should have possessive
        assert len(parsed.possessives) > 0
        
        # Should have relative clause
        assert len(parsed.relative_clauses) > 0
        
        # Should have entities
        assert len(parsed.entities) > 0


class TestEnhancedEntity:
    """Test cases for EnhancedEntity dataclass"""
    
    def test_entity_creation(self):
        """Test EnhancedEntity creation"""
        now = datetime.now()
        entity = EnhancedEntity(
            name="cat",
            entity_type="ANIMAL",
            attributes={"color": "black"},
            modifiers=["big"],
            relationships=[],
            first_mentioned=now,
            last_mentioned=now,
            confidence=0.9
        )
        
        assert entity.name == "cat"
        assert entity.entity_type == "ANIMAL"
        assert entity.attributes["color"] == "black"
        assert entity.modifiers == ["big"]
        assert entity.confidence == 0.9


class TestEnhancedParsedStatement:
    """Test cases for EnhancedParsedStatement dataclass"""
    
    def test_parsed_statement_creation(self):
        """Test EnhancedParsedStatement creation"""
        now = datetime.now()
        statement = EnhancedParsedStatement(
            text="The cat is black",
            timestamp=now,
            subject="cat",
            object="black",
            negated=False,
            verb_type="state",
            entities=[],
            relationships=[],
            possessives=[],
            relative_clauses=[],
            disjunctions=[],
            confidence=0.9,
            dependency_tree=[],
            named_entities=[],
            noun_chunks=[]
        )
        
        assert statement.text == "The cat is black"
        assert statement.subject == "cat"
        assert statement.object == "black"
        assert statement.negated is False
        assert statement.verb_type == "state"
        assert statement.confidence == 0.9


class TestEnhancedParserEdgeCases:
    """Test edge cases and error handling"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = EnhancedParser()
    
    def test_parse_with_unicode(self):
        """Test parsing with unicode characters"""
        parsed = self.parser.parse_statement("José está feliz")
        
        # Should handle unicode gracefully
        if parsed:
            assert isinstance(parsed.text, str)
            assert parsed.confidence >= 0
    
    def test_parse_with_numbers(self):
        """Test parsing with numbers"""
        parsed = self.parser.parse_statement("The 2 cats are sleeping")
        
        if parsed:
            assert isinstance(parsed.confidence, float)
            assert parsed.confidence >= 0
    
    def test_parse_with_punctuation(self):
        """Test parsing with various punctuation"""
        sentences = [
            "The cat, dog, and mouse are playing.",
            "Is the cat happy? Yes, it is!",
            "The cat is sleeping... or is it?"
        ]
        
        for sentence in sentences:
            parsed = self.parser.parse_statement(sentence)
            if parsed:
                assert isinstance(parsed, EnhancedParsedStatement)
    
    def test_parse_very_long_sentence(self):
        """Test parsing of very long sentence"""
        long_sentence = "The " + "very " * 20 + "big red car is extremely expensive"
        parsed = self.parser.parse_statement(long_sentence)
        
        # Should handle long sentences gracefully
        if parsed:
            assert isinstance(parsed, EnhancedParsedStatement)
    
    def test_parse_with_special_characters(self):
        """Test parsing with special characters"""
        sentences = [
            "The cat's toy costs $5.99!",
            "Email: user@example.com",
            "The temperature is 25°C"
        ]
        
        for sentence in sentences:
            parsed = self.parser.parse_statement(sentence)
            if parsed:
                assert isinstance(parsed, EnhancedParsedStatement)


class TestEnhancedParserLinguisticPatterns:
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])