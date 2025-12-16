#!/usr/bin/env python3
"""
Debug script to understand modifier extraction
"""

import spacy

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Test sentence
sentence = "The big happy dog is sleeping"
doc = nlp(sentence)

print(f"Sentence: {sentence}")
print("=" * 50)

print("Noun Chunks:")
for chunk in doc.noun_chunks:
    print(f"Chunk: '{chunk.text}'")
    print(f"  Root: {chunk.root.text}")
    print(f"  Root dep: {chunk.root.dep_}")
    print(f"  Tokens in chunk:")
    for token in chunk:
        print(f"    {token.text} - POS: {token.pos_}, Dep: {token.dep_}")
    print()

print("All tokens with POS:")
for token in doc:
    print(f"{token.text} - POS: {token.pos_}, Dep: {token.dep_}, Head: {token.head.text}")
    print(f"  Children: {[f'{child.text}({child.dep_})' for child in token.children]}")
    print()