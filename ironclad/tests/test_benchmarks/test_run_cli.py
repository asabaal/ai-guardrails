"""Test for benchmarks/run.py CLI entry point."""
import sys
import unittest
from unittest.mock import patch, MagicMock, Mock
from pathlib import Path
import tempfile
import json
import yaml
import time

sys.path.insert(0, '/mnt/storage/repos/ai-guardrails/ironclad')

import benchmarks.run


class TestCleanVerifiedBricks(unittest.TestCase):
    """Test clean_verified_bricks function."""

    @patch('benchmarks.run.Path')
    def test_clean_verified_bricks_no_directory(self, mock_path):
        """Test when verified_bricks directory does not exist."""
        mock_path.return_value.exists.return_value = False
        benchmarks.run.clean_verified_bricks()
        mock_path.return_value.exists.assert_called_once()

    @patch('benchmarks.run.Path')
    def test_clean_verified_bricks_with_files(self, mock_path):
        """Test when verified_bricks directory has files to clean."""
        mock_file1 = MagicMock()
        mock_file2 = MagicMock()
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.glob.return_value = [mock_file1, mock_file2]
        
        benchmarks.run.clean_verified_bricks()
        
        mock_file1.unlink.assert_called_once()
        mock_file2.unlink.assert_called_once()

    @patch('benchmarks.run.Path')
    def test_clean_verified_bricks_with_delete_error(self, mock_path):
        """Test when file deletion raises exception."""
        mock_file = MagicMock()
        mock_file.unlink.side_effect = Exception("Permission denied")
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.glob.return_value = [mock_file]
        
        with patch('builtins.print') as mock_print:
            benchmarks.run.clean_verified_bricks()
            self.assertTrue(any("Warning" in str(call) for call in mock_print.call_args_list))

    @patch('benchmarks.run.Path')
    def test_clean_verified_bricks_empty_directory(self, mock_path):
        """Test when verified_bricks directory is empty."""
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.glob.return_value = []
        
        benchmarks.run.clean_verified_bricks()
        
        mock_path.return_value.glob.assert_called_once_with("*.py")


class TestComputeWilsonCI(unittest.TestCase):
    """Test compute_wilson_ci function."""

    def test_compute_wilson_ci_success(self):
        """Test Wilson CI computation with typical success rate."""
        ci = benchmarks.run.compute_wilson_ci(8, 10)
        self.assertEqual(len(ci), 2)
        self.assertGreater(ci[1], ci[0])
        self.assertGreater(ci[0], 0)
        self.assertLess(ci[1], 1)

    def test_compute_wilson_ci_all_success(self):
        """Test Wilson CI with 100% success."""
        ci = benchmarks.run.compute_wilson_ci(10, 10)
        self.assertEqual(len(ci), 2)
        self.assertEqual(ci[1], 1.0)

    def test_compute_wilson_ci_no_success(self):
        """Test Wilson CI with 0% success."""
        ci = benchmarks.run.compute_wilson_ci(0, 10)
        self.assertEqual(len(ci), 2)
        self.assertEqual(ci[0], 0.0)

    def test_compute_wilson_ci_zero_total(self):
        """Test Wilson CI with zero total runs."""
        with self.assertRaises(ZeroDivisionError):
            benchmarks.run.compute_wilson_ci(0, 0)


class TestLoadSuite(unittest.TestCase):
    """Test load_suite function."""

    def test_load_suite_success(self):
        """Test loading a valid YAML suite."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({
                'suite_id': 'test_suite',
                'mode': 'canonical',
                'runs_per_case': 5,
                'small': [
                    {'id': 'case1', 'complexity': 'small', 'instruction': 'test instruction'}
                ]
            }, f)
            f.flush()
            
            suite = benchmarks.run.load_suite(f.name)
            
            self.assertEqual(suite['suite_id'], 'test_suite')
            self.assertEqual(suite['mode'], 'canonical')
            self.assertEqual(len(suite['small']), 1)
            
            Path(f.name).unlink()

    def test_load_suite_invalid_yaml(self):
        """Test loading invalid YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content:\n  - broken")
            f.flush()
            
            with self.assertRaises(yaml.YAMLError):
                benchmarks.run.load_suite(f.name)
            
            Path(f.name).unlink()


