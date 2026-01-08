import os
from ironclad_ai_guardrails.ironclad import generate_candidate
from unittest.mock import patch

os.environ["IRONCLAD_DEBUG"] = "1"

with patch("ironclad_ai_guardrails.ironclad.ollama.chat") as mock_chat:
    mock_chat.return_value = {
        "message": {
            "content": "{ this is not valid json"
        }
    }

    result = generate_candidate({
        "filename": "broken_func.py",
        "description": "This should fail"
    })

    print("RESULT:", result)
