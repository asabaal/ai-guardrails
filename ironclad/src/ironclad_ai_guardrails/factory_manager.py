import json
import os
import sys
import ollama
import ast
import tempfile
import shutil
import subprocess
# We import logic from your existing Ironclad tool
from ironclad_ai_guardrails.code_utils import clean_json_response as utils_clean_json, clean_code_content, validate_python_syntax
from ironclad_ai_guardrails.ironclad import generate_candidate, validate_candidate, repair_candidate, save_brick

MODEL_NAME = "gpt-oss:20b"

def build_components(blueprint, resume_mode="smart"):
    """
    Iterates through the blueprint and orders Ironclad to build each brick.
    resume_mode: "smart" (default) or "resume" (continue from existing)
    Returns: (partial_success, module_dir, successful_components, failed_components, status_report)
    """
    module_dir = os.path.join("build", blueprint['module_name'])
    
    # Handle resume modes
    if resume_mode == "smart" and os.path.exists(module_dir):
        # Fresh start for smart mode
        shutil.rmtree(module_dir)
    elif resume_mode == "resume" and os.path.exists(module_dir):
        print(f"[*] Resuming from existing module: {module_dir}")
    else:
        # Fresh start
        os.makedirs(module_dir, exist_ok=True)
    
    successful_components = []
    failed_components = []
    status_report = {}

    print(f"[*] Starting build for module: {blueprint['module_name']}")
    
    # Check existing components if resuming
    existing_components = set()
    if resume_mode == "resume":
        for func in blueprint['functions']:
            component_file = os.path.join(module_dir, f"{func['name']}.py")
            if os.path.exists(component_file):
                existing_components.add(func['name'])
                successful_components.append(func['name'])
                print(f"   [+] Found existing: {func['name']}")
    
    for func in blueprint['functions']:
        # Skip if already built and resuming
        if func['name'] in existing_components:
            continue
            
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
        
        if candidate is None:
            print(f"[❌] Failed to generate candidate for {func['name']}")
            failed_components.append(func['name'])
            status_report[func['name']] = "Generation failed"
            continue
        
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
            else:
                attempts += 1  # Count successful attempt too
        
        if is_valid and candidate:
            print(f"   [+] Verified: {func['name']}")
            # Save the file into the module folder with cleaned code
            filename = f"{func['name']}.py"
            cleaned_code = clean_code_content(candidate.get('code', ''))
            with open(os.path.join(module_dir, filename), "w") as f:
                f.write(cleaned_code)
            successful_components.append(func['name'])
            status_report[func['name']] = {'status': 'success', 'attempts': attempts}
        else:
            print(f"   [!] FAILED: Could not build {func['name']}.")
            failed_components.append(func['name'])
            status_report[func['name']] = {'status': 'failed', 'attempts': attempts}

    partial_success = len(successful_components) > 0
    return partial_success, module_dir, successful_components, failed_components, status_report

def generate_main_candidate(blueprint, components):
    """Generate main.py candidate with enhanced prompt"""
    assembler_prompt = f"""
    You are the Lead Integrator.
    We have verified Python files in the current directory: {components}.
    
    Your Job: Write a `main.py` script that imports these functions and implements this logic:
    "{blueprint['main_logic_description']}"
    
    Requirements:
    1. Import all component functions from their respective files
    2. Implement the main logic using these functions
    3. Include proper error handling
    4. Add a main() function and if __name__ == "__main__" guard
    5. Ensure the code is syntactically correct Python
    6. CRITICAL: Use actual newline characters in your code, not escaped \\n sequences
    
    Output JSON with "filename": "main.py" and "code" fields only.
    The code field must contain properly formatted Python code with real newlines.
    """
    
    # Use ollama.generate instead of chat to avoid hanging with gpt-oss models
    full_prompt = "You output valid JSON only. All code fields must contain actual newline characters, not escaped sequences.\n\n" + assembler_prompt
    response = ollama.generate(model=MODEL_NAME, prompt=full_prompt)
    
    try:
        data = json.loads(clean_json(response['response']))
        code = clean_code_content(data.get('code', ''))
        return code
    except (json.JSONDecodeError, KeyError) as e:
        print(f"   [!] Failed to parse main.py generation response: {e}")
        return None

