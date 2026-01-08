import json
from typing import Dict, Any


ENUMERATION_SCHEMA = {
    "type": "object",
    "properties": {
        "functions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "inputs": {"type": "array", "items": {"type": "string"}},
                    "outputs": {"type": "string"},
                    "side_effects": {"type": "string"},
                    "dependencies": {"type": "array", "items": {"type": "string"}},
                    "estimated_implementation_order": {"type": "integer"}
                },
                "required": ["name", "description", "inputs", "outputs", "side_effects"]
            }
        },
        "implementation_order": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Ordered list of function names representing optimal implementation order"
        },
        "questions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Any blocking questions that need clarification before proceeding"
        },
        "is_complete": {
            "type": "boolean",
            "description": "True if enumeration is complete with no blocking questions"
        }
    },
    "required": ["functions", "implementation_order", "questions", "is_complete"]
}


IMPLEMENTATION_PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "function_name": {"type": "string"},
        "contract": {
            "type": "object",
            "properties": {
                "description": {"type": "string"},
                "input_validation": {"type": "array", "items": {"type": "string"}},
                "output_format": {"type": "string"},
                "raises": {"type": "array", "items": {"type": "string"}}
            }
        },
        "implementation": {
            "type": "string",
            "description": "The actual Python function code as a string"
        },
        "file_path": {"type": "string"},
        "file_content": {
            "type": "string",
            "description": "Full content of the file to write"
        },
        "files_to_create": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"}
                }
            }
        },
        "questions": {
            "type": "array",
            "items": {"type": "string"}
        },
        "is_complete": {"type": "boolean"}
    },
    "required": ["function_name", "contract", "implementation", "file_path", "file_content", "questions", "is_complete"]
}


TEST_PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "function_name": {"type": "string"},
        "test_cases": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "inputs": {"type": "object"},
                    "expected_output": {"type": "object"},
                    "expected_exception": {"type": "string"},
                    "category": {
                        "type": "string",
                        "enum": ["normal", "edge", "failure"]
                    }
                },
                "required": ["name", "description", "category"]
            }
        },
        "coverage_analysis": {
            "type": "string",
            "description": "Explanation of how this achieves 100.00% statement coverage"
        },
        "questions": {
            "type": "array",
            "items": {"type": "string"}
        },
        "is_complete": {"type": "boolean"}
    },
    "required": ["function_name", "test_cases", "coverage_analysis", "questions", "is_complete"]
}


UI_GENERATION_SCHEMA = {
    "type": "object",
    "properties": {
        "function_name": {"type": "string"},
        "html_content": {
            "type": "string",
            "description": "The complete HTML content for the verification UI"
        },
        "sample_inputs": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "label": {"type": "string"},
                    "inputs": {"type": "object"}
                }
            }
        },
        "run_instructions": {
            "type": "string",
            "description": "Instructions for running the UI locally"
        },
        "questions": {
            "type": "array",
            "items": {"type": "string"}
        },
        "is_complete": {"type": "boolean"}
    },
    "required": ["function_name", "html_content", "sample_inputs", "run_instructions", "questions", "is_complete"]
}


SPEC_GENERATION_SCHEMA = {
    "type": "object",
    "properties": {
        "module_name": {
            "type": "string",
            "description": "Name of the module/package"
        },
        "module_description": {
            "type": "string",
            "description": "Brief description of what the module does"
        },
        "required_public_functions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "inputs": {"type": "array", "items": {"type": "string"}},
                    "outputs": {"type": "string"},
                    "side_effects": {"type": "string"}
                },
                "required": ["name", "description", "inputs", "outputs", "side_effects"]
            }
        }
    },
    "required": ["module_name", "module_description", "required_public_functions"]
}


def validate_output(output: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    try:
        from jsonschema import validate
        validate(instance=output, schema=schema)
        return True
    except Exception as e:
        raise ValueError(f"Schema validation failed: {e}")
