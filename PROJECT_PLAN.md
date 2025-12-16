# AI Guardrails Project Plan

## Executive Summary

This project aims to build a transparent, controllable truthfulness evaluation system that can detect logical inconsistencies in text and eventually verify claims against external sources. The system follows a "human-in-the-loop" philosophy where automated components are exposed through an interactive UI that allows for manual oversight and correction.

## Project Vision & Philosophy

### Core Principles
1. **Transparency**: All logic must be inspectable and understandable
2. **Controllability**: Human operators must have final authority over automated decisions
3. **"Done Means Taught"**: Every component includes validation tools and test suites
4. **Tool-First Development**: Build interactive UIs as primary development environment
5. **Incremental Complexity**: Start with simple logic and gradually add sophistication

### Development Strategy
- **UI-First**: Build interactive tools before backend optimization
- **Human-in-the-Loop**: Assume automated components will be imperfect
- **Local AI Integration**: Leverage Ollama and local models for data generation and testing
- **Modular Architecture**: Separate core logic from data pipeline and testing infrastructure

## Current State Analysis

### What's Built
1. **Core Logic Engine** (`core_logic/reasoner.py`): Basic contradiction detection using regex parsing
2. **Advanced Parser** (`core_logic/parser.py`): spaCy-based linguistic analysis
3. **Interactive UI** (`app.py`): Streamlit-based "Logic Lab" for manual testing and correction
4. **Project Structure**: Organized codebase with separation of concerns

### Technical Issues Identified
- Python environment mismatch between Streamlit execution and spaCy installation
- Need to resolve virtual environment configuration

## Technical Architecture

### Current Structure
```
ai_guardrails/
├── app.py                    # Streamlit UI (Logic Lab)
├── core_logic/
│   ├── __init__.py
│   ├── parser.py            # spaCy-based statement parser
│   └── reasoner.py         # Simple logic engine
└── __pycache__/
```

### Planned Expansion
```
ai_guardrails/
├── app.py                           # Main UI
├── core_logic/
│   ├── __init__.py
│   ├── parser.py                    # Statement parsing
│   ├── reasoner.py                  # Logic engine
│   ├── knowledge_base.py            # Structured knowledge storage
│   └── inference_engine.py          # Rule-based inference
├── data_pipeline/
│   ├── __init__.py
│   ├── generator.py                # LLM-based test data generation
│   ├── validators.py               # Data quality checks
│   └── sources.py                  # External data source connectors
├── tests/
│   ├── test_parser.py
│   ├── test_reasoner.py
│   └── integration_tests.py
├── tools/
│   ├── validate.py                 # CLI validation tools
│   └── data_export.py             # Knowledge base export
└── requirements.txt
```

## Development Roadmap

### Phase 1: Foundational Logician (Current Sprint)
**Goal**: Robust detection of explicit logical contradictions

#### Milestones:
- [x] Basic contradiction detection
- [x] spaCy-based parsing
- [x] Interactive UI for manual correction
- [x] 100% test coverage achieved
- [ ] Fix Python environment issues
- [ ] **Phase 1.5: Conversation Memory System**
- [ ] **Phase 1.5: Enhanced Parser for multiple sentence patterns**
- [ ] **Phase 1.5: Basic Anaphora Resolution**
- [ ] **Phase 1.5: Simple Semantic Normalization**
- [ ] Improve parsing accuracy for complex sentences
- [ ] Add pronoun resolution (anaphora)
- [ ] Implement semantic normalization (synonyms)

#### Success Criteria:
- Parser correctly identifies 95% of contradictions in test dataset
- UI provides clear visibility into parsing decisions
- Human correction workflow is seamless

### Phase 1.5: Contextual Foundation (NEW)
**Goal**: Build robust foundation for contextual reasoning

#### Core Components to Build:

**1. Conversation Memory System**
```python
class ConversationMemory:
    def __init__(self):
        self.statements = []  # Chronological statement history
        self.entities = {}    # Tracked entities and their attributes
        self.pronoun_map = {} # "it" → "the cat", "he" → "john"
    
    def add_statement(self, parsed_statement):
        self.statements.append(parsed_statement)
        self.update_entity_tracker(parsed_statement)
        self.update_pronoun_mapping(parsed_statement)
```

**2. Enhanced Parser**
- **Current**: Only "X is Y" patterns
- **Phase 1.5**: Multiple sentence structures
```python
# Patterns to support:
"The cat is black"           # Current
"The cat has black fur"       # New: possession
"The cat seems black"         # New: perception  
"The cat becomes black"        # New: change over time
"The cat, which is big, is black"  # New: relative clauses
```

