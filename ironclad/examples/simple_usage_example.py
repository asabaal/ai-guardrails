#!/usr/bin/env python3
"""
Simple Usage Example

Quick demonstration of how to use the UI generation system
with minimal setup and clear explanations.
"""

import os
import sys

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import the main components
from ui_spec import UIType, transform_module_spec_to_ui_spec
from ui_generator import save_ui_artifacts
from ui_validator import validate_ui_directory, print_validation_report


def simple_calculator_spec():
    """Simple calculator module specification"""
    return {
        "module_name": "simple_calculator",
        "main_logic_description": "Basic calculator with add and subtract operations",
        "functions": [
            {
                "name": "add",
                "signature": "def add(a: float, b: float) -> float:",
                "description": "Add two numbers"
            },
            {
                "name": "subtract",
                "signature": "def subtract(a: float, b: float) -> float:",
                "description": "Subtract b from a"
            },
            {
                "name": "main",
                "signature": "def main(operation: str, a: float, b: float) -> float:",
                "description": "Main calculator function"
            }
        ]
    }


def main():
    """Simple usage demonstration"""
    
    print("🎯 SIMPLE UI GENERATION EXAMPLE")
    print("=" * 50)
    
    # Step 1: Define your module specification
    print("\n📝 Step 1: Module Specification")
    module_spec = simple_calculator_spec()
    print(f"   Module: {module_spec['module_name']}")
    print(f"   Functions: {len(module_spec['functions'])}")
    
    # Step 2: Transform to UI specification
    print("\n🔄 Step 2: Transform to UI Specification")
    ui_spec = transform_module_spec_to_ui_spec(module_spec, UIType.WEB)
    print(f"   UI Title: {ui_spec.title}")
    print(f"   Components: {len(ui_spec.components)}")
    print(f"   Layout: {ui_spec.layout.type}")
    
    # Step 3: Generate UI files
    print("\n🎨 Step 3: Generate UI Files")
    output_dir = "generated_ui"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save UI artifacts
    saved_files = save_ui_artifacts(ui_spec, output_dir)
    print(f"   Generated {len(saved_files)} files:")
    for file_path in saved_files.keys():
        filename = os.path.basename(file_path)
        print(f"     - {filename}")
    
    # Step 4: Validate the generated UI
    print("\n🔍 Step 4: Validate Generated UI")
    validation_result = validate_ui_directory(output_dir, "web")
    print(f"   Status: {validation_result.status.value}")
    print(f"   Issues: {len(validation_result.issues)}")
    print(f"   Time: {validation_result.execution_time:.2f}s")
    
    # Print detailed validation report
    print("\n📊 Detailed Validation Report:")
    print_validation_report(validation_result)
    
    # Show next steps
    print("\n🚀 Next Steps:")
    if validation_result.status.value in ["passed", "warning"]:
        print("   ✅ UI generation successful!")
        print(f"   📁 Check the '{output_dir}' directory")
        print("   🌐 Open index.html in a web browser")
        print("   🔧 Customize the generated files as needed")
    else:
        print("   ⚠️  Some issues were found")
        print("   🔧 Review the validation report above")
        print("   🔄 Fix issues and regenerate if needed")
    
    print("\n💡 Advanced Usage:")
    print("   • Try different UI types: 'cli_gui', 'desktop', 'api_docs', 'cli_tui'")
    print("   • Add custom styling and validation rules")
    print("   • Extend with custom component types")
    print("   • Integrate with your existing Module Forge workflow")


if __name__ == "__main__":
    main()