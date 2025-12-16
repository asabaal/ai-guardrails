# 🏗️ Global System Architecture

**Document Version:** 1.0  
**Author:** opencode (AI Assistant)  
**Date:** December 15, 2025  
**Purpose:** Universal architectural principles and patterns for all projects  
**Compliance:** Following AI Safety Development Protocols (AI_SAFETY_DEVELOPMENT_PROTOCOLS.md)  
**Reference Implementation:** TSHill Logistics LLC System Architecture (SYSTEM_ARCHITECTURE.md)

---

## 🎯 Global Architecture Overview

### **System Purpose**
This Global System Architecture provides universal principles, patterns, and frameworks that apply to ALL projects. It establishes consistent standards for system design, validation, collaboration, and quality assurance across the entire development ecosystem.

### **Core Architectural Philosophy**

#### **Universal Design Principles**
1. **Single Responsibility Principle:** Each module has one clear, well-defined purpose
2. **Open/Closed Principle:** Modules open for extension, closed for modification
3. **Liskov Substitution:** Components can be substituted without breaking functionality
4. **Interface Segregation:** Clients depend only on interfaces they actually use
5. **Dependency Inversion:** High-level modules don't depend on low-level modules

#### **Layer-Based Architecture**
- **Template Layer:** Defines visual layout, styling, and content slots
- **Business Logic Layer:** Handles content processing and transformation
- **Rendering Layer:** Converts structured data into visual outputs
- **Output Layer:** Manages file organization and metadata

#### **Separation of Concerns**
- **Content vs. Presentation:** Brief data separate from visual rendering
- **Configuration vs. Logic:** Template definitions separate from processing logic
- **Generation vs. Output:** Content creation separate from file management

---

## 🧱 Universal Component Architecture

### **1. Template System Pattern**
**Purpose:** Defines reusable visual layouts and content slots

#### **Universal Template Components**
- **Template Files:** YAML files defining layer structure and styling
- **Palette Definitions:** Color schemes and branding configurations
- **Slot Definitions:** Content placeholders (title, bullets, etc.)

#### **Template Structure Pattern**
```yaml
layers:
  - kind: [background_type]
  - kind: [overlay_type]
  - kind: [text_block] (role: [content_type])
  - kind: [list_block] (role: [content_type])
  - kind: [watermark]
```

### **2. Input System Pattern**
**Purpose:** Structured content requests defining output requirements

#### **Universal Input Structure**
```yaml
id: unique_identifier
title: "Content Title"
content:
  - "Content item"
output_kind: [output_type]
aspect_ratio: [dimensions]
palette: [color_scheme]
```

### **3. Rendering Engine Pattern**
**Purpose:** Converts template + data into visual assets

#### **Core Rendering Classes**
- **`Renderer`**: Main interface for visual generation
- **Rendering Methods**: `_draw_title()`, `_draw_content()`, `_add_watermark()`
- **Positioning Logic**: Coordinate calculation and layout
- **Output Generation**: `_save_output()`

#### **Universal Rendering Pipeline**
1. Load template configuration
2. Parse input data
3. Filter components by content availability
4. Render each component in sequence
5. Composite final output
6. Save with metadata

### **4. Output Management Pattern**
**Purpose:** Handles file organization and metadata

#### **Core Output Classes**
- **`OutputManager`**: Centralized file and metadata handler
- **Directory Structure**: Creates standardized output folders
- **Metadata Management**: Saves specifications and job data
- **Validation Support**: Handles positioning metadata for validation

### **5. Pipeline Orchestration Pattern**
**Purpose:** Coordinates end-to-end content generation

#### **Core Orchestration Classes**
- **`Engine`**: Main pipeline controller
- **Orchestration Methods**: `run_job()`, `_load_input()`, `_compose_spec()`
- **CLI Interface**: Command-line execution support

---

## 🔄 Universal Data Flow Architecture

