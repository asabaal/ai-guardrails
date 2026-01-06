import pytest
import sys
import os
import tempfile
import json
from unittest.mock import patch, MagicMock, mock_open
from collections import namedtuple

from ironclad_ai_guardrails.ui_cli import (
    main,
    load_module_spec,
    validate_ui_type,
    create_sample_module_spec,
    handle_generate,
    handle_validate,
    handle_create_sample,
    handle_list_types
)
from ironclad_ai_guardrails.ui_spec import UIType


def create_mock_args(**kwargs):
    """Create mock args object"""
    Args = namedtuple('Args', kwargs.keys())
    return Args(**kwargs)


class TestLoadModuleSpec:
    """Test module specification loading"""
    
    def test_load_module_spec_success(self):
        """Test successful loading of module specification"""
        spec_data = {
            "module_name": "test_module",
            "functions": [{"name": "test_func"}]
        }
        with patch("builtins.open", mock_open(read_data=json.dumps(spec_data))):
            result = load_module_spec("test_spec.json")
            assert result == spec_data
    
    def test_load_module_spec_file_not_found(self):
        """Test handling of missing specification file"""
        with patch("builtins.open", side_effect=FileNotFoundError):
            with pytest.raises(SystemExit) as exc_info:
                load_module_spec("nonexistent.json")
            assert exc_info.value.code == 1
    
    def test_load_module_spec_invalid_json(self):
        """Test handling of invalid JSON"""
        with patch("builtins.open", mock_open(read_data="invalid json")):
            with pytest.raises(SystemExit) as exc_info:
                load_module_spec("invalid.json")
            assert exc_info.value.code == 1
    
    def test_load_module_spec_general_error(self):
        """Test handling of general read errors"""
        with patch("builtins.open", side_effect=Exception("Read error")):
            with pytest.raises(SystemExit) as exc_info:
                load_module_spec("error.json")
            assert exc_info.value.code == 1


class TestValidateUIType:
    """Test UI type validation"""
    
    def test_validate_ui_type_valid(self):
        """Test validation of valid UI types"""
        for ui_type in ["web", "cli_gui", "desktop", "api_docs", "cli_tui"]:
            result = validate_ui_type(ui_type)
            assert isinstance(result, UIType)
    
    def test_validate_ui_type_case_insensitive(self):
        """Test case insensitive UI type validation"""
        result = validate_ui_type("WEB")
        assert result == UIType.WEB
    
    def test_validate_ui_type_invalid(self):
        """Test handling of invalid UI type"""
        with pytest.raises(SystemExit) as exc_info:
            validate_ui_type("invalid_type")
        assert exc_info.value.code == 1


class TestCreateSampleModuleSpec:
    """Test sample module specification creation"""
    
    def test_create_sample_module_spec_structure(self):
        """Test structure of sample specification"""
        spec = create_sample_module_spec()
        assert "module_name" in spec
        assert "main_logic_description" in spec
        assert "functions" in spec
        assert isinstance(spec["functions"], list)
        assert len(spec["functions"]) > 0


class TestHandleListTypes:
    """Test list-types command handler"""
    
    def test_handle_list_types_output(self, capsys):
        """Test list-types command output"""
        handle_list_types()
        captured = capsys.readouterr()
        assert "Available UI Types" in captured.out
        assert "web" in captured.out
        assert "cli_gui" in captured.out
        assert "desktop" in captured.out


