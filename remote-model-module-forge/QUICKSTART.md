# Quick Start Guide

Get started commissioning your first brick in 5 minutes.

## Step 1: Install (30 seconds)

```bash
# From the project directory
pip install -e .
```

## Step 2: Set API Key (10 seconds)

```bash
# Option A: Environment variable
export Z_AI_API_KEY=your_actual_z_ai_api_key

# Option B: .env file
cp .env.example .env
nano .env  # Edit and save your API key
```

**Important**: The variable is `Z_AI_API_KEY` (with underscore between Z and AI).

## Step 3: Describe Your Module (NEW - Optional but Recommended)

Instead of writing a JSON spec manually, describe what you want in plain English:

```bash
# Describe your module
brick describe "A calculator that can add, subtract, and multiply numbers"

# Or provide a description file
echo "A calculator with add, subtract, multiply, divide" > my_module_desc.txt
brick describe --output calculator_spec.json my_module_desc.txt
```

This will:
- Analyze your description
- Generate a complete JSON spec
- Write it to a file for you to review
- Save time and avoid JSON syntax errors

### What Makes a Good Description?

**✅ Good:**
```
"A calculator that performs basic arithmetic: add, subtract, multiply, and divide two numbers. 
All operations should handle floating point numbers and return floats."
```

**✅ Good:**
```
"A string utilities module with functions to reverse strings, convert to uppercase/lowercase,
and count words in a text."
```

**❌ Too vague:**
```
"A math module"  // What kind of math?
"A string module"  // What should it do?
```

**✅ Specific:**
```
"A module that validates email addresses, sanitizes user input by removing HTML tags,
and generates unique IDs with a configurable prefix."
```

### Review and Edit the Generated Spec

After `brick describe` creates your spec file, review it:

```bash
# View the generated spec
cat calculator_spec.json

# Or edit it if needed
nano calculator_spec.json  # or your preferred editor
```

## Step 4: Commission Your Brick (2-5 minutes)

```bash
brick run calculator_spec.json
```

**What happens:**
1. System enumerates your functions
2. AI chooses which function to implement first
3. Generates Python code for the function
4. Creates pytest tests with 100.00% coverage goal
5. Runs tests and enforces 100.00% coverage
6. Generates a colorful verification UI
7. Halt with a complete report

## Step 5: Review the Report

## Step 1: Install (30 seconds)

```bash
# From the project directory
pip install -e .
```

## Step 2: Set API Key (10 seconds)

```bash
# Option A: Environment variable
export Z_AI_API_KEY=your_actual_z_ai_api_key

# Option B: .env file
cp .env.example .env
nano .env  # Edit and save your API key
```

**Important**: The variable is `Z_AI_API_KEY` (with underscore between Z and AI).

## Step 3: Describe and Create Your First Spec (2 minutes)

**No JSON needed!** Just describe what you want:

```bash
# One command that does it all
brick build "A calculator that adds and subtracts numbers"
```

This will:
1. Generate a proper JSON spec from your description
2. Run the brick commission automatically
3. Show you the final code and results

OR create JSON manually (advanced):

Create a file `my_first_brick.json`:

```json
{
  "module_name": "simple_math",
  "module_description": "Basic arithmetic operations",
  "required_public_functions": [
    {
      "name": "add",
      "description": "Adds two numbers together",
      "inputs": ["a: float", "b: float"],
      "outputs": "float",
      "side_effects": "None"
    }
  ]
}
```

## Step 4: Commission Your Brick (2-5 minutes)

```bash
brick run my_first_brick.json
```

**What happens:**
1. System enumerates your functions
2. AI chooses which function to implement first
3. Generates Python code for the function
4. Creates pytest tests with 100.00% coverage goal
5. Runs tests and enforces 100.00% coverage
6. Generates a colorful verification UI
7. Halts with a complete report

## Step 5: Review the Report

After completion, you'll see:

```
============================================================
BRICK COMMISSION REPORT
============================================================

Module: simple_math
Brick Function: add
Status: completed

FILES CHANGED
-------------
  - simple_math.py
  - tests/test_simple_math.py

TEST COMMAND
------------
pytest tests/test_simple_math.py -v

UI RUN COMMAND
--------------
python runs/simple_math_<timestamp>_runner.py

UI URL
------
http://127.0.0.1:8000
```

## Step 6: Try the UI (1 minute)

```bash
# Start the UI server
python runs/simple_math_<timestamp>_runner.py

# In your browser, open:
# http://127.0.0.1:8000
```

The UI lets you:
- Click sample input buttons
- Enter custom inputs
- See the function output immediately
- View validation errors

## What If Something Goes Wrong?

### API Key Not Set

