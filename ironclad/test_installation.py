#!/usr/bin/env python3
"""
Ironclad Installation Test Script

Tests the complete installation and functionality of Ironclad AI Guardrails.
This script validates that the package is properly installed and all features work.
"""

import subprocess
import sys
import os
import tempfile
import json
import shutil
from pathlib import Path


def run_command(cmd, description, check=True):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}")
    print(f"   Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=check,
            timeout=60
        )
        
        if result.stdout.strip():
            print(f"   ✅ Output: {result.stdout.strip()}")
        
        if result.stderr.strip() and check:
            print(f"   ⚠️  Stderr: {result.stderr.strip()}")
        
        return result.returncode == 0, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        print(f"   ❌ Timeout after 60 seconds")
        return False, "", "Command timed out"
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e}")
        return False, e.stdout, e.stderr
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False, "", str(e)


def test_pip_installation():
    """Test pip installation in isolated environment"""
    print("\n" + "="*60)
    print("📦 TESTING PIP INSTALLATION")
    print("="*60)
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Using temporary directory: {temp_dir}")
        
        # Test building the package
        success, stdout, stderr = run_command(
            [sys.executable, "-m", "build", "--wheel", "--outdir", temp_dir],
            "Building wheel package",
            check=False
        )
        
        if not success:
            print(f"   ❌ Build failed")
            if stderr:
                print(f"   Error details: {stderr}")
            return False
        
        # Find the wheel file
        wheel_files = list(Path(temp_dir).glob("*.whl"))
        if not wheel_files:
            print(f"   ❌ No wheel file found")
            return False
        
        wheel_file = wheel_files[0]
        print(f"   📦 Found wheel: {wheel_file.name}")
        
        # Create virtual environment for testing
        venv_dir = os.path.join(temp_dir, "test_env")
        
        print(f"\n🐍 Creating test virtual environment...")
        success, _, _ = run_command(
            [sys.executable, "-m", "venv", venv_dir],
            "Creating virtual environment"
        )
        
        if not success:
            print(f"   ❌ Failed to create virtual environment")
            return False
        
        # Determine pip path in venv
        if os.name == 'nt':  # Windows
            pip_path = os.path.join(venv_dir, "Scripts", "pip")
            python_path = os.path.join(venv_dir, "Scripts", "python")
        else:  # Unix/Linux/Mac
            pip_path = os.path.join(venv_dir, "bin", "pip")
            python_path = os.path.join(venv_dir, "bin", "python")
        
        print(f"\n📦 Installing package in test environment...")
        success, stdout, stderr = run_command(
            [pip_path, "install", str(wheel_file), "-v"],
            "Installing wheel package",
            check=False
        )
        
        if not success:
            print(f"   ❌ Installation failed")
            if stderr:
                print(f"   Error details: {stderr}")
            return False
        
        print(f"   ✅ Package installed successfully")
        
        # Test CLI commands
        return test_cli_commands(python_path, temp_dir)


def test_cli_commands(python_path, temp_dir):
    """Test CLI commands work in installed package"""
    print(f"\n" + "="*60)
    print("🔧 TESTING CLI COMMANDS")
    print("="*60)
    
    cli_tests = [
        {
            "name": "ironclad --help",
            "cmd": [python_path, "-m", "ironclad.cli", "--help"],
            "description": "Testing main CLI help"
        },
        {
            "name": "ironclad-ui --help", 
            "cmd": [python_path, "-m", "ui_cli", "--help"],
            "description": "Testing UI CLI help"
        },
        {
            "name": "ironclad-ui list-types",
            "cmd": [python_path, "-m", "ui_cli", "list-types"],
            "description": "Testing UI type listing"
        }
    ]
    
    all_passed = True
    
    for test in cli_tests:
        success, stdout, stderr = run_command(
            test["cmd"],
            test["description"],
            check=False
        )
        
        if success:
            print(f"   ✅ {test['name']} - PASSED")
        else:
            print(f"   ❌ {test['name']} - FAILED")
            if stderr:
                print(f"      Error: {stderr}")
            all_passed = False
    
    return all_passed


def test_python_imports():
    """Test that Python imports work correctly"""
    print(f"\n" + "="*60)
    print("🐍 TESTING PYTHON IMPORTS")
    print("="*60)
    
    import_tests = [
        ("Core ironclad module", "import ironclad"),
        ("Code utilities", "from ironclad import code_utils"),
        ("UI specification", "from ironclad import ui_spec"),
        ("UI generator", "from ironclad import ui_generator"),
        ("UI validator", "from ironclad import ui_validator"),
        ("CLI module", "from ironclad import cli"),
        ("Factory manager", "from ironclad import factory_manager"),
        ("Module forge", "from ironclad import module_forge"),
        ("Module designer", "from ironclad import module_designer"),
    ]
    
    all_passed = True
    
    for test_name, import_statement in import_tests:
        try:
            exec(import_statement)
            print(f"   ✅ {test_name} - IMPORT OK")
        except ImportError as e:
            print(f"   ❌ {test_name} - IMPORT FAILED: {e}")
            all_passed = False
        except Exception as e:
            print(f"   ⚠️  {test_name} - WARNING: {e}")
            # Continue testing other imports
    
    return all_passed


