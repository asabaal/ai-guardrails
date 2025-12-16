# Overseer: AI Logic Analysis Tool - Project Organization Plan

## Project Overview

Overseer is an AI safety tool that analyzes text to extract and validate logical reasoning. The system processes AI-generated text to identify logical structures, detect fallacies, and provide human-readable analysis of reasoning soundness.

## Architecture

The project follows a 4-layer architecture:

1. **Layer 1: Segmentation** - Break text into logical steps
2. **Layer 2: Logic Extraction** - Convert steps to structured objects  
3. **Layer 3: Logic Evaluation** - Check entailment, contradictions, fallacies
4. **Layer 4: Human-Safe Output** - Generate readable analysis reports

## Directory Structure

```
overseer/
├── README.md                    # Project overview and mission
├── requirements.txt              # Python dependencies
├── setup.py                     # Package configuration
│
├── config/                      # Core configuration and taxonomies
│   ├── logical_primitives.yaml  # The 7 core logical categories
│   ├── extraction_rules.yaml    # Prompt templates and rules
│   └── validation_criteria.yaml # Success criteria for each phase
│
├── test_cases/                  # Reference examples organized by category
│   ├── simple_logic/            # Examples A-C (baseline tests)
│   ├── fallacies/              # Examples D-F (logical fallacies)
│   ├── chains/                 # Examples G-I (multi-step reasoning)
│   ├── realistic_ai/           # Examples J-L (LLM-style reasoning)
│   ├── contradictions/         # Examples M-N (mixed truth/contradiction)
│   ├── misbehavior/            # Examples O-R (safety-critical errors)
│   └── test_suite.py           # Automated test runner
│
├── src/
│   └── overseer/
│       ├── __init__.py
│       ├── layer1/             # Phase 1: Segmentation
│       │   ├── __init__.py
│       │   ├── extractor.py    # LLM-based step extraction
│       │   ├── splitter.py     # Rule-based fallback
│       │   ├── normalizer.py   # Text cleaning and standardization
│       │   └── aggregator.py   # Combine results into final steps
│       │
│       ├── layer2/             # Phase 2: Logic Extraction (future)
│       ├── layer3/             # Phase 3: Logic Evaluation (future)
│       ├── layer4/             # Phase 4: Human-Safe Output (future)
│       │
│       ├── core/               # Shared utilities
│       │   ├── llm_interface.py # Local model communication
│       │   ├── primitives.py   # Logical primitive definitions
│       │   └── utils.py        # Common helper functions
│       │
│       └── cli.py              # Command-line interface
│
├── tests/                      # Unit tests for each component
│   ├── test_layer1/
│   ├── test_layer2/
│   └── integration/
│
├── docs/                       # Documentation and specifications
│   ├── phase1_spec.md         # Layer 1 detailed specification
│   ├── logical_grammar.md     # Explanation of the 7 primitives
│   └── development_workflow.md # Phase-by-phase plan
│
└── experiments/                # Sandbox for trying new approaches
    ├── prompts/
    ├── fallback_rules/
    └── validation_experiments/
```

## Organizational Principles

### 1. Test-Case-Driven Development
- Examples A-R from conversation become authoritative test suite
- Each category gets dedicated directory with expected inputs/outputs
- Validation criteria defined by handling of these reference cases

### 2. Phase-Based Architecture
- Clear separation between 4 layers
- Each layer independently testable and validateable
- Progress measured by phase completion criteria

### 3. Configuration-Driven Logic
- 7 logical primitives defined as configurable taxonomy
- Prompt templates and extraction rules externalized
- Easy iteration without code changes

### 4. Safety-First Validation
- Misbehavior examples (O-R) prioritized as test cases
- Each phase must pass safety-critical tests before advancing
- Human-readable validation reports

## Logical Primitives Taxonomy

The foundation of the system is a 7-category logical primitive taxonomy:

1. **Atomic Assertions** - "X is Y", "X has property P", "X does action A"
2. **Conditional Statements** - "If X, then Y", "X implies Y", "Y because X"
3. **Causal Statements** - "X causes Y", "X leads to Y", "X results in Y"
4. **Generalizations** - "All X are Y", "Some X are Y", "Most X are Y", "No X are Y"
5. **Quantitative/Comparative Statements** - "X is greater than Y", "X increases Y"
6. **Normative/Prescriptive Statements** - "You should", "You must", "Therefore we must"
7. **Conclusions** - "Therefore", "Thus", "So", "In conclusion", "Hence"

## Development Workflow

### Phase 1: Layer 1 (Segmentation)
- Extract reasoning steps using LLM prompts
- Implement rule-based fallback splitter
- Normalize and aggregate results
- Validate against simple logic and chain examples

### Phase 2: Layer 2 (Logic Extraction)
- Convert steps to structured logic objects
- Classify statement types using the 7 primitives
- Extract entities and relationships
- Validate against fallacy and contradiction examples

### Phase 3: Layer 3 (Logic Evaluation)
- Implement NLI-based entailment checking
- Build reasoning graphs
- Create fallacy pattern recognition
- Validate against realistic AI and misbehavior examples

### Phase 4: Layer 4 (Human-Safe Output)
- Generate readable analysis reports
- Implement severity classification
- Create CLI interface
- Final integration testing

## Next Steps

1. Extract and organize test cases from conversation into structured test suite
2. Define logical primitives taxonomy as core configuration
3. Create Phase 1 (Layer 1: Segmentation) module structure
4. Design validation framework for each development phase

This plan ensures test cases drive development, each phase is independently validateable, and the logical primitives taxonomy remains the authoritative foundation for the entire system.