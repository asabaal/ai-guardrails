"""
Quick integration test runner.

Usage:
    export Z_AI_API_KEY=your_actual_key
    python tests/integration/run_tests.py
"""

import sys
import os
import subprocess
from pathlib import Path


def check_api_key():
    """Check if API key is set."""
    api_key = os.environ.get('Z_AI_API_KEY')
    if not api_key or api_key in ['your_api_key_here', 'test123', '']:
        print("ERROR: Z_AI_API_KEY not set or is a placeholder")
        print("\nPlease set your API key:")
        print("  export Z_AI_API_KEY=your_actual_key")
        sys.exit(1)
    
    print(f"API Key is set (length: {len(api_key)})")
    return True


def run_test_spec(spec_path: str, test_name: str):
    """Run a single test spec."""
    print(f"\n{'='*70}")
    print(f"Running test: {test_name}")
    print(f"Spec: {spec_path}")
    print('='*70)
    
    result = subprocess.run(
        ['brick', 'run', spec_path],
        capture_output=True,
        text=True,
        timeout=300
    )
    
    if result.returncode == 0:
        print(f"✅ {test_name} PASSED")
    else:
        print(f"❌ {test_name} FAILED")
        print("\nSTDOUT:")
        print(result.stdout)
        print("\nSTDERR:")
        print(result.stderr)
    
    return result.returncode == 0


def main():
    """Main test runner."""
    print("Brick Commissioner Integration Tests")
    print("="*70)
    
    if not check_api_key():
        return
    
    specs_dir = Path(__file__).parent / "specs"
    
    test_specs = [
        (str(specs_dir / "simple_math.json"), "Simple Math"),
        (str(specs_dir / "string_utils.json"), "String Utils"),
        (str(specs_dir / "string_calculator.json"), "String Calculator"),
    ]
    
    results = []
    
    for spec_path, test_name in test_specs:
        if Path(spec_path).exists():
            passed = run_test_spec(spec_path, test_name)
            results.append((test_name, passed))
        else:
            print(f"⚠️  Spec file not found: {spec_path}")
            results.append((test_name, False))
    
    print(f"\n{'='*70}")
    print("SUMMARY")
    print('='*70)
    
    passed = sum(1 for _, is_passed in results if is_passed)
    total = len(results)
    
    for test_name, is_passed in results:
        status = "✅ PASSED" if is_passed else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All integration tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
