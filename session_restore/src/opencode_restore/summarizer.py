"""
Summarizer for session transcripts using LLM.
Supports Ollama and extensible backends.
"""

import subprocess
import textwrap
from abc import ABC, abstractmethod
from typing import Optional

from .config import DEFAULT_OLLAMA_BASE_URL, SUMMARY_SCHEMA


class SummarizerBackend(ABC):
    """Abstract base class for LLM backends."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate summary from prompt."""
        pass


class OllamaBackend(SummarizerBackend):
    """Ollama backend for local LLM inference."""

    def __init__(self, model: str, base_url: str = DEFAULT_OLLAMA_BASE_URL):
        self.model = model
        self.base_url = base_url

    def generate(self, prompt: str) -> str:
        """Generate summary using Ollama CLI."""

        proc = subprocess.run(
            ["ollama", "run", self.model],
            input=prompt,
            text=True,
            capture_output=True,
        )

        if proc.returncode != 0:
            raise RuntimeError(
                f"Ollama failed (exit {proc.returncode}):\n{proc.stderr}"
            )

        return proc.stdout.strip()


class Summarizer:
    """Main summarizer orchestrating LLM backends."""

    def __init__(self, backend: Optional[SummarizerBackend] = None):
        self.backend = backend

    def build_prompt(self, session_name: str, transcript: str) -> str:
        """Build prompt for LLM from session name and transcript."""

        return textwrap.dedent(f"""
        You are a session recovery assistant.

        Your job is to reconstruct the CURRENT STATE of an interrupted
        OpenCode session from a transcript.

        Focus on intent, decisions, constraints, and next steps.
        Ignore UI noise, repetition, and dead ends.

        Session name: {session_name}

        {SUMMARY_SCHEMA}

        TRANSCRIPT (most recent portion):
        ----------------
        {transcript}
        ----------------
        """)

    def summarize(self, session_name: str, transcript: str) -> str:
        """Generate session summary from transcript."""

        if not self.backend:
            raise ValueError("No backend configured. Provide a SummarizerBackend.")

        prompt = self.build_prompt(session_name, transcript)
        summary = self.backend.generate(prompt)
        return summary


def create_ollama_summarizer(model: str) -> Summarizer:
    """Factory function to create summarizer with Ollama backend."""

    backend = OllamaBackend(model=model)
    return Summarizer(backend=backend)
