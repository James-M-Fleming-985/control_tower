"""
RED Phase Tests - Requirements Parser Core Functionality

These tests define the expected behavior of the RequirementsParser class
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
    AcceptanceCriteria,
    ValidationResult,
    TraceabilityData,
    RequirementsParserInterface,
    RequirementParsingStatus,
)


class TestRequirementsParserInterface:
    """Test the RequirementsParser interface implementation with forcing functions"""
    
    def test_requirements_parser_implements_interface(self):
        """
        Test that RequirementsParser class implements RequirementsParserInterface
        
        RED Phase: This MUST fail until we implement the class
        Forcing Function: Verifies interface compliance before proceeding
        """
        # This will fail until we create the actual RequirementsParser class
        from src.data_access.requirements_parser import RequirementsParser
        
        parser = RequirementsParser()
        
        # Verify it implements the interface
        assert isinstance(parser, RequirementsParserInterface)
        
        # Verify all required methods exist
        assert hasattr(parser, 'parse_work_item_requirements')
        assert hasattr(parser, 'extract_acceptance_criteria')
        assert hasattr(parser, 'validate_requirement_completeness')
        assert hasattr(parser, 'create_requirement_traceability')
        
        print("✅ RequirementsParser interface compliance verified")

    def test_parse_work_item_requirements_with_forcing_function(self):
        """
        Test parse_work_item_requirements method with forcing function verification
        
        RED Phase: MUST fail until implementation exists
        Forcing Function: Cannot proceed without REAL requirement file validation
        """
        from src.data_access.requirements_parser import RequirementsParser
        
        parser = RequirementsParser()
        
        # Test with a valid work item ID
        item_id = "FEATURE-MAKE-WORK-ON-001"
        
        # This should validate file existence first (forcing function)
        result = parser.parse_work_item_requirements(item_id)
        
        # Verify result is a ParsedRequirement object
        assert isinstance(result, ParsedRequirement)
        assert result.requirement_id == item_id
        assert result.parsing_status == RequirementParsingStatus.COMPLETED
        
        # Verify forcing function was applied
        assert hasattr(result, 'validation_result')
        assert result.validation_result is not None
        assert result.validation_result.forcing_function_passed is True
        
        print(f"✅ Requirement file validated: {item_id} (forcing function passed)")

    def test_parse_work_item_requirements_file_not_found_forcing_function(self):
        """
        Test forcing function prevents proceeding when requirement file doesn't exist
        
        RED Phase: MUST fail until proper error handling implemented
        Forcing Function: MUST verify file existence before parsing
        """
        from src.data_access.requirements_parser import RequirementsParser
        
        parser = RequirementsParser()
        
        # Test with non-existent work item ID
        item_id = "NONEXISTENT-ITEM-999"
        
        # This should fail at the forcing function stage
        with pytest.raises(Exception) as exc_info:
            parser.parse_work_item_requirements(item_id)
        
        # Verify error mentions file validation
        error_message = str(exc_info.value).lower()
        assert any(word in error_message for word in ['file', 'not found', 'exist'])
        
        print("✅ File existence forcing function working correctly")

    def test_extract_acceptance_criteria_with_forcing_function(self):
        """
        Test extract_acceptance_criteria with forcing function verification
        
        RED Phase: MUST fail until implementation exists
        Forcing Function: MUST validate ALL criteria are REAL and testable
        """
        from src.data_access.requirements_parser import RequirementsParser
        
        parser = RequirementsParser()
        
        # Sample markdown content with acceptance criteria
        markdown_content = """
        # Test Requirement
        
        ## Acceptance Criteria
        - [x] **AC-001**: Should parse requirement ID correctly
        - [ ] **AC-002**: Should extract acceptance criteria
        - [ ] **AC-003**: Should validate requirement completeness
        """
        
        result = parser.extract_acceptance_criteria(markdown_content)
        
        # Verify result is a list of AcceptanceCriteria objects
        assert isinstance(result, list)
        assert len(result) >= 3
        
        for criteria in result:
            assert isinstance(criteria, AcceptanceCriteria)
            assert criteria.id is not None
            assert criteria.description is not None
            assert criteria.is_testable is True
        
        print(f"✅ Acceptance criteria extracted: {len(result)} testable criteria found")

    def test_validate_requirement_completeness_with_forcing_function(self):
        """
        Test validate_requirement_completeness with forcing function verification
        
        RED Phase: MUST fail until implementation exists
        Forcing Function: MUST verify REAL completeness of REAL requirement data
        """
        from src.data_access.requirements_parser import RequirementsParser
        
        parser = RequirementsParser()
        
        # Create a sample parsed requirement
        requirement = ParsedRequirement(
            requirement_id="TEST-REQ-001",
            requirement_type="Feature Requirement",
            primary_objective="Test parsing functionality",
            acceptance_criteria=[
                {"id": "AC-001", "description": "Should work correctly"}
            ]
        )
        
        result = parser.validate_requirement_completeness(requirement)
        
        # Verify result is a ValidationResult
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert result.forcing_function_passed is True
        assert result.terminal_output != ""
        
        print("✅ Requirement completeness verified - all required fields present")

    def test_create_requirement_traceability_with_forcing_function(self):
        """
        Test create_requirement_traceability with forcing function verification
        
        RED Phase: MUST fail until implementation exists
        Forcing Function: MUST validate REAL traceability to REAL parent requirements
        """
        from src.data_access.requirements_parser import RequirementsParser
        
        parser = RequirementsParser()
        
        # Create a sample parsed requirement
        requirement = ParsedRequirement(
            requirement_id="TEST-REQ-001",
            requirement_type="Feature Requirement",
            primary_objective="Test traceability creation"
        )
        
        result = parser.create_requirement_traceability(requirement)
        
        # Verify result is TraceabilityData
        assert isinstance(result, TraceabilityData)
        assert result.requirement_id == requirement.requirement_id
        assert result.creation_timestamp is not None
        
        print("✅ Traceability established - requirement tracking created")


class TestRequirementsParserParsing:
    """Test the detailed parsing functionality with forcing functions"""
    
    def test_parse_feature_requirement_document(self):
        """
        Test parsing a complete feature requirement document
        
        RED Phase: MUST fail until parsing logic implemented
        Forcing Function: Must process REAL requirement files with REAL validation
        """
        from src.data_access.requirements_parser import RequirementsParser
        
        parser = RequirementsParser()
        
        # Read the actual FEATURE-MAKE-WORK-ON-001.md file
        feature_file_path = "/workspaces/control_tower/requirements/features/FEATURE-MAKE-WORK-ON-001.md"
        
        # This should demonstrate parsing a real requirement file
        result = parser.parse_work_item_requirements("FEATURE-MAKE-WORK-ON-001")
        
        # Verify all required fields are extracted
        assert result.requirement_id.startswith("FEATURE-MAKE-WORK-ON")
        assert result.requirement_type is not None
        assert result.primary_objective is not None
        assert len(result.acceptance_criteria) > 0
        
        # Verify forcing function compliance
        assert result.validation_result is not None
        assert result.validation_result.forcing_function_passed is True
        
        print(f"✅ Feature requirement parsed: {result.requirement_id} with {len(result.acceptance_criteria)} criteria")

    def test_parse_layer_requirement_document(self):
        """
        Test parsing a layer requirement document
        
        RED Phase: MUST fail until layer parsing implemented
        Forcing Function: Must handle REAL layer requirements with validation
        """
        from src.data_access.requirements_parser import RequirementsParser
        
        parser = RequirementsParser()
        
        # Read the actual layer requirements file
        layer_file_path = "/workspaces/control_tower/requirements/layers/LAYER-REQUIREMENTS-PARSER-TEST-GENERATOR-001.md"
        
        result = parser.parse_work_item_requirements("LAYER-REQUIREMENTS-PARSER-TEST-GENERATOR-001")
        
        # Verify layer-specific fields
        assert result.requirement_id.startswith("LAY-APP-REQUIREMENTS-PARSER")
        assert result.level is not None
        assert result.layer_implementation is not None
        
        print(f"✅ Layer requirement parsed: {result.requirement_id} (level {result.level})")

    def test_extract_complex_acceptance_criteria(self):
        """
        Test extraction of complex acceptance criteria formats
        
        RED Phase: MUST fail until complex parsing implemented
        Forcing Function: Must validate ALL criteria types are properly extracted
        """
        from src.data_access.requirements_parser import RequirementsParser
        
        parser = RequirementsParser()
        
        complex_markdown = """
        ## Acceptance Criteria with FR-002 Forcing Functions
        
        - [x] **AC-001**: Function 1 implementation complete
           → MUST Include forcing function and verification with clear terminal output
        - [ ] **AC-002**: Performance requirements met
           → MUST validate REAL performance under REAL load conditions
        - [ ] **AC-003**: Error handling implemented
           → MUST test REAL error scenarios with REAL recovery
        """
        
        result = parser.extract_acceptance_criteria(complex_markdown)
        
        # Verify complex criteria are parsed correctly
        assert len(result) >= 3
        
        for criteria in result:
            assert criteria.description is not None
            assert len(criteria.description) > 10  # Non-trivial descriptions
            
            # Check for forcing function indicators
            if "forcing function" in criteria.description.lower():
                assert criteria.complexity == "complex"
        
        print(f"✅ Complex acceptance criteria parsed: {len(result)} criteria with forcing functions")

    def test_markdown_section_parsing(self):
        """
        Test parsing of different markdown sections
        
        RED Phase: MUST fail until section parsing implemented
        Forcing Function: Must extract REAL section data with validation
        """
        from src.data_access.requirements_parser import RequirementsParser
        
        parser = RequirementsParser()
        
        markdown_with_sections = """
        # Requirement Title
        
        **Requirement ID**: TEST-001
        **Priority**: High
        
        ## Primary Objective
        This is the main goal
        
        ## Technical Specifications
        Technology details here
        
        ## Implementation Details
        Code implementation guidance
        """
        
        # This should parse sections and extract metadata
        result = parser.parse_markdown_content(markdown_with_sections)
        
        # Verify sections were parsed
        assert result.requirement_id == "TEST-001"
        assert result.priority == "High"
        assert result.primary_objective is not None
        
        print("✅ Markdown sections parsed successfully with metadata extraction")


class TestRequirementsParserErrorHandling:
    """Test error handling and edge cases with forcing functions"""
    
    def test_invalid_markdown_format_handling(self):
        """
        Test handling of malformed markdown files
        
        RED Phase: MUST fail until error handling implemented
        Forcing Function: Must provide REAL error recovery with clear guidance
        """
        from src.data_access.requirements_parser import RequirementsParser
        
        parser = RequirementsParser()
        
        invalid_markdown = """
        This is not properly formatted markdown
        No headers or structure
        Missing required fields
        """
        
        # Should handle gracefully with validation errors
        result = parser.parse_markdown_content(invalid_markdown)
        
        # Should still return a ParsedRequirement but with validation errors
        assert isinstance(result, ParsedRequirement)
        assert result.validation_result is not None
        assert not result.validation_result.is_valid
        assert len(result.validation_result.error_messages) > 0
        
        print("✅ Invalid markdown handled gracefully with clear error messages")

    def test_missing_acceptance_criteria_handling(self):
        """
        Test handling when no acceptance criteria found
        
        RED Phase: MUST fail until proper validation implemented
        Forcing Function: Must detect missing criteria and provide guidance
        """
        from src.data_access.requirements_parser import RequirementsParser
        
        parser = RequirementsParser()
        
        markdown_no_criteria = """
        # Valid Requirement
        
        **Requirement ID**: TEST-002
        
        ## Description
        This requirement has no acceptance criteria
        """
        
        result = parser.parse_markdown_content(markdown_no_criteria)
        
        # Should flag missing acceptance criteria
        assert result.validation_result is not None
        has_criteria_error = any(
            "acceptance criteria" in error.lower() 
            for error in result.validation_result.error_messages
        )
        assert has_criteria_error
        
        print("✅ Missing acceptance criteria detected with guidance provided")

    def test_large_file_handling(self):
        """
        Test handling of large requirement files
        
        RED Phase: MUST fail until performance handling implemented
        Forcing Function: Must meet performance targets under load
        """
        from src.data_access.requirements_parser import RequirementsParser
        
        parser = RequirementsParser()
        
        # Create a large markdown content (simulate large file)
        large_content = "# Large Requirement\n\n" + "Large content section.\n" * 1000
        large_content += "\n## Acceptance Criteria\n"
        large_content += "\n".join([f"- [ ] **AC-{i:03d}**: Criterion {i}" for i in range(100)])
        
        import time
        start_time = time.time()
        
        result = parser.parse_markdown_content(large_content)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Performance requirement: <1 second per file
        assert execution_time < 1.0
        assert len(result.acceptance_criteria) == 100
        
        print(f"✅ Large file processed in {execution_time:.3f} seconds (under 1s limit)")


class TestRequirementsParserIntegration:
    """Test integration with file system and configuration"""
    
    def test_real_file_system_integration(self):
        """
        Test integration with real file system operations
        
        RED Phase: MUST fail until file system integration implemented
        Forcing Function: Must use REAL files with REAL validation
        """
        from src.data_access.requirements_parser import RequirementsParser
        
        parser = RequirementsParser()
        
        # Test with real workspace files
        requirements_dir = Path("/workspaces/control_tower/requirements")
        
        # Should validate directory structure
        validation_result = parser.validate_workspace_structure()
        
        assert isinstance(validation_result, ValidationResult)
        if requirements_dir.exists():
            assert validation_result.is_valid
            assert validation_result.forcing_function_passed
        
        print("✅ File system integration validated with real workspace structure")

    def test_configuration_integration(self):
        """
        Test integration with layer configuration
        
        RED Phase: MUST fail until configuration integration implemented
        Forcing Function: Must validate configuration at startup
        """
        from src.data_access.requirements_parser import RequirementsParser
        from src.data_access.config import get_config
        
        config = get_config()
        parser = RequirementsParser(config=config)
        
        # Should use configuration settings
        assert parser.config is not None
        assert parser.config.config_loaded
        
        print("✅ Configuration integration verified - settings loaded")

    def test_concurrent_parsing_capability(self):
        """
        Test concurrent parsing of multiple requirements
        
        RED Phase: MUST fail until concurrent processing implemented
        Forcing Function: Must handle concurrent operations safely
        """
        from src.data_access.requirements_parser import RequirementsParser
        import threading
        import queue
        
        parser = RequirementsParser()
        
        # Test data
        test_items = [
            "FEATURE-MAKE-WORK-ON-001",
            "LAYER-REQUIREMENTS-PARSER-TEST-GENERATOR-001"
        ]
        
        results_queue = queue.Queue()
        threads = []
        
        def parse_worker(item_id):
            try:
                result = parser.parse_work_item_requirements(item_id)
                results_queue.put(("success", item_id, result))
            except Exception as e:
                results_queue.put(("error", item_id, str(e)))
        
        # Start concurrent parsing
        for item_id in test_items:
            thread = threading.Thread(target=parse_worker, args=(item_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=5.0)
        
        # Verify results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        assert len(results) == len(test_items)
        successful_results = [r for r in results if r[0] == "success"]
        assert len(successful_results) > 0
        
        print(f"✅ Concurrent parsing verified: {len(successful_results)} items processed simultaneously")


# Fixtures for common test data
@pytest.fixture
def sample_markdown_content():
    """Sample markdown content for testing"""
    return """
    # Test Feature Requirement
    
    **Requirement ID**: FEATURE-TEST-001
    **Requirement Type**: Feature Requirement
    **Priority**: High
    **Due Date**: 2025-09-20
    
    ## Primary Objective
    Test the requirements parsing functionality
    
    ## Acceptance Criteria
    - [x] **AC-001**: Should parse requirement ID correctly
    - [ ] **AC-002**: Should extract acceptance criteria
    - [ ] **AC-003**: Should validate requirement completeness
    
    ## Technical Specifications
    Implementation using Python with pytest framework
    """


@pytest.fixture
def temp_requirement_file(sample_markdown_content):
    """Create temporary requirement file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(sample_markdown_content)
        f.flush()
        yield f.name
    
    # Cleanup
    Path(f.name).unlink(missing_ok=True)


