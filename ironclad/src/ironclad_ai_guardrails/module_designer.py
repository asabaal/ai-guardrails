import sys
import json
import re
import ollama

# --- CONFIGURATION ---
MODEL_NAME = "gpt-oss:20b"

# --- THE ARCHITECT PERSONA ---
ARCHITECT_PROMPT = """
You are a Senior Software Architect. You do not write code implementation. 
You design the structure of Python modules.

Your Goal: Break a user request into small, atomic, testable functions.

Output strict JSON only (no markdown) in this format:
{
    "module_name": "snake_case_name",
    "dependencies": ["list", "of", "libs"],
    "functions": [
        {
            "name": "function_name",
            "signature": "def function_name(arg1: type) -> type",
            "description": "Detailed description of logic and edge cases."
        }
    ],
    "main_logic_description": "Describe how the main block should stitch these functions together."
}
"""

def clean_json(text):
    text = text.strip()
    text = re.sub(r"^```(json)?", "", text)
    text = re.sub(r"```$", "", text)
    return text.strip()

def draft_blueprint(request):
    print(f"[*] Architecting solution for: '{request}'...")
    try:
        # Use ollama.generate instead of chat to avoid hanging with gpt-oss models
        full_prompt = f"{ARCHITECT_PROMPT}\n\n{request}"
        response = ollama.generate(model=MODEL_NAME, prompt=full_prompt)
        return json.loads(clean_json(response['response']))
    except Exception as e:
        print(f"[!] Blueprint Failed: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python module_designer.py 'I want a tool that...'")
        sys.exit(1)
        
    blueprint = draft_blueprint(sys.argv[1])
    
    if blueprint:
        print(json.dumps(blueprint, indent=4))
        # In the next step, we will pipe this JSON into the Factory.
        with open("blueprint.json", "w") as f:
            json.dump(blueprint, f, indent=4)
        print("[+] Blueprint saved to blueprint.json")

if __name__ == "__main__":
    main()