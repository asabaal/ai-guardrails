# Test Fixing Plan for session_restore

## Executive Summary
- **Total Tests**: 156
- **Failed Tests**: 31
- **Current Coverage**: 91% (48 missing lines)
- **Target Coverage**: 100%

## Categories of Failures

### 1. CLI Tests (6 tests failing)
**Error**: "expected string or bytes-like object, got 'MagicMock'"
**Root Cause**: Tests mock `backend.summarize` but code calls `backend.generate`
**Affected Tests**:
- `test_main_success`
- `test_main_with_session_name`
- `test_main_with_custom_output`
- `test_main_with_dedupe`
- `test_main_with_include_header`
- `test_main_with_max_lines`

**Fix**: Update CLI tests to set `mock_summarizer_obj.backend.generate.return_value` instead of `summarize`

### 2. Evidence Gatherer Tests (10 tests failing)

#### a. Tool Call Extraction (4 tests)
**Tests**: `test_extract_search_log`, `test_extract_search_file`, `test_extract_read_file`, `test_extract_read_file_with_range`
**Root Cause**: `extract_tool_calls` function has bugs in argument extraction
- For `SEARCH_FILE`: extracting wrong tuple index
- For `READ_FILE`: not capturing line range groups correctly
- `raw` field not returning complete tool call string

**File**: `session_restore/src/opencode_restore/evidence_gatherer.py:179-201`

**Fix**: Correct regex match group extraction logic

#### b. Template Issues (1 test)
**Test**: `test_build_prompt_with_turns`
**Root Cause**: `EVIDENCE_SEARCH_PROMPT_TEMPLATE` doesn't include `session_name` placeholder
**File**: `session_restore/src/opencode_restore/config.py:77-103`

**Fix**: Add `{session_name}` to template and update formatting call

#### c. Call Count Issue (1 test)
**Test**: `test_immediate_completion`
**Root Cause**: Function calls `backend.generate()` twice (once at line 306, once at line 369)
**Expected Behavior**: First call for search, second for final summary
**Fix**: Update test expectation or clarify function behavior

#### d. Final Summary Text Missing (2 tests)
**Tests**: `test_searches_with_completions`, `test_empty_turn_summaries`
**Root Cause**: "FINAL SESSION SUMMARY" text not being included properly
**File**: `session_restore/src/opencode_restore/evidence_gatherer.py:334-367`

**Fix**: Ensure final prompt includes "FINAL SESSION SUMMARY"

#### e. StopIteration (1 test)
**Test**: `test_max_searches_without_completion`
**Root Cause**: side_effect list has 9 items but max_searches is 8
**Fix**: Test needs more responses or function needs better handling

### 3. Integration Tests (5 tests failing)

#### a. Version Mismatch (1 test)
**Test**: `test_version_attribute`
**Root Cause**: Version is "2.0.0" but test expects "1.0.0"
**File**: `session_restore/tests/test_integration.py:222`

**Fix**: Update test to expect "2.0.0"

#### b. Wrong Backend Method (1 test)
**Test**: `test_turns_with_accumulated_state_are_processed`
**Root Cause**: Test mocks `summarize` but code calls `generate`
**File**: `session_restore/tests/test_integration_e2e.py:64`

**Fix**: Change `mock_backend.summarize` to `mock_backend.generate`

#### c. CLI Integration (2 tests)
**Tests**: `test_cli_full_workflow`, `test_cli_integration`
**Root Cause**: Subprocess returns non-zero exit code
**Fix**: Add `--skip-evidence-search` flag or mock Ollama

#### d. Help Test (1 test)
**Test**: `test_cli_help`
**Root Cause**: Empty stdout from subprocess
**Fix**: Verify help output path

### 4. Parser Tests (2 tests failing)

**Tests**: `test_strip_ansi_cursor_movement`, `test_is_ui_artifact_cursor_sequences`
**Root Cause**: `ANSI_ESCAPE_PATTERN` doesn't match cursor sequences like `\x1b[?25l`
**File**: `session_restore/src/opencode_restore/config.py:15`

