#!/usr/bin/env python3
"""
create-project CLI Tool
Automates creation of new Python projects with global architecture standards.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Get directory where this script is located
SCRIPT_DIR = (Path(__file__).resolve().parent.parent.parent.parent / "create_project").resolve()
GLOBAL_SAFETY_DIR = SCRIPT_DIR / ".ai_safety"
GLOBAL_ARCH_DIR = SCRIPT_DIR / ".architecture"

LOCAL_ARCH_TEMPLATE = """# Local System Architecture

**Document Version:** 1.0  
**Date:** {date}  
**Project:** {project_name}  
**Purpose:** Project-specific architecture extension of global principles  
**Compliance:** Following AI Safety Development Protocols (AI_SAFETY_DEVELOPMENT_PROTOCOLS.md)  
**Global Reference:** Global System Architecture (architecture/GLOBAL_SYSTEM_ARCHITECTURE.md)

---

## Project-Specific Architecture Extension

This document extends to global architecture principles for **{project_name}**. All project-specific implementations must comply with universal design principles, validation frameworks, and safety protocols defined in the global architecture.

---

## Project Overview

### **Purpose**
{project_purpose_placeholder}

### **Scope**
{project_scope_placeholder}

### **Requirements**
{project_requirements_placeholder}

### **Success Criteria**
{success_criteria_placeholder}

---

## Local Components

### Project-Specific Modules

#### **Component 1: [Component Name]**
- **Purpose**: [Component purpose and responsibility]
- **Integration**: [How it integrates with other components]
- **Interface**: [Public interface and contracts]
- **Dependencies**: [Required dependencies and their versions]

#### **Component 2: [Component Name]**
- **Purpose**: [Component purpose and responsibility]
- **Integration**: [How it integrates with other components]
- **Interface**: [Public interface and contracts]
- **Dependencies**: [Required dependencies and their versions]

#### **Component N: [Component Name]**
- **Purpose**: [Component purpose and responsibility]
- **Integration**: [How it integrates with other components]
- **Interface**: [Public interface and contracts]
- **Dependencies**: [Required dependencies and their versions]

---

## Data Flow

### Project-Specific Data Architecture

#### **Input Formats and Validation**
- **Primary Input Format**: [Describe input format]
- **Validation Schema**: [Describe validation requirements]
- **Error Handling**: [Describe error handling strategy]
- **Security Considerations**: [Describe input security measures]

#### **Processing Pipeline**
```mermaid
graph TD
    A[Input Data] --> B[Processing Step 1]
    B --> C[Processing Step 2]
    C --> D[Processing Step N]
    D --> E[Output Generation]
```

#### **Output Specifications**
- **Primary Output Format**: [Describe output format]
- **Metadata Requirements**: [Describe metadata requirements]
- **File Organization**: [Describe file organization structure]
- **Quality Standards**: [Describe output quality requirements]

#### **Integration with Global Standards**
- **Global Pattern Compliance**: [How this project follows global patterns]
- **Universal Interface Implementation**: [How universal interfaces are implemented]
- **Validation Framework Integration**: [How validation framework is used]
- **Safety Protocol Adherence**: [How safety protocols are followed]

---

## Safety and Boundaries

### Project-Specific Safety Constraints

#### **Interpretation of Global Safety Protocols**
- **AI Safety Protocol Application**: [How AI safety protocols apply to this project]
- **Human-in-the-Loop Implementation**: [How human oversight is implemented]
- **Scope Creep Prevention**: [How scope creep is prevented in this project]
- **Real Data Requirements**: [How real data-only development is enforced]

#### **Project-Specific Risk Assessments**
- **Technical Risks**: [List technical risks and mitigation strategies]
- **Process Risks**: [List process risks and mitigation strategies]
- **Security Risks**: [List security risks and mitigation strategies]
- **Collaboration Risks**: [List collaboration risks and mitigation strategies]

#### **Local Validation Requirements**
- **Component-Level Validation**: [How individual components are validated]
- **Integration Validation**: [How component integration is validated]
- **End-to-End Validation**: [How complete workflows are validated]
- **Performance Validation**: [How performance requirements are validated]

#### **Integration Testing Boundaries**
- **Unit Testing Boundaries**: [Scope of unit testing]
- **Integration Testing Boundaries**: [Scope of integration testing]
- **System Testing Boundaries**: [Scope of system testing]
- **User Acceptance Testing Boundaries**: [Scope of user acceptance testing]

---

## Compliance Framework

### Global Standards Integration

#### **Safety Protocol Adherence Methods**
- **Protocol Implementation**: [How safety protocols are implemented]
- **Compliance Verification**: [How compliance is verified]
- **Violation Detection**: [How protocol violations are detected]
- **Correction Procedures**: [How violations are corrected]

