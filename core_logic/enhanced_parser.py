"""
Enhanced Parser Module for Advanced Linguistic Analysis

This module extends basic parsing with:
- Named Entity Recognition (NER)
- Compound entity handling
- Possessive parsing
- Relative clause analysis
- Complex sentence structures
"""

import spacy
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class EnhancedEntity:
    """Enhanced entity with additional metadata"""
    name: str
    entity_type: str  # PERSON, ORG, GPE, etc.
    attributes: Dict[str, Any]
    modifiers: List[str]  # adjectives, descriptors
    relationships: List[Dict[str, str]]  # relationships to other entities
    first_mentioned: datetime
    last_mentioned: datetime
    confidence: float  # confidence score for entity recognition


@dataclass
class EnhancedParsedStatement:
    """Enhanced parsed statement with advanced linguistic features"""
    text: str
    timestamp: datetime
    
    # Basic parsing
    subject: Optional[str]
    object: Optional[str] 
    negated: bool
    verb_type: str
    
    # Enhanced features
    entities: List[EnhancedEntity]
    relationships: List[Dict[str, str]]
    possessives: List[Dict[str, str]]
    relative_clauses: List[Dict[str, str]]
    disjunctions: List[str]  # either/or options
    confidence: float
    
    # Linguistic features
    dependency_tree: List[Dict[str, Any]]
    named_entities: List[Dict[str, str]]
    noun_chunks: List[str]


