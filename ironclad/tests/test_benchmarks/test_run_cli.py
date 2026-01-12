"""Test for benchmarks/run.py CLI entry point."""
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, '/mnt/storage/repos/ai-guardrails/ironclad')

import benchmarks.run


class TestRunCLI(unittest.TestCase):
    """Test benchmarks/run.py CLI entry point."""

    @patch('benchmarks.run.argparse.ArgumentParser')
    def test_main_with_suite_argument(self, mock_parser_class):
        """Test main() with --suite argument."""
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = MagicMock(
            suite='suites/test.yaml',
            output_dir='outputs',
            dry_run=True,
            model='openai',
            max_failures=5
        )
        mock_parser_class.return_value = mock_parser

        benchmarks.run.main()

    @patch('benchmarks.run.Path')
    @patch('benchmarks.run.argparse.ArgumentParser')
    def test_main_without_suite_all_exist(self, mock_parser_class, mock_path_class):
        """Test main() without --suite, all suite files exist."""
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = MagicMock(
            suite=None,
            output_dir='benchmarks/outputs',
            dry_run=False,
            model='ollama',
            max_failures=None
        )
        mock_parser_class.return_value = mock_parser

        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_class.side_effect = lambda x: mock_path_instance

        with patch('builtins.print') as mock_print:
            benchmarks.run.main()
            mock_print.assert_any_call("[*] No suite specified, running all suites...")

    @patch('benchmarks.run.Path')
    @patch('benchmarks.run.argparse.ArgumentParser')
    def test_main_without_suite_some_missing(self, mock_parser_class, mock_path_class):
        """Test main() without --suite, some suite files missing."""
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = MagicMock(
            suite=None,
            output_dir='benchmarks/outputs',
            dry_run=False,
            model='ollama',
            max_failures=None
        )
        mock_parser_class.return_value = mock_parser

        suite_files = ["suites/baseline.yaml", "suites/adversarial.yaml", "suites/stress.yaml"]

        mock_path_instances = []
        for i, suite in enumerate(suite_files):
            mock_instance = MagicMock()
            mock_instance.exists.return_value = i in [0, 2]
            mock_path_instances.append(mock_instance)

        mock_path_class.side_effect = mock_path_instances

        with patch('builtins.print') as mock_print:
            benchmarks.run.main()
            calls = [c[0][0] for c in mock_print.call_args_list]
            self.assertIn("[*] No suite specified, running all suites...", calls)
            self.assertTrue(any("[!] Suite file not found:" in c for c in calls))

    @patch('benchmarks.run.argparse.ArgumentParser')
    def test_main_default_arguments(self, mock_parser_class):
        """Test main() with default arguments."""
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = MagicMock(
            suite=None,
            output_dir='benchmarks/outputs',
            dry_run=False,
            model='ollama',
            max_failures=None
        )
        mock_parser_class.return_value = mock_parser

        with patch('benchmarks.run.Path'):
            with patch('builtins.print'):
                benchmarks.run.main()

    def test_argparse_setup(self):
        """Test argparse is configured correctly."""
        with patch('argparse.ArgumentParser') as mock_parser_class:
            mock_parser = MagicMock()
            mock_parser_class.return_value = mock_parser
            mock_parser.parse_args.return_value = MagicMock(
                suite=None,
                output_dir='benchmarks/outputs',
                dry_run=False,
                model='ollama',
                max_failures=None
            )

            with patch('benchmarks.run.Path'):
                with patch('builtins.print'):
                    benchmarks.run.main()

                    mock_parser.add_argument.assert_any_call(
                        "--suite",
                        help="Suite file to run (default: run all suites)",
                    )
                    mock_parser.add_argument.assert_any_call(
                        "--output-dir",
                        default="benchmarks/outputs",
                        help="Output directory for benchmark results",
                    )
                    mock_parser.add_argument.assert_any_call(
                        "--dry-run",
                        action="store_true",
                        help="Generate instruction variants but don't run Ironclad",
                    )
                    mock_parser.add_argument.assert_any_call(
                        "--model",
                        default="ollama",
                        help="AI model to use for AI-based generators",
                    )
                    mock_parser.add_argument.assert_any_call(
                        "--max-failures",
                        type=int,
                        default=None,
                        help="Stop benchmark after N AI generation failures (default: unlimited)",
                    )


if __name__ == "__main__":
    unittest.main()