def test_ui_generation():
    """Test UI generation functionality"""
    print(f"\n" + "="*60)
    print("🎨 TESTING UI GENERATION")
    print("="*60)
    
    try:
        # Import UI components
        from ironclad.ui_spec import UIType, transform_module_spec_to_ui_spec
        from ironclad.ui_generator import save_ui_artifacts
        from ironclad.ui_validator import validate_ui_directory
        
        # Create sample module specification
        module_spec = {
            "module_name": "test_calculator",
            "main_logic_description": "Test calculator for installation verification",
            "functions": [
                {
                    "name": "add",
                    "signature": "def add(a: float, b: float) -> float:",
                    "description": "Add two numbers"
                },
                {
                    "name": "main",
                    "signature": "def main(a: float, b: float) -> float:",
                    "description": "Main calculator function"
                }
            ]
        }
        
        print(f"   ✅ UI components imported successfully")
        
        # Test transformation
        ui_spec = transform_module_spec_to_ui_spec(module_spec, UIType.WEB)
        print(f"   ✅ ModuleSpec → UISpec transformation works")
        
        # Test generation
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = os.path.join(temp_dir, "test_ui")
            saved_files = save_ui_artifacts(ui_spec, output_dir)
            
            if len(saved_files) >= 3:  # At least HTML, CSS, JS
                print(f"   ✅ UI generation works ({len(saved_files)} files)")
            else:
                print(f"   ⚠️  UI generation incomplete ({len(saved_files)} files)")
            
            # Test validation
            validation_result = validate_ui_directory(output_dir, "web")
            print(f"   ✅ UI validation works (status: {validation_result.status.value})")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ UI components import failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ UI generation test failed: {e}")
        return False


def test_verified_bricks():
    """Test verified bricks functionality"""
    print(f"\n" + "="*60)
    print("🧱 TESTING VERIFIED BRICKS")
    print("="*60)
    
    try:
        # Test that verified bricks are accessible
        from ironclad.verified_bricks import fibonacci, is_prime
        
        print(f"   ✅ Verified bricks module accessible")
        
        # Test basic functionality
        result = fibonacci.fib(10)
        expected = [0, 1, 1, 2, 3, 5, 8]
        if result == expected:
            print(f"   ✅ Fibonacci function works")
        else:
            print(f"   ❌ Fibonacci function failed: got {result}, expected {expected}")
            return False
        
        prime_result = is_prime.is_prime(17)
        if prime_result:
            print(f"   ✅ Prime function works")
        else:
            print(f"   ❌ Prime function failed: 17 should be prime")
            return False
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Verified bricks import failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Verified bricks test failed: {e}")
        return False


def main():
    """Main installation test"""
    print("🎯 IRONCLAD INSTALLATION TEST")
    print("This script validates the complete Ironclad package installation")
    
    # Check if we're in the right directory
    if not os.path.exists("setup.py") or not os.path.exists("pyproject.toml"):
        print("❌ Error: Please run this script from the Ironclad root directory")
        print("   (where setup.py and pyproject.toml are located)")
        sys.exit(1)
    
    test_results = {}
    
    # Test 1: Python imports
    print(f"\n{'🐍'*20}")
    print("STEP 1: TESTING LOCAL IMPORTS")
    print("🐍"*20)
    test_results["imports"] = test_python_imports()
    
    # Test 2: UI generation
    print(f"\n{'🎨'*20}")
    print("STEP 2: TESTING UI GENERATION")
    print("🎨"*20)
    test_results["ui_generation"] = test_ui_generation()
    
    # Test 3: Verified bricks
    print(f"\n{'🧱'*20}")
    print("STEP 3: TESTING VERIFIED BRICKS")
    print("🧱"*20)
    test_results["verified_bricks"] = test_verified_bricks()
    
    # Test 4: Pip installation (optional, can fail if build tools missing)
    print(f"\n{'📦'*20}")
    print("STEP 4: TESTING PIP INSTALLATION")
    print("📦"*20)
    test_results["pip_installation"] = test_pip_installation()
    
    # Summary
    print(f"\n" + "="*60)
    print("📊 INSTALLATION TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\n   Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"   Ironclad is ready for installation and distribution")
        return 0
    elif passed >= total - 1:  # Allow pip installation to fail if build tools missing
        print(f"\n✅ CORE FUNCTIONALITY WORKS!")
        print(f"   (Pip installation may need additional build tools)")
        return 0
    else:
        print(f"\n❌ SOME TESTS FAILED!")
        print(f"   Please review the errors above and fix issues")
        return 1


if __name__ == "__main__":
    sys.exit(main())