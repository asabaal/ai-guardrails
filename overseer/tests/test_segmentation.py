#!/usr/bin/env python3
"""
Test Layer 1: Text Segmentation Components

Tests the text segmentation components including:
- LLMTextSegmenter
- RuleBasedSplitter  
- Normalizer
- Aggregator
"""

import sys
import os
import json
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from layer1_segmentation.text_segmenter import LLMTextSegmenter, RuleBasedSplitter, Normalizer, Aggregator

def test_llm_segmenter():
    """Test LLM Text Segmenter functionality."""
    print("Testing LLM Text Segmenter...")
    print("=" * 50)
    
    config = {
        'model_name': 'gpt-oss:20b',
        'max_retries': 1,
        'timeout': 60
    }
    
    segmenter = LLMTextSegmenter(config)
    normalizer = Normalizer()
    aggregator = Aggregator()
    
    # Test cases
    test_cases = [
        "Apples contain fiber. Fiber supports digestion. Therefore, apples support digestion.",
        "If it rains, then the ground gets wet. It is raining. Therefore, the ground is wet.",
        "All humans are mortal. Socrates is human. Therefore, Socrates is mortal."
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\nTest {i}: {text[:60]}...")
        
        try:
            # Test segmentation
            segments = segmenter.segment(text)
            normalized = normalizer.normalize(segments)
            
            if normalized:
                print(f"✅ PASS - {len(normalized)} segments generated")
                print(f"   First segment: {normalized[0]}")
                passed += 1
            else:
                print("❌ FAIL - No segments generated")
                
        except Exception as e:
            print(f"❌ ERROR - {e}")
    
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} tests passed")
    return passed == total

def test_rule_based_splitter():
    """Test Rule Based Splitter functionality."""
    print("\nTesting Rule Based Splitter...")
    print("=" * 50)
    
    splitter = RuleBasedSplitter()
    normalizer = Normalizer()
    
    test_text = "Apples contain fiber. Therefore, apples support digestion."
    
    try:
        segments = splitter.segment(test_text)
        normalized = normalizer.normalize(segments)
        
        print(f"Input: {test_text}")
        print(f"Segments: {len(normalized)}")
        for i, segment in enumerate(normalized, 1):
            print(f"  {i}. {segment}")
        
        return len(normalized) > 0
        
    except Exception as e:
        print(f"❌ ERROR - {e}")
        return False

def test_normalizer():
    """Test Normalizer functionality."""
    print("\nTesting Normalizer...")
    print("=" * 50)
    
    normalizer = Normalizer()
    
    test_segments = [
        "apples contain fiber",
        "fiber supports digestion", 
        "apples support digestion"
    ]
    
    try:
        normalized = normalizer.normalize(test_segments)
        print(f"Input segments: {len(test_segments)}")
        print(f"Normalized segments: {len(normalized)}")
        
        for i, segment in enumerate(normalized, 1):
            print(f"  {i}. {segment}")
            
        return len(normalized) == len(test_segments)
        
    except Exception as e:
        print(f"❌ ERROR - {e}")
        return False

def test_aggregator():
    """Test Aggregator functionality."""
    print("\nTesting Aggregator...")
    print("=" * 50)
    
    config = {'prefer_llm': True}
    aggregator = Aggregator(config)
    
    llm_segments = ["Apples contain fiber.", "Fiber supports digestion.", "Therefore, apples support digestion."]
    rule_segments = ["Apples contain fiber", "Therefore, apples support digestion"]
    
    try:
        result = aggregator.aggregate(llm_segments, rule_segments)
        print(f"LLM segments: {len(llm_segments)}")
        print(f"Rule segments: {len(rule_segments)}")
        print(f"Aggregated segments: {len(result)}")
        
        for i, segment in enumerate(result, 1):
            print(f"  {i}. {segment}")
            
        return len(result) > 0
        
    except Exception as e:
        print(f"❌ ERROR - {e}")
        return False

def main():
    """Run all Layer 1 tests."""
    print("Layer 1: Text Segmentation Tests")
    print("=" * 60)
    
    results = []
    
    # Test individual components
    results.append(("LLM Segmenter", test_llm_segmenter()))
    results.append(("Rule Based Splitter", test_rule_based_splitter()))
    results.append(("Normalizer", test_normalizer()))
    results.append(("Aggregator", test_aggregator()))
    
    # Summary
    print(f"\n{'='*60}")
    print("LAYER 1 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} test suites passed")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    return passed == total

if __name__ == "__main__":
    main()