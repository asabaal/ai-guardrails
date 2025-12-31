# Turn-by-Turn Conversation Restoration - Implementation Plan

## Overview
Enhance `opencode-restore` to parse conversations by turn rounds, process incrementally, and enable agentic evidence gathering in final synthesis phase.

## Design Goals
1. Parse conversations into turn rounds (user request + agent response)
2. Process each turn incrementally with context from previous turns
3. Track artifacts (files edited/created/read) across session
4. Enable agentic evidence search in final phase
5. Maintain 100% test coverage

---

## Phase 1: Turn Parsing Infrastructure

### 1.1 New Module: `turn_parser.py`
**File**: `src/opencode_restore/turn_parser.py`

**Purpose**: Parse ANSI-stripped transcript into turn rounds with artifact tracking.

**Data Structures**:
```python
@dataclass
class ArtifactAction:
    file_path: str
    action_type: 'read' | 'edited' | 'created'
    line_number: int

@dataclass
class TurnRound:
    turn_number: int
    user_messages: List[str]
    agent_responses: List[str]
    raw_lines: List[str]
    start_line_index: int
    end_line_index: int
    artifacts: List[ArtifactAction]
```

**Turn Detection Logic**:
1. Detect user messages: `┃ <content> ┃` pattern followed by username + timestamp
2. Agent responses: All content between user messages
3. Group consecutive messages from same speaker into one turn round

**Artifact Extraction**:
- Pattern match for tool calls: `Read <path>`, `Edit <path>`, `Shell ...` output
- Extract file paths from command output, edit blocks, read operations

---

## Phase 2: Turn-by-Turn Summarizer

### 2.1 New Module: `turn_summarizer.py`
**File**: `src/opencode_restore/turn_summarizer.py`

**Purpose**: Process each turn incrementally, passing previous turn summary as context.

**Turn Summary Schema**:
```
TURN SUMMARY

Turn number: N
User request summary: <concise summary of what user asked>
Agent response summary: <what agent did/approached>
Key outcomes: <what was accomplished>
State changes: <what changed in overall session state>
Artifacts modified: <files touched in this turn>
Constraints/assumptions added: <new constraints from this turn>
Open questions after this turn: <unresolved issues>
```

**Processing Flow**:
1. Initialize empty accumulated state
2. For each turn:
   - Build prompt with: current turn, previous summary, accumulated state
   - Send to LLM for analysis
   - Extract state updates and artifacts
   - Accumulate state
3. Return all turn summaries + final accumulated state

---

## Phase 3: Agentic Evidence Search

### 3.1 New Module: `evidence_gatherer.py`
**File**: `src/opencode_restore/evidence_gatherer.py`

**Purpose**: Provide LLM with tools to search log and files for evidence.

**Search Tool Interface**:
```python
class EvidenceSearchTools:
    def search_log(self, pattern: str, context_lines: int = 3) -> str
    def search_file(self, file_path: str, pattern: str) -> str
    def read_file(self, file_path: str, line_range: Optional[Tuple] = None) -> str
    def list_artifacts(self) -> str
    def should_continue_search(self) -> bool
```

**Tool Call Format** (LLM outputs):
- `[SEARCH_LOG: "pattern"]` - Search raw log
- `[SEARCH_FILE: "path" "pattern"]` - Search specific file
- `[READ_FILE: "path"]` - Read file (full or with line range)
- `[LIST_ARTIFACTS]` - List all tracked artifacts
- `[COMPLETE_EVIDENCE_SEARCH]` - Signal completion

**Agentic Loop**:
1. Provide LLM with: turn summaries, accumulated state, available tools
2. LLM requests searches via tool call syntax
3. Execute searches, return results
4. LLM processes results, requests more searches or completes
5. Continue until `[COMPLETE_EVIDENCE_SEARCH]` or max iterations (default: 8)

---

## Phase 4: Final Aggregation

### 4.1 CLI Workflow Update
**File**: `src/opencode_restore/cli.py`

**New Flow**:
1. Parse raw log into clean transcript
2. Parse transcript into turn rounds with artifact tracking
3. Process turns incrementally (each with previous context)
4. Run agentic evidence gathering
5. Synthesize final SESSION SUMMARY from all evidence

---

## Phase 5: Configuration

### 5.1 New Constants in `config.py`
**File**: `src/opencode_restore/config.py`

```python
# Turn detection patterns
USER_MESSAGE_PATTERN = r'┃\s+(.+?)\s+┃'
USERNAME_TIMESTAMP_PATTERN = r'(\w+)\s+\(\d{1,2}:\d{2}\s+[AP]M\)'
AGENT_WORKING_PATTERN = r'[Gg]enerating'

# Tool patterns for artifact extraction
READ_FILE_PATTERN = r'Read\s+(\S+)'
EDIT_FILE_PATTERN = r'Edit\s+(\S+)'

# Agentic search limits
MAX_EVIDENCE_SEARCHES = 8
SEARCH_CONTEXT_LINES = 3
SEARCH_PATTERN_MAX_LENGTH = 200

# Turn summary schema
TURN_SUMMARY_SCHEMA = """..."""
EVIDENCE_SEARCH_PROMPT_TEMPLATE = """..."""
```

---

## Phase 6: Testing

### 6.1 Test Files
- `tests/test_turn_parser.py` - Turn detection and artifact extraction
- `tests/test_turn_summarizer.py` - Turn processing with context
- `tests/test_evidence_gatherer.py` - Search tools and agentic loop

### 6.2 Test Fixtures
- Sample logs with:
  - Single user message + agent response
  - Multiple user messages before agent responds
  - Agent responses with multiple tool calls
  - Files edited, read, created

---

## CLI Flags (New)

```python
--max-turns N          Limit number of turns to process
--skip-evidence-search  Skip agentic evidence gathering phase
--max-searches N       Max evidence search iterations (default: 8)
--dump-turns           Output turn-by-turn summaries instead of aggregated
```

---

## Module Dependencies
```
parser.py → turn_parser.py
parser.py → turn_summarizer.py (uses LogParser)
turn_summarizer.py → evidence_gatherer.py (uses search tools)
cli.py → turn_parser.py, turn_summarizer.py, evidence_gatherer.py
```

---

## Error Handling Strategy

1. **Turn parsing failure**: Log error, continue with remaining turns
2. **Turn summarization failure**: Skip turn, use previous state
3. **Evidence search failure**: Log tool errors, continue loop
4. **Max searches without completion**: Force complete with gathered evidence

---

## Implementation Order
1. `config.py` - Add new constants
2. `turn_parser.py` - New module + tests
3. `turn_summarizer.py` - New module + tests
4. `evidence_gatherer.py` - New module + tests
5. `cli.py` - Update workflow
6. Integration tests
7. Verify 100% coverage
