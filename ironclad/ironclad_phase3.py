import os
import sys
import json
import subprocess
import tempfile
import re
import time
import shutil
import ollama

# --- CONFIGURATION ---
MODEL_NAME = "gpt-oss:20b"
OUTPUT_BASE_DIR = "verified_bricks"
MAX_RETRIES = 3
MAX_ATTEMPTS = 10  # Safety limit for dynamic retry logic

# --- PROMPTS ---
SYSTEM_PROMPT = """
You are a strict code generator. You output JSON only.
Your goal is to write a Python function and a corresponding Pytest unit test.
CRITICAL: Your tests MUST cover 100% of the function code.

Output format must be exactly this JSON structure:
{
    "filename": "function_name",
    "code": "def function_name... ",
    "test": "import pytest\\nfrom function_name import function_name\\n\\ndef test_case_1()..."
}
"""

REPAIR_PROMPT_TEMPLATE = """
Your previous attempt failed validation.
Failure Reason:
{error_log}

Test Results Summary:
{test_summary}

Coverage Analysis:
{coverage_analysis}

Here is the code you wrote:
{code}

Fix the code and/or tests to solve the error and ensure 100% coverage.
Do not output explanation. Output only the fixed JSON structure.
"""

def clean_json_response(response_text):
    cleaned = response_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(json)?", "", cleaned)
        cleaned = re.sub(r"```$", "", cleaned)
    return cleaned.strip()

def generate_candidate(request):
    print(f"[*] Generating candidate for: '{request}'...")
    user_message = f"Write a Python function that: {request}. Include comprehensive tests."
    start_time = time.time()
    try:
        response = ollama.chat(model=MODEL_NAME, messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': user_message},
        ])
        data = json.loads(clean_json_response(response['message']['content']))
        data['gen_time'] = time.time() - start_time
        return data
    except Exception as e:
        print(f"[!] Generation Error: {e}")
        return None

def repair_candidate(candidate, error_log, test_summary=None, coverage_analysis=None):
    print(f"[*] Attempting repair (Target: Fix Logic/Coverage)...")
    
    # Format test summary for the prompt
    test_summary_text = ""
    if test_summary:
        test_summary_text = f"Total Tests: {test_summary['total_tests']}, Passed: {test_summary['passed_tests']}, Failed: {test_summary['failed_tests']}, Pass Rate: {test_summary['pass_rate']:.1f}%\n"
        for test in test_summary['test_results']:
            if test['status'] != 'PASSED':
                test_summary_text += f"- {test['name']}: {test['status']}"
                if test['error']:
                    test_summary_text += f" | Error: {test['error']}"
                test_summary_text += "\n"
    
    # Format coverage analysis for the prompt
    coverage_text = ""
    if coverage_analysis:
        coverage_text = f"Current Coverage: {coverage_analysis['percent_covered']:.1f}%\n"
        if coverage_analysis.get('missing_lines'):
            coverage_text += f"Missing lines: {coverage_analysis['missing_lines']}\n"
    
    prompt_content = REPAIR_PROMPT_TEMPLATE.format(
        error_log=error_log,
        test_summary=test_summary_text or "No test results available",
        coverage_analysis=coverage_text or "No coverage analysis available",
        code=candidate.get("code", "")
    )
    
    try:
        response = ollama.chat(model=MODEL_NAME, messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': prompt_content},
        ])
        data = json.loads(clean_json_response(response['message']['content']))
        return data
    except Exception as e:
        print(f"[!] Repair Error: {e}")
        return None

def parse_test_results(test_output):
    """
    Parse pytest output to extract test results and error details.
    """
    lines = test_output.split('\n')
    test_results = []
    current_test = None
    
    for line in lines:
        line = line.strip()
        
        # Test result lines - more precise pattern matching
        # Look for lines that start with test path and end with status
        if '::test_' in line:
            # Check if this is an actual test result line
            # Valid patterns: "path/to/test.py::test_name PASSED" etc.
            if line.endswith(' PASSED') or line.endswith(' FAILED') or line.endswith(' ERROR'):
                parts = line.rsplit(' ', 1)  # Split on last space only
                if len(parts) == 2:
                    test_name = parts[0]
                    status = parts[1]
                    test_results.append({'name': test_name, 'status': status, 'error': None})
                    current_test = len(test_results) - 1
        
        # Error details - look for actual error lines
        elif line.startswith('E       ') and current_test is not None:
            error_msg = line[8:].strip()  # Remove 'E       ' prefix
            if test_results and current_test < len(test_results):
                test_results[current_test]['error'] = error_msg
    
    # Calculate pass rate
    total_tests = len(test_results)
    passed_tests = sum(1 for t in test_results if t['status'] == 'PASSED')
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    return {
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'failed_tests': total_tests - passed_tests,
        'pass_rate': pass_rate,
        'test_results': test_results
    }

