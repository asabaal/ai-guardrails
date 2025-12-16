#!/usr/bin/env python3
"""
Module Forge - End-to-end module generation integration layer

This module orchestrates the complete workflow from user request to finished module:
1. Designs blueprint using module_designer
2. Builds components using factory_manager  
3. Assembles final module using factory_manager
"""
import sys
import json
import os
from module_designer import draft_blueprint
import factory_manager


def main():
    """
    Main entry point for end-to-end module generation
    """
    if len(sys.argv) < 2:
        print("Usage: python module_forge.py 'I need a tool that...'")
        print("Example: python module_forge.py 'I need a CLI tool that processes stock data'")
        sys.exit(1)
    
    user_request = sys.argv[1]
    
    print("=" * 60)
    print("🔨 MODULE FORGE - End-to-End Module Generation")
    print("=" * 60)
    
    # Step 1: Design Blueprint
    print("\n[1/3] 📐 Designing module blueprint...")
    blueprint = draft_blueprint(user_request)
    
    if not blueprint:
        print("[❌] Failed to generate blueprint. Aborting.")
        sys.exit(1)
    
    print(f"[✅] Blueprint designed: {blueprint['module_name']}")
    print(f"    Functions: {[f['name'] for f in blueprint['functions']]}")
    
    # Save blueprint for factory manager
    blueprint_file = "blueprint.json"
    with open(blueprint_file, "w") as f:
        json.dump(blueprint, f, indent=4)
    print(f"[💾] Blueprint saved to: {blueprint_file}")
    
    # Step 2: Build Components
    print("\n[2/3] 🏗️  Building components...")
    success, module_dir, components = factory_manager.build_components(blueprint)
    
    if not success:
        print("[❌] Failed to build components. Aborting.")
        sys.exit(1)
    
    print(f"[✅] Components built: {components}")
    print(f"    Module directory: {module_dir}")
    
    # Step 3: Assemble Module
    print("\n[3/3] 🔧 Assembling final module...")
    try:
        factory_manager.assemble_main(blueprint, module_dir, components)
        print(f"[✅] Module assembled successfully!")
        print(f"    📁 Location: {module_dir}")
        print(f"    🚀 Run: cd {module_dir} && python main.py")
    except Exception as e:
        print(f"[❌] Failed to assemble module: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 MODULE FORGE COMPLETE - Your module is ready!")
    print("=" * 60)


if __name__ == "__main__":
    main()