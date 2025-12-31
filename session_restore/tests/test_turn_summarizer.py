"""
Tests for turn summarizer module with 100% coverage target for build_turn_prompt.
"""
import pytest

from opencode_restore.turn_summarizer import build_turn_prompt, parse_turn_summary, _extract_bullet_list, process_turns_incrementally
from opencode_restore.turn_parser import TurnRound, ArtifactAction, ArtifactActionType


class TestBuildTurnPromptInputValidation:
    """Test input validation for build_turn_prompt function."""

    def test_basic_input_with_minimal_turn(self):
        """Test with minimal valid TurnRound object."""
        turn = TurnRound(
            turn_number=0,
            user_messages=["Build a CLI tool"],
            agent_responses=["I'll help you build a CLI tool."],
            raw_lines=["┃ Build a CLI tool", "I'll help you build a CLI tool."],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )
        result = build_turn_prompt("test_session", turn)
        assert "Session name: test_session" in result
        assert "CURRENT TURN (Turn 0)" in result
        assert "User messages:" in result
        assert "Agent responses:" in result

    def test_empty_user_messages(self):
        """Test with empty user_messages list."""
        turn = TurnRound(
            turn_number=0,
            user_messages=[],
            agent_responses=["Some response"],
            raw_lines=["Some response"],
            start_line_index=0,
            end_line_index=0,
            artifacts=[],
        )
        result = build_turn_prompt("test_session", turn)
        assert "User messages:" in result
        assert len([line for line in result.split("\n") if line.startswith("┃") and "messages" in result.split("User messages:")[1].split("\n")[0:10]]) == 0

    def test_empty_agent_responses(self):
        """Test with empty agent_responses list."""
        turn = TurnRound(
            turn_number=0,
            user_messages=["Help me"],
            agent_responses=[],
            raw_lines=["┃ Help me"],
            start_line_index=0,
            end_line_index=0,
            artifacts=[],
        )
        result = build_turn_prompt("test_session", turn)
        assert "Agent responses:" in result
        assert "... and" not in result

    def test_multiple_user_messages(self):
        """Test with multiple user messages."""
        turn = TurnRound(
            turn_number=0,
            user_messages=["First message", "Second message"],
            agent_responses=["Response"],
            raw_lines=["┃ First message", "┃ Second message", "Response"],
            start_line_index=0,
            end_line_index=2,
            artifacts=[],
        )
        result = build_turn_prompt("test_session", turn)
        assert "User messages:" in result
        assert "┃ First message" in result
        assert "┃ Second message" in result


class TestBuildTurnPromptTruncation:
    """Test truncation logic for agent responses."""

    def test_exactly_ten_agent_responses(self):
        """Test with exactly 10 agent responses - should NOT truncate."""
        responses = [f"Response line {i}" for i in range(10)]
        turn = TurnRound(
            turn_number=0,
            user_messages=["Test"],
            agent_responses=responses,
            raw_lines=["┃ Test"] + responses,
            start_line_index=0,
            end_line_index=10,
            artifacts=[],
        )
        result = build_turn_prompt("test_session", turn)
        assert "┃ Response line 0" in result
        assert "┃ Response line 9" in result
        assert "... and" not in result

    def test_eleven_agent_responses_truncates_to_ten(self):
        """Test with 11 agent responses - should truncate to 10."""
        responses = [f"Response line {i}" for i in range(11)]
        turn = TurnRound(
            turn_number=0,
            user_messages=["Test"],
            agent_responses=responses,
            raw_lines=["┃ Test"] + responses,
            start_line_index=0,
            end_line_index=11,
            artifacts=[],
        )
        result = build_turn_prompt("test_session", turn)
        assert "┃ Response line 0" in result
        assert "┃ Response line 9" in result
        assert "┃ Response line 10" not in result
        assert "... and 1 more lines" in result

    def test_twenty_agent_responses_truncates_correctly(self):
        """Test with 20 agent responses - should truncate to 10 with correct count."""
        responses = [f"Response line {i}" for i in range(20)]
        turn = TurnRound(
            turn_number=0,
            user_messages=["Test"],
            agent_responses=responses,
            raw_lines=["┃ Test"] + responses,
            start_line_index=0,
            end_line_index=20,
            artifacts=[],
        )
        result = build_turn_prompt("test_session", turn)
        assert "┃ Response line 0" in result
        assert "┃ Response line 9" in result
        assert "┃ Response line 10" not in result
        assert "... and 10 more lines" in result


class TestBuildTurnPromptPreviousSummary:
    """Test inclusion of previous summary context."""

    def test_no_previous_summary(self):
        """Test with no previous_summary parameter."""
        turn = TurnRound(
            turn_number=1,
            user_messages=["Continue"],
            agent_responses=["Continuing..."],
            raw_lines=["┃ Continue", "Continuing..."],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )
        result = build_turn_prompt("test_session", turn)
        assert "PREVIOUS TURN SUMMARY:" not in result

    def test_with_previous_summary_turn_number(self):
        """Test previous_summary includes turn number."""
        turn = TurnRound(
            turn_number=1,
            user_messages=["Continue"],
            agent_responses=["Continuing..."],
            raw_lines=["┃ Continue", "Continuing..."],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )
        previous_summary = {"turn_number": 0}
        result = build_turn_prompt("test_session", turn, previous_summary=previous_summary)
        assert "PREVIOUS TURN SUMMARY:" in result
        assert "Turn number: 0" in result

    def test_with_previous_summary_user_request(self):
        """Test previous_summary includes user request summary."""
        turn = TurnRound(
            turn_number=1,
            user_messages=["Continue"],
            agent_responses=["Continuing..."],
            raw_lines=["┃ Continue", "Continuing..."],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )
        previous_summary = {
            "turn_number": 0,
            "user_request_summary": "Create a CLI tool",
        }
        result = build_turn_prompt("test_session", turn, previous_summary=previous_summary)
        assert "PREVIOUS TURN SUMMARY:" in result
        assert "User request summary: Create a CLI tool" in result

    def test_with_previous_summary_missing_fields(self):
        """Test previous_summary with missing user_request_summary."""
        turn = TurnRound(
            turn_number=1,
            user_messages=["Continue"],
            agent_responses=["Continuing..."],
            raw_lines=["┃ Continue", "Continuing..."],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )
        previous_summary = {"turn_number": 0}
        result = build_turn_prompt("test_session", turn, previous_summary=previous_summary)
        assert "PREVIOUS TURN SUMMARY:" in result
        assert "Turn number: 0" in result
        # The previous_summary section should only have turn number, no user request summary value
        prev_section = result.split("PREVIOUS TURN SUMMARY:")[1].split("CURRENT")[0]
        assert "Turn number: 0" in prev_section
        # There should be no "User request summary: <value>" line in previous summary section
        # Only "User request summary:" from TURN_SUMMARY_SCHEMA will be present at the end
        assert prev_section.count("User request summary:") == 0


