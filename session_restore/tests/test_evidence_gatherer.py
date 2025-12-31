"""
Tests for evidence_gatherer module.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock

from opencode_restore.evidence_gatherer import (
    EvidenceSearchTools,
    extract_tool_calls,
    execute_tool_calls,
    build_evidence_search_prompt,
    build_continuation_prompt,
    run_agentic_evidence_gathering,
)


@pytest.fixture
def sample_log_file(tmp_path):
    """Create a sample log file for testing."""
    log_file = tmp_path / "test.raw.log"
    log_file.write_text(
        "User message\n"
        "Read src/main.py\n"
        "Edit config.yaml\n"
        "Shell cd /home/user\n"
        "def main():\n"
        "    return 42\n"
        "Read tests/test_file.py\n"
    )
    return log_file


@pytest.fixture
def sample_turn_summaries():
    """Sample turn summaries for testing."""
    return [
        {
            'turn_number': '0',
            'user_request_summary': 'Fix bug',
            'agent_response_summary': 'Analyzed file',
            'key_outcomes': 'Found issue',
            'state_changes': 'Bug in line 42',
            'artifacts_modified': ['file1.py'],
            'constraints_added': ['Use Python 3.8+'],
            'open_questions': [],
            'state_updates': {},
        },
        {
            'turn_number': '1',
            'user_request_summary': 'Add tests',
            'agent_response_summary': 'Created tests',
            'key_outcomes': 'Tests added',
            'state_changes': 'Coverage improved',
            'artifacts_modified': ['test_file.py'],
            'constraints_added': [],
            'open_questions': ['Need more edge cases'],
            'state_updates': {},
        },
    ]


@pytest.fixture
def sample_accumulated_state():
    """Sample accumulated state for testing."""
    return {
        'high_level_goal': 'Debug module forge',
        'key_decisions': ['Found bug in line 42', 'Need refactoring'],
        'constraints': ['Use Python 3.8+', 'Maintain backwards compatibility'],
        'artifacts': {'file1.py', 'file2.py', 'test_file.py', 'config.yaml'},
        'open_questions': ['How to handle edge cases?'],
    }


class TestEvidenceSearchTools:
    def test_search_log_finds_matches(self, sample_log_file, tmp_path):
        tools = EvidenceSearchTools(
            log_path=sample_log_file,
            repo_root=tmp_path,
            artifacts={'file1.py', 'file2.py'},
        )

        result = tools.search_log("Read")

        assert "Found 2 matches" in result
        assert "Read src/main.py" in result
        assert "Read tests/test_file.py" in result

    def test_search_log_no_matches(self, sample_log_file, tmp_path):
        tools = EvidenceSearchTools(
            log_path=sample_log_file,
            repo_root=tmp_path,
            artifacts=set(),
        )

        result = tools.search_log("NonExistentPatternXYZ123")

        assert "No matches found" in result

    def test_search_log_invalid_regex(self, sample_log_file, tmp_path):
        tools = EvidenceSearchTools(
            log_path=sample_log_file,
            repo_root=tmp_path,
            artifacts=set(),
        )

        result = tools.search_log("[Invalid[Regex")

        assert "Error: Invalid regex pattern" in result

    def test_search_log_pattern_too_long(self, sample_log_file, tmp_path):
        tools = EvidenceSearchTools(
            log_path=sample_log_file,
            repo_root=tmp_path,
            artifacts=set(),
        )

        long_pattern = "a" * 300
        result = tools.search_log(long_pattern)

        assert "Error: Search pattern too long" in result

    def test_search_file_finds_matches(self, tmp_path):
        test_file = tmp_path / "test.py"
        test_file.write_text("class User:\n    pass\n\nclass Admin:\n    pass\n")

        log_file = tmp_path / "dummy.log"
        log_file.write_text("Dummy log")

        tools = EvidenceSearchTools(
            log_path=log_file,
            repo_root=tmp_path,
            artifacts={'test.py'},
        )

        result = tools.search_file("test.py", "class")

        assert "Found 2 matches in test.py" in result
        assert "class User" in result
        assert "class Admin" in result

    def test_search_file_not_found(self, tmp_path):
        log_file = tmp_path / "dummy.log"
        log_file.write_text("Dummy")

        tools = EvidenceSearchTools(
            log_path=log_file,
            repo_root=tmp_path,
            artifacts=set(),
        )

        result = tools.search_file("nonexistent.py", "pattern")

        assert "Error: File not found" in result

    def test_read_file_full(self, tmp_path):
        test_file = tmp_path / "test.py"
        test_file.write_text("line1\nline2\nline3\n")

        log_file = tmp_path / "dummy.log"
        log_file.write_text("Dummy")

        tools = EvidenceSearchTools(
            log_path=log_file,
            repo_root=tmp_path,
            artifacts={'test.py'},
        )

        result = tools.read_file("test.py")

        assert "File test.py (3 lines):" in result
        assert "line1" in result
        assert "line2" in result
        assert "line3" in result

    def test_read_file_with_range(self, tmp_path):
        test_file = tmp_path / "test.py"
        test_file.write_text("line1\nline2\nline3\nline4\nline5\n")

        log_file = tmp_path / "dummy.log"
        log_file.write_text("Dummy")

        tools = EvidenceSearchTools(
            log_path=log_file,
            repo_root=tmp_path,
            artifacts={'test.py'},
        )

        result = tools.read_file("test.py", "(2-4)")

        assert "File test.py lines 2-4:" in result
        assert "line2" in result
        assert "line3" in result
        assert "line4" in result
        assert "line1" not in result
        assert "line5" not in result

    def test_read_file_truncates_long_file(self, tmp_path):
        test_file = tmp_path / "test.py"
        test_file.write_text("\n".join(f"line {i}" for i in range(300)))

        log_file = tmp_path / "dummy.log"
        log_file.write_text("Dummy")

        tools = EvidenceSearchTools(
            log_path=log_file,
            repo_root=tmp_path,
            artifacts={'test.py'},
        )

        result = tools.read_file("test.py")

        assert "File test.py (300 lines):" in result
        assert "First 200 lines:" in result
        assert "line 1" in result
        assert "line 199" in result
        assert "line 0" in result
        assert "line 200" not in result
        assert "line 201" not in result

    def test_read_file_invalid_range(self, tmp_path):
        test_file = tmp_path / "test.py"
        test_file.write_text("line1\nline2\nline3\n")

        log_file = tmp_path / "dummy.log"
        log_file.write_text("Dummy")

        tools = EvidenceSearchTools(
            log_path=log_file,
            repo_root=tmp_path,
            artifacts={'test.py'},
        )

        result = tools.read_file("test.py", "(5-10)")

        assert "Error: Line 4 is beyond file length (3)" in result

    def test_read_file_invalid_format(self, tmp_path):
        test_file = tmp_path / "test.py"
        test_file.write_text("line1\nline2\nline3\n")

        log_file = tmp_path / "dummy.log"
        log_file.write_text("Dummy")

        tools = EvidenceSearchTools(
            log_path=log_file,
            repo_root=tmp_path,
            artifacts={'test.py'},
        )

        result = tools.read_file("test.py", "invalid")

        assert "Error: Invalid line range format" in result

    def test_list_artifacts(self, tmp_path):
        log_file = tmp_path / "dummy.log"
        log_file.write_text("Dummy")

        tools = EvidenceSearchTools(
            log_path=log_file,
            repo_root=tmp_path,
            artifacts={'file1.py', 'file2.py', 'test_file.py'},
        )

        result = tools.list_artifacts()

        assert "Artifacts tracked (3 files):" in result
        assert "  - file1.py" in result
        assert "  - file2.py" in result
        assert "  - test_file.py" in result

    def test_list_artifacts_empty(self, tmp_path):
        log_file = tmp_path / "dummy.log"
        log_file.write_text("Dummy")

        tools = EvidenceSearchTools(
            log_path=log_file,
            repo_root=tmp_path,
            artifacts=set(),
        )

        result = tools.list_artifacts()

        assert "No artifacts tracked" in result

    def test_should_continue_search(self, tmp_path):
        log_file = tmp_path / "dummy.log"
        log_file.write_text("Dummy")

        tools = EvidenceSearchTools(
            log_path=log_file,
            repo_root=tmp_path,
            artifacts=set(),
        )

        assert tools.should_continue_search() == True

        for i in range(8):
            tools.increment_search_count()
            expected = i < 7
            assert tools.should_continue_search() == expected

    def test_get_tool_descriptions(self, tmp_path):
        log_file = tmp_path / "dummy.log"
        log_file.write_text("Dummy")

        tools = EvidenceSearchTools(
            log_path=log_file,
            repo_root=tmp_path,
            artifacts=set(),
        )

        desc = tools.get_tool_descriptions()

        assert "SEARCH_LOG" in desc
        assert "SEARCH_FILE" in desc
        assert "READ_FILE" in desc
        assert "LIST_ARTIFACTS" in desc
        assert "COMPLETE_EVIDENCE_SEARCH" in desc


class TestExtractToolCalls:
    def test_extract_search_log(self):
        response = "I need to search for the error. [SEARCH_LOG: \"Traceback\"] Let me check."

        calls = extract_tool_calls(response)

        assert len(calls) == 1
        assert calls[0]['tool'] == 'search_log'
        assert calls[0]['args'] == ['Traceback']
        assert calls[0]['raw'] == '[SEARCH_LOG: "Traceback"]'

    def test_extract_search_file(self):
        response = "[SEARCH_FILE: \"src/main.py\" \"class User\"]"

        calls = extract_tool_calls(response)

        assert len(calls) == 1
        assert calls[0]['tool'] == 'search_file'
        assert calls[0]['args'] == ['src/main.py', 'class User']

    def test_extract_read_file(self):
        response = "[READ_FILE: \"config.yaml\"]"

        calls = extract_tool_calls(response)

        assert len(calls) == 1
        assert calls[0]['tool'] == 'read_file'
        assert calls[0]['args'] == ['config.yaml']

    def test_extract_read_file_with_range(self):
        response = "[READ_FILE: \"src/main.py\" (10-20)]"

        calls = extract_tool_calls(response)

        assert len(calls) == 1
        assert calls[0]['tool'] == 'read_file'
        assert len(calls[0]['args']) == 3
        assert calls[0]['args'][0] == 'src/main.py'
        assert calls[0]['args'][1] == '10'
        assert calls[0]['args'][2] == '20'

    def test_extract_list_artifacts(self):
        response = "[LIST_ARTIFACTS] Let me see what files we have."

        calls = extract_tool_calls(response)

        assert len(calls) == 1
        assert calls[0]['tool'] == 'list_artifacts'

    def test_extract_multiple_tool_calls(self):
        response = """
        [SEARCH_LOG: "error"]
        [READ_FILE: "main.py"]
        [LIST_ARTIFACTS]
        """

        calls = extract_tool_calls(response)

        assert len(calls) == 3
        tool_names = [c['tool'] for c in calls]
        assert 'search_log' in tool_names
        assert 'read_file' in tool_names
        assert 'list_artifacts' in tool_names

    def test_extract_no_tool_calls(self):
        response = "I need to search for evidence. Let me look at the logs."

        calls = extract_tool_calls(response)

        assert calls == []


class TestExecuteToolCalls:
    def test_execute_search_log(self, tmp_path):
        log_file = tmp_path / "test.log"
        log_file.write_text("Line 1: pattern here\nLine 2: pattern again\n")

        tools = EvidenceSearchTools(
            log_path=log_file,
            repo_root=tmp_path,
            artifacts=set(),
        )

        calls = [{'tool': 'search_log', 'args': ['pattern'], 'raw': '[SEARCH_LOG: "pattern"]'}]

        results = execute_tool_calls(calls, tools)

        assert len(results) == 1
        assert "SEARCH_LOG" in results[0]
        assert "Found 2 matches" in results[0]

    def test_execute_search_file(self, tmp_path):
        test_file = tmp_path / "test.py"
        test_file.write_text("User\nAdmin\n")

        log_file = tmp_path / "test.log"
        log_file.write_text("dummy")

        tools = EvidenceSearchTools(
            log_path=log_file,
            repo_root=tmp_path,
            artifacts=set(),
        )

        calls = [{'tool': 'search_file', 'args': ['test.py', 'User'], 'raw': '[SEARCH_FILE: "test.py" "User"]'}]

        results = execute_tool_calls(calls, tools)

        assert len(results) == 1
        assert "Found 1 matches in test.py" in results[0]

    def test_execute_read_file(self, tmp_path):
        test_file = tmp_path / "test.py"
        test_file.write_text("content")

        log_file = tmp_path / "test.log"
        log_file.write_text("dummy")

        tools = EvidenceSearchTools(
            log_path=log_file,
            repo_root=tmp_path,
            artifacts=set(),
        )

        calls = [{'tool': 'read_file', 'args': ['test.py'], 'raw': '[READ_FILE: "test.py"]'}]

        results = execute_tool_calls(calls, tools)

        assert len(results) == 1
        assert "File test.py" in results[0]

    def test_execute_list_artifacts(self, tmp_path):
        log_file = tmp_path / "test.log"
        log_file.write_text("dummy")

        tools = EvidenceSearchTools(
            log_path=log_file,
            repo_root=tmp_path,
            artifacts={'file1.py', 'file2.py'},
        )

        calls = [{'tool': 'list_artifacts', 'args': [], 'raw': '[LIST_ARTIFACTS]'}]

        results = execute_tool_calls(calls, tools)

        assert len(results) == 1
        assert "Artifacts tracked (2 files)" in results[0]

    def test_execute_unknown_tool(self, tmp_path):
        log_file = tmp_path / "test.log"
        log_file.write_text("dummy")

        tools = EvidenceSearchTools(
            log_path=log_file,
            repo_root=tmp_path,
            artifacts=set(),
        )

        calls = [{'tool': 'unknown_tool', 'args': [], 'raw': '[UNKNOWN: "arg"]'}]

        results = execute_tool_calls(calls, tools)

        assert len(results) == 1
        assert "Error: Unknown tool" in results[0]


class TestBuildEvidenceSearchPrompt:
    def test_build_prompt_with_turns(self, sample_turn_summaries, sample_accumulated_state):
        prompt = build_evidence_search_prompt(
            turn_summaries=sample_turn_summaries,
            accumulated_state=sample_accumulated_state,
            tools=MagicMock(),
            session_name="test_session",
        )

        assert "test_session" in prompt
        assert "CURRENT TURN SUMMARIES" in prompt
        assert "Turn 0:" in prompt
        assert "Turn 1:" in prompt
        assert "ACCUMULATED STATE" in prompt
        assert "High-level goal: Debug module forge" in prompt
        assert "AVAILABLE TOOLS" in prompt

    def test_build_prompt_truncates_many_turns(self, tmp_path):
        many_turns = [
            {
                'turn_number': str(i),
                'user_request_summary': f'Request {i}',
                'agent_response_summary': f'Response {i}',
                'key_outcomes': f'Outcome {i}',
                'state_changes': f'Change {i}',
                'artifacts_modified': [],
                'constraints_added': [],
                'open_questions': [],
                'state_updates': {},
            }
            for i in range(10)
        ]

        prompt = build_evidence_search_prompt(
            turn_summaries=many_turns,
            accumulated_state={'artifacts': set(), 'constraints': []},
            tools=MagicMock(max_searches=8),
            session_name="test",
        )

        assert "Turn 9:" not in prompt
        assert "... and 5 more turns" in prompt


class TestBuildContinuationPrompt:
    def test_build_continuation(self):
        previous_results = [
            "Result 1",
            "Result 2",
            "Result 3",
        ]

        prompt = build_continuation_prompt(
            previous_results=previous_results,
            iteration=2,
            max_searches=8,
        )

        assert "PREVIOUS SEARCH RESULTS" in prompt
        assert "Result 1" in prompt
        assert "Result 2" in prompt
        assert "Result 3" in prompt
        assert "Iteration 2/8" in prompt


class TestRunAgenticEvidenceGathering:
    def test_immediate_completion(self, sample_turn_summaries, sample_accumulated_state, tmp_path):
        mock_backend = MagicMock()
        mock_backend.generate.side_effect = [
            "[COMPLETE_EVIDENCE_SEARCH]",
            "SESSION SUMMARY\n\nSession name:\n- test",
        ]
    
        log_file = tmp_path / "dummy.log"
        log_file.write_text("dummy")
    
        tools = EvidenceSearchTools(
            log_path=log_file,
            repo_root=tmp_path,
            artifacts=set(),
        )
    
        result = run_agentic_evidence_gathering(
            turn_summaries=sample_turn_summaries,
            accumulated_state=sample_accumulated_state,
            backend=mock_backend,
            search_tools=tools,
            session_name="test",
        )
    
        assert mock_backend.generate.call_count == 2
        assert "SESSION SUMMARY" in result
        assert "test" in result

    def test_searches_with_completions(self, sample_turn_summaries, sample_accumulated_state, tmp_path):
        mock_backend = MagicMock()
        mock_backend.generate.side_effect = [
            "I need to check the log. [SEARCH_LOG: \"error\"]",
            "Found some results. Let me check files. [COMPLETE_EVIDENCE_SEARCH]",
            "SESSION SUMMARY\n\nSession name:\n- test\n\nHigh-level goal:\n- Debug",
        ]
    
        log_file = tmp_path / "dummy.log"
        log_file.write_text("dummy")
    
        tools = EvidenceSearchTools(
            log_path=log_file,
            repo_root=tmp_path,
            artifacts=set(),
        )
    
        result = run_agentic_evidence_gathering(
            turn_summaries=sample_turn_summaries,
            accumulated_state=sample_accumulated_state,
            backend=mock_backend,
            search_tools=tools,
            session_name="test",
        )
    
        assert mock_backend.generate.call_count == 3
        assert "SESSION SUMMARY" in result

    def test_max_searches_without_completion(self, sample_turn_summaries, sample_accumulated_state, tmp_path):
        mock_backend = MagicMock()
        mock_backend.generate.side_effect = ["Need more info"] * 10
    
        log_file = tmp_path / "dummy.log"
        log_file.write_text("dummy")
    
        tools = EvidenceSearchTools(
            log_path=log_file,
            repo_root=tmp_path,
            artifacts=set(),
        )
    
        result = run_agentic_evidence_gathering(
            turn_summaries=sample_turn_summaries,
            accumulated_state=sample_accumulated_state,
            backend=mock_backend,
            search_tools=tools,
            session_name="test",
        )
    
        assert mock_backend.generate.call_count == 9

    def test_empty_turn_summaries(self, tmp_path):
        mock_backend = MagicMock()
        mock_backend.generate.side_effect = [
            "[COMPLETE_EVIDENCE_SEARCH]",
            "SESSION SUMMARY\n\nSession name:\n- test",
        ]
    
        log_file = tmp_path / "dummy.log"
        log_file.write_text("dummy")
    
        tools = EvidenceSearchTools(
            log_path=log_file,
            repo_root=tmp_path,
            artifacts=set(),
        )
    
        result = run_agentic_evidence_gathering(
            turn_summaries=[],
            accumulated_state={'artifacts': set(), 'constraints': []},
            backend=mock_backend,
            search_tools=tools,
            session_name="test",
        )
    
        assert "SESSION SUMMARY" in result
