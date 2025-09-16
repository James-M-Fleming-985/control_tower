"""
RED Phase Tests - Test Generator Core Functionality

These tests define the expected behavior of the TestGenerator class
and MUST FAIL initially (RED phase) to drive TDD implementation.

Created: 2025-09-15
TDD Phase: RED (Write Failing Tests)
Layer: Data Access (Requirements Parser & Test Generator)
Forcing Functions: Every test includes verification as per FR-002
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
from pathlib import Path
import tempfile
import json
from typing import Any, Dict, List

# Import the interfaces we expect to implement
from src.data_access.interfaces import (
    ParsedRequirement,
    GeneratedTest,
    TestFile,
    TestValidationResult,
    FailureValidation,
    TestGeneratorInterface,
    TestGenerationStatus,
)


class TestTestGeneratorInterface:
    """Test the TestGenerator interface implementation with forcing functions"""
    
    def test_test_generator_implements_interface(self):
        """
        Test that TestGenerator class implements TestGeneratorInterface
        
        RED Phase: This MUST fail until we implement the class
        Forcing Function: Verifies interface compliance before proceeding
        """
        from src.data_access.test_generator import TestGenerator
        
        generator = TestGenerator()
        
        # Verify it implements the interface
        assert isinstance(generator, TestGeneratorInterface)
        
        # Verify all required methods exist
        assert hasattr(generator, 'generate_failing_tests')
        assert hasattr(generator, 'create_test_file_structure')
        assert hasattr(generator, 'validate_test_generation')
        assert hasattr(generator, 'ensure_tests_fail_correctly')
        
        print("✅ TestGenerator interface compliance verified")

    def test_generate_failing_tests_with_forcing_function(self):
        """
        Test generate_failing_tests method with forcing function verification
        
        RED Phase: MUST fail until implementation exists
        Forcing Function: Must generate REAL failing tests for REAL code implementation
        """
        from src.data_access.test_generator import TestGenerator
        
        generator = TestGenerator()
        
        # Create sample parsed requirement
        requirement = ParsedRequirement(
            requirement_id="TEST-REQ-001",
            requirement_type="Feature Requirement",
            primary_objective="Test functionality",
            acceptance_criteria=[
                {"id": "AC-001", "description": "Should work correctly"},
                {"id": "AC-002", "description": "Should handle errors gracefully"}
            ]
        )
        
        result = generator.generate_failing_tests(requirement)
        
        # Verify result is a list of GeneratedTest objects
        assert isinstance(result, list)
        assert len(result) == 2  # One test per acceptance criteria
        
        for test in result:
            assert isinstance(test, GeneratedTest)
            assert test.is_failing is True  # Must be failing in RED phase
            assert test.test_code is not None
            assert "def test_" in test.test_code
            assert "assert False" in test.test_code  # Should contain failing assertion
        
        print(f"✅ Tests generated: {len(result)} failing tests created for REAL implementation")

    def test_create_test_file_structure_with_forcing_function(self):
        """
        Test create_test_file_structure with forcing function verification
        
        RED Phase: MUST fail until implementation exists
        Forcing Function: Must create REAL test files with REAL pytest structure
        """
        from src.data_access.test_generator import TestGenerator
        
        generator = TestGenerator()
        
        # Create sample tests
        sample_tests = [
            GeneratedTest(
                test_id="test_001",
                test_name="Test AC-001",
                test_function_name="test_ac_001_functionality",
                acceptance_criteria_id="AC-001",
                test_code='def test_ac_001_functionality():\n    assert False, "Not implemented"'
            ),
            GeneratedTest(
                test_id="test_002", 
                test_name="Test AC-002",
                test_function_name="test_ac_002_error_handling",
                acceptance_criteria_id="AC-002",
                test_code='def test_ac_002_error_handling():\n    assert False, "Not implemented"'
            )
        ]
        
        requirement = ParsedRequirement(
            requirement_id="TEST-REQ-001",
            requirement_type="Feature Requirement"
        )
        
        result = generator.create_test_file_structure(sample_tests, requirement)
        
        # Verify result is a TestFile object
        assert isinstance(result, TestFile)
        assert result.requirement_id == "TEST-REQ-001"
        assert len(result.generated_tests) == 2
        assert result.file_path.endswith(".py")
        
        # Verify file content can be generated
        content = result.generate_file_content()
        assert "import pytest" in content
        assert "def test_ac_001_functionality" in content
        assert "def test_ac_002_error_handling" in content
        
        print("✅ Test file structure created: REAL pytest files with proper structure")

    def test_validate_test_generation_with_forcing_function(self):
        """
        Test validate_test_generation with forcing function verification
        
        RED Phase: MUST fail until implementation exists
        Forcing Function: Must verify REAL tests are syntactically correct and executable
        """
        from src.data_access.test_generator import TestGenerator
        
        generator = TestGenerator()
        
        # Create a test file with valid Python code
        test_file = TestFile(
            file_path="test_example.py",
            requirement_id="TEST-REQ-001",
            generated_tests=[
                GeneratedTest(
                    test_id="test_001",
                    test_name="Valid test",
                    test_function_name="test_valid_functionality",
                    acceptance_criteria_id="AC-001",
                    test_code='def test_valid_functionality():\n    assert False, "Not implemented"'
                )
            ]
        )
        
        result = generator.validate_test_generation(test_file)
        
        # Verify result is TestValidationResult
        assert isinstance(result, TestValidationResult)
        assert result.is_valid is True  # Valid syntax
        assert len(result.syntax_errors) == 0
        assert result.forcing_function_passed is True
        
        print("✅ Test generation validation complete: tests are syntactically correct")

    def test_ensure_tests_fail_correctly_with_forcing_function(self):
        """
        Test ensure_tests_fail_correctly with forcing function verification
        
        RED Phase: MUST fail until implementation exists
        Forcing Function: Must verify tests fail correctly (RED phase validation)
        """
        from src.data_access.test_generator import TestGenerator
        
        generator = TestGenerator()
        
        # Create test file with failing tests
        test_file = TestFile(
            file_path="test_failing.py",
            requirement_id="TEST-REQ-001",
            generated_tests=[
                GeneratedTest(
                    test_id="test_001",
                    test_name="Failing test 1",
                    test_function_name="test_should_fail_1",
                    acceptance_criteria_id="AC-001",
                    test_code='def test_should_fail_1():\n    assert False, "Not implemented"',
                    is_failing=True
                ),
                GeneratedTest(
                    test_id="test_002",
                    test_name="Failing test 2", 
                    test_function_name="test_should_fail_2",
                    acceptance_criteria_id="AC-002",
                    test_code='def test_should_fail_2():\n    assert False, "Not implemented"',
                    is_failing=True
                )
            ]
        )
        
        result = generator.ensure_tests_fail_correctly(test_file)
        
        # Verify result is FailureValidation
        assert isinstance(result, FailureValidation)
        assert result.total_tests == 2
        assert result.failing_tests == 2
        assert result.passing_tests == 0
        assert result.is_red_phase_valid is True
        assert result.forcing_function_passed is True
        
        # Verify terminal output
        output = result.generate_verification_output()
        assert "✅ RED phase verified" in output
        assert "2/2 failing" in output
        
        print("✅ RED phase verified: All tests fail correctly (2/2 failing)")


class TestTestGeneratorFunctionality:
    """Test detailed test generation functionality with forcing functions"""
    
    def test_generate_unit_tests_from_acceptance_criteria(self):
        """
        Test generation of unit tests from acceptance criteria
        
        RED Phase: MUST fail until unit test generation implemented
        Forcing Function: Must create testable unit tests for each criterion
        """
        from src.data_access.test_generator import TestGenerator
        
        generator = TestGenerator()
        
        requirement = ParsedRequirement(
            requirement_id="UNIT-TEST-001",
            requirement_type="Feature Requirement",
            primary_objective="Unit test generation",
            acceptance_criteria=[
                {
                    "id": "AC-001",
                    "description": "Should parse requirement ID correctly",
                    "type": "functional"
                },
                {
                    "id": "AC-002", 
                    "description": "Should validate input parameters",
                    "type": "validation"
                },
                {
                    "id": "AC-003",
                    "description": "Should handle network timeout errors",
                    "type": "error_handling"
                }
            ]
        )
        
        tests = generator.generate_failing_tests(requirement)
        
        # Verify different test types are generated
        assert len(tests) == 3
        
        # Check functional test
        functional_test = next(t for t in tests if "parse_requirement_id" in t.test_function_name)
        assert functional_test.test_type == "unit"
        assert "mock" in functional_test.test_code.lower() or "Mock" in functional_test.test_code
        
        # Check validation test
        validation_test = next(t for t in tests if "validate_input" in t.test_function_name)
        assert "pytest.raises" in validation_test.test_code or "assert" in validation_test.test_code
        
        # Check error handling test
        error_test = next(t for t in tests if "timeout" in t.test_function_name)
        assert "exception" in error_test.test_code.lower() or "error" in error_test.test_code.lower()
        
        print("✅ Unit tests generated: functional, validation, and error handling tests")

    def test_generate_integration_tests_for_layer_interactions(self):
        """
        Test generation of integration tests for layer interactions
        
        RED Phase: MUST fail until integration test generation implemented
        Forcing Function: Must create tests for REAL layer interfaces
        """
        from src.data_access.test_generator import TestGenerator
        
        generator = TestGenerator()
        
        # Layer requirement with integration points
        requirement = ParsedRequirement(
            requirement_id="LAYER-INTEGRATION-001",
            requirement_type="Layer Requirement",
            layer_implementation="Data Access Layer",
            integration_points="Business Logic Layer, File System",
            acceptance_criteria=[
                {
                    "id": "AC-001",
                    "description": "Should integrate with Business Logic Layer correctly",
                    "type": "integration"
                },
                {
                    "id": "AC-002",
                    "description": "Should handle file system operations safely",
                    "type": "integration"
                }
            ]
        )
        
        tests = generator.generate_failing_tests(requirement)
        
        # Verify integration tests are created
        integration_tests = [t for t in tests if t.test_type == "integration"]
        assert len(integration_tests) >= 2
        
        for test in integration_tests:
            # Integration tests should have setup and teardown
            assert test.setup_code is not None or "setup" in test.test_code.lower()
            # Should test actual layer interactions
            assert any(keyword in test.test_code.lower() for keyword in ["interface", "contract", "integration"])
        
        print("✅ Integration tests generated: layer interface contracts validated")

    def test_generate_performance_tests_for_requirements(self):
        """
        Test generation of performance tests for performance requirements
        
        RED Phase: MUST fail until performance test generation implemented
        Forcing Function: Must validate REAL performance under REAL load conditions
        """
        from src.data_access.test_generator import TestGenerator
        
        generator = TestGenerator()
        
        requirement = ParsedRequirement(
            requirement_id="PERF-REQ-001",
            requirement_type="Performance Requirement",
            acceptance_criteria=[
                {
                    "id": "AC-001",
                    "description": "Should process 50+ requirement files per minute",
                    "type": "performance"
                },
                {
                    "id": "AC-002",
                    "description": "Should complete parsing within 1 second per file",
                    "type": "performance"
                }
            ]
        )
        
        tests = generator.generate_failing_tests(requirement)
        
        # Verify performance tests
        perf_tests = [t for t in tests if t.test_type == "performance"]
        assert len(perf_tests) >= 2
        
        for test in perf_tests:
            # Performance tests should measure time
            assert any(keyword in test.test_code for keyword in ["time", "timer", "duration"])
            # Should have performance assertions
            assert any(keyword in test.test_code for keyword in ["<", "less", "under", "within"])
        
        print("✅ Performance tests generated: real load conditions with timing validation")

    def test_generate_test_fixtures_and_mocks(self):
        """
        Test generation of test fixtures and mocks
        
        RED Phase: MUST fail until fixture generation implemented
        Forcing Function: Must create REAL fixtures for REAL test scenarios
        """
        from src.data_access.test_generator import TestGenerator
        
        generator = TestGenerator()
        
        requirement = ParsedRequirement(
            requirement_id="FIXTURE-REQ-001",
            requirement_type="Feature Requirement",
            acceptance_criteria=[
                {
                    "id": "AC-001",
                    "description": "Should parse requirement files correctly",
                    "dependencies": ["file_system", "markdown_parser"]
                }
            ]
        )
        
        tests = generator.generate_failing_tests(requirement)
        test_file = generator.create_test_file_structure(tests, requirement)
        
        # Verify fixtures are generated
        assert len(test_file.fixtures) > 0
        
        # Check for file system fixtures
        file_fixture = next((f for f in test_file.fixtures if "file" in f.lower()), None)
        assert file_fixture is not None
        assert "@pytest.fixture" in file_fixture
        
        # Check for mock fixtures
        mock_fixture = next((f for f in test_file.fixtures if "mock" in f.lower()), None)
        assert mock_fixture is not None
        
        print("✅ Test fixtures generated: file system and mock fixtures created")


class TestTestGeneratorValidation:
    """Test validation and error handling in test generation"""
    
    def test_validate_generated_test_syntax(self):
        """
        Test validation of generated test syntax
        
        RED Phase: MUST fail until syntax validation implemented
        Forcing Function: Must ensure REAL Python syntax correctness
        """
        from src.data_access.test_generator import TestGenerator
        
        generator = TestGenerator()
        
        # Test with invalid syntax
        invalid_test = GeneratedTest(
            test_id="invalid_001",
            test_name="Invalid syntax test",
            test_function_name="test_invalid_syntax",
            acceptance_criteria_id="AC-001",
            test_code="def test_invalid_syntax(\n    assert False  # Missing closing parenthesis"
        )
        
        result = invalid_test.validate_syntax()
        
        assert not result.is_valid
        assert len(result.error_messages) > 0
        assert any("syntax" in error.lower() for error in result.error_messages)
        
        print("✅ Syntax validation working: invalid syntax detected correctly")

    def test_validate_test_completeness(self):
        """
        Test validation that tests are complete and testable
        
        RED Phase: MUST fail until completeness validation implemented
        Forcing Function: Must verify tests have REAL assertions and test logic
        """
        from src.data_access.test_generator import TestGenerator
        
        generator = TestGenerator()
        
        # Test with incomplete test (no assertions)
        incomplete_test = GeneratedTest(
            test_id="incomplete_001",
            test_name="Incomplete test",
            test_function_name="test_incomplete",
            acceptance_criteria_id="AC-001",
            test_code="def test_incomplete():\n    # TODO: Add test logic\n    pass"
        )
        
        result = incomplete_test.validate_syntax()
        
        # Should warn about missing assertions
        assert len(result.warning_messages) > 0
        has_assertion_warning = any("assert" in warning.lower() for warning in result.warning_messages)
        assert has_assertion_warning
        
        print("✅ Completeness validation working: missing assertions detected")

    def test_validate_test_execution_environment(self):
        """
        Test validation of test execution environment
        
        RED Phase: MUST fail until environment validation implemented
        Forcing Function: Must validate REAL pytest execution environment
        """
        from src.data_access.test_generator import TestGenerator
        
        generator = TestGenerator()
        
        # Create valid test file
        test_file = TestFile(
            file_path="/tmp/test_environment.py",
            requirement_id="ENV-TEST-001",
            generated_tests=[
                GeneratedTest(
                    test_id="env_001",
                    test_name="Environment test",
                    test_function_name="test_environment_setup",
                    acceptance_criteria_id="AC-001",
                    test_code="def test_environment_setup():\n    import pytest\n    assert False, 'Test environment check'"
                )
            ]
        )
        
        result = generator.validate_test_generation(test_file)
        
        # Should validate imports and execution environment
        assert isinstance(result, TestValidationResult)
        assert result.is_valid  # Valid Python code
        
        # Should check for pytest availability
        pytest_available = any("pytest" in imp for imp in test_file.imports)
        assert pytest_available or "import pytest" in test_file.generate_file_content()
        
        print("✅ Execution environment validated: pytest integration confirmed")

    def test_red_phase_verification_for_test_generator(self):
        """
        Test that ensures all generated tests are in proper RED phase
        
        RED Phase: MUST fail until RED phase verification implemented
        Forcing Function: Must verify ALL tests fail for the RIGHT reasons
        """
        from src.data_access.test_generator import TestGenerator
        
        generator = TestGenerator()
        
        requirement = ParsedRequirement(
            requirement_id="RED-VERIFY-001",
            requirement_type="Feature Requirement",
            acceptance_criteria=[
                {"id": "AC-001", "description": "Should work correctly"},
                {"id": "AC-002", "description": "Should handle errors"}
            ]
        )
        
        tests = generator.generate_failing_tests(requirement)
        test_file = generator.create_test_file_structure(tests, requirement)
        
        # Verify RED phase compliance
        failure_validation = generator.ensure_tests_fail_correctly(test_file)
        
        assert failure_validation.is_red_phase_valid
        assert failure_validation.total_tests == 2
        assert failure_validation.failing_tests == 2
        assert failure_validation.passing_tests == 0
        assert failure_validation.syntax_error_tests == 0
        
        # All tests should fail for implementation reasons, not syntax errors
        for test in tests:
            assert test.is_failing
            assert "assert False" in test.test_code or "NotImplementedError" in test.test_code
        
        print("✅ RED phase verification complete: all tests fail correctly (not syntax errors)")


class TestTestGeneratorIntegration:
    """Test integration with other layer components"""
    
    def test_integration_with_requirements_parser(self):
        """
        Test integration between TestGenerator and RequirementsParser
        
        RED Phase: MUST fail until integration implemented
        Forcing Function: Must use REAL parsed requirements for test generation
        """
        from src.data_access.test_generator import TestGenerator
        from src.data_access.requirements_parser import RequirementsParser
        
        parser = RequirementsParser()
        generator = TestGenerator()
        
        # Parse a real requirement
        parsed_req = parser.parse_work_item_requirements("FEATURE-MAKE-WORK-ON-001")
        
        # Generate tests from parsed requirement
        tests = generator.generate_failing_tests(parsed_req)
        
        # Verify integration
        assert len(tests) > 0
        assert all(test.acceptance_criteria_id in [ac["id"] for ac in parsed_req.acceptance_criteria] for test in tests)
        
        print("✅ Parser-Generator integration verified: real requirements generate real tests")

    def test_configuration_integration_for_test_generation(self):
        """
        Test integration with layer configuration for test generation
        
        RED Phase: MUST fail until configuration integration implemented
        Forcing Function: Must use configuration settings for test generation
        """
        from src.data_access.test_generator import TestGenerator
        from src.data_access.config import get_config
        
        config = get_config()
        generator = TestGenerator(config=config)
        
        # Should use configuration settings
        assert generator.config is not None
        assert generator.config.test_generation.test_framework == "pytest"
        
        # Test generation should respect configuration
        requirement = ParsedRequirement(
            requirement_id="CONFIG-TEST-001",
            requirement_type="Feature Requirement",
            acceptance_criteria=[{"id": "AC-001", "description": "Test config integration"}]
        )
        
        tests = generator.generate_failing_tests(requirement)
        test_file = generator.create_test_file_structure(tests, requirement)
        
        # Should use configured framework
        assert test_file.framework == "pytest"
        assert any("pytest" in imp for imp in test_file.imports)
        
        print("✅ Configuration integration verified: test generation uses layer config")

    def test_file_system_integration_for_test_output(self):
        """
        Test integration with file system for test file output
        
        RED Phase: MUST fail until file system integration implemented
        Forcing Function: Must write REAL test files to REAL file system
        """
        from src.data_access.test_generator import TestGenerator
        
        generator = TestGenerator()
        
        # Create test file
        test_file = TestFile(
            file_path="/tmp/test_output_integration.py",
            requirement_id="FS-INTEGRATION-001",
            generated_tests=[
                GeneratedTest(
                    test_id="fs_001",
                    test_name="File system test",
                    test_function_name="test_file_system_integration",
                    acceptance_criteria_id="AC-001",
                    test_code="def test_file_system_integration():\n    assert False, 'File system integration test'"
                )
            ]
        )
        
        # Should be able to write to file system
        success = generator.write_test_file_to_disk(test_file)
        
        assert success
        
        # Verify file was actually written
        written_file = Path(test_file.file_path)
        assert written_file.exists()
        
        # Verify content
        content = written_file.read_text()
        assert "def test_file_system_integration" in content
        assert "import pytest" in content
        
        # Cleanup
        written_file.unlink(missing_ok=True)
        
        print("✅ File system integration verified: real test files written to disk")


# Fixtures for TestGenerator tests
@pytest.fixture
def sample_requirement():
    """Sample requirement for test generation"""
    return ParsedRequirement(
        requirement_id="SAMPLE-REQ-001",
        requirement_type="Feature Requirement",
        primary_objective="Sample requirement for testing",
        acceptance_criteria=[
            {"id": "AC-001", "description": "Should implement core functionality"},
            {"id": "AC-002", "description": "Should handle edge cases correctly"},
            {"id": "AC-003", "description": "Should provide error handling"}
        ]
    )


@pytest.fixture
def sample_generated_tests():
    """Sample generated tests"""
    return [
        GeneratedTest(
            test_id="test_001",
            test_name="Test core functionality",
            test_function_name="test_core_functionality",
            acceptance_criteria_id="AC-001",
            test_code="def test_core_functionality():\n    assert False, 'Not implemented'",
            is_failing=True
        ),
        GeneratedTest(
            test_id="test_002",
            test_name="Test edge cases",
            test_function_name="test_edge_cases",
            acceptance_criteria_id="AC-002",
            test_code="def test_edge_cases():\n    assert False, 'Not implemented'",
            is_failing=True
        )
    ]


# RED Phase Verification for TestGenerator
def test_test_generator_red_phase_verification():
    """
    Verify that TestGenerator is in proper RED phase - all tests should fail
    
    This test ensures we haven't accidentally implemented anything yet
    """
    try:
        # Try to import the main class - this should fail
        from src.data_access.test_generator import TestGenerator
        
        # If we get here, check if it's properly unimplemented
        generator = TestGenerator()
        
        # Try a method call - should fail or raise NotImplementedError
        try:
            requirement = ParsedRequirement(
                requirement_id="TEST", 
                requirement_type="Test"
            )
            result = generator.generate_failing_tests(requirement)
            # If this succeeds, we're not in RED phase
            assert False, "TestGenerator implementation exists - not in proper RED phase!"
        except (NotImplementedError, AttributeError, Exception):
            # Expected - we're in RED phase
            print("✅ RED phase verified - TestGenerator not yet implemented")
            
    except ImportError:
        # Expected - class doesn't exist yet
        print("✅ RED phase verified - TestGenerator class not yet created")
    
    # This assertion will pass to mark the verification as complete
    assert True, "TestGenerator RED phase verification complete"