#!/usr/bin/env python3
"""
Comprehensive tests for code_utils module newline handling functionality.
"""

import pytest
import json
import os
import sys

import ironclad_ai_guardrails.code_utils as code_utils


class TestDecodeNewlinesInText:
    """Test the decode_newlines_in_text function"""
    
    def test_simple_newline_decoding(self):
        """Test basic \\n to newline conversion"""
        input_text = "line1\\nline2\\nline3"
        expected = "line1\nline2\nline3"
        assert code_utils.decode_newlines_in_text(input_text) == expected
    
    def test_escape_quote_decoding(self):
        """Test escaped quote conversion"""
        input_text = 'He said \\"hello\\" to me'
        expected = 'He said "hello" to me'
        assert code_utils.decode_newlines_in_text(input_text) == expected
    
    def test_combined_decoding(self):
        """Test combined newlines and quotes"""
        input_text = 'print(\\"hello\\")\\nprint(\\"world\\")'
        expected = 'print("hello")\nprint("world")'
        assert code_utils.decode_newlines_in_text(input_text) == expected
    
    def test_no_decoding_needed(self):
        """Test text that doesn't need decoding"""
        input_text = "regular text\nwith real newlines"
        expected = "regular text\nwith real newlines"
        assert code_utils.decode_newlines_in_text(input_text) == expected
    
    def test_non_string_input(self):
        """Test non-string input handling"""
        assert code_utils.decode_newlines_in_text(123) == 123
        assert code_utils.decode_newlines_in_text(None) is None
        assert code_utils.decode_newlines_in_text([]) == []


class TestDecodeNewlinesRecursive:
    """Test recursive newline decoding in complex data structures"""
    
    def test_dict_decoding(self):
        """Test decoding in dictionary values"""
        input_dict = {
            "code": "def hello():\\n    print(\"world\")",
            "filename": "test.py",
            "description": "A function\\nwith newlines"
        }
        expected = {
            "code": "def hello():\n    print(\"world\")",
            "filename": "test.py",
            "description": "A function\nwith newlines"
        }
        assert code_utils.decode_newlines_recursive(input_dict) == expected
    
    def test_nested_dict_decoding(self):
        """Test decoding in nested dictionaries"""
        input_dict = {
            "function": {
                "code": "line1\\nline2",
                "test": "test_line1\\ntest_line2"
            },
            "metadata": "simple\\ntext"
        }
        expected = {
            "function": {
                "code": "line1\nline2",
                "test": "test_line1\ntest_line2"
            },
            "metadata": "simple\ntext"
        }
        assert code_utils.decode_newlines_recursive(input_dict) == expected
    
    def test_list_decoding(self):
        """Test decoding in lists"""
        input_list = ["item1\\nitem2", "item3\\nitem4"]
        expected = ["item1\nitem2", "item3\nitem4"]
        assert code_utils.decode_newlines_recursive(input_list) == expected
    
    def test_mixed_structure_decoding(self):
        """Test decoding in mixed data structures"""
        input_data = {
            "functions": [
                {"name": "func1", "code": "line1\\nline2"},
                {"name": "func2", "code": "line3\\nline4"}
            ],
            "main": "main_code\\nwith newlines"
        }
        expected = {
            "functions": [
                {"name": "func1", "code": "line1\nline2"},
                {"name": "func2", "code": "line3\nline4"}
            ],
            "main": "main_code\nwith newlines"
        }
        assert code_utils.decode_newlines_recursive(input_data) == expected


class TestCleanJsonResponse:
    """Test JSON response cleaning functionality"""
    
    def test_clean_markdown_fences(self):
        """Test removal of markdown fences"""
        input_json = '```json\\n{"code": "line1\\\\nline2"}\\n```'
        result = code_utils.clean_json_response(input_json)
        # Should be valid JSON string
        parsed = json.loads(result)
        assert parsed["code"] == "line1\nline2"
    
    def test_clean_without_fences(self):
        """Test cleaning without markdown fences"""
        input_json = '{\n  "code": "line1\\\\nline2"\n}'
        result = code_utils.clean_json_response(input_json)
        parsed = json.loads(result)
        assert parsed["code"] == "line1\nline2"
    
    def test_complex_json_cleaning(self):
        """Test complex JSON structure cleaning"""
        input_json = '''```json
        {
            "filename": "test_function",
            "code": "def test():\\n    pass\\n\\nprint(\\"done\\")",
            "test": "import pytest\\n\\ndef test_test():\\n    test()"
        }
        ```'''
        result = code_utils.clean_json_response(input_json)
        parsed = json.loads(result)
        assert parsed["filename"] == "test_function"
        assert parsed["code"] == "def test():\n    pass\n\nprint(\"done\")"
        assert "import pytest\n\ndef test_test():\n    test()" in parsed["test"]
    
    def test_malformed_json_fallback(self):
        """Test fallback handling for malformed JSON"""
        input_json = 'invalid json with \\n escapes'
        result = code_utils.clean_json_response(input_json)
        assert result == 'invalid json with \n escapes'


