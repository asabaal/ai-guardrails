# Semantic Change Agent: Design Plan v1

**Status:** Design Phase Complete, Implementation Phase Started
**Date:** January 1, 2026
**Protocol:** AI Safety Development Protocols v1.4

## Overview

This document describes the design plan for a Semantic Change Agent that uses Pyright as a deterministic semantic oracle and local LLM (GPT-OSS20B) as a constrained reasoner to evaluate and execute code changes with structural safety guarantees.

## High Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLI Interface                            │
│                   (Developer / Programmatic)                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │ Natural Language Request
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Orchestrator Layer                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 1. Goal Extraction & Constraint Parsing                │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Semantic Oracle Layer (Pyright)                │
│  Extracted Facts:                                               │
│  - Symbol definitions and locations                           │
│  - Symbol references (cross-file)                             │
│  - Type information and signatures                            │
│  - Dependency graphs (imports, inheritance)                  │
│  - Module boundaries and exports                              │
│  - Diagnostic information (errors, warnings)                 │
│  - Function/class complexity metrics                          │
└───────────────────────────┬─────────────────────────────────────┘
                            │ Structured JSON Facts
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Reasoning Layer (Ollama)                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Decision Phase                                           │  │
│  │  Output: One of {PROCEED, REFACTOR, ABORT}              │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Planning Phase (if PROCEED or REFACTOR)                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Execution Layer                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ File Operations & Verification                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Repair Loop (if verification fails)                     │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Phase by Phase Workflow

### Phase 0: Input Processing
Parse natural language into structured goal and constraints

### Phase 1: Oracle Interrogation
Extract semantic facts using Pyright queries

### Phase 2: Feasibility Decision
Model evaluates: PROCEED_DIRECTLY, REFACTOR_FIRST, or ABORT_OUT_OF_SCOPE

### Phase 3: Human Approval #1
Present decision and rationale, request confirmation

### Phase 4: Planning
Generate refactor plan or feature scaffold plan

### Phase 5: Human Approval #2
Present plan, request confirmation before execution

### Phase 6: Execution
Apply changes step-by-step with verification

### Phase 7: Repair Loop
Fix single failures with minimal diffs and stop conditions

### Phase 8: Completion
Generate summary report and exit

## V1 Scope

### IN SCOPE
- Feasibility evaluation (PROCEED/REFACTOR/ABORT)
- Structural refactoring (extract interface, extract method, split module, etc.)
- Minimal feature scaffolding
- Test-driven repair loop
- Python codebases only
- Pyright LSP only
- CLI tool (single-shot execution)

### OUT OF SCOPE
- Multi-language support
- New module creation from scratch
- Architectural redesign
- Cross-repo changes
- Performance optimization
- UI/UX improvements
- Background processes
- Multi-agent coordination

## Risk Analysis

### Critical Risks
1. **Oracle Failure** - Pyright crashes or hangs
2. **Model Hallucination** - Model ignores oracle facts
3. **Scope Explosion** - Agent attempts changes beyond intended scope
4. **Repair Loop Recursion** - Agent keeps applying repairs without convergence
5. **Type Contract Degradation** - Introduction of type ambiguity

### Failure Modes
All critical risks have defined mitigation strategies, detection methods, and recovery plans.

## Incremental Build Order

### Milestone 0: Foundation (Week 1-2)
- Pyright daemon wrapper
- CLI scaffold
- Basic query methods

### Milestone 1: Goal Extraction & Oracle Interrogation (Week 2-3)
- Goal extraction module
- Targeted oracle queries
- Fact normalization

### Milestone 2: Feasibility Decision Engine (Week 3-4)
- Decision rubric implementation
- Model integration
- Rationale generation

### Milestone 3: Human Approval Integration (Week 4)
- Approval UI
- Approval state machine

### Milestone 4: Refactor Planning (Week 5)
- Refactor pattern library
- Refactor planning prompts

### Milestone 5: Feature Planning (Week 5-6)
- Pattern matching
- Feature planning prompts

### Milestone 6: Execution Engine (Week 6-7)
- File operations module
- Verification runner
- Execution logging

### Milestone 7: Repair Loop (Week 7-8)
- Failure identification
- Minimal repair generation

### Milestone 8: Integration Testing & Documentation (Week 8-9)
- Test suite
- Documentation
- Sample repos

### Milestone 9: v1 Release Candidate (Week 9-10)
- Stability fixes
- Performance optimization
- Packaging

## Implementation Status

**Current Milestone:** 0 - Foundation

**Started:** January 1, 2026

**Progress:**
- ✅ Project structure created
- ✅ Brick 1: `start_daemon()` and `_is_port_in_use()` - 100% coverage, verified UI
- ✅ Brick 2: `stop_daemon()` - 98% coverage, verified UI
- ✅ Oracle functions implemented: `initialize()`, `get_definition()`, `get_references()`, `get_type_info()`
- ⏳ Tests for oracle functions (pending)
- ⏳ Verification UIs for oracle functions (pending)
- ⏳ CLI scaffold (pending)
- ⏳ Integration testing (pending)

**Completed Functions:**
- `start_daemon(repo_path, port)` - Start Pyright daemon
- `stop_daemon(process)` - Stop Pyright daemon gracefully
- `initialize(process, root_path)` - Initialize LSP for repository
- `get_definition(process, file_path, line, character)` - Get symbol definition location
- `get_references(process, file_path, line, character)` - Find all references to symbol
- `get_type_info(process, file_path, line, character)` - Get type information for symbol
