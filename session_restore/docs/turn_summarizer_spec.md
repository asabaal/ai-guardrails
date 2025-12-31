# build_turn_prompt() - Test Coverage Specification

## Overview

The `build_turn_prompt()` function constructs prompts for LLM to summarize individual conversation turns with context from previous turns and accumulated session state.

**Current Coverage**: To be determined

**Purpose**: Build prompt for single turn processing with full context

## Function Signature

```python
def build_turn_prompt(
    session_name: str,
    turn: TurnRound,
    previous_summary: Optional[Dict] = None,
    accumulated_state: Optional[Dict] = None,
) -> str
```

## Parameters

| Parameter | Type | Description |
|----------|-------|-----------|
| `session_name` | str | Name of the session |
| `turn` | TurnRound | Current turn to summarize |
| `previous_summary` | Optional[Dict] | Previous turn's summary for context |
| `accumulated_state` | Optional[Dict] | Current accumulated session state |

## Behavior

### Input Handling
- If `previous_summary` is None`: No previous turn context in prompt
- If `accumulated_state` is None`: No accumulated state in prompt
- If `turn.agent_responses` has more than 10 lines: Truncate to 10 lines with "... and N more lines" suffix

### Output Format

Returns a formatted string containing:

1. **Session header**
2. **Previous turn summary** (if provided)
3. **Current turn section** including:
   - User messages (all, truncated if >10)
   - Agent responses (all, truncated if >10)
4. **Current accumulated state** including:
   - High-level goal (if established)
   - Key decisions made (if any)
   - All accumulated constraints (if any)
   - All accumulated artifacts (if any)
   - Open questions (if any)
5. **TURN_SUMMARY_SCHEMA** template

## Coverage Areas

### Input Validation
- Validate `session_name` parameter
- Validate `turn` is TurnRound with required fields (turn_number, user_messages, agent_responses, raw_lines, start_line_index, end_line_index, artifacts)
- Validate `turn.user_messages` is not empty
- Validate `turn.agent_responses` is not empty

### Format Validation
- Contains all required TURN_SUMMARY_SCHEMA sections
- Follows exact formatting rules

### Truncation
- Agent responses limited to 10 lines max
- Truncation suffix added when limit exceeded

### Context Inclusion
- Previous turn number included if previous_summary provided
- User request summary included if previous_summary provided
- Previous high-level goal included if accumulated_state provides it

### State Inclusion
- All accumulated state fields included if accumulated_state is not None

## Test Requirements for 100% Coverage

### Input Validation Tests
- Test with `session_name` variations
- Test with valid TurnRound objects
- Test with empty user messages
- Test with >10 agent responses (tests truncation)
- Test with previous_summary
- Test with accumulated_state

### Format Validation Tests
- Verify all required TURN_SUMMARY_SCHEMA sections present
- Verify exact string format compliance
- Test output structure

### Truncation Tests
- Test with exactly 10 agent responses → should NOT truncate
- Test with 11 agent responses → should truncate to 10
- Test truncation suffix is "... and N more lines"

### State Inclusion Tests
- Test accumulated_state is passed through correctly
- Verify high_level_goal is set when in accumulated_state
- Verify key_decisions accumulate
- Verify constraints accumulate
- Verify artifacts accumulate

### Edge Cases
- None inputs for all optional parameters
- Empty list inputs for user/agent responses
- Missing required fields in TurnRound

## Dependencies

- `TurnRound` (from turn_parser.py)
- `TURN_SUMMARY_SCHEMA` (from config.py)
- `textwrap` (from standard library)

## Error Handling

### Input Errors
- Invalid `session_name` type
- Invalid `turn` structure
- Missing required fields in `turn`

### Integration Tests
- Integration with `parse_turn_summary()` and `process_turns_incrementally()`

---

## Expected Output Format

```python
Session name: session_abc123

[PREVIOUS TURN SUMMARY if previous_summary else '']

CURRENT ACCUMULATED STATE:
Session name: session_abc123
High-level goal: Build CLI tool
Key decisions: Use argparse
Constraints: Python 3.8+
All artifacts: main.py, config.py

CURRENT TURN (Turn 0):
User messages:
┃ Hi, please help me build a CLI tool.

Agent responses:
┃ I'll help you build a CLI tool.

[TURN SUMMARY_SCHEMA]
```

---

## Coverage Target

**Function**: `build_turn_prompt()`

**Lines**: 46-47 (estimated based on 20-30 lines of code)
**Target**: 100% test coverage

**Current Coverage**: Unknown (to be determined)

## Test Files

- `tests/test_turn_summarizer.py` (new file)
- `tests/test_turn_parser.py` (existing)
- `tests/test_config.py` (existing)