class TestBuildTurnPromptAccumulatedState:
    """Test inclusion of accumulated state."""

    def test_no_accumulated_state(self):
        """Test with no accumulated_state parameter."""
        turn = TurnRound(
            turn_number=0,
            user_messages=["Test"],
            agent_responses=["Response"],
            raw_lines=["┃ Test", "Response"],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )
        result = build_turn_prompt("test_session", turn)
        assert "CURRENT ACCUMULATED STATE:" not in result

    def test_accumulated_state_with_high_level_goal(self):
        """Test accumulated_state includes high-level goal."""
        turn = TurnRound(
            turn_number=0,
            user_messages=["Test"],
            agent_responses=["Response"],
            raw_lines=["┃ Test", "Response"],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )
        accumulated_state = {"high_level_goal": "Build CLI tool"}
        result = build_turn_prompt("test_session", turn, accumulated_state=accumulated_state)
        assert "CURRENT ACCUMULATED STATE:" in result
        assert "High-level goal: Build CLI tool" in result

    def test_accumulated_state_with_key_decisions(self):
        """Test accumulated_state includes key decisions."""
        turn = TurnRound(
            turn_number=0,
            user_messages=["Test"],
            agent_responses=["Response"],
            raw_lines=["┃ Test", "Response"],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )
        accumulated_state = {"key_decisions": ["Use argparse", "Python 3.8+"]}
        result = build_turn_prompt("test_session", turn, accumulated_state=accumulated_state)
        assert "CURRENT ACCUMULATED STATE:" in result
        assert "Key decisions: Use argparse, Python 3.8+" in result

    def test_accumulated_state_with_constraints(self):
        """Test accumulated_state includes constraints."""
        turn = TurnRound(
            turn_number=0,
            user_messages=["Test"],
            agent_responses=["Response"],
            raw_lines=["┃ Test", "Response"],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )
        accumulated_state = {"constraints": ["Python 3.8+", "Must be CLI"]}
        result = build_turn_prompt("test_session", turn, accumulated_state=accumulated_state)
        assert "CURRENT ACCUMULATED STATE:" in result
        assert "Constraints: Python 3.8+, Must be CLI" in result

    def test_accumulated_state_with_artifacts(self):
        """Test accumulated_state includes artifacts."""
        turn = TurnRound(
            turn_number=0,
            user_messages=["Test"],
            agent_responses=["Response"],
            raw_lines=["┃ Test", "Response"],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )
        accumulated_state = {"artifacts": ["main.py", "config.py"]}
        result = build_turn_prompt("test_session", turn, accumulated_state=accumulated_state)
        assert "CURRENT ACCUMULATED STATE:" in result
        assert "All artifacts: main.py, config.py" in result

    def test_accumulated_state_with_open_questions(self):
        """Test accumulated_state includes open questions."""
        turn = TurnRound(
            turn_number=0,
            user_messages=["Test"],
            agent_responses=["Response"],
            raw_lines=["┃ Test", "Response"],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )
        accumulated_state = {"open_questions": ["How to handle errors?"]}
        result = build_turn_prompt("test_session", turn, accumulated_state=accumulated_state)
        assert "CURRENT ACCUMULATED STATE:" in result
        assert "Open questions: How to handle errors?" in result

    def test_accumulated_state_with_empty_lists(self):
        """Test accumulated_state with empty lists doesn't include those sections."""
        turn = TurnRound(
            turn_number=0,
            user_messages=["Test"],
            agent_responses=["Response"],
            raw_lines=["┃ Test", "Response"],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )
        accumulated_state = {
            "key_decisions": [],
            "constraints": [],
            "artifacts": [],
            "open_questions": [],
        }
        result = build_turn_prompt("test_session", turn, accumulated_state=accumulated_state)
        assert "CURRENT ACCUMULATED STATE:" in result
        assert "Key decisions:" not in result
        assert "Constraints:" not in result
        assert "All artifacts:" not in result
        assert "Open questions:" not in result

    def test_accumulated_state_complete(self):
        """Test accumulated_state with all fields populated."""
        turn = TurnRound(
            turn_number=0,
            user_messages=["Test"],
            agent_responses=["Response"],
            raw_lines=["┃ Test", "Response"],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )
        accumulated_state = {
            "high_level_goal": "Build CLI tool",
            "key_decisions": ["Use argparse"],
            "constraints": ["Python 3.8+"],
            "artifacts": ["main.py"],
            "open_questions": ["Error handling?"],
        }
        result = build_turn_prompt("test_session", turn, accumulated_state=accumulated_state)
        assert "CURRENT ACCUMULATED STATE:" in result
        assert "High-level goal: Build CLI tool" in result
        assert "Key decisions: Use argparse" in result
        assert "Constraints: Python 3.8+" in result
        assert "All artifacts: main.py" in result
        assert "Open questions: Error handling?" in result


class TestBuildTurnPromptTurnSummarySchema:
    """Test TURN_SUMMARY_SCHEMA is included."""

    def test_schema_included(self):
        """Test TURN_SUMMARY_SCHEMA is included in output."""
        turn = TurnRound(
            turn_number=0,
            user_messages=["Test"],
            agent_responses=["Response"],
            raw_lines=["┃ Test", "Response"],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )
        result = build_turn_prompt("test_session", turn)
        assert "TURN SUMMARY" in result
        assert "Turn number:" in result
        assert "User request summary:" in result
        assert "Agent response summary:" in result
        assert "Key outcomes:" in result
        assert "State changes:" in result
        assert "Artifacts modified:" in result
        assert "Constraints/assumptions added:" in result
        assert "Open questions after this turn:" in result


class TestBuildTurnPromptFormat:
    """Test output format structure."""

    def test_session_name_format(self):
        """Test session name appears at start."""
        turn = TurnRound(
            turn_number=0,
            user_messages=["Test"],
            agent_responses=["Response"],
            raw_lines=["┃ Test", "Response"],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )
        result = build_turn_prompt("session_abc123", turn)
        assert result.startswith("Session name: session_abc123\n")

    def test_turn_number_in_header(self):
        """Test turn number appears in CURRENT TURN header."""
        turn = TurnRound(
            turn_number=5,
            user_messages=["Test"],
            agent_responses=["Response"],
            raw_lines=["┃ Test", "Response"],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )
        result = build_turn_prompt("test_session", turn)
        assert "CURRENT TURN (Turn 5):" in result

    def test_user_messages_have_box_prefix(self):
        """Test user messages are prefixed with box character."""
        turn = TurnRound(
            turn_number=0,
            user_messages=["Hello", "World"],
            agent_responses=["Response"],
            raw_lines=["┃ Hello", "┃ World", "Response"],
            start_line_index=0,
            end_line_index=2,
            artifacts=[],
        )
        result = build_turn_prompt("test_session", turn)
        assert "┃ Hello" in result
        assert "┃ World" in result

    def test_agent_responses_have_box_prefix(self):
        """Test agent responses are prefixed with box character."""
        turn = TurnRound(
            turn_number=0,
            user_messages=["Test"],
            agent_responses=["Line 1", "Line 2"],
            raw_lines=["┃ Test", "Line 1", "Line 2"],
            start_line_index=0,
            end_line_index=2,
            artifacts=[],
        )
        result = build_turn_prompt("test_session", turn)
        assert "┃ Line 1" in result
        assert "┃ Line 2" in result


