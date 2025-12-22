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
import argparse
from module_designer import draft_blueprint
import factory_manager


def main():
    """
    Main entry point for end-to-end module generation
    """
    parser = argparse.ArgumentParser(
        description="End-to-end module generation from user request to working module",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python module_forge.py 'I need a CLI tool that adds two numbers'
  python module_forge.py --resume 'I need a CLI tool that adds two numbers'
        """
    )
    
    parser.add_argument('request', help='User request describing the module to build')
    parser.add_argument('--resume', action='store_true', 
                       help='Continue from existing progress, keeping successful components')
    
    args = parser.parse_args()
    
    user_request = args.request
    resume_mode = "resume" if args.resume else "smart"
    
    print("=" * 60)
    print("🔨 MODULE FORGE - End-to-End Module Generation")
    if resume_mode == "resume":
        print("🔄 RESUME MODE - Continuing from existing progress")
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
    partial_success, module_dir, successful_components, failed_components, status_report = factory_manager.build_components(blueprint, resume_mode)
    
    if not partial_success or not successful_components:
        print("[❌] No components could be built successfully. Aborting.")
        sys.exit(1)
    
    print(f"[✅] Components built: {len(successful_components)}/{len(blueprint['functions'])} successful")
    if successful_components:
        print(f"    ✅ {successful_components}")
    if failed_components:
        print(f"    ❌ {failed_components}")
    print(f"    Module directory: {module_dir}")
    
    # Step 3: Assemble Module
    print("\n[3/3] 🔧 Assembling final module...")
    try:
        factory_manager.assemble_main(blueprint, module_dir, successful_components)
        print(f"[✅] Module assembled successfully!")
        print(f"    📁 Location: {module_dir}")
        print(f"    🚀 Run: cd {module_dir} && python main.py")
    except Exception as e:
        print(f"[❌] Failed to assemble module: {e}")
        sys.exit(1)
    
    # Final status report
    print("\n" + "=" * 60)
    if failed_components:
        print(f"🎉 MODULE FORGE COMPLETE - Module ready with {len(failed_components)} components skipped")
        print(f"   ⚠️  Skipped components: {', '.join(failed_components)}")
    else:
        print("🎉 MODULE FORGE COMPLETE - Your module is fully ready!")
    print("=" * 60)


if __name__ == "__main__":
    main()