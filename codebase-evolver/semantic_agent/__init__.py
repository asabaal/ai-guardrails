"""
Semantic Change Agent v1

A codebase-aware change evaluator and executor that uses Pyright as a
deterministic semantic oracle and local LLM as a constrained reasoner.

This system:
- Evaluates whether features fit existing architecture
- Proposes structural refactors when needed
- Generates minimal, correct code changes
- Enforces semantic correctness through LSP grounding
"""

__version__ = "0.1.0"