def validate_candidate(candidate):
    """
    Runs pytest WITH coverage enforcement and detailed test reporting.
    """
    if not candidate or "code" not in candidate:
        return False, "Invalid JSON structure", 0, {}, {}

    function_name = candidate.get("filename", "unknown_func")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        code_path = os.path.join(temp_dir, f"{function_name}.py")
        test_path = os.path.join(temp_dir, f"test_{function_name}.py")
        
        with open(code_path, "w") as f:
            f.write(candidate['code'])
        
        # Inject path so pytest finds the module
        import_fix = "import sys\nimport os\nsys.path.append(os.getcwd())\n"
        with open(test_path, "w") as f:
            f.write(import_fix + candidate['test'])
            
        print(f"[*] Running Sandbox Tests & Coverage Check...")
        
        # COMMAND: Run pytest + pytest-cov, output report to json
        cmd = [
            sys.executable, "-m", "pytest", 
            test_path, 
            f"--cov={function_name}", 
            "--cov-report=json:coverage.json",
            "-v"  # Verbose output for better parsing
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, cwd=temp_dir
        )
        
        # Parse test results
        test_summary = parse_test_results(result.stdout + result.stderr)
        
        # 1. Check if Tests Passed
        if result.returncode != 0:
            return False, f"TESTS FAILED:\n{result.stdout}", 0, test_summary, {}

        # 2. Check Coverage
        cov_file = os.path.join(temp_dir, "coverage.json")
        if not os.path.exists(cov_file):
            return False, "CRITICAL: Coverage report not generated.", 0, test_summary, {}
            
        with open(cov_file, 'r') as cf:
            cov_data = json.load(cf)
            # pytest-cov json structure: totals -> percent_covered
            # Use strict floating point comparison
            coverage_percent = cov_data.get("totals", {}).get("percent_covered", 0)
        
        # Extract coverage details for analysis
        coverage_analysis = {
            'percent_covered': coverage_percent,
            'missing_lines': cov_data.get('files', {}).get(function_name, {}).get('missing_lines', []),
            'summary': cov_data.get('totals', {})
        }
        
        if coverage_percent < 100.0:
            return False, f"COVERAGE FAILURE: Only {coverage_percent}% covered. Missing branches/lines.", coverage_percent, test_summary, coverage_analysis

        return True, "All Checks Passed", coverage_percent, test_summary, coverage_analysis

def save_brick(candidate, report):
    """
    Creates a structured folder for the verified brick.
    """
    name = candidate['filename']
    brick_dir = os.path.join(OUTPUT_BASE_DIR, name)
    
    # Wipe old version if exists
    if os.path.exists(brick_dir):
        shutil.rmtree(brick_dir)
    os.makedirs(brick_dir)
    
    # Save Code
    with open(os.path.join(brick_dir, f"{name}.py"), "w") as f:
        f.write(candidate['code'])
    
    # Save Tests
    with open(os.path.join(brick_dir, f"test_{name}.py"), "w") as f:
        f.write(candidate['test'])
        
    # Save Metadata Report
    with open(os.path.join(brick_dir, "report.json"), "w") as f:
        json.dump(report, f, indent=4)
        
    print(f"[SUCCESS] Brick stored at: {brick_dir}/")
    print(f"          Stats: {report['attempts']} attempts | {report['coverage']}% coverage")

