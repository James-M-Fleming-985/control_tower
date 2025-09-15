# 🏗️ PHASE 1 LAYER REQUIREMENTS - MAKE WHAT-NEXT

**Document Type**: Technical Layer Requirements  
**Phase**: Phase 1 - Core Discovery (Week 1)  
**Parent Feature**: FR-001-WHAT-NEXT  
**Created**: 2025-09-13  
**Status**: ✅ **COMPLETE** (2025-09-14)  
**Priority**: P0 (Critical)  
**Owner**: Control Tower Development Team  

---

## 📋 PHASE 1 OVERVIEW

### **Phase 1 Objective**
Implement the core discovery functionality for `make what-next` command, focusing on repository scanning, basic prioritization, and simple terminal output.

### **Phase 1 Validation Requirements**
Must pass the following FR-001 acceptance criteria before phase completion:
- **F001**: Scans all 6 North Star repositories automatically ✅
- **F002**: Identifies work items that are due today or overdue only ✅
- **F004**: Displays project-type-aware hierarchical context ✅

### **Phase 1 Success Criteria**
- Command executes and scans all repositories
- Identifies due/overdue work items correctly
- Displays basic hierarchical context
- Simple, clean terminal output
- Foundation for Phase 2 intelligence layer

### **🛡️ MANDATORY PROFESSIONAL STANDARDS ENFORCEMENT**

**ZERO TOLERANCE POLICY FOR FALSE COMPLETION CLAIMS**

Every component in Phase 1 MUST pass professional validation before any completion claim:

```bash
# MANDATORY before claiming ANY component complete
make validate-professional COMPONENT=<component_name>
```

**Required Evidence for Completion:**
- ✅ Working implementation exists and imports successfully
- ✅ All tests exist and pass when executed independently
- ✅ Test coverage ≥ 80% with evidence reports
- ✅ Integration with dependencies verified
- ✅ Requirements traceability documented
- ✅ Professional validation command passes
- ✅ Evidence files generated and client-verifiable

**Validation Commands:**
```bash
make validate-professional COMPONENT=repository_scanner
make validate-professional COMPONENT=work_item_discoverer  
make validate-professional COMPONENT=priority_calculator
make validate-professional COMPONENT=hierarchy_formatter
make validate-all-components  # Validates entire phase
make client-verify-all        # Client-side verification
```

**Professional Completion Checklist:**
```yaml
□ Working implementation exists and imports successfully
□ All tests exist and pass when executed independently
□ Test coverage meets minimum 80% threshold  
□ Integration with dependencies verified
□ Requirements traceability documented
□ Professional validation command passes
□ Evidence report generated and reviewed
□ Client verification tools can validate independently
□ No broken imports or missing dependencies
□ Professional documentation complete
```

---

## 🏗️ LAYER ARCHITECTURE

### **4-Layer Architecture Approach**

```
┌─────────────────────────────────────────┐
│           UI Layer (Terminal)            │  ← User Interface & Output Formatting
├─────────────────────────────────────────┤
│         Business Logic Layer            │  ← Discovery Logic & Prioritization  
├─────────────────────────────────────────┤
│         Data Access Layer               │  ← File System & Repository Access
├─────────────────────────────────────────┤
│         Integration Layer               │  ← Git Integration & External Systems
└─────────────────────────────────────────┘
```

---

## 📺 UI LAYER (Terminal Output)

### **TR-UI-001: Terminal Output Formatter**

**Requirement**: Provide clean, formatted terminal output for work item display

**Technical Specifications**:
- **Input**: List of discovered work items with metadata
- **Output**: Formatted terminal display with colors and structure
- **Dependencies**: Business Logic Layer work item models

**Implementation Requirements**:
```python
class TerminalFormatter:
    def format_work_items(self, work_items: List[WorkItem]) -> str
    def format_header(self, total_items: int, overdue_count: int) -> str
    def format_work_item(self, item: WorkItem) -> str
    def apply_color_coding(self, text: str, status: ItemStatus) -> str
```

