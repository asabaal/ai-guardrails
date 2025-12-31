# build_turn_prompt() - 100% Test Coverage Specification

## Overview

The `build_turn_prompt()` function constructs prompts for LLM to summarize individual conversation turns. It includes previous turn context and accumulated session state.

## Purpose

1. **Turn-Level Context**: Pass previous turn summary to next turn for continuity
2. **Accumulated State**: Maintain session state (high-level goal, key decisions, constraints, artifacts, open questions) across all turns
3. **Truncation**: Limit agent responses to 10 lines max

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
|----------|------|------------|
| `session_name` | str | Name of the session being restored |
| `turn` | TurnRound | Current turn to summarize |
| `previous_summary` | Optional[Dict] | Previous turn's summary |
| `accumulated_state` | Optional[Dict] | Accumulated session state |

---

## Returns

**Type**: str - Formatted prompt ready for LLM

## Coverage Target

**Target**: 100% line coverage on `build_turn_prompt()`

## Implementation Requirements

### High Priority
1. Test all possible code paths through:
   - Previous summary: Provided vs None
   - Agent response length: <10 vs >10
   - Artifacts: None vs populated list
   - Constraints: None vs populated list
   - Open questions: None vs populated list
   - High-level goal: Established vs "Not established yet"

### Medium Priority
2. Test accumulated state management:
   - Initial state initialization
   - Adding artifacts to set()
   - Accumulating key decisions
   - Extending constraints list
   - Accumulating open questions

### Low Priority
3. Test state updates
   - `state_updates` dictionary updates
   - `state_updates['constraints']` list

---

## Test Coverage Strategy

### Test 1: Empty inputs
- **Input**: `turn=None`, `previous_summary=None`, `accumulated_state=None`
- **Expected**: Returns prompt without previous context
- **Coverage**: Lines 1-27 (initial build)

### Test 2: Previous summary only
- **Input**: `previous_summary=summary_dict`
- **Expected**: Prompt includes "PREVIOUS TURN SUMMARY" with previous turn details
- **Coverage**: Lines 28-65 (includes previous context)

### Test 3: Accumulated state only
- **Input**: `accumulated_state={...state...}`
- **Expected**: Prompt includes accumulated state section
- **Coverage**: Lines 66-102 (includes all state sections)

### Test 4: Agent response truncation
- **Input**: `turn.agent_responses` with 15 lines
- **Expected**: Agent responses truncated to 10 lines
- **Coverage**: Lines 103-140 (includes truncation logic)

### Test 5: Artifacts
- **Input**: `summary['artifacts_modified']=['file1.py', 'file2.py']`
- **Expected**: Artifacts accumulated in `accumulated_state['artifacts']`
- **Coverage**: Lines 145-180 (accumulates artifacts)

### Test 6: Constraints
- **Input**: `summary['constraints_added']=['must use Python 3.8+']`
- **Expected**: Constraints added to `accumulated_state['constraints']`
- **Coverage**: Lines 181-220 (extends constraints)

### Test 7: Open questions
- **Input**: `summary['open_questions']=['What about tests?']`
- **Expected**: Questions added to `accumulated_state['open_questions']`
- **Coverage**: Lines 221-240 (adds questions)

### Test 8: Full state with all fields
- **Input**: All fields populated
- **Expected**: Full prompt with all sections
- **Coverage**: Lines 222-270 (complete prompt)

### Test 9: High-level goal
- **Input**: `accumulated_state={'high_level_goal': 'Build CLI tool'}`
- **Expected**: High-level goal in prompt
- **Coverage**: Lines 224-240 (includes high-level goal)

### Test 10: Turn number
- **Input**: `turn.turn_number=5`
- **Expected**: Turn number in prompt
- **Coverage**: Lines 224-250 (includes turn number)

---

## Code Structure

### Required Imports

```python
from .config import TURN_SUMMARY_SCHEMA
from .turn_parser import TurnRound
from typing import Dict, List, Optional
import textwrap
```

### Function Layout

```python
def build_turn_prompt(
    session_name: str,
    turn: TurnRound,
    previous_summary: Optional[Dict] = None,
    accumulated_state: Optional[Dict] = None,
) -> str
    """
    Build prompt for single turn processing with context.
    """
```

---

## Dependencies

### Internal (from project)
- `.config.TURN_SUMMARY_SCHEMA` - Turn summary schema template
- `.turn_parser.Turn_parser.py` - TurnRound class
- `.turn_parser.turn_parser.py` - TurnParser class

### External (from standard library)
- `typing` - Type hints
- `textwrap` - Text formatting
- `unittest.mock` - For testing

---

## Usage Example

```python
from opencode_restore.turn_parser import TurnParser
from opencode_restore.turn_summarizer import build_turn_prompt

# Parse conversation
parser = TurnParser()
turns = parser.parse_turns(open('session.raw.log'))

# Build prompt for first turn
prompt = build_turn_prompt(
    session_name='test_session',
    turn=turns[0],
    previous_summary=None,
    accumulated_state=None,
)

print(prompt)
```