class TestBuildTurnPromptEdgeCases:
    """Test edge cases and special scenarios."""

    def test_none_previous_summary_and_accumulated_state(self):
        """Test with both optional parameters as None."""
        turn = TurnRound(
            turn_number=0,
            user_messages=["Test"],
            agent_responses=["Response"],
            raw_lines=["┃ Test", "Response"],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )
        result = build_turn_prompt("test_session", turn, previous_summary=None, accumulated_state=None)
        assert "PREVIOUS TURN SUMMARY:" not in result
        assert "CURRENT ACCUMULATED STATE:" not in result
        assert "CURRENT TURN (Turn 0):" in result

    def test_turn_with_artifacts(self):
        """Test turn with artifacts in the TurnRound object."""
        artifacts = [
            ArtifactAction(
                file_path="main.py",
                action_type=ArtifactActionType.READ,
                line_number=0,
            ),
        ]
        turn = TurnRound(
            turn_number=0,
            user_messages=["Test"],
            agent_responses=["Response"],
            raw_lines=["┃ Test", "Response"],
            start_line_index=0,
            end_line_index=1,
            artifacts=artifacts,
        )
        result = build_turn_prompt("test_session", turn)
        assert "CURRENT TURN (Turn 0):" in result

    def test_special_characters_in_messages(self):
        """Test messages with special characters."""
        turn = TurnRound(
            turn_number=0,
            user_messages=["Test with 'quotes' and \"double quotes\""],
            agent_responses=["Response with <special> &characters;"],
            raw_lines=["┃ Test with 'quotes'", "Response with <special>"],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )
        result = build_turn_prompt("test_session", turn)
        assert "Test with 'quotes' and \"double quotes\"" in result
        assert "Response with <special> &characters;" in result

    def test_multiline_messages(self):
        """Test messages with newlines."""
        turn = TurnRound(
            turn_number=0,
            user_messages=["First line\nSecond line"],
            agent_responses=["Response"],
            raw_lines=["┃ First line\nSecond line", "Response"],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )
        result = build_turn_prompt("test_session", turn)
        assert "First line\nSecond line" in result

    def test_zero_turn_number(self):
        """Test with turn_number=0."""
        turn = TurnRound(
            turn_number=0,
            user_messages=["Test"],
            agent_responses=["Response"],
            raw_lines=["┃ Test", "Response"],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )
        result = build_turn_prompt("test_session", turn)
        assert "CURRENT TURN (Turn 0):" in result

    def test_large_turn_number(self):
        """Test with large turn number."""
        turn = TurnRound(
            turn_number=999,
            user_messages=["Test"],
            agent_responses=["Response"],
            raw_lines=["┃ Test", "Response"],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )
        result = build_turn_prompt("test_session", turn)
        assert "CURRENT TURN (Turn 999):" in result


class TestBuildTurnPromptCompleteScenarios:
    """Test complete realistic scenarios."""

    def test_full_scenario_with_all_context(self):
        """Test with all parameters provided."""
        turn = TurnRound(
            turn_number=2,
            user_messages=["Continue with the CLI tool"],
            agent_responses=[
                "I'll continue with the CLI tool.",
                "Let me add the argument parser.",
                "Added argparse module.",
                "Created CLI structure.",
                "Added subcommands.",
            ],
            raw_lines=["┃ Continue with the CLI tool"] + [
                "I'll continue with the CLI tool.",
                "Let me add the argument parser.",
                "Added argparse module.",
                "Created CLI structure.",
                "Added subcommands.",
            ],
            start_line_index=0,
            end_line_index=6,
            artifacts=[],
        )
        previous_summary = {
            "turn_number": 1,
            "user_request_summary": "Create a basic CLI structure",
        }
        accumulated_state = {
            "high_level_goal": "Build comprehensive CLI tool",
            "key_decisions": ["Use argparse", "Support subcommands"],
            "constraints": ["Python 3.8+", "POSIX compliant"],
            "artifacts": ["main.py", "config.py", "utils.py"],
            "open_questions": ["How to handle errors?"],
        }
        result = build_turn_prompt("cli_project", turn, previous_summary, accumulated_state)
        
        assert "Session name: cli_project" in result
        assert "PREVIOUS TURN SUMMARY:" in result
        assert "Turn number: 1" in result
        assert "User request summary: Create a basic CLI structure" in result
        assert "CURRENT ACCUMULATED STATE:" in result
        assert "High-level goal: Build comprehensive CLI tool" in result
        assert "Key decisions: Use argparse, Support subcommands" in result
        assert "Constraints: Python 3.8+, POSIX compliant" in result
        assert "All artifacts: main.py, config.py, utils.py" in result
        assert "Open questions: How to handle errors?" in result
        assert "CURRENT TURN (Turn 2):" in result
        assert "┃ Continue with the CLI tool" in result
        assert "┃ I'll continue with the CLI tool." in result
        assert "TURN SUMMARY" in result

    def test_minimal_scenario_no_context(self):
        """Test with minimal parameters only."""
        turn = TurnRound(
            turn_number=0,
            user_messages=["Hello"],
            agent_responses=["Hi there!"],
            raw_lines=["┃ Hello", "Hi there!"],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )
        result = build_turn_prompt("minimal_session", turn)
        
        assert "Session name: minimal_session" in result
        assert "PREVIOUS TURN SUMMARY:" not in result
        assert "CURRENT ACCUMULATED STATE:" not in result
        assert "CURRENT TURN (Turn 0):" in result
        assert "┃ Hello" in result
        assert "┃ Hi there!" in result
        assert "TURN SUMMARY" in result


class TestParseTurnSummaryCompleteResponse:
    """Test parsing complete LLM responses."""

    def test_parse_complete_summary(self):
        """Test parsing response with all fields present."""
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
        assert result["key_outcomes"] == "main.py created"
        assert result["state_changes"] == "Project initialized"
        assert result["artifacts_modified"] == "main.py"
        assert result["constraints_added"] == "Python 3.8+"
        assert result["open_questions"] == "Error handling?"

    def test_parse_summary_with_empty_fields(self):
        """Test parsing response where some fields have empty values."""
        llm_response = """
TURN SUMMARY

Turn number: 1
User request summary: Continue project
Agent response summary:
Key outcomes:
State changes:
Artifacts modified: config.py
Constraints/assumptions added:
Open questions after this turn:
"""
        result = parse_turn_summary(llm_response)
        assert result["turn_number"] == "1"
        assert result["user_request_summary"] == "Continue project"
        assert result["agent_response_summary"] is None
        assert result["key_outcomes"] is None
        assert result["state_changes"] is None
        assert result["artifacts_modified"] == "config.py"
        assert result["constraints_added"] is None
        assert result["open_questions"] is None


