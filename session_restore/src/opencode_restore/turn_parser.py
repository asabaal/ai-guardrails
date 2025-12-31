"""
Parser for OpenCode conversations into turn rounds.
Handles turn detection and artifact extraction from parsed transcripts.
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from .config import (
    TOOL_PATTERNS,
)


class ArtifactActionType(Enum):
    READ = 'read'
    EDITED = 'edited'
    CREATED = 'created'


@dataclass
class ArtifactAction:
    file_path: str
    action_type: ArtifactActionType
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


class TurnParser:
    """Parser for conversation turns and artifact extraction."""

    def __init__(self):
        self.user_message_pattern = re.compile(r'┃\s+(.+?)\s+┃')
        self.username_timestamp_pattern = re.compile(r'(\w+)\s+\(\d{1,2}:\d{2}\s+[AP]M\)')
        self.read_file_pattern = re.compile(TOOL_PATTERNS['read_file'])
        self.edit_file_pattern = re.compile(TOOL_PATTERNS['edit_file'])
        self.shell_cd_pattern = re.compile(TOOL_PATTERNS['shell_cd'])

    def extract_user_message(self, line: str) -> Optional[str]:
        """Extract user message content from line."""

        match = self.user_message_pattern.search(line)
        if match:
            return match.group(1).strip()
        return None

    def is_username_timestamp(self, line: str) -> bool:
        """Check if line contains username and timestamp pattern."""

        return bool(self.username_timestamp_pattern.search(line))

    def extract_artifacts(self, lines: List[str], start_idx: int, end_idx: Optional[int] = None) -> List[ArtifactAction]:
        """Extract artifact actions (read, edit, create) from lines."""

        artifacts = []
        actual_end_idx = end_idx if end_idx is not None else len(lines)

        for i, line in enumerate(lines[start_idx:actual_end_idx], start=start_idx):
            for pattern_str, pattern in [
                ('read', self.read_file_pattern),
                ('edit', self.edit_file_pattern),
            ]:
                match = pattern.search(line)
                if match:
                    file_path = match.group(1)
                    action_type = ArtifactActionType.READ if pattern_str == 'read' else ArtifactActionType.EDITED
                    artifacts.append(ArtifactAction(
                        file_path=file_path,
                        action_type=action_type,
                        line_number=i,
                    ))
            match = self.shell_cd_pattern.search(line)
            if match and match.group(1):
                artifacts.append(ArtifactAction(
                    file_path=match.group(1),
                    action_type=ArtifactActionType.READ,
                    line_number=i,
                ))
        return artifacts

    def parse_turns(self, content_lines: List[str]) -> List[TurnRound]:
        """Parse conversation content into turn rounds."""

        turns = []
        current_turn_user_messages = []
        current_turn_agent_responses = []
        current_turn_start_idx = 0
        turn_number = 0

        for i, line in enumerate(content_lines):
            user_message = self.extract_user_message(line)

            if user_message is not None:
                if current_turn_user_messages and not current_turn_agent_responses:
                    current_turn_user_messages.append(user_message)
                elif current_turn_agent_responses:
                    turns.append(TurnRound(
                        turn_number=turn_number,
                        user_messages=current_turn_user_messages,
                        agent_responses=current_turn_agent_responses,
                        raw_lines=content_lines[current_turn_start_idx:i],
                        start_line_index=current_turn_start_idx,
                        end_line_index=i - 1,
                        artifacts=self.extract_artifacts(
                            content_lines,
                            current_turn_start_idx,
                            i,
                        ),
                    ))
                    turn_number += 1
                    current_turn_user_messages = [user_message]
                    current_turn_agent_responses = []
                    current_turn_start_idx = i
                else:
                    current_turn_user_messages = [user_message]
                    current_turn_agent_responses = []
                    current_turn_start_idx = i
            elif self.is_username_timestamp(line):
                pass
            elif current_turn_user_messages or current_turn_agent_responses:
                current_turn_agent_responses.append(line)

        if current_turn_user_messages or current_turn_agent_responses:
            turns.append(TurnRound(
                turn_number=turn_number,
                user_messages=current_turn_user_messages,
                agent_responses=current_turn_agent_responses,
                raw_lines=content_lines[current_turn_start_idx:],
                start_line_index=current_turn_start_idx,
                end_line_index=len(content_lines) - 1,
                artifacts=self.extract_artifacts(
                    content_lines,
                    current_turn_start_idx,
                    len(content_lines),
                ),
            ))

        return turns