**Fix**: Update pattern to include cursor show/hide sequences

### 5. Turn Parser Tests (4 tests failing)

**Test**: `test_parse_single_turn`
**Root Cause**: Expecting 3 agent responses but getting 4 (includes "Read src/main.py")

**Test**: `test_parse_consecutive_user_messages`
**Root Cause**: Getting 3 turns instead of 1 (should group consecutive user messages)

**Test**: `test_extract_multiple_artifacts`
**Root Cause**: Extracting 3 artifacts instead of 1 (scanning outside turn bounds)

**Test**: `test_agent_working_not_in_responses`
**Root Cause**: "nerating..." still in responses (filter not working)
**File**: `session_restore/src/opencode_restore/turn_parser.py:97-149`

**Fix**:
- Group consecutive user messages into one turn
- Filter out all agent working lines thoroughly
- Limit artifact extraction to turn bounds

### 6. Turn Summarizer Tests (4 tests failing)

**Tests**: `test_build_prompt_with_previous_summary`
**Root Cause**: `session_name` not included in prompt
**File**: `session_restore/src/opencode_restore/turn_summarizer.py:14-74`

**Fix**: Add session_name to prompt template

**Tests**: `test_parse_summary_with_multiline_bullets`, `test_extract_multiline_bullets`
**Root Cause**: Multiline bullets not being concatenated correctly
**File**: `session_restore/src/opencode_restore/turn_summarizer.py:125-136`

**Fix**: Fix `_extract_bullet_list` to handle continuation lines

**Tests**: `test_process_single_turn`, `test_process_multiple_turns_accumulates_state`
**Root Cause**: Constraints not being added to accumulated_state
**File**: `session_restore/src/opencode_restore/turn_summarizer.py:139-181`

**Fix**: Ensure constraints are accumulated properly

## Coverage Gaps (48 lines)

### CLI Module (32 lines uncovered)
- Lines 157-159: `dump_turns_to_file` function
- Lines 170: `max_searches` assignment
- Lines 180-211: Evidence search skip path
- Lines 227-243: `synthesize_summary_from_accumulated_state` function
- Lines 249-262: Various branches in summary synthesis

### Evidence Gatherer Module (13 lines uncovered)
- Line 69: Invalid regex pattern handling
- Lines 73-74, 78-79: File read error handling
- Line 91: Pattern too long error handling
- Line 193: Search tool error handling
- Lines 226-227: Execution error handling
- Line 324: Search iteration handling

### Turn Parser Module (1 line uncovered)
- Line 90: Edge case in artifact extraction

### Turn Summarizer Module (2 lines uncovered)
- Lines 133-134: Bullet list concatenation edge cases

## Implementation Phases

### Phase 1: Evidence Gatherer (Foundation)
Priority: HIGH - breaks many other tests

1. Fix `extract_tool_calls` function
2. Update `EVIDENCE_SEARCH_PROMPT_TEMPLATE`
3. Update `EVIDENCE_SEARCH_CONTINUE_PROMPT_TEMPLATE`
4. Fix `run_agentic_evidence_gathering`

### Phase 2: Parser
Priority: MEDIUM - fixes 2 tests

5. Update `ANSI_ESCAPE_PATTERN`

### Phase 3: Turn Parser
Priority: MEDIUM - fixes 4 tests

6. Fix `parse_turns` method
7. Fix artifact extraction bounds

### Phase 4: Turn Summarizer
Priority: MEDIUM - fixes 4 tests

8. Fix `_extract_bullet_list`
9. Fix `build_turn_prompt`
10. Fix state accumulation

### Phase 5: Integration Tests
Priority: MEDIUM - fixes 5 tests

11. Fix `test_version_attribute`
12. Fix `test_turns_with_accumulated_state_are_processed`
13. Fix CLI integration tests

### Phase 6: Coverage
Priority: LOW - improves coverage

14. Add tests for uncovered CLI branches
15. Add tests for error handling paths
16. Ensure all edge cases covered

## Success Criteria
- All 31 failing tests pass
- Coverage reaches 100%
- No regression in existing passing tests