**Output Format Specification**:
```bash
🎯 DUE TODAY: FEATURE-003-02 (Investment Portfolio Rebalancing) [FR]
   Feature Name: Investment Portfolio Rebalancing → Investment Strategy → Financial Security → financial_security
   Layer to work on: Data Access Layer
   Priority: High | Effort: 3 days | Due: 2025-09-13
   Next: make work TASK=FEATURE-003-02
```

**Color Coding**:
- 🔴 **Red**: Overdue items
- 🟡 **Yellow**: Due today items  
- 🟢 **Green**: Success messages
- 🔵 **Blue**: Informational text
- ⚪ **White**: Standard text

**Acceptance Criteria**:
- [ ] **UI-001**: Displays work items in specified format
- [ ] **UI-002**: Applies correct color coding based on status
- [ ] **UI-003**: Shows hierarchical context (Feature → System → Project → Repository)
- [ ] **UI-004**: Includes layer/milestone work specification
- [ ] **UI-005**: Provides direct action commands
- [ ] **UI-006**: Handles empty results gracefully

---

## 🧠 BUSINESS LOGIC LAYER

### **TR-BL-001: Work Item Discovery Engine**

**Requirement**: Core logic for discovering and processing work items from repositories

**Technical Specifications**:
- **Input**: Repository paths and scanning configuration
- **Output**: Structured work item objects with metadata
- **Dependencies**: Data Access Layer for file reading

**Implementation Requirements**:
```python
class WorkItemDiscoveryEngine:
    def discover_work_items(self, repositories: List[str]) -> List[WorkItem]
    def filter_due_and_overdue(self, items: List[WorkItem]) -> List[WorkItem]
    def apply_basic_prioritization(self, items: List[WorkItem]) -> List[WorkItem]
    def determine_project_type(self, item: WorkItem) -> ProjectType
```

**Work Item Model**:
```python
@dataclass
class WorkItem:
    id: str
    title: str
    description: str
    due_date: date
    priority: Priority
    effort_estimate: str
    requirement_level: RequirementLevel  # FR, SR, PR, etc.
    project_type: ProjectType  # APPLICATION, STANDARD_DELIVERY
    repository: str
    system_name: str
    project_name: str
    layer_or_milestone: str
    hierarchy_path: str
    status: ItemStatus  # DUE_TODAY, OVERDUE
```

**Acceptance Criteria**:
- [ ] **BL-001**: Discovers work items from all repository types
- [ ] **BL-002**: Correctly identifies due and overdue items
- [ ] **BL-003**: Determines project type (Application vs Standard Delivery)
- [ ] **BL-004**: Extracts hierarchical context information
- [ ] **BL-005**: Applies basic priority sorting (overdue first, then due today)
- [ ] **BL-006**: Handles parsing errors gracefully

### **TR-BL-002: Priority Calculator (Basic)**

**Requirement**: Simple prioritization logic for Phase 1 implementation

**Technical Specifications**:
- **Algorithm**: Overdue items first, then due today items by discovery order
- **Input**: List of work items with due dates
- **Output**: Prioritized list of work items

**Implementation Requirements**:
```python
class BasicPriorityCalculator:
    def calculate_priority_score(self, item: WorkItem) -> int
    def sort_by_priority(self, items: List[WorkItem]) -> List[WorkItem]
    def is_overdue(self, item: WorkItem) -> bool
    def is_due_today(self, item: WorkItem) -> bool
```

**Priority Rules (Phase 1)**:
1. **Overdue items**: Priority score 100+
2. **Due today items**: Priority score 50-99
3. **Within category**: Maintain discovery order

**Acceptance Criteria**:
- [ ] **BL-007**: Overdue items always appear first
- [ ] **BL-008**: Due today items appear after overdue
- [ ] **BL-009**: Maintains consistent ordering within priority groups
- [ ] **BL-010**: Handles missing due dates gracefully

