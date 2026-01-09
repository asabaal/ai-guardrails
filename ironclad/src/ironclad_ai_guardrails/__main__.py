"""
Entry point for ironclad package.

This module prevents RuntimeWarning by only executing CLI logic
when run as a module, not when imported as a package.
"""

from ironclad_ai_guardrails.ironclad import main

if __name__ == "__main__":
    main()