class TestRunIronclad(unittest.TestCase):
    """Test run_ironclad function."""

    @patch('benchmarks.run.subprocess.run')
    @patch('benchmarks.run.clean_verified_bricks')
    @patch('benchmarks.run.datetime')
    @patch('benchmarks.run.time')
    def test_run_ironclad_success(self, mock_time, mock_datetime, mock_clean, mock_subprocess):
        """Test successful Ironclad run."""
        benchmarks.run.run_counter = 0
        mock_time.time.return_value = 1000.0
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T00:00:00Z"
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout="Success output",
            stderr=""
        )
        
        result = benchmarks.run.run_ironclad("test instruction")
        
        self.assertTrue(result['success'])
        self.assertEqual(result['run_id'], 'run_001')
        self.assertEqual(result['failure_stage'], 'unknown')
        self.assertEqual(result['attempts'], 1)
        mock_subprocess.assert_called_once()

    @patch('benchmarks.run.subprocess.run')
    @patch('benchmarks.run.clean_verified_bricks')
    @patch('benchmarks.run.datetime')
    @patch('benchmarks.run.time')
    def test_run_ironclad_generation_failure(self, mock_time, mock_datetime, mock_clean, mock_subprocess):
        """Test Ironclad run with generation failure."""
        benchmarks.run.run_counter = 0
        mock_time.time.return_value = 1000.0
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T00:00:00Z"
        mock_subprocess.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="FAIL: Generation failed"
        )
        
        result = benchmarks.run.run_ironclad("test instruction")
        
        self.assertFalse(result['success'])
        self.assertEqual(result['failure_stage'], 'generation')

    @patch('benchmarks.run.subprocess.run')
    @patch('benchmarks.run.clean_verified_bricks')
    @patch('benchmarks.run.datetime')
    @patch('benchmarks.run.time')
    def test_run_ironclad_repair_failure(self, mock_time, mock_datetime, mock_clean, mock_subprocess):
        """Test Ironclad run with repair failure."""
        benchmarks.run.run_counter = 0
        mock_time.time.return_value = 1000.0
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T00:00:00Z"
        mock_subprocess.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="repair failed"
        )
        
        result = benchmarks.run.run_ironclad("test instruction")
        
        self.assertFalse(result['success'])
        self.assertEqual(result['failure_stage'], 'repair')

    @patch('benchmarks.run.subprocess.run')
    @patch('benchmarks.run.clean_verified_bricks')
    @patch('benchmarks.run.datetime')
    @patch('benchmarks.run.time')
    def test_run_ironclad_validation_failure(self, mock_time, mock_datetime, mock_clean, mock_subprocess):
        """Test Ironclad run with validation failure."""
        benchmarks.run.run_counter = 0
        mock_time.time.return_value = 1000.0
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T00:00:00Z"
        mock_subprocess.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="validation error"
        )
        
        result = benchmarks.run.run_ironclad("test instruction")
        
        self.assertFalse(result['success'])
        self.assertEqual(result['failure_stage'], 'validation')

    @patch('benchmarks.run.subprocess.run')
    @patch('benchmarks.run.clean_verified_bricks')
    @patch('benchmarks.run.datetime')
    @patch('benchmarks.run.time')
    def test_run_ironclad_with_debug(self, mock_time, mock_datetime, mock_clean, mock_subprocess):
        """Test Ironclad run with debug mode enabled."""
        benchmarks.run.run_counter = 0
        mock_time.time.return_value = 1000.0
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T00:00:00Z"
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout="",
            stderr=""
        )
        
        result = benchmarks.run.run_ironclad("test instruction", debug=True)
        
        self.assertTrue(result['debug_enabled'])
        self.assertTrue(result['success'])
        env_arg = mock_subprocess.call_args[1]['env']
        self.assertIsNotNone(env_arg)
        self.assertEqual(env_arg['IRONCLAD_DEBUG'], '1')