#### **Architecture Principle Implementation**
- **SOLID Principles**: [How SOLID principles are applied]
- **Layer-Based Architecture**: [How layering is implemented]
- **Separation of Concerns**: [How concerns are separated]
- **Interface Design**: [How interfaces are designed and implemented]

#### **Validation and Testing Approaches**
- **Universal Validation Pattern**: [How universal validation patterns are used]
- **Milestone-Based Testing**: [How milestone-based testing is implemented]
- **Real Data Testing**: [How real data testing is conducted]
- **Automated Testing**: [How automated testing is implemented]

#### **Documentation and Reporting Standards**
- **Code Documentation**: [How code is documented]
- **Architecture Documentation**: [How architecture is documented]
- **Test Documentation**: [How tests are documented]
- **Progress Reporting**: [How progress is reported]

---

## Project-Specific Implementation Details

### Technology Stack
- **Primary Language/Framework**: [Main technology choices]
- **Supporting Technologies**: [Supporting technologies and tools]
- **Development Environment**: [Development environment setup]
- **Deployment Environment**: [Deployment environment requirements]

### Development Workflow
- **Development Methodology**: [Development approach and methodology]
- **Code Review Process**: [How code reviews are conducted]
- **Testing Strategy**: [Overall testing strategy]
- **Release Process**: [How releases are managed]

### Maintenance and Evolution
- **Maintenance Strategy**: [How project will be maintained]
- **Evolution Planning**: [How project will evolve over time]
- **Update Procedures**: [How updates and changes are managed]
- **Decommissioning Planning**: [How end-of-life will be handled]

---

## Architecture Compliance Checklist

### Design Principle Compliance
- [ ] **Single Responsibility**: Each module has one clear purpose
- [ ] **Open/Closed**: Modules open for extension, closed for modification
- [ ] **Liskov Substitution**: Components can be substituted safely
- [ ] **Interface Segregation**: Minimal, focused interfaces
- [ ] **Dependency Inversion**: High-level modules independent of low-level details

### Structural Compliance
- [ ] **No Circular Dependencies**: Clean dependency graph
- [ ] **Loose Coupling**: Components communicate through interfaces
- [ ] **Strong Cohesion**: Related functionality grouped together
- [ ] **Layer Integrity**: Clear architectural layer separation
- [ ] **Abstraction Boundaries**: Implementation details properly encapsulated

### Safety Protocol Compliance
- [ ] **AI Safety Protocols**: All AI safety protocols followed
- [ ] **Human-in-the-Loop**: Human oversight implemented where required
- [ ] **Scope Creep Prevention**: Scope boundaries maintained
- [ ] **Real Data Development**: Only real data used for development and testing

### Quality Assurance Compliance
- [ ] **Testing Strategy**: Comprehensive test coverage implemented
- [ ] **Validation Framework**: Universal validation patterns used
- [ ] **Performance Monitoring**: Performance requirements met
- [ ] **Documentation**: Complete and up-to-date documentation

---

## Integration with Global Architecture

### Global Pattern Implementation
This project implements the following global patterns:

1. **Universal Component Architecture**: All components follow universal component patterns
2. **Data Flow Architecture**: Data flow follows universal pipeline patterns
3. **Validation Architecture**: Validation follows universal 4-phase pattern
4. **Human-AI Collaboration**: Collaboration follows universal protocols

### Global Standards Compliance
- **Design Principles**: All universal design principles are followed
- **Safety Protocols**: All safety protocols are implemented
- **Validation Standards**: All validation standards are met
- **Documentation Standards**: All documentation standards are followed

### Global Integration Points
- **Template System**: Uses universal template system patterns
- **Input/Output Interfaces**: Implements universal interface standards
- **Error Handling**: Follows universal error handling patterns
- **Security Standards**: Implements universal security requirements

---

## Version History

**v1.0 ({date}):** Initial local architecture document for {project_name}, extending global architecture principles with project-specific implementations and compliance frameworks.

---

**This document serves as a project-specific extension of global architecture principles and must be maintained in sync with the global architecture document to ensure consistency and compliance across all projects.**
"""

def ensure_global_files():
    """Verify that required global files exist."""
    required = [
        GLOBAL_SAFETY_DIR / "AI_SAFETY_DEVELOPMENT_PROTOCOLS.md",
        GLOBAL_ARCH_DIR / "GLOBAL_SYSTEM_ARCHITECTURE.md",
    ]
    for path in required:
        if not os.path.exists(path):
            print(f"[ERROR] Missing required global file: {path}")
            print(f"[INFO] Please ensure global architecture files are set up in:")
            print(f"  - {GLOBAL_SAFETY_DIR}/")
            print(f"  - {GLOBAL_ARCH_DIR}/")
            sys.exit(1)
    
    print("[INFO] Global architecture files verified")

def create_symlink(target, link_path):
    """Create a symbolic link if it doesn't already exist."""
    if os.path.exists(link_path):
        if os.path.islink(link_path):
            print(f"[INFO] Symlink already exists: {link_path}")
            return
        else:
            print(f"[ERROR] Path exists but is not a symlink: {link_path}")
            sys.exit(1)
    
    try:
        os.symlink(target, link_path)
        print(f"[INFO] Created symlink: {link_path} -> {target}")
    except OSError as e:
        print(f"[ERROR] Failed to create symlink {link_path} -> {target}: {e}")
        sys.exit(1)