**3. Basic Anaphora Resolution**
- **Current**: "It is black" → subject="it"
- **Phase 1.5**: "It is black" → subject="the cat" (from previous context)
```python
def resolve_pronoun(self, pronoun, conversation_history):
    # Look back 3-5 statements for noun phrases
    # Find most recent matching entity (gender, number, etc.)
    # Return resolved entity or None
```

**4. Simple Semantic Normalization**
- **Current**: "red" ≠ "crimson" (different contradiction)
- **Phase 1.5**: "red" ≈ "crimson" (same meaning)
```python
semantic_groups = {
    'colors': ['red', 'crimson', 'scarlet', 'burgundy'],
    'sizes': ['big', 'large', 'huge', 'enormous'],
    'states': ['happy', 'joyful', 'cheerful', 'glad']
}
```

#### Concrete Examples of Phase 1.5 Capabilities:

**Conversation Flow:**
```
User: "The cat is on the mat."
System: [stores: cat.location = mat]

User: "It is sleeping."  
System: [resolves "it" → "the cat"]
System: [stores: cat.state = sleeping]

User: "The feline is awake."
System: [normalizes "feline" → "cat"]
System: [detects contradiction: cat.state = sleeping vs awake]
```

#### Technical Implementation Plan:

**Week 1: Conversation Memory**
- Extend `SimpleLogicEngine` → `ContextualLogicEngine`
- Add statement history tracking
- Implement basic entity tracking
- Update UI to show conversation context

**Week 2: Enhanced Parser**
- Extend `StatementParser` to handle multiple sentence patterns
- Add dependency parsing for complex structures
- Implement basic pronoun detection
- Update tests for new patterns

**Week 3: Anaphora Resolution**
- Implement pronoun-to-entity mapping
- Add gender/number agreement checking
- Handle ambiguous pronouns
- Create tests for resolution accuracy

**Week 4: Semantic Normalization**
- Build semantic group mappings
- Implement synonym detection
- Add semantic contradiction detection
- Create adversarial tests for semantic edge cases

#### UI Enhancements for Phase 1.5:

**Context Panel:**
```
Conversation History:
1. The cat is on the mat. [cat.location=mat]
2. It is sleeping. [cat.state=sleeping] 
3. The feline is awake. [CONTRADICTION!]

Entity Tracker:
- cat: location=mat, state=sleeping→awake (contradiction)
- mat: location_of=cat
```

**Resolution Tools:**
- "Resolve 'it' → 'the cat'" button
- "Accept semantic match: feline≈cat" checkbox
- "Ignore contradiction" option for valid changes

#### Success Metrics for Phase 1.5:
1. **Conversation Memory**: Track 10+ statements accurately
2. **Pronoun Resolution**: 80% accuracy on simple cases
3. **Semantic Matching**: Handle basic synonym groups
4. **Enhanced Contradictions**: Detect semantic inconsistencies
5. **UI Integration**: Full context visualization

### Phase 2: Contextual Reasoner
**Goal**: Understand temporal logic and basic inference

#### Technical Challenges:
- **Temporal Logic**: Handle state changes over time
- **Rule-Based Inference**: Apply general rules to specific facts
- **Mutual Exclusion**: Infer opposite states (light on → light not off)

#### Implementation:
```python
# Example rule system
rules = [
    {"if": {"subject": "X", "object": "dog"}, "then": {"subject": "X", "object": "mammal"}},
    {"if": {"subject": "X", "object": "light", "negated": False}, "then": {"subject": "X", "object": "light", "negated": True}}
]
```

### Phase 3: External Grounding Agent
**Goal**: Connect internal logic to verifiable external sources

#### Components:
- **Structured Data Queries**: Wikidata API integration
- **Unstructured Data Search**: Web search with source reliability scoring
- **Source Trust Model**: Weighted confidence based on source authority

### Phase 4: Conversational Truth Evaluator
**Goal**: Real-time evaluation of multi-turn conversations

#### Features:
- Multi-claim deconstruction
- Subjectivity detection
- Probabilistic truth assessment
- Real-time consistency monitoring

### Phase 5: Autonomous Truth Agent
**Goal**: Proactive truth-seeking and synthesis

#### Capabilities:
- Consensus synthesis across multiple sources
- Curiosity-driven knowledge gap identification
- Real-time monitoring of data streams

## Immediate Action Items

### 1. Fix Environment Issues (Priority: Critical)
```bash
# Use virtual environment's Python directly
python -m streamlit run app.py
# Or ensure streamlit is installed in correct environment
pip install streamlit spacy
python -m spacy download en_core_web_sm
```

