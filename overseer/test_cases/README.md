# Overseer Test Suite

This directory contains the ground truth test cases for the Overseer AI logic analysis tool.

## Structure

Each category contains a `test_cases.json` file with machine-readable test data:

- **simple_logic/**: Basic valid/invalid reasoning (Examples A-C)
- **fallacies/**: Logical fallacy detection (Examples D-F)  
- **chains/**: Multi-step reasoning chains (Examples G-I)
- **realistic_ai/**: LLM-style reasoning patterns (Examples J-L)
- **contradictions/**: Contradiction detection (Examples M-N)
- **misbehavior/**: AI agent misbehavior patterns (Examples O-P)
- **safety_protocols/**: Safety-critical violations (Examples Q-R)

## Test Case Schema

Each test case includes:

```json
{
  "id": "A",
  "category": "simple_logic", 
  "description": "Brief description",
  "input_text": "Raw reasoning text to analyze",
  "expected_segments": ["List of expected logical steps"],
  "expected_logic_objects": [
    {
      "text": "Original text segment",
      "type": "atomic_assertion|conditional|causal|generalization|quantitative|normative|conclusion",
      "entities": ["List of entities"],
      "relationship": "Type of relationship"
    }
  ],
  "expected_evaluation": {
    "valid_reasoning": true/false,
    "fallacies": ["List of detected fallacies"],
    "contradictions": ["List of contradictions"],
    "unsupported_inferences": ["List of unsupported steps"],
    "severity": "none|minor|major|critical"
  },
  "metadata": {
    "test_purpose": "What this validates",
    "complexity": "simple|medium|high",
    "logical_steps": 3,
    "safety_critical": true/false
  }
}
```

## Usage

These test cases serve as the authoritative ground truth for:

1. **Layer 1 (Segmentation)**: Validate correct step extraction
2. **Layer 2 (Logic Extraction)**: Validate logical primitive classification
3. **Layer 3 (Evaluation)**: Validate fallacy and contradiction detection
4. **Layer 4 (Output)**: Validate human-readable reporting

## Validation Criteria

Each development phase must achieve:
- **Simple Logic**: 95%+ accuracy on examples A-C
- **Fallacies**: 90%+ detection rate on D-F
- **Chains**: 85%+ accuracy on G-I
- **Realistic AI**: 80%+ accuracy on J-L
- **Contradictions**: 95%+ detection on M-N
- **Misbehavior**: 100% detection on O-P (safety critical)
- **Safety Protocols**: 100% detection on Q-R (safety critical)