class EnhancedParser:
    """Enhanced parser with advanced NLP capabilities"""
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """Initialize enhanced parser with spaCy model"""
        try:
            self.nlp = spacy.load(model_name)
            print(f"Enhanced Parser initialized with spaCy model: {model_name}")
        except OSError:
            print(f"Downloading spaCy model: {model_name}")
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "spacy", "download", model_name])
            self.nlp = spacy.load(model_name)
            print(f"Enhanced Parser initialized with spaCy model: {model_name}")
    
    def parse_statement(self, text: str) -> Optional[EnhancedParsedStatement]:
        """
        Parse a statement with enhanced linguistic analysis
        
        Args:
            text: Input statement to parse
            
        Returns:
            EnhancedParsedStatement with detailed linguistic information
        """
        if not text or not text.strip():
            return None
            
        # Process with spaCy
        doc = self.nlp(text)
        
        # Extract basic parsing (reuse existing logic)
        basic_parsed = self._extract_basic_parse(doc)
        if not basic_parsed:
            return None
            
        # Extract enhanced features
        entities = self._extract_entities(doc)
        relationships = self._extract_relationships(doc)
        possessives = self._extract_possessives(doc)
        relative_clauses = self._extract_relative_clauses(doc)
        disjunctions = self._extract_disjunctions(doc)
        
        # Extract linguistic features
        dependency_tree = self._build_dependency_tree(doc)
        named_entities = self._extract_named_entities(doc)
        noun_chunks = self._extract_noun_chunks(doc)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(basic_parsed, entities, relationships)
        
        return EnhancedParsedStatement(
            text=text,
            timestamp=datetime.now(),
            subject=basic_parsed.get('subject'),
            object=basic_parsed.get('object'),
            negated=basic_parsed.get('negated', False),
            verb_type=basic_parsed.get('verb_type', 'unknown'),
            entities=entities,
            relationships=relationships,
            possessives=possessives,
            relative_clauses=relative_clauses,
            disjunctions=disjunctions,
            confidence=confidence,
            dependency_tree=dependency_tree,
            named_entities=named_entities,
            noun_chunks=noun_chunks
        )
    
    def _extract_basic_parse(self, doc) -> Optional[Dict[str, Any]]:
        """Extract basic parsing information (reuse existing logic)"""
        # Handle negation first
        negated = any(token.dep_ == "neg" for token in doc)
        
        # Extract subject and object
        subject = None
        object_value = None
        
        for token in doc:
            if token.dep_ == "nsubj":
                subject = token.text.lower()
            elif token.dep_ in ["attr", "acomp", "dobj"]:
                object_value = token.text.lower()
        
        # If no subject/object found, try noun chunks
        if not subject:
            for chunk in doc.noun_chunks:
                if chunk.root.dep_ == "nsubj":
                    subject = chunk.text.lower()
                    break
        
        if not object_value:
            for chunk in doc.noun_chunks:
                if chunk.root.dep_ in ["attr", "acomp", "dobj"]:
                    object_value = chunk.text.lower()
                    break
        
        # Special handling for sentences without clear objects
        if not object_value:
            # Look for intransitive verbs with no complement (e.g., "The dog is sleeping")
            for token in doc:
                if token.pos_ == "VERB" and self._is_intransitive_in_context(token, doc):
                    object_value = token.lemma_.lower()  # Use verb as object
                    break
        
        # Handle compound subjects with disjunctions
        if not object_value and subject:
            # For "Either the cat or the dog is sleeping", use verb as object
            # But only if the verb is truly intransitive (no prepositional phrases)
            for token in doc:
                if token.pos_ == "VERB" and token.dep_ == "ROOT" and self._is_intransitive_in_context(token, doc):
                    object_value = token.lemma_.lower()
                    break
        
        # Handle conjunctions without main verb (e.g., "The big red car and the small house")
        if not object_value and not any(token.pos_ == "VERB" for token in doc):
            # This is a noun phrase conjunction, not a full sentence
            # Use the first noun as subject and "conjunction" as object
            if subject:
                object_value = "conjunction"
            else:
                # If no subject found, use first noun chunk as subject
                for chunk in doc.noun_chunks:
                    if chunk.root.dep_ == "ROOT":
                        subject = chunk.text.lower()
                        object_value = "conjunction"
                        break
        
        if not subject or not object_value:
            return None
            
        # Classify verb type
        verb_type = self._classify_verb(doc)
        
        return {
            "subject": subject,
            "object": object_value,
            "negated": negated,
            "verb_type": verb_type
        }
    
    def _classify_verb(self, doc) -> str:
        """Classify the type of verb used"""
        for token in doc:
            if token.pos_ in ["VERB", "AUX"]:  # Include auxiliary verbs
                lemma = token.lemma_.lower()
                if lemma in ['be', 'is', 'are', 'was', 'were']:
                    return 'state'
                elif lemma in ['have', 'has', 'had']:
                    return 'possession'
                elif lemma in ['seem', 'appear', 'look']:
                    return 'perception'
                elif lemma in ['become', 'became', 'turn']:
                    return 'change'
        return 'unknown'
    
    def _extract_entities(self, doc) -> List[EnhancedEntity]:
        """Extract enhanced entities with NER and compound handling"""
        entities = []
        now = datetime.now()
        
        # Extract named entities
        for ent in doc.ents:
            entity = EnhancedEntity(
                name=ent.text.lower(),
                entity_type=ent.label_,
                attributes={},
                modifiers=self._extract_modifiers_for_entity(ent, doc),
                relationships=[],
                first_mentioned=now,
                last_mentioned=now,
                confidence=self._calculate_entity_confidence(ent)
            )
            entities.append(entity)
        
        # Extract compound noun phrases that aren't named entities
        noun_chunks = [chunk.text.lower() for chunk in doc.noun_chunks]
        named_entity_texts = [ent.text.lower() for ent in doc.ents]
        
        for chunk in noun_chunks:
            if chunk not in named_entity_texts and len(chunk.split()) > 1:
                # Create a temporary entity object for modifier extraction
                temp_entity = type('TempEntity', (), {'name': chunk})()
                modifiers = self._extract_modifiers_for_entity(temp_entity, doc)
                
                entity = EnhancedEntity(
                    name=chunk,
                    entity_type="COMPOUND",
                    attributes={},
                    modifiers=modifiers,
                    relationships=[],
                    first_mentioned=now,
                    last_mentioned=now,
                    confidence=0.7  # moderate confidence for compounds
                )
                entities.append(entity)
        
        return entities
    
    def _extract_modifiers_for_entity(self, entity, doc) -> List[str]:
        """Extract adjectives and modifiers for a specific entity using linguistic analysis"""
        modifiers = []
        
        # For named entities, use dependency parsing to find adjectival modifiers
        if hasattr(entity, 'start'):
            # Find the entity span in the document
            entity_span = doc[entity.start:entity.end]
            
            # Look for adjectival modifiers (amod) that modify this entity
            for token in entity_span:
                # Find children that are adjectives modifying this token
                for child in token.children:
                    if child.dep_ == "amod" and child.pos_ == "ADJ":
                        modifiers.append(child.text.lower())
                
                # Find adjectives before the entity in the dependency tree
                if token.head.dep_ == "amod" and token.head.pos_ == "ADJ":
                    modifiers.append(token.head.text.lower())
                
                # Handle compound words within the entity (like "Tall John")
                if token.dep_ == "compound":
                    modifiers.append(token.text.lower())
            
            # Also check for adjectives immediately before the entity (fallback)
            start = entity.start
            for i in range(max(0, start-3), start):
                token = doc[i]
                if token.pos_ == "ADJ" and (i+1 >= start or doc[i+1].pos_ == "DET"):
                    modifiers.append(token.text.lower())
                # Also handle compound proper nouns (like "Tall John")
                elif token.dep_ == "compound" and i+1 < len(doc) and doc[i+1].ent_type:
                    modifiers.append(token.text.lower())
        else:
            # For compound entities, analyze the actual document structure
            # Find the noun chunk that matches this entity
            for chunk in doc.noun_chunks:
                if chunk.text.lower() == entity.name.lower():
                    # Extract adjectives from this noun chunk
                    for token in chunk:
                        if token.pos_ == "ADJ":
                            modifiers.append(token.text.lower())
                    
                    # Also check for adjectival modifiers of the chunk root
                    for child in chunk.root.children:
                        if child.dep_ == "amod" and child.pos_ == "ADJ":
                            modifiers.append(child.text.lower())
                    break
            
            # If no exact match found, try to find partial matches and extract adjectives
            if not modifiers:
                # Split entity name and look for adjectives in the document
                entity_words = entity.name.split()
                for word in entity_words:
                    # Find tokens that match this word and check if they're adjectives
                    for token in doc:
                        if token.text.lower() == word.lower() and token.pos_ == "ADJ":
                            modifiers.append(word.lower())
        
        return list(set(modifiers))  # Remove duplicates
    
    def _extract_relationships(self, doc) -> List[Dict[str, str]]:
        """Extract relationships between entities"""
        relationships = []
        
        # Simple subject-object relationships
        for token in doc:
            if token.dep_ == "nsubj" and token.head.pos_ == "VERB":
                subject = token.text.lower()
                verb = token.head.lemma_.lower()
                
                # Find object
                for child in token.head.children:
                    if child.dep_ in ["dobj", "attr", "acomp"]:
                        obj = child.text.lower()
                        relationships.append({
                            "type": "subject_verb_object",
                            "subject": subject,
                            "verb": verb,
                            "object": obj
                        })
        
        return relationships
    
    def _extract_possessives(self, doc) -> List[Dict[str, str]]:
        """Extract possessive relationships"""
        possessives = []
        
        for token in doc:
            if token.dep_ == "poss":
                possessor = token.text.lower()
                possessed = token.head.text.lower()  # The head is what is possessed
                
                possessives.append({
                    "type": "possessive",
                    "possessor": possessor,
                    "possessed": possessed,
                    "full_phrase": f"{possessor} {possessed}"
                })
        
        return possessives
    
    def _extract_relative_clauses(self, doc) -> List[Dict[str, str]]:
        """Extract relative clauses (that, which, who, etc.)"""
        relative_clauses = []
        
        for token in doc:
            if token.tag_ in ["WDT", "WP", "WRB"]:  # that, which, who, where, when
                # Find the head noun this clause modifies
                head = token.head
                while head and head.pos_ != "NOUN":
                    head = head.head
                    if head == token:
                        break
                
                if head:
                    clause_text = " ".join([t.text for t in token.subtree])
                    relative_clauses.append({
                        "type": "relative_clause",
                        "relative_pronoun": token.text.lower(),
                        "modified_noun": head.text.lower(),
                        "clause": clause_text.lower()
                    })
        
        return relative_clauses
    
    def _extract_disjunctions(self, doc) -> List[str]:
        """Extract either/or disjunctions"""
        disjunctions = []
        
        # Look for "either...or" patterns
        either_or_pattern = r"either\s+(.+?)\s+or\s+(.+)"
        match = re.search(either_or_pattern, doc.text.lower())
        if match:
            disjunctions.extend([match.group(1).strip(), match.group(2).strip()])
            return disjunctions
        
        # Look for simple "or" conjunctions - extract just the nouns
        for i, token in enumerate(doc):
            if token.text.lower() == "or" and token.dep_ == "cc":
                # Find noun before "or"
                left_noun = None
                for j in range(i-1, -1, -1):
                    if doc[j].pos_ == "NOUN":
                        left_noun = doc[j].text.lower()
                        break
                
                # Find noun after "or"
                right_noun = None
                for j in range(i+1, len(doc)):
                    if doc[j].pos_ == "NOUN":
                        right_noun = doc[j].text.lower()
                        break
                
                if left_noun and right_noun:
                    disjunctions.extend([left_noun, right_noun])
        
        return disjunctions
    
    def _build_dependency_tree(self, doc) -> List[Dict[str, Any]]:
        """Build dependency tree representation"""
        tree = []
        for token in doc:
            tree.append({
                "text": token.text,
                "lemma": token.lemma_,
                "pos": token.pos_,
                "tag": token.tag_,
                "dep": token.dep_,
                "head": token.head.text if token.head != token else "ROOT",
                "children": [child.text for child in token.children]
            })
        return tree
    
    def _extract_named_entities(self, doc) -> List[Dict[str, Any]]:
        """Extract named entities with types"""
        return [
            {
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
                "confidence": self._calculate_entity_confidence(ent)
            }
            for ent in doc.ents
        ]
    
    def _extract_noun_chunks(self, doc) -> List[str]:
        """Extract noun chunks"""
        return [chunk.text.lower() for chunk in doc.noun_chunks]
    
    def _calculate_confidence(self, basic_parsed, entities, relationships) -> float:
        """Calculate overall parsing confidence score"""
        confidence = 0.0
        
        # Basic parsing confidence
        if basic_parsed:
            confidence += 0.4
        
        # Entity confidence
        if entities:
            confidence += 0.3
            entity_conf = sum(e.confidence for e in entities) / len(entities)
            confidence += 0.2 * entity_conf
        
        # Relationship confidence
        if relationships:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _calculate_entity_confidence(self, entity) -> float:
        """Calculate confidence score for entity recognition"""
        base_confidence = 0.5
        
        # Named entities get higher confidence
        if hasattr(entity, 'label_'):
            if entity.label_ in ["PERSON", "ORG", "GPE"]:
                base_confidence = 0.9
            elif entity.label_ in ["DATE", "TIME", "MONEY"]:
                base_confidence = 0.8
            else:
                base_confidence = 0.7
        
        # Length bonus
        if len(entity.text) > 1:
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def _is_intransitive_in_context(self, token, doc) -> bool:
        """
        Determine if a verb is being used intransitively in this specific context
        
        Uses linguistic analysis rather than hardcoded verb lists:
        1. Check if verb already has direct object children in current sentence
        2. Analyze sentence structure for object expectations
        3. Use dependency parsing to determine grammatical requirements
        """
        # 1. Check if verb already has direct object children in current sentence
        has_direct_object = any(child.dep_ in ["dobj", "attr", "acomp"] for child in token.children)
        if has_direct_object:
            return False
        
        # 2. Check for indirect objects that might imply transitivity
        has_indirect_object = any(child.dep_ == "iobj" for child in token.children)
        if has_indirect_object:
            return False
        
        # 3. Check for prepositional phrases that might serve as objects
        # Prepositional phrases attached to the verb suggest transitive use
        prep_objects = [child for child in token.children if child.dep_ == "prep"]
        if prep_objects:
            # Has prepositional objects - likely transitive
            return False
        
        # 4. Default to intransitive if no evidence of transitivity found
        return True


