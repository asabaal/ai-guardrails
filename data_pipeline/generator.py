"""
Adversarial Test Data Generator using Local LLM
DMT Protocol: Done Means Taught - Automated weakness detection
"""
import json
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("Warning: ollama not available. Install with: pip install ollama")

class AdversarialGenerator:
    """Generates challenging test cases using local LLM to find parser weaknesses"""
    
    def __init__(self, model_name="qwen3:4b"):
        self.model_name = model_name
        if not OLLAMA_AVAILABLE:
            raise ImportError("ollama package required for adversarial generation")
    
    def generate_contradiction_pairs(self, num_cases=10):
        """Generate fact/contradiction pairs to test logic engine"""
        prompt = f"""Generate {num_cases} JSON objects. Each object should contain two keys: "fact" and "contradiction".
        
Rules:
- The "fact" should be a simple sentence in form "[Subject] is [Object]".
- The "contradiction" should directly contradict the fact using "is not".
- Use varied subjects (animals, objects, people, places).
- Use varied objects (colors, sizes, states, properties).
- Include some complex sentence structures with adjectives.

Example format:
{{"fact": "The sky is blue", "contradiction": "The sky is not blue"}}

Return ONLY a valid JSON array. No extra text."""
        
        return self._query_ollama(prompt)
    
    def generate_synonym_tests(self, num_cases=10):
        """Generate tests using synonyms to challenge semantic understanding"""
        prompt = f"""Generate {num_cases} JSON objects. Each object should contain two keys: "original" and "synonym_variant".
        
Rules:
- Both sentences should express the same meaning using different words
- Focus on color synonyms (red/crimson/scarlet), size synonyms (big/large/huge), etc.
- Use the pattern "[Subject] is [Object]"

Example format:
{{"original": "The car is red", "synonym_variant": "The vehicle is crimson"}}

Return ONLY a valid JSON array. No extra text."""
        
        return self._query_ollama(prompt)
    
    def generate_complex_sentences(self, num_cases=10):
        """Generate grammatically complex sentences to challenge parser"""
        prompt = f"""Generate {num_cases} JSON objects with key "sentence" and expected "parse_result".
        
Rules:
- Sentences should be grammatically complex but still parseable
- Include prepositional phrases, compound subjects, adjectives
- Expected result should show subject, object, negation

Example format:
{{"sentence": "The big brown dog is not on the mat", "parse_result": {{"subject": "the big brown dog", "object": "on the mat", "negated": true}}}}

Return ONLY a valid JSON array. No extra text."""
        
        return self._query_ollama(prompt)
    
    def generate_edge_cases(self, num_cases=10):
        """Generate edge cases that might break the parser"""
        prompt = f"""Generate {num_cases} JSON objects with "sentence" and "should_parse" keys.
        
Rules:
- Include questions, commands, fragments
- Include special characters, numbers, unicode
- Mix parseable and unparseable sentences

Example format:
{{"sentence": "Is the cat black?", "should_parse": false}}

Return ONLY a valid JSON array. No extra text."""
        
        return self._query_ollama(prompt)
    
    def _query_ollama(self, prompt):
        """Query local Ollama model and parse JSON response"""
        if not OLLAMA_AVAILABLE:
            return []
        
        try:
            print(f"Querying {self.model_name} for adversarial test cases...")
            response = ollama.generate(model=self.model_name, prompt=prompt)
            
            # Parse JSON from response
            if response and 'response' in response:
                response_text = response['response'].strip()
                test_cases = json.loads(response_text)
                return test_cases
            else:
                print("No valid response from Ollama")
                return []
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON from LLM response: {e}")
            if response:
                print("Raw response:", response.get('response', 'No response'))
            return []
        except Exception as e:
            print(f"Error querying Ollama: {e}")
            return []

# Standalone execution for testing
if __name__ == "__main__":
    if not OLLAMA_AVAILABLE:
        print("Install ollama package first: pip install ollama")
        sys.exit(1)
    
    generator = AdversarialGenerator()
    
    print("=== Generating Contradiction Pairs ===")
    contradictions = generator.generate_contradiction_pairs(3)
    for case in contradictions:
        print(f"Fact: {case.get('fact')}")
        print(f"Contradiction: {case.get('contradiction')}")
        print()
    
    print("=== Generating Synonym Tests ===")
    synonyms = generator.generate_synonym_tests(3)
    for case in synonyms:
        print(f"Original: {case.get('original')}")
        print(f"Synonym: {case.get('synonym_variant')}")
        print()