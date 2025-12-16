import pytest
import sys
import os
import tempfile
from unittest.mock import patch, MagicMock
from unittest.mock import mock_open

# Add src to path for importing
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
from cli import create_parser, load_prompt_file, main
import ironclad


class TestCreateParser:
    """Test the CLI argument parser creation"""
    
    def test_create_parser_exists(self):
        """Test that parser can be created"""
        parser = create_parser()
        assert parser is not None
    
    def test_parser_with_request_only(self):
        """Test parsing with just the required request argument"""
        parser = create_parser()
        args = parser.parse_args(['test request'])
        assert args.request == 'test request'
        assert args.model is None
        assert args.output is None
        assert args.prompt_file is None
    
    def test_parser_with_all_arguments(self):
        """Test parsing with all arguments"""
        parser = create_parser()
        args = parser.parse_args([
            'test request',
            '--model', 'llama3',
            '--output', 'custom_output',
            '--prompt-file', 'custom.txt'
        ])
        assert args.request == 'test request'
        assert args.model == 'llama3'
        assert args.output == 'custom_output'
        assert args.prompt_file == 'custom.txt'


class TestLoadPromptFile:
    """Test the prompt file loading functionality"""
    
    def test_load_prompt_file_success(self):
        """Test successful loading of prompt file"""
        prompt_content = "Custom system prompt content"
        with patch("builtins.open", mock_open(read_data=prompt_content)):
            result = load_prompt_file("test_prompt.txt")
            assert result == prompt_content
    
    def test_load_prompt_file_not_found(self):
        """Test handling of missing prompt file"""
        with patch("builtins.open", side_effect=FileNotFoundError):
            with patch("sys.exit") as mock_exit:
                load_prompt_file("nonexistent.txt")
                mock_exit.assert_called_once_with(1)
    
    def test_load_prompt_file_permission_error(self):
        """Test handling of permission errors"""
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            with patch("sys.exit") as mock_exit:
                load_prompt_file("restricted.txt")
                mock_exit.assert_called_once_with(1)


class TestCliMain:
    """Test the main CLI functionality"""
    
    @patch('cli.ironclad_main')
    def test_main_with_basic_request(self, mock_ironclad_main):
        """Test main function with basic request"""
        mock_ironclad_main.return_value = None
        
        with patch('sys.argv', ['cli', 'test request']):
            main()
            mock_ironclad_main.assert_called_once_with(
                request='test request',
                model_name=None,
                output_dir=None,
                system_prompt=ironclad.DEFAULT_SYSTEM_PROMPT
            )
    
    @patch('cli.ironclad_main')
    def test_main_with_all_options(self, mock_ironclad_main):
        """Test main function with all CLI options"""
        mock_ironclad_main.return_value = None
        
        with patch('sys.argv', [
            'cli', 
            'test request',
            '--model', 'llama3',
            '--output', 'custom_dir',
            '--prompt-file', 'custom.txt'
        ]):
            with patch('cli.load_prompt_file', return_value='Custom prompt'):
                with patch('builtins.print'):
                    main()
                    mock_ironclad_main.assert_called_once_with(
                        request='test request',
                        model_name='llama3',
                        output_dir='custom_dir',
                        system_prompt='Custom prompt'
                    )
    
    @patch('cli.ironclad_main')
    def test_main_with_keyboard_interrupt(self, mock_ironclad_main):
        """Test handling of keyboard interrupt"""
        mock_ironclad_main.side_effect = KeyboardInterrupt()
        
        with patch('sys.argv', ['cli', 'test request']):
            with patch('sys.exit') as mock_exit:
                with patch('builtins.print'):
                    main()
                    mock_exit.assert_called_once_with(1)
    
    @patch('cli.ironclad_main')
    def test_main_with_unexpected_error(self, mock_ironclad_main):
        """Test handling of unexpected errors"""
        mock_ironclad_main.side_effect = Exception("Unexpected error")
        
        with patch('sys.argv', ['cli', 'test request']):
            with patch('sys.exit') as mock_exit:
                with patch('builtins.print'):
                    main()
                    mock_exit.assert_called_once_with(1)


class TestCliIntegration:
    """Integration tests for CLI functionality"""
    
    @patch('cli.ironclad_main')
    def test_cli_with_custom_prompt_file(self, mock_ironclad_main):
        """Test CLI with custom prompt file loading"""
        mock_ironclad_main.return_value = None
        custom_prompt = "You are a Python expert. Generate clean code."
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(custom_prompt)
            prompt_file = f.name
        
        try:
            with patch('sys.argv', [
                'cli', 
                'test request',
                '--prompt-file', prompt_file
            ]):
                with patch('builtins.print'):
                    main()
                    mock_ironclad_main.assert_called_once_with(
                        request='test request',
                        model_name=None,
                        output_dir=None,
                        system_prompt=custom_prompt
                    )
        finally:
            os.unlink(prompt_file)
    
    @patch('cli.ironclad_main')
    def test_cli_main_as_script(self, mock_ironclad_main):
        """Test CLI main when called as script"""
        mock_ironclad_main.return_value = None
        
        with patch('sys.argv', ['cli.py', 'test request']):
            with patch('builtins.print'):
                main()
                mock_ironclad_main.assert_called_once_with(
                    request='test request',
                    model_name=None,
                    output_dir=None,
                    system_prompt=ironclad.DEFAULT_SYSTEM_PROMPT
                )
    
    @patch('cli.ironclad_main')
    def test_cli_main_block_execution(self, mock_ironclad_main):
        """Test that __main__ block calls main()"""
        mock_ironclad_main.return_value = None
        
        # Test the __main__ block by importing and checking the source
        import cli
        import inspect
        source = inspect.getsource(cli)
        assert "if __name__ == '__main__':" in source
        assert "main()" in source