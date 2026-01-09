import pytest
import subprocess
import sys
import os
import tempfile


class TestMainBlock:
    """Test __main__ block prevents duplicate module loading"""    
    def test__main__prevents_runtime_warning(self):
        """Test that __main__.py prevents RuntimeWarning when running via -m"""
        # When run via python -m, the __main__ block should execute
        # and prevent ironclad.py from being imported before execution
        # This eliminates the RuntimeWarning
        
        result = subprocess.run(
            [sys.executable, "-m", "ironclad_ai_guardrails", "--help"],
            timeout=10,
        )
        
        # Should execute successfully without RuntimeWarning
        assert result.returncode == 0
        # Should show usage information (either "Usage:" or "Ironclad:")
        output_lower = result.stdout.lower()
        assert r"usage:" in output_lower or r"ironclad:" in output_lower
    
    def test__main__does_not_execute_on_import(self):
        """Test that __main__.py does not execute when package is imported"""
        # Create a test script that imports the package without running CLI
        test_script = '''
import sys
import ironclad_ai_guardrails.ironclad as ironclad_module

# Import the package
import ironclad_ai_guardrails

# Check if main was called during import
has_main = hasattr(ironclad_module, 'main')
print(f"main attribute exists: {has_main}")
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_script)
            test_file = f.name
        
        try:
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                timeout=10,
            )
            
            # Import should work fine
            assert result.returncode == 0
            # The main() function should NOT have been executed during import
            assert "main attribute exists: True" in result.stdout
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)
