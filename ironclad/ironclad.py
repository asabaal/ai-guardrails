import os
import sys
import json
import subprocess
import tempfile
import re
import ollama

# --- CONFIGURATION ---
MODEL_NAME = "gpt-oss:20b"  # Must be installed via 'ollama pull llama3'
OUTPUT_DIR = "verified_bricks"  # Where successful code is saved

# --- PROMPT TEMPLATE ---
# We force the model to output strict JSON so we can parse it reliably.
SYSTEM_PROMPT = """
You are a strict code generator. You do not talk. You output JSON only.
Your goal is to write a Python function and a corresponding Pytest unit test.
The test must prove the function works and handle edge cases.

Output format must be exactly this JSON structure:
{
    "filename": "function_name",
    "code": "def function_name... ",
    "test": "import pytest\\nfrom function_name import function_name\\n\\ndef test_case_1()..."
}
"""

def clean_json_response(response_text):
    """
    Cleans up the model's output if it adds markdown fences (```json ... ```).
    """
    cleaned = response_text.strip()
    # Remove markdown code blocks if present
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(json)?", "", cleaned)
        cleaned = re.sub(r"```$", "", cleaned)
    return cleaned.strip()

def generate_candidate(request):
    """
    Step 1: The Generator
    Sends the request to the local LLM and expects a JSON response.
    """
    print(f"[*] Generating candidate for: '{request}'...")
    
    user_message = f"Write a Python function that: {request}. Include comprehensive tests."
    
    try:
        response = ollama.chat(model=MODEL_NAME, messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': user_message},
        ])
        
        raw_content = response['message']['content']
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
    function_name = candidate.get("filename", "unknown_func")
    code_content = candidate.get("code", "")
    test_content = candidate.get("test", "")
    
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

def save_brick(candidate):
    """
    Step 4: The Vault
    Saves the verified code permanently.
    """
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    name = candidate['filename']
    with open(os.path.join(OUTPUT_DIR, f"{name}.py"), "w") as f:
        f.write(candidate['code'])
    
    with open(os.path.join(OUTPUT_DIR, f"test_{name}.py"), "w") as f:
        f.write(candidate['test'])
        
    print(f"[SUCCESS] Verified brick saved to: {OUTPUT_DIR}/{name}.py")

def main():
    if len(sys.argv) < 2:
        print("Usage: python ironclad.py 'Your request here'")
        print("Example: python ironclad.py 'extract phone numbers from a string'")
        sys.exit(1)

    user_request = sys.argv[1]
    
    # 1. Generate
    candidate = generate_candidate(user_request)
    
    if not candidate:
        print("[X] INCINERATED: Output invalid.")
        sys.exit(1)
        
    # 2. Validate
    is_valid, logs = validate_candidate(candidate)
    
    # 3. Decision Gate
    if is_valid:
        save_brick(candidate)
    else:
        print("[X] INCINERATED: Logic failed verification. Code discarded.")
        sys.exit(1)

if __name__ == "__main__":
    main()