class TestRunCanonicalSuite(unittest.TestCase):
    """Test run_canonical_suite function."""

    @patch('benchmarks.run.run_ironclad')
    @patch('benchmarks.run.Path')
    def test_run_canonical_suite_small_filter(self, mock_path, mock_run):
        """Test running canonical suite with small filter."""
        suite = {
            'suite_id': 'test_suite',
            'mode': 'canonical',
            'runs_per_case': 2,
            'small': [
                {'id': 'case1', 'complexity': 'small', 'instruction': 'test 1'},
                {'id': 'case2', 'complexity': 'small', 'instruction': 'test 2'}
            ],
            'mid': [{'id': 'case3', 'complexity': 'mid', 'instruction': 'test 3'}],
            'large': [{'id': 'case4', 'complexity': 'large', 'instruction': 'test 4'}]
        }
        
        mock_case_dir = MagicMock()
        mock_case_dir.mkdir = MagicMock()
        mock_run_dir = MagicMock()
        mock_run_dir.mkdir = MagicMock()
        mock_case_dir.__truediv__ = MagicMock(return_value=mock_run_dir)
        mock_output_dir = MagicMock()
        mock_output_dir.__truediv__ = MagicMock(return_value=mock_case_dir)
        
        mock_run.return_value = {
            'run_id': 'run_001',
            'success': True,
            'duration_ms': 100
        }
        
        args = Mock()
        args.filter = 'small'
        args.timeout = None
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__ = MagicMock()
            mock_open.return_value.__exit__ = MagicMock()
            mock_open.return_value.write = MagicMock()
            
            benchmarks.run.run_canonical_suite(suite, mock_output_dir, args)
            
            self.assertEqual(mock_run.call_count, 4)

    @patch('benchmarks.run.run_ironclad')
    @patch('benchmarks.run.Path')
    def test_run_canonical_suite_all_filter(self, mock_path, mock_run):
        """Test running canonical suite with all filter."""
        suite = {
            'suite_id': 'test_suite',
            'mode': 'canonical',
            'runs_per_case': 1,
            'small': [{'id': 'case1', 'complexity': 'small', 'instruction': 'test 1'}],
            'mid': [{'id': 'case2', 'complexity': 'mid', 'instruction': 'test 2'}],
            'large': [{'id': 'case3', 'complexity': 'large', 'instruction': 'test 3'}]
        }
        
        mock_case_dir = MagicMock()
        mock_case_dir.mkdir = MagicMock()
        mock_run_dir = MagicMock()
        mock_run_dir.mkdir = MagicMock()
        mock_case_dir.__truediv__ = MagicMock(return_value=mock_run_dir)
        mock_output_dir = MagicMock()
        mock_output_dir.__truediv__ = MagicMock(return_value=mock_case_dir)
        
        mock_run.return_value = {
            'run_id': 'run_001',
            'success': True,
            'duration_ms': 100
        }
        
        args = Mock()
        args.filter = 'all'
        args.timeout = None
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__ = MagicMock()
            mock_open.return_value.__exit__ = MagicMock()
            mock_open.return_value.write = MagicMock()
            
            benchmarks.run.run_canonical_suite(suite, mock_output_dir, args)
            
            self.assertEqual(mock_run.call_count, 3)

    @patch('benchmarks.run.run_ironclad')
    @patch('benchmarks.run.Path')
    def test_run_canonical_suite_custom_timeout(self, mock_path, mock_run):
        """Test running canonical suite with custom timeout."""
        suite = {
            'suite_id': 'test_suite',
            'mode': 'canonical',
            'runs_per_case': 1,
            'small': [{'id': 'case1', 'complexity': 'small', 'instruction': 'test 1'}]
        }
        
        mock_case_dir = MagicMock()
        mock_case_dir.mkdir = MagicMock()
        mock_run_dir = MagicMock()
        mock_run_dir.mkdir = MagicMock()
        mock_case_dir.__truediv__ = MagicMock(return_value=mock_run_dir)
        mock_output_dir = MagicMock()
        mock_output_dir.__truediv__ = MagicMock(return_value=mock_case_dir)
        
        mock_run.return_value = {
            'run_id': 'run_001',
            'success': True,
            'duration_ms': 100
        }
        
        args = Mock()
        args.filter = 'small'
        args.timeout = 120
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__ = MagicMock()
            mock_open.return_value.__exit__ = MagicMock()
            mock_open.return_value.write = MagicMock()
            
            benchmarks.run.run_canonical_suite(suite, mock_output_dir, args)
            
            self.assertEqual(mock_run.call_args[0][1], 120)


