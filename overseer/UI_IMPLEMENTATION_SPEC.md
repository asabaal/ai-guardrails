# Overseer UI Implementation Specification

**Document Version:** 1.0  
**Author:** opencode (AI Assistant)  
**Date:** December 1, 2025  
**Purpose:** Detailed implementation specifications for test case visualization UI  
**Scope:** Dark mode test case explorer with discussion-friendly features  

---

## 🎯 I. REQUIREMENTS CLARIFICATION PROTOCOL

### **A. Explicit Understanding Statement**
Following AI Safety Development Protocols (Section II.A), I understand the requirement is to create a dark mode UI for exploring test cases in their ground truth state, with discussion-friendly features, using only real test case data, with no data modification capabilities.

### **B. Assumption Identification**
I am making the following assumptions:
- **Technical**: User wants static HTML/CSS/JS implementation (no build tools)
- **Data**: Test case data structure is stable and final for current exploration needs
- **Scope**: Focus on visualization and discussion features, not data management
- **Constraints**: Must follow all safety protocols, especially safe server launch protocol and real data only
- **User Experience**: Dark mode is required for extended analysis sessions

### **C. Constraint Documentation**
**Technical Constraints:**
- Must work as static files when possible (server permitted with silent-detached pattern)
- Must function without external dependencies
- Must use only real test case data from JSON files
- Must never compromise security for convenience

**Process Constraints:**
- Must use only real test case data (no mock data)
- Must implement visualization only (no CRUD operations)
- Must follow incremental implementation protocol
- Must maintain scope boundaries (no feature creep)
- Must follow safe server launch protocol if server functionality is used

**User Experience Constraints:**
- Must provide dark mode for reduced eye strain
- Must be discussion-friendly (copy features, reference generation)
- Must be responsive and performant
- Must not compromise user experience for technical convenience

### **D. User Confirmation Required**
"Please confirm this understanding of requirements and constraints is correct before I proceed with implementation."

---

## 🏗️ II. TECHNICAL ARCHITECTURE

### **A. Technology Stack (Safety-Compliant)**
Following **Section III.A** (Real Data-Only Development Mandate):

#### **Core Technologies**
- **HTML5**: Semantic structure, no build tools required
- **CSS3**: Dark theme, Grid/Flexbox layout, no preprocessors
- **Vanilla JavaScript**: ES6+, no frameworks, no build dependencies
- **JSON**: Native parsing, no external libraries required

#### **Explicitly Prohibited Technologies**
- **Build Tools**: No Webpack, Vite, or similar (violates static file requirement)
- **Frameworks**: No React, Vue, Angular (violates minimal scope requirement)
- **Unsafe Server Practices**: No server launch without silent-detached pattern (violates safe server protocol)
- **External Dependencies**: No npm packages, CDNs (violates self-contained requirement)

### **B. File Structure (Minimal)**
```
overseer/
├── index.html              # Single page application
├── styles.css             # Dark theme and layout
├── script.js              # All functionality
├── data/                  # Symlink to ../test_cases
│   ├── simple_logic/
│   ├── fallacies/
│   ├── chains/
│   ├── realistic_ai/
│   ├── contradictions/
│   ├── misbehavior/
│   └── safety_protocols/
└── assets/               # Icons and images
    └── icons/
```

### **C. Component Architecture**
Following **SYSTEM_ARCHITECTURE.md** specifications:

#### **Data Layer (Read-Only)**
```javascript
class TestCaseLoader {
  constructor() {
    this.cache = new Map();
  }
  
  async loadCategory(category) {
    // Read-only access to JSON files
    const response = await fetch(`data/${category}/test_cases.json`);
    const data = await response.json();
    this.cache.set(category, data);
    return data;
  }
  
  // No data modification methods
}
```