class TestHandleCreateSample:
    """Test create-sample command handler"""
    
    def test_handle_create_sample_success(self):
        """Test successful sample creation"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            output_path = f.name
        
        try:
            args = create_mock_args(output=output_path)
            handle_create_sample(args)
            
            # Verify file was created
            assert os.path.exists(output_path)
            
            # Verify content
            with open(output_path, 'r') as f:
                spec = json.load(f)
                assert "module_name" in spec
                assert "functions" in spec
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_handle_create_sample_with_exception(self, capsys):
        """Test create-sample with exception (lines 258-260)"""
        args = create_mock_args(output="/invalid/path/file.json")
        
        with patch('sys.exit') as mock_exit:
            handle_create_sample(args)
            mock_exit.assert_called_once_with(1)
        
        captured = capsys.readouterr()
        assert "Error creating sample" in captured.out


class TestHandleValidate:
    """Test validate command handler"""
    
    def test_handle_validate_missing_directory(self):
        """Test validation with missing directory"""
        args = create_mock_args(ui_dir="/nonexistent/directory", ui_type="web")
        with pytest.raises(SystemExit) as exc_info:
            handle_validate(args)
        assert exc_info.value.code == 1
    
    @patch('ironclad_ai_guardrails.ui_cli.validate_ui_directory')
    def test_handle_validate_success(self, mock_validate, capsys):
        """Test successful validation"""
        # Mock successful validation result
        from ironclad_ai_guardrails.ui_validator import ValidationStatus, ValidationResult
        mock_validate.return_value = ValidationResult(
            status=ValidationStatus.PASSED,
            issues=[],
            execution_time=0.5,
            metadata={"total_issues": 0}
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            args = create_mock_args(ui_dir=temp_dir, ui_type="web")
            handle_validate(args)
            
            captured = capsys.readouterr()
            assert "VALIDATION RESULTS" in captured.out
            assert "Validation passed!" in captured.out
    
    def test_handle_validate_with_failed_status(self):
        """Test validation with failed status (lines 224-225, 229)"""
        from ironclad_ai_guardrails.ui_validator import ValidationStatus, ValidationResult, ValidationLevel, ValidationIssue
        
        with tempfile.TemporaryDirectory() as temp_dir:
            args = create_mock_args(ui_dir=temp_dir, ui_type="web")
            
            with patch('ironclad_ai_guardrails.ui_cli.validate_ui_directory') as mock_validate:
                mock_validate.return_value = ValidationResult(
                    status=ValidationStatus.FAILED,
                    issues=[ValidationIssue(level=ValidationLevel.ERROR, message="Test error")],
                    execution_time=0.5,
                    metadata={"total_issues": 1}
                )
                
                with pytest.raises(SystemExit) as exc_info:
                    handle_validate(args)
                assert exc_info.value.code == 1
    
    @patch('ironclad_ai_guardrails.ui_cli.validate_ui_directory')
    def test_handle_validate_with_warning_status(self, mock_validate, capsys):
        """Test validation with warning status (line 231)"""
        from ironclad_ai_guardrails.ui_validator import ValidationStatus, ValidationResult
        mock_validate.return_value = ValidationResult(
            status=ValidationStatus.WARNING,
            issues=[],
            execution_time=0.5,
            metadata={}
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            args = create_mock_args(ui_dir=temp_dir, ui_type="web")
            with patch('sys.exit') as mock_exit:
                handle_validate(args)
                mock_exit.assert_called_once_with(2)
    
    @patch('ironclad_ai_guardrails.ui_cli.validate_ui_directory')
    def test_handle_validate_with_exception(self, mock_validate, capsys):
        """Test validation with exception (lines 235-237)"""
        mock_validate.side_effect = Exception("Validation error")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            args = create_mock_args(ui_dir=temp_dir, ui_type="web")
            with patch('sys.exit') as mock_exit:
                handle_validate(args)
                mock_exit.assert_called_once_with(1)
        
        captured = capsys.readouterr()
        assert "Error during validation" in captured.out


class TestHandleGenerate:
    """Test generate command handler"""
    
    @patch('ironclad_ai_guardrails.ui_cli.validate_ui_type')
    @patch('ironclad_ai_guardrails.ui_cli.transform_module_spec_to_ui_spec')
    @patch('ironclad_ai_guardrails.ui_cli.save_ui_artifacts')
    @patch('ironclad_ai_guardrails.ui_cli.validate_ui_directory')
    @patch('ironclad_ai_guardrails.ui_cli.load_module_spec')
    def test_handle_generate_with_validation_flag_enabled(self, mock_load_spec, mock_validate_ui, mock_save, mock_transform, mock_validate_type):
        """Test generate command with validation enabled (lines 187-195)"""
        from ironclad_ai_guardrails.ui_validator import ValidationStatus, ValidationResult
        mock_load_spec.return_value = {"module_name": "test", "functions": []}
        mock_validate_type.return_value = UIType.WEB
        mock_transform.return_value = MagicMock()
        mock_save.return_value = ["index.html", "styles.css"]
        mock_validate_ui.return_value = ValidationResult(
            status=ValidationStatus.PASSED,
            issues=[],
            execution_time=0.1,
            metadata={}
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            args = create_mock_args(
                spec="spec.json",
                type="web",
                output=temp_dir,
                validate=True,
                title=None
            )
            handle_generate(args)
        
        mock_validate_ui.assert_called_once()
    
    @patch('ironclad_ai_guardrails.ui_cli.validate_ui_type')
    @patch('ironclad_ai_guardrails.ui_cli.transform_module_spec_to_ui_spec')
    @patch('ironclad_ai_guardrails.ui_cli.save_ui_artifacts')
    @patch('ironclad_ai_guardrails.ui_cli.validate_ui_directory')
    @patch('ironclad_ai_guardrails.ui_cli.load_module_spec')
    def test_handle_generate_with_validation_issues_output(self, mock_load_spec, mock_validate_ui, mock_save, mock_transform, mock_validate_type):
        """Test generate with validation issues output (lines 187-195)"""
        from ironclad_ai_guardrails.ui_validator import ValidationLevel, ValidationStatus, ValidationResult, ValidationIssue
        mock_load_spec.return_value = {"module_name": "test", "functions": []}
        mock_validate_type.return_value = UIType.WEB
        mock_transform.return_value = MagicMock()
        mock_save.return_value = ["index.html", "styles.css"]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            args = create_mock_args(
                spec="spec.json",
                type="web",
                output=temp_dir,
                validate=True,
                title=None
            )
            with patch('ironclad_ai_guardrails.ui_cli.validate_ui_directory') as mock_validate_dir:
                mock_validate_dir.return_value = ValidationResult(
                    status=ValidationStatus.PASSED,
                    issues=[ValidationIssue(level=ValidationLevel.INFO, message="Test issue")],
                    execution_time=0.1,
                    metadata={}
                )
                handle_generate(args)
    
    @patch('ironclad_ai_guardrails.ui_cli.validate_ui_type')
    @patch('ironclad_ai_guardrails.ui_cli.transform_module_spec_to_ui_spec')
    @patch('ironclad_ai_guardrails.ui_cli.save_ui_artifacts')
    @patch('ironclad_ai_guardrails.ui_cli.load_module_spec')
    def test_handle_generate_failure_exit(self, mock_load_spec, mock_save, mock_transform, mock_validate_type):
        """Test generate command with failure (lines 202-203)"""
        mock_load_spec.return_value = {"module_name": "test", "functions": []}
        mock_validate_type.return_value = UIType.WEB
        mock_transform.return_value = MagicMock()
        mock_save.side_effect = Exception("Generation error")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            args = create_mock_args(
                spec="spec.json",
                type="web",
                output=temp_dir,
                validate=False,
                title=None
            )
            with patch('sys.exit') as mock_exit:
                handle_generate(args)
                mock_exit.assert_called_once_with(1)
    
    @patch('ironclad_ai_guardrails.ui_cli.validate_ui_type')
    @patch('ironclad_ai_guardrails.ui_cli.transform_module_spec_to_ui_spec')
    @patch('ironclad_ai_guardrails.ui_cli.save_ui_artifacts')
    @patch('ironclad_ai_guardrails.ui_cli.load_module_spec')
    def test_handle_generate_all_types(self, mock_load_spec, mock_save, mock_transform, mock_validate_type):
        """Test generating all UI types (lines 151-152, 174, 200)"""
        mock_load_spec.return_value = {"module_name": "test", "functions": []}
        mock_validate_type.return_value = UIType.WEB
        mock_transform.return_value = MagicMock()
        mock_save.return_value = ["index.html", "styles.css"]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            args = create_mock_args(
                spec="spec.json",
                type="all",
                output=temp_dir,
                validate=False,
                title=None
            )
            handle_generate(args)
        
        assert mock_save.call_count == len([t.value for t in UIType])


class TestUICLIMain:
    """Test main CLI entry point"""
    
    def test_main_no_command_shows_help(self, capsys):
        """Test that main shows help when no command provided"""
        with patch('sys.argv', ['ironclad-ui']):
            with patch('sys.exit') as mock_exit:
                main()
                mock_exit.assert_called_once_with(1)
        
        captured = capsys.readouterr()
        assert "usage:" in captured.out.lower() or "usage:" in captured.out
    
    @patch('ironclad_ai_guardrails.ui_cli.handle_generate')
    def test_main_generate_command(self, mock_handle_generate):
        """Test main with generate command"""
        with patch('sys.argv', ['ironclad-ui', 'generate', '--spec', 'spec.json', '--type', 'web', '--output', './ui']):
            with patch('sys.exit'):
                main()
        
        mock_handle_generate.assert_called_once()
        args = mock_handle_generate.call_args[0][0]
        assert args.spec == 'spec.json'
        assert args.type == 'web'
        assert args.output == './ui'
    
    @patch('ironclad_ai_guardrails.ui_cli.handle_validate')
    def test_main_validate_command(self, mock_handle_validate):
        """Test main with validate command"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('sys.argv', ['ironclad-ui', 'validate', '--ui-dir', temp_dir, '--ui-type', 'web']):
                with patch('sys.exit'):
                    main()
            
            mock_handle_validate.assert_called_once()
            args = mock_handle_validate.call_args[0][0]
            assert args.ui_dir == temp_dir
            assert args.ui_type == 'web'
    
    @patch('ironclad_ai_guardrails.ui_cli.handle_create_sample')
    def test_main_create_sample_command(self, mock_handle_create_sample):
        """Test main with create-sample command"""
        with patch('sys.argv', ['ironclad-ui', 'create-sample', '--output', 'sample.json']):
            with patch('sys.exit'):
                main()
        
        mock_handle_create_sample.assert_called_once()
        args = mock_handle_create_sample.call_args[0][0]
        assert args.output == 'sample.json'
    
    @patch('ironclad_ai_guardrails.ui_cli.handle_list_types')
    def test_main_list_types_command(self, mock_handle_list_types):
        """Test main with list-types command"""
        with patch('sys.argv', ['ironclad-ui', 'list-types']):
            with patch('sys.exit'):
                main()
        
        mock_handle_list_types.assert_called_once()
    
    @patch('ironclad_ai_guardrails.ui_cli.handle_generate')
    def test_main_with_custom_title(self, mock_handle_generate):
        """Test main with custom title parameter"""
        with patch('sys.argv', ['ironclad-ui', 'generate', '--spec', 'spec.json', '--type', 'web', '--output', './ui', '--title', 'Custom Title']):
            with patch('sys.exit'):
                main()
        
        mock_handle_generate.assert_called_once()
        args = mock_handle_generate.call_args[0][0]
        assert args.title == 'Custom Title'
    
    @patch('ironclad_ai_guardrails.ui_cli.handle_generate')
    def test_main_with_validate_flag(self, mock_handle_generate):
        """Test main with validate flag"""
        with patch('sys.argv', ['ironclad-ui', 'generate', '--spec', 'spec.json', '--type', 'web', '--output', './ui', '--validate']):
            with patch('sys.exit'):
                main()
        
        mock_handle_generate.assert_called_once()
        args = mock_handle_generate.call_args[0][0]
        assert args.validate is True
