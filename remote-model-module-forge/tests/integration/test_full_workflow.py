"""
Integration tests for Brick Commissioner with real API calls.

These tests require Z_AI_API_KEY to be set in environment variables.
"""

import os
import json
import pytest
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
import time


def requires_api_key():
    """Skip test if API key is not set."""
    api_key = os.environ.get('Z_AI_API_KEY')
    if not api_key or api_key == 'your_api_key_here' or api_key == 'test123':
        pytest.skip("Z_AI_API_KEY not set or is placeholder - skipping integration test")


class TestSimpleBrick:
    """Test commissioning a single simple brick."""
    
    def test_add_numbers_brick(self):
        """Test commissioning an add_numbers function brick."""
        requires_api_key()
        
        spec = {
            "module_name": "simple_math",
            "module_description": "Simple math operations",
            "required_public_functions": [
                {
                    "name": "add_numbers",
                    "description": "Adds two numbers together",
                    "inputs": ["a: float", "b: float"],
                    "outputs": "float",
                    "side_effects": "None"
                }
            ]
        }
        
        with TemporaryDirectory() as tmpdir:
            spec_path = Path(tmpdir) / "spec.json"
            with open(spec_path, 'w') as f:
                json.dump(spec, f)
            
            # Run brick commission
            result = subprocess.run(
                ['brick', 'run', str(spec_path)],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Should complete successfully
            assert result.returncode == 0, f"Brick run failed: {result.stderr}"
            
            # Check that function file was created
            func_files = list(Path('.').glob('**/simple_math.py'))
            assert len(func_files) > 0, "Function file not created"
            
            # Check that tests were created
            test_files = list(Path('.').glob('**/test_simple_math.py'))
            assert len(test_files) > 0, "Test file not created"
            
            # Run tests
            test_result = subprocess.run(
                ['pytest', str(test_files[0]), '-v'],
                capture_output=True,
                text=True
            )
            assert test_result.returncode == 0, f"Tests failed: {test_result.stderr}"
            
            # Clean up created files
            for f in func_files + test_files:
                if f.exists():
                    f.unlink()
    
    def test_string_length_brick(self):
        """Test commissioning a string_length function brick."""
        requires_api_key()
        
        spec = {
            "module_name": "string_utils",
            "module_description": "String utility functions",
            "required_public_functions": [
                {
                    "name": "string_length",
                    "description": "Returns the length of a string",
                    "inputs": ["s: str"],
                    "outputs": "int",
                    "side_effects": "None"
                }
            ]
        }
        
        with TemporaryDirectory() as tmpdir:
            spec_path = Path(tmpdir) / "spec.json"
            with open(spec_path, 'w') as f:
                json.dump(spec, f)
            
            result = subprocess.run(
                ['brick', 'run', str(spec_path)],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            assert result.returncode == 0, f"Brick run failed: {result.stderr}"
            assert "Brick function name: string_length" in result.stdout
            
            # Clean up
            for pattern in ['string_utils.py', 'test_string_utils.py']:
                for f in Path('.').glob(f'**/{pattern}'):
                    if f.exists():
                        f.unlink()


class TestFullWorkflow:
    """Test the complete workflow from spec to UI."""
    
    def test_calculator_module_workflow(self):
        """Test full workflow for a simple calculator module."""
        requires_api_key()
        
        spec = {
            "module_name": "calculator",
            "module_description": "A simple calculator module",
            "required_public_functions": [
                {
                    "name": "add",
                    "description": "Adds two numbers",
                    "inputs": ["a: float", "b: float"],
                    "outputs": "float",
                    "side_effects": "None"
                }
            ]
        }
        
        with TemporaryDirectory() as tmpdir:
            spec_path = Path(tmpdir) / "spec.json"
            with open(spec_path, 'w') as f:
                json.dump(spec, f)
            
            result = subprocess.run(
                ['brick', 'run', str(spec_path)],
                capture_output=True,
                text=True,
                timeout=300,
                env={**os.environ, 'RUNS_DIR': str(tmpdir)}
            )
            
            assert result.returncode == 0, f"Brick run failed: {result.stderr}"
            
            # Check run report was generated
            report_files = list(Path(tmpdir).glob('*_report.txt'))
            assert len(report_files) > 0, "Report file not generated"
            
            # Check UI was generated
            ui_files = list(Path(tmpdir).glob('*_ui.html'))
            assert len(ui_files) > 0, "UI file not generated"
            
            # Check runner script was generated
            runner_files = list(Path(tmpdir).glob('*_runner.py'))
            assert len(runner_files) > 0, "Runner script not generated"
            
            # Verify report content
            report_content = report_files[0].read_text()
            assert 'Brick function name: add' in report_content
            assert 'Test command:' in report_content
            assert 'Coverage command:' in report_content
            assert 'UI RUN COMMAND:' in report_content


class TestErrorHandling:
    """Test error handling in various scenarios."""
    
    def test_invalid_spec_stops(self):
        """Test that invalid spec causes controlled halt."""
        requires_api_key()
        
        spec = {
            "module_name": "bad_spec",
            "module_description": "A badly specified module"
            # Missing required_public_functions - should cause halt
        }
        
        with TemporaryDirectory() as tmpdir:
            spec_path = Path(tmpdir) / "spec.json"
            with open(spec_path, 'w') as f:
                json.dump(spec, f)
            
            result = subprocess.run(
                ['brick', 'run', str(spec_path)],
                capture_output=True,
                text=True,
                timeout=300,
                env={**os.environ, 'RUNS_DIR': str(tmpdir)}
            )
            
            # Should halt gracefully, not crash
            assert 'BRICK COMMISSION HALTED' in result.stdout or 'Brick halted' in result.stderr
            
    
    def test_empty_spec_stops(self):
        """Test that empty function list causes controlled halt."""
        requires_api_key()
        
        spec = {
            "module_name": "empty_spec",
            "module_description": "Module with no functions",
            "required_public_functions": []
        }
        
        with TemporaryDirectory() as tmpdir:
            spec_path = Path(tmpdir) / "spec.json"
            with open(spec_path, 'w') as f:
                json.dump(spec, f)
            
            result = subprocess.run(
                ['brick', 'run', str(spec_path)],
                capture_output=True,
                text=True,
                timeout=300,
                env={**os.environ, 'RUNS_DIR': str(tmpdir)}
            )
            
            assert 'No functions enumerated' in result.stderr or 'BRICK COMMISSION HALTED' in result.stdout


class TestLimitsEnforcement:
    """Test that limits are enforced."""
    
    def test_stop_file_halts_immediately(self):
        """Test that STOP file causes immediate halt."""
        requires_api_key()
        
        spec = {
            "module_name": "stop_test",
            "module_description": "Test STOP file behavior",
            "required_public_functions": [
                {
                    "name": "dummy",
                    "description": "Dummy function",
                    "inputs": [],
                    "outputs": "None",
                    "side_effects": "None"
                }
            ]
        }
        
        with TemporaryDirectory() as tmpdir:
            spec_path = Path(tmpdir) / "spec.json"
            with open(spec_path, 'w') as f:
                json.dump(spec, f)
            
            # Create STOP file
            stop_file = Path(tmpdir) / "STOP"
            stop_file.write_text("")
            
            result = subprocess.run(
                ['brick', 'run', str(spec_path)],
                capture_output=True,
                text=True,
                timeout=300,
                env={**os.environ, 'RUNS_DIR': str(tmpdir)}
            )
            
            assert 'STOP file detected' in result.stderr or 'STOP file detected' in result.stdout
            
            # Clean up
            if stop_file.exists():
                stop_file.unlink()


class TestMultipleFunctions:
    """Test behavior with multiple functions in spec."""
    
    def test_selects_first_function_only(self):
        """Test that only one function is implemented per run."""
        requires_api_key()
        
        spec = {
            "module_name": "multi_func",
            "module_description": "Module with multiple functions",
            "required_public_functions": [
                {
                    "name": "func_a",
                    "description": "First function",
                    "inputs": ["x: int"],
                    "outputs": "int",
                    "side_effects": "None"
                },
                {
                    "name": "func_b",
                    "description": "Second function",
                    "inputs": ["x: int"],
                    "outputs": "int",
                    "side_effects": "None"
                }
            ]
        }
        
        with TemporaryDirectory() as tmpdir:
            spec_path = Path(tmpdir) / "spec.json"
            with open(spec_path, 'w') as f:
                json.dump(spec, f)
            
            result = subprocess.run(
                ['brick', 'run', str(spec_path)],
                capture_output=True,
                text=True,
                timeout=300,
                env={**os.environ, 'RUNS_DIR': str(tmpdir)}
            )
            
            assert result.returncode == 0, f"Brick run failed: {result.stderr}"
            
            # Check that only one function was implemented
            func_files = list(Path('.').glob('**/multi_func.py'))
            if func_files:
                content = func_files[0].read_text()
                # Should only implement ONE function
                func_count = content.count('def ')
                assert func_count == 1, f"Expected 1 function, found {func_count}"
                
                if func_files[0].exists():
                    func_files[0].unlink()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
