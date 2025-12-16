#!/usr/bin/env python3
"""
Tests for module_forge integration layer
"""

import pytest
import json
import os
import sys
from unittest.mock import patch, MagicMock, mock_open

# Add src to path for importing
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

import module_forge


class TestModuleForgeMain:
    """Test the main module_forge integration function"""
    
    @patch('module_designer.draft_blueprint')
    @patch('factory_manager.build_components')
    @patch('factory_manager.assemble_main')
    @patch('builtins.open', new_callable=mock_open)
    @patch('builtins.print')
    def test_main_success_flow(self, mock_print, mock_file, mock_assemble, mock_build, mock_draft):
        """Test successful end-to-end module generation"""
        # Setup mocks
        mock_blueprint = {
            'module_name': 'test_module',
            'functions': [
                {'name': 'test_func', 'signature': 'def test_func()', 'description': 'A test function'}
            ]
        }
        mock_draft.return_value = mock_blueprint
        mock_build.return_value = (True, 'build/test_module', ['test_func'])
        
        # Mock file operations
        mock_file.return_value.write = MagicMock()
        
        # Execute
        with patch('sys.argv', ['module_forge.py', 'test request']):
            module_forge.main()
        
        # Verify blueprint design
        mock_draft.assert_called_once_with('test request')
        
        # Verify blueprint was saved
        mock_file.assert_any_call('blueprint.json', 'w')
        written_data = mock_file.return_value.write.call_args[0][0]
        saved_blueprint = json.loads(written_data)
        assert saved_blueprint['module_name'] == 'test_module'
        
        # Verify component building
        mock_build.assert_called_once_with(mock_blueprint)
        
        # Verify module assembly
        mock_assemble.assert_called_once_with(mock_blueprint, 'build/test_module', ['test_func'])
        
        # Verify success messages
        mock_print.assert_any_call('[✅] Blueprint designed: test_module')
        mock_print.assert_any_call('[✅] Components built: [\'test_func\']')
        mock_print.assert_any_call('[✅] Module assembled successfully!')
    
    @patch('module_designer.draft_blueprint')
    @patch('builtins.print')
    def test_main_no_arguments(self, mock_print, mock_draft):
        """Test main function with no arguments"""
        with patch('sys.argv', ['module_forge.py']):
            with pytest.raises(SystemExit) as exc_info:
                module_forge.main()
            assert exc_info.value.code == 1
            mock_print.assert_any_call('Usage: python module_forge.py \'I need a tool that...\'')
    
    @patch('module_designer.draft_blueprint')
    @patch('builtins.print')
    def test_main_blueprint_failure(self, mock_print, mock_draft):
        """Test main function when blueprint design fails"""
        mock_draft.return_value = None
        
        with patch('sys.argv', ['module_forge.py', 'test request']):
            with pytest.raises(SystemExit) as exc_info:
                module_forge.main()
            assert exc_info.value.code == 1
            mock_print.assert_any_call('[❌] Failed to generate blueprint. Aborting.')
    
    @patch('module_designer.draft_blueprint')
    @patch('factory_manager.build_components')
    @patch('builtins.open', new_callable=mock_open)
    @patch('builtins.print')
    def test_main_build_failure(self, mock_print, mock_file, mock_build, mock_draft):
        """Test main function when component building fails"""
        mock_blueprint = {
            'module_name': 'test_module',
            'functions': []
        }
        mock_draft.return_value = mock_blueprint
        mock_build.return_value = (False, 'build/test_module', [])
        
        mock_file.return_value.write = MagicMock()
        
        with patch('sys.argv', ['module_forge.py', 'test request']):
            with pytest.raises(SystemExit) as exc_info:
                module_forge.main()
            assert exc_info.value.code == 1
            mock_print.assert_any_call('[❌] Failed to build components. Aborting.')
    
    @patch('module_designer.draft_blueprint')
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
        mock_build.return_value = (True, 'build/test_module', [])
        mock_assemble.side_effect = Exception("Assembly error")
        
        mock_file.return_value.write = MagicMock()
        
        with patch('sys.argv', ['module_forge.py', 'test request']):
            with pytest.raises(SystemExit) as exc_info:
                module_forge.main()
            assert exc_info.value.code == 1
            mock_print.assert_any_call('[❌] Failed to assemble module: Assembly error')


class TestModuleForgeIntegration:
    """Test integration between module_forge components"""
    
    @patch('module_designer.draft_blueprint')
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
        mock_build.return_value = (True, 'build/stock_analyzer', ['fetch_prices', 'calculate_average'])
        
        mock_file.return_value.write = MagicMock()
        
        with patch('sys.argv', ['module_forge.py', 'Create stock analyzer']):
            module_forge.main()
        
        # Verify complete workflow
        mock_draft.assert_called_once_with('Create stock analyzer')
        mock_build.assert_called_once_with(mock_blueprint)
        mock_assemble.assert_called_once()
        
        # Verify blueprint contains expected structure
        written_data = mock_file.return_value.write.call_args[0][0]
        saved_blueprint = json.loads(written_data)
        assert len(saved_blueprint['functions']) == 2
        assert saved_blueprint['module_name'] == 'stock_analyzer'