def main():
    if len(sys.argv) < 2:
        print("Usage: python ironclad_phase3.py 'request'")
        sys.exit(1)

    request = sys.argv[1]
    start_total = time.time()
    
    # 1. Initial Generation
    candidate = generate_candidate(request)
    if not candidate:
        sys.exit(1)

    attempts = 1
    is_valid = False
    logs = ""
    final_coverage = 0
    attempt_history = []
    no_improvement_count = 0
    prev_pass_rate = 0
    prev_coverage = 0

    # 2. Validation & Repair Loop with Dynamic Retry Logic
    while attempts <= MAX_ATTEMPTS:
        is_valid, logs, final_coverage, test_summary, coverage_analysis = validate_candidate(candidate)
        
        # Record attempt data
        current_pass_rate = test_summary.get('pass_rate', 0)
        attempt_data = {
            'attempt': attempts,
            'coverage': final_coverage,
            'pass_rate': current_pass_rate,
            'tests_passed': test_summary.get('passed_tests', 0),
            'tests_total': test_summary.get('total_tests', 0),
            'status': 'PASS' if is_valid else 'FAIL',
            'error_type': 'None' if is_valid else ('Test Failure' if test_summary.get('failed_tests', 0) > 0 else 'Coverage Failure')
        }
        attempt_history.append(attempt_data)
        
        # Display attempt summary
        status_icon = "✓" if is_valid else "✗"
        print(f"[{status_icon}] Attempt {attempts}: Coverage {final_coverage}% | Pass Rate {current_pass_rate:.1f}% | Tests {test_summary.get('passed_tests', 0)}/{test_summary.get('total_tests', 0)}")
        
        if is_valid:
            break
            
        # Check for improvement (pass rate OR coverage)
        coverage_improved = final_coverage > prev_coverage
        pass_rate_improved = current_pass_rate > prev_pass_rate
        
        if coverage_improved or pass_rate_improved:
            improvement_type = []
            if coverage_improved:
                improvement_type.append(f"coverage +{final_coverage - prev_coverage}%")
            if pass_rate_improved:
                improvement_type.append(f"pass rate +{current_pass_rate - prev_pass_rate:.1f}%")
            print(f"    ↑ Improvement detected: {', '.join(improvement_type)}")
            no_improvement_count = 0
        else:
            no_improvement_count += 1
            print(f"    → No improvement ({no_improvement_count}/2 consecutive attempts)")
            
        # Stop conditions
        if no_improvement_count >= 2:
            print(f"    ⚠ Stopping: No improvement for 2 consecutive attempts")
            break
            
        if attempts >= MAX_ATTEMPTS:
            print(f"    ⚠ Stopping: Maximum attempts ({MAX_ATTEMPTS}) reached")
            break
            
        prev_pass_rate = current_pass_rate
        prev_coverage = final_coverage
            
        print(f"[-] FAIL (Attempt {attempts}). Triggering repair...")
        candidate = repair_candidate(candidate, logs, test_summary, coverage_analysis)
        if not candidate:
            print("[!] Repair produced invalid JSON. Aborting.")
            sys.exit(1)
        attempts += 1

    # 3. Final Report Data
    report = {
        "function_name": candidate.get("filename"),
        "status": "verified" if is_valid else "rejected",
        "attempts": attempts,
        "coverage": final_coverage,
        "total_time_sec": round(time.time() - start_total, 2),
        "failure_log": logs if not is_valid else None,
        "attempt_history": attempt_history
    }

    # Display attempt summary table
    print("\n" + "="*60)
    print("ATTEMPT SUMMARY")
    print("="*60)
    print(f"{'Attempt':<8} {'Coverage':<10} {'Pass Rate':<10} {'Tests':<12} {'Status':<8} {'Error Type'}")
    print("-"*60)
    for attempt in attempt_history:
        tests_str = f"{attempt['tests_passed']}/{attempt['tests_total']}"
        print(f"{attempt['attempt']:<8} {attempt['coverage']:<10}% {attempt['pass_rate']:<10.1f}% {tests_str:<12} {attempt['status']:<8} {attempt['error_type']}")
    
    # Show improvement trends
    if len(attempt_history) > 1:
        print("-"*60)
        first_cov = attempt_history[0]['coverage']
        last_cov = attempt_history[-1]['coverage']
        first_pass = attempt_history[0]['pass_rate']
        last_pass = attempt_history[-1]['pass_rate']
        
        cov_trend = "↑" if last_cov > first_cov else "→" if last_cov == first_cov else "↓"
        pass_trend = "↑" if last_pass > first_pass else "→" if last_pass == first_pass else "↓"
        
        print(f"Trends: Coverage {cov_trend} {first_cov}%→{last_cov}% | Pass Rate {pass_trend} {first_pass:.1f}%→{last_pass:.1f}%")
        
        # Decision rationale
        if not is_valid:
            if no_improvement_count >= 2:
                print(f"Stop Reason: No improvement for 2 consecutive attempts")
            elif attempts >= MAX_ATTEMPTS:
                print(f"Stop Reason: Maximum attempts ({MAX_ATTEMPTS}) reached")
    
    print("="*60)

    if is_valid:
        save_brick(candidate, report)
        print(f"\n[SUCCESS] Function verified and saved!")
        print(f"          Final Stats: {attempts} attempts | {final_coverage}% coverage | {attempt_history[-1]['pass_rate']:.1f}% pass rate")
    else:
        print("\n[-] FINAL FAILURE.")
        print(f"    Final Coverage: {final_coverage}%")
        print(f"    Final Pass Rate: {attempt_history[-1]['pass_rate']:.1f}%")
        print(f"    Total Attempts: {attempts}")
        print("    See detailed attempt summary above.")
        print("[X] INCINERATED.")
        sys.exit(1)

if __name__ == "__main__":
    main()