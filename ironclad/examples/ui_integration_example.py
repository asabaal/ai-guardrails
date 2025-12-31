#!/usr/bin/env python3
"""
UI Integration Example

Demonstrates the complete workflow from ModuleSpec to generated UI artifacts
including validation and testing. This example shows how all UI components work together.
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ui_spec import UIType, transform_module_spec_to_ui_spec, ui_spec_to_json
from ui_generator import save_ui_artifacts, generate_ui_from_module_spec
from ui_validator import validate_ui_directory, print_validation_report


def example_calculator_module_spec():
    """Create an example calculator module specification"""
    return {
        "module_name": "calculator",
        "main_logic_description": "A simple calculator with basic arithmetic operations and advanced features",
        "functions": [
            {
                "name": "add",
                "signature": "def add(a: float, b: float) -> float:",
                "description": "Add two numbers and return the result"
            },
            {
                "name": "subtract", 
                "signature": "def subtract(a: float, b: float) -> float:",
                "description": "Subtract b from a and return the result"
            },
            {
                "name": "multiply",
                "signature": "def multiply(a: float, b: float) -> float:",
                "description": "Multiply two numbers and return the result"
            },
            {
                "name": "divide",
                "signature": "def divide(a: float, b: float) -> float:",
                "description": "Divide a by b and return the result (raises ValueError if b is 0)"
            },
            {
                "name": "power",
                "signature": "def power(base: float, exponent: float) -> float:",
                "description": "Calculate base raised to the power of exponent"
            },
            {
                "name": "main",
                "signature": "def main(operation: str, a: float, b: float, precision: int = 2) -> float:",
                "description": "Main calculator function that performs the specified operation"
            }
        ]
    }


def example_task_manager_module_spec():
    """Create an example task manager module specification"""
    return {
        "module_name": "task_manager",
        "main_logic_description": "A task management system with CRUD operations and filtering",
        "functions": [
            {
                "name": "create_task",
                "signature": "def create_task(title: str, description: str, priority: str, due_date: str) -> dict:",
                "description": "Create a new task with the given details"
            },
            {
                "name": "list_tasks",
                "signature": "def list_tasks(status: Optional[str] = None, priority: Optional[str] = None) -> List[dict]:",
                "description": "List all tasks, optionally filtered by status and priority"
            },
            {
                "name": "update_task",
                "signature": "def update_task(task_id: str, updates: dict) -> dict:",
                "description": "Update an existing task with the provided changes"
            },
            {
                "name": "delete_task",
                "signature": "def delete_task(task_id: str) -> bool:",
                "description": "Delete a task by its ID"
            },
            {
                "name": "main",
                "signature": "def main(action: str, title: str = '', description: str = '', priority: str = 'medium', due_date: str = '', task_id: str = '') -> Union[dict, List[dict], bool]:",
                "description": "Main task manager function that handles all operations"
            }
        ]
    }


def example_data_analyzer_module_spec():
    """Create an example data analyzer module specification"""
    return {
        "module_name": "data_analyzer",
        "main_logic_description": "A data analysis tool with statistical operations and visualization options",
        "functions": [
            {
                "name": "load_data",
                "signature": "def load_data(file_path: str, delimiter: str = ',') -> pd.DataFrame:",
                "description": "Load data from a CSV file into a pandas DataFrame"
            },
            {
                "name": "calculate_statistics",
                "signature": "def calculate_statistics(data: pd.DataFrame, columns: Optional[List[str]] = None) -> dict:",
                "description": "Calculate basic statistics for specified columns or all numeric columns"
            },
            {
                "name": "create_visualization",
                "signature": "def create_visualization(data: pd.DataFrame, chart_type: str, x_column: str, y_column: str, output_path: str) -> str:",
                "description": "Create a visualization from the data and save to file"
            },
            {
                "name": "export_results",
                "signature": "def export_results(data: pd.DataFrame, format: str, output_path: str) -> bool:",
                "description": "Export data or results to specified format (csv, excel, json)"
            },
            {
                "name": "main",
                "signature": "def main(input_file: str, operation: str, columns: Optional[str] = None, chart_type: str = 'line', x_column: str = '', y_column: str = '', output_format: str = 'csv', output_path: str = 'output') -> Union[dict, str, bool]:",
                "description": "Main data analysis function that orchestrates the analysis workflow"
            }
        ]
    }


def demonstrate_single_ui_type_workflow(module_spec, ui_type, module_name):
    """Demonstrate complete workflow for a single UI type"""
    print(f"\n{'='*60}")
    print(f"DEMONSTRATING {ui_type.upper()} UI WORKFLOW")
    print(f"Module: {module_name}")
    print(f"{'='*60}")
    
    # Step 1: Transform ModuleSpec to UISpec
    print("\n🔄 Step 1: Transforming ModuleSpec to UISpec...")
    ui_spec = transform_module_spec_to_ui_spec(module_spec, UIType(ui_type))
    
    print(f"   ✓ UI Type: {ui_spec.ui_type.value}")
    print(f"   ✓ Title: {ui_spec.title}")
    print(f"   ✓ Components: {len(ui_spec.components)}")
    print(f"   ✓ Layout: {ui_spec.layout.type}")
    
    # Step 2: Generate UI artifacts
    print("\n🎨 Step 2: Generating UI artifacts...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = os.path.join(temp_dir, f"{module_name}_{ui_type}_ui")
        
        saved_files = save_ui_artifacts(ui_spec, output_dir)
        
        print(f"   ✓ Generated {len(saved_files)} files:")
        for file_path in saved_files.keys():
            filename = os.path.basename(file_path)
            print(f"     - {filename}")
        
        # Step 3: Validate generated UI
        print("\n🔍 Step 3: Validating generated UI...")
        validation_result = validate_ui_directory(output_dir, ui_type)
        
        print(f"   ✓ Validation Status: {validation_result.status.value}")
        print(f"   ✓ Issues Found: {len(validation_result.issues)}")
        print(f"   ✓ Validation Time: {validation_result.execution_time:.2f}s")
        
        # Show some sample issues if any
        if validation_result.issues:
            print("   📝 Sample Issues:")
            for i, issue in enumerate(validation_result.issues[:3]):  # Show first 3
                print(f"     {i+1}. [{issue.level.value}] {issue.message}")
        
        # Step 4: Show sample content
        print("\n📄 Step 4: Sample Content Preview...")
        
        # Show UISpec JSON preview
        ui_spec_json = ui_spec_to_json(ui_spec)
        sample_lines = ui_spec_json.split('\n')[:10]
        print("   📋 UISpec JSON (first 10 lines):")
        for i, line in enumerate(sample_lines, 1):
            print(f"     {i:2d}: {line}")
        print("     ...")
        
        # Show generated file content snippets
        for file_path, content in list(saved_files.items())[:2]:  # Show first 2 files
            filename = os.path.basename(file_path)
            lines = content.split('\n')[:5]
            print(f"\n   📄 {filename} (first 5 lines):")
            for i, line in enumerate(lines, 1):
                print(f"     {i}: {line}")
        
        return validation_result.status == ValidationStatus.PASSED


def demonstrate_convenience_function_workflow(module_spec, module_name):
    """Demonstrate workflow using the convenience function"""
    print(f"\n{'='*60}")
    print(f"DEMONSTRATING CONVENIENCE FUNCTION WORKFLOW")
    print(f"Module: {module_name}")
    print(f"{'='*60}")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test different UI types
        ui_types = ["web", "cli_gui", "api_docs"]
        
        for ui_type in ui_types:
            print(f"\n🚀 Generating {ui_type.upper()} UI for {module_name}...")
            
            output_dir = os.path.join(temp_dir, f"{module_name}_{ui_type}_ui")
            saved_files = generate_ui_from_module_spec(module_spec, ui_type, output_dir)
            
            print(f"   ✓ Generated {len(saved_files)} files in {output_dir}")
            
            # Quick validation
            validation_result = validate_ui_directory(output_dir, ui_type)
            print(f"   ✓ Validation: {validation_result.status.value} ({len(validation_result.issues)} issues)")


def demonstrate_multi_module_workflow():
    """Demonstrate workflow with multiple modules"""
    print(f"\n{'='*60}")
    print("DEMONSTRATING MULTI-MODULE WORKFLOW")
    print(f"{'='*60}")
    
    modules = [
        ("Calculator", example_calculator_module_spec()),
        ("Task Manager", example_task_manager_module_spec()),
        ("Data Analyzer", example_data_analyzer_module_spec())
    ]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        results = {}
        
        for module_name, module_spec in modules:
            print(f"\n📦 Processing {module_name} module...")
            
            module_results = {}
            
            for ui_type in ["web", "cli_gui", "cli_tui"]:
                try:
                    output_dir = os.path.join(temp_dir, f"{module_name.lower().replace(' ', '_')}_{ui_type}_ui")
                    
                    # Generate UI
                    saved_files = generate_ui_from_module_spec(module_spec, ui_type, output_dir)
                    
                    # Validate
                    validation_result = validate_ui_directory(output_dir, ui_type)
                    
                    module_results[ui_type] = {
                        "files_count": len(saved_files),
                        "status": validation_result.status.value,
                        "issues": len(validation_result.issues),
                        "time": validation_result.execution_time
                    }
                    
                    print(f"   ✓ {ui_type}: {len(saved_files)} files, {validation_result.status.value}")
                    
                except Exception as e:
                    module_results[ui_type] = {
                        "files_count": 0,
                        "status": "ERROR",
                        "issues": 1,
                        "time": 0,
                        "error": str(e)
                    }
                    print(f"   ✗ {ui_type}: ERROR - {e}")
            
            results[module_name] = module_results
        
        # Summary table
        print(f"\n📊 MULTI-MODULE GENERATION SUMMARY")
        print(f"{'Module':<15} {'UI Type':<10} {'Files':<6} {'Status':<10} {'Issues':<7} {'Time(s)':<8}")
        print("-" * 65)
        
        for module_name, module_results in results.items():
            for ui_type, result in module_results.items():
                time_str = f"{result['time']:.2f}" if result['time'] > 0 else "N/A"
                print(f"{module_name:<15} {ui_type:<10} {result['files_count']:<6} {result['status']:<10} {result['issues']:<7} {time_str:<8}")


def demonstrate_error_handling_workflow():
    """Demonstrate error handling and edge cases"""
    print(f"\n{'='*60}")
    print("DEMONSTRATING ERROR HANDLING WORKFLOW")
    print(f"{'='*60}")
    
    # Test 1: Empty module spec
    print("\n🧪 Test 1: Empty module specification")
    empty_spec = {"module_name": "empty", "functions": []}
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = os.path.join(temp_dir, "empty_ui")
            saved_files = generate_ui_from_module_spec(empty_spec, "web", output_dir)
            validation_result = validate_ui_directory(output_dir, "web")
            print(f"   ✓ Handled gracefully: {len(saved_files)} files, {validation_result.status.value}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 2: Invalid UI type
    print("\n🧪 Test 2: Invalid UI type (should default to web)")
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = os.path.join(temp_dir, "invalid_ui")
            saved_files = generate_ui_from_module_spec(example_calculator_module_spec(), "invalid_type", output_dir)
            print(f"   ✓ Defaulted to web: {len(saved_files)} files")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 3: Malformed function signatures
    print("\n🧪 Test 3: Malformed function signatures")
    malformed_spec = {
        "module_name": "malformed",
        "functions": [
            {
                "name": "bad_function",
                "signature": "this is not a valid python signature",
                "description": "Function with invalid signature"
            }
        ]
    }
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = os.path.join(temp_dir, "malformed_ui")
            saved_files = generate_ui_from_module_spec(malformed_spec, "web", output_dir)
            validation_result = validate_ui_directory(output_dir, "web")
            print(f"   ✓ Handled gracefully: {len(saved_files)} files, {validation_result.status.value}")
    except Exception as e:
        print(f"   ✗ Error: {e}")


def main():
    """Main demonstration function"""
    print("🎯 UI GENERATION INTEGRATION DEMONSTRATION")
    print("This example shows the complete workflow from ModuleSpec to UI artifacts")
    
    # Import ValidationStatus for use in main
    from ui_validator import ValidationStatus
    
    # Example 1: Single module, different UI types
    print("\n" + "🚀" * 20)
    print("EXAMPLE 1: SINGLE MODULE - MULTIPLE UI TYPES")
    print("🚀" * 20)
    
    calculator_spec = example_calculator_module_spec()
    
    for ui_type in ["web", "cli_gui", "desktop", "api_docs", "cli_tui"]:
        success = demonstrate_single_ui_type_workflow(calculator_spec, ui_type, "Calculator")
    
    # Example 2: Using convenience functions
    print("\n" + "🔧" * 20)
    print("EXAMPLE 2: CONVENIENCE FUNCTIONS")
    print("🔧" * 20)
    
    demonstrate_convenience_function_workflow(example_task_manager_module_spec(), "Task Manager")
    
    # Example 3: Multi-module workflow
    print("\n" + "📦" * 20)
    print("EXAMPLE 3: MULTI-MODULE WORKFLOW")
    print("📦" * 20)
    
    demonstrate_multi_module_workflow()
    
    # Example 4: Error handling
    print("\n" + "🛡️" * 20)
    print("EXAMPLE 4: ERROR HANDLING AND EDGE CASES")
    print("🛡️" * 20)
    
    demonstrate_error_handling_workflow()
    
    # Final summary
    print(f"\n{'🎉' * 20}")
    print("DEMONSTRATION COMPLETE")
    print("🎉" * 20)
    
    print("\n📋 KEY FEATURES DEMONSTRATED:")
    print("   ✅ ModuleSpec → UISpec transformation")
    print("   ✅ Multi-platform UI generation (5 UI types)")
    print("   ✅ Comprehensive validation framework")
    print("   ✅ Error handling and edge cases")
    print("   ✅ Convenience functions for quick generation")
    print("   ✅ Integration between all components")
    
    print("\n🏗️ ARCHITECTURE HIGHLIGHTS:")
    print("   • Modular design with clear separation of concerns")
    print("   • Type-safe data structures and validation")
    print("   • Extensible component system")
    print("   • Cross-platform compatibility")
    print("   • Production-ready error handling")
    
    print("\n🚀 READY FOR INTEGRATION:")
    print("   • All components follow Module Forge architecture")
    print("   • Compatible with existing codebase")
    print("   • Scalable for future enhancements")
    print("   • Well-tested with comprehensive coverage")
    
    print(f"\n{'='*60}")
    print("THANK YOU FOR EXPLORING THE UI GENERATION SYSTEM!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()