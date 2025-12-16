import os
import sys
import json
import subprocess
import tempfile
import re
import ollama

# --- CONFIGURATION ---
MODEL_NAME = "gpt-oss:20b" 
OUTPUT_DIR = "verified_bricks"
MAX_RETRIES = 3  # The "Bound" in Bounded Mechanic

# --- PROMPTS ---
SYSTEM_PROMPT = """
You are a strict code generator. You output JSON only.
Your goal is to write a Python function and a corresponding Pytest unit test.

IMPORTANT: The "filename" field MUST exactly match the actual function name you create in the code.
Do not use generic placeholders like "function_name".

Output format must be exactly this JSON structure:
{
    "filename": "actual_function_name",
    "code": "def actual_function_name... ",
    "test": "import pytest\\nfrom actual_function_name import actual_function_name\\n\\ndef test_case_1()..."
}
"""

REPAIR_PROMPT_TEMPLATE = """
The code you generated failed the tests.
Here is the error traceback:
{traceback}

Here is the code you wrote:
{code}

Fix the code (and tests if necessary) to solve the error.
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
    try:
        response = ollama.chat(model=MODEL_NAME, messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': user_message},
        ])
        return json.loads(clean_json_response(response['message']['content']))
    except Exception as e:
        print(f"[!] Generation Error: {e}")
        return None

def repair_candidate(candidate, traceback_log):
    """
    The Repair Mechanic: Takes broken code + error, asks for a patch.
    """
    print(f"[*] Attempting repair...")
    
    prompt_content = REPAIR_PROMPT_TEMPLATE.format(
        traceback=traceback_log,
        code=candidate.get("code", "")
    )
    
    try:
        response = ollama.chat(model=MODEL_NAME, messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': prompt_content},
        ])
        return json.loads(clean_json_response(response['message']['content']))
    except Exception as e:
        print(f"[!] Repair Error: {e}")
        return None

def validate_candidate(candidate):
    if not candidate or "code" not in candidate:
        return False, "Invalid JSON structure"

    function_name = candidate.get("filename", "unknown_func")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        code_path = os.path.join(temp_dir, f"{function_name}.py")
        test_path = os.path.join(temp_dir, f"test_{function_name}.py")
        
        with open(code_path, "w") as f:
            f.write(candidate['code'])
        
        import_fix = "import sys\nimport os\nsys.path.append(os.getcwd())\n"
        with open(test_path, "w") as f:
            f.write(import_fix + candidate['test'])
            
        print(f"[*] Running tests...")
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_path],
            capture_output=True, text=True, cwd=temp_dir
        )
        
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stdout

def save_brick(candidate):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    name = candidate['filename']
    with open(os.path.join(OUTPUT_DIR, f"{name}.py"), "w") as f:
        f.write(candidate['code'])
    with open(os.path.join(OUTPUT_DIR, f"test_{name}.py"), "w") as f:
        f.write(candidate['test'])
    print(f"[SUCCESS] Saved to: {OUTPUT_DIR}/{name}.py")

def main():
    if len(sys.argv) < 2:
        print("Usage: python ironclad_phase2.py 'request'")
        sys.exit(1)

    # 1. First Attempt
    candidate = generate_candidate(sys.argv[1])
    if not candidate:
        sys.exit(1)

    # 2. Validation Loop
    is_valid, logs = validate_candidate(candidate)
    
    attempts = 0
    while not is_valid and attempts < MAX_RETRIES:
        print(f"[-] FAIL (Attempt {attempts + 1}/{MAX_RETRIES}). triggering repair...")
        # print(logs) # Uncomment if you want to see the error every time
        
        # 3. The Bounded Repair
        candidate = repair_candidate(candidate, logs)
        if not candidate:
            print("[!] Repair produced invalid JSON. Aborting.")
            sys.exit(1)
            
        is_valid, logs = validate_candidate(candidate)
        attempts += 1

    # 4. Final Gate
    if is_valid:
        print(f"[+] Verified after {attempts} repairs.")
        save_brick(candidate)
    else:
        print("[-] FINAL FAILURE.")
        print("--- Last Traceback ---")
        print(logs)
        print("[X] INCINERATED.")
        sys.exit(1)

if __name__ == "__main__":
    main()