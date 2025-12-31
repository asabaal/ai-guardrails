"""
opencode-restore - Parse and summarize OpenCode session logs.
"""

from .config import (
    DEFAULT_MODEL,
    DEFAULT_MAX_LINES,
    DEFAULT_OUTPUT_FORMAT,
    SUMMARY_SCHEMA,
    get_default_output_path,
    TURN_SUMMARY_SCHEMA,
    EVIDENCE_SEARCH_PROMPT_TEMPLATE,
    EVIDENCE_SEARCH_CONTINUE_PROMPT_TEMPLATE,
)
from .parser import LogParser, ParsedTranscript, ScriptHeader
from .summarizer import Summarizer, OllamaBackend, create_ollama_summarizer
from .turn_parser import TurnParser, TurnRound, ArtifactAction, ArtifactActionType
from .turn_summarizer import process_turns_incrementally
from .evidence_gatherer import run_agentic_evidence_gathering, EvidenceSearchTools

__version__ = "2.0.0"

__all__ = [
    "DEFAULT_MODEL",
    "DEFAULT_MAX_LINES",
    "DEFAULT_OUTPUT_FORMAT",
    "SUMMARY_SCHEMA",
    "get_default_output_path",
    "LogParser",
    "ParsedTranscript",
    "ScriptHeader",
    "Summarizer",
    "OllamaBackend",
    "create_ollama_summarizer",
    "TurnParser",
    "TurnRound",
    "ArtifactAction",
    "ArtifactActionType",
    "process_turns_incrementally",
    "run_agentic_evidence_gathering",
    "EvidenceSearchTools",
]