---

## Test Requirements

### Test Categories

| Category | Description | Coverage Goal |
|---------|-------------|-----------|---------|
| **Previous Summary Handling** | Previous summary None vs provided | Lines 1-27 |
| **State Accumulation** | All state types updated correctly | Lines 66-102 |
| **Response Truncation** | Responses > 10 lines truncated to 10 | Lines 103-140 |
| **Artifact Accumulation** | Artifacts added to set | Lines 145-180 |
| **Constraint Accumulation** | Constraints added to list | Lines 181-220 |
| **Question Accumulation** | Questions added to list | Lines 221-240 |
| **Full Prompt Building** | All sections included | Lines 222-270 |

---

## Metrics

### Complexity: Medium

### Lines of Code: ~270

### Branches:
- 1 main `if/elif` chain (previous_summary handling)
- 1 `if/elif` chain (parsing each key)
- 6 `if/elif` chains (parsing each key)
- 1 `while` loop (artifact list continuation)
- 1 `for` loop (multi-line artifact list)
- 1 `if` statement (constraint accumulation)

### Cyclomatic Complexity: 4

---

## Known Issues

### Current State

- `accumulated_state` initialization issues
- Multi-line bullet list handling edge cases
- Response truncation logic
- Constraint accumulation bug

### Testing Gaps

1. **No integration tests for `build_turn_prompt()`**
2. **Mock backend issues in test_cli.py** (5 tests failing)
3. **Version mismatch** in `test_integration.py`
4. **Ollama dependency** in `test_integration_e2e.py`

---

## Plan

1. Create `tests/test_build_turn_prompt.py` - New test file with 100% coverage
2. Add imports and fixtures
3. Test all 8 categories above
4. Mock backend with realistic responses
5. Validate prompt format matches TURN_SUMMARY_SCHEMA exactly

---

## Success Criteria

- All tests pass
- 100% coverage on `build_turn_prompt()`
- No `test_cli.py` mock errors
- `test_integration.py` version matches
- `test_integration_e2e.py` handles Ollama dependency

---

**Ready for implementation when you authorize.**</think><tool_call>write<arg_key>content</arg_key><arg_value># build_turn_prompt() - 100% Test Coverage Specification

## Overview

The `build_turn_prompt()` function constructs prompts for LLM to summarize individual conversation turns. It includes previous turn context and accumulated session state.

## Purpose

1. **Turn-Level Context**: Pass previous turn summary to next turn for continuity
2. **Accumulated State**: Maintain session state (high-level goal, key decisions, constraints, artifacts, open questions) across all turns
3. **Truncation**: Limit agent responses to 10 lines max

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
|----------|------|------------|
| `session_name` | str | Name of the session being restored |
| `turn` | TurnRound | Current turn to summarize |
| `previous_summary` | Optional[Dict] | Previous turn's summary |
| `accumulated_state` | Optional[Dict] | Current accumulated session state |

---

## Returns

**Type**: str - Formatted prompt ready for LLM

## Coverage Target

**Target**: 100% line coverage on `build_turn_prompt()`

## Implementation Requirements

### High Priority
1. Test all possible code paths through:
   - Previous summary: Provided vs None
   - Agent response length: <10 vs >10
   - Artifacts: None vs populated list
   - Constraints: None vs populated list
   - Open questions: None vs populated list
   - High-level goal: Established vs "Not established yet"
   - State updates: state_updates['constraints'] dictionary

### Medium Priority
2. Test accumulated state management:
   - Initial state initialization
   - Adding artifacts to set()
   - Accumulating key decisions
   - Extending constraints list
   - Accumulating open questions

### Low Priority
3. Test state updates
   - `state_updates['constraints']` dictionary updates

---

## Test Coverage Strategy

### Test 1: Empty inputs
- **Input**: `turn=None`, `previous_summary=None`, `accumulated_state=None`
- **Expected**: Returns prompt without previous context
- **Coverage**: Lines 1-27 (initial build)
- **Test Cases**: 4 test scenarios

### Test 2: Previous summary only
- **Input**: `previous_summary={'turn_number': '0', ...}`
- **Expected**: Prompt includes "PREVIOUS TURN SUMMARY" with previous turn details
- **Coverage**: Lines 28-65 (includes previous context)

### Test 3: Accumulated state only
- **Input**: `accumulated_state={'high_level_goal': 'Build CLI tool', ...}`
- **Expected**: Prompt includes accumulated state section
- **Coverage**: Lines 66-102 (includes all state sections)

### Test 4: Agent response truncation
- **Input**: `turn.agent_responses = [f"Line {i}" for i in range(15)]`
- **Expected**: Agent responses truncated to 10 lines
- **Coverage**: Lines 103-140 (includes truncation logic)

