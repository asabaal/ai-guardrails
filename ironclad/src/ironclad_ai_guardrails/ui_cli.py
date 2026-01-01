#!/usr/bin/env python3
"""
UI Generator CLI - Command line interface for UI generation
"""

import argparse
import sys
import json
import os
from pathlib import Path

# Import UI generation components
from ironclad_ai_guardrails.ui_spec import UIType, transform_module_spec_to_ui_spec
from ironclad_ai_guardrails.ui_generator import save_ui_artifacts
from ironclad_ai_guardrails.ui_validator import validate_ui_directory, print_validation_report


def load_module_spec(spec_file):
    """Load module specification from JSON file"""
    try:
        with open(spec_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Module specification file '{spec_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in '{spec_file}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading '{spec_file}': {e}")
        sys.exit(1)


def validate_ui_type(ui_type):
    """Validate and normalize UI type"""
    valid_types = [t.value for t in UIType]
    
    if ui_type.lower() not in valid_types:
        print(f"❌ Error: Invalid UI type '{ui_type}'")
        print(f"Valid types: {', '.join(valid_types)}")
        sys.exit(1)
    
    return UIType(ui_type.lower())


def create_sample_module_spec():
    """Create a sample module specification for demonstration"""
    return {
        "module_name": "example_calculator",
        "main_logic_description": "A simple calculator with basic arithmetic operations",
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
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="ironclad-ui",
        description="Generate user interfaces from module specifications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate web UI from module specification
  ironclad-ui generate --spec module.json --type web --output ./ui
  
  # Generate all UI types
  ironclad-ui generate --spec module.json --type all --output ./ui_all
  
  # Validate existing UI
  ironclad-ui validate --ui-type web --ui-dir ./web_ui
  
  # Create sample specification
  ironclad-ui create-sample --output sample_module.json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate UI from module specification')
    generate_parser.add_argument('--spec', '-s', required=True,
                             help='Path to module specification JSON file')
    generate_parser.add_argument('--type', '-t', required=True,
                             choices=[t.value for t in UIType] + ['all'],
                             help='UI type to generate (or "all" for all types)')
    generate_parser.add_argument('--output', '-o', required=True,
                             help='Output directory for generated UI files')
    generate_parser.add_argument('--validate', '-v', action='store_true',
                             help='Validate generated UI after creation')
    generate_parser.add_argument('--title', help='Custom UI title (overrides default)')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate generated UI files')
    validate_parser.add_argument('--ui-dir', '-d', required=True,
                              help='Directory containing UI files to validate')
    validate_parser.add_argument('--ui-type', '-t', required=True,
                              choices=[t.value for t in UIType],
                              help='Type of UI to validate')
    
    # Create sample command
    sample_parser = subparsers.add_parser('create-sample', help='Create sample module specification')
    sample_parser.add_argument('--output', '-o', required=True,
                            help='Output path for sample specification file')
    
    # List types command
    list_parser = subparsers.add_parser('list-types', help='List available UI types')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Handle commands
    if args.command == 'generate':
        handle_generate(args)
    elif args.command == 'validate':
        handle_validate(args)
    elif args.command == 'create-sample':
        handle_create_sample(args)
    elif args.command == 'list-types':
        handle_list_types()


def handle_generate(args):
    """Handle generate command"""
    print(f"🎨 Generating UI from specification: {args.spec}")
    
    # Load module specification
    module_spec = load_module_spec(args.spec)
    
    # Handle UI types
    ui_types = [args.type]
    if args.type.lower() == 'all':
        ui_types = [t.value for t in UIType]
        print(f"📦 Generating all UI types: {', '.join(ui_types)}")
    else:
        print(f"🎯 UI type: {args.type}")
    
    # Generate UI(s)
    all_success = True
    for ui_type in ui_types:
        try:
            print(f"\n🔄 Generating {ui_type.upper()} UI...")
            
            # Validate UI type
            ui_type_enum = validate_ui_type(ui_type)
            
            # Transform specification
            ui_spec = transform_module_spec_to_ui_spec(
                module_spec, 
                ui_type_enum, 
                ui_title=args.title
            )
            
            # Determine output directory
            if len(ui_types) > 1:
                output_dir = os.path.join(args.output, f"{ui_type}_ui")
            else:
                output_dir = args.output
            
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate UI artifacts
            saved_files = save_ui_artifacts(ui_spec, output_dir)
            print(f"   ✅ Generated {len(saved_files)} files in {output_dir}")
            
            # Validate if requested
            if args.validate:
                print(f"   🔍 Validating {ui_type} UI...")
                validation_result = validate_ui_directory(output_dir, ui_type)
                print(f"   📊 Status: {validation_result.status.value}")
                if validation_result.issues:
                    print(f"   ⚠️  Found {len(validation_result.issues)} issues")
            
        except Exception as e:
            print(f"   ❌ Error generating {ui_type} UI: {e}")
            all_success = False
    
    if all_success:
        print(f"\n🎉 UI generation completed successfully!")
        if len(ui_types) > 1:
            print(f"📁 Check output directory: {args.output}")
    else:
        print(f"\n❌ Some UI types failed to generate.")
        sys.exit(1)


def handle_validate(args):
    """Handle validate command"""
    print(f"🔍 Validating UI in directory: {args.ui_dir}")
    print(f"🎯 UI type: {args.ui_type}")
    
    if not os.path.exists(args.ui_dir):
        print(f"❌ Error: Directory '{args.ui_dir}' does not exist.")
        sys.exit(1)
    
    try:
        validation_result = validate_ui_directory(args.ui_dir, args.ui_type)
        
        print(f"\n📊 VALIDATION RESULTS")
        print(f"   Status: {validation_result.status.value}")
        print(f"   Issues: {len(validation_result.issues)}")
        print(f"   Time: {validation_result.execution_time:.2f}s")
        
        if validation_result.issues:
            print(f"\n🔍 DETAILED REPORT")
            print_validation_report(validation_result)
        
        # Exit with appropriate code
        if validation_result.status.value == 'failed':
            sys.exit(1)
        elif validation_result.status.value == 'warning':
            sys.exit(2)
        else:
            print(f"\n✅ Validation passed!")
            
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        sys.exit(1)


def handle_create_sample(args):
    """Handle create-sample command"""
    print(f"📝 Creating sample module specification: {args.output}")
    
    try:
        sample_spec = create_sample_module_spec()
        
        # Create output directory if needed
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write sample specification
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(sample_spec, f, indent=2)
        
        print(f"✅ Sample specification created: {args.output}")
        print(f"💡 You can now use: ironclad-ui generate --spec {args.output} --type web --output ./ui")
        
    except Exception as e:
        print(f"❌ Error creating sample: {e}")
        sys.exit(1)


def handle_list_types():
    """Handle list-types command"""
    print("📋 Available UI Types:")
    print("-" * 30)
    
    for ui_type in UIType:
        description = {
            UIType.WEB: "Modern web interface with HTML/CSS/JS",
            UIType.CLI_GUI: "Desktop GUI using Tkinter",
            UIType.DESKTOP: "Electron desktop application",
            UIType.API_DOCS: "OpenAPI/Swagger documentation",
            UIType.CLI_TUI: "Terminal UI using Rich/Textual"
        }.get(ui_type, "Unknown")
        
        print(f"  {ui_type.value:<12} - {description}")
    
    print(f"\n💡 Use 'all' to generate all UI types")


if __name__ == '__main__':
    main()