#!/usr/bin/env python3
"""
Test script for LLM text segmentation
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from layer1_segmentation.text_segmenter import LLMTextSegmenter

def test_llm_segmentation():
    """Test the LLM segmentation with sample text."""
    
    # Test text from the test cases
    test_text = """Apples contain fiber. Fiber supports digestion. Therefore, apples support digestion."""
    
    print("Testing LLM Text Segmentation")
    print("=" * 50)
    print(f"Input text: {test_text}")
    print()
    
    # Initialize segmenter with gpt-oss:20b
    config = {
        'model_name': 'gpt-oss:20b',
        'max_retries': 2,
        'timeout': 30
    }
    
    segmenter = LLMTextSegmenter(config)
    
    try:
        segments = segmenter.segment(test_text)
        print("LLM Segmentation Results:")
        for i, segment in enumerate(segments, 1):
            print(f"{i}. {segment}")
        print()
        print(f"Total segments: {len(segments)}")
        
    except Exception as e:
        print(f"Error during segmentation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_llm_segmentation()