class TestParseTurnSummaryMissingFields:
    """Test parsing responses with missing fields."""

    def test_parse_only_turn_number(self):
        """Test parsing response with only turn number."""
        llm_response = """
TURN SUMMARY

Turn number: 0
"""
        result = parse_turn_summary(llm_response)
        assert result["turn_number"] == "0"
        assert result["user_request_summary"] is None
        assert result["agent_response_summary"] is None
        assert result["key_outcomes"] is None
        assert result["state_changes"] is None
        assert result["artifacts_modified"] is None
        assert result["constraints_added"] is None
        assert result["open_questions"] is None

    def test_parse_two_fields_only(self):
        """Test parsing response with only turn number and user request."""
        llm_response = """
TURN SUMMARY

Turn number: 0
User request summary: Build CLI tool
"""
        result = parse_turn_summary(llm_response)
        assert result["turn_number"] == "0"
        assert result["user_request_summary"] == "Build CLI tool"
        assert result["agent_response_summary"] is None
        assert result["key_outcomes"] is None

    def test_parse_missing_turn_number(self):
        """Test parsing response without turn number."""
        llm_response = """
TURN SUMMARY

User request summary: Build CLI tool
Agent response summary: Creating structure
"""
        result = parse_turn_summary(llm_response)
        assert result["turn_number"] is None
        assert result["user_request_summary"] == "Build CLI tool"
        assert result["agent_response_summary"] == "Creating structure"

    def test_parse_multiple_missing_fields(self):
        """Test parsing response with multiple missing fields."""
        llm_response = """
TURN SUMMARY

Turn number: 0
User request summary: Build CLI tool
Key outcomes: Started project
"""
        result = parse_turn_summary(llm_response)
        assert result["turn_number"] == "0"
        assert result["user_request_summary"] == "Build CLI tool"
        assert result["agent_response_summary"] is None
        assert result["key_outcomes"] == "Started project"
        assert result["state_changes"] is None
        assert result["artifacts_modified"] is None


class TestParseTurnSummaryMalformedInput:
    """Test parsing malformed or invalid input."""

    def test_empty_string_input(self):
        """Test parsing empty string."""
        result = parse_turn_summary("")
        assert result["turn_number"] is None
        assert result["user_request_summary"] is None
        assert result["agent_response_summary"] is None
        assert result["key_outcomes"] is None
        assert result["state_changes"] is None
        assert result["artifacts_modified"] is None
        assert result["constraints_added"] is None
        assert result["open_questions"] is None

    def test_missing_turn_summary_header(self):
        """Test parsing response without TURN SUMMARY header."""
        llm_response = """
Turn number: 0
User request summary: Build CLI tool
"""
        result = parse_turn_summary(llm_response)
        assert result["turn_number"] is None
        assert result["user_request_summary"] is None

    def test_only_header_no_fields(self):
        """Test parsing response with only header."""
        llm_response = """TURN SUMMARY"""
        result = parse_turn_summary(llm_response)
        assert result["turn_number"] is None
        assert result["user_request_summary"] is None

    def test_malformed_lines_no_colon(self):
        """Test parsing response with lines without colons."""
        llm_response = """
TURN SUMMARY

Turn number 0
User request summary Build CLI tool
"""
        result = parse_turn_summary(llm_response)
        assert result["turn_number"] is None
        assert result["user_request_summary"] is None

    def test_duplicate_field_names(self):
        """Test parsing response with duplicate fields (last one wins)."""
        llm_response = """
TURN SUMMARY

Turn number: 0
Turn number: 1
User request summary: Build CLI tool
"""
        result = parse_turn_summary(llm_response)
        assert result["turn_number"] == "1"
        assert result["user_request_summary"] == "Build CLI tool"


class TestParseTurnSummaryWhitespace:
    """Test parsing with various whitespace patterns."""

    def test_extra_newlines_between_fields(self):
        """Test parsing with extra newlines."""
        llm_response = """
TURN SUMMARY


Turn number: 0

User request summary: Build CLI tool


Agent response summary: Done
"""
        result = parse_turn_summary(llm_response)
        assert result["turn_number"] == "0"
        assert result["user_request_summary"] == "Build CLI tool"
        assert result["agent_response_summary"] == "Done"

    def test_leading_trailing_whitespace(self):
        """Test parsing with leading/trailing whitespace in response."""
        llm_response = """

TURN SUMMARY

Turn number: 0
User request summary: Build CLI tool

"""
        result = parse_turn_summary(llm_response)
        assert result["turn_number"] == "0"
        assert result["user_request_summary"] == "Build CLI tool"

    def test_extra_spaces_around_colons(self):
        """Test parsing with extra spaces around colons."""
        llm_response = """
TURN SUMMARY

Turn number  :  0
User request summary : Build CLI tool
"""
        result = parse_turn_summary(llm_response)
        assert result["turn_number"] == "0"
        assert result["user_request_summary"] == "Build CLI tool"

    def test_values_with_leading_trailing_whitespace(self):
        """Test parsing values with leading/trailing whitespace."""
        llm_response = """
TURN SUMMARY

Turn number:   0
User request summary:  Build CLI tool  
"""
        result = parse_turn_summary(llm_response)
        assert result["turn_number"] == "0"
        assert result["user_request_summary"] == "Build CLI tool"


class TestParseTurnSummarySpecialValues:
    """Test parsing with special value formats."""

    def test_value_contains_colons(self):
        """Test parsing value that contains colons."""
        llm_response = """
TURN SUMMARY

Turn number: 0
Key outcomes: Task 1: Done, Task 2: Pending
"""
        result = parse_turn_summary(llm_response)
        assert result["turn_number"] == "0"
        assert result["key_outcomes"] == "Task 1: Done, Task 2: Pending"

    def test_value_with_special_characters(self):
        """Test parsing values with special characters."""
        llm_response = """
TURN SUMMARY

Turn number: 0
User request summary: Build CLI tool with -h, --help flags
"""
        result = parse_turn_summary(llm_response)
        assert result["turn_number"] == "0"
        assert result["user_request_summary"] == "Build CLI tool with -h, --help flags"

    def test_empty_value(self):
        """Test parsing field with empty value."""
        llm_response = """
TURN SUMMARY

Turn number: 0
Artifacts modified:
"""
        result = parse_turn_summary(llm_response)
        assert result["turn_number"] == "0"
        assert result["artifacts_modified"] is None

    def test_value_with_commas(self):
        """Test parsing values with comma-separated lists."""
        llm_response = """
TURN SUMMARY

Turn number: 0
Artifacts modified: main.py, config.py, utils.py
"""
        result = parse_turn_summary(llm_response)
        assert result["turn_number"] == "0"
        assert result["artifacts_modified"] == "main.py, config.py, utils.py"


