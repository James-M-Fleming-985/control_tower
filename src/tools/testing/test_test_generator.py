#!/usr/bin/env python3
"""
Unit Tests for Test Generator - TR-DA-003

Tests for FR-DA-003-003: Automated Test Generation
Following TDD methodology - RED phase tests that will initially fail
"""

import pytest
from pathlib import Path
from typing import List, Dict, Any
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from data_access.test_generator import TestGenerator, GeneratedTest
from data_access.requirements_parser import ParsedRequirement
from data_access.requirements_models import ProjectType


class TestAutomatedTestGeneration:
    """Unit tests for automated test generation from requirements"""
    
    def setup_method(self):
        """Set up test fixtures before each test"""
        self.test_generator = TestGenerator()
        
        # Sample parsed requirement for testing - using correct constructor parameters
        self.sample_requirement = ParsedRequirement(
            requirement_id="FEATURE-001-05-02",
            requirement_type="Feature Requirement", 
            level=4,
            primary_objective="Implement automated execution of portfolio rebalancing trades",
            acceptance_criteria=[
                {
                    "id": "AC-001",
                    "description": "Calculates optimal buy/sell orders for rebalancing",
                    "completed": False
                },
                {
                    "id": "AC-002", 
                    "description": "Implements cost optimization algorithms",
                    "completed": False
                },
                {
                    "id": "AC-003",
                    "description": "Integrates with trading platform APIs",
                    "completed": False
                }
            ],
            layer_implementation="Integration Layer",
            project_type=ProjectType.APPLICATION
        )
    
    # RED PHASE TESTS - These will fail initially
    
    def test_generate_failing_unit_tests_from_acceptance_criteria(self):
        """Test generation of failing pytest unit tests from acceptance criteria"""
        # This will fail until we implement the test generator
        generated_tests = self.test_generator.generate_unit_tests(self.sample_requirement)
        
        assert len(generated_tests) == 3  # One test per acceptance criterion
        
        # Check first generated test
        test_ac_001 = generated_tests[0]
        assert test_ac_001.test_name == "test_calculates_optimal_buy_sell_orders_for_rebalancing"
        assert test_ac_001.test_type == "unit"
        assert "def test_calculates_optimal_buy_sell_orders_for_rebalancing" in test_ac_001.test_code
        assert "pytest" in test_ac_001.framework_imports
        
        # Check that tests are failing initially
        assert test_ac_001.initial_status == "failing"
    
    def test_generate_test_names_from_acceptance_criteria(self):
        """Test generation of meaningful test names from acceptance criteria"""
        generated_tests = self.test_generator.generate_unit_tests(self.sample_requirement)
        
        expected_names = [
            "test_calculates_optimal_buy_sell_orders_for_rebalancing",
            "test_implements_cost_optimization_algorithms", 
            "test_integrates_with_trading_platform_apis"
        ]
        
        actual_names = [test.test_name for test in generated_tests]
        assert actual_names == expected_names
    
    def test_generate_pytest_test_file_with_proper_structure(self):
        """Test generation of complete pytest file with imports and fixtures"""
        test_file = self.test_generator.generate_test_file(self.sample_requirement)
        
        assert test_file.filename == "test_feature_001_05_02_automated_rebalancing_execution.py"
        assert "import pytest" in test_file.content
        assert "class TestAutomatedRebalancingExecution:" in test_file.content
        assert "def setup_method(self):" in test_file.content
        
        # Should include all generated test methods
        assert "test_calculates_optimal_buy_sell_orders_for_rebalancing" in test_file.content
        assert "test_implements_cost_optimization_algorithms" in test_file.content
        assert "test_integrates_with_trading_platform_apis" in test_file.content
    
    def test_include_appropriate_fixtures_and_mocks(self):
        """Test inclusion of appropriate pytest fixtures and mock setups"""
        test_file = self.test_generator.generate_test_file(self.sample_requirement)
        
        # Should include fixtures based on Integration Layer context
        assert "@pytest.fixture" in test_file.content
        assert "mock_trading_platform" in test_file.content
        assert "mock_portfolio_data" in test_file.content
        
        # Should include imports for mocking
        assert "from unittest.mock import Mock, patch" in test_file.content
    
    def test_create_failing_tests_initially(self):
        """Test that generated tests fail initially (RED phase)"""
        test_file = self.test_generator.generate_test_file(self.sample_requirement)
        
        # All tests should contain assert statements that will fail
        assert "assert False, \"Test not implemented\"" in test_file.content or \
               "raise NotImplementedError(\"Test implementation pending\")" in test_file.content
    
    def test_generate_integration_test_templates(self):
        """Test generation of integration test templates for layer interactions"""
        integration_tests = self.test_generator.generate_integration_tests(self.sample_requirement)
        
        assert len(integration_tests) > 0
        
        # Should generate tests for Integration Layer interactions
        integration_test = integration_tests[0]
        assert integration_test.test_type == "integration"
        assert "integration" in integration_test.test_name.lower()
        assert "test_integration_with_" in integration_test.test_name
    
    def test_generate_different_tests_for_different_layers(self):
        """Test that different target layers generate appropriate test patterns"""
        # Business Logic Layer requirement
        bl_requirement = ParsedRequirement(
            requirement_id="FEATURE-002",
            target_layer="Business Logic Layer",
            acceptance_criteria=[{"id": "AC-001", "description": "Processes business rules", "completed": False}],
            project_type="Application"
        )
        
        bl_tests = self.test_generator.generate_unit_tests(bl_requirement)
        
        # Should generate business logic focused tests
        assert any("business" in test.test_code.lower() for test in bl_tests)
        
        # Data Access Layer requirement  
        da_requirement = ParsedRequirement(
            requirement_id="FEATURE-003",
            target_layer="Data Access Layer",
            acceptance_criteria=[{"id": "AC-001", "description": "Stores data correctly", "completed": False}],
            project_type="Application"
        )
        
        da_tests = self.test_generator.generate_unit_tests(da_requirement)
        
        # Should generate data access focused tests
        assert any("data" in test.test_code.lower() or "database" in test.test_code.lower() for test in da_tests)
    
    def test_generate_parameterized_tests_for_multiple_scenarios(self):
        """Test generation of parameterized tests for scenarios with multiple cases"""
        requirement_with_scenarios = ParsedRequirement(
            requirement_id="FEATURE-004",
            acceptance_criteria=[{
                "id": "AC-001", 
                "description": "Validates input data for different portfolio types (stocks, bonds, ETFs)",
                "completed": False
            }],
            target_layer="Business Logic Layer",
            project_type="Application"
        )
        
        generated_tests = self.test_generator.generate_unit_tests(requirement_with_scenarios)
        
        # Should generate parameterized tests for multiple scenarios
        test_code = generated_tests[0].test_code
        assert "@pytest.mark.parametrize" in test_code
        assert "stocks" in test_code and "bonds" in test_code and "ETFs" in test_code
    
    def test_generate_tests_for_standard_delivery_projects(self):
        """Test generation of tests for Standard Delivery milestone requirements"""
        milestone_requirement = ParsedRequirement(
            requirement_id="MILESTONE-002-03",
            requirement_type="Milestone",
            project_type="Standard Delivery",
            focus_area="Task Requirements",
            acceptance_criteria=[{
                "id": "AC-001",
                "description": "Database migration completes successfully", 
                "completed": False
            }],
            target_component="Database Layer"
        )
        
        generated_tests = self.test_generator.generate_unit_tests(milestone_requirement)
        
        # Should generate task-focused tests for Standard Delivery
        assert len(generated_tests) > 0
        assert "migration" in generated_tests[0].test_name.lower()
        assert "database" in generated_tests[0].test_code.lower()


class TestGeneratedTestDataModel:
    """Unit tests for GeneratedTest data model"""
    
    def test_generated_test_object_creation(self):
        """Test creating GeneratedTest objects with validation"""
        test_data = {
            'test_name': 'test_example',
            'test_type': 'unit',
            'test_code': 'def test_example(): pass',
            'framework_imports': ['pytest'],
            'initial_status': 'failing'
        }
        
        # This will fail until we implement the data model
        generated_test = GeneratedTest(**test_data)
        
        assert generated_test.test_name == 'test_example'
        assert generated_test.test_type == 'unit'
        assert generated_test.initial_status == 'failing'
    
    def test_test_file_generation_with_proper_structure(self):
        """Test generation of complete test file structure"""
        test_file = self.test_generator.create_test_file_structure(
            requirement_id="FEATURE-001",
            test_class_name="TestFeature001",
            generated_tests=[]
        )
        
        assert test_file.filename.endswith(".py")
        assert "class TestFeature001:" in test_file.content
        assert "import pytest" in test_file.content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])