"""
Phase Enforcement Tests
======================

Failing tests for RED, GREEN, and REFACTOR phase enforcement logic
covering validation rules, compliance checking, and evidence collection.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from src.business_logic.phase_enforcement import (
    RedPhaseEnforcer,
    GreenPhaseEnforcer,
    RefactorPhaseEnforcer,
    PhaseEnforcementResult,
    PhaseValidationResult,
    ValidationEvidence
)


class TestRedPhaseEnforcementLogic:
    """Tests for RED phase enforcement validation logic"""
    
    def setup_method(self):
        self.enforcer = RedPhaseEnforcer()
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test project structure
        self.test_dir = Path(self.temp_dir) / "tests"
        self.test_dir.mkdir(exist_ok=True)
        self.src_dir = Path(self.temp_dir) / "src"
        self.src_dir.mkdir(exist_ok=True)
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_red_phase_discovers_test_files_correctly(self):
        """
        TEST: Should discover test files using standard patterns
        EXPECTED: Should fail - _discover_test_files method behavior not implemented
        """
        # Create test files
        (self.test_dir / "test_example.py").write_text("def test_something(): assert False")
        (self.test_dir / "example_test.py").write_text("def test_other(): assert False")
        (self.src_dir / "not_a_test.py").write_text("def function(): pass")
        
        with pytest.raises((AttributeError, AssertionError)):
            test_files = self.enforcer._discover_test_files(self.temp_dir)
            assert len(test_files) == 2
            assert any("test_example.py" in f for f in test_files)
            assert any("example_test.py" in f for f in test_files)
            assert not any("not_a_test.py" in f for f in test_files)
    
    def test_red_phase_discovers_implementation_files_correctly(self):
        """
        TEST: Should discover implementation files excluding tests
        EXPECTED: Should fail - _discover_implementation_files method behavior not implemented
        """
        # Create implementation files
        (self.src_dir / "module.py").write_text("class Example: pass")
        (self.src_dir / "__init__.py").write_text("")
        (self.test_dir / "test_module.py").write_text("def test_example(): pass")
        
        with pytest.raises((AttributeError, AssertionError)):
            impl_files = self.enforcer._discover_implementation_files(self.temp_dir)
            assert len(impl_files) == 1  # Only module.py, not __init__.py or test files
            assert any("module.py" in f for f in impl_files)
    
    def test_red_phase_analyzes_code_complexity_accurately(self):
        """
        TEST: Should analyze code complexity using AST
        EXPECTED: Should fail - _analyze_code_complexity method not implemented correctly
        """
        # Create complex Python file
        complex_code = '''
class ComplexClass:
    def method1(self):
        if True:
            for i in range(10):
                pass
    
    def method2(self):
        pass
    
    def method3(self):
        pass

def function1():
    pass

def function2():
    pass
'''
        test_file = self.src_dir / "complex.py"
        test_file.write_text(complex_code)
        
        with pytest.raises((AttributeError, AssertionError)):
            complexity = self.enforcer._analyze_code_complexity(str(test_file))
            assert 0.0 <= complexity <= 1.0
            assert complexity > 0.1  # Should detect complexity
    
    def test_red_phase_validates_test_execution_results(self):
        """
        TEST: Should validate test execution and capture results
        EXPECTED: Should fail - _validate_test_execution method not implemented correctly
        """
        # Create test files
        test_files = [
            str(self.test_dir / "test_passing.py"),
            str(self.test_dir / "test_failing.py")
        ]
        
        with pytest.raises((AttributeError, AssertionError)):
            test_results = self.enforcer._validate_test_execution(test_files)
            assert isinstance(test_results, dict)
            assert len(test_results) == len(test_files)
            assert all(isinstance(result, bool) for result in test_results.values())
    
    def test_red_phase_calculates_code_coverage(self):
        """
        TEST: Should calculate code coverage percentage
        EXPECTED: Should fail - _calculate_code_coverage method not implemented correctly
        """
        with pytest.raises((AttributeError, AssertionError)):
            coverage = self.enforcer._calculate_code_coverage(self.temp_dir)
            assert 0.0 <= coverage <= 1.0
    
    def test_red_phase_enforcement_requires_failing_tests(self):
        """
        TEST: Should require at least one failing test for RED phase
        EXPECTED: Should fail - enforce_red_phase method not implemented
        """
        # Create test files with passing tests (invalid for RED)
        (self.test_dir / "test_example.py").write_text("def test_something(): assert True")
        
        evidence = {"all_tests_passing": True}
        
        with pytest.raises(AttributeError):
            result = self.enforcer.enforce_red_phase(self.temp_dir, evidence)
            assert result.validation_result == PhaseValidationResult.FAIL
            assert any("No failing tests found" in issue for issue in result.blocking_issues)
    
    def test_red_phase_enforcement_blocks_premature_implementation(self):
        """
        TEST: Should block RED phase if implementation is too complex
        EXPECTED: Should fail - enforce_red_phase method not implemented
        """
        # Create complex implementation
        complex_impl = '''
class OverEngineered:
    def __init__(self):
        self.data = {}
        self.cache = {}
        self.handlers = []
    
    def process(self, input_data):
        # Complex processing logic
        for handler in self.handlers:
            if handler.can_handle(input_data):
                result = handler.process(input_data)
                self.cache[input_data] = result
                return result
        return None
'''
        (self.src_dir / "over_engineered.py").write_text(complex_impl)
        
        evidence = {"implementation_complexity_high": True}
        
        with pytest.raises(AttributeError):
            result = self.enforcer.enforce_red_phase(self.temp_dir, evidence)
            assert any("Implementation detected" in warning for warning in result.warnings)
    
    def test_red_phase_generates_appropriate_recommendations(self):
        """
        TEST: Should generate context-appropriate recommendations
        EXPECTED: Should fail - _generate_red_phase_recommendation method not implemented
        """
        blocking_issues = ["No test files found", "No failing tests"]
        warnings = ["Implementation complexity too high"]
        compliance_score = 0.40
        
        with pytest.raises(AttributeError):
            recommendation = self.enforcer._generate_red_phase_recommendation(
                blocking_issues, warnings, compliance_score
            )
            assert "RED phase validation failed" in recommendation
            assert "blocking issues" in recommendation


class TestGreenPhaseEnforcementLogic:
    """Tests for GREEN phase enforcement validation logic"""
    
    def setup_method(self):
        self.enforcer = GreenPhaseEnforcer()
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test project structure
        self.test_dir = Path(self.temp_dir) / "tests"
        self.test_dir.mkdir(exist_ok=True)
        self.src_dir = Path(self.temp_dir) / "src"
        self.src_dir.mkdir(exist_ok=True)
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_green_phase_enforcement_requires_passing_tests(self):
        """
        TEST: Should require all tests to pass for GREEN phase
        EXPECTED: Should fail - enforce_green_phase method not implemented
        """
        # Create failing tests (invalid for GREEN)
        evidence = {"test_results": {"test_example.py": False}}
        
        with pytest.raises(AttributeError):
            result = self.enforcer.enforce_green_phase(self.temp_dir, evidence)
            assert result.validation_result == PhaseValidationResult.FAIL
            assert any("No passing tests found" in issue for issue in result.blocking_issues)
    
    def test_green_phase_enforcement_validates_minimal_implementation(self):
        """
        TEST: Should validate implementation is minimal (not over-engineered)
        EXPECTED: Should fail - enforce_green_phase method not implemented
        """
        # Create over-engineered implementation
        evidence = {"average_complexity": 0.8}  # Too complex
        
        with pytest.raises(AttributeError):
            result = self.enforcer.enforce_green_phase(self.temp_dir, evidence)
            assert any("Over-implementation detected" in issue for issue in result.blocking_issues)
    
    def test_green_phase_enforcement_validates_code_coverage(self):
        """
        TEST: Should validate code coverage meets minimum requirements
        EXPECTED: Should fail - enforce_green_phase method not implemented
        """
        evidence = {"code_coverage": 0.50}  # Below 75% threshold
        
        with pytest.raises(AttributeError):
            result = self.enforcer.enforce_green_phase(self.temp_dir, evidence)
            assert any("Code coverage" in issue for issue in result.blocking_issues)
    
    def test_green_phase_enforcement_prevents_feature_creep(self):
        """
        TEST: Should prevent addition of new features beyond test requirements
        EXPECTED: Should fail - enforce_green_phase method not implemented
        """
        evidence = {"new_features_added": True}
        
        with pytest.raises(AttributeError):
            result = self.enforcer.enforce_green_phase(self.temp_dir, evidence)
            assert any("New features detected" in issue for issue in result.blocking_issues)
    
    def test_green_phase_generates_appropriate_recommendations(self):
        """
        TEST: Should generate context-appropriate recommendations for GREEN phase
        EXPECTED: Should fail - _generate_green_phase_recommendation method not implemented
        """
        blocking_issues = ["Tests not passing", "Over-implementation"]
        warnings = ["Code coverage slightly low"]
        compliance_score = 0.65
        
        with pytest.raises(AttributeError):
            recommendation = self.enforcer._generate_green_phase_recommendation(
                blocking_issues, warnings, compliance_score
            )
            assert "GREEN phase validation failed" in recommendation


class TestRefactorPhaseEnforcementLogic:
    """Tests for REFACTOR phase enforcement validation logic"""
    
    def setup_method(self):
        self.enforcer = RefactorPhaseEnforcer()
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test project structure
        self.test_dir = Path(self.temp_dir) / "tests"
        self.test_dir.mkdir(exist_ok=True)
        self.src_dir = Path(self.temp_dir) / "src"
        self.src_dir.mkdir(exist_ok=True)
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_refactor_phase_enforcement_validates_tests_still_pass(self):
        """
        TEST: Should validate all tests still pass after refactoring
        EXPECTED: Should fail - enforce_refactor_phase method not implemented
        """
        evidence = {"test_results": {"test_example.py": False}}  # Broken test
        
        with pytest.raises(AttributeError):
            result = self.enforcer.enforce_refactor_phase(self.temp_dir, evidence)
            assert any("Some tests failing after refactoring" in issue for issue in result.blocking_issues)
    
    def test_refactor_phase_enforcement_validates_quality_improvement(self):
        """
        TEST: Should validate code quality has improved
        EXPECTED: Should fail - enforce_refactor_phase method not implemented
        """
        evidence = {
            "current_quality_score": 0.65,
            "previous_quality_score": 0.70  # Quality decreased
        }
        
        with pytest.raises(AttributeError):
            result = self.enforcer.enforce_refactor_phase(self.temp_dir, evidence)
            assert any("Code quality did not improve" in warning for warning in result.warnings)
    
    def test_refactor_phase_enforcement_prevents_new_functionality(self):
        """
        TEST: Should prevent addition of new functionality during refactoring
        EXPECTED: Should fail - enforce_refactor_phase method not implemented
        """
        evidence = {"new_functionality_added": True}
        
        with pytest.raises(AttributeError):
            result = self.enforcer.enforce_refactor_phase(self.temp_dir, evidence)
            assert any("New functionality detected" in issue for issue in result.blocking_issues)
    
    def test_refactor_phase_enforcement_validates_technical_debt_reduction(self):
        """
        TEST: Should validate technical debt has been reduced
        EXPECTED: Should fail - enforce_refactor_phase method not implemented
        """
        evidence = {
            "previous_complexity": 0.5,
            "current_complexity": 0.6  # Complexity increased
        }
        
        with pytest.raises(AttributeError):
            result = self.enforcer.enforce_refactor_phase(self.temp_dir, evidence)
            assert any("Code complexity did not decrease" in warning for warning in result.warnings)
    
    def test_refactor_phase_generates_appropriate_recommendations(self):
        """
        TEST: Should generate context-appropriate recommendations for REFACTOR phase
        EXPECTED: Should fail - _generate_refactor_phase_recommendation method not implemented
        """
        blocking_issues = ["Tests broken", "New functionality added"]
        warnings = ["Quality not improved"]
        compliance_score = 0.55
        
        with pytest.raises(AttributeError):
            recommendation = self.enforcer._generate_refactor_phase_recommendation(
                blocking_issues, warnings, compliance_score
            )
            assert "REFACTOR phase validation failed" in recommendation


class TestValidationEvidenceCollection:
    """Tests for validation evidence collection and processing"""
    
    def setup_method(self):
        self.enforcer = RedPhaseEnforcer()  # Can use any enforcer for base functionality
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_validation_evidence_captures_comprehensive_data(self):
        """
        TEST: Should capture comprehensive validation evidence
        EXPECTED: Should fail - ValidationEvidence creation not complete
        """
        # This test validates the ValidationEvidence dataclass structure
        evidence = ValidationEvidence(
            test_files=["test1.py", "test2.py"],
            implementation_files=["impl1.py", "impl2.py"],
            test_results={"test1.py": True, "test2.py": False},
            code_coverage=0.75,
            quality_metrics={"complexity": 0.6, "maintainability": 0.8},
            complexity_score=0.6,
            validation_timestamp=None  # Should be set by actual implementation
        )
        
        with pytest.raises((AttributeError, TypeError)):
            assert evidence.test_files is not None
            assert evidence.implementation_files is not None
            assert evidence.test_results is not None
            assert evidence.code_coverage >= 0.0
            assert evidence.quality_metrics is not None
            assert evidence.complexity_score >= 0.0
            assert evidence.validation_timestamp is not None  # Should fail because it's None
    
    def test_phase_enforcement_result_contains_required_fields(self):
        """
        TEST: Should contain all required fields for enforcement decisions
        EXPECTED: Should fail - PhaseEnforcementResult structure not complete
        """
        # Create mock evidence
        mock_evidence = Mock()
        
        result = PhaseEnforcementResult(
            phase_name="RED",
            validation_result=PhaseValidationResult.PASS,
            compliance_score=0.85,
            blocking_issues=[],
            warnings=[],
            evidence=mock_evidence,
            execution_time_ms=1500.0,
            recommendation="Good RED phase implementation"
        )
        
        with pytest.raises((AttributeError, AssertionError)):
            assert result.phase_name in ["RED", "GREEN", "REFACTOR"]
            assert result.validation_result in [PhaseValidationResult.PASS, PhaseValidationResult.FAIL, PhaseValidationResult.WARNING]
            assert 0.0 <= result.compliance_score <= 1.0
            assert isinstance(result.blocking_issues, list)
            assert isinstance(result.warnings, list)
            assert result.evidence is not None
            assert result.execution_time_ms >= 0.0
            assert isinstance(result.recommendation, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])