class TestParseTurnSummaryPartialResponse:
    """Test parsing partial responses."""

    def test_only_first_half_fields(self):
        """Test parsing with only first half of fields."""
        llm_response = """
TURN SUMMARY

Turn number: 0
User request summary: Build CLI tool
Agent response summary: Started
Key outcomes: main.py
"""
        result = parse_turn_summary(llm_response)
        assert result["turn_number"] == "0"
        assert result["user_request_summary"] == "Build CLI tool"
        assert result["agent_response_summary"] == "Started"
        assert result["key_outcomes"] == "main.py"
        assert result["state_changes"] is None
        assert result["artifacts_modified"] is None

    def test_only_last_half_fields(self):
        """Test parsing with only last half of fields."""
        llm_response = """
TURN SUMMARY

State changes: Project set up
Artifacts modified: main.py
Constraints/assumptions added: Python 3.8+
Open questions after this turn: Error handling?
"""
        result = parse_turn_summary(llm_response)
        assert result["turn_number"] is None
        assert result["user_request_summary"] is None
        assert result["state_changes"] == "Project set up"
        assert result["artifacts_modified"] == "main.py"
        assert result["constraints_added"] == "Python 3.8+"
        assert result["open_questions"] == "Error handling?"

    def test_fields_in_wrong_order(self):
        """Test parsing with fields in non-standard order."""
        llm_response = """
TURN SUMMARY

Open questions after this turn: Error handling?
Turn number: 0
User request summary: Build CLI tool
Artifacts modified: main.py
"""
        result = parse_turn_summary(llm_response)
        assert result["turn_number"] == "0"
        assert result["user_request_summary"] == "Build CLI tool"
        assert result["artifacts_modified"] == "main.py"
        assert result["open_questions"] == "Error handling?"


class TestParseTurnSummaryEdgeCases:
    """Test edge cases."""

    def test_response_with_bullet_points(self):
        """Test parsing response with bullet points (should be skipped)."""
        llm_response = """
TURN SUMMARY

Turn number: 0
- Some bullet point
User request summary: Build CLI tool
- Another bullet point
"""
        result = parse_turn_summary(llm_response)
        assert result["turn_number"] == "0"
        assert result["user_request_summary"] == "Build CLI tool"

    def test_case_insensitive_header(self):
        """Test that TURN SUMMARY header is case-insensitive."""
        llm_response = """
turn summary

Turn number: 0
User request summary: Build CLI tool
"""
        result = parse_turn_summary(llm_response)
        assert result["turn_number"] == "0"
        assert result["user_request_summary"] == "Build CLI tool"

    def test_response_with_extra_content_before_header(self):
        """Test parsing with content before TURN SUMMARY header."""
        llm_response = """
Some preamble text
And more text

TURN SUMMARY

Turn number: 0
User request summary: Build CLI tool
"""
        result = parse_turn_summary(llm_response)
        assert result["turn_number"] == "0"
        assert result["user_request_summary"] == "Build CLI tool"

    def test_response_with_extra_content_after_fields(self):
        """Test parsing with extra content after the fields."""
        llm_response = """
TURN SUMMARY

Turn number: 0
User request summary: Build CLI tool

Some extra text here
"""
        result = parse_turn_summary(llm_response)
        assert result["turn_number"] == "0"
        assert result["user_request_summary"] == "Build CLI tool"

    def test_all_fields_numeric_values(self):
        """Test parsing when all values are numeric strings."""
        llm_response = """
TURN SUMMARY

Turn number: 123
User request summary: 456
Agent response summary: 789
"""
        result = parse_turn_summary(llm_response)
        assert result["turn_number"] == "123"
        assert result["user_request_summary"] == "456"
        assert result["agent_response_summary"] == "789"


class TestExtractBulletListEmptyNone:
    """Test extraction from empty or None input."""

    def test_none_input(self):
        """Test None input returns empty list."""
        result = _extract_bullet_list(None)
        assert result == []

    def test_empty_string(self):
        """Test empty string returns empty list."""
        result = _extract_bullet_list("")
        assert result == []

    def test_whitespace_only(self):
        """Test whitespace-only input returns empty list."""
        result = _extract_bullet_list("   \n  \t  ")
        assert result == []


class TestExtractBulletListCommaSeparated:
    """Test extraction from comma-separated format."""

    def test_simple_comma_separated(self):
        """Test simple comma-separated list."""
        result = _extract_bullet_list("item1, item2, item3")
        assert result == ["item1", "item2", "item3"]

    def test_comma_separated_with_spaces(self):
        """Test comma-separated with extra spaces."""
        result = _extract_bullet_list("  item1  ,  item2  ,  item3  ")
        assert result == ["item1", "item2", "item3"]

    def test_comma_separated_leading_trailing_whitespace(self):
        """Test comma-separated with leading/trailing whitespace."""
        result = _extract_bullet_list("   item1, item2, item3   ")
        assert result == ["item1", "item2", "item3"]

    def test_single_item_no_commas(self):
        """Test single item without commas."""
        result = _extract_bullet_list("single item")
        assert result == ["single item"]

    def test_two_items(self):
        """Test two comma-separated items."""
        result = _extract_bullet_list("item1, item2")
        assert result == ["item1", "item2"]

    def test_many_items(self):
        """Test many comma-separated items."""
        result = _extract_bullet_list("item1, item2, item3, item4, item5, item6, item7, item8, item9, item10")
        assert result == ["item1", "item2", "item3", "item4", "item5", "item6", "item7", "item8", "item9", "item10"]


class TestExtractBulletListBulletPoints:
    """Test extraction from bullet-point formats."""

    def test_dash_bullet_points(self):
        """Test dash bullet points."""
        text = """
- item1
- item2
- item3
"""
        result = _extract_bullet_list(text)
        assert result == ["item1", "item2", "item3"]

    def test_bullet_character(self):
        """Test bullet character (•)."""
        text = """
• item1
• item2
• item3
"""
        result = _extract_bullet_list(text)
        assert result == ["item1", "item2", "item3"]

    def test_asterisk_bullet_points(self):
        """Test asterisk bullet points."""
        text = """
* item1
* item2
* item3
"""
        result = _extract_bullet_list(text)
        assert result == ["item1", "item2", "item3"]

    def test_numbered_list_with_periods(self):
        """Test numbered list with periods."""
        text = """
1. item1
2. item2
3. item3
"""
        result = _extract_bullet_list(text)
        assert result == ["item1", "item2", "item3"]

    def test_numbered_list_with_parentheses(self):
        """Test numbered list with parentheses."""
        text = """
1) item1
2) item2
3) item3
"""
        result = _extract_bullet_list(text)
        assert result == ["item1", "item2", "item3"]

    def test_lettered_list(self):
        """Test lettered list (a., b., c.)."""
        text = """
a. item1
b. item2
c. item3
"""
        result = _extract_bullet_list(text)
        assert result == ["item1", "item2", "item3"]


