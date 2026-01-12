"""
Simple test to verify benchmark files exist.
"""

import unittest
from pathlib import Path


class TestBenchmarkFilesExist(unittest.TestCase):
    """Test that all benchmark files exist."""

    def test_readme_exists(self):
        """Test that benchmarks/README.md exists."""
        readme_path = Path("benchmarks/README.md")
        self.assertTrue(readme_path.exists())
        self.assertTrue(readme_path.is_file())

    def test_run_cli_exists(self):
        """Test that benchmarks/run.py CLI exists."""
        run_path = Path("benchmarks/run.py")
        self.assertTrue(run_path.exists())
        self.assertTrue(run_path.is_file())


if __name__ == "__main__":
    unittest.main()