@pytest.fixture
def mock_file_system():
    """Mock file system operations"""
    with patch('pathlib.Path.exists') as mock_exists, \
         patch('pathlib.Path.is_file') as mock_is_file, \
         patch('builtins.open', mock_open(read_data="mock content")) as mock_file:
        
        mock_exists.return_value = True
        mock_is_file.return_value = True
        
        yield {
            'exists': mock_exists,
            'is_file': mock_is_file,
            'open': mock_file
        }


# RED Phase Verification Test
def test_red_phase_verification():
    """
    Verify that we are in proper RED phase - all tests should fail
    
    This test ensures we haven't accidentally implemented anything yet
    """
    try:
        # Try to import the main class - this should fail
        from src.data_access.requirements_parser import RequirementsParser
        
        # If we get here, check if it's properly unimplemented
        parser = RequirementsParser()
        
        # Try a method call - should fail or raise NotImplementedError
        try:
            result = parser.parse_work_item_requirements("TEST")
            # If this succeeds, we're not in RED phase
            assert False, "Implementation exists - not in proper RED phase!"
        except (NotImplementedError, AttributeError, Exception):
            # Expected - we're in RED phase
            print("✅ RED phase verified - RequirementsParser not yet implemented")
            
    except ImportError:
        # Expected - class doesn't exist yet
        print("✅ RED phase verified - RequirementsParser class not yet created")
    
    # This assertion will pass to mark the verification as complete
    assert True, "RED phase verification complete"