#### **Presentation Layer**
```javascript
class CategoryNavigator {
  constructor(dataLoader) {
    this.dataLoader = dataLoader;
    this.categories = [];
  }
  
  render() {
    // Display categories with real data counts
    // No data modification capabilities
  }
}

class TestCaseViewer {
  render(testCase) {
    // Display test case with discussion helpers
    // Copy buttons, reference generation
  }
}
```

#### **Interaction Layer**
```javascript
class EventManager {
  constructor(stateManager) {
    this.stateManager = stateManager;
  }
  
  handleTestCaseSelection(id) {
    // Update state, trigger viewer update
    // No direct data modification
  }
}
```

---

## 🎨 III. UI DESIGN SPECIFICATIONS

### **A. Dark Theme Design**
Following **User Experience Constraints**:

#### **Color Palette**
```css
:root {
  /* Backgrounds */
  --bg-primary: #0a0a0a;      /* Main background */
  --bg-secondary: #1a1a1a;    /* Panels, cards */
  --bg-tertiary: #2a2a2a;     /* Hover states */
  
  /* Text */
  --text-primary: #e0e0e0;     /* Main text */
  --text-secondary: #a0a0a0;   /* Secondary info */
  --text-accent: #00ff88;       /* Highlights, success */
  
  /* Categories (distinct colors) */
  --simple-logic: #4a9eff;     /* Blue */
  --fallacies: #ff6b6b;         /* Red */
  --chains: #ffd93d;            /* Yellow */
  --realistic-ai: #6bcf7f;      /* Green */
  --contradictions: #e056fd;     /* Purple */
  --misbehavior: #ff9f43;       /* Orange */
  --safety-protocols: #ff4757;   /* Critical red */
  
  /* Severity */
  --severity-none: #2ecc71;       /* Green */
  --severity-minor: #f39c12;     /* Yellow */
  --severity-major: #e67e22;     /* Orange */
  --severity-critical: #e74c3c;   /* Red */
}
```

#### **Layout Structure**
```css
body {
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: 'SF Mono', 'Monaco', monospace;
  margin: 0;
  padding: 0;
}

.app-container {
  display: grid;
  grid-template-columns: 250px 1fr 300px;
  grid-template-rows: 60px 1fr;
  height: 100vh;
  gap: 1px;
}

.header {
  grid-column: 1 / -1;
  grid-row: 1;
  background: var(--bg-secondary);
  padding: 0 20px;
  display: flex;
  align-items: center;
  gap: 20px;
}

.category-panel {
  grid-column: 1;
  grid-row: 2;
  background: var(--bg-secondary);
  overflow-y: auto;
}

.viewer-panel {
  grid-column: 2;
  grid-row: 2;
  background: var(--bg-primary);
  overflow-y: auto;
  padding: 20px;
}

.analytics-panel {
  grid-column: 3;
  grid-row: 2;
  background: var(--bg-secondary);
  padding: 20px;
  overflow-y: auto;
}
```

### **B. Component Specifications**

#### **Category Navigator (Left Panel)**
```javascript
class CategoryNavigator {
  render() {
    return `
      <div class="category-panel">
        <h3>Test Case Categories</h3>
        ${this.renderCategoryList()}
        ${this.renderQuickFilters()}
        ${this.renderStatistics()}
      </div>
    `;
  }
  
  renderCategoryList() {
    return Object.entries(this.categories).map(([category, cases]) => `
      <div class="category-item" data-category="${category}">
        <div class="category-header">
          <span class="category-color" style="background: var(--${category})"></span>
          <span class="category-name">${this.formatCategoryName(category)}</span>
          <span class="category-count">${Object.keys(cases).length}</span>
        </div>
        <div class="test-case-list">
          ${Object.entries(cases).map(([id, testCase]) => 
            this.renderTestCaseItem(id, testCase)
          ).join('')}
        </div>
      </div>
    `).join('');
  }
  
  renderQuickFilters() {
    return `
      <div class="quick-filters">
        <label>
          <input type="checkbox" id="safety-critical">
          Safety Critical Only
        </label>
        <label>
          <input type="checkbox" id="high-complexity">
          High Complexity Only
        </label>
      </div>
    `;
  }
}
```

