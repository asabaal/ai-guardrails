"""
Comprehensive test suite for ContextualLogicEngine
DMT Protocol: Done Means Taught - 100% coverage required
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from core_logic.contextual_engine import (
    ContextualLogicEngine, 
    ConversationMemory, 
    Entity, 
    Statement
)

class TestConversationMemory:
    """Test suite for ConversationMemory class"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.memory = ConversationMemory()
    
    def test_init_empty_memory(self):
        """Test memory initialization"""
        assert len(self.memory.statements) == 0
        assert len(self.memory.entities) == 0
        assert len(self.memory.pronoun_map) == 0
    
    def test_add_simple_statement(self):
        """Test adding a simple statement"""
        parsed = {"subject": "the cat", "object": "black", "negated": False}
        self.memory.add_statement("The cat is black", parsed)
        
        assert len(self.memory.statements) == 1
        assert len(self.memory.entities) == 1
        assert "cat" in self.memory.entities
        
        statement = self.memory.statements[0]
        assert statement.text == "The cat is black"
        assert statement.parsed == parsed
        assert statement.entities_mentioned == ["cat"]
    
    def test_entity_attribute_tracking(self):
        """Test entity attribute tracking"""
        # Add first statement
        parsed1 = {"subject": "the cat", "object": "black", "negated": False}
        self.memory.add_statement("The cat is black", parsed1)
        
        # Add second statement
        parsed2 = {"subject": "the cat", "object": "sleeping", "negated": False}
        self.memory.add_statement("The cat is sleeping", parsed2)
        
        entity = self.memory.entities["cat"]
        assert entity.attributes["black"] is True
        assert entity.attributes["sleeping"] is True
        assert entity.name == "cat"
    
    def test_negated_attribute_handling(self):
        """Test handling of negated attributes"""
        # Add positive statement
        parsed1 = {"subject": "the cat", "object": "black", "negated": False}
        self.memory.add_statement("The cat is black", parsed1)
        
        # Add negated statement
        parsed2 = {"subject": "the cat", "object": "black", "negated": True}
        self.memory.add_statement("The cat is not black", parsed2)
        
        entity = self.memory.entities["cat"]
        assert "black" not in entity.attributes
        assert entity.attributes["not_black"] is True
    
    def test_pronoun_mapping(self):
        """Test pronoun-to-entity mapping"""
        # Add entity first
        parsed = {"subject": "the cat", "object": "black", "negated": False}
        self.memory.add_statement("The cat is black", parsed)
        
        # Check pronoun mapping was created
        assert "it" in self.memory.pronoun_map
        assert self.memory.pronoun_map["it"] == "cat"
    
    def test_resolve_pronoun(self):
        """Test pronoun resolution"""
        # Setup mapping
        self.memory.pronoun_map["it"] = "cat"
        
        # Test resolution
        resolved = self.memory.resolve_pronoun("it")
        assert resolved == "cat"
        
        # Test non-existent pronoun
        unresolved = self.memory.resolve_pronoun("they")
        assert unresolved is None
    
    def test_get_entity_attributes(self):
        """Test getting entity attributes"""
        # Add entity with attributes
        parsed = {"subject": "the cat", "object": "black", "negated": False}
        self.memory.add_statement("The cat is black", parsed)
        
        attrs = self.memory.get_entity_attributes("cat")
        assert attrs["black"] is True
        
        # Test non-existent entity
        empty_attrs = self.memory.get_entity_attributes("dog")
        assert empty_attrs == {}
    
    def test_get_conversation_context(self):
        """Test getting conversation context"""
        # Add multiple statements
        statements = [
            ("The cat is black", {"subject": "the cat", "object": "black", "negated": False}),
            ("The dog is brown", {"subject": "the dog", "object": "brown", "negated": False}),
            ("The cat is sleeping", {"subject": "the cat", "object": "sleeping", "negated": False}),
        ]
        
        for text, parsed in statements:
            self.memory.add_statement(text, parsed)
        
        # Get last 2 statements
        context = self.memory.get_conversation_context(2)
        assert len(context) == 2
        assert context[0]["text"] == "The dog is brown"
        assert context[1]["text"] == "The cat is sleeping"
    
    def test_extract_entities(self):
        """Test entity extraction from parsed statements"""
        parsed = {"subject": "the cat", "object": "black", "negated": False}
        entities = self.memory._extract_entities(parsed)
        assert entities == ["cat"]
        
        # Test with article removal
        parsed2 = {"subject": "a dog", "object": "brown", "negated": False}
        entities2 = self.memory._extract_entities(parsed2)
        assert entities2 == ["dog"]

