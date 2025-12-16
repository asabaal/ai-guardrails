#!/usr/bin/env python3
"""
Direct test to hit missing lines with step-by-step verification.
"""

import sys
import os
sys.path.insert(0, 'src')

from layer1_segmentation.text_segmenter import LLMTextSegmenter

def test_line_189():
    """Direct test to hit line 189."""
    print("=== Testing Line 189 ===")
    segmenter = LLMTextSegmenter()
    
    # Create response that should have empty lines after strip
    response = "1. First step\n   \n\t\n2. Second step\n   \n3. Third step"
    print(f"Input: {repr(response)}")
    
    # Manually go through the logic
    filtered_response = response.strip()
    print(f"After strip: {repr(filtered_response)}")
    
    lines = filtered_response.split('\n')
    print(f"Lines: {lines}")
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        print(f"Line {i}: {repr(line)} -> strip: {repr(line_stripped)} -> empty: {not line_stripped}")
        if not line_stripped:
            print(f"*** HIT LINE 189: continue on line {i} ***")
    
    # Now call the actual method
    result = segmenter._parse_llm_response(response)
    print(f"Result: {result}")
    print(f"Length: {len(result)}")

def test_lines_305_309():
    """Direct test to hit lines 305-309."""
    print("\n=== Testing Lines 305-309 ===")
    segmenter = LLMTextSegmenter()
    
    # Test with text that should split on connectors
    text = "First statement. However, second statement. Therefore, third statement."
    print(f"Input: {repr(text)}")
    
    # Now call the actual method and trace through it
    result = segmenter._fallback_segmentation(text)
    print(f"Actual result: {result}")
    print(f"Length: {len(result)}")
    
    # Test with simpler text that should definitely split
    simple_text = "First. However, second"
    print(f"\nSimple test: {repr(simple_text)}")
    simple_result = segmenter._fallback_segmentation(simple_text)
    print(f"Simple result: {simple_result}")
    print(f"Simple length: {len(simple_result)}")

if __name__ == "__main__":
    test_line_189()
    test_lines_305_309()