#### **Test Case Viewer (Center Panel)**
```javascript
class TestCaseViewer {
  render(testCase) {
    if (!testCase) return this.renderEmptyState();
    
    return `
      <div class="test-case-viewer">
        ${this.renderHeader(testCase)}
        ${this.renderInputText(testCase)}
        ${this.renderSegments(testCase)}
        ${this.renderLogicObjects(testCase)}
        ${this.renderEvaluation(testCase)}
        ${this.renderMetadata(testCase)}
      </div>
    `;
  }
  
  renderHeader(testCase) {
    return `
      <div class="test-case-header">
        <span class="test-id">Example ${testCase.id}</span>
        <span class="test-description">${testCase.description}</span>
        <div class="test-actions">
          <button class="copy-reference" data-id="${testCase.id}" title="Copy for discussion">📋</button>
          <button class="copy-full" data-id="${testCase.id}" title="Copy full test case">📄</button>
          <button class="generate-prompt" data-id="${testCase.id}" title="Generate discussion prompt">💬</button>
        </div>
      </div>
    `;
  }
  
  renderInputText(testCase) {
    return `
      <div class="input-text-section">
        <h4>Input Text</h4>
        <div class="input-text copyable" data-section="input_text">
          ${testCase.input_text}
        </div>
      </div>
    `;
  }
  
  renderLogicObjects(testCase) {
    return `
      <div class="logic-objects-section">
        <h4>Logic Objects</h4>
        ${testCase.expected_logic_objects.map(obj => `
          <div class="logic-object copyable" data-type="${obj.type}">
            <span class="type-badge" style="background: var(--${this.getTypeColor(obj.type)})">
              ${this.formatTypeName(obj.type)}
            </span>
            <span class="object-text">${obj.text}</span>
            ${obj.entities ? `
              <div class="entities">
                Entities: ${obj.entities.join(', ')}
              </div>
            ` : ''}
          </div>
        `).join('')}
      </div>
    `;
  }
}
```

#### **Analytics Panel (Right Panel)**
```javascript
class AnalyticsPanel {
  render(allTestCases) {
    const stats = this.calculateStatistics(allTestCases);
    
    return `
      <div class="analytics-panel">
        <h3>📊 Analytics</h3>
        ${this.renderOverview(stats)}
        ${this.renderDistribution(stats)}
        ${this.renderSeverityBreakdown(stats)}
      </div>
    `;
  }
  
  renderOverview(stats) {
    return `
      <div class="stats-overview">
        <div class="stat-item">
          <span class="stat-value">${stats.total}</span>
          <span class="stat-label">Total Cases</span>
        </div>
        <div class="stat-item">
          <span class="stat-value" style="color: var(--severity-critical)">${stats.critical}</span>
          <span class="stat-label">Critical</span>
        </div>
        <div class="stat-item">
          <span class="stat-value" style="color: var(--severity-major)">${stats.major}</span>
          <span class="stat-label">Major</span>
        </div>
      </div>
    `;
  }
}
```

---

## 🔧 IV. IMPLEMENTATION PHASES

### **Phase 1: Safety-First Foundation (Days 1-2)**
Following **Section III.B** (Incremental Implementation Protocol):

#### **Day 1: Core Structure**
1. **Create basic HTML structure** with semantic tags
2. **Implement dark theme CSS** with category colors
3. **Create basic JavaScript classes** for Data Layer
4. **Test file loading** with real test case data
5. **Verify static file operation** (test both direct open and server-based loading)

#### **Day 2: Basic Functionality**
1. **Implement TestCaseLoader** with read-only JSON access
2. **Create CategoryNavigator** with real data display
3. **Add basic event handling** for navigation
4. **Test with all 18 test cases** from real data
5. **Verify constraint compliance** (safe server protocol, static files)

### **Phase 2: Core Visualization (Days 3-4)**
Following **Section XIII** (Scope Creep Prevention Protocol):