```bash
# Check if it's set
echo $Z_AI_API_KEY

# If empty, set it
export Z_AI_API_KEY=your_actual_key
```

### Want to Test Without Using API

```bash
# Dry run mode - no API calls, just tests logic
DRY_RUN=true brick run my_first_brick.json
```

### Need to Stop Immediately

```bash
# Create a STOP file in project root
touch STOP

# The brick will halt immediately
```

### Coverage Fails

The system will automatically retry once. If still fails, manually:

```bash
# Run tests manually
pytest tests/test_simple_math.py -v

# Check coverage
coverage run -m pytest && coverage report

# Look for lines not covered, adjust spec if needed, then:
brick run my_first_brick.json
```

## What Next?

### Commission More Bricks

If your spec has multiple functions, just run again:

```bash
# Each run implements ONE function
# State is preserved between runs
brick run my_first_brick.json
```

The AI will implement functions in optimal order based on dependencies.

### Create a New Module

Just create a new spec file:

```bash
# Create spec for a new module
cat > my_new_module.json << 'EOF'
{
  "module_name": "my_module",
  "module_description": "What my module does",
  "required_public_functions": [
    {
      "name": "my_function",
      "description": "What my function does",
      "inputs": ["param: type"],
      "outputs": "return_type",
      "side_effects": "Any side effects"
    }
  ]
}
EOF

# Commission it
brick run my_new_module.json
```

## Common Spec Patterns

### Simple Function

```json
{
  "name": "add",
  "description": "Adds two numbers",
  "inputs": ["a: float", "b: float"],
  "outputs": "float",
  "side_effects": "None"
}
```

### String Function

```json
{
  "name": "reverse",
  "description": "Reverses a string",
  "inputs": ["s: str"],
  "outputs": "str",
  "side_effects": "None"
}
```

### Validation Function

```json
{
  "name": "is_valid_email",
  "description": "Validates email format",
  "inputs": ["email: str"],
  "outputs": "bool",
  "side_effects": "None"
}
```

### Function With Multiple Inputs

```json
{
  "name": "calculate_tax",
  "description": "Calculates tax on price",
  "inputs": ["price: float", "rate: float"],
  "outputs": "float",
  "side_effects": "None"
}
```

## Quick Reference

| Command | What It Does | Example |
|----------|----------------|----------|
| `brick run <spec>` | Commission one brick | `brick run my_spec.json` |
| `brick status <id>` | Check run status | `brick status calculator_20251231_120000` |
| `brick report <id>` | View full report | `brick report calculator_20251231_120000` |
| `brick ui <id>` | Open verification UI | `brick ui calculator_20251231_120000` |

## Environment Variables

| Variable | Purpose | Default |
|----------|-----------|----------|
| `Z_AI_API_KEY` | Your Z.ai API key | (required) |
| `Z_AI_BASE_URL` | API endpoint | `https://open.bigmodel.cn/api/paas/v4` |
| `Z_AI_MODEL_NAME` | Model to use | `glm-4.7` |
| `DRY_RUN` | Skip API calls | `false` |
| `RUNS_DIR` | Where to store runs | `runs` |
| `LOGS_DIR` | Where to store logs | `logs` |

## Getting Help

```bash
# CLI help
brick --help

# Command help
brick run --help
brick status --help
brick report --help
brick ui --help
```

## Tips for Success

1. **Start Simple**: Begin with a single, clear function
2. **Be Descriptive**: Good descriptions lead to better implementations
3. **Specify Types Clearly**: Use Python types (`str`, `float`, `int`, `bool`, etc.)
4. **One Brick at a Time**: Let the AI choose the order
5. **Review Generated Code**: Check that it matches your expectations
6. **Use the UI**: It's great for manual verification
7. **Check Coverage**: Verify tests actually cover all branches

## Example: Full Session

```bash
# 1. Install
pip install -e .

# 2. Set API key
export Z_AI_API_KEY=sk-xxxxxxxxxxxxx

# 3. Create spec
cat > my_brick.json << 'EOF'
{
  "module_name": "calculator",
  "module_description": "Simple calculator",
  "required_public_functions": [
    {
      "name": "add",
      "description": "Adds two numbers",
      "inputs": ["a: float", "b: float"],
      "outputs": "float",
      "side_effects": "None"
    }
  ]
}
EOF

# 4. Commission brick
brick run my_brick.json

# 5. View report
brick report calculator_$(date +%Y%m%d_%H%M%S)

# 6. Try the UI
python runs/calculator_$(date +%Y%m%d_%H%M%S)_runner.py

# Open http://127.0.0.1:8000 in browser
```

## Need More Help?

- Full documentation: See `README.md`
- Integration tests: See `tests/integration/README.md`
- Example specs: See `tests/integration/specs/`
