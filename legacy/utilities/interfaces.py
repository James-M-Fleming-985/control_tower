"""
Interface Definitions for Requirements Parser & Test Generator Layer

This module defines the data models and interfaces that serve as contracts
between the Data Access Layer and Business Logic Layer, following FR-002
compliance with forcing functions and verification at each stage.

Created: 2025-09-15
Layer: Data Access (Requirements Parser & Test Generator)  
TDD Phase: Architecture Definition (Pre-RED)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Union
from pathlib import Path
from enum import Enum
from datetime import datetime


class TestGenerationStatus(Enum):
    """Status of test generation process"""
    NOT_STARTED = "not_started"
    PARSING_REQUIREMENTS = "parsing_requirements"
    GENERATING_TESTS = "generating_tests"
    VALIDATING_TESTS = "validating_tests"
    COMPLETED = "completed"
    FAILED = "failed"


class RequirementParsingStatus(Enum):
    """Status of requirement parsing process"""
    NOT_STARTED = "not_started"
    READING_FILE = "reading_file"
    PARSING_CONTENT = "parsing_content"
    EXTRACTING_CRITERIA = "extracting_criteria"
    VALIDATING_COMPLETENESS = "validating_completeness"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ValidationResult:
    """Result of requirement validation with forcing function compliance"""
    is_valid: bool
    error_messages: List[str] = field(default_factory=list)
    warning_messages: List[str] = field(default_factory=list)
    validation_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    forcing_function_passed: bool = False
    terminal_output: str = ""
    
    def add_error(self, message: str) -> None:
        """Add an error message and mark validation as failed"""
        self.error_messages.append(message)
        self.is_valid = False
    
    def add_warning(self, message: str) -> None:
        """Add a warning message"""
        self.warning_messages.append(message)
    
    def set_forcing_function_result(self, passed: bool, output: str) -> None:
        """Set forcing function result with terminal output"""
        self.forcing_function_passed = passed
        self.terminal_output = output
        if not passed:
            self.is_valid = False


@dataclass 
class TraceabilityData:
    """Traceability information linking requirements to tests"""
    requirement_id: str
    parent_requirement_ids: List[str] = field(default_factory=list)
    child_requirement_ids: List[str] = field(default_factory=list)
    generated_test_ids: List[str] = field(default_factory=list)
    source_file_path: str = ""
    target_test_file_paths: List[str] = field(default_factory=list)
    traceability_matrix: Dict[str, List[str]] = field(default_factory=dict)
    creation_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AcceptanceCriteria:
    """Single acceptance criterion with testability information"""
    id: str
    description: str
    criterion_type: str = "functional"  # functional, non_functional, boundary, error
    is_testable: bool = True
    test_approach: str = ""  # unit, integration, system, manual
    priority: str = "normal"  # high, normal, low
    complexity: str = "simple"  # simple, medium, complex
    dependencies: List[str] = field(default_factory=list)
    given: Optional[str] = None  # For Given-When-Then format
    when: Optional[str] = None
    then: Optional[str] = None
    completed: bool = False
    test_generated: bool = False
    verification_method: str = "automated_test"
    
    def validate(self) -> ValidationResult:
        """Validate that acceptance criteria is well-formed and testable"""
        result = ValidationResult(is_valid=True)
        
        if not self.id:
            result.add_error("Acceptance criteria must have an ID")
        
        if not self.description:
            result.add_error("Acceptance criteria must have a description")
        
        if self.criterion_type == "given_when_then":
            if not (self.given and self.when and self.then):
                result.add_error("Given-When-Then criteria must have all three parts")
        
        if not self.is_testable:
            result.add_warning("Criteria marked as not testable - may need manual validation")
        
        return result


@dataclass
class ParsedRequirement:
    """Complete parsed requirement with all extracted information"""
    # Core identification
    requirement_id: str
    requirement_type: str
    level: Optional[int] = None
    
    # Metadata
    parent_system: Optional[str] = None
    repository: Optional[str] = None
    status: Optional[str] = None
    created: Optional[str] = None
    
    # Timeline information
    duration: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None
    effort_estimate: Optional[str] = None
    
    # Content
    primary_objective: Optional[str] = None
    acceptance_criteria: List[Dict[str, Any]] = field(default_factory=list)
    layer_implementation: Optional[str] = None
    integration_points: Optional[str] = None
    
    # File information
    source_file_path: str = ""
    parsing_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    parsing_status: RequirementParsingStatus = RequirementParsingStatus.NOT_STARTED
    
    # Validation
    validation_result: Optional[ValidationResult] = None
    traceability_data: Optional[TraceabilityData] = None
    
    def validate(self) -> ValidationResult:
        """Validate that parsed requirement is complete and well-formed"""
        result = ValidationResult(is_valid=True)
        
        # Core validation
        if not self.requirement_id:
            result.add_error("Requirement must have an ID")
        
        if not self.requirement_type:
            result.add_error("Requirement must have a type")
        
        if not self.primary_objective:
            result.add_warning("Requirement should have a primary objective")
        
        if not self.acceptance_criteria:
            result.add_error("Requirement must have acceptance criteria for test generation")
        
        # Acceptance criteria validation
        for i, criteria in enumerate(self.acceptance_criteria):
            if not isinstance(criteria, dict):
                result.add_error(f"Acceptance criteria {i} is not properly formatted")
                continue
            
            if 'id' not in criteria or 'description' not in criteria:
                result.add_error(f"Acceptance criteria {i} missing required fields")
        
        # File validation
        if self.source_file_path:
            source_path = Path(self.source_file_path)
            if not source_path.exists():
                result.add_warning(f"Source file not found: {self.source_file_path}")
        
        self.validation_result = result
        return result
    
    def get_testable_criteria(self) -> List[AcceptanceCriteria]:
        """Extract testable acceptance criteria as AcceptanceCriteria objects"""
        testable_criteria = []
        
        for criteria_dict in self.acceptance_criteria:
            criteria = AcceptanceCriteria(
                id=criteria_dict.get('id', f"AC-{len(testable_criteria)+1:03d}"),
                description=criteria_dict.get('description', ''),
                criterion_type=criteria_dict.get('type', 'functional')
            )
            
            if criteria.validate().is_valid:
                testable_criteria.append(criteria)
        
        return testable_criteria


@dataclass
class GeneratedTest:
    """A single generated test with metadata"""
    test_id: str
    test_name: str
    test_function_name: str
    acceptance_criteria_id: str
    test_code: str
    test_type: str = "unit"  # unit, integration, system
    framework: str = "pytest"
    file_path: str = ""
    
    # Test execution information
    is_failing: bool = True  # Should be True in RED phase
    failure_reason: str = ""
    execution_time: Optional[float] = None
    last_run_timestamp: Optional[str] = None
    
    # Dependencies and setup
    imports: List[str] = field(default_factory=list)
    fixtures: List[str] = field(default_factory=list)
    mocks: List[str] = field(default_factory=list)
    setup_code: str = ""
    teardown_code: str = ""
    
    def validate_syntax(self) -> ValidationResult:
        """Validate that generated test code has correct syntax"""
        result = ValidationResult(is_valid=True)
        
        if not self.test_code:
            result.add_error("Test code cannot be empty")
            return result
        
        try:
            # Try to compile the test code
            compile(self.test_code, f"<test_{self.test_id}>", "exec")
        except SyntaxError as e:
            result.add_error(f"Syntax error in test code: {e}")
        except Exception as e:
            result.add_error(f"Compilation error in test code: {e}")
        
        # Check for required pytest elements
        if "def test_" not in self.test_code:
            result.add_error("Test code must contain a test function starting with 'test_'")
        
        if "assert" not in self.test_code:
            result.add_warning("Test code should contain assertions")
        
        return result


@dataclass
class TestFile:
    """Complete test file with multiple tests"""
    file_path: str
    requirement_id: str
    generated_tests: List[GeneratedTest] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    fixtures: List[str] = field(default_factory=list)
    setup_code: str = ""
    teardown_code: str = ""
    
    # File metadata
    creation_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    last_modified: Optional[str] = None
    total_tests: int = 0
    passing_tests: int = 0
    failing_tests: int = 0
    
    def generate_file_content(self) -> str:
        """Generate complete test file content"""
        lines = []
        
        # Add file header
        lines.append('"""')
        lines.append(f"Generated tests for requirement: {self.requirement_id}")
        lines.append(f"Generated on: {self.creation_timestamp}")
        lines.append(f"Total tests: {len(self.generated_tests)}")
        lines.append('"""')
        lines.append("")
        
        # Add imports
        default_imports = [
            "import pytest",
            "from unittest.mock import Mock, patch, MagicMock",
            "from pathlib import Path",
            "import tempfile",
            "import json"
        ]
        
        all_imports = default_imports + self.imports
        for import_line in sorted(set(all_imports)):
            lines.append(import_line)
        lines.append("")
        
        # Add fixtures
        for fixture in self.fixtures:
            lines.append(fixture)
            lines.append("")
        
        # Add setup code
        if self.setup_code:
            lines.append(self.setup_code)
            lines.append("")
        
        # Add test functions
        for test in self.generated_tests:
            lines.append(test.test_code)
            lines.append("")
        
        # Add teardown code
        if self.teardown_code:
            lines.append(self.teardown_code)
        
        return "\n".join(lines)
    
    def update_test_counts(self) -> None:
        """Update test count statistics"""
        self.total_tests = len(self.generated_tests)
        self.passing_tests = sum(1 for test in self.generated_tests if not test.is_failing)
        self.failing_tests = sum(1 for test in self.generated_tests if test.is_failing)