### Test 5: Artifacts
- **Input**: `summary['artifacts_modified']=['file1.py', 'file2.py']`
- **Expected**: Artifacts accumulated in `accumulated_state['artifacts']`
- **Coverage**: Lines 145-180 (accumulates artifacts)

### Test 6: Constraints
- **Input**: `summary['constraints_added']=['must use Python 3.8+']`
- **Expected**: Constraints added to `accumulated_state['constraints']`
- **Coverage**: Lines 181-220 (extends constraints)

### Test 7: Open questions
- **Input**: `summary['open_questions']=['What about tests?']`
- **Expected**: Questions added to `accumulated_state['open_questions']`
- **Coverage**: Lines 221-240 (adds questions)

### Test 8: Full state with all fields
- **Input**: All fields populated
- **Expected**: Full prompt with all sections
- **Coverage**: Lines 222-270 (complete prompt)

### Test 9: High-level goal
- **Input**: `accumulated_state={'high_level_goal': 'Build CLI tool'}`
- **Expected**: High-level goal in prompt
- **Coverage**: Lines 224-250 (includes high-level goal)

---

## Code Structure

### Required Imports

```python
from .config import TURN_SUMMARY_SCHEMA
from .turn_parser import TurnRound
from typing import Dict, List, Optional
import textwrap
```

### Function Layout

```python
def build_turn_prompt(
    session_name: str,
    turn: TurnRound,
    previous_summary: Optional[Dict] = None,
    accumulated_state: Optional[Dict] = None,
) -> str:
    """
    Build prompt for single turn processing with context.
    """
```

---

## Dependencies

### Internal (from project)
- `.config.TURN_SUMMARY_SCHEMA` - Turn summary schema template
- `.turn_parser.turn_parser.py` - TurnRound class
- `.turn_parser.turn_parser.py` - TurnParser class

### External (from standard library)
- `typing` - Type hints
- `textwrap` - Text formatting
- `unittest.mock` - For testing

---

## Usage Example

```python
from opencode_restore.turn_parser import TurnParser
from opencode_restore.turn_summarizer import build_turn_prompt

# Parse conversation
parser = TurnParser()
turns = parser.parse_turns(open('session.raw.log'))

# Build prompt for first turn
prompt = build_turn_prompt(
    session_name='test_session',
    turn=turns[0],
    previous_summary=None,
    accumulated_state=None,
)

print(prompt)
```

---

## Test Requirements

### Test Categories

| Category | Description | Coverage Goal |
|---------|-------------|-----------|---------|
| **Previous Summary Handling** | Previous summary None vs provided | Lines 1-27 |
| **State Accumulation** | All state types updated correctly | Lines 66-102 |
| **Response Truncation** | Responses > 10 lines truncated to 10 | Lines 103-140 |
| **Artifact Accumulation** | Artifacts added to set | Lines 145-180 |
| **Constraint Accumulation** | Constraints added to list | Lines 181-220 |
| **Question Accumulation** | Questions added to list | Lines 221-240 |

### Test 9: Full state with all fields
- **Input**: All fields populated
- **Expected**: Full prompt with all sections
- **Coverage**: Lines 222-270 (complete prompt)

### Test 10: High-level goal
- **Input**: `accumulated_state={'high_level_goal': 'Build CLI tool'}`
- **Expected**: High-level goal in prompt
- **Coverage**: Lines 224-250 (includes high-level goal)

---

## Metrics

### Complexity: Medium

### Lines of Code: ~270

### Branches:
- 1 main `if/elif` chain (previous_summary handling)
- 1 `if/elif` chain (parsing each key)
- 6 `if/elif` chains (parsing each key)
- 1 `while` loop (artifact list continuation)
- 1 `for` loop (multi-line artifact list)
- 1 `if` statement (constraint accumulation)

### Cyclomatic Complexity: 4

---

## Known Issues

### Current State

- `accumulated_state` initialization issues
- Multi-line bullet list handling edge cases
- Response truncation logic
- Constraint accumulation bug

### Testing Gaps

1. **No integration tests for `build_turn_prompt()`**
2. **Mock backend issues in test_cli.py** (5 tests failing)
3. **Version mismatch** in `test_integration.py`
4. **Ollama dependency** in `test_integration_e2e.py`

---

## Plan

1. Create `tests/test_build_turn_prompt.py` - New test file with 100% coverage
2. Add imports and fixtures
3. Test all 8 categories above
4. Mock backend with realistic responses
5. Validate prompt format matches TURN_SUMMARY_SCHEMA exactly

---

## Success Criteria

- All tests pass
- 100% coverage on `build_turn_prompt()`
- No `test_cli.py` mock errors
- `test_integration.py` version matches
- `test_integration_e2e.py` handles Ollama dependency

---

**Ready for implementation when you authorize.**