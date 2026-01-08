import os
from ironclad_ai_guardrails.ironclad import generate_candidate, repair_candidate

os.environ["IRONCLAD_DEBUG"] = "1"

SPEC = "Create a function that compiles email patterns"

print("=== GENERATE ===")
candidate = generate_candidate(SPEC)

if candidate is None:
    print("❌ Generation failed — cannot test repair")
    exit(1)

print("Generated OK")

# 🔥 INTENTIONALLY BREAK THE CODE
print("\n=== CORRUPT CANDIDATE ===")
candidate["code"] = "def compile_email_pattern(\n    return re.compile("  # invalid syntax
print(candidate["code"])

# === REPAIR LOOP ===
print("\n=== REPAIR ===")
repaired = repair_candidate(candidate, "Test traceback")

if repaired is None:
    print("❌ Repair failed (check debug logs)")
else:
    print("✅ Repair returned candidate")
    print(repaired["code"])