@dataclass
class TestValidationResult:
    """Result of test validation with execution details"""
    is_valid: bool
    syntax_errors: List[str] = field(default_factory=list)
    execution_errors: List[str] = field(default_factory=list)
    test_results: Dict[str, Any] = field(default_factory=dict)
    coverage_percentage: Optional[float] = None
    forcing_function_passed: bool = False
    terminal_output: str = ""
    
    def add_syntax_error(self, error: str) -> None:
        """Add a syntax error"""
        self.syntax_errors.append(error)
        self.is_valid = False
    
    def add_execution_error(self, error: str) -> None:
        """Add an execution error"""
        self.execution_errors.append(error)
        self.is_valid = False


@dataclass
class FailureValidation:
    """Validation that tests fail correctly (RED phase verification)"""
    total_tests: int
    failing_tests: int
    passing_tests: int
    syntax_error_tests: int
    correct_failure_tests: int
    incorrect_failure_tests: int
    
    # Forcing function compliance
    forcing_function_passed: bool = False
    terminal_output: str = ""
    validation_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def failure_percentage(self) -> float:
        """Percentage of tests that are failing correctly"""
        if self.total_tests == 0:
            return 0.0
        return (self.correct_failure_tests / self.total_tests) * 100
    
    @property
    def is_red_phase_valid(self) -> bool:
        """Check if RED phase is valid (all tests failing correctly)"""
        return (
            self.total_tests > 0 and
            self.syntax_error_tests == 0 and
            self.passing_tests == 0 and
            self.correct_failure_tests == self.total_tests
        )
    
    def generate_verification_output(self) -> str:
        """Generate terminal output for forcing function verification"""
        if self.is_red_phase_valid:
            output = f"✅ RED phase verified - all tests failing correctly ({self.failing_tests}/{self.total_tests} failing)"
        else:
            output = f"❌ RED phase verification failed:\n"
            output += f"  - Total tests: {self.total_tests}\n"
            output += f"  - Correctly failing: {self.correct_failure_tests}\n"
            output += f"  - Incorrectly failing: {self.incorrect_failure_tests}\n"
            output += f"  - Syntax errors: {self.syntax_error_tests}\n"
            output += f"  - Passing (should be 0): {self.passing_tests}"
        
        self.terminal_output = output
        self.forcing_function_passed = self.is_red_phase_valid
        return output


