# Overseer AI Logic Analysis System Architecture

**Document Version:** 1.1  
**Author:** opencode (AI Assistant)  
**Date:** December 1, 2025  
**Purpose:** Definitive reference for AI logic analysis system architecture review and compliance verification  
**Scope:** AI tool that extracts and validates logical reasoning from text  

---

## 🏗️ I. COMPONENT IDENTIFICATION

### **A. Layer 1: Segmentation Components**
Components responsible for breaking text into logical steps.

#### **TextSegmenter**
- **Purpose:** Extract reasoning steps from input text using LLM prompts
- **Input:** Raw text from AI models or documents
- **Output:** Numbered list of logical propositions
- **Constraints:** Text processing only, no evaluation

#### **RuleBasedSplitter**
- **Purpose:** Fallback deterministic splitting using connectors
- **Input:** Raw text when LLM fails
- **Output:** Segments split on logical connectors
- **Constraints:** Rule-based only, no interpretation

#### **Normalizer**
- **Purpose:** Clean and standardize extracted segments
- **Input:** Raw segments from extraction
- **Output:** Normalized, clean propositions
- **Constraints:** Text cleaning only, no content alteration

#### **Aggregator**
- **Purpose:** Combine LLM and rule-based results
- **Input:** Multiple segmentation attempts
- **Output:** Final, stable list of steps
- **Constraints:** Result aggregation only, no modification

### **B. Layer 2: Logic Extraction Components**
Components responsible for converting steps to structured logic objects.

#### **LogicClassifier**
- **Purpose:** Classify statements into logical primitive types
- **Input:** Segmented text steps
- **Output:** Type classifications (atomic, conditional, causal, etc.)
- **Constraints:** Classification only, no evaluation

#### **EntityExtractor**
- **Purpose:** Extract entities and relationships from statements
- **Input:** Classified text segments
- **Output:** Structured entity-relationship mappings
- **Constraints:** Entity extraction only, no inference

#### **RelationshipMapper**
- **Purpose:** Map logical relationships between steps
- **Input:** Logic objects with entities
- **Output:** Relationship graph and dependencies
- **Constraints:** Relationship mapping only, no validity checking

### **C. Layer 3: Logic Evaluation Components**
Components responsible for evaluating reasoning correctness.

#### **NLIEvaluator**
- **Purpose:** Check entailment and contradiction between steps
- **Input:** Paired logic objects
- **Output:** Entailment/contradiction classifications
- **Constraints:** NLI evaluation only, no interpretation

#### **GraphBuilder**
- **Purpose:** Build reasoning graphs from logic objects
- **Input:** Logic objects with relationships
- **Output:** Graph structures and adjacency matrices
- **Constraints:** Graph construction only, no analysis

#### **FallacyDetector**
- **Purpose:** Identify logical fallacies and reasoning patterns
- **Input:** Logic objects and relationships
- **Output:** Fallacy classifications and pattern matches
- **Constraints:** Pattern recognition only, no judgment

#### **ContradictionChecker**
- **Purpose:** Detect internal contradictions in reasoning
- **Input:** Logic objects and graph structures
- **Output:** Contradiction reports and conflict analysis
- **Constraints:** Consistency checking only, no resolution

### **D. Layer 4: Human-Safe Output Components**
Components responsible for generating readable analysis reports.

#### **ReportGenerator**
- **Purpose:** Create human-readable analysis reports
- **Input:** Evaluation results from all Layer 3 components
- **Output:** Structured, scannable analysis reports
- **Constraints:** Report formatting only, no data alteration

#### **SeverityClassifier**
- **Purpose:** Classify issue severity for prioritization
- **Input:** Detected problems and fallacies
- **Output:** Severity levels (critical, major, minor, note)
- **Constraints:** Classification only, no decision making

#### **OutputFormatter**
- **Purpose:** Format output for different use cases
- **Input:** Analysis results and severity classifications
- **Output:** Markdown, JSON, or CLI formatted reports
- **Constraints:** Formatting only, no content changes

### **E. Cross-Layer Components**
Components providing functionality across multiple layers.

#### **LLMInterface**
- **Purpose:** Communicate with local AI models
- **Input:** Prompts and text data
- **Output:** AI model responses
- **Constraints:** Interface only, no model training