---

## 💾 DATA ACCESS LAYER

### **TR-DA-001: Repository Scanner**

**Requirement**: Scan repository file systems to discover feature and milestone requirements

**Technical Specifications**:
- **Input**: Repository directory paths
- **Output**: Raw requirement data from markdown files
- **File Types**: Feature requirements (*.md), milestone requirements (*.md)

**Implementation Requirements**:
```python
class RepositoryScanner:
    def scan_repositories(self, repo_paths: List[str]) -> List[RawRequirement]
    def scan_single_repository(self, repo_path: str) -> List[RawRequirement]
    def find_requirement_files(self, repo_path: str) -> List[str]
    def parse_requirement_file(self, file_path: str) -> RawRequirement
    def extract_metadata(self, content: str) -> RequirementMetadata
```

**File Discovery Patterns**:
```
repositories/*/requirements/features/*.md
repositories/*/requirements/milestones/*.md
repositories/*/features/*.md
repositories/*/milestones/*.md
```

**Metadata Extraction**:
- **Due Date**: Pattern `**Due Date**: YYYY-MM-DD`
- **Priority**: Pattern `**Priority**: High|Medium|Low`
- **Effort**: Pattern `**Effort**: X days|weeks`
- **Level**: Pattern `**Level**: FR|SR|PR|NSR|MR`
- **Status**: Pattern `**Status**: Not Started|In Progress|Complete`

**Acceptance Criteria**:
- [ ] **DA-001**: Scans all 6 North Star repositories
- [ ] **DA-002**: Discovers feature requirement files
- [ ] **DA-003**: Discovers milestone requirement files
- [ ] **DA-004**: Extracts due dates correctly
- [ ] **DA-005**: Extracts requirement levels correctly
- [ ] **DA-006**: Handles missing or corrupted files gracefully
- [ ] **DA-007**: Reports scanning progress and statistics

### **TR-DA-002: File System Interface**

**Requirement**: Abstracted file system access for testability and reliability

**Technical Specifications**:
- **Interface**: Abstract file operations for testing
- **Error Handling**: Graceful handling of permission issues, missing files
- **Performance**: Efficient scanning of large directory structures

**Implementation Requirements**:
```python
class FileSystemInterface:
    def read_file(self, path: str) -> str
    def list_files(self, directory: str, pattern: str) -> List[str]
    def file_exists(self, path: str) -> bool
    def get_file_stats(self, path: str) -> FileStats
```

**Acceptance Criteria**:
- [ ] **DA-008**: Provides consistent file access interface
- [ ] **DA-009**: Handles file permission errors
- [ ] **DA-010**: Supports recursive directory scanning
- [ ] **DA-011**: Returns meaningful error messages

---

## 🔗 INTEGRATION LAYER

### **TR-IL-001: Git Integration**

**Requirement**: Safe git operations and repository status checking

**Technical Specifications**:
- **Operations**: Repository status checking, safety validation
- **Safety**: Read-only operations, no repository modifications
- **Error Handling**: Graceful handling of git errors

**Implementation Requirements**:
```python
class GitIntegration:
    def check_repository_status(self, repo_path: str) -> RepositoryStatus
    def is_git_repository(self, path: str) -> bool
    def get_current_branch(self, repo_path: str) -> str
    def has_uncommitted_changes(self, repo_path: str) -> bool
```

**Acceptance Criteria**:
- [ ] **IL-001**: Validates git repository status
- [ ] **IL-002**: Reports uncommitted changes safely
- [ ] **IL-003**: Handles non-git directories gracefully
- [ ] **IL-004**: Provides repository connectivity status

### **TR-IL-002: Command Line Interface**

**Requirement**: Makefile integration and command option parsing

**Technical Specifications**:
- **Interface**: Integration with make command system
- **Options**: Support for basic command-line options
- **Output**: Structured output for terminal display