class TestCleanCodeContent:
    """Test code content cleaning functionality"""
    
    def test_basic_code_cleaning(self):
        """Test basic code cleaning"""
        input_code = 'def hello():\\n    print(\\"world\\")\\n'
        expected = 'def hello():\n    print("world")\n'
        assert code_utils.clean_code_content(input_code) == expected
    
    def test_markdown_removal(self):
        """Test removal of markdown fences from code"""
        input_code = '```python\\ndef hello():\\n    pass\\n```'
        expected = 'def hello():\n    pass\n'
        assert code_utils.clean_code_content(input_code) == expected
    
    def test_code_with_excessive_blank_lines(self):
        """Test removal of excessive blank lines at start"""
        input_code = '\\n\\n\\ndef hello():\\n    pass'
        expected = 'def hello():\n    pass\n'
        assert code_utils.clean_code_content(input_code) == expected
    
    def test_code_already_clean(self):
        """Test that already clean code is preserved"""
        input_code = 'def hello():\n    pass\n'
        expected = 'def hello():\n    pass\n'
        assert code_utils.clean_code_content(input_code) == expected
    
    def test_non_string_input(self):
        """Test non-string input handling"""
        assert code_utils.clean_code_content(123) == "123"


class TestValidatePythonSyntax:
    """Test Python syntax validation"""
    
    def test_valid_syntax(self):
        """Test validation of valid Python code"""
        valid_code = "def hello():\n    return 'world'"
        is_valid, error = code_utils.validate_python_syntax(valid_code)
        assert is_valid is True
        assert error == ""
    
    def test_invalid_syntax(self):
        """Test validation of invalid Python code"""
        invalid_code = "def hello()\n    return 'world'  # missing colon"
        is_valid, error = code_utils.validate_python_syntax(invalid_code)
        assert is_valid is False
        assert "Syntax error" in error
    
    def test_empty_code(self):
        """Test validation of empty code"""
        is_valid, error = code_utils.validate_python_syntax("")
        assert is_valid is True
        assert error == ""
    
    def test_import_syntax(self):
        """Test validation of import statements"""
        import_code = "import os\nimport sys\nfrom pathlib import Path"
        is_valid, error = code_utils.validate_python_syntax(import_code)
        assert is_valid is True
        assert error == ""


class TestFixCommonCodeIssues:
    """Test fixing of common code issues"""
    
    def test_newline_normalization(self):
        """Test normalization of different newline types"""
        input_code = "line1\\r\\nline2\\rline3\\nline4"
        result = code_utils.fix_common_code_issues(input_code)
        expected = "line1\nline2\nline3\nline4\n"
        assert result == expected
    
    def test_operator_spacing(self):
        """Test operator spacing fixes"""
        input_code = "a=1+b-2*c/3"
        result = code_utils.fix_common_code_issues(input_code)
        # Should add spaces around operators
        assert "=" in result and "+" in result and "-" in result and "/" in result
    
    def test_excessive_whitespace_cleanup(self):
        """Test cleanup of excessive whitespace"""
        input_code = "def hello():    \\n    \\n    pass\\n"
        result = code_utils.fix_common_code_issues(input_code)
        assert result.strip() == "def hello():\n    pass"


class TestSanitizeJsonContent:
    """Test JSON content sanitization"""
    
    def test_dict_sanitization(self):
        """Test sanitizing dictionary content"""
        input_data = {
            "code": "def hello():\\n    pass",
            "test": "import pytest\\n\\ndef test():\\n    pass",
            "metadata": "simple\\ntext"
        }
        result = code_utils.sanitize_json_content(input_data)
        assert result["code"] == "def hello():\n    pass"
        assert result["test"] == "import pytest\n\ndef test():\n    pass"
        assert result["metadata"] == "simple\ntext"
    
    def test_list_sanitization(self):
        """Test sanitizing list content"""
        input_list = [
            "item1\\nitem2",
            {"nested": "value\\nwith\\nnewlines"}
        ]
        result = code_utils.sanitize_json_content(input_list)
        assert result[0] == "item1\nitem2"
        assert result[1]["nested"] == "value\nwith\nnewlines"


