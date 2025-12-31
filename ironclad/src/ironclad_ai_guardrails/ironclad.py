import os
import sys
import json
import subprocess
import tempfile
import re
import ollama
from ironclad_ai_guardrails.code_utils import clean_json_response as utils_clean_json_response, clean_code_content

# --- DEFAULT CONFIGURATION ---
DEFAULT_MODEL_NAME = "gpt-oss:20b"  # Must be installed via 'ollama pull llama3'
DEFAULT_OUTPUT_DIR = "verified_bricks"  # Where successful code is saved
MAX_RETRIES = 3  # Maximum number of repair attempts

# --- DEFAULT PROMPT TEMPLATE ---
# We force the model to output strict JSON so we can parse it reliably.
DEFAULT_SYSTEM_PROMPT = """
You are a strict code generator. You do not talk. You output JSON only.
Your goal is to write a Python function and a corresponding Pytest unit test.
The test must prove the function works and handle edge cases.

CRITICAL: All code must contain actual newline characters, not escaped \\n sequences.
When writing Python code, use real newlines between statements and lines.

Output format must be exactly this JSON structure:
{
    "filename": "function_name",
    "code": "def function_name... ",
    "test": "import pytest\nfrom function_name import function_name\n\ndef test_case_1()..."
}

The code and test fields must contain properly formatted Python code with actual newline characters.
"""

def clean_json_response(response_text):
    """
    Cleans up the model's output if it adds markdown fences (```json ... ```).
    Also decodes escaped newlines in JSON content.
    Returns a cleaned JSON string ready for parsing.
    """
    return utils_clean_json_response(response_text)

def generate_candidate(request, model_name=DEFAULT_MODEL_NAME, system_prompt=DEFAULT_SYSTEM_PROMPT):
    """
    Step 1: The Generator
    Sends the request to the local LLM and expects a JSON response.
    """
    print(f"[*] Generating candidate for: '{request}'...")
    
    user_message = f"Write a Python function that: {request}. Include comprehensive tests."
    
    try:
        # Use ollama.generate instead of chat to avoid hanging with gpt-oss models
        full_prompt = f"{system_prompt}\n\n{user_message}"
        response = ollama.generate(model=model_name, prompt=full_prompt)
        
        raw_content = response['response']
        json_content = clean_json_response(raw_content)
        
        return json.loads(json_content)
    
    except json.JSONDecodeError:
        print("[!] Validation Failed: Model output was not valid JSON.")
        return None
    except Exception as e:
        print(f"[!] Error connecting to Ollama: {e}")
        return None

def validate_candidate(candidate):
    """
    Step 2: The Sandbox
    Writes code to a temp folder and runs pytest.
    """
    if candidate is None:
        return False, "Candidate is None - generation failed"
    
    function_name = candidate.get("filename", "unknown_func")
    code_content = clean_code_content(candidate.get("code", ""))
    test_content = clean_code_content(candidate.get("test", ""))
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Define paths
        code_path = os.path.join(temp_dir, f"{function_name}.py")
        test_path = os.path.join(temp_dir, f"test_{function_name}.py")
        
        # Write files
        with open(code_path, "w") as f:
            f.write(code_content)
        
        # We need to make sure the test file imports from the code file correctly
        # This simple injection ensures the test can find the module in the temp dir
        import_fix = "import sys\nimport os\nsys.path.append(os.getcwd())\n"
        with open(test_path, "w") as f:
            f.write(import_fix + test_content)
            
        print(f"[*] Executing tests in sandbox: {temp_dir}...")
        
        # Step 3: Execution
        # Run pytest on the temp directory
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_path],
            capture_output=True,
            text=True,
            cwd=temp_dir # Run context inside the temp dir
        )
        
        if result.returncode == 0:
            print("[+] PASS: Tests passed successfully.")
            return True, result.stdout
        else:
            print("[-] FAIL: Tests failed.")
            print("--- Traceback ---")
            print(result.stdout)
            print("-----------------")
            return False, result.stdout

def save_brick(candidate, output_dir=DEFAULT_OUTPUT_DIR):
    """
    Step 4: The Vault
    Saves the verified code permanently.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    name = candidate['filename']
    with open(os.path.join(output_dir, f"{name}.py"), "w") as f:
        f.write(candidate['code'])
    
    with open(os.path.join(output_dir, f"test_{name}.py"), "w") as f:
        f.write(candidate['test'])
        
    print(f"[SUCCESS] Verified brick saved to: {output_dir}/{name}.py")

def repair_candidate(candidate, traceback_log, model_name=DEFAULT_MODEL_NAME, system_prompt=DEFAULT_SYSTEM_PROMPT):
    """
    The Repair Mechanic: Takes broken code + error, asks for a patch.
    """
    print(f"[*] Attempting repair...")
    
    REPAIR_PROMPT_TEMPLATE = """
    The code you generated failed tests.
    Here is error traceback:
    {traceback}
    
    Here is the code you wrote:
    {code}
    
    Fix the code (and tests if necessary) to solve the error.
    Do not output explanation. Output only the fixed JSON structure.
    """
    
    prompt_content = REPAIR_PROMPT_TEMPLATE.format(
        traceback=traceback_log,
        code=candidate.get("code", "")
    )
    
    try:
        # Use ollama.generate instead of chat to avoid hanging with gpt-oss models
        full_prompt = f"{system_prompt}\n\n{prompt_content}"
        response = ollama.generate(model=model_name, prompt=full_prompt)
        return json.loads(clean_json_response(response['response']))
    except Exception as e:
        print(f"[!] Repair Error: {e}")
        return None


def main(request=None, model_name=None, output_dir=None, system_prompt=None):
    """
    Main function that can be called with parameters or from CLI
    """
    # Handle CLI mode if no parameters provided
    if request is None:
        if len(sys.argv) < 2:
            print("Usage: python ironclad.py 'Your request here'")
            print("Example: python ironclad.py 'extract phone numbers from a string'")
            sys.exit(1)
        request = sys.argv[1]
    
    # Set defaults if not provided
    model_name = model_name or DEFAULT_MODEL_NAME
    output_dir = output_dir or DEFAULT_OUTPUT_DIR
    system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
    
    # 1. Generate
    candidate = generate_candidate(request, model_name, system_prompt)
    
    if not candidate:
        print("[X] INCINERATED: Output invalid.")
        sys.exit(1)
        
    # 2. Validation Loop with Repair
    is_valid, logs = validate_candidate(candidate)
    attempts = 0
    
    while not is_valid and attempts < MAX_RETRIES:
        print(f"[-] FAIL (Attempt {attempts + 1}/{MAX_RETRIES}). Triggering repair...")
        
        # 3. The Repair
        candidate = repair_candidate(candidate, logs, model_name, system_prompt)
        if not candidate:
            print("[!] Repair produced invalid JSON. Aborting.")
            sys.exit(1)
            
        is_valid, logs = validate_candidate(candidate)
        attempts += 1

    # 4. Final Gate
    if is_valid:
        if attempts > 0:
            print(f"[+] Verified after {attempts} repairs.")
        save_brick(candidate, output_dir)
    else:
        print("[-] FINAL FAILURE.")
        print("--- Last Traceback ---")
        print(logs)
        print("[X] INCINERATED.")
        sys.exit(1)

if __name__ == "__main__":
    main()