# --- How to run it ---
if __name__ == "__main__":
    parser = EnhancedParser()
    
    test_sentences = [
        "The big red car that John bought yesterday is expensive",
        "Either the cat or the dog is sleeping",
        "Mary's cat seems very happy",
        "The company's new product becomes successful",
        "The tall man who lives next door is friendly"
    ]
    
    for sentence in test_sentences:
        print(f"\n{'='*60}")
        print(f"Analyzing: '{sentence}'")
        print('='*60)
        
        parsed = parser.parse_statement(sentence)
        if parsed:
            print(f"Subject: {parsed.subject}")
            print(f"Object: {parsed.object}")
            print(f"Negated: {parsed.negated}")
            print(f"Verb Type: {parsed.verb_type}")
            print(f"Confidence: {parsed.confidence:.2f}")
            
            print(f"\nEntities ({len(parsed.entities)}):")
            for entity in parsed.entities:
                print(f"  - {entity.name} ({entity.entity_type}) - confidence: {entity.confidence:.2f}")
                if entity.modifiers:
                    print(f"    Modifiers: {entity.modifiers}")
            
            if parsed.relationships:
                print(f"\nRelationships ({len(parsed.relationships)}):")
                for rel in parsed.relationships:
                    print(f"  - {rel['subject']} -> {rel['verb']} -> {rel['object']}")
            
            if parsed.possessives:
                print(f"\nPossessives ({len(parsed.possessives)}):")
                for poss in parsed.possessives:
                    print(f"  - {poss['possessor']} -> {poss['possessed']}")
            
            if parsed.relative_clauses:
                print(f"\nRelative Clauses ({len(parsed.relative_clauses)}):")
                for clause in parsed.relative_clauses:
                    print(f"  - {clause['relative_pronoun']} modifies '{clause['modified_noun']}': {clause['clause']}")
            
            if parsed.disjunctions:
                print(f"\nDisjunctions: {parsed.disjunctions}")
        else:
            print("Could not parse sentence")