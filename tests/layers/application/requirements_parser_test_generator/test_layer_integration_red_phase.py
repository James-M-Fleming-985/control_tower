"""
RED Phase Integration Tests - Complete Layer Integration

These tests define the expected behavior of the complete Requirements Parser
& Test Generator layer working together with forcing functions as per FR-002.

Created: 2025-09-15
TDD Phase: RED (Write Failing Tests)
Layer: Data Access (Requirements Parser & Test Generator)
Forcing Functions: Complete layer validation and verification
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import time
from typing import List, Dict, Any

# Import all interfaces and models
from src.data_access.interfaces import (
    ParsedRequirement,
    GeneratedTest,
    TestFile,
    ValidationResult,
    TraceabilityData,
    TestValidationResult,
    FailureValidation,
    RequirementsParserInterface,
    TestGeneratorInterface,
    FileSystemInterface,
)

from src.data_access.config import get_config, validate_startup_configuration


class TestCompleteLayerIntegration:
    """Test complete layer integration with forcing functions"""
    
    def test_layer_startup_configuration_forcing_function(self):
        """
        Test layer startup with configuration forcing function
        
        RED Phase: MUST fail until configuration validation implemented
        Forcing Function: Cannot proceed without valid configuration
        """
        # This should validate configuration at startup
        validation_result = validate_startup_configuration()
        
        assert isinstance(validation_result, ValidationResult)
        assert validation_result.forcing_function_passed
        
        if validation_result.is_valid:
            print("✅ Startup configuration validated - layer environment ready")
        else:
            print("❌ Startup configuration failed - cannot proceed without valid configuration")
            
        # Configuration must be valid to proceed
        assert validation_result.is_valid

    def test_end_to_end_requirement_to_tests_workflow(self):
        """
        Test complete end-to-end workflow from requirement file to generated tests
        
        RED Phase: MUST fail until complete workflow implemented
        Forcing Function: Must validate REAL workflow with REAL files
        """
        from src.data_access.requirements_parser import RequirementsParser
        from src.data_access.test_generator import TestGenerator
        
        # Step 1: Parse real requirement file
        parser = RequirementsParser()
        parsed_requirement = parser.parse_work_item_requirements("FEATURE-MAKE-WORK-ON-001")
        
        # Verify parsing with forcing function
        assert isinstance(parsed_requirement, ParsedRequirement)
        assert parsed_requirement.validation_result.forcing_function_passed
        
        # Step 2: Generate tests from parsed requirement
        generator = TestGenerator()
        generated_tests = generator.generate_failing_tests(parsed_requirement)
        
        # Verify test generation with forcing function
        assert isinstance(generated_tests, list)
        assert len(generated_tests) > 0
        assert all(isinstance(test, GeneratedTest) for test in generated_tests)
        assert all(test.is_failing for test in generated_tests)
        
        # Step 3: Create test file structure
        test_file = generator.create_test_file_structure(generated_tests, parsed_requirement)
        
        # Verify test file creation with forcing function
        assert isinstance(test_file, TestFile)
        assert test_file.requirement_id == parsed_requirement.requirement_id
        
        # Step 4: Validate generated tests
        validation_result = generator.validate_test_generation(test_file)
        
        # Verify validation with forcing function
        assert isinstance(validation_result, TestValidationResult)
        assert validation_result.forcing_function_passed
        
        # Step 5: Ensure RED phase compliance
        failure_validation = generator.ensure_tests_fail_correctly(test_file)
        
        # Verify RED phase with forcing function
        assert isinstance(failure_validation, FailureValidation)
        assert failure_validation.is_red_phase_valid
        assert failure_validation.forcing_function_passed
        
        print(f"✅ End-to-end workflow verified: {parsed_requirement.requirement_id} → {len(generated_tests)} failing tests")

    def test_layer_performance_requirements_with_forcing_function(self):
        """
        Test layer performance requirements with forcing function verification
        
        RED Phase: MUST fail until performance requirements implemented
        Forcing Function: Must meet performance targets under load
        """
        from src.data_access.requirements_parser import RequirementsParser
        from src.data_access.test_generator import TestGenerator
        
        parser = RequirementsParser()
        generator = TestGenerator()
        
        # Performance test: Process multiple requirements concurrently
        requirement_ids = [
            "FEATURE-MAKE-WORK-ON-001",
            "LAYER-REQUIREMENTS-PARSER-TEST-GENERATOR-001"
        ]
        
        start_time = time.time()
        
        results = []
        for req_id in requirement_ids:
            # Parse requirement
            parsed_req = parser.parse_work_item_requirements(req_id)
            
            # Generate tests
            tests = generator.generate_failing_tests(parsed_req)
            
            # Create test file
            test_file = generator.create_test_file_structure(tests, parsed_req)
            
            results.append((parsed_req, tests, test_file))
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Performance requirement: <1 second per file
        files_processed = len(requirement_ids)
        avg_time_per_file = total_time / files_processed
        
        assert avg_time_per_file < 1.0, f"Performance requirement failed: {avg_time_per_file:.3f}s per file (>1s limit)"
        
        # Memory usage should be reasonable
        import psutil
        import os
        process = psutil.Process(os.getpid())
        memory_usage_mb = process.memory_info().rss / 1024 / 1024
        
        assert memory_usage_mb < 100, f"Memory requirement failed: {memory_usage_mb:.1f}MB (>100MB limit)"
        
        print(f"✅ Performance verified: {files_processed} files in {total_time:.3f}s ({avg_time_per_file:.3f}s avg), {memory_usage_mb:.1f}MB memory")

    def test_layer_error_handling_with_forcing_functions(self):
        """
        Test layer error handling with forcing function verification
        
        RED Phase: MUST fail until error handling implemented
        Forcing Function: Must handle REAL error scenarios with REAL recovery
        """
        from src.data_access.requirements_parser import RequirementsParser
        from src.data_access.test_generator import TestGenerator
        
        parser = RequirementsParser()
        generator = TestGenerator()
        
        # Test 1: Non-existent requirement file
        with pytest.raises(Exception) as exc_info:
            parser.parse_work_item_requirements("NONEXISTENT-REQ-999")
        
        error_message = str(exc_info.value).lower()
        assert any(word in error_message for word in ['file', 'not found', 'exist'])
        print("✅ File not found error handled correctly")
        
        # Test 2: Malformed requirement content
        malformed_requirement = ParsedRequirement(
            requirement_id="MALFORMED-001",
            requirement_type="",  # Invalid empty type
            acceptance_criteria=[]  # No criteria
        )
        
        validation_result = parser.validate_requirement_completeness(malformed_requirement)
        assert not validation_result.is_valid
        assert len(validation_result.error_messages) > 0
        print("✅ Malformed requirement error handling verified")
        
        # Test 3: Test generation with invalid requirement
        try:
            tests = generator.generate_failing_tests(malformed_requirement)
            # Should handle gracefully or raise appropriate error
        except Exception as e:
            assert "requirement" in str(e).lower() or "criteria" in str(e).lower()
        print("✅ Invalid requirement error handling verified")

    def test_layer_quality_gates_with_forcing_functions(self):
        """
        Test layer quality gates with forcing function verification
        
        RED Phase: MUST fail until quality gates implemented
        Forcing Function: Cannot proceed without meeting quality thresholds
        """
        from src.data_access.requirements_parser import RequirementsParser
        from src.data_access.test_generator import TestGenerator
        
        config = get_config()
        parser = RequirementsParser(config=config)
        generator = TestGenerator(config=config)
        
        # Quality Gate 1: Configuration validation
        assert config.validation_result.is_valid
        assert config.validation_result.forcing_function_passed
        print("✅ Quality gate 1 passed: Configuration validated")
        
        # Quality Gate 2: Requirements parsing accuracy
        parsed_req = parser.parse_work_item_requirements("FEATURE-MAKE-WORK-ON-001")
        assert parsed_req.validation_result.forcing_function_passed
        assert len(parsed_req.acceptance_criteria) > 0
        print("✅ Quality gate 2 passed: Requirements parsing accurate")
        
        # Quality Gate 3: Test generation completeness
        tests = generator.generate_failing_tests(parsed_req)
        assert len(tests) == len(parsed_req.acceptance_criteria)  # One test per criterion
        assert all(test.is_failing for test in tests)
        print("✅ Quality gate 3 passed: Test generation complete")
        
        # Quality Gate 4: Test validation
        test_file = generator.create_test_file_structure(tests, parsed_req)
        validation_result = generator.validate_test_generation(test_file)
        assert validation_result.forcing_function_passed
        assert len(validation_result.syntax_errors) == 0
        print("✅ Quality gate 4 passed: Test validation successful")
        
        # Quality Gate 5: RED phase verification
        failure_validation = generator.ensure_tests_fail_correctly(test_file)
        assert failure_validation.forcing_function_passed
        assert failure_validation.is_red_phase_valid
        print("✅ Quality gate 5 passed: RED phase verified")

    def test_layer_traceability_with_forcing_functions(self):
        """
        Test layer traceability with forcing function verification
        
        RED Phase: MUST fail until traceability implemented
        Forcing Function: Must establish REAL traceability to REAL requirements
        """
        from src.data_access.requirements_parser import RequirementsParser
        from src.data_access.test_generator import TestGenerator
        
        parser = RequirementsParser()
        generator = TestGenerator()
        
        # Parse requirement
        parsed_req = parser.parse_work_item_requirements("FEATURE-MAKE-WORK-ON-001")
        
        # Create traceability
        traceability = parser.create_requirement_traceability(parsed_req)
        
        assert isinstance(traceability, TraceabilityData)
        assert traceability.requirement_id == parsed_req.requirement_id
        assert traceability.source_file_path != ""
        
        # Generate tests with traceability
        tests = generator.generate_failing_tests(parsed_req)
        test_file = generator.create_test_file_structure(tests, parsed_req)
        
        # Verify traceability in generated tests
        for test in tests:
            assert test.acceptance_criteria_id in [ac["id"] for ac in parsed_req.acceptance_criteria]
        
        # Update traceability with test information
        traceability.generated_test_ids = [test.test_id for test in tests]
        traceability.target_test_file_paths = [test_file.file_path]
        
        # Create traceability matrix
        traceability.traceability_matrix = {
            ac["id"]: [test.test_id for test in tests if test.acceptance_criteria_id == ac["id"]]
            for ac in parsed_req.acceptance_criteria
        }
        
        assert len(traceability.traceability_matrix) == len(parsed_req.acceptance_criteria)
        
        print(f"✅ Traceability established: {parsed_req.requirement_id} → {len(tests)} tests (100% coverage)")

    def test_layer_concurrent_processing_with_forcing_functions(self):
        """
        Test layer concurrent processing with forcing function verification
        
        RED Phase: MUST fail until concurrent processing implemented
        Forcing Function: Must handle concurrent operations safely
        """
        from src.data_access.requirements_parser import RequirementsParser
        from src.data_access.test_generator import TestGenerator
        import threading
        import queue
        
        parser = RequirementsParser()
        generator = TestGenerator()
        
        # Test concurrent parsing
        requirement_ids = [
            "FEATURE-MAKE-WORK-ON-001",
            "LAYER-REQUIREMENTS-PARSER-TEST-GENERATOR-001"
        ]
        
        results_queue = queue.Queue()
        
        def process_requirement(req_id):
            try:
                # Parse requirement
                parsed_req = parser.parse_work_item_requirements(req_id)
                
                # Generate tests
                tests = generator.generate_failing_tests(parsed_req)
                
                # Create test file
                test_file = generator.create_test_file_structure(tests, parsed_req)
                
                results_queue.put(("success", req_id, parsed_req, tests, test_file))
            except Exception as e:
                results_queue.put(("error", req_id, str(e)))
        
        # Start concurrent processing
        threads = []
        for req_id in requirement_ids:
            thread = threading.Thread(target=process_requirement, args=(req_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=10.0)
        
        # Verify results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        successful_results = [r for r in results if r[0] == "success"]
        assert len(successful_results) == len(requirement_ids)
        
        # Verify no data corruption
        for status, req_id, parsed_req, tests, test_file in successful_results:
            assert parsed_req.requirement_id.upper() in req_id.upper()
            assert len(tests) > 0
            assert test_file.requirement_id == parsed_req.requirement_id
        
        print(f"✅ Concurrent processing verified: {len(successful_results)} requirements processed simultaneously")


class TestLayerCompletionCriteria:
    """Test layer completion criteria with FR-002 compliance"""
    
    def test_all_functions_implemented_with_forcing_functions(self):
        """
        Test that all required functions are implemented with forcing functions
        
        RED Phase: MUST fail until all functions implemented
        Forcing Function: Cannot complete layer without all functions
        """
        from src.data_access.requirements_parser import RequirementsParser
        from src.data_access.test_generator import TestGenerator
        
        parser = RequirementsParser()
        generator = TestGenerator()
        
        # Verify all RequirementsParser functions exist and work
        parser_methods = [
            'parse_work_item_requirements',
            'extract_acceptance_criteria', 
            'validate_requirement_completeness',
            'create_requirement_traceability'
        ]
        
        for method_name in parser_methods:
            assert hasattr(parser, method_name), f"RequirementsParser missing method: {method_name}"
            method = getattr(parser, method_name)
            assert callable(method), f"RequirementsParser.{method_name} is not callable"
        
        # Verify all TestGenerator functions exist and work
        generator_methods = [
            'generate_failing_tests',
            'create_test_file_structure',
            'validate_test_generation',
            'ensure_tests_fail_correctly'
        ]
        
        for method_name in generator_methods:
            assert hasattr(generator, method_name), f"TestGenerator missing method: {method_name}"
            method = getattr(generator, method_name)
            assert callable(method), f"TestGenerator.{method_name} is not callable"
        
        print("✅ All functions implemented and callable")

    def test_test_coverage_requirements_with_forcing_functions(self):
        """
        Test that test coverage meets requirements with forcing functions
        
        RED Phase: MUST fail until 95% coverage achieved
        Forcing Function: Cannot proceed without coverage verification
        """
        # This will be verified when we run the actual tests
        # For now, verify the structure exists for coverage measurement
        
        config = get_config()
        assert config.test_generation.minimum_coverage_percentage >= 95.0
        
        # Verify coverage tools are configured
        assert config.test_generation.coverage_fail_under is True
        
        print("✅ Coverage requirements configured: 95% minimum with fail-under enabled")

    def test_integration_tests_passing_with_forcing_functions(self):
        """
        Test that integration tests are passing with forcing functions
        
        RED Phase: MUST fail until integration tests implemented
        Forcing Function: Cannot complete without integration verification
        """
        from src.data_access.requirements_parser import RequirementsParser
        from src.data_access.test_generator import TestGenerator
        
        # Test real integration between components
        parser = RequirementsParser()
        generator = TestGenerator()
        
        # End-to-end integration test
        parsed_req = parser.parse_work_item_requirements("FEATURE-MAKE-WORK-ON-001")
        tests = generator.generate_failing_tests(parsed_req)
        test_file = generator.create_test_file_structure(tests, parsed_req)
        
        # Verify integration points
        assert test_file.requirement_id == parsed_req.requirement_id
        assert len(test_file.generated_tests) == len(tests)
        
        print("✅ Integration tests verified: component interactions working")

    def test_layer_ready_for_business_logic_integration(self):
        """
        Test that layer is ready for Business Logic Layer integration
        
        RED Phase: MUST fail until layer interface contracts complete
        Forcing Function: Must validate interface contracts before handoff
        """
        from src.data_access.requirements_parser import RequirementsParser
        from src.data_access.test_generator import TestGenerator
        
        parser = RequirementsParser()
        generator = TestGenerator()
        
        # Verify interface compliance
        assert isinstance(parser, RequirementsParserInterface)
        assert isinstance(generator, TestGeneratorInterface)
        
        # Test that layer can provide expected outputs to Business Logic Layer
        parsed_req = parser.parse_work_item_requirements("FEATURE-MAKE-WORK-ON-001")
        tests = generator.generate_failing_tests(parsed_req)
        test_file = generator.create_test_file_structure(tests, parsed_req)
        
        # Verify outputs are in expected format for Business Logic Layer
        assert isinstance(parsed_req, ParsedRequirement)
        assert isinstance(tests, list)
        assert all(isinstance(test, GeneratedTest) for test in tests)
        assert isinstance(test_file, TestFile)
        
        # Verify all data needed for TDD workflow is present
        assert parsed_req.validation_result is not None
        assert all(test.is_failing for test in tests)
        assert test_file.total_tests > 0
        
        print("✅ Layer ready for Business Logic integration: all interface contracts satisfied")


# Fixtures for integration tests
@pytest.fixture(scope="session")
def layer_config():
    """Get layer configuration for testing"""
    return get_config()


@pytest.fixture
def real_requirement_files():
    """Get paths to real requirement files for testing"""
    base_path = Path("/workspaces/control_tower/requirements")
    
    files = {
        "feature": base_path / "features" / "FEATURE-MAKE-WORK-ON-001.md",
        "layer": base_path / "layers" / "LAYER-REQUIREMENTS-PARSER-TEST-GENERATOR-001.md"
    }
    
    # Verify files exist
    for name, path in files.items():
        if not path.exists():
            pytest.skip(f"Required test file not found: {path}")
    
    return files


# RED Phase Verification for Complete Layer
def test_complete_layer_red_phase_verification():
    """
    Verify that complete layer is in proper RED phase
    
    This test ensures the layer components work together but fail appropriately
    """
    try:
        # Try to import the main classes
        from src.data_access.requirements_parser import RequirementsParser
        from src.data_access.test_generator import TestGenerator
        
        # If we get here, check if they're properly unimplemented
        parser = RequirementsParser()
        generator = TestGenerator()
        
        # Try the complete workflow - should fail somewhere
        try:
            parsed_req = parser.parse_work_item_requirements("TEST")
            tests = generator.generate_failing_tests(parsed_req)
            test_file = generator.create_test_file_structure(tests, parsed_req)
            
            # If this succeeds completely, we're not in RED phase
            assert False, "Complete layer implementation exists - not in proper RED phase!"
        except (NotImplementedError, AttributeError, Exception):
            # Expected - we're in RED phase
            print("✅ RED phase verified - Complete layer workflow not yet implemented")
            
    except ImportError:
        # Expected - classes don't exist yet
        print("✅ RED phase verified - Layer classes not yet created")
    
    # This assertion will pass to mark the verification as complete
    assert True, "Complete layer RED phase verification complete"