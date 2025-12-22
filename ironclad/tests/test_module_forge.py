#!/usr/bin/env python3
"""
Tests for module_forge integration layer
"""

import pytest
import json
import os
import sys
import argparse
from unittest.mock import patch, MagicMock, mock_open

# Add src to path for importing
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

import module_forge


class TestModuleForgeMain:
    """Test the main module_forge integration function"""
    
    @patch('module_forge.draft_blueprint')
    @patch('factory_manager.build_components')
    @patch('factory_manager.assemble_main')
    @patch('builtins.open', new_callable=mock_open)
    @patch('builtins.print')
    def test_main_blueprint_failure(self, mock_print, mock_file, mock_assemble, mock_build, mock_draft):
        """Test main function when blueprint design fails"""
        mock_draft.return_value = None
        mock_build.return_value = (False, 'build/test_module', [], [], {})
        
        with patch('argparse.ArgumentParser.parse_args') as mock_parse:
            mock_parse.return_value = argparse.Namespace(request='test request', resume=False)
            with pytest.raises(SystemExit) as exc_info:
                module_forge.main()
            assert exc_info.value.code == 1
            mock_print.assert_any_call('[❌] Failed to generate blueprint. Aborting.')
    
    @patch('module_forge.draft_blueprint')
    @patch('factory_manager.build_components')
    @patch('factory_manager.assemble_main')
    @patch('builtins.open', new_callable=mock_open)
    @patch('builtins.print')
    def test_main_build_failure(self, mock_print, mock_file, mock_assemble, mock_build, mock_draft):
        """Test main function when component building fails"""
        mock_blueprint = {
            'module_name': 'test_module',
            'functions': []
        }
        mock_draft.return_value = mock_blueprint
        mock_build.return_value = (False, 'build/test_module', [], [], {})
        
        mock_file.return_value.write = MagicMock()
        
        with patch('sys.argv', ['module_forge.py', 'test request']):
            with pytest.raises(SystemExit) as exc_info:
                module_forge.main()
            assert exc_info.value.code == 1
            mock_print.assert_any_call('[❌] No components could be built successfully. Aborting.')
    
    @patch('module_forge.draft_blueprint')
    @patch('factory_manager.build_components')
    @patch('factory_manager.assemble_main')
    @patch('builtins.open', new_callable=mock_open)
    @patch('builtins.print')
    def test_main_assembly_failure(self, mock_print, mock_file, mock_assemble, mock_build, mock_draft):
        """Test main function when module assembly fails"""
        mock_blueprint = {
            'module_name': 'test_module',
            'functions': []
        }
        mock_draft.return_value = mock_blueprint
        mock_build.return_value = (True, 'build/test_module', ['test_func'], [], {})
        mock_assemble.side_effect = Exception("Assembly error")
        
        mock_file.return_value.write = MagicMock()
        
        with patch('sys.argv', ['module_forge.py', 'test request']):
            with pytest.raises(SystemExit) as exc_info:
                module_forge.main()
            assert exc_info.value.code == 1
            mock_print.assert_any_call('[❌] Failed to assemble module: Assembly error')