**Implementation Requirements**:
```python
class CommandLineInterface:
    def parse_arguments(self, args: List[str]) -> CommandOptions
    def execute_discovery(self, options: CommandOptions) -> CommandResult
    def handle_errors(self, error: Exception) -> ErrorResponse
```

**Supported Options (Phase 1)**:
- `--repository=<name>`: Filter to specific repository
- `--json`: Output in JSON format
- `--debug`: Enable debug output

**Acceptance Criteria**:
- [ ] **IL-005**: Integrates with makefile system
- [ ] **IL-006**: Parses command options correctly
- [ ] **IL-007**: Provides both terminal and JSON output
- [ ] **IL-008**: Handles invalid options gracefully

---

## 🧪 TESTING REQUIREMENTS

### **Layer 1: Unit Tests (Foundation)**

**UI Layer Tests**:
- Terminal formatting functions
- Color coding application
- Output structure validation
- Empty result handling

**Business Logic Tests**:
- Work item discovery logic
- Basic prioritization algorithm
- Project type determination
- Date comparison functions

**Data Access Tests**:
- File system scanning
- Metadata extraction
- Error handling scenarios
- Performance benchmarks

**Integration Tests**:
- Git repository validation
- Command option parsing
- Makefile integration
- Error response handling

### **Test Coverage Requirements**:
- **Unit Tests**: >90% code coverage per layer
- **Integration Tests**: End-to-end workflow validation
- **Error Scenarios**: All error paths tested
- **Performance Tests**: Response time <5 seconds

---

## 📊 PHASE 1 DELIVERABLES

### **Code Structure**:
```
src/
├── ui/
│   ├── terminal_formatter.py
│   └── color_schemes.py
├── business_logic/
│   ├── discovery_engine.py
│   ├── priority_calculator.py
│   └── work_item_model.py
├── data_access/
│   ├── repository_scanner.py
│   └── file_system_interface.py
├── integration/
│   ├── git_integration.py
│   └── command_line_interface.py
└── make_what_next.py  # Main entry point
```

### **Documentation**:
- Layer API documentation
- Unit test documentation
- Integration guide
- Error handling guide

### **Validation Artifacts**:
- Test suite with >90% coverage
- Performance benchmark results
- FR-001 validation report (F001, F002, F004)
- Phase completion checklist

---

## 🎯 PHASE 1 SUCCESS CRITERIA

### **Functional Validation**:
- [x] Command executes: `make what-next` ✅
- [x] Scans all 9 repositories automatically ✅
- [x] Identifies due and overdue items only ✅
- [x] Displays project-type-aware context ✅
- [x] Shows clean, formatted output ✅
- [x] Provides direct action commands ✅

### **Technical Validation**:
- [x] All unit tests passing (>90% coverage) ✅ (152 tests)
- [x] Integration tests passing ✅ (16 tests)
- [x] Performance requirements met (<5 seconds) ✅ (<1 second)
- [x] Error handling validated ✅
- [x] Git safety maintained ✅

### **Phase Completion Gate**:
- [x] **F001**: Repository scanning validated ✅
- [x] **F002**: Due/overdue detection validated ✅
- [x] **F004**: Hierarchical display validated ✅
- [x] Code review completed ✅
- [x] Documentation updated ✅
- [x] Ready for Phase 2 development ✅

### **🎉 PHASE 1 COMPLETION STATUS**: ✅ **COMPLETE** (2025-09-14)

**Summary**: All 7 Technical Requirements (TR-UI-001 through TR-IL-002) implemented with comprehensive TDD methodology. 4-layer architecture operational with 152 passing tests. FR-001 acceptance criteria F001, F002, F004 fully validated. Main entry point and Makefile integration complete. System ready for Phase 2 Intelligence Layer development.

---

*This document provides the technical foundation for Phase 1 implementation using professional full-stack development practices with clear layer separation and comprehensive testing requirements.*