### **Primary Data Flow Pattern**
```mermaid
graph TD
    A[Structured Input] --> B[Engine.run_job()]
    B --> C[Template Loader]
    B --> D[Input Parser]
    C --> E[Renderer]
    D --> E
    E --> F[OutputManager]
    E --> G[Content Builder]
    F --> H[final/output]
    G --> I[final/metadata]
    F --> J[meta/specification.json]
```

### **Component Interaction Patterns**

#### **Template → Renderer Interface**
- **Input**: Template path and palette definitions
- **Output**: Component configuration and styling rules
- **Interface**: YAML parsing and component filtering

#### **Input → Renderer Interface**
- **Input**: Input file path
- **Output**: Structured content data
- **Interface**: YAML validation and content extraction

#### **Renderer → OutputManager Interface**
- **Input**: Rendered object and metadata
- **Output**: Saved files and directory structure
- **Interface**: File saving and folder creation

---

## 🏛️ Universal System Boundaries & Interfaces

### **External Interface Standards**

#### **Input Interface**
- **Format**: Structured files (YAML, JSON)
- **Validation**: Schema validation for required fields
- **Error Handling**: Missing fields, invalid formats

#### **Output Interface**
- **Standard Structure**: `outputs/{job_id}/final/`
- **File Types**: Output files, metadata files, specifications
- **Naming Convention**: Consistent, timestamped job IDs

### **Internal Interface Standards**

#### **Template → Renderer Interface**
```python
class Renderer:
    def __init__(template_path: str, palette_path: Optional[str])
    def render(self, input_data: dict) -> Output
```

#### **Input → Engine Interface**
```python
class Engine:
    def run_job(self, input_path: str) -> dict
    def _load_input(self, path: str) -> dict
    def _compose_spec(self, template: dict, input_data: dict) -> dict
```

#### **Output Manager Interface**
```python
class OutputManager:
    def create_job_folder(self, job_id: str) -> str
    def save_output(self, output: Any, path: str) -> str
    def save_metadata(self, data: dict) -> str
    def write_spec(self, spec: dict) -> str
```

---

## ⚠️ Universal Architectural Constraints

### **Technical Constraints**
- **Static Templates**: No dynamic template generation
- **Dependency Management**: Clear dependency boundaries
- **Configuration Format**: Structured configuration files
- **File System**: Local file system with standardized organization

### **Performance Constraints**
- **Memory Usage**: Efficient resource management
- **Processing Time**: Optimized processing pipelines
- **File I/O**: Synchronous file operations with error handling
- **Concurrency**: Single-threaded processing for consistency

### **Security Boundaries**
- **File Access**: Limited to specified directories only
- **No Network Access**: No external API calls unless explicitly required
- **No Code Execution**: Input files cannot contain executable code
- **Input Validation**: All user inputs must be validated

---

## 🔍 Universal Architecture Violation Detection Framework

### **Design Principle Violations**

#### **Single Responsibility Violations**
- **Symptom**: Components handling multiple unrelated concerns
- **Detection**: Methods with mixed purposes
- **Impact**: Reduced maintainability, testing complexity

#### **Dependency Inversion Violations**
- **Symptom**: High-level modules importing low-level implementation details
- **Detection**: Main classes importing specific utility functions
- **Impact**: Tight coupling, difficult to test

#### **Interface Segregation Violations**
- **Symptom**: Large interfaces forcing unused implementations
- **Detection**: Classes implementing methods they don't use
- **Impact**: Unnecessary complexity, violation of interface contract

#### **Open/Closed Violations**
- **Symptom**: Modifying core class behavior instead of extending
- **Detection**: Direct modifications to base classes
- **Impact**: Breaking existing functionality, reduced extensibility

### **Structural Violations**

#### **Circular Dependencies**
- **Symptom**: Module A imports B, B imports A
- **Detection**: Import cycles in dependency graph
- **Impact**: Initialization failures, memory leaks

