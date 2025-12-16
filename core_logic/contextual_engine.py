"""
Contextual Logic Engine - Phase 1.5
DMT Protocol: Done Means Taught - Conversation memory and entity tracking
"""
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Entity:
    """Represents a tracked entity with its attributes"""
    name: str
    attributes: Dict[str, Any]
    first_mentioned: datetime
    last_mentioned: datetime

@dataclass
class Statement:
    """Represents a parsed statement with context"""
    text: str
    parsed: Dict[str, Any]
    timestamp: datetime
    entities_mentioned: List[str]

class ConversationMemory:
    """Manages conversation state and entity tracking"""
    
    def __init__(self):
        self.statements: List[Statement] = []
        self.entities: Dict[str, Entity] = {}
        self.pronoun_map: Dict[str, str] = {}  # "it" -> "the cat"
        
    def add_statement(self, text: str, parsed: Dict[str, Any]) -> None:
        """Add a new statement to conversation memory"""
        timestamp = datetime.now()
        
        # Extract entities from parsed statement
        entities_mentioned = self._extract_entities(parsed)
        
        # Create statement record
        statement = Statement(
            text=text,
            parsed=parsed,
            timestamp=timestamp,
            entities_mentioned=entities_mentioned
        )
        
        self.statements.append(statement)
        
        # Update entity tracking
        self._update_entity_tracker(parsed, timestamp)
        
        # Update pronoun mappings
        self._update_pronoun_mapping(parsed, entities_mentioned)
    
    def _extract_entities(self, parsed: Dict[str, Any]) -> List[str]:
        """Extract entity names from parsed statement"""
        entities = []
        if parsed and 'subject' in parsed:
            subject = parsed['subject']
            # Clean up common articles and get core entity name
            core_subject = subject.replace('the ', '').replace('a ', '').replace('an ', '')
            entities.append(core_subject)
        return entities
    
    def _update_entity_tracker(self, parsed: Dict[str, Any], timestamp: datetime) -> None:
        """Update entity attributes based on parsed statement"""
        if not parsed or 'subject' not in parsed:
            return
            
        subject = parsed['subject']
        core_subject = subject.replace('the ', '').replace('a ', '').replace('an ', '')
        
        if core_subject not in self.entities:
            # New entity
            self.entities[core_subject] = Entity(
                name=core_subject,
                attributes={},
                first_mentioned=timestamp,
                last_mentioned=timestamp
            )
        
        # Update entity attributes
        entity = self.entities[core_subject]
        entity.last_mentioned = timestamp
        
        if 'object' in parsed:
            object_value = parsed['object']
            negated = parsed.get('negated', False)
            
            # Store attribute with negation state
            if negated:
                # Handle negated attributes
                entity.attributes[f"not_{object_value}"] = True
                # Remove positive version if it exists
                entity.attributes.pop(object_value, None)
            else:
                # Handle positive attributes
                entity.attributes[object_value] = True
                # Remove negated version if it exists
                entity.attributes.pop(f"not_{object_value}", None)
    
    def _update_pronoun_mapping(self, parsed: Dict[str, Any], entities_mentioned: List[str]) -> None:
        """Update pronoun-to-entity mappings"""
        if not parsed or 'subject' not in parsed:
            return
            
        subject = parsed['subject']
        
        # Map pronouns to the most recent entity
        pronouns = ['it', 'he', 'she', 'they', 'this', 'that']
        if subject.lower() in pronouns and entities_mentioned:
            # This shouldn't happen with proper parsing, but handle gracefully
            return
            
        # Map recent entities to pronouns for future resolution
        if entities_mentioned:
            latest_entity = entities_mentioned[-1]
            # Simple mapping - in real implementation would be more sophisticated
            if 'cat' in latest_entity.lower() or 'dog' in latest_entity.lower():
                self.pronoun_map['it'] = latest_entity
            elif 'man' in latest_entity.lower() or 'john' in latest_entity.lower():
                self.pronoun_map['he'] = latest_entity
            elif 'woman' in latest_entity.lower() or 'mary' in latest_entity.lower():
                self.pronoun_map['she'] = latest_entity
    
    def resolve_pronoun(self, pronoun: str) -> Optional[str]:
        """Resolve a pronoun to its entity reference"""
        return self.pronoun_map.get(pronoun.lower())
    
    def get_entity_attributes(self, entity_name: str) -> Dict[str, Any]:
        """Get all known attributes for an entity"""
        core_name = entity_name.replace('the ', '').replace('a ', '').replace('an ', '')
        entity = self.entities.get(core_name)
        return entity.attributes if entity else {}
    
    def get_conversation_context(self, last_n: int = 5) -> List[Dict[str, Any]]:
        """Get the last N statements for context"""
        recent_statements = self.statements[-last_n:] if self.statements else []
        return [
            {
                'text': stmt.text,
                'timestamp': stmt.timestamp,
                'parsed': stmt.parsed,
                'entities': stmt.entities_mentioned
            }
            for stmt in recent_statements
        ]