### 2. Phase 1.5: Conversation Memory System (Priority: High)
- Extend `SimpleLogicEngine` → `ContextualLogicEngine`
- Add statement history tracking
- Implement basic entity tracking
- Update UI to show conversation context

### 3. Phase 1.5: Enhanced Parser (Priority: High)
- Extend `StatementParser` to handle multiple sentence patterns
- Add dependency parsing for complex structures
- Implement basic pronoun detection
- Update tests for new patterns

### 4. Phase 1.5: Anaphora Resolution (Priority: High)
- Implement pronoun-to-entity mapping
- Add gender/number agreement checking
- Handle ambiguous pronouns
- Create tests for resolution accuracy

### 5. Phase 1.5: Semantic Normalization (Priority: Medium)
- Build semantic group mappings
- Implement synonym detection
- Add semantic contradiction detection
- Create adversarial tests for semantic edge cases

### 6. Expand UI Capabilities (Priority: Medium)
- Add knowledge base visualization
- Implement statement history tracking
- Create rule management interface
- Add context panel for conversation tracking

### 7. Integrate Local AI (Priority: Medium)
- Set up Ollama integration for adversarial testing
- Create automated test case generation
- Implement LLM-assisted parsing validation

## Testing Strategy

### "Done Means Taught" Approach
Every component includes:
1. **Unit Tests**: Verify individual functions work correctly
2. **Integration Tests**: Ensure components work together
3. **Adversarial Tests**: Use local LLMs to find edge cases
4. **Human Validation**: UI-based testing with manual oversight

### Test Data Generation
```python
# Use Ollama to generate challenging test cases
def generate_adversarial_examples():
    prompt = """
    Generate sentence pairs that test logical consistency:
    1. Direct contradictions
    2. Synonym-based contradictions
    3. Complex sentence structures
    4. Edge cases with pronouns
    """
    # Query local LLM for diverse test cases
```

## Success Metrics

### Phase 1.5 Success Metrics
1. **Conversation Memory**: Track 10+ statements accurately
2. **Pronoun Resolution**: 80% accuracy on simple cases
3. **Semantic Matching**: Handle basic synonym groups
4. **Enhanced Contradictions**: Detect semantic inconsistencies
5. **UI Integration**: Full context visualization

### Technical Metrics
- **Parsing Accuracy**: % of sentences correctly parsed
- **Contradiction Detection**: % of contradictions correctly identified
- **False Positive Rate**: % of non-contradictions flagged incorrectly
- **UI Responsiveness**: Time from input to feedback
- **Context Memory Accuracy**: % of entities correctly tracked across conversation

### User Experience Metrics
- **Correction Frequency**: How often humans need to override automated decisions
- **Learning Rate**: Reduction in correction frequency over time
- **Task Completion Time**: Time to validate a set of statements
- **Pronoun Resolution Acceptance**: % of pronoun resolutions accepted by users
- **Semantic Match Accuracy**: % of semantic normalizations confirmed as correct

## Risk Assessment & Mitigation

### Technical Risks
1. **Parser Brittleness**: Mitigate with extensive testing and human oversight
2. **Knowledge Base Scalability**: Implement efficient data structures and indexing
3. **External Source Reliability**: Develop source trust scoring system
4. **Phase 1.5 Scope Creep**: Risk of jumping to Phase 2 without solid foundation
5. **Pronoun Resolution Complexity**: Ambiguous references may frustrate users
6. **Semantic Normalization Overreach**: False semantic matches could create incorrect contradictions

### Phase 1.5 Risk Mitigation
1. **Incremental Development**: Build each component separately with clear success criteria
2. **Human-in-the-Loop**: All automated resolutions require user confirmation
3. **Conservative Semantic Matching**: Only normalize high-confidence synonym groups
4. **Extensive Testing**: Use adversarial testing to find edge cases before deployment
5. **User Feedback Integration**: Track which automated decisions are overridden

### Philosophical Risks
1. **Over-automation**: Maintain human-in-the-loop at all decision points
2. **Black Box Components**: Keep all logic transparent and inspectable
3. **Truth Definition Complexity**: Start with demonstrable facts, expand gradually

## Conclusion

This project represents a fundamental shift from building automated AI systems to creating transparent tools that augment human reasoning. The "Logic Lab" approach ensures we maintain control and understanding while progressively building more sophisticated capabilities.

The current foundation is solid, with working contradiction detection, parsing, and an interactive UI. The immediate focus should be on resolving environment issues and enhancing parser's accuracy while maintaining transparent, human-in-the-loop philosophy that defines this project.

---

*Document created: November 16, 2025*
*Based on conversation analysis and code review*