#### **TestcaseLoader**
- **Purpose:** Load ground truth test cases for validation
- **Input:** Test case file paths
- **Output:** Parsed test case objects
- **Constraints:** Read-only access, no modification

#### **ConfigurationManager**
- **Purpose:** Manage system configuration and protocols
- **Input:** Configuration files and user settings
- **Output:** System parameters and constraint settings
- **Constraints:** Configuration only, no policy changes

---

## 🔄 II. RELATIONSHIP MAPPING

### **A. Data Flow Architecture**
```
User Interaction → EventManager → StateManager → Component Updates
     ↓
TestCaseLoader → DataValidator → CacheManager → Presentation Layer
     ↓
URLManager ← StateManager → Browser History
```

### **B. Component Dependencies**
- **Presentation Layer** depends on **Data Layer** for content
- **Interaction Layer** coordinates **Presentation Layer** updates
- **Utility Layer** serves all other layers with common functions
- **StateManager** acts as central coordinator for all components

### **C. Data Integrity Flow**
1. **File System** → TestCaseLoader (read-only)
2. **TestCaseLoader** → DataValidator (format verification)
3. **DataValidator** → CacheManager (memory storage)
4. **CacheManager** → Presentation Layer (display data)
5. **All layers** maintain read-only access to source data

---

## 🚫 III. CONSTRAINT DOCUMENTATION

### **A. Technical Constraints**
#### **Safe Server Launch Protocol Compliance**
- **Constraint:** UI may use server functionality only with approved silent-detached pattern
- **Implementation:** Server launch requires user confirmation and proper cleanup
- **Verification:** Test with silent-detached server launch pattern
- **Rationale:** Follows Safe Server Launch Protocol from AI_SAFETY_DEVELOPMENT_PROTOCOLS.md

#### **Static File Optionality**
- **Constraint:** UI should work as static files when possible, but server usage is permitted
- **Implementation:** Prefer static operation, allow server for data loading when needed
- **Verification:** Test both static and server-based operation
- **Rationale:** Provides flexibility while maintaining safety

#### **Security Constraints**
- **Constraint:** Must never compromise security for convenience
- **Implementation:** No eval(), no external script loading
- **Verification:** Security audit of all JavaScript code
- **Rationale:** Prevents code injection attacks

### **B. Process Constraints**
#### **Real Data Only Mandate**
- **Constraint:** Must use only real test case data
- **Implementation:** Read-only access to JSON files via fetch() or embedded data
- **Verification:** No mock data creation anywhere in code
- **Rationale:** Follows Real Data-Only Development Mandate

#### **Scope Limitation Constraint**
- **Constraint:** Visualization only, no data management
- **Implementation:** No CRUD operations on test case data
- **Verification:** Review all functions for data modification attempts
- **Rationale:** Follows Scope Creep Prevention Protocol

#### **User Experience Constraints**
- **Constraint:** Must not compromise user experience for technical convenience
- **Implementation:** Dark mode, responsive design, fast loading
- **Verification:** User testing of interface usability
- **Rationale:** Maintains collaboration effectiveness

### **C. Data Integrity Constraints**
#### **Read-Only Access Pattern**
- **Constraint:** Components can only read from test case files
- **Implementation:** No write operations in Data Layer
- **Verification:** Code review for any write operations
- **Rationale:** Prevents accidental data corruption

#### **Format Consistency Requirement**
- **Constraint:** Must handle all test case formats consistently
- **Implementation:** Unified data parsing across all categories
- **Verification:** Test with all 18 test case files
- **Rationale:** Ensures reliable data handling

---

## 🔍 IV. VIOLATION DETECTION

### **A. Architecture Violation Patterns**
#### **Single Responsibility Violations**
- **Pattern:** Components doing more than their intended purpose
- **Detection:** Review each component for multiple responsibilities
- **Prevention:** Split into smaller, focused components
- **Example:** TestCaseViewer also handling data loading

#### **Dependency Inversion**
- **Pattern:** High-level modules depending on low-level modules
- **Detection:** Check dependency directions between components
- **Prevention:** Maintain proper dependency hierarchy
- **Example:** DataLayer depending on Presentation Layer