#### **Day 3: Test Case Display**
1. **Implement TestCaseViewer** with all sections
2. **Add logic object formatting** with type colors
3. **Create discussion helper functions** (copy, reference)
4. **Test with real test case data** (all categories)
5. **Verify scope compliance** (visualization only)

#### **Day 4: Analytics and Filtering**
1. **Implement AnalyticsPanel** with real statistics
2. **Add search and filter functionality**
3. **Create comparison mode** for side-by-side view
4. **Test with real data combinations**
5. **Verify no data modification** capabilities exist

### **Phase 3: Safety-Compliant Features (Days 5-6)**
Following **Section III.C** (Continuous Verification):

#### **Day 5: Advanced Features**
1. **Implement URL deep linking** for test case references
2. **Add keyboard navigation** for power users
3. **Create export functions** for discussion formatting
4. **Test performance** with all 18 test cases loaded
5. **Verify security constraints** (no eval(), safe code)

#### **Day 6: Polish and Verification**
1. **Add responsive design** for different screen sizes
2. **Implement error handling** for missing/invalid data
3. **Test constraint compliance** thoroughly
4. **Document verification results**
5. **Prepare for user confirmation**

---

## ✅ V. VERIFICATION PROTOCOLS

### **A. Pre-Implementation Verification**
Following **Section III.C** (Continuous Verification):

#### **Technical Verification**
- [ ] **Static File Operation**: Confirm HTML file works without server
- [ ] **Server-Based Loading**: Verify fetch() calls work with silent-detached server
- [ ] **Real Data Loading**: Verify all 18 test cases load from JSON files
- [ ] **No Mock Data**: Confirm no fake data is created anywhere
- [ ] **Security Compliance**: Verify no eval() or unsafe functions

#### **Constraint Verification**
- [ ] **Safe Server Protocol**: Confirm server usage follows silent-detached pattern
- [ ] **Read-Only Data**: Confirm no data modification capabilities
- [ ] **Scope Compliance**: Confirm only visualization features implemented
- [ ] **User Experience**: Confirm dark mode and discussion features work

### **B. Post-Implementation Verification**
Following **Section IV.B** (Reality Documentation Standards):

#### **Evidence Collection**
For each verification step:
- **Input Data**: Real test case files used
- **Execution Process**: How verification was conducted
- **Output Data**: What system produced
- **Verification Method**: How correctness was determined
- **Result**: Pass/fail status with specific evidence

#### **Success Criteria**
Following **Section IV.D** (External Confirmation Procedures):
- "I have implemented [specific functionality]. The test results show [specific evidence]. Can you confirm this meets requirements?"
- "The system now displays [specific output] which meets [specific requirement]. Does this match your expectations?"
- "I have verified [specific functionality]. The evidence shows [specific behavior]. Is this correct?"

---

## 🚫 VI. SCOPE CREEP PREVENTION

### **A. Explicit Scope Definition**
Following **Section XIII.A** (Pre-Implementation Scope Validation):

#### **Required Deliverables**
1. **Test Case Explorer**: Dark mode UI for exploring ground truth test cases
2. **Discussion Features**: Copy buttons, reference generation, comparison mode
3. **Category Navigation**: Filterable list of all test case categories
4. **Analytics Display**: Real statistics from actual test case data

#### **Out-of-Scope Items**
1. **Data Management**: No CRUD operations on test case data
2. **Unsafe Server Practices**: No server launch without silent-detached pattern
3. **Build Tools**: No complex build systems or frameworks
4. **Database Integration**: No external data storage or synchronization
5. **User Authentication**: No login systems or user management

### **B. Real-Time Scope Enforcement**
Following **Section XIII.B** (Real-Time Scope Enforcement):

#### **Step-by-Scope Check Protocol**
Before each implementation action:
1. **Deliverable Identification**: "Which specific deliverable does this step serve?"
2. **Direct Path Verification**: "Is this most direct path to deliverable?"
3. **Scope Boundary Check**: "Is this action within defined scope boundaries?"
4. **Stop Immediately**: If boundary violation detected