class TestMain(unittest.TestCase):
    """Test main function."""

    @patch('sys.argv', ['run.py', '--dry-run'])
    @patch('benchmarks.run.Path')
    @patch('benchmarks.run.datetime')
    def test_main_dry_run(self, mock_datetime, mock_path):
        """Test main with --dry-run flag."""
        mock_datetime.now.return_value.strftime.return_value = "20240101_120000"
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T12:00:00Z"
        mock_output_path = MagicMock()
        mock_run_dir = MagicMock()
        mock_run_dir.mkdir = MagicMock()
        mock_output_path.__truediv__ = MagicMock(return_value=mock_run_dir)
        mock_path.return_value = mock_output_path
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__ = MagicMock()
            mock_open.return_value.__exit__ = MagicMock()
            mock_open.return_value.write = MagicMock()
            
            benchmarks.run.main()

    @patch('sys.argv', ['run.py', '--dry-run', '--suite', 'test_suite.yaml'])
    @patch('benchmarks.run.Path')
    @patch('benchmarks.run.load_suite')
    @patch('benchmarks.run.datetime')
    def test_main_dry_run_with_suite(self, mock_datetime, mock_load, mock_path):
        """Test main with --dry-run and --suite."""
        mock_datetime.now.return_value.strftime.return_value = "20240101_120000"
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T12:00:00Z"
        mock_path.return_value.exists.return_value = True
        mock_output_path = MagicMock()
        mock_run_dir = MagicMock()
        mock_run_dir.mkdir = MagicMock()
        mock_output_path.__truediv__ = MagicMock(return_value=mock_run_dir)
        mock_path.return_value = mock_output_path
        
        mock_load.return_value = {
            'suite_id': 'test_suite',
            'mode': 'canonical',
            'small': [{'id': 'case1', 'complexity': 'small', 'instruction': 'test'}]
        }
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__ = MagicMock()
            mock_open.return_value.__exit__ = MagicMock()
            mock_open.return_value.write = MagicMock()
            
            benchmarks.run.main()

    @patch('sys.argv', ['run.py', '--filter', 'small'])
    @patch('benchmarks.run.Path')
    @patch('benchmarks.run.load_suite')
    @patch('benchmarks.run.run_canonical_suite')
    @patch('benchmarks.run.datetime')
    def test_main_with_filter(self, mock_datetime, mock_run_suite, mock_load, mock_path):
        """Test main with --filter argument."""
        mock_datetime.now.return_value.strftime.return_value = "20240101_120000"
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T12:00:00Z"
        mock_path.return_value.exists.return_value = True
        mock_output_path = MagicMock()
        mock_run_dir = MagicMock()
        mock_run_dir.mkdir = MagicMock()
        mock_output_path.__truediv__ = MagicMock(return_value=mock_run_dir)
        mock_path.return_value = mock_output_path
        
        mock_load.return_value = {
            'suite_id': 'canonical',
            'mode': 'canonical',
            'small': [{'id': 'case1', 'complexity': 'small', 'instruction': 'test'}]
        }
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__ = MagicMock()
            mock_open.return_value.__exit__ = MagicMock()
            mock_open.return_value.write = MagicMock()
            
            benchmarks.run.main()

    @patch('sys.argv', ['run.py', '--timeout', '120'])
    @patch('benchmarks.run.Path')
    @patch('benchmarks.run.load_suite')
    @patch('benchmarks.run.run_canonical_suite')
    @patch('benchmarks.run.datetime')
    def test_main_with_timeout(self, mock_datetime, mock_run_suite, mock_load, mock_path):
        """Test main with --timeout argument."""
        mock_datetime.now.return_value.strftime.return_value = "20240101_120000"
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T12:00:00Z"
        mock_path.return_value.exists.return_value = True
        mock_output_path = MagicMock()
        mock_run_dir = MagicMock()
        mock_run_dir.mkdir = MagicMock()
        mock_output_path.__truediv__ = MagicMock(return_value=mock_run_dir)
        mock_path.return_value = mock_output_path
        
        mock_load.return_value = {
            'suite_id': 'canonical',
            'mode': 'canonical',
            'small': [{'id': 'case1', 'complexity': 'small', 'instruction': 'test'}]
        }
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__ = MagicMock()
            mock_open.return_value.__exit__ = MagicMock()
            mock_open.return_value.write = MagicMock()
            
            benchmarks.run.main()

    @patch('sys.argv', ['run.py', '--output-dir', 'custom_output'])
    @patch('benchmarks.run.Path')
    @patch('benchmarks.run.load_suite')
    @patch('benchmarks.run.run_canonical_suite')
    @patch('benchmarks.run.datetime')
    def test_main_custom_output_dir(self, mock_datetime, mock_run_suite, mock_load, mock_path):
        """Test main with custom output directory."""
        mock_datetime.now.return_value.strftime.return_value = "20240101_120000"
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T12:00:00Z"
        mock_path.return_value.exists.return_value = True
        mock_output_path = MagicMock()
        mock_run_dir = MagicMock()
        mock_run_dir.mkdir = MagicMock()
        mock_output_path.__truediv__ = MagicMock(return_value=mock_run_dir)
        mock_path.return_value = mock_output_path
        
        mock_load.return_value = {
            'suite_id': 'canonical',
            'mode': 'canonical',
            'small': [{'id': 'case1', 'complexity': 'small', 'instruction': 'test'}]
        }
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__ = MagicMock()
            mock_open.return_value.__exit__ = MagicMock()
            mock_open.return_value.write = MagicMock()
            
            benchmarks.run.main()

    @patch('sys.argv', ['run.py', '--model', 'custom_model'])
    @patch('benchmarks.run.Path')
    @patch('benchmarks.run.load_suite')
    @patch('benchmarks.run.run_canonical_suite')
    @patch('benchmarks.run.datetime')
    def test_main_custom_model(self, mock_datetime, mock_run_suite, mock_load, mock_path):
        """Test main with custom model."""
        mock_datetime.now.return_value.strftime.return_value = "20240101_120000"
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T12:00:00Z"
        mock_path.return_value.exists.return_value = True
        mock_output_path = MagicMock()
        mock_run_dir = MagicMock()
        mock_run_dir.mkdir = MagicMock()
        mock_output_path.__truediv__ = MagicMock(return_value=mock_run_dir)
        mock_path.return_value = mock_output_path
        
        mock_load.return_value = {
            'suite_id': 'canonical',
            'mode': 'canonical',
            'small': [{'id': 'case1', 'complexity': 'small', 'instruction': 'test'}]
        }
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__ = MagicMock()
            mock_open.return_value.__exit__ = MagicMock()
            mock_open.return_value.write = MagicMock()
            
            benchmarks.run.main()


if __name__ == "__main__":
    unittest.main()