def create_project(project_name):
    """Create a new project with global architecture standards."""
    project_path = Path(project_name)
    if project_path.exists():
        print(f"[ERROR] Directory '{project_name}' already exists.")
        sys.exit(1)

    print(f"[INFO] Creating project at {project_path}")
    project_path.mkdir(parents=True)

    # 1. Symlink Global Safety Directory
    create_symlink(GLOBAL_SAFETY_DIR, project_path / "ai_safety")

    # 2. Architecture Setup
    arch_dir = project_path / "architecture"
    arch_dir.mkdir()
    # Symlink Global Architecture File
    create_symlink(f"{GLOBAL_ARCH_DIR}/GLOBAL_SYSTEM_ARCHITECTURE.md", 
                   arch_dir / "GLOBAL_SYSTEM_ARCHITECTURE.md")
    # Write Local Architecture Template with project-specific content
    current_date = datetime.now().strftime("%B %d, %Y")
    local_arch_content = LOCAL_ARCH_TEMPLATE.format(
        date=current_date,
        project_name=project_name,
        project_purpose_placeholder="[Describe the specific purpose and goals of this project]",
        project_scope_placeholder="[Define the boundaries and limitations of this project]",
        project_requirements_placeholder="[List specific technical and functional requirements]",
        success_criteria_placeholder="[Define measurable success criteria for this project]"
    )
    with open(arch_dir / "LOCAL_SYSTEM_ARCHITECTURE.md", "w") as f:
        f.write(local_arch_content)
    print(f"[INFO] Created local architecture template")

    # 3. Standard Directories
    for folder in ["src", "tests", "docs"]:
        (project_path / folder).mkdir()
        if folder in ["src", "tests"]:
            open(project_path / folder / "__init__.py", "w").close()
    print(f"[INFO] Created standard directories")

    # 4. Meta Files
    with open(project_path / ".gitignore", "w") as f:
        f.write("__pycache__/\n.env\n.DS_Store\n*.pyc\n")
    with open(project_path / "README.md", "w") as f:
        f.write(f"""# {project_name}

Generated via create-project CLI with global architecture standards.

## Architecture

This project follows global architecture principles defined in:
- `ai_safety/AI_SAFETY_DEVELOPMENT_PROTOCOLS.md`
- `architecture/GLOBAL_SYSTEM_ARCHITECTURE.md`
- `architecture/LOCAL_SYSTEM_ARCHITECTURE.md`

## Getting Started

1. Review the architecture documents
2. Update the local architecture with project-specific details
3. Follow the safety protocols for all development

## Compliance

This project complies with:
- AI Safety Development Protocols
- Global System Architecture Principles
- Universal Validation Framework
- Human-AI Collaboration Protocols

## Development

This project includes standard Python project structure:
- `src/` - Source code
- `tests/` - Test files
- `docs/` - Documentation

## Next Steps

1. Update `architecture/LOCAL_SYSTEM_ARCHITECTURE.md` with project-specific details
2. Begin development following the safety protocols
3. Use the validation frameworks for testing and quality assurance
""")
    print(f"[INFO] Created meta files")

    print(f"[SUCCESS] Project '{project_name}' scaffolded with global architecture standards.")
    print(f"[INFO] Next steps:")
    print(f"  1. cd {project_name}")
    print(f"  2. Review architecture/LOCAL_SYSTEM_ARCHITECTURE.md")
    print(f"  3. Update with project-specific details")
    print(f"  4. Follow ai_safety/AI_SAFETY_DEVELOPMENT_PROTOCOLS.md for all development")

def main():
    """Main entry point for the CLI tool."""
    if len(sys.argv) != 2:
        print("Usage: create-project <project_name>")
        print("Creates a new Python project with global architecture standards.")
        sys.exit(1)
    
    project_name = sys.argv[1]
    
    # Validate project name
    if not project_name.isidentifier():
        print(f"[ERROR] Project name '{project_name}' is not a valid Python identifier.")
        print("[INFO] Project names should contain only letters, numbers, and underscores.")
        print("[INFO] They must start with a letter or underscore.")
        sys.exit(1)
    
    ensure_global_files()
    create_project(project_name)

if __name__ == "__main__":
    main()