#### **Feature Addition Stop Protocol**
When considering any feature not in original specification:
1. **IMMEDIATE STOP** - Halt all implementation activities
2. **Feature Identification** - "I am considering [specific feature]"
3. **Scope Verification** - "This was NOT in original specification"
4. **User Clarification** - "Should I proceed with [feature] or return to required deliverables?"

---

## 📋 VII. IMPLEMENTATION CHECKLISTS

### **Pre-Development Safety Checklist**
Following **Section V** (Implementation Checklists):
- [ ] **Requirements Clarified**: I understand exactly what is required
- [ ] **Assumptions Identified**: I have listed all assumptions I'm making
- [ ] **Constraints Documented**: All constraints are identified and documented
- [ ] **Risk Assessment Completed**: All risks have been assessed and planned for
- [ ] **Minimal Scope Defined**: The smallest possible solution is defined
- [ ] **User Confirmation Received**: User has confirmed understanding and approach

### **Implementation Safety Checklist**
- [ ] **Real Data Only**: I am using only real test case data, never mock data
- [ ] **Incremental Changes**: I am making smallest possible changes
- [ ] **Continuous Testing**: I am testing each change immediately
- [ ] **Constraint Compliance**: I am respecting all explicit constraints
- [ ] **Pattern Monitoring**: I am watching for failure patterns
- [ ] **Communication Maintained**: I am maintaining clear communication with user

### **Post-Implementation Safety Checklist**
- [ ] **Real Testing**: Functionality has been tested with real test case data
- [ ] **Requirements Verified**: All requirements have been actually satisfied
- [ ] **Constraints Checked**: All constraints have been verified as satisfied
- [ ] **Evidence Collected**: Verifiable evidence has been collected
- [ ] **User Confirmation**: User has confirmed successful implementation
- [ ] **Documentation Updated**: Only verifiable facts have been documented

---

## 🚨 VIII. EMERGENCY RESPONSE PROTOCOLS

### **Critical Failure Detection**
If any of these occur during implementation:
1. **Scope Violation**: Implementing data management features
2. **Unsafe Server Usage**: Creating server functionality without silent-detached pattern
3. **Mock Data Usage**: Creating fake test data
4. **Overengineering**: Adding unnecessary complexity
5. **Constraint Violation**: Breaking any explicit user constraints

**Immediate Response**:
1. **IMMEDIATE STOP**: Halt all implementation activities
2. **FAILURE ACKNOWLEDGMENT**: Clearly and honestly acknowledge failure
3. **IMPACT ASSESSMENT**: Assess scope and impact of failure
4. **USER NOTIFICATION**: Immediately inform user of failure
5. **RECOVERY PLANNING**: Plan specific recovery actions

---

## 📄 IX. DOCUMENTATION VERSION CONTROL

### **Current Version:** 1.1  
### **Version Date:** December 1, 2025  
### **Author:** opencode (AI Assistant)  
### **Status:** Active - Must be followed for all UI development

### **Version History**
- **v1.0 (December 1, 2025):** Initial comprehensive UI implementation specification following AI Safety Development Protocols
- **v1.1 (December 1, 2025):** Updated to align with corrected SYSTEM_ARCHITECTURE.md - removed outdated "No Servers" prohibition, now permits servers with silent-detached pattern per AI Safety Development Protocols

### **Update Process**
- **Event-Driven Updates**: Immediate updates following implementation insights or user feedback
- **Scheduled Reviews**: Regular reviews and updates as specified in continuous improvement framework
- **Community Input**: Incorporation of feedback from users and stakeholders
- **Cross-Project Integration**: Updates based on insights from multiple project applications

---

**This specification represents complete alignment with AI Safety Development Protocols while providing detailed implementation guidance for a safe, effective, and focused test case visualization tool.**