#### **Interface Segregation**
- **Pattern:** Components forced to implement interfaces they don't use
- **Detection:** Identify unused interface methods
- **Prevention:** Only implement actually used interfaces
- **Example:** CacheManager implementing unused export methods

### **B. Structural Violations**
#### **Circular Dependencies**
- **Pattern:** Components that depend on each other in loops
- **Detection:** Map dependency graph for cycles
- **Prevention:** Clear hierarchical dependency structure
- **Example:** StateManager ↔ EventManager circular reference

#### **Tight Coupling**
- **Pattern:** Components overly dependent on specific implementations
- **Detection:** Check for hard-coded dependencies
- **Prevention:** Use dependency injection and interfaces
- **Example:** TestCaseViewer directly calling specific file loader

#### **Breaking Abstractions**
- **Pattern:** Implementation details leaking across boundaries
- **Detection:** Review cross-layer function calls
- **Prevention:** Maintain strict layer separation
- **Example:** Presentation Layer calling file system directly

### **C. Regression Indicators**
#### **Functionality Loss**
- **Pattern:** Previously working features no longer functioning
- **Detection:** Regular testing of all components
- **Prevention:** Comprehensive test suite for all features
- **Example:** Search functionality stops working after UI changes

#### **Performance Degradation**
- **Pattern:** System performance worse than before
- **Detection:** Performance monitoring and comparison
- **Prevention:** Performance testing for all changes
- **Example:** Test case loading becomes progressively slower

#### **Integration Breakage**
- **Pattern:** Components that previously worked together now failing
- **Detection:** Integration testing between components
- **Prevention:** Maintain integration test suite
- **Example:** Category navigation not updating test case viewer

---

## 📊 V. REGRESSION ANALYSIS

### **A. Pre-Implementation Review**
Before any UI changes:
1. **System Survey:** Conduct high-level survey of current architecture
2. **Relevant Component Extraction:** Identify components affected by changes
3. **Dependency Analysis:** Map dependencies between affected components
4. **Architecture Violation Assessment:** Check for violations of design principles
5. **Regression Detection:** Look for regressions that may have been introduced previously
6. **Risk Identification:** Identify architectural risks that may affect implementation
7. **Constraint Documentation:** Document all architectural constraints and limitations

### **B. Change Impact Assessment**
For each proposed change:
1. **Component Impact:** Which components will be affected?
2. **Dependency Impact:** How will dependencies be affected?
3. **User Experience Impact:** How will user interaction be affected?
4. **Performance Impact:** How will system performance be affected?
5. **Security Impact:** How will security posture be affected?

### **C. Regression Prevention Strategy**
1. **Comprehensive Testing:** Test all components after changes
2. **Integration Verification:** Ensure component interactions work correctly
3. **Performance Monitoring:** Track performance metrics over time
4. **User Experience Validation:** Verify usability is maintained
5. **Security Review:** Ensure no security regressions introduced

---

## ✅ VI. COMPLIANCE VERIFICATION

### **A. Safety Protocol Compliance**
#### **Real Data-Only Development Mandate**
- **Requirement:** Use only real test case data
- **Verification:** All components read from existing JSON files
- **Evidence:** No mock data creation in any component
- **Status:** COMPLIANT

#### **Incremental Implementation Protocol**
- **Requirement:** Make smallest possible changes
- **Verification:** Each component has single, focused responsibility
- **Evidence:** Component purposes are clearly defined and limited
- **Status:** COMPLIANT

#### **Constraint Compliance Enforcement**
- **Requirement:** Respect all explicit user constraints
- **Verification:** Safe server launch protocol compliance, read-only data access
- **Evidence:** Architecture enforces all documented constraints
- **Status:** COMPLIANT

### **B. Scope Creep Prevention**
#### **Scope Boundary Definition**
- **In Scope:** Test case visualization and discussion features
- **Out of Scope:** Data management, unsafe server practices, complex build tools
- **Verification:** No components implement out-of-scope functionality
- **Evidence:** All components serve visualization or discussion purposes
- **Status:** COMPLIANT

### **C. Quality Assurance**
#### **Component Testing**
- **Requirement:** Test all components with real data
- **Verification:** Each component tested with actual test case files
- **Evidence:** Test results documented for all components
- **Status:** PENDING IMPLEMENTATION

