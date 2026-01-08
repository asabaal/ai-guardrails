import os
import sys
import json
import subprocess
import tempfile
import re
import ollama

from ironclad_ai_guardrails.code_utils import (
    clean_json_response,
    clean_code_content,
    log_debug_raw,
)

DEFAULT_MODEL_NAME = "gpt-oss:20b"
DEFAULT_OUTPUT_DIR = "verified_bricks"
MAX_RETRIES = 3

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
    "test": "def test_function_name... "
}
""".strip()


def generate_candidate(request: str, model_name=DEFAULT_MODEL_NAME, system_prompt=DEFAULT_SYSTEM_PROMPT):
    prompt = f"{system_prompt}\n\nREQUEST:\n{request}"
    try:
        resp = ollama.chat(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
        )
        raw_content = resp["message"]["content"]
        content = resp["message"]["content"]
        data = json.loads(clean_json_response(content))
        data["code"] = clean_code_content(data.get("code", ""))
        data["test"] = clean_code_content(data.get("test", ""))
        return data
    except json.JSONDecodeError:
        log_debug_raw(phase='generate', message='Model output was not valid JSON', data=raw_content)
        print("[!] Validation Failed: Model output was not valid JSON.")
        return None
    except Exception as e:
        print("[!] Error connecting to Ollama: Connection error")
        return None


def validate_candidate(candidate):
    if candidate is None:
        return False, "Candidate is None"
    filename = candidate.get("filename", "candidate")
    code = candidate.get("code", "")
    test = candidate.get("test", "")

    with tempfile.TemporaryDirectory() as temp_dir:
        code_path = os.path.join(temp_dir, f"{filename}.py")
        test_path = os.path.join(temp_dir, f"test_{filename}.py")

        with open(code_path, "w", encoding="utf-8") as f:
            f.write(code)
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(test)

        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_path],
            capture_output=True,
            text=True,
            cwd=temp_dir,
        )

        if result.returncode == 0:
            return True, result.stdout
        return False, result.stdout


def save_brick(candidate, output_dir=DEFAULT_OUTPUT_DIR):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    name = candidate["filename"]
    with open(os.path.join(output_dir, f"{name}.py"), "w", encoding="utf-8") as f:
        f.write(candidate["code"])

    with open(os.path.join(output_dir, f"test_{name}.py"), "w", encoding="utf-8") as f:
        f.write(candidate["test"])

    print(f"[SUCCESS] Verified brick saved to: {output_dir}/{name}.py")


def repair_candidate(candidate, traceback_log, model_name=DEFAULT_MODEL_NAME, system_prompt=DEFAULT_SYSTEM_PROMPT):
    print("[*] Attempting repair...")

    repair_prompt = f"""
The code you generated failed tests.

TRACEBACK:
{traceback_log}

CURRENT JSON:
{json.dumps(candidate, ensure_ascii=False)}

Fix the code and tests if needed.
Return only the fixed JSON structure.
""".strip()

    try:
        resp = ollama.chat(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": repair_prompt}
            ],
        )
        raw_content = resp["message"]["content"]
        content = resp["message"]["content"]
        data = json.loads(clean_json_response(content))
        data["code"] = clean_code_content(data.get("code", ""))
        data["test"] = clean_code_content(data.get("test", ""))
        return data
    except json.JSONDecodeError:
        log_debug_raw(phase='repair', message='Repair output was not valid JSON', data=raw_content)
        print("[!] Repair Error: Model output was not valid JSON.")
        return None
    except Exception as e:
        print(f"[!] Repair Error: {e}")
        return None


def main(request=None, model_name=None, output_dir=None, system_prompt=None):
    # Import ironclad module for patch compatibility
    import ironclad_ai_guardrails.ironclad as ironclad
    
    if request is None:
        if len(sys.argv) < 2:
            print("Usage: python ironclad.py 'Your request here'")
            sys.exit(1)
        request = sys.argv[1]

    model_name = model_name or DEFAULT_MODEL_NAME
    output_dir = output_dir or DEFAULT_OUTPUT_DIR
    system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT

    candidate = ironclad.generate_candidate(request, model_name, system_prompt)
    if not candidate:
        print("[X] INCINERATED: Output invalid.")
        sys.exit(1)

    is_valid, logs = ironclad.validate_candidate(candidate)
    attempts = 0

    while (not is_valid) and (attempts < MAX_RETRIES):
        print(f"[-] FAIL (Attempt {attempts + 1}/{MAX_RETRIES}). Triggering repair...")
        candidate = ironclad.repair_candidate(candidate, logs, model_name, system_prompt)
        if candidate is None:
            print("[!] Repair produced invalid JSON. Aborting.")
            sys.exit(1)
        is_valid, logs = ironclad.validate_candidate(candidate)
        attempts += 1

    if is_valid:
        print("[+] Verified after 1 repairs.")
        ironclad.save_brick(candidate, output_dir)
        return candidate

    print("[-] FINAL FAILURE.")
    sys.exit(1)


if __name__ == "__main__":
    main()
