# process_turns_incrementally() - Test Coverage Specification

## Overview

The `process_turns_incrementally()` function orchestrates the turn-by-turn summarization process, building up accumulated session state across all conversation turns.

**Purpose**: Process all turns sequentially, accumulating state across the session

**Current Coverage**: To be determined

## Function Signature

```python
def process_turns_incrementally(
    session_name: str,
    turns: List[TurnRound],
    llm_backend: Optional[Callable] = None,
) -> Dict
```

## Parameters

| Parameter | Type | Description |
|----------|-------|-----------|
| `session_name` | str | Name of the session |
| `turns` | List[TurnRound] | List of parsed conversation turns |
| `llm_backend` | Optional[Callable] | Function to call for LLM inference (signature: `prompt: str -> str: response`) |

## Returns

Dictionary with:
- `turn_summaries`: List of parsed turn summaries (one per turn)
- `accumulated_state`: Final accumulated session state with:
  - `high_level_goal`: String or None
  - `key_decisions`: List of strings
  - `constraints`: List of strings
  - `artifacts`: List of strings
  - `open_questions`: List of strings

## Behavior

### Processing Loop
For each turn in sequence:
1. Build prompt using `build_turn_prompt()` with previous summary and accumulated state
2. Call LLM backend (or use mock if not provided)
3. Parse LLM response using `parse_turn_summary()`
4. Extract list fields using `_extract_bullet_list()` for accumulation
5. Update accumulated state with new information
6. Store summary for later use

### State Accumulation Rules
- `high_level_goal`: Set from first turn that establishes it, never overridden
- `key_decisions`: Accumulate all unique decisions across turns
- `constraints`: Accumulate all unique constraints across turns
- `artifacts`: Accumulate all unique artifacts across turns
- `open_questions`: Replace with latest set of questions

### Accumulation Logic
```python
# For first turn, extract all accumulated fields from summary
# For subsequent turns, extract and add to existing
```

### LLM Backend
- If provided: Call with prompt, use response for parsing
- If None: Return empty summary (for testing without LLM)

## Coverage Areas

### Input Validation
- Empty turns list
- Single turn
- Multiple turns (3, 5, 10+)
- With LLM backend provided
- Without LLM backend (mock mode)

### State Accumulation
- High-level goal set on first turn
- Key decisions accumulate across turns
- Constraints accumulate across turns
- Artifacts accumulate across turns
- Open questions updated (replace, not accumulate)

### Turn Processing
- First turn (no previous context)
- Middle turn (with previous summary and accumulated state)
- Last turn (final state accumulation)
- All turns processed in order

### Edge Cases
- Turn with no extracted artifacts
- Turn with no constraints
- Turn with empty user request
- LLM returns empty response
- LLM returns malformed response
- Duplicate items in accumulation

## Test Requirements for 100% Coverage

### Input Validation Tests
- Empty turns list → returns empty turn_summaries and empty accumulated_state
- Single turn → processes correctly
- Multiple turns (3) → processes all in order
- Many turns (10+) → handles large sessions

### LLM Backend Tests
- With real LLM backend (mocked callable)
- Without LLM backend (None) → returns empty summaries

### State Accumulation Tests
- High-level goal set on turn 0
- High-level goal not overridden by later turns
- Key decisions accumulate (add unique items)
- Constraints accumulate (add unique items)
- Artifacts accumulate (add unique items)
- Open questions replace (latest wins)

### Turn Processing Tests
- Turn 0 (first turn): no previous context
- Turn 1 (second turn): has previous summary and initial state
- Turn 2 (third turn): builds on accumulated state
- Turn order preserved in turn_summaries list

### Edge Case Tests
- Turn with no artifacts → artifacts list unchanged
- Turn with no decisions → decisions list unchanged
- Turn with no constraints → constraints list unchanged
- Turn with empty extracted lists → no accumulation
- LLM returns None/empty → handles gracefully
- Duplicate items in same turn → deduplicated

## Dependencies

- `build_turn_prompt()` - Build prompts for each turn
- `parse_turn_summary()` - Parse LLM responses
- `_extract_bullet_list()` - Extract list fields for accumulation
- `List`, `Dict`, `Optional`, `Callable` - Type hints

## Error Handling

### Input Errors
- Empty turns list → returns empty result structure
- Invalid turn objects → may raise exception from called functions

### LLM Errors
- LLM backend raises exception → propagates up
- LLM returns None → handled gracefully

## Implementation Notes

### Algorithm
1. Initialize empty accumulated_state and turn_summaries
2. For each turn in turns:
   a. Determine previous_summary (None for first turn)
   b. Call build_turn_prompt() with context
   c. Call llm_backend(prompt) or use empty response
   d. Parse response with parse_turn_summary()
   e. Extract and update accumulated fields
   f. Append summary to turn_summaries
3. Return {turn_summaries, accumulated_state}

### Accumulation Helper Function
```python
def _accumulate_state(
    current_state: Dict,
    new_summary: Dict,
    is_first_turn: bool
) -> Dict:
    """Update accumulated_state with new summary."""
```

## Integration Tests

- End-to-end with mock LLM backend
- End-to-end without LLM backend
- Integration with `TurnParser` output

## Coverage Target

**Function**: `process_turns_incrementally()`

**Estimated Lines**: 60-100 lines
**Target**: 100% test coverage

**Current Coverage**: Unknown (to be determined)

## Test Files

- `tests/test_turn_summarizer.py` (extend existing file)

## Example Test Case

```python
def test_single_turn_with_mock_llm():
    turns = [TurnRound(...)]
    
    def mock_llm(prompt):
        return """
        TURN SUMMARY
        
        Turn number: 0
        User request summary: Build CLI tool
        High-level goal: Build CLI tool
        Key decisions: Use argparse
        Artifacts modified: main.py
        """
    
    result = process_turns_incrementally("test", turns, mock_llm)
    
    assert len(result["turn_summaries"]) == 1
    assert result["accumulated_state"]["high_level_goal"] == "Build CLI tool"
    assert "Use argparse" in result["accumulated_state"]["key_decisions"]
    assert "main.py" in result["accumulated_state"]["artifacts"]
```

## Accumulation State Structure

```python
{
    "high_level_goal": "Build comprehensive CLI tool",
    "key_decisions": [
        "Use argparse",
        "Python 3.8+",
        "Add subcommands"
    ],
    "constraints": [
        "Must be CLI",
        "POSIX compliant",
        "No external dependencies"
    ],
    "artifacts": [
        "main.py",
        "config.py",
        "utils.py",
        "cli.py"
    ],
    "open_questions": [
        "Error handling?",
        "Help text format?"
    ]
}
```

## Notes

1. **First Turn Special Case**: First turn should extract all accumulated fields from its summary
2. **Deduplication**: Lists should deduplicate items (same decision added in multiple turns)
3. **Order Preservation**: Turn summaries maintain order of processing
4. **Empty Lists**: Empty extracted lists should not add to accumulation
5. **Backward Compatibility**: LLM backend optional for testing flexibility