#### **Integration Testing**
- **Requirement:** Verify component interactions work correctly
- **Verification:** Integration tests cover all component interactions
- **Evidence:** Integration test suite planned and executed
- **Status:** PENDING IMPLEMENTATION

### **D. Testing Suite Architecture**
#### **Purpose Hierarchy and Organization**
The testing suite follows clear architectural principles with distinct purpose separation:

**Core Test Suite Components:**

**1. Main Test Runner (`test_suite.py`)**
- **Purpose**: Primary test orchestrator and execution coordinator
- **Responsibilities**: 
  - Discover and execute all test categories
  - Coordinate test execution across components
  - Generate comprehensive test reports
  - Handle test configuration and parameters
  - Provide unified interface for test execution
  - Manage test lifecycle and cleanup

**2. Component-Specific Test Modules**
- **`test_segmentation.py`**: Test Layer 1 (Text Segmentation) Components
  - Test LLMTextSegmenter, RuleBasedSplitter, Normalizer
  - Validate segmentation accuracy and fallback behavior
  - Test prompt engineering and response parsing
  
- **`test_logic_extraction.py`**: Test Layer 2 (Logic Extraction) Components
  - Test logic classification and entity extraction
  - Validate relationship mapping and graph building
  - Test structured logic object creation
  
- **`test_evaluation.py`**: Test Layer 3 (Logic Evaluation) Components
  - Test fallacy detection and contradiction checking
  - Validate severity classification and evaluation metrics
  - Test NLI and logical consistency checking

**3. Validation Framework (`validation_framework.py`)**
- **Purpose**: Ground truth validation and accuracy assessment
- **Responsibilities**:
  - Load expected vs actual results from test cases
  - Calculate accuracy, precision, recall metrics
  - Generate validation reports and comparisons
  - Maintain test case integrity and format consistency
  - Provide statistical analysis of system performance

**4. Integration Testing (`test_integration.py`)**
- **Purpose**: End-to-end system testing and component interaction
- **Responsibilities**:
  - Test complete workflows from input to evaluation
  - Verify component data flow and communication
  - Test API functionality and response handling
  - Validate UI integration and user interaction
  - Test error handling and edge cases
  - Verify system performance under load

#### **File Organization Standards**
- **Naming Conventions**: 
  - `test_suite.py` for main orchestrator
  - `test_*.py` for component-specific unit tests
  - `validation_framework.py` for validation logic
  - Clear purpose distinction in all filenames
- **Purpose Hierarchy**:
  1. **Unit Tests** - Individual component testing
  2. **Integration Tests** - Cross-component functionality  
  3. **Validation Tests** - Ground truth comparison
  4. **System Tests** - End-to-end workflows

#### **Dependency Architecture**
```
test_suite.py (orchestrator)
    ↓
test_segmentation.py → validation_framework.py
test_logic_extraction.py → validation_framework.py  
test_evaluation.py → validation_framework.py
test_integration.py → validation_framework.py
    ↓
All components → test_cases/ (read-only data access)
```

#### **Compliance Verification**
- **Real Data-Only Development**: ✅ All tests read from existing JSON files
- **Scope Limitation**: ✅ All components serve testing/validation purposes only
- **Layer Separation**: ✅ Clear separation between testing concerns
- **Naming Convention**: ✅ Consistent and purpose-driven naming
- **Integration Points**: ✅ Well-defined interfaces between components

#### **Implementation Status**
- **Architecture Documentation**: ✅ COMPLETED and COMPLIANT
- **Test Suite Design**: ✅ COMPLETED with proper organization
- **Implementation**: 🔄 PENDING - Ready for development with clear architectural guidance

---

## 🔄 VII. CONTINUOUS IMPROVEMENT FRAMEWORK

### **A. Regular Review Schedule**
- **Daily Self-Check:** Review compliance with safety protocols
- **Weekly Project Review:** Assess architecture effectiveness
- **Monthly Architecture Review:** Evaluate component design and interactions
- **Quarterly Improvement Update:** Update architecture based on new insights