#### **Tight Coupling**
- **Symptom**: Components requiring specific implementation knowledge
- **Detection**: Hard-coded class names, specific method calls
- **Impact**: Reduced flexibility, difficult to modify

#### **Breaking Abstractions**
- **Symptom**: Implementation details leaking across layer boundaries
- **Detection**: Rendering logic in input processing, file management in rendering
- **Impact**: Architectural boundary violations, maintenance complexity

---

## 🧪 Universal Milestone Validation Architecture

### **Validation System Overview**
The Universal Milestone Validation Architecture provides comprehensive validation for ALL milestones through a consistent 4-phase pattern: Abstract Framework → Milestone-Specific Implementation → Dashboard → Test Data.

### **Universal 4-Phase Milestone Pattern**

#### **Phase 1: Abstract Validation Framework**
**Location:** `tests/validation/framework/`  
**Purpose:** Milestone-agnostic base classes and common functionality

**Core Components:**
```python
tests/validation/framework/
├── base_dashboard.py          # Abstract dashboard functionality
├── base_metadata_extractor.py # Abstract metadata extraction
├── base_overlay_generator.py  # Abstract visual overlay creation
└── base_test_runner.py        # Abstract test execution
```

#### **Phase 2: Milestone-Specific Implementation**
**Location:** `tests/validation/milestone[X]/`  
**Purpose:** Milestone-specific validation implementations

**Implementation Pattern:**
```python
tests/validation/milestone[X]/
├── [milestone]_metadata_extractor.py  # Extract [milestone] positioning data
├── [milestone]_overlay_generator.py    # Create visual overlays
├── [milestone]_test_runner.py          # Execute [milestone] validation tests
├── [milestone]_dashboard.html          # Interactive validation interface
└── [milestone]_validation_data.js     # Formatted validation data
```

#### **Phase 3: Universal Dashboard Features**
**Purpose:** Interactive validation interface with consistent functionality

**Universal Dashboard Components:**
1. **Position Analysis**: X/Y coordinate accuracy validation
2. **Rendering Validation**: Font loading and rendering verification
3. **Interactive Controls**: Test scenario selection and tolerance adjustment
4. **Validation Metrics**: Positioning accuracy scores and consistency metrics

#### **Phase 4: Universal Test Data Categories**
**Purpose:** Comprehensive test coverage using consistent test categories

**Universal Test Categories:**
1. **Basic Positioning Tests**: Standard positions and configurations
2. **Line/Spacing Validation**: Consistency checks across elements
3. **Content Wrapping Tests**: Various content lengths and wrapping scenarios
4. **Edge Cases**: Boundary condition testing and error conditions
5. **Integration Tests**: Multi-component interaction testing

---

## 🤖 Universal Human-AI Collaboration Protocol

### **Milestone-Agnostic Development and Review Workflow**

#### **Universal Process Flow**
1. **AI Implementation** → Generate outputs using real data for current milestone
2. **Real Data Extraction** → Extract positioning metadata from actual outputs
3. **Human Review** → Validate against milestone requirements using visual dashboard
4. **Feedback Integration** → AI incorporates specific feedback for current milestone
5. **Iteration** → Repeat until milestone requirements satisfied

#### **Universal Collaboration Framework**

**Phase 1: Implementation**
- **AI Responsibility**: Implement milestone features following specifications exactly
- **Constraint**: Use only real data, never mock or assumed data
- **Verification**: Test with actual system outputs for current milestone
- **Documentation**: Report only verifiable facts for current milestone

**Phase 2: Validation**
- **Human Responsibility**: Review implementation against milestone requirements
- **Tools**: Use milestone-specific visual validation dashboard
- **Criteria**: Validate milestone-specific accuracy, visual quality, compliance
- **Feedback**: Provide specific, actionable feedback for current milestone

**Phase 3: Iteration**
- **AI Responsibility**: Address specific feedback points for current milestone
- **Constraint**: Make minimal changes addressing only identified issues
- **Verification**: Re-test with real data to confirm milestone-specific fixes
- **Documentation**: Report only verified improvements for current milestone