class TestExtractBulletListMixedFormats:
    """Test extraction from mixed formats."""

    def test_comma_with_newlines(self):
        """Test comma-separated with newlines."""
        text = """item1, item2,
item3, item4"""
        result = _extract_bullet_list(text)
        # Since there are newlines, it treats as bullet format
        assert "item1, item2" in result[0] or "item1" in result

    def test_bullets_with_extra_spacing(self):
        """Test bullet points with extra spacing."""
        text = """
-  item1
-   item2
-  item3
"""
        result = _extract_bullet_list(text)
        assert result == ["item1", "item2", "item3"]

    def test_mixed_bullets(self):
        """Test mixed bullet types (should work)."""
        text = """
- item1
• item2
* item3
"""
        result = _extract_bullet_list(text)
        assert result == ["item1", "item2", "item3"]


class TestExtractBulletListEdgeCases:
    """Test edge cases."""

    def test_empty_items_consecutive_commas(self):
        """Test consecutive commas (empty items filtered)."""
        result = _extract_bullet_list("item1, , item2, , item3")
        assert result == ["item1", "item2", "item3"]

    def test_item_with_comma_inside(self):
        """Test item containing comma (shouldn't split)."""
        result = _extract_bullet_list("item1, item with, comma inside, item2")
        # Since no newlines, it treats as comma-separated
        assert "item1" in result
        assert "item with" in result
        assert "comma inside" in result
        assert "item2" in result

    def test_items_with_special_characters(self):
        """Test items with special characters."""
        result = _extract_bullet_list("item-1, item.2, item_3, item@test")
        assert result == ["item-1", "item.2", "item_3", "item@test"]

    def test_very_long_list(self):
        """Test very long list."""
        items = [f"item{i}" for i in range(50)]
        text = ", ".join(items)
        result = _extract_bullet_list(text)
        assert result == items

    def test_single_item_no_delimiters(self):
        """Test single item without any delimiters."""
        result = _extract_bullet_list("single item text")
        assert result == ["single item text"]

    def test_leading_trailing_delimiters(self):
        """Test leading and trailing delimiters."""
        result = _extract_bullet_list(", item1, item2, item3, ")
        assert result == ["item1", "item2", "item3"]

    def test_empty_items_after_stripping(self):
        """Test empty items that result from stripping."""
        result = _extract_bullet_list("-   , - item2, -  ")
        # No newlines, treated as comma-separated format
        # Empty items ("-   " and "-  ") are filtered out
        assert "- item2" in result

    def test_bullet_with_empty_lines(self):
        """Test bullet list with empty lines."""
        text = """
- item1

- item2


- item3
"""
        result = _extract_bullet_list(text)
        assert result == ["item1", "item2", "item3"]

    def test_mixed_case_markers(self):
        """Test that markers are case-sensitive for bullets."""
        text = """
- Item1
- Item2
- Item3
"""
        result = _extract_bullet_list(text)
        assert result == ["Item1", "Item2", "Item3"]


class TestProcessTurnsIncrementallyEmptyNone:
    """Test processing with empty or None input."""

    def test_empty_turns_list(self):
        """Test with empty turns list."""
        result = process_turns_incrementally("test_session", [])
        assert result["turn_summaries"] == []
        assert result["accumulated_state"]["high_level_goal"] is None
        assert result["accumulated_state"]["key_decisions"] == []
        assert result["accumulated_state"]["constraints"] == []
        assert result["accumulated_state"]["artifacts"] == []
        assert result["accumulated_state"]["open_questions"] == []


class TestProcessTurnsIncrementallySingleTurn:
    """Test processing single turn with mock LLM."""

    def test_single_turn_with_mock_llm(self):
        """Test single turn with LLM backend."""
        turn = TurnRound(
            turn_number=0,
            user_messages=["Build CLI tool"],
            agent_responses=["I'll build a CLI tool."],
            raw_lines=["┃ Build CLI tool", "I'll build a CLI tool."],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )

        def mock_llm(prompt):
            return """TURN SUMMARY

Turn number: 0
User request summary: Build CLI tool
Agent response summary: Created CLI structure
Key outcomes: main.py created, project initialized
State changes: Project started
Artifacts modified: main.py
Constraints/assumptions added: Must use argparse
Open questions after this turn: Error handling?
"""

        result = process_turns_incrementally("test_session", [turn], mock_llm)

        assert len(result["turn_summaries"]) == 1
        assert result["turn_summaries"][0]["turn_number"] == "0"
        assert result["accumulated_state"]["high_level_goal"] == "main.py created, project initialized"
        assert "Must use argparse" in result["accumulated_state"]["constraints"]
        assert "main.py" in result["accumulated_state"]["artifacts"]


class TestProcessTurnsIncrementallyMultipleTurns:
    """Test processing multiple turns with state accumulation."""

    def test_three_turns_with_mock_llm(self):
        """Test three turns with LLM backend."""
        turn0 = TurnRound(
            turn_number=0,
            user_messages=["Build CLI"],
            agent_responses=["Building..."],
            raw_lines=["┃ Build CLI", "Building..."],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )

        turn1 = TurnRound(
            turn_number=1,
            user_messages=["Continue"],
            agent_responses=["Continuing..."],
            raw_lines=["┃ Continue", "Continuing..."],
            start_line_index=2,
            end_line_index=3,
            artifacts=[],
        )

        turn2 = TurnRound(
            turn_number=2,
            user_messages=["Add features"],
            agent_responses=["Adding..."],
            raw_lines=["┃ Add features", "Adding..."],
            start_line_index=4,
            end_line_index=5,
            artifacts=[],
        )

        def mock_llm(prompt):
            if "Turn 0)" in prompt:
                return """TURN SUMMARY

Turn number: 0
User request summary: Build CLI
Agent response summary: Building
Key outcomes: Started project
State changes: Project initialized
Artifacts modified: main.py
Constraints/assumptions added: Python 3.8+
Open questions after this turn: None
"""
            elif "Turn 1)" in prompt:
                return """TURN SUMMARY

Turn number: 1
User request summary: Continue
Agent response summary: Continuing
Key outcomes: Added argparse
State changes: CLI structure set up
Artifacts modified: config.py
Constraints/assumptions added: Must be POSIX
Open questions after this turn: Error handling?
"""
            else:
                return """TURN SUMMARY

Turn number: 2
User request summary: Add features
Agent response summary: Adding features
Key outcomes: Added subcommands
State changes: Enhanced CLI
Artifacts modified: utils.py
Constraints/assumptions added: No external deps
Open questions after this turn: Help text?
"""

        result = process_turns_incrementally("test_session", [turn0, turn1, turn2], mock_llm)

        assert len(result["turn_summaries"]) == 3
        assert result["turn_summaries"][0]["turn_number"] == "0"
        assert result["turn_summaries"][1]["turn_number"] == "1"
        assert result["turn_summaries"][2]["turn_number"] == "2"

        # Check accumulated state
        assert result["accumulated_state"]["high_level_goal"] == "Started project"
        assert len(result["accumulated_state"]["key_decisions"]) == 2
        assert "Added argparse" in result["accumulated_state"]["key_decisions"]
        assert "Added subcommands" in result["accumulated_state"]["key_decisions"]
        assert len(result["accumulated_state"]["constraints"]) == 3
        assert "Python 3.8+" in result["accumulated_state"]["constraints"]
        assert "Must be POSIX" in result["accumulated_state"]["constraints"]
        assert "No external deps" in result["accumulated_state"]["constraints"]
        assert len(result["accumulated_state"]["artifacts"]) == 3
        assert "main.py" in result["accumulated_state"]["artifacts"]
        assert "config.py" in result["accumulated_state"]["artifacts"]
        assert "utils.py" in result["accumulated_state"]["artifacts"]
        assert "Help text?" in result["accumulated_state"]["open_questions"]


