"""
Ironclad - AI-powered code generation and verification

This package provides tools for generating Python code using AI models
and automatically verifying the generated code through comprehensive testing.
"""

from ironclad_ai_guardrails.ironclad import (
    clean_json_response,
    generate_candidate,
    validate_candidate,
    save_brick,
    repair_candidate,
    main,
    DEFAULT_MODEL_NAME,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SYSTEM_PROMPT,
    MAX_RETRIES
)

__version__ = "1.0.0"

__all__ = [
    "clean_json_response",
    "generate_candidate",
    "validate_candidate",
    "save_brick",
    "repair_candidate",
    "main",
    "DEFAULT_MODEL_NAME",
    "DEFAULT_OUTPUT_DIR",
    "DEFAULT_SYSTEM_PROMPT",
    "MAX_RETRIES",
]
