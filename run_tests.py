#!/usr/bin/env python3
"""
Comprehensive Test Runner for AI Guardrails System
DMT Protocol: Done Means Taught - Complete test execution and reporting
"""
import sys
import os
import subprocess
import time
from pathlib import Path

def run_command(cmd, description):
    """Run command and return success status"""
    print(f"\n🔧 {description}...")
    print(f"   Command: {' '.join(cmd)}")
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
    end_time = time.time()
    
    duration = end_time - start_time
    success = result.returncode == 0
    
    print(f"   Duration: {duration:.2f}s")
    print(f"   Status: {'✅ PASS' if success else '❌ FAIL'}")
    
    if not success:
        print(f"   Error: {result.stderr}")
    
    return success, duration, result.stdout, result.stderr

def main():
    """Run complete test suite with coverage reporting"""
    print("🚀 AI Guardrails - Complete Test Suite")
    print("=" * 60)
    print("DMT Protocol: Done Means Taught")
    print("=" * 60)
    
    results = []
    
    # 1. Unit Tests
    success, duration, _, _ = run_command(
        [sys.executable, "-m", "pytest", "tests/test_parser.py", "-v"],
        "Parser Unit Tests"
    )
    results.append(("Parser Unit Tests", success, duration))
    
    success, duration, _, _ = run_command(
        [sys.executable, "-m", "pytest", "tests/test_reasoner.py", "-v"],
        "Reasoner Unit Tests"
    )
    results.append(("Reasoner Unit Tests", success, duration))
    
    # 2. Integration Tests
    success, duration, _, _ = run_command(
        [sys.executable, "-m", "pytest", "tests/integration_tests.py", "-v"],
        "Integration Tests"
    )
    results.append(("Integration Tests", success, duration))
    
    # 3. CLI Validation
    success, duration, _, _ = run_command(
        [sys.executable, "tools/validate.py"],
        "CLI Validation Tools"
    )
    results.append(("CLI Validation Tools", success, duration))
    
    # 4. Code Quality Checks
    success, duration, _, _ = run_command(
        [sys.executable, "-m", "pytest", "tests/", "--cov=core_logic", "--cov-report=term-missing"],
        "Test Coverage Analysis"
    )
    results.append(("Test Coverage", success, duration))
    
    # Summary Report
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 60)
    
    total_duration = 0
    all_passed = True
    
    for test_name, success, duration in results:
        total_duration += duration
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:25} : {status} ({duration:.2f}s)")
        if not success:
            all_passed = False
    
    print("-" * 60)
    print(f"{'Total Duration':25} : {total_duration:.2f}s")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ System meets DMT Protocol requirements")
        print("✅ Ready for development and deployment")
    else:
        print("⚠️  SOME TESTS FAILED!")
        print("❌ Review failures before proceeding")
        print("❌ System does not meet DMT Protocol requirements")
    
    print("=" * 60)
    
    # Additional validation
    print("\n🔍 Additional System Validation...")
    
    # Check if core files exist
    core_files = [
        "core_logic/parser.py",
        "core_logic/reasoner.py", 
        "app.py",
        "tools/validate.py"
    ]
    
    missing_files = []
    for file_path in core_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing core files: {missing_files}")
        all_passed = False
    else:
        print("✅ All core files present")
    
    # Check if test files exist
    test_files = [
        "tests/test_parser.py",
        "tests/test_reasoner.py",
        "tests/integration_tests.py"
    ]
    
    missing_tests = []
    for file_path in test_files:
        if not Path(file_path).exists():
            missing_tests.append(file_path)
    
    if missing_tests:
        print(f"❌ Missing test files: {missing_tests}")
        all_passed = False
    else:
        print("✅ All test files present")
    
    print("\n" + "=" * 60)
    print("🏁 FINAL VALIDATION STATUS")
    print("=" * 60)
    
    if all_passed:
        print("🌟 SYSTEM FULLY VALIDATED")
        print("📋 DMT Protocol Compliance: 100%")
        print("🚀 Ready for next development phase")
    else:
        print("⚠️  SYSTEM VALIDATION INCOMPLETE")
        print("📋 DMT Protocol Compliance: FAILED")
        print("🔧 Address issues before proceeding")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())