class ContextualLogicEngine:
    """Enhanced logic engine with conversation memory and context"""
    
    def __init__(self):
        self.memory = ConversationMemory()
        print("Contextual Logic Engine initialized with conversation memory.")
    
    def _parse_statement(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Parse a statement into structured format.
        Enhanced to handle more patterns than basic regex.
        """
        # Try specific patterns in order
        # X is not Y (must come before X is Y)
        match = re.match(r"(.+?)\s+is\s+not\s+(.+)", text, re.IGNORECASE)
        if match:
            subject = match.group(1).strip().lower()
            object_value = match.group(2).strip().lower()
            return {
                "subject": subject,
                "object": object_value,
                "negated": True,
                "verb_type": "state"
            }
        
        # X has/have Y
        match = re.match(r"(.+?)\s+(has|have)\s+(.+)", text, re.IGNORECASE)
        if match:
            subject = match.group(1).strip().lower()
            verb = match.group(2).strip().lower()
            # Extract object after the verb
            remaining_text = text.lower().split(verb, 1)[1].strip()
            return {
                "subject": subject,
                "object": remaining_text,
                "negated": False,
                "verb_type": "possession"
            }
        
        # X seems/appears/looks Y
        match = re.match(r"(.+?)\s+(seems|appears|looks)\s+(.+)", text, re.IGNORECASE)
        if match:
            subject = match.group(1).strip().lower()
            verb = match.group(2).strip().lower()
            # Extract object after the verb
            remaining_text = text.lower().split(verb, 1)[1].strip()
            return {
                "subject": subject,
                "object": remaining_text,
                "negated": False,
                "verb_type": "perception"
            }
        
        # X becomes/became Y
        match = re.match(r"(.+?)\s+(becomes|became)\s+(.+)", text, re.IGNORECASE)
        if match:
            subject = match.group(1).strip().lower()
            verb = match.group(2).strip().lower()
            # Extract object after the verb
            remaining_text = text.lower().split(verb, 1)[1].strip()
            return {
                "subject": subject,
                "object": remaining_text,
                "negated": False,
                "verb_type": "change"
            }
        
        # X is Y (must come last to avoid conflicts)
        match = re.match(r"(.+?)\s+is\s+(.+)", text, re.IGNORECASE)
        if match:
            subject = match.group(1).strip().lower()
            object_value = match.group(2).strip().lower()
            return {
                "subject": subject,
                "object": object_value,
                "negated": False,
                "verb_type": "state"
            }
        
        return None  # Couldn't parse sentence
    
    def _classify_verb(self, verb_phrase: str) -> str:
        """Classify the type of verb used"""
        if 'is' in verb_phrase or 'are' in verb_phrase:
            return 'state'
        elif 'has' in verb_phrase or 'have' in verb_phrase:
            return 'possession'
        elif 'seems' in verb_phrase or 'appears' in verb_phrase or 'looks' in verb_phrase:
            return 'perception'
        elif 'becomes' in verb_phrase or 'became' in verb_phrase:
            return 'change'
        else:
            return 'unknown'
    
    def process_statement(self, text: str) -> None:
        """
        Process a statement with full contextual awareness
        """
        parsed = self._parse_statement(text)
        if not parsed:
            print(f"  -> Could not understand: '{text}'")
            return
        
        # Resolve pronouns before processing
        if self._is_pronoun(parsed['subject']):
            resolved_subject = self.memory.resolve_pronoun(parsed['subject'])
            if resolved_subject:
                parsed['subject'] = resolved_subject
                print(f"  -> Resolved '{parsed['subject']}' from pronoun context")
        
        # Check for contradictions with existing knowledge
        contradiction_found = self._check_contextual_contradiction(parsed)
        
        if contradiction_found:
            print(f"  -> CONTEXTUAL CONTRADICTION DETECTED!")
            print(f"     You stated: '{text}'")
            print(f"     Contradicts: {contradiction_found['context']}")
        else:
            print(f"  -> OK (Contextually consistent): '{text}'")
        
        # Add to memory
        self.memory.add_statement(text, parsed)
    
    def _is_pronoun(self, subject: str) -> bool:
        """Check if subject is a pronoun"""
        pronouns = ['it', 'he', 'she', 'they', 'this', 'that']
        return subject.lower() in pronouns
    
    def _check_contextual_contradiction(self, parsed: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check for contradictions using contextual memory"""
        if not parsed or 'subject' not in parsed:
            return None
        
        subject = parsed['subject']
        core_subject = subject.replace('the ', '').replace('a ', '').replace('an ', '')
        
        # Get entity's current attributes
        entity_attrs = self.memory.get_entity_attributes(core_subject)
        
        if not entity_attrs:
            return None  # No prior knowledge about this entity
        
        # Check for contradictions
        object_value = parsed.get('object')
        is_negated = parsed.get('negated', False)
        
        if object_value:
            if is_negated:
                # Check if this contradicts a known positive attribute
                if entity_attrs.get(object_value):
                    return {
                        'type': 'negation_contradiction',
                        'context': f"Previously established: {subject} is {object_value}",
                        'new_statement': f"Now stating: {subject} is not {object_value}"
                    }
            else:
                # Check if this contradicts a known negative attribute
                negated_key = f"not_{object_value}"
                if entity_attrs.get(negated_key):
                    return {
                        'type': 'affirmation_contradiction', 
                        'context': f"Previously established: {subject} is not {object_value}",
                        'new_statement': f"Now stating: {subject} is {object_value}"
                    }
                
                # Check for semantic contradictions with existing positive attributes
                contradiction = self._check_semantic_contradiction(object_value, entity_attrs, subject)
                if contradiction:
                    return contradiction
        
        return None
    
    def _check_semantic_contradiction(self, new_object: str, entity_attrs: Dict[str, Any], subject: str) -> Optional[Dict[str, Any]]:
        """Check for semantic contradictions between states"""
        # Define semantic opposites
        semantic_opposites = {
            'sleeping': ['awake', 'awakened', 'conscious'],
            'awake': ['sleeping', 'asleep', 'unconscious'],
            'asleep': ['awake', 'awakened', 'conscious'],
            'conscious': ['sleeping', 'asleep', 'unconscious'],
            'unconscious': ['awake', 'awakened', 'conscious'],
            'hot': ['cold', 'cool', 'freezing'],
            'cold': ['hot', 'warm', 'boiling'],
            'warm': ['cold', 'cool', 'freezing'],
            'cool': ['hot', 'warm', 'boiling'],
            'big': ['small', 'tiny', 'little'],
            'small': ['big', 'large', 'huge'],
            'large': ['small', 'tiny', 'little'],
            'tiny': ['big', 'large', 'huge'],
            'happy': ['sad', 'unhappy', 'miserable'],
            'sad': ['happy', 'joyful', 'cheerful'],
            'empty': ['full', 'filled', 'occupied'],
            'full': ['empty', 'vacant', 'hollow'],
            'inside': ['outside', 'outdoors', 'exterior'],
            'outside': ['inside', 'indoors', 'interior'],
            'standing': ['sitting', 'lying', 'kneeling'],
            'sitting': ['standing', 'lying', 'kneeling'],
            'lying': ['standing', 'sitting', 'kneeling']
        }
        
        # Check if new object contradicts any existing attributes
        for existing_attr in entity_attrs.keys():
            if existing_attr.startswith('not_'):
                continue  # Skip negated attributes for now
            
            # Check direct opposites
            if new_object in semantic_opposites.get(existing_attr, []):
                return {
                    'type': 'semantic_contradiction',
                    'context': f"Previously established: {subject} is {existing_attr}",
                    'new_statement': f"Now stating: {subject} is {new_object}"
                }
            
            # Check reverse mapping
            if existing_attr in semantic_opposites.get(new_object, []):
                return {
                    'type': 'semantic_contradiction',
                    'context': f"Previously established: {subject} is {existing_attr}",
                    'new_statement': f"Now stating: {subject} is {new_object}"
                }
        
        return None
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the current conversation state"""
        return {
            'total_statements': len(self.memory.statements),
            'entities_tracked': len(self.memory.entities),
            'recent_context': self.memory.get_conversation_context(3),
            'entity_states': {
                name: attrs for name, attrs in self.memory.entities.items()
            }
        }

# --- How to run it ---
if __name__ == "__main__":
    engine = ContextualLogicEngine()
    
    conversation = [
        "The cat is on the mat",
        "It is sleeping",  # Should resolve "it" to "the cat"
        "The cat is awake",  # Should detect contradiction
        "The dog is brown",
        "He is hungry",  # Should resolve "he" to "the dog"
    ]
    
    for line in conversation:
        print(f"\nProcessing: '{line}'")
        engine.process_statement(line)
    
    print("\n--- Conversation Summary ---")
    summary = engine.get_conversation_summary()
    print(f"Total statements: {summary['total_statements']}")
    print(f"Entities tracked: {summary['entities_tracked']}")
    print("\nEntity states:")
    for entity_name, entity in summary['entity_states'].items():
        print(f"  {entity_name}: {entity.attributes}")