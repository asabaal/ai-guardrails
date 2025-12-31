# opencode-restore

Parse and summarize OpenCode session logs for session restoration.

## Overview

`opencode-restore` is a command-line tool that parses raw OpenCode terminal log files (`.raw.log`) and generates structured session summaries using local LLMs (via Ollama). These summaries help you understand the state of an interrupted OpenCode session and pick up where you left off.

## Features

- **Raw Log Parsing**: Handles OpenCode's raw terminal logs with ANSI escape codes
- **Automatic Cleanup**: Strips ANSI codes and removes UI artifacts automatically
- **LLM Summarization**: Uses Ollama to generate intelligent session summaries
- **Flexible Output**: Supports Markdown and JSON output formats
- **Deduplication**: Option to remove consecutive duplicate lines from transcripts
- **Header Extraction**: Optionally includes script metadata (timestamp, working directory)

## Installation

### From Source

```bash
cd session_restore
pip install -e .
```

### After Installation

The `opencode-restore` command will be available globally:

```bash
opencode-restore --help
```

## Requirements

- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running
- At least one Ollama model installed (default: `gpt-oss20b`)

## Usage

### Basic Usage

```bash
opencode-restore session.raw.log
```

This will:
1. Parse `session.raw.log`
2. Strip ANSI codes and UI artifacts
3. Send the transcript to Ollama for summarization
4. Write the summary to `SUMMARY_session.md`

### With Custom Model

```bash
opencode-restore session.raw.log --model llama3
```

### With Custom Output File

```bash
opencode-restore session.raw.log --output my_summary.md
```

### With Transcript Limit

```bash
opencode-restore session.raw.log --max-lines 300
```

### With All Options

```bash
opencode-restore session.raw.log \
  --session-name "my-custom-session" \
  --model llama3 \
  --max-lines 500 \
  --format json \
  --dedupe \
  --include-header \
  --output custom_summary.json
```

## Command-Line Options

| Option | Description | Default |
|--------|-------------|----------|
| `log_file` | Path to OpenCode `.raw.log` file | (required) |
| `--session-name` | Logical session name | (filename stem) |
| `--model` | Ollama model to use | `gpt-oss20b` |
| `--max-lines` | Max transcript lines to include from tail | `600` |
| `--out` | Output file path | `SUMMARY_<session>.md` |
| `--format` | Output format (`md` or `json`) | `md` |
| `--dedupe` | Remove consecutive duplicate lines | `False` |
| `--include-header` | Include script header info in summary | `False` |

## Output Format

The generated summary follows a structured format:

### Markdown Output

```markdown
SESSION SUMMARY

Session name:
- <session name>

High-level goal:
- <bullet>

Primary task in progress:
- <bullet>

Key decisions already made:
- <bullet list>

Constraints and assumptions:
- <bullet list>

Artifacts referenced or created:
- <bullet list>

Open questions:
- <bullet list>

Next concrete steps:
- <bullet list>
```

### JSON Output

```json
{
  "session_name": "...",
  "high_level_goal": "...",
  "primary_task": "...",
  "key_decisions": [...],
  "constraints": [...],
  "artifacts": [...],
  "open_questions": [...],
  "next_steps": [...]
}
```

## Development

### Running Tests

```bash
cd session_restore
pip install -e ".[test]"
pytest
```

### Code Coverage

Tests are configured to require 100% coverage:

```bash
pytest --cov=src/opencode_restore --cov-fail-under=100
```

### Project Structure

```
session_restore/
├── src/
│   └── opencode_restore/
│       ├── __init__.py
│       ├── cli.py              # CLI entry point
│       ├── config.py           # Configuration constants
│       ├── parser.py           # Raw log parsing
│       └── summarizer.py      # LLM integration
├── tests/
│   ├── conftest.py          # Shared fixtures
│   ├── test_cli.py          # CLI tests
│   ├── test_config.py        # Config tests
│   ├── test_integration.py   # Integration/E2E tests
│   ├── test_parser.py        # Parser tests
│   └── test_summarizer.py   # Summarizer tests
├── pyproject.toml           # Modern packaging config
├── setup.py                 # Setuptools compatibility
└── README.md
```

## Environment Variables

- `OLLAMA_HOST`: Custom Ollama server URL (default: `http://localhost:11434`)

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please ensure all tests pass before submitting PRs.

```bash
pytest --cov=src/opencode_restore
```
