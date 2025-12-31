import pytest
import sys
import os

import ironclad_ai_guardrails as ironclad_package


class TestInitModule:
    """Test the __init__.py module functionality"""
    
    def test_package_imports(self):
        """Test that all expected functions and constants are imported"""
        # Check that all expected attributes are available
        expected_attributes = [
            'clean_json_response',
            'generate_candidate', 
            'validate_candidate',
            'save_brick',
            'main',
            'DEFAULT_MODEL_NAME',
            'DEFAULT_OUTPUT_DIR',
            'DEFAULT_SYSTEM_PROMPT',
            '__version__',
            '__all__'
        ]
        
        for attr in expected_attributes:
            assert hasattr(ironclad_package, attr), f"Missing attribute: {attr}"
    
    def test_version_defined(self):
        """Test that version is defined"""
        assert ironclad_package.__version__ == "1.0.0"
    
    def test_all_contains_expected_items(self):
        """Test that __all__ contains expected items"""
        expected_all = [
            "clean_json_response",
            "generate_candidate", 
            "validate_candidate",
            "save_brick",
            "repair_candidate",
            "main",
            "DEFAULT_MODEL_NAME",
            "DEFAULT_OUTPUT_DIR",
            "DEFAULT_SYSTEM_PROMPT",
            "MAX_RETRIES"
        ]
        
        assert set(ironclad_package.__all__) == set(expected_all)
    
    def test_default_values(self):
        """Test that default values are reasonable"""
        assert ironclad_package.DEFAULT_MODEL_NAME == "gpt-oss:20b"
        assert ironclad_package.DEFAULT_OUTPUT_DIR == "verified_bricks"
        assert "strict code generator" in ironclad_package.DEFAULT_SYSTEM_PROMPT.lower()
    
    def test_functions_are_callable(self):
        """Test that imported functions are callable"""
        functions = [
            'clean_json_response',
            'generate_candidate', 
            'validate_candidate',
            'save_brick',
            'main'
        ]
        
        for func_name in functions:
            func = getattr(ironclad_package, func_name)
            assert callable(func), f"{func_name} should be callable"