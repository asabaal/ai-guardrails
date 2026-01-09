import pytest


class TestMainBlock:
    """Test __main__ block prevents duplicate module loading"""    
    def test__main__exists(self):
        """Test that __main__.py file exists and is valid Python"""
        import os
        main_file = os.path.join(
            os.path.dirname(__file__), 
            '..', 'src', 'ironclad_ai_guardrails', '__main__.py'
        )
        assert os.path.exists(main_file), f"__main__.py should exist at {main_file}"
        
        # Verify it's importable
        import importlib.util
        spec = importlib.util.spec_from_file_location("__main__", main_file)
        assert spec is not None, "__main__.py should be a valid module"
    
    def test__main__imports_main_function(self):
        """Test that __main__.py imports main from ironclad"""
        import os
        import sys
        
        # Add src to path temporarily
        src_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
        sys.path.insert(0, src_dir)
        
        try:
            from ironclad_ai_guardrails import __main__
            
            # Verify that __main__ can access main
            assert hasattr(__main__, 'main'), "__main__ should have main function"
        finally:
            sys.path.pop(0)
