# Integration Tests

This directory contains integration tests that make real API calls to Z.ai.

## Prerequisites

1. Set your Z.ai API key:
   ```bash
   export Z_AI_API_KEY=your_actual_key
   ```

2. Install brick_commissioner:
   ```bash
   pip install -e .
   ```

## Running Tests

### Quick Test Runner

Run all integration tests with a single command:

```bash
python tests/integration/run_tests.py
```

### Run with pytest

Run specific test categories:

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run only simple brick tests
pytest tests/integration/test_full_workflow.py::TestSimpleBrick -v

# Run only workflow tests
pytest tests/integration/test_full_workflow.py::TestFullWorkflow -v

# Run only error handling tests
pytest tests/integration/test_full_workflow.py::TestErrorHandling -v
```

## Test Specs

Integration test specs are in `tests/integration/specs/`:

- `simple_math.json` - Basic arithmetic operations
- `string_utils.json` - String manipulation functions
- `string_calculator.json` - Multiple string operations

## What Gets Tested

1. **Simple Bricks** - Single function implementation
   - Function code generation
   - Test file creation
   - 100% coverage enforcement

2. **Full Workflow** - End-to-end process
   - Spec parsing
   - Function selection
   - Code generation
   - Test implementation
   - Coverage verification
   - UI generation
   - Report creation

3. **Error Handling**
   - Invalid specs
   - Empty function lists
   - STOP file behavior

4. **Limits Enforcement**
   - File change limits
   - Timeout behavior
   - Wall time limits

5. **Multiple Functions**
   - Correct selection of one function per run
   - Implementation order based on dependencies

## Cleanup

After running tests, you may want to clean up generated files:

```bash
# Clean up test modules
find . -name "*test*.py" -path "*/test_*" -delete 2>/dev/null || true
find . -name "*.pyc" -delete
rm -rf .coverage htmlcov .pytest_cache
```
