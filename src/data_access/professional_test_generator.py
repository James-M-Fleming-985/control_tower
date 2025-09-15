#!/usr/bin/env python3
"""
Quality-Aware TestGenerator - Phase 2A with Automated Professional Standards
Integrates TestGenerator with automated quality gates for professional compliance
"""

from typing import Dict, Any, List
from pathlib import Path

from src.data_access.test_generator import TestGenerator, GeneratedTest
from src.data_access.requirements_models import ParsedRequirement
from src.quality_gates import create_professional_standards_context
from src.quality_gates.test_generator_gate import TestGeneratorQualityGate


class ProfessionalTestGenerator:
    """
    TestGenerator with integrated quality gates and professional standards enforcement
    
    This wrapper ensures that all test generation operations meet professional
    standards before allowing progression. No test generation without quality validation.
    """
    
    def __init__(self, workspace_root: str = "/workspaces/control_tower"):
        self.workspace_root = Path(workspace_root)
        self.test_generator = TestGenerator()
        self.quality_gate = TestGeneratorQualityGate(str(workspace_root))
        
    def generate_professional_tests(self, requirement: ParsedRequirement) -> List[GeneratedTest]:
        """
        Generate tests with automated professional standards validation
        
        This method enforces quality gates before, during, and after test generation
        to ensure professional standards are met.
        """
        print("🛡️ PROFESSIONAL TEST GENERATION")
        print("=" * 50)
        
        # Create professional standards context
        context = create_professional_standards_context(
            operation="test_generation",
            requirement_id=requirement.requirement_id,
            component="test_generator"
        )
        
        try:
            # Execute quality gate validation
            quality_result = self.quality_gate.execute_quality_gate(context)
            
            # Check if quality standards are met
            if quality_result.status.value != "passed":
                print("❌ PROFESSIONAL STANDARDS VIOLATION")
                print("🚫 TEST GENERATION BLOCKED")
                for violation in quality_result.violations:
                    print(f"   🔥 {violation}")
                for recommendation in quality_result.recommendations:
                    print(f"   💡 {recommendation}")
                
                raise ProfessionalStandardsViolation(
                    "TestGenerator does not meet professional standards",
                    quality_result.violations,
                    "test_generation"
                )
            
            # Quality gates passed - proceed with test generation
            print("✅ PROFESSIONAL STANDARDS MET")
            print("✅ PROCEEDING WITH TEST GENERATION")
            
            # Generate tests using validated TestGenerator
            generated_tests = self.test_generator.generate_tests_from_requirement(requirement)
            
            # Validate generated tests meet professional standards
            self._validate_generated_tests(generated_tests)
            
            print(f"✅ GENERATED {len(generated_tests)} PROFESSIONAL-GRADE TESTS")
            return generated_tests
            
        except Exception as e:
            print(f"❌ TEST GENERATION FAILED: {e}")
            raise
    
    def generate_professional_unit_tests(self, requirement: ParsedRequirement) -> List[GeneratedTest]:
        """Generate unit tests with professional standards validation"""
        return self.generate_professional_tests(requirement)
    
    def generate_professional_integration_tests(self, requirement: ParsedRequirement) -> List[GeneratedTest]:
        """Generate integration tests with professional standards validation"""
        context = create_professional_standards_context(
            operation="integration_test_generation",
            requirement_id=requirement.requirement_id
        )
        
        # Execute quality validation
        quality_result = self.quality_gate.execute_quality_gate(context)
        
        if quality_result.status.value != "passed":
            raise ProfessionalStandardsViolation(
                "Cannot generate integration tests - professional standards not met",
                quality_result.violations
            )
        
        return self.test_generator.generate_integration_tests(requirement)
    
    def create_professional_test_structure(self, component_name: str, test_type: str = "unit") -> str:
        """Create test file structure with professional standards validation"""
        context = create_professional_standards_context(
            operation="test_structure_creation",
            component_name=component_name,
            test_type=test_type
        )
        
        # Execute quality validation
        quality_result = self.quality_gate.execute_quality_gate(context)
        
        if quality_result.status.value != "passed":
            raise ProfessionalStandardsViolation(
                "Cannot create test structure - professional standards not met",
                quality_result.violations
            )
        
        return self.test_generator.create_test_file_structure(component_name, test_type)
    
    def _validate_generated_tests(self, generated_tests: List[GeneratedTest]):
        """Validate that generated tests meet professional standards"""
        if not generated_tests:
            raise ValueError("No tests generated - professional standards require test coverage")
        
        for test in generated_tests:
            # Validate test structure
            if not test.test_name.startswith("test_"):
                raise ValueError(f"Test name {test.test_name} doesn't follow professional naming conventions")
            
            # Validate test code contains assertions
            if "assert" not in test.test_code:
                raise ValueError(f"Test {test.test_name} lacks assertions - professional standards require proper validation")
            
            # Validate test has proper docstring
            if '"""' not in test.test_code:
                raise ValueError(f"Test {test.test_name} lacks docstring - professional standards require documentation")


class ProfessionalStandardsViolation(Exception):
    """Exception raised when professional standards are violated"""
    
    def __init__(self, message: str, violations: List[str] = None, component: str = None):
        super().__init__(message)
        self.violations = violations or []
        self.component = component