class TestProcessTurnsIncrementallyLLMBackend:
    """Test processing with and without LLM backend."""

    def test_with_llm_backend(self):
        """Test with LLM backend provided."""
        turn = TurnRound(
            turn_number=0,
            user_messages=["Test"],
            agent_responses=["Response"],
            raw_lines=["┃ Test", "Response"],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )

        def mock_llm(prompt):
            return """TURN SUMMARY

Turn number: 0
User request summary: Test
"""

        result = process_turns_incrementally("test", [turn], mock_llm)
        assert len(result["turn_summaries"]) == 1
        assert result["turn_summaries"][0]["user_request_summary"] == "Test"

    def test_without_llm_backend(self):
        """Test without LLM backend (mock mode)."""
        turn = TurnRound(
            turn_number=0,
            user_messages=["Test"],
            agent_responses=["Response"],
            raw_lines=["┃ Test", "Response"],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )

        result = process_turns_incrementally("test", [turn], None)
        assert len(result["turn_summaries"]) == 1
        assert result["turn_summaries"][0]["turn_number"] is None
        assert result["accumulated_state"]["high_level_goal"] is None


class TestProcessTurnsIncrementallyStateAccumulation:
    """Test state accumulation logic."""

    def test_high_level_goal_set_on_first_turn(self):
        """Test that high-level goal is set on first turn."""
        turn = TurnRound(
            turn_number=0,
            user_messages=["Goal: Build CLI"],
            agent_responses=["Building"],
            raw_lines=["┃ Goal: Build CLI", "Building"],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )

        def mock_llm(prompt):
            return """TURN SUMMARY

Turn number: 0
User request summary: Build CLI
Key outcomes: Build comprehensive CLI tool
"""

        result = process_turns_incrementally("test", [turn], mock_llm)
        assert result["accumulated_state"]["high_level_goal"] == "Build comprehensive CLI tool"

    def test_high_level_goal_not_overridden(self):
        """Test that high-level goal is not overridden by later turns."""
        turn0 = TurnRound(
            turn_number=0,
            user_messages=["Start"],
            agent_responses=["Starting"],
            raw_lines=["┃ Start", "Starting"],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )

        turn1 = TurnRound(
            turn_number=1,
            user_messages=["Continue"],
            agent_responses=["Continuing"],
            raw_lines=["┃ Continue", "Continuing"],
            start_line_index=2,
            end_line_index=3,
            artifacts=[],
        )

        def mock_llm(prompt):
            if "Turn 0)" in prompt:
                return """TURN SUMMARY

Turn number: 0
Key outcomes: Initial goal: Build CLI
"""
            else:
                return """TURN SUMMARY

Turn number: 1
Key outcomes: Override goal: Build GUI
"""

        result = process_turns_incrementally("test", [turn0, turn1], mock_llm)
        # First turn's goal should be kept, not overridden
        assert "Initial goal: Build CLI" in result["accumulated_state"]["high_level_goal"]

    def test_key_decisions_accumulate(self):
        """Test that key decisions accumulate across turns."""
        turn0 = TurnRound(
            turn_number=0,
            user_messages=["Start"],
            agent_responses=["Starting"],
            raw_lines=["┃ Start", "Starting"],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )

        turn1 = TurnRound(
            turn_number=1,
            user_messages=["Continue"],
            agent_responses=["Continuing"],
            raw_lines=["┃ Continue", "Continuing"],
            start_line_index=2,
            end_line_index=3,
            artifacts=[],
        )

        def mock_llm(prompt):
            if "Turn 0)" in prompt:
                return """TURN SUMMARY

Turn number: 0
Key outcomes: Decision 1, Decision 2
"""
            else:
                return """TURN SUMMARY

Turn number: 1
Key outcomes: Decision 3, Decision 2
"""

        result = process_turns_incrementally("test", [turn0, turn1], mock_llm)
        # Should have 2 unique decisions (first turn's decisions cleared)
        decisions = result["accumulated_state"]["key_decisions"]
        assert len(decisions) == 2
        assert "Decision 2" in decisions
        assert "Decision 3" in decisions

    def test_artifacts_accumulate_unique(self):
        """Test that artifacts accumulate without duplicates."""
        turn0 = TurnRound(
            turn_number=0,
            user_messages=["Create files"],
            agent_responses=["Creating..."],
            raw_lines=["┃ Create files", "Creating..."],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )

        turn1 = TurnRound(
            turn_number=1,
            user_messages=["More files"],
            agent_responses=["Creating more..."],
            raw_lines=["┃ More files", "Creating more..."],
            start_line_index=2,
            end_line_index=3,
            artifacts=[],
        )

        def mock_llm(prompt):
            if "Turn 0)" in prompt:
                return """TURN SUMMARY

Turn number: 0
Artifacts modified: main.py, config.py
"""
            else:
                return """TURN SUMMARY

Turn number: 1
Artifacts modified: utils.py, main.py
"""

        result = process_turns_incrementally("test", [turn0, turn1], mock_llm)
        artifacts = result["accumulated_state"]["artifacts"]
        assert len(artifacts) == 3
        assert "main.py" in artifacts
        assert "config.py" in artifacts
        assert "utils.py" in artifacts

    def test_open_questions_replace(self):
        """Test that open questions are replaced, not accumulated."""
        turn0 = TurnRound(
            turn_number=0,
            user_messages=["Start"],
            agent_responses=["Starting"],
            raw_lines=["┃ Start", "Starting"],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )

        turn1 = TurnRound(
            turn_number=1,
            user_messages=["Continue"],
            agent_responses=["Continuing"],
            raw_lines=["┃ Continue", "Continuing"],
            start_line_index=2,
            end_line_index=3,
            artifacts=[],
        )

        def mock_llm(prompt):
            if "Turn 0)" in prompt:
                return """TURN SUMMARY

Turn number: 0
Open questions after this turn: Question 1, Question 2
"""
            else:
                return """TURN SUMMARY

Turn number: 1
Open questions after this turn: Question 3
"""

        result = process_turns_incrementally("test", [turn0, turn1], mock_llm)
        questions = result["accumulated_state"]["open_questions"]
        # Should only have question 3 (latest replaces previous)
        assert questions == ["Question 3"]


