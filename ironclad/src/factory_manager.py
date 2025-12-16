import json
import os
import sys
import ollama
# We import logic from your existing Ironclad tool
import ironclad

MODEL_NAME = "gpt-oss:20b"

def build_components(blueprint):
    """
    Iterates through the blueprint and orders Ironclad to build each brick.
    """
    module_dir = os.path.join("build", blueprint['module_name'])
    os.makedirs(module_dir, exist_ok=True)
    
    verified_files = []

    print(f"[*] Starting build for module: {blueprint['module_name']}")
    
    for func in blueprint['functions']:
        print(f"\n[Factory] Commissioning brick: {func['name']}...")
        
        # Construct the detailed prompt for Ironclad
        request = (
            f"Create a function with signature '{func['signature']}'. "
            f"Requirements: {func['description']}. "
            "Ensure 100% test coverage."
        )
        
# --- CALLING IRONCLAD ---
        # Hooking into your existing Ironclad logic:
        candidate = ironclad.generate_candidate(request, MODEL_NAME, ironclad.DEFAULT_SYSTEM_PROMPT) 
        
        # Run Ironclad Validation Loop
        is_valid = False
        attempts = 0
        while not is_valid and attempts < 3:
            is_valid, logs = ironclad.validate_candidate(candidate)
            if not is_valid:
                if attempts < 2:  # Only repair 2 times max
                    print(f"   [-] Ironclad Repairing {func['name']} (Attempt {attempts+1})...")
                    candidate = ironclad.repair_candidate(candidate, logs, MODEL_NAME, ironclad.DEFAULT_SYSTEM_PROMPT)
                attempts += 1
        
        if is_valid and candidate:
            print(f"   [+] Verified: {func['name']}")
            # Save the file into the module folder
            filename = f"{func['name']}.py"
            with open(os.path.join(module_dir, filename), "w") as f:
                f.write(candidate['code'])
            verified_files.append(func['name'])
        else:
            print(f"   [!] CRITICAL FAILURE: Could not build {func['name']}.")
            return False, module_dir, []

    return True, module_dir, verified_files

def assemble_main(blueprint, module_dir, components):
    """
    The Final Step: The Architect writes the 'main.py' glue code 
    that imports the verified components.
    """
    print("\n[*] Assembling final application...")
    
    assembler_prompt = f"""
    You are the Lead Integrator.
    We have verified Python files in the current directory: {components}.
    
    Your Job: Write a `main.py` script that imports these functions and implements this logic:
    "{blueprint['main_logic_description']}"
    
    The script must be robust and ready to run. Output JSON with "filename": "main.py" and "code".
    """
    
    response = ollama.chat(model=MODEL_NAME, messages=[
        {'role': 'system', 'content': "You output JSON only."},
        {'role': 'user', 'content': assembler_prompt}
    ])
    
    data = json.loads(clean_json(response['message']['content']))
    
    with open(os.path.join(module_dir, "main.py"), "w") as f:
        f.write(data['code'])
        
    # Create __init__.py
    with open(os.path.join(module_dir, "__init__.py"), "w") as f:
        f.write("")
        
    print(f"[SUCCESS] Module built at: {module_dir}/")

def clean_json(text):
    import re
    text = re.sub(r"^```(json)?", "", text.strip())
    return re.sub(r"```$", "", text).strip()

if __name__ == "__main__":
    if not os.path.exists("blueprint.json"):
        print("Run module_designer.py first!")
        sys.exit(1)
        
    with open("blueprint.json", "r") as f:
        blueprint = json.load(f)
        
    success, directory, components = build_components(blueprint)
    
    if success:
        assemble_main(blueprint, directory, components)