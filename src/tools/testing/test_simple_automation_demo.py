#!/usr/bin/env python3
"""
REAL Business Value TDD Automation Tests
These tests implement actual business requirements for the control tower system
"""

def test_parse_requirement_priority():
    """Test: Parse requirement priority from markdown content - REAL business need"""
    from data_access.requirements_parser import RequirementsParser
    parser = RequirementsParser()
    
    # REAL business case: Extract priority from requirement documents
    markdown_content = """
    # REQ-001: Critical System Enhancement
    **Priority:** HIGH
    **Impact:** Customer-facing functionality
    """
    
    assert hasattr(parser, 'extract_priority_level'), "Parser should extract priority levels"
    priority = parser.extract_priority_level(markdown_content)
    assert priority == "HIGH", "Should correctly extract HIGH priority"
    assert isinstance(priority, str), "Priority should be string type"

def test_generate_traceability_matrix():
    """Test: Generate requirement traceability matrix - REAL compliance need"""
    from data_access.test_generator import TestGenerator
    generator = TestGenerator()
    
    # REAL business case: Generate traceability for compliance/audit
    requirements = [
        {"id": "REQ-001", "tests": ["test_login", "test_auth"]},
        {"id": "REQ-002", "tests": ["test_data_validation"]}
    ]
    
    assert hasattr(generator, 'generate_traceability_matrix'), "Generator should create traceability"
    matrix = generator.generate_traceability_matrix(requirements)
    assert len(matrix) == 2, "Should have traceability for all requirements"
    assert "REQ-001" in matrix, "Should include all requirement IDs"
    assert len(matrix["REQ-001"]["tests"]) == 2, "Should track all associated tests"

def test_validate_acceptance_criteria_completeness():
    """Test: Validate acceptance criteria completeness - REAL quality assurance"""
    from data_access.requirements_parser import RequirementsParser
    parser = RequirementsParser()
    
    # REAL business case: Ensure all requirements have proper acceptance criteria
    requirement_data = {
        "id": "REQ-003",
        "title": "User Authentication",
        "acceptance_criteria": [
            {"id": "AC-001", "description": "User can login with valid credentials"},
            {"id": "AC-002", "description": "User receives error for invalid credentials"}
        ]
    }
    
    assert hasattr(parser, 'validate_acceptance_criteria_completeness'), "Parser should validate criteria"
    validation = parser.validate_acceptance_criteria_completeness(requirement_data)
    assert validation["is_complete"] == True, "Should validate complete acceptance criteria"
    assert validation["criteria_count"] == 2, "Should count acceptance criteria correctly"
    assert "coverage_percentage" in validation, "Should calculate coverage metrics"