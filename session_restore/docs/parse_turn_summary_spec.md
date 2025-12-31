# parse_turn_summary() - Test Coverage Specification

## Overview

The `parse_turn_summary()` function parses the LLM's structured response into a dictionary containing the turn summary fields.

**Purpose**: Extract structured data from LLM-generated turn summary

**Current Coverage**: To be determined

## Function Signature

```python
def parse_turn_summary(llm_response: str) -> Dict[str, Optional[str]]
```

## Parameters

| Parameter | Type | Description |
|----------|-------|-----------|
| `llm_response` | str | The LLM's response following TURN_SUMMARY_SCHEMA format |

## Returns

A dictionary with the following keys (all Optional[str]):
- `turn_number`: Integer turn number as string
- `user_request_summary`: Summary of what user asked
- `agent_response_summary`: What agent did/approached
- `key_outcomes`: What was accomplished in this turn
- `state_changes`: What changed in overall session state
- `artifacts_modified`: Comma-separated list of files touched
- `constraints_added`: New constraints or assumptions from this turn
- `open_questions`: Unresolved issues or questions

## Behavior

### Input Handling
- Extracts the "TURN SUMMARY" section from the response
- Parses each field using the pattern "Field name: value"
- Handles missing or empty fields (returns None for missing values)
- Strips leading/trailing whitespace from values
- Handles multi-line responses gracefully

### Expected Input Format

```text
TURN SUMMARY

Turn number: 0
User request summary: Build a CLI tool
Agent response summary: I helped build the CLI tool
Key outcomes: Created main.py and config.py
State changes: Project structure established
Artifacts modified: main.py, config.py
Constraints/assumptions added: Must use argparse
Open questions after this turn: How to handle errors?
```

### Output Format

```python
{
    "turn_number": "0",
    "user_request_summary": "Build a CLI tool",
    "agent_response_summary": "I helped build the CLI tool",
    "key_outcomes": "Created main.py and config.py",
    "state_changes": "Project structure established",
    "artifacts_modified": "main.py, config.py",
    "constraints_added": "Must use argparse",
    "open_questions": "How to handle errors?",
}
```

## Coverage Areas

### Input Validation
- Empty response string
- Response without "TURN SUMMARY" header
- Response with missing fields
- Response with extra whitespace
- Response with extra content before/after summary

### Field Parsing
- All 8 required fields present
- Some fields missing
- All fields missing (minimal valid format)
- Fields with empty values (e.g., "Key outcomes: ")

### Format Handling
- Field with colon in value (e.g., "Constraints/assumptions added: Use: argparse library")
- Multi-line values
- Values with leading/trailing whitespace
- Values with special characters

### Edge Cases
- Response contains only header
- Response contains header but no fields
- Response has malformed lines (no colon)
- Response with duplicate field names

## Test Requirements for 100% Coverage

### Complete Response Tests
- Test with all fields present and populated
- Test with all fields present but some empty

### Missing Field Tests
- Test with only turn_number present
- Test with only turn_number and user_request_summary
- Test with missing turn_number
- Test with missing multiple fields

### Malformed Input Tests
- Empty string input
- Response without "TURN SUMMARY" header
- Response with only "TURN SUMMARY" line
- Response with malformed field lines (no colon)

### Whitespace Tests
- Response with extra newlines between fields
- Response with leading/trailing whitespace
- Response with extra spaces around colons
- Values with leading/trailing whitespace

### Special Value Tests
- Value contains colons (e.g., "Key outcomes: Task 1: Done")
- Value contains special characters
- Empty value (e.g., "Artifacts modified: ")
- Multi-line value (though schema expects single line)

### Partial Response Tests
- Response with only first half of fields
- Response with only last half of fields
- Response with fields in wrong order

## Dependencies

- `re` (from standard library) - For pattern matching

## Error Handling

### Input Errors
- Empty input returns dictionary with all None values
- Missing "TURN SUMMARY" header returns dictionary with all None values
- Malformed lines are skipped (field not included in result)

### Return Value
- Always returns a dictionary with all 8 keys present
- Missing fields have value None
- Present but empty fields have value "" (empty string)

## Implementation Notes

### Algorithm
1. Find the "TURN SUMMARY" header in the response
2. Extract all lines after the header
3. For each line:
   - Skip empty lines and header lines
   - Split on first colon to separate field name and value
   - Map field name to corresponding key in output dictionary
   - Strip whitespace from value
4. Return dictionary with all keys (missing fields = None)

### Field Name Mapping

| Schema Field Name | Dictionary Key |
|-------------------|----------------|
| Turn number | turn_number |
| User request summary | user_request_summary |
| Agent response summary | agent_response_summary |
| Key outcomes | key_outcomes |
| State changes | state_changes |
| Artifacts modified | artifacts_modified |
| Constraints/assumptions added | constraints_added |
| Open questions after this turn | open_questions |

## Integration Tests

- Integration with `build_turn_prompt()` to validate round-trip
- Integration with `process_turns_incrementally()` for end-to-end flow

## Coverage Target

**Function**: `parse_turn_summary()`

**Estimated Lines**: 40-60 lines
**Target**: 100% test coverage

**Current Coverage**: Unknown (to be determined)

## Test Files

- `tests/test_turn_summarizer.py` (extend existing file)
- Integration tests in `tests/test_integration.py` (existing)

## Example Test Case

```python
def test_parse_complete_summary():
    llm_response = """
    TURN SUMMARY

    Turn number: 0
    User request summary: Build a CLI tool
    Agent response summary: Created CLI structure
    Key outcomes: main.py created
    State changes: Project initialized
    Artifacts modified: main.py
    Constraints/assumptions added: Python 3.8+
    Open questions after this turn: Error handling?
    """
    result = parse_turn_summary(llm_response)
    assert result["turn_number"] == "0"
    assert result["user_request_summary"] == "Build a CLI tool"
    assert result["agent_response_summary"] == "Created CLI structure"
    # ... etc
```