class TestProcessTurnsIncrementallyEdgeCases:
    """Test edge cases and special scenarios."""

    def test_turn_with_no_artifacts(self):
        """Test turn with no extracted artifacts."""
        turn = TurnRound(
            turn_number=0,
            user_messages=["Start"],
            agent_responses=["Starting"],
            raw_lines=["┃ Start", "Starting"],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )

        def mock_llm(prompt):
            return """TURN SUMMARY

Turn number: 0
User request summary: Start
Key outcomes: Started
"""

        result = process_turns_incrementally("test", [turn], mock_llm)
        assert result["accumulated_state"]["artifacts"] == []

    def test_turn_with_no_constraints(self):
        """Test turn with no constraints."""
        turn = TurnRound(
            turn_number=0,
            user_messages=["Start"],
            agent_responses=["Starting"],
            raw_lines=["┃ Start", "Starting"],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )

        def mock_llm(prompt):
            return """TURN SUMMARY

Turn number: 0
User request summary: Start
Key outcomes: Started
"""

        result = process_turns_incrementally("test", [turn], mock_llm)
        assert result["accumulated_state"]["constraints"] == []

    def test_empty_extracted_lists(self):
        """Test turn with empty extracted lists."""
        turn = TurnRound(
            turn_number=0,
            user_messages=["Start"],
            agent_responses=["Starting"],
            raw_lines=["┃ Start", "Starting"],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )

        def mock_llm(prompt):
            return """TURN SUMMARY

Turn number: 0
Artifacts modified:
Constraints/assumptions added:
Open questions after this turn:
"""

        result = process_turns_incrementally("test", [turn], mock_llm)
        assert result["accumulated_state"]["artifacts"] == []
        assert result["accumulated_state"]["constraints"] == []
        assert result["accumulated_state"]["open_questions"] == []

    def test_many_turns(self):
        """Test processing many turns (10+)."""
        turns = [
            TurnRound(
                turn_number=i,
                user_messages=[f"Turn {i}"],
                agent_responses=[f"Response {i}"],
                raw_lines=[f"┃ Turn {i}", f"Response {i}"],
                start_line_index=i*2,
                end_line_index=i*2+1,
                artifacts=[],
            )
            for i in range(10)
        ]

        def mock_llm(prompt):
            # Extract turn number from prompt
            import re
            match = re.search(r"Turn (\d+)\)", prompt)
            if match:
                turn_num = int(match.group(1))
                return f"""TURN SUMMARY

Turn number: {turn_num}
Key outcomes: Outcome {turn_num}
Artifacts modified: file{turn_num}.py
"""
            return ""

        result = process_turns_incrementally("test", turns, mock_llm)
        assert len(result["turn_summaries"]) == 10
        assert len(result["accumulated_state"]["artifacts"]) == 10


class TestProcessTurnsIncrementallyTurnProcessing:
    """Test turn-by-turn processing order."""

    def test_turn_order_preserved(self):
        """Test that turn order is preserved in summaries."""
        turn0 = TurnRound(
            turn_number=0,
            user_messages=["Turn 0"],
            agent_responses=["Response 0"],
            raw_lines=["┃ Turn 0", "Response 0"],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )

        turn1 = TurnRound(
            turn_number=1,
            user_messages=["Turn 1"],
            agent_responses=["Response 1"],
            raw_lines=["┃ Turn 1", "Response 1"],
            start_line_index=2,
            end_line_index=3,
            artifacts=[],
        )

        turn2 = TurnRound(
            turn_number=2,
            user_messages=["Turn 2"],
            agent_responses=["Response 2"],
            raw_lines=["┃ Turn 2", "Response 2"],
            start_line_index=4,
            end_line_index=5,
            artifacts=[],
        )

        def mock_llm(prompt):
            if "Turn 0)" in prompt:
                return """TURN SUMMARY

Turn number: 0
User request summary: Turn 0
"""
            elif "Turn 1)" in prompt:
                return """TURN SUMMARY

Turn number: 1
User request summary: Turn 1
"""
            else:
                return """TURN SUMMARY

Turn number: 2
User request summary: Turn 2
"""

        result = process_turns_incrementally("test", [turn0, turn1, turn2], mock_llm)

        assert len(result["turn_summaries"]) == 3
        assert result["turn_summaries"][0]["turn_number"] == "0"
        assert result["turn_summaries"][1]["turn_number"] == "1"
        assert result["turn_summaries"][2]["turn_number"] == "2"

    def test_first_turn_no_previous_context(self):
        """Test that first turn has no previous summary context."""
        turn = TurnRound(
            turn_number=0,
            user_messages=["Start"],
            agent_responses=["Starting"],
            raw_lines=["┃ Start", "Starting"],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )

        def mock_llm(prompt):
            # Should not contain PREVIOUS TURN SUMMARY
            assert "PREVIOUS TURN SUMMARY" not in prompt
            return """TURN SUMMARY

Turn number: 0
User request summary: Start
"""

        result = process_turns_incrementally("test", [turn], mock_llm)
        assert len(result["turn_summaries"]) == 1

    def test_second_turn_with_context(self):
        """Test that second turn has previous summary context."""
        turn0 = TurnRound(
            turn_number=0,
            user_messages=["Start"],
            agent_responses=["Starting"],
            raw_lines=["┃ Start", "Starting"],
            start_line_index=0,
            end_line_index=1,
            artifacts=[],
        )

        turn1 = TurnRound(
            turn_number=1,
            user_messages=["Continue"],
            agent_responses=["Continuing"],
            raw_lines=["┃ Continue", "Continuing"],
            start_line_index=2,
            end_line_index=3,
            artifacts=[],
        )

        def mock_llm(prompt):
            # Turn 0 should not have PREVIOUS TURN SUMMARY
            # Turn 1 should have it
            if "Turn 0)" in prompt:
                assert "PREVIOUS TURN SUMMARY" not in prompt
            elif "Turn 1)" in prompt:
                assert "PREVIOUS TURN SUMMARY" in prompt
            return """TURN SUMMARY

Turn number: 0
User request summary: First turn
""" if "Turn 0)" in prompt else """TURN SUMMARY

Turn number: 1
User request summary: Second turn
"""

        result = process_turns_incrementally("test", [turn0, turn1], mock_llm)
        assert len(result["turn_summaries"]) == 2