# Interface protocols for dependency injection and testing
from abc import ABC, abstractmethod


class RequirementsParserInterface(ABC):
    """Interface for requirements parsing with FR-002 compliance"""
    
    @abstractmethod
    def parse_work_item_requirements(self, item_id: str) -> ParsedRequirement:
        """Parse work item requirements with forcing function verification"""
        pass
    
    @abstractmethod
    def extract_acceptance_criteria(self, markdown_content: str) -> List[AcceptanceCriteria]:
        """Extract acceptance criteria with forcing function verification"""
        pass
    
    @abstractmethod
    def validate_requirement_completeness(self, requirement: ParsedRequirement) -> ValidationResult:
        """Validate requirement completeness with forcing function verification"""
        pass
    
    @abstractmethod
    def create_requirement_traceability(self, requirement: ParsedRequirement) -> TraceabilityData:
        """Create requirement traceability with forcing function verification"""
        pass


class TestGeneratorInterface(ABC):
    """Interface for test generation with FR-002 compliance"""
    
    @abstractmethod
    def generate_failing_tests(self, parsed_requirement: ParsedRequirement) -> List[GeneratedTest]:
        """Generate failing tests with forcing function verification"""
        pass
    
    @abstractmethod
    def create_test_file_structure(self, tests: List[GeneratedTest], requirement: ParsedRequirement) -> TestFile:
        """Create test file structure with forcing function verification"""
        pass
    
    @abstractmethod
    def validate_test_generation(self, test_file: TestFile) -> TestValidationResult:
        """Validate test generation with forcing function verification"""
        pass
    
    @abstractmethod
    def ensure_tests_fail_correctly(self, test_file: TestFile) -> FailureValidation:
        """Ensure tests fail correctly with forcing function verification"""
        pass


class FileSystemInterface(ABC):
    """Interface for file system operations"""
    
    @abstractmethod
    def read_requirement_file(self, file_path: str) -> str:
        """Read requirement file content"""
        pass
    
    @abstractmethod
    def write_test_file(self, test_file: TestFile) -> bool:
        """Write test file to filesystem"""
        pass
    
    @abstractmethod
    def validate_file_access(self, file_path: str) -> ValidationResult:
        """Validate file access permissions"""
        pass