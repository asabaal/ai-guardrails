import os
import re

# All files that need fixing
for filename in [f for f in os.listdir('.') if f.endswith('.py') and f != '__init__.py']:
    with open(filename, 'r') as f:
        content = f.read()
    
    # Replace ALL imports to use absolute package paths
    # Pattern 1: from .module import -> from ironclad_ai_guardrails.module import
    content = re.sub(r'^from \.([a-z_][a-z_]*) import', r'from ironclad_ai_guardrails.\1 import', content)
    
    # Pattern 2: from ..module import -> from ironclad_ai_guardrails.module import  
    content = re.sub(r'^from \.\.([a-z_][a-z_]*) import', r'from ironclad_ai_guardrails.\1 import', content)
    
    # Pattern 3: from .import X -> import X (for ollama)
    content = re.sub(r'^from \.import ollama', r'import ollama', content)
    
    # Pattern 4: from ironclad_ai_guardrails.typing import -> from typing import
    content = re.sub(r'from ironclad_ai_guardrails\.typing import', r'from typing import', content)
    
    # Pattern 5: from ironclad_ai_guardrails.dataclasses import -> from dataclasses import
    content = re.sub(r'from ironclad_ai_guardrails\.dataclasses import', r'from dataclasses import', content)
    
    # Pattern 6: from ironclad_ai_guardrails.enum import -> from enum import
    content = re.sub(r'from ironclad_ai_guardrails\.enum import', r'from enum import', content)
    
    if content != f.read():
        with open(filename, 'w') as f:
            f.write(content)
            print(f'Fixed: {filename}')

print('Done fixing all imports')