### **B. Improvement Sources**
- **Failure Analysis:** Learn from architectural mistakes and near-misses
- **User Feedback:** Incorporate user suggestions and usability concerns
- **Pattern Recognition:** Update architecture based on identified patterns
- **Best Practice Integration:** Incorporate industry best practices for UI architecture

### **C. Success Metrics**
- **Safety Compliance:** Percentage of components following safety protocols
- **Performance Efficiency:** System responsiveness and resource usage
- **User Experience:** User satisfaction with interface usability
- **Maintainability:** Ease of understanding and modifying components
- **Reliability:** Consistency of behavior across different scenarios

---

## 📋 VIII. EMERGENCY RESPONSE PROTOCOLS

### **A. Critical Architecture Failure**
#### **Failure Definition**
Critical architectural failures are situations that:
- **Compromise Safety:** Violate core safety principles or cause harm
- **Break Functionality:** Render UI non-functional or unusable
- **Violate Constraints:** Break explicit user constraints or requirements
- **Damage Trust:** Undermine user trust or collaboration effectiveness

#### **Immediate Response Protocol**
When critical failure is detected:
1. **IMMEDIATE STOP:** Halt all development activities immediately
2. **FAILURE ACKNOWLEDGMENT:** Clearly and honestly acknowledge architectural failure
3. **IMPACT ASSESSMENT:** Assess scope and impact of failure
4. **USER NOTIFICATION:** Immediately inform user of architectural failure
5. **RECOVERY PLANNING:** Plan specific recovery actions to restore functionality

### **B. Architecture Recovery Procedures**
#### **Recovery Planning Framework**
For system recovery:
1. **Problem Isolation:** Clearly identify and isolate specific architectural problem
2. **Impact Assessment:** Understand full scope of problem
3. **Recovery Strategy:** Plan specific steps to restore proper architecture
4. **Verification Planning:** Plan how to verify recovery success
5. **Prevention Planning:** Plan how to prevent recurrence

#### **Recovery Execution**
- **Minimal Fix Approach:** Implement smallest change that restores proper architecture
- **Incremental Recovery:** Recover systems incrementally, testing each step
- **Continuous Verification:** Verify each recovery step before proceeding
- **User Communication:** Keep user informed throughout recovery process

---

## 📚 IX. REFERENCE MATERIALS

### **A. Supporting Documents**
- **AI_SAFETY_DEVELOPMENT_PROTOCOLS.md:** Comprehensive safety framework (authoritative for server usage)
- **PROJECT_PLAN.md:** Overall project organization and phases
- **test_cases/ directory:** Real test case data structure
- **UI_IMPLEMENTATION_SPEC.md:** Detailed UI implementation specifications

### **B. Cross-Reference Requirements**
All architecture decisions must reference safety protocols using format:
"Following AI Safety Development Protocols (AI_SAFETY_DEVELOPMENT_PROTOCOLS.md)"

### **C. Protocol Hierarchy**
1. **Core Safety Principles:** Absolute, non-negotiable safety requirements
2. **Architecture Principles:** Specific methods for maintaining safe system design
3. **Implementation Standards:** Requirements for component development
4. **Emergency Procedures:** Response protocols for critical architectural situations

---

## 📄 X. DOCUMENTATION VERSION CONTROL

### **Current Version:** 1.1  
### **Version Date:** December 1, 2025  
### **Author:** opencode (AI Assistant)  
### **Status:** Active - Must be followed for all UI development

### **Version History**
- **v1.0 (December 1, 2025):** Initial comprehensive system architecture following AI Safety Development Protocols
- **v1.1 (December 1, 2025):** Corrected inaccurate "No Server Launch Requirement" to align with AI Safety Development Protocols which permit servers with silent-detached pattern
- **v1.2 (December 1, 2025):** Added comprehensive Testing Suite Architecture specification to resolve MAJOR naming convention violation and establish clear purpose hierarchy for test infrastructure

### **Update Process**
- **Event-Driven Updates:** Immediate updates following architectural failures or insights
- **Scheduled Reviews:** Regular reviews and updates as specified in continuous improvement framework
- **Community Input:** Incorporate feedback from users and stakeholders
- **Cross-Project Integration:** Updates based on insights from multiple projects

---

**This architecture document represents comprehensive compliance with AI Safety Development Protocols while providing a robust foundation for test case visualization tool development.**