class TestExtractCodeFromResponse:
    """Test code extraction from responses"""
    
    def test_extract_from_code_blocks(self):
        """Test extracting code from markdown blocks"""
        response = '''Here's some code:
        
        ```python
        def hello():
            print("world")
        ```
        
        And here's some explanation.'''
        result = code_utils.extract_code_from_response(response)
        assert 'def hello():' in result
        assert 'print("world")' in result
    
    def test_extract_from_python_patterns(self):
        """Test extracting code based on Python patterns"""
        response = '''Here's my function: def test_function(): return 42. 
        It's a simple function that returns 42.'''
        result = code_utils.extract_code_from_response(response)
        assert result.startswith('def test_function():')
        assert 'return 42' in result
    
    def test_no_code_found(self):
        """Test fallback when no clear code is found"""
        response = 'This is just some explanation text without any code.'
        result = code_utils.extract_code_from_response(response)
        assert result == response
    
    def test_multiple_code_blocks(self):
        """Test extracting from multiple code blocks"""
        response = '''First block:
        ```python
        def hello():
            pass
        ```
        Second block:
        ```python
        def world():
            pass
        ```'''
        result = code_utils.extract_code_from_response(response)
        assert 'def hello():' in result
        assert 'def world():' in result


class TestIntegration:
    """Integration tests combining multiple functions"""
    
    def test_complete_newline_handling_pipeline(self):
        """Test complete pipeline from JSON to clean code"""
        # Simulate a model response with escaped newlines
        model_response = '''```json
        {
            "filename": "test_func",
            "code": "def test_function():\\n    \\"Code with newlines and quotes\\"\\n    return True",
            "test": "import pytest\\n\\ndef test_test_function():\\n    assert test_function() == True"
        }
        ```'''
        
        # Clean the JSON response
        cleaned_json = code_utils.clean_json_response(model_response)
        parsed = json.loads(cleaned_json)
        
        # Clean the code content
        cleaned_code = code_utils.clean_code_content(parsed['code'])
        cleaned_test = code_utils.clean_code_content(parsed['test'])
        
        # Verify the results
        assert 'def test_function():' in cleaned_code
        assert '"Code with newlines and quotes"' in cleaned_code
        assert 'import pytest\n\ndef test_test_function():' in cleaned_test
        
        # Verify the syntax is valid
        is_valid, error = code_utils.validate_python_syntax(cleaned_code)
        assert is_valid, f"Code syntax error: {error}"
    
    def test_problematic_case_from_existing_build(self):
        """Test handling of the actual problematic case we observed"""
        problematic_code = 'import sys\\nfrom parse_args import parse_args\\nfrom convert_to_float import convert_to_float\\nfrom add_numbers import add_numbers\\nfrom print_result import print_result\\n\\n\\ndef main():\\n    try:\\n        arg1, arg2 = parse_args()\\n    except Exception as e:\\n        print(f"Error parsing arguments: {e}", file=sys.stderr)\\n        sys.exit(1)\\n\\n    try:\\n        num1 = convert_to_float(arg1)\\n        num2 = convert_to_float(arg2)\\n    except ValueError as e:\\n        print(f"Invalid number: {e}", file=sys.stderr)\\n        sys.exit(1)\\n\\n    try:\\n        result = add_numbers(num1, num2)\\n    except Exception as e:\\n        print(f"Error adding numbers: {e}", file=sys.stderr)\\n        sys.exit(1)\\n\\n    print_result(result)\\n\\n\\nif __name__ == "__main__":\\n    main()'
        
        cleaned_code = code_utils.clean_code_content(problematic_code)
        
        # Verify newlines are properly decoded
        assert '\n' in cleaned_code
        assert '\\n' not in cleaned_code
        
        # Verify the syntax is valid
        is_valid, error = code_utils.validate_python_syntax(cleaned_code)
        assert is_valid, f"Fixed code should have valid syntax: {error}"