"""
Business Logic Layer Requirements Parser
LAYER-003-01-02-002 Requirements Extraction and Analysis

Parses business logic requirements for TDD implementation.
Focuses on REAL verification algorithms and stage gate enforcement.
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Any
from pathlib import Path


@dataclass
class FunctionalRequirement:
    """Business Logic functional requirement"""
    id: str
    title: str
    description: str
    business_problem: str
    acceptance_criteria: List[str]
    test_scenarios: List[str]


@dataclass
class QualityRequirement:
    """Business Logic quality requirement"""
    id: str
    category: str  # Performance, Reliability, Security
    requirement: str
    target_value: str
    measurement_method: str


@dataclass
class BusinessLogicRequirements:
    """Complete Business Logic Layer requirements"""
    layer_id: str
    functional_requirements: List[FunctionalRequirement]
    quality_requirements: List[QualityRequirement]
    dependencies: List[str]
    business_rules: List[str]


class BusinessLogicRequirementsParser:
    """Parse Business Logic Layer requirements for TDD implementation"""
    
    def __init__(self, requirements_file_path: str):
        self.requirements_file = Path(requirements_file_path)
        
    def parse_requirements(self) -> BusinessLogicRequirements:
        """Parse all Business Logic requirements"""
        content = self._read_requirements_file()
        
        return BusinessLogicRequirements(
            layer_id="LAYER-003-01-02-002",
            functional_requirements=self._extract_functional_requirements(content),
            quality_requirements=self._extract_quality_requirements(content),
            dependencies=self._extract_dependencies(content),
            business_rules=self._extract_business_rules(content)
        )
    
    def _read_requirements_file(self) -> str:
        """Read requirements document"""
        try:
            return self.requirements_file.read_text(encoding='utf-8')
        except FileNotFoundError:
            return ""
    
    def _extract_functional_requirements(self, content: str) -> List[FunctionalRequirement]:
        """Extract functional requirements with business problems"""
        requirements = []
        
        # F1: REAL test generation verification with physical file confirmation
        requirements.append(FunctionalRequirement(
            id="F1",
            title="REAL test generation verification with physical file confirmation",
            description="Verify that test files exist physically and contain valid test functions",
            business_problem="Prevent false positive verification when test files are missing or empty",
            acceptance_criteria=[
                "Must verify physical file existence on filesystem",
                "Must parse file content to confirm valid test functions", 
                "Must detect test file modifications and updates",
                "Must provide detailed verification evidence",
                "Must handle file corruption and access errors"
            ],
            test_scenarios=[
                "Verify existing test file with valid test functions",
                "Detect missing test file and fail verification",
                "Parse corrupted test file and report error",
                "Verify test file with multiple test functions",
                "Handle file permission errors gracefully"
            ]
        ))
        
        # F2: REAL stage gate validation with blocking enforcement logic
        requirements.append(FunctionalRequirement(
            id="F2", 
            title="REAL stage gate validation with blocking enforcement logic",
            description="Enforce TDD stage gates (RED->GREEN->REFACTOR) with blocking logic",
            business_problem="Prevent TDD workflow violations and ensure proper test-first development",
            acceptance_criteria=[
                "Must block progression from RED to GREEN without failing tests",
                "Must block progression from GREEN to REFACTOR without passing tests",
                "Must enforce minimum test coverage before stage progression",
                "Must validate test execution results before gate passage",
                "Must provide clear blocking reasons and remediation steps"
            ],
            test_scenarios=[
                "Block GREEN phase when tests are still failing",
                "Allow GREEN phase when all tests pass",
                "Block REFACTOR phase when coverage is insufficient", 
                "Allow REFACTOR phase when all gates pass",
                "Provide clear error messages for blocking reasons"
            ]
        ))
        
        # F3: REAL TDD compliance assessment with failure prevention
        requirements.append(FunctionalRequirement(
            id="F3",
            title="REAL TDD compliance assessment with failure prevention", 
            description="Assess TDD compliance and prevent non-compliant code progression",
            business_problem="Ensure code quality and prevent technical debt from TDD violations",
            acceptance_criteria=[
                "Must assess test-first development compliance",
                "Must validate test coverage meets minimum standards",
                "Must check for proper test structure and naming",
                "Must verify test independence and isolation",
                "Must prevent deployment of non-compliant code"
            ],
            test_scenarios=[
                "Assess compliant TDD workflow and pass validation",
                "Detect code-first development and fail assessment",
                "Validate sufficient test coverage and pass",
                "Detect insufficient coverage and fail validation",
                "Check test isolation and report violations"
            ]
        ))
        
        # F4: REAL test quality scoring with enforced minimum standards
        requirements.append(FunctionalRequirement(
            id="F4",
            title="REAL test quality scoring with enforced minimum standards",
            description="Score test quality and enforce minimum standards for progression",
            business_problem="Maintain high test quality and prevent low-quality tests from passing",
            acceptance_criteria=[
                "Must score test quality using multiple metrics",
                "Must enforce minimum quality thresholds",
                "Must provide detailed quality feedback",
                "Must prevent progression below quality standards",
                "Must suggest improvements for quality enhancement"
            ],
            test_scenarios=[
                "Score high-quality tests and allow progression",
                "Score low-quality tests and block progression",
                "Provide detailed quality metrics and feedback",
                "Suggest specific improvements for failing tests",
                "Validate quality improvements and update scores"
            ]
        ))
        
        return requirements
    
    def _extract_quality_requirements(self, content: str) -> List[QualityRequirement]:
        """Extract quality requirements"""
        requirements = []
        
        # Performance requirements
        requirements.extend([
            QualityRequirement("Q1", "Performance", "Response Time", "< 200ms for verification", "Response time measurement"),
            QualityRequirement("Q2", "Performance", "Throughput", "100+ verifications per second", "Load testing"),
            QualityRequirement("Q3", "Performance", "Memory Usage", "< 512MB for verification cache", "Memory profiling"),
            QualityRequirement("Q4", "Performance", "CPU Usage", "< 20% during verification", "CPU monitoring")
        ])
        
        # Reliability requirements  
        requirements.extend([
            QualityRequirement("Q5", "Reliability", "Error Rate", "< 0.1% for verification operations", "Error tracking"),
            QualityRequirement("Q6", "Reliability", "Availability", "99.9% uptime for verification service", "Uptime monitoring"),
            QualityRequirement("Q7", "Reliability", "Recovery Time", "< 10 seconds for verification recovery", "Recovery testing"),
            QualityRequirement("Q8", "Reliability", "Data Integrity", "100% verification accuracy", "Accuracy validation")
        ])
        
        # Security requirements
        requirements.extend([
            QualityRequirement("Q9", "Security", "Input Validation", "Secure verification parameter validation", "Security testing"),
            QualityRequirement("Q10", "Security", "Code Injection", "Prevent code injection in verification", "Injection testing"),
            QualityRequirement("Q11", "Security", "Access Control", "Secure verification access control", "Access testing"),
            QualityRequirement("Q12", "Security", "Audit Logging", "Complete verification audit trail", "Audit validation")
        ])
        
        return requirements
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract layer dependencies"""
        return [
            "LAY-003-01-02-001 (Data Access Layer)",
            "Test framework integration (pytest)",
            "File system access for test verification",
            "Memory management for verification caching"
        ]
    
    def _extract_business_rules(self, content: str) -> List[str]:
        """Extract key business rules"""
        return [
            "TDD stage gates must be enforced sequentially (RED -> GREEN -> REFACTOR)",
            "Test coverage below 75% blocks stage progression", 
            "Code changes without corresponding tests are rejected",
            "Test quality scores below B grade (75%) prevent deployment",
            "All verification evidence must be physically stored and auditable",
            "Stage gate violations must be logged and reported immediately"
        ]
    
    def generate_test_specifications(self) -> Dict[str, Any]:
        """Generate test specifications for TDD implementation"""
        requirements = self.parse_requirements()
        
        test_specs = {
            "red_phase_tests": [],
            "green_phase_tests": [],
            "refactor_phase_tests": [],
            "integration_tests": []
        }
        
        # Generate RED phase tests (failing tests for each requirement)
        for req in requirements.functional_requirements:
            test_specs["red_phase_tests"].extend([
                f"test_{req.id.lower()}_requirement_fails_without_implementation",
                f"test_{req.id.lower()}_business_problem_validation",
                f"test_{req.id.lower()}_acceptance_criteria_verification"
            ])
        
        # Generate GREEN phase tests (implementation validation)
        for req in requirements.functional_requirements:
            test_specs["green_phase_tests"].extend([
                f"test_{req.id.lower()}_implementation_satisfies_requirements",
                f"test_{req.id.lower()}_business_problem_solved",
                f"test_{req.id.lower()}_all_scenarios_pass"
            ])
        
        # Generate REFACTOR phase tests (quality and performance)
        for req in requirements.quality_requirements:
            test_specs["refactor_phase_tests"].append(
                f"test_{req.id.lower()}_{req.category.lower()}_{req.requirement.replace(' ', '_').lower()}"
            )
        
        # Integration tests
        test_specs["integration_tests"] = [
            "test_business_logic_integrates_with_data_access_layer",
            "test_business_logic_provides_ui_interface", 
            "test_end_to_end_verification_workflow",
            "test_stage_gate_enforcement_across_layers"
        ]
        
        return test_specs


if __name__ == "__main__":
    # Example usage
    parser = BusinessLogicRequirementsParser(
        "projects/PROJECT-003 TDD ENFORCER/SYSTEM-003-01 CORE TDD WORKFLOW ENGINE/"
        "FEATURE-003-01-02 TEST GENERATION VERIFICATION SYSTEM/BUSINESS LOGIC LAYER/"
        "LAYER-003-01-02-002_business_logic_requirements.md"
    )
    
    requirements = parser.parse_requirements()
    test_specs = parser.generate_test_specifications()
    
    print("🔍 BUSINESS LOGIC REQUIREMENTS PARSED:")
    print(f"📋 Functional Requirements: {len(requirements.functional_requirements)}")
    print(f"⚡ Quality Requirements: {len(requirements.quality_requirements)}")
    print(f"🔗 Dependencies: {len(requirements.dependencies)}")
    print(f"📏 Business Rules: {len(requirements.business_rules)}")
    print(f"🧪 Test Specifications Generated: {sum(len(tests) for tests in test_specs.values())}")