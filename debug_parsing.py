#!/usr/bin/env python3
"""
Debug script to understand spaCy dependency parsing
"""

import spacy

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Test sentence
sentence = "The cat sleeps on the mat"
doc = nlp(sentence)

print(f"Sentence: {sentence}")
print("=" * 50)

for token in doc:
    print(f"Token: {token.text}")
    print(f"  Lemma: {token.lemma_}")
    print(f"  POS: {token.pos_}")
    print(f"  Dep: {token.dep_}")
    print(f"  Head: {token.head.text}")
    print(f"  Children: {[child.text for child in token.children]}")
    print()

# Focus on the verb
verb_token = None
for token in doc:
    if token.pos_ == "VERB":
        verb_token = token
        break

if verb_token:
    print(f"Verb Analysis: {verb_token.text}")
    print("=" * 30)
    
    # Check for direct objects
    direct_objects = [child for child in verb_token.children if child.dep_ in ["dobj", "attr", "acomp"]]
    print(f"Direct objects: {direct_objects}")
    
    # Check for prepositional phrases
    prep_phrases = [child for child in verb_token.children if child.dep_ == "prep"]
    print(f"Prepositional phrases: {prep_phrases}")
    
    # Check all children
    all_children = list(verb_token.children)
    print(f"All children: {all_children}")
    
    # Check if any child is a preposition
    has_prep = any(child.dep_ == "prep" for child in verb_token.children)
    print(f"Has preposition: {has_prep}")