def validate_main_candidate(candidate_code, components, module_dir):
    """Test that main.py works with actual components"""
    if not candidate_code:
        return False, "No candidate code provided"
    
    errors = []
    
    # 1. Syntax validation
    try:
        ast.parse(candidate_code)
    except SyntaxError as e:
        errors.append(f"Syntax error: {e}")
        return False, "; ".join(errors)
    
    # 2. Import validation - create temporary test environment
    with tempfile.TemporaryDirectory() as temp_dir:
        # Copy component files to temp directory
        for component in components:
            src_file = os.path.join(module_dir, f"{component}.py")
            if os.path.exists(src_file):
                shutil.copy(src_file, temp_dir)
        
        # Write main.py candidate to temp directory
        main_file = os.path.join(temp_dir, "main.py")
        with open(main_file, "w") as f:
            f.write(candidate_code)
        
        # 3. Try importing and running basic validation
        try:
            # Test import
            result = subprocess.run([
                sys.executable, "-c", 
                f"import sys; sys.path.insert(0, '{temp_dir}'); import main"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                errors.append(f"Import error: {result.stderr}")
        except subprocess.TimeoutExpired:
            errors.append("Import timeout")
        except Exception as e:
            errors.append(f"Import test failed: {e}")
    
    # 4. Basic integration test (if CLI tool)
    if "argparse" in candidate_code or "sys.argv" in candidate_code:
        try:
            # Test with --help flag
            with tempfile.TemporaryDirectory() as temp_dir:
                for component in components:
                    src_file = os.path.join(module_dir, f"{component}.py")
                    if os.path.exists(src_file):
                        shutil.copy(src_file, temp_dir)
                
                main_file = os.path.join(temp_dir, "main.py")
                with open(main_file, "w") as f:
                    f.write(candidate_code)
                
                result = subprocess.run([
                    sys.executable, main_file, "--help"
                ], capture_output=True, text=True, timeout=5, cwd=temp_dir)
                
                # --help should exit with error code 0 or 1, but not crash
                if result.returncode not in [0, 1] and "Error" in result.stderr:
                    errors.append(f"CLI test failed: {result.stderr}")
        except Exception as e:
            errors.append(f"CLI test error: {e}")
    
    is_valid = len(errors) == 0
    return is_valid, "; ".join(errors) if errors else "Valid"

def repair_main_candidate(candidate_code, error_logs, components, module_dir):
    """Use Ironclad to repair main.py based on validation failures"""
    repair_prompt = f"""
    The following main.py code has errors that need to be fixed:
    
    ERRORS: {error_logs}
    
    CURRENT CODE:
    {candidate_code}
    
    Available components: {components}
    
    Please fix the errors and return a corrected version of the main.py code.
    Focus on:
    1. Fixing syntax errors
    2. Correcting import statements
    3. Ensuring proper integration with available components
    4. Maintaining the original functionality
    5. CRITICAL: Ensure all code uses actual newline characters, not \\n escape sequences
    
    Return only the corrected Python code, no JSON formatting.
    The code must be properly formatted with real newlines.
    """
    
    # Use ollama.generate instead of chat to avoid hanging with gpt-oss models
    full_prompt = "You are a Python code repair specialist. Return only corrected Python code with actual newlines.\n\n" + repair_prompt
    response = ollama.generate(model=MODEL_NAME, prompt=full_prompt)
    
    repaired_code = clean_code_content(response['response'])
    return repaired_code

def assemble_main(blueprint, module_dir, components):
    """
    The Final Step: The Architect writes the 'main.py' glue code 
    that imports the verified components, with full testing/repair loop.
    """
    print("\n[*] Assembling final application...")
    
    # 1. Generate initial candidate
    candidate = generate_main_candidate(blueprint, components)
    if not candidate:
        raise Exception("Failed to generate initial main.py candidate")
    
    # 2. Ironclad validation loop
    is_valid = False
    attempts = 0
    while not is_valid and attempts < 3:
        is_valid, logs = validate_main_candidate(candidate, components, module_dir)
        if not is_valid:
            if attempts < 2:
                print(f"   [-] Repairing main.py (Attempt {attempts+1})...")
                print(f"       Issues: {logs}")
                candidate = repair_main_candidate(candidate, logs, components, module_dir)
            attempts += 1
    
    # 3. Save only if valid
    if is_valid:
        with open(os.path.join(module_dir, "main.py"), "w") as f:
            f.write(candidate)
        print(f"   [+] Main.py validated and saved")
    else:
        raise Exception(f"Failed to generate valid main.py after 3 attempts. Final errors: {logs}")
        
    # Create __init__.py
    with open(os.path.join(module_dir, "__init__.py"), "w") as f:
        f.write("")
        
    print(f"[SUCCESS] Module built at: {module_dir}/")

def clean_json(text):
    """
    Enhanced JSON cleaning function that handles markdown fences and escaped newlines.
    Returns a cleaned JSON string ready for parsing.
    """
    return utils_clean_json(text)

def run_factory_manager_workflow():
    """Run the complete factory manager workflow from blueprint.json"""
    if not os.path.exists("blueprint.json"):
        print("Run module_designer.py first!")
        sys.exit(1)
        return  # Add return for testing purposes
        
    with open("blueprint.json", "r") as f:
        blueprint = json.load(f)
        
    partial_success, directory, successful_components, failed_components, status_report = build_components(blueprint)
    
    if partial_success and successful_components:
        assemble_main(blueprint, directory, successful_components)
        
        # Report final status
        if failed_components:
            print(f"\n[⚠️]  Module completed with {len(failed_components)} failed components:")
            for comp in failed_components:
                print(f"     [❌] {comp}")
        else:
            print(f"\n[✅] All {len(successful_components)} components built successfully!")
    else:
        print(f"\n[❌] No components could be built successfully.")
        sys.exit(1)


if __name__ == "__main__":
    run_factory_manager_workflow()