class TestContextualLogicEngine:
    """Test suite for ContextualLogicEngine class"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.engine = ContextualLogicEngine()
    
    def test_init_engine(self):
        """Test engine initialization"""
        assert self.engine.memory is not None
        assert len(self.engine.memory.statements) == 0
        assert len(self.engine.memory.entities) == 0
    
    def test_parse_basic_is_statement(self):
        """Test parsing basic 'is' statements"""
        result = self.engine._parse_statement("The cat is black")
        expected = {
            "subject": "the cat",
            "object": "black", 
            "negated": False,
            "verb_type": "state"
        }
        assert result == expected
    
    def test_parse_negated_is_statement(self):
        """Test parsing negated 'is' statements"""
        result = self.engine._parse_statement("The cat is not black")
        expected = {
            "subject": "the cat",
            "object": "black",
            "negated": True,
            "verb_type": "state"
        }
        assert result == expected
    
    def test_parse_has_statement(self):
        """Test parsing 'has' statements"""
        result = self.engine._parse_statement("The cat has black fur")
        expected = {
            "subject": "the cat",
            "object": "black fur",
            "negated": False,
            "verb_type": "possession"
        }
        assert result == expected
    
    def test_parse_seems_statement(self):
        """Test parsing 'seems' statements"""
        result = self.engine._parse_statement("The cat seems happy")
        expected = {
            "subject": "the cat",
            "object": "happy",
            "negated": False,
            "verb_type": "perception"
        }
        assert result == expected
    
    def test_parse_becomes_statement(self):
        """Test parsing 'becomes' statements"""
        result = self.engine._parse_statement("The cat becomes angry")
        expected = {
            "subject": "the cat",
            "object": "angry",
            "negated": False,
            "verb_type": "change"
        }
        assert result == expected
    
    def test_parse_unparseable_statement(self):
        """Test parsing unparseable statements"""
        result = self.engine._parse_statement("Random text without structure")
        assert result is None
    
    def test_classify_verb_state(self):
        """Test verb classification for state verbs"""
        assert self.engine._classify_verb("is") == "state"
        assert self.engine._classify_verb("are") == "state"
    
    def test_classify_verb_possession(self):
        """Test verb classification for possession verbs"""
        assert self.engine._classify_verb("has") == "possession"
        assert self.engine._classify_verb("have") == "possession"
    
    def test_classify_verb_perception(self):
        """Test verb classification for perception verbs"""
        assert self.engine._classify_verb("seems") == "perception"
        assert self.engine._classify_verb("appears") == "perception"
        assert self.engine._classify_verb("looks") == "perception"
    
    def test_classify_verb_change(self):
        """Test verb classification for change verbs"""
        assert self.engine._classify_verb("becomes") == "change"
        assert self.engine._classify_verb("became") == "change"
    
    def test_classify_verb_unknown(self):
        """Test verb classification for unknown verbs"""
        assert self.engine._classify_verb("jumps") == "unknown"
    
    def test_is_pronoun_detection(self):
        """Test pronoun detection"""
        assert self.engine._is_pronoun("it") is True
        assert self.engine._is_pronoun("he") is True
        assert self.engine._is_pronoun("she") is True
        assert self.engine._is_pronoun("they") is True
        assert self.engine._is_pronoun("this") is True
        assert self.engine._is_pronoun("that") is True
        assert self.engine._is_pronoun("cat") is False
    
    def test_process_simple_statement(self):
        """Test processing a simple statement"""
        with patch('builtins.print') as mock_print:
            self.engine.process_statement("The cat is black")
            
            # Should add to memory
            assert len(self.engine.memory.statements) == 1
            assert "cat" in self.engine.memory.entities
            
            # Should print success message
            mock_print.assert_any_call("  -> OK (Contextually consistent): 'The cat is black'")
    
    def test_process_unparseable_statement(self):
        """Test processing unparseable statement"""
        with patch('builtins.print') as mock_print:
            self.engine.process_statement("Random text")
            
            # Should not add to memory
            assert len(self.engine.memory.statements) == 0
            
            # Should print error message
            mock_print.assert_called_with("  -> Could not understand: 'Random text'")
    
    def test_process_pronoun_resolution(self):
        """Test processing statement with pronoun resolution"""
        # First establish entity
        self.engine.process_statement("The cat is black")
        
        # Then use pronoun
        with patch('builtins.print') as mock_print:
            self.engine.process_statement("It is sleeping")
            
            # Should print resolution message
            mock_print.assert_any_call("  -> Resolved 'cat' from pronoun context")
    
    def test_contextual_contradiction_detection(self):
        """Test detection of contextual contradictions"""
        # Establish initial state
        self.engine.process_statement("The cat is sleeping")
        
        # Try to contradict
        with patch('builtins.print') as mock_print:
            self.engine.process_statement("The cat is awake")
            
            # Should detect contradiction
            mock_print.assert_any_call("  -> CONTEXTUAL CONTRADICTION DETECTED!")
    
    def test_check_contextual_contradiction_positive(self):
        """Test contradiction detection for positive statements"""
        # Setup entity with negative attribute
        parsed = {"subject": "the cat", "object": "black", "negated": True}
        self.engine.memory.add_statement("The cat is not black", parsed)
        
        # Try to add positive
        new_parsed = {"subject": "the cat", "object": "black", "negated": False}
        contradiction = self.engine._check_contextual_contradiction(new_parsed)
        
        assert contradiction is not None
        assert contradiction['type'] == 'affirmation_contradiction'
    
    def test_check_contextual_contradiction_negative(self):
        """Test contradiction detection for negative statements"""
        # Setup entity with positive attribute
        parsed = {"subject": "the cat", "object": "black", "negated": False}
        self.engine.memory.add_statement("The cat is black", parsed)
        
        # Try to add negative
        new_parsed = {"subject": "the cat", "object": "black", "negated": True}
        contradiction = self.engine._check_contextual_contradiction(new_parsed)
        
        assert contradiction is not None
        assert contradiction['type'] == 'negation_contradiction'
    
    def test_check_no_contradiction(self):
        """Test no contradiction when attributes are different"""
        # Setup entity with one attribute
        parsed = {"subject": "the cat", "object": "black", "negated": False}
        self.engine.memory.add_statement("The cat is black", parsed)
        
        # Add different attribute
        new_parsed = {"subject": "the cat", "object": "sleeping", "negated": False}
        contradiction = self.engine._check_contextual_contradiction(new_parsed)
        
        assert contradiction is None
    
    def test_get_conversation_summary(self):
        """Test getting conversation summary"""
        # Add some statements
        self.engine.process_statement("The cat is black")
        self.engine.process_statement("The dog is brown")
        
        summary = self.engine.get_conversation_summary()
        
        assert summary['total_statements'] == 2
        assert summary['entities_tracked'] == 2
        assert 'recent_context' in summary
        assert 'entity_states' in summary
        assert 'cat' in summary['entity_states']
        assert 'dog' in summary['entity_states']

class TestEntityAndStatement:
    """Test suite for Entity and Statement dataclasses"""
    
    def test_entity_creation(self):
        """Test Entity dataclass creation"""
        now = datetime.now()
        entity = Entity(
            name="cat",
            attributes={"black": True},
            first_mentioned=now,
            last_mentioned=now
        )
        
        assert entity.name == "cat"
        assert entity.attributes["black"] is True
        assert entity.first_mentioned == now
        assert entity.last_mentioned == now
    
    def test_statement_creation(self):
        """Test Statement dataclass creation"""
        now = datetime.now()
        parsed = {"subject": "the cat", "object": "black", "negated": False}
        statement = Statement(
            text="The cat is black",
            parsed=parsed,
            timestamp=now,
            entities_mentioned=["cat"]
        )
        
        assert statement.text == "The cat is black"
        assert statement.parsed == parsed
        assert statement.timestamp == now
        assert statement.entities_mentioned == ["cat"]
    
    def test_update_entity_tracker_empty_parsed(self):
        """Test _update_entity_tracker with empty parsed data"""
        memory = ConversationMemory()
        memory._update_entity_tracker(None, datetime.now())
        memory._update_entity_tracker({}, datetime.now())
        # Should not raise any errors
        assert len(memory.entities) == 0
    
    def test_update_pronoun_mapping_empty_parsed(self):
        """Test _update_pronoun_mapping with empty parsed data"""
        memory = ConversationMemory()
        memory._update_pronoun_mapping(None, [])
        memory._update_pronoun_mapping({}, [])
        # Should not raise any errors
        assert len(memory.pronoun_map) == 0
    
    def test_update_pronoun_mapping_no_entities_mentioned(self):
        """Test _update_pronoun_mapping with no entities mentioned"""
        memory = ConversationMemory()
        parsed = {"subject": "it"}  # pronoun but no entities mentioned
        memory._update_pronoun_mapping(parsed, [])
        # Should return early without mapping
        assert len(memory.pronoun_map) == 0
    
    def test_update_pronoun_mapping_pronoun_with_entities(self):
        """Test _update_pronoun_mapping with pronoun subject and entities mentioned"""
        memory = ConversationMemory()
        # This case shouldn't happen with proper parsing but we test the graceful handling
        parsed = {"subject": "it"}  # pronoun as subject
        entities_mentioned = ["cat"]  # but entities were mentioned
        memory._update_pronoun_mapping(parsed, entities_mentioned)
        # Should return early without mapping due to pronoun subject
        assert len(memory.pronoun_map) == 0
    
    def test_check_contextual_contradiction_empty_parsed(self):
        """Test _check_contextual_contradiction with empty parsed data"""
        engine = ContextualLogicEngine()
        result1 = engine._check_contextual_contradiction(None)
        result2 = engine._check_contextual_contradiction({})
        # Should return None for both cases
        assert result1 is None
        assert result2 is None
    
    def test_check_semantic_contradiction_negated_attributes(self):
        """Test _check_semantic_contradiction with negated attributes"""
        engine = ContextualLogicEngine()
        entity_attrs = {"not_black": True, "white": True}
        result = engine._check_semantic_contradiction("black", entity_attrs, "the cat")
        # Should skip negated attributes and find contradiction with white
        # Note: white and black are not semantic opposites in our current mapping
        # Let's use a pair that is actually mapped
        entity_attrs_opposites = {"not_awake": True, "sleeping": True}
        result_opposites = engine._check_semantic_contradiction("awake", entity_attrs_opposites, "the cat")
        assert result_opposites is not None
        assert result_opposites['type'] == 'semantic_contradiction'
    
    def test_check_semantic_contradiction_no_contradiction(self):
        """Test _check_semantic_contradiction with no contradictions"""
        engine = ContextualLogicEngine()
        entity_attrs = {"black": True, "large": True}
        result = engine._check_semantic_contradiction("black", entity_attrs, "the cat")
        # Should return None since black doesn't contradict black or large
        assert result is None
    
    def test_update_pronoun_mapping_gender_specific(self):
        """Test _update_pronoun_mapping with gender-specific pronouns"""
        memory = ConversationMemory()
        
        # Test male pronoun mapping
        parsed_man = {"subject": "the man"}
        memory._update_pronoun_mapping(parsed_man, ["man"])
        assert memory.pronoun_map.get("he") == "man"
        
        # Test female pronoun mapping
        parsed_woman = {"subject": "mary"}
        memory._update_pronoun_mapping(parsed_woman, ["mary"])
        assert memory.pronoun_map.get("she") == "mary"
        
        # Test neutral pronoun mapping
        parsed_cat = {"subject": "the cat"}
        memory._update_pronoun_mapping(parsed_cat, ["cat"])
        assert memory.pronoun_map.get("it") == "cat"
    
    def test_check_semantic_contradiction_reverse_mapping(self):
        """Test _check_semantic_contradiction with reverse mapping"""
        engine = ContextualLogicEngine()
        # Set up entity with "awake" attribute
        entity_attrs = {"awake": True}
        # Check if "sleeping" contradicts "awake" (reverse mapping)
        result = engine._check_semantic_contradiction("sleeping", entity_attrs, "the cat")
        assert result is not None
        assert result['type'] == 'semantic_contradiction'
        assert "awake" in result['context']
        assert "sleeping" in result['new_statement']
    
    def test_check_semantic_contradiction_specific_reverse_case(self):
        """Test specific case that triggers line 366 reverse mapping"""
        engine = ContextualLogicEngine()
        # Use a pair where existing_attr is in new_object's opposites list
        # This should trigger reverse mapping check on line 365-366
        entity_attrs = {"hot": True}  # existing attribute
        result = engine._check_semantic_contradiction("cold", entity_attrs, "the water")
        # This should find that "hot" is in semantic_opposites["cold"]
        assert result is not None
        assert result['type'] == 'semantic_contradiction'
        assert result['context'] == "Previously established: the water is hot"
        assert result['new_statement'] == "Now stating: the water is cold"
    
    def test_check_semantic_contradiction_line_366_direct(self):
        """Direct test to ensure line 366 (return statement) is executed"""
        engine = ContextualLogicEngine()
        # Create scenario where we hit reverse mapping return on line 366
        # Use asymmetric case: existing_attr="awakened" is in semantic_opposites.get("sleeping", [])
        # BUT "sleeping" is NOT in semantic_opposites.get("awakened", [])
        # This ensures we hit line 366 (reverse mapping) but NOT line 357 (direct mapping)
        entity_attrs = {"awakened": True}
        result = engine._check_semantic_contradiction("sleeping", entity_attrs, "the cat")
        
        # Verify we get the expected contradiction
        assert result is not None
        assert result['type'] == 'semantic_contradiction'
        
        # Verify exact structure to ensure line 366 was executed
        expected_context = "Previously established: the cat is awakened"
        expected_new = "Now stating: the cat is sleeping"
        assert result['context'] == expected_context
        assert result['new_statement'] == expected_new
    
    def test_check_semantic_contradiction_line_358_direct(self):
        """Direct test to ensure line 358 (direct mapping return statement) is executed"""
        engine = ContextualLogicEngine()
        # Create scenario where we hit direct mapping return on line 358
        # existing_attr="sleeping" and new_object="awake" 
        # "awake" is in semantic_opposites.get("sleeping", [])
        # This ensures we hit line 358 (direct mapping)
        entity_attrs = {"sleeping": True}
        result = engine._check_semantic_contradiction("awake", entity_attrs, "the cat")
        
        # Verify we get the expected contradiction
        assert result is not None
        assert result['type'] == 'semantic_contradiction'
        
        # Verify exact structure to ensure line 358 was executed
        expected_context = "Previously established: the cat is sleeping"
        expected_new = "Now stating: the cat is awake"
        assert result['context'] == expected_context
        assert result['new_statement'] == expected_new

if __name__ == "__main__":
    pytest.main([__file__, "-v"])