---

## 🎯 Universal Single Source of Truth Requirements

### **Critical Validation Data Requirements**

#### **Primary Source Mandate**
- **Primary Source**: All validation data MUST come from actual outputs
- **Extraction Method**: Real data extraction from output files
- **Data Integrity**: Validation data must match actual output exactly
- **Verification**: All validation data must be verifiable against real outputs

#### **Forbidden Practices**
- **Mock Data**: Never create fake validation results
- **Assumed Data**: Never use assumed or calculated positioning data
- **Fake Validation**: Never generate validation reports without real outputs
- **Multiple Sources**: Never create competing validation data sources

#### **Universal Data Extraction Pipeline**
1. **Generate Real Outputs**: Use system with actual input files
2. **Extract Metadata**: Use enhanced system to extract positioning data
3. **Store Validation Data**: Save metadata to structured JSON files
4. **Generate Reports**: Create milestone-specific HTML dashboard using real data
5. **Verify Integrity**: Ensure all validation data matches actual outputs

---

## 🚫 Universal Error Prevention Guidelines

### **Historical Failure Analysis**

#### **Past Critical Failures**
1. **Font Size Regression**: Used wrong font sizes instead of correct specifications
2. **Architectural Destruction**: Created multiple competing data sources
3. **Plan Mode Violations**: Attempted file edits while in read-only mode
4. **False Success Reporting**: Reported completion using wrong specifications
5. **Milestone-Specific Repetition**: Same failure patterns repeated across milestones

#### **Universal Prevention Strategies**

**Font Size Regression Prevention:**
- **Specification Reference**: Always verify against template specifications
- **Template Authority**: Template files are single source of truth for styling
- **Validation Requirement**: Font sizes must be validated against template definitions

**Multiple Data Sources Prevention:**
- **Single Source Mandate**: All validation data from single, authoritative source
- **Version Control**: Clear versioning, no competing versions
- **Output Management**: Centralized output organization with clear naming

**Plan Mode Violation Prevention:**
- **Mode Awareness**: Always check operational mode before making changes
- **Permission Verification**: Confirm edit permissions before file modifications
- **Safety Protocol Compliance**: Follow all safety protocols regardless of mode

**False Success Reporting Prevention:**
- **Evidence-Based Reporting**: Report only verified, testable results
- **Real Data Requirement**: Use only actual system outputs for validation
- **External Confirmation**: Never claim success without user confirmation

---

## 📁 Universal File Organization Standards

### **Consistent Naming Convention**
**Mandatory Naming Standards:**
- Validation Data: `milestone[X]_validation_data.js`
- Dashboard Files: `milestone[X]_dashboard.html`
- Data Generators: `generate_milestone[X]_data.py`
- Metadata: `milestone[X]_metadata/` (milestone-specific directories)

### **Standardized Directory Structure**
**Architectural Requirement:** Clean, organized structure with no duplicate files
```
tests/validation/
├── milestone5/
│   ├── milestone5_validation_data.js
│   ├── metadata/ (M5-specific)
│   └── milestone5_dashboard.html
├── milestone6/
│   ├── milestone6_validation_data.js
│   ├── metadata/ (M6-specific)
│   └── milestone6_dashboard.html
└── integration/
    ├── integration_dashboard.html
    └── integration_validation_data.js
```

### **Duplicate File Prevention**
**Zero Tolerance Policy:**
- Single authoritative data file per milestone
- No duplicate files across multiple directories
- Clear version control with single source of truth
- Immediate cleanup of any duplicate files discovered

---

## 🔒 Browser-Compatible Path Standards

### **Relative Path Mandate**
**Security Requirement:** All dashboard image paths must be relative for browser security
- **No Absolute Paths**: Forbidden in all validation data files
- **Browser Compatibility**: Required for all dashboard functionality
- **Consistent Patterns**: Follow working examples from functional dashboards

