import os
import sys
sys.path.insert(0, '/mnt/storage/repos/ai-guardrails/ironclad/src')
from ironclad_ai_guardrails.ironclad import repair_candidate

os.environ['IRONCLAD_DEBUG'] = '1'

# Mock ollama to return invalid JSON
class MockOllama:
    def chat(self, model, messages):
        return {
            'message': {
                'content': '{"filename": "bad", "code": "def bad():\\n    return bad\\n"}'
            }
        }

# Patch it
import ironclad_ai_guardrails.ironclad as ironclad_module
original_chat = ironclad_module.ollama.chat
ironclad_module.ollama.chat = MockOllama().chat

# Call repair
candidate = {
    'filename': 'test',
    'code': 'def test(): pass',
    'test': 'def test_test(): assert test()'
}
traceback_log = 'Test traceback'
repaired = repair_candidate(candidate, traceback_log)

print('\n=== DEBUG MODE TEST ===')
print('IRONCLAD_DEBUG:', os.environ.get('IRONCLAD_DEBUG'))
print('\n=== REPAIR CALL ===')
print('Repaired:', repaired is not None)
print('\n=== CHECK DEBUG ARTIFACTS ===')

import glob
debug_files = sorted(glob.glob('build/.ironclad_debug/repair*.txt'))
if debug_files:
    print('Found', len(debug_files), 'debug file(s):')
    for df in debug_files:
        with open(df, 'r') as f:
            content = f.read()
            print('File:', df)
            phase_in_file = 'Phase: repair' in content
            msg_in_file = 'Message: Repair output was not valid JSON' in content
            raw_data_in_file = 'RAW DATA:' in content
            print('Phase check:', 'Phase: repair' in content)
            print('Message check:', 'Message: Repair output was not valid JSON' in content)
            print('Raw data check:', 'RAW DATA:' in content)
else:
    print('No debug files found')
