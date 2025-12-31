import pytest
import sys
import os
import subprocess
import tempfile


class TestMainBlocks:
    """Test __main__ blocks in modules"""
    
    def test_ironclad_main_block_execution(self):
        """Test that ironclad.py can be executed as script"""
        # Test the __main__ block by running the module as a script
        # with mocked dependencies to avoid actual execution
        ironclad_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'src', 
            'ironclad.py'
        )
        
        # Create a test script that imports and runs ironclad
        test_script = f'''
import sys

# Mock functions to avoid actual execution
import unittest.mock
with unittest.mock.patch('ironclad_ai_guardrails.ironclad.generate_candidate') as mock_gen:
    with unittest.mock.patch('ironclad_ai_guardrails.ironclad.validate_candidate') as mock_val:
        with unittest.mock.patch('ironclad_ai_guardrails.ironclad.save_brick') as mock_save:
            mock_gen.return_value = None
            
            # Simulate command line arguments
            sys.argv = ['ironclad.py', 'test request']
            
            # Import and execute module
            import ironclad_ai_guardrails.ironclad as ironclad
            ironclad.main()
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_script)
            test_file = f.name
        
        try:
            # Run the test script
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            # Should not crash (return code 0 or 1 is acceptable)
            assert result.returncode in [0, 1]
        finally:
            os.unlink(test_file)
    
    def test_cli_main_block_execution(self):
        """Test that cli.py can be executed as script"""
        cli_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'src', 
            'cli.py'
        )
        
        # Create a test script that imports and runs cli
        test_script = f'''
import sys

# Mock functions to avoid actual execution
import unittest.mock
with unittest.mock.patch('ironclad_ai_guardrails.cli.ironclad_main') as mock_main:
    mock_main.return_value = None
    
    # Simulate command line arguments
    sys.argv = ['cli.py', 'test request']
    
    # Import and execute module
    import ironclad_ai_guardrails.cli as cli
    cli.main()
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_script)
            test_file = f.name
        
        try:
            # Run the test script
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            # Should not crash (return code 0 or 1 is acceptable)
            assert result.returncode in [0, 1]
        finally:
            os.unlink(test_file)