### **Working Path Patterns**
**Proven Working Examples:**
```javascript
// Milestone Pattern:
"image_path": "../../../../tests/validation/outputs/example_output.png"

// Integration Pattern:
"imageUrl": "../../../../tests/validation/outputs/integration/example.png"
```

### **Path Security Implementation**
**Generator Requirements:**
- Convert absolute paths to relative paths
- Use dashboard location as reference point
- Test browser compatibility before deployment
- Validate all paths exist and are accessible

---

## 🚀 Extension Architecture

### **Universal Plugin Points**
- **Template Extensions**: New template files in standardized locations
- **Renderer Extensions**: New rendering backends with consistent interfaces
- **Output Extensions**: New output formats with standardized metadata
- **Validation Extensions**: New validation rules following universal patterns

### **Future Module Integration**
- **AI Integration**: Extend rendering with AI models following safety protocols
- **Cloud Storage**: Extend output management with remote storage
- **Batch Processing**: Extend pipeline with job queuing
- **API Integration**: Extend input processing with external data sources

---

## 📊 Universal System Metrics & Monitoring

### **Key Performance Indicators**
- **Processing Time**: Time to generate single output
- **Memory Usage**: Peak memory during processing
- **File Size**: Output dimensions and file size
- **Success Rate**: Percentage of successful operations

### **Quality Metrics**
- **Positioning Accuracy**: Deviation from target coordinates
- **Rendering Quality**: Font rendering quality and consistency
- **Color Accuracy**: Adherence to specified palette
- **Template Compliance**: Correct component rendering order

---

## 🛡️ Universal Security Architecture

### **Input Validation**
- **Schema Validation**: Input structure validation
- **File Path Security**: Path traversal prevention
- **Content Sanitization**: Text content validation
- **Size Limits**: Maximum file and content sizes

### **Output Security**
- **Directory Isolation**: Sandboxed output directories
- **File Permissions**: Controlled access to generated files
- **Metadata Sanitization**: Safe data generation
- **Path Validation**: Secure file path handling

---

## 📋 Universal Architecture Compliance Checklist

### **Design Principle Compliance**
- [ ] **Single Responsibility**: Each module has one clear purpose
- [ ] **Open/Closed**: Modules open for extension, closed for modification
- [ ] **Liskov Substitution**: Components can be substituted safely
- [ ] **Interface Segregation**: Minimal, focused interfaces
- [ ] **Dependency Inversion**: High-level modules independent of low-level details

### **Structural Compliance**
- [ ] **No Circular Dependencies**: Clean dependency graph
- [ ] **Loose Coupling**: Components communicate through interfaces
- [ ] **Strong Cohesion**: Related functionality grouped together
- [ ] **Layer Integrity**: Clear architectural layer separation
- [ ] **Abstraction Boundaries**: Implementation details properly encapsulated

### **Integration Compliance**
- [ ] **Interface Contracts**: All interfaces well-defined and consistent
- [ ] **Data Flow**: Clean, predictable data transformation pipeline
- [ ] **Error Handling**: Comprehensive error propagation and handling
- [ ] **Configuration Management**: Centralized, consistent configuration

### **Quality Assurance**
- [ ] **Testing Strategy**: Comprehensive test coverage for all components
- [ ] **Validation Framework**: Automated architecture compliance checking
- [ ] **Performance Monitoring**: System performance tracking and alerting
- [ ] **Documentation**: Complete, up-to-date architecture documentation

---

## 🔄 Version History

**v1.0 (December 15, 2025):** Initial comprehensive global system architecture document establishing universal principles, patterns, and frameworks for all projects. Extracted from TSHill Logistics LLC reference implementation and adapted for universal application across all development initiatives.

---

**This document serves as the definitive reference for global system architecture and must be consulted before any architectural modifications or implementations to ensure compliance with established universal design principles, validation requirements, and error prevention guidelines.**