class TestModuleForgeIntegration:
    """Test integration between module_forge components"""
    
    @patch('module_forge.draft_blueprint')
    @patch('factory_manager.build_components')
    @patch('factory_manager.assemble_main')
    @patch('builtins.open', new_callable=mock_open)
    def test_full_integration_workflow(self, mock_file, mock_assemble, mock_build, mock_draft):
        """Test complete integration workflow"""
        # Setup realistic blueprint
        mock_blueprint = {
            'module_name': 'stock_analyzer',
            'functions': [
                {
                    'name': 'fetch_prices',
                    'signature': 'def fetch_prices(tickers: list) -> dict',
                    'description': 'Fetch stock prices'
                },
                {
                    'name': 'calculate_average',
                    'signature': 'def calculate_average(prices: dict) -> float',
                    'description': 'Calculate average price'
                }
            ],
            'main_logic_description': 'Process stock data and save to CSV'
        }
        
        mock_draft.return_value = mock_blueprint
        mock_build.return_value = (True, 'build/stock_analyzer', ['fetch_prices', 'calculate_average'], [], {})
        
        mock_file.return_value.write = MagicMock()
        
        with patch('argparse.ArgumentParser.parse_args') as mock_parse:
            mock_parse.return_value = argparse.Namespace(request='Create stock analyzer', resume=False)
            module_forge.main()
        
        # Verify complete workflow
        mock_draft.assert_called_once_with('Create stock analyzer')
        mock_build.assert_called_once_with(mock_blueprint, "smart")
        mock_assemble.assert_called_once()
        
        # Verify blueprint contains expected structure
        # Get all write calls and join them to reconstruct the JSON
        write_calls = [call[0][0] for call in mock_file.return_value.write.call_args_list]
        written_data = ''.join(write_calls)
        saved_blueprint = json.loads(written_data)
        assert len(saved_blueprint['functions']) == 2
        assert saved_blueprint['module_name'] == 'stock_analyzer'


class TestModuleForgeResume:
    """Test resume functionality in module_forge"""
    
    @patch('module_forge.draft_blueprint')
    @patch('factory_manager.build_components')
    @patch('factory_manager.assemble_main')
    @patch('builtins.open', new_callable=mock_open)
    @patch('builtins.print')
    def test_resume_mode_flag(self, mock_print, mock_file, mock_assemble, mock_build, mock_draft):
        """Test --resume flag functionality"""
        mock_blueprint = {
            'module_name': 'test_module',
            'functions': [
                {'name': 'test_func', 'signature': 'def test_func()', 'description': 'A test function'}
            ]
        }
        mock_draft.return_value = mock_blueprint
        mock_build.return_value = (True, 'build/test_module', ['test_func'], [], {})
        
        mock_file.return_value.write = MagicMock()
        
        # Execute with --resume flag
        with patch('argparse.ArgumentParser.parse_args') as mock_parse:
            mock_parse.return_value = argparse.Namespace(request='test request', resume=True)
            module_forge.main()
        
        # Verify build_components was called with resume mode
        mock_build.assert_called_once_with(mock_blueprint, "resume")
        
        # Verify resume mode message
        mock_print.assert_any_call('🔄 RESUME MODE - Continuing from existing progress')


class TestModuleForgePartialFailure:
    """Test module_forge with partial component failures"""
    
    @patch('module_forge.draft_blueprint')
    @patch('factory_manager.build_components')
    @patch('factory_manager.assemble_main')
    @patch('builtins.open', new_callable=mock_open)
    @patch('builtins.print')
    def test_partial_component_failure(self, mock_print, mock_file, mock_assemble, mock_build, mock_draft):
        """Test case where some components fail but others succeed"""
        mock_blueprint = {
            'module_name': 'test_module',
            'functions': [
                {'name': 'success_func', 'signature': 'def success_func()', 'description': 'A successful function'},
                {'name': 'fail_func', 'signature': 'def fail_func()', 'description': 'A failing function'}
            ]
        }
        mock_draft.return_value = mock_blueprint
        # Return partial success: some components succeed, others fail
        mock_build.return_value = (True, 'build/test_module', ['success_func'], ['fail_func'], {})
        
        mock_file.return_value.write = MagicMock()
        
        with patch('argparse.ArgumentParser.parse_args') as mock_parse:
            mock_parse.return_value = argparse.Namespace(request='test request', resume=False)
            module_forge.main()
        
        # Verify failed components message (line 76)
        mock_print.assert_any_call('    ❌ [\'fail_func\']')
        
        # Verify partial success completion message (lines 93-94)
        mock_print.assert_any_call('🎉 MODULE FORGE COMPLETE - Module ready with 1 components skipped')
        mock_print.assert_any_call('   ⚠️  Skipped components: fail_func')