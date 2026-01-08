import os
from ironclad_ai_guardrails.ironclad import generate_candidate

os.environ["IRONCLAD_DEBUG"] = "1"

spec = {
    "filename": "compile_email_pattern.py",
    "description": "Compile and return a regex pattern that matches email addresses."
}

candidate = generate_candidate(spec)

print("RESULT:", candidate)
