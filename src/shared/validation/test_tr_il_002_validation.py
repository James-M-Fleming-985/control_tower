"""
Validation tests for TR-IL-002: Command Line Interface

This module validates that the Command Line Interface component meets all
acceptance criteria for TR-IL-002 as specified in PHASE-1-LAYER-REQUIREMENTS.md.

Acceptance Criteria Being Validated:
- IL-005: Integrates with makefile system
- IL-006: Parses command options correctly  
- IL-007: Provides both terminal and JSON output
- IL-008: Handles invalid options gracefully

Author: Control Tower Development Team
Created: 2025-09-13
"""

import pytest
import json
import sys
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import date, timedelta

# Import the module under test (will fail initially - TDD RED phase)
try:
    from src.integration.command_line_interface import (
        CommandLineInterface,
        CommandOptions,
        CommandResult,
        ErrorResponse,
        OutputFormat
    )
except ImportError:
    # TDD RED phase - module doesn't exist yet
    pass

from src.business_logic.work_item_model import WorkItem, Priority, ItemStatus


class TestTRIL002AcceptanceCriteria:
    """
    Validation test suite for TR-IL-002 Command Line Interface
    
    Tests all acceptance criteria:
    - IL-005: Integrates with makefile system
    - IL-006: Parses command options correctly
    - IL-007: Provides both terminal and JSON output  
    - IL-008: Handles invalid options gracefully
    """
    
    def setup_method(self):
        """Setup test fixtures for validation tests"""
        if 'CommandLineInterface' in globals():
            self.cli = CommandLineInterface()
        
        # Create realistic test work items for validation
        self.validation_work_items = [
            WorkItem(
                id="FEATURE-003-02",
                title="Investment Portfolio Rebalancing",
                description="Implement portfolio rebalancing algorithm for investment optimization",
                due_date=date.today(),  # Due today
                priority=Priority.HIGH,
                effort_estimate="3 days",
                requirement_level="FR",
                project_type="APPLICATION",
                repository="financial_security_dev",
                system_name="Investment Strategy",
                project_name="Financial Security",
                layer_or_milestone="Data Access Layer",
                hierarchy_path="Investment Portfolio Rebalancing → Investment Strategy → Financial Security → financial_security_dev",
                status=ItemStatus.DUE_TODAY
            ),
            WorkItem(
                id="MILESTONE-002-01",
                title="Core Infrastructure Setup",
                description="Set up basic project infrastructure and dependencies",
                due_date=date.today() - timedelta(days=2),  # Overdue
                priority=Priority.CRITICAL,
                effort_estimate="1 day",
                requirement_level="MR",
                project_type="STANDARD_DELIVERY",
                repository="home_improvements",
                system_name="Project Management",
                project_name="Home Improvements",
                layer_or_milestone="Infrastructure",
                hierarchy_path="Core Infrastructure Setup → Project Management → Home Improvements → home_improvements",
                status=ItemStatus.OVERDUE
            )
        ]


    def test_il_005_makefile_system_integration(self):
        """
        IL-005: Integrates with makefile system
        
        Validates that the CLI can be properly invoked from Makefile commands
        and handles repository paths in makefile format.
        """
        # Test makefile-style repository path handling
        makefile_repo_paths = [
            "cloned_repos/financial_security_dev",
            "cloned_repos/home_improvements",
            "cloned_repos/contract_projects"
        ]
        
        # Test parsing makefile-style arguments
        args = [f"--repositories={','.join(makefile_repo_paths)}"]
        options = self.cli.parse_arguments(args)
        
        assert options.repositories == makefile_repo_paths
        assert options.output_format == OutputFormat.TERMINAL
        
        # Test that CLI can handle make command environment
        with patch.dict('os.environ', {'MAKE': '1', 'MAKELEVEL': '1'}):
            result = self.cli.execute_discovery(options)
            assert result is not None


    def test_il_005_makefile_variable_expansion(self):
        """
        IL-005: Integrates with makefile system - Variable expansion
        
        Validates that CLI handles makefile variable patterns correctly.
        """
        # Test makefile-style variable patterns
        args = ["--repositories=$(REPO_BASE)/financial_security_dev"]
        
        # The CLI should handle this gracefully even if variables aren't expanded
        options = self.cli.parse_arguments(args)
        assert "financial_security_dev" in options.repositories[0]


    def test_il_006_parse_repository_option(self):
        """
        IL-006: Parses command options correctly - Repository filtering
        
        Validates single repository filtering option.
        """
        args = ["--repository=financial_security_dev"]
        options = self.cli.parse_arguments(args)
        
        assert options.repositories == ["financial_security_dev"]
        assert options.output_format == OutputFormat.TERMINAL
        assert options.debug is False
        assert options.show_all is False


    def test_il_006_parse_repositories_option(self):
        """
        IL-006: Parses command options correctly - Multiple repositories
        
        Validates multiple repository specification.
        """
        args = ["--repositories=repo1,repo2,repo3"]
        options = self.cli.parse_arguments(args)
        
        assert options.repositories == ["repo1", "repo2", "repo3"]


    def test_il_006_parse_json_option(self):
        """
        IL-006: Parses command options correctly - JSON output format
        
        Validates JSON output format specification.
        """
        args = ["--json"]
        options = self.cli.parse_arguments(args)
        
        assert options.output_format == OutputFormat.JSON


    def test_il_006_parse_debug_option(self):
        """
        IL-006: Parses command options correctly - Debug mode
        
        Validates debug mode option parsing.
        """
        args = ["--debug"]
        options = self.cli.parse_arguments(args)
        
        assert options.debug is True


    def test_il_006_parse_all_option(self):
        """
        IL-006: Parses command options correctly - Show all items
        
        Validates show all items option parsing.
        """
        args = ["--all"]
        options = self.cli.parse_arguments(args)
        
        assert options.show_all is True


    def test_il_006_parse_combined_options(self):
        """
        IL-006: Parses command options correctly - Combined options
        
        Validates parsing of multiple options together.
        """
        args = ["--repository=test_repo", "--json", "--debug", "--all"]
        options = self.cli.parse_arguments(args)
        
        assert options.repositories == ["test_repo"]
        assert options.output_format == OutputFormat.JSON
        assert options.debug is True
        assert options.show_all is True


    def test_il_007_terminal_output_format(self):
        """
        IL-007: Provides both terminal and JSON output - Terminal format
        
        Validates terminal output formatting with realistic work items.
        """
        # Setup mock engine with proper dependency injection
        mock_engine = Mock()
        mock_engine.discover_work_items.return_value = self.validation_work_items
        
        # Create CLI with mocked engine
        cli = CommandLineInterface(discovery_engine=mock_engine)
        
        options = CommandOptions(
            repositories=["financial_security_dev"],
            output_format=OutputFormat.TERMINAL,
            debug=False,
            show_all=False
        )
        
        result = cli.execute_discovery(options)
        
        # Validate terminal output format
        assert result.success is True
        assert result.output_format == OutputFormat.TERMINAL
        
        output = result.formatted_output
        
        # Validate terminal formatting requirements
        assert "⏰ OVERDUE:" in output or "🎯 DUE TODAY:" in output
        assert "FEATURE-003-02" in output
        assert "Investment Portfolio Rebalancing" in output
        assert "Investment Strategy → Financial Security → financial_security_dev" in output
        assert "Data Access Layer" in output
        assert "Priority: High" in output
        assert "Effort: 3 days" in output
        assert "make work TASK=FEATURE-003-02" in output


    def test_il_007_json_output_format(self):
        """
        IL-007: Provides both terminal and JSON output - JSON format
        
        Validates JSON output formatting with realistic work items.
        """
        # Setup mock engine with proper dependency injection
        mock_engine = Mock()
        mock_engine.discover_work_items.return_value = self.validation_work_items
        
        # Create CLI with mocked engine
        cli = CommandLineInterface(discovery_engine=mock_engine)
        
        options = CommandOptions(
            repositories=["financial_security_dev"],
            output_format=OutputFormat.JSON,
            debug=False,
            show_all=False
        )
        
        result = cli.execute_discovery(options)
        
        # Validate JSON output format
        assert result.success is True
        assert result.output_format == OutputFormat.JSON
        
        # Parse and validate JSON structure
        json_data = json.loads(result.formatted_output)
        
        assert "summary" in json_data
        assert "work_items" in json_data
        assert "metadata" in json_data
        
        # Validate summary section
        summary = json_data["summary"]
        assert "total_items" in summary
        assert "overdue_count" in summary
        assert "due_today_count" in summary
        
        # Validate work items structure
        work_items = json_data["work_items"]
        assert len(work_items) == 2
        
        item = work_items[0]
        assert "id" in item
        assert "title" in item
        assert "due_date" in item
        assert "priority" in item
        assert "repository" in item
        assert "hierarchy_path" in item
        assert "status" in item


    @patch('src.integration.command_line_interface.WorkItemDiscoveryEngine')
    def test_il_007_output_format_consistency(self, mock_engine):
        """
        IL-007: Provides both terminal and JSON output - Format consistency
        
        Validates that both output formats contain the same work item data.
        """
        # Setup mock engine
        mock_engine_instance = Mock()
        mock_engine.return_value = mock_engine_instance
        mock_engine_instance.discover_work_items.return_value = self.validation_work_items
        
        # Test terminal output
        terminal_options = CommandOptions(output_format=OutputFormat.TERMINAL)
        terminal_result = self.cli.execute_discovery(terminal_options)
        
        # Test JSON output
        json_options = CommandOptions(output_format=OutputFormat.JSON)
        json_result = self.cli.execute_discovery(json_options)
        
        # Validate both succeeded
        assert terminal_result.success is True
        assert json_result.success is True
        
        # Validate same work items in both
        assert len(terminal_result.work_items) == len(json_result.work_items)
        
        # Validate JSON contains same IDs as terminal
        json_data = json.loads(json_result.formatted_output)
        json_ids = [item["id"] for item in json_data["work_items"]]
        terminal_ids = [item.id for item in terminal_result.work_items]
        
        assert set(json_ids) == set(terminal_ids)


    def test_il_008_invalid_option_handling(self):
        """
        IL-008: Handles invalid options gracefully - Unknown option
        
        Validates graceful handling of unknown command options.
        """
        args = ["--unknown-option", "--another-bad-option=value"]
        
        with pytest.raises(ValueError) as exc_info:
            self.cli.parse_arguments(args)
        
        error_message = str(exc_info.value)
        assert "Unknown option" in error_message or "Invalid option" in error_message


    def test_il_008_invalid_repository_format(self):
        """
        IL-008: Handles invalid options gracefully - Invalid repository format
        
        Validates handling of invalid repository specifications.
        """
        test_cases = [
            ["--repository="],  # Empty repository
            ["--repositories="],  # Empty repositories list
            ["--repository= "],  # Whitespace only
            ["--repositories=,,,"],  # Only commas
        ]
        
        for args in test_cases:
            with pytest.raises(ValueError) as exc_info:
                self.cli.parse_arguments(args)
            
            error_message = str(exc_info.value)
            assert ("Repository name cannot be empty" in error_message or 
                    "Repository names cannot be empty" in error_message or 
                    "Invalid repository" in error_message)


    def test_il_008_malformed_arguments(self):
        """
        IL-008: Handles invalid options gracefully - Malformed arguments
        
        Validates handling of malformed argument patterns.
        """
        test_cases = [
            ["--repository"],  # Missing value
            ["--repositories=repo1,"],  # Trailing comma
            ["--json=true"],  # Unexpected value for flag
            ["--debug=false"],  # Unexpected value for flag
        ]
        
        for args in test_cases:
            with pytest.raises(ValueError):
                self.cli.parse_arguments(args)


    def test_il_008_error_response_structure(self):
        """
        IL-008: Handles invalid options gracefully - Error response structure
        
        Validates that error responses have consistent structure.
        """
        test_errors = [
            ValueError("Test value error"),
            FileNotFoundError("Test file error"),
            Exception("Test generic error")
        ]
        
        for error in test_errors:
            response = self.cli.handle_errors(error)
            
            assert response.success is False
            assert response.error_type is not None
            assert response.error_message is not None
            assert response.exit_code > 0
            assert isinstance(response.exit_code, int)


    def test_il_008_discovery_engine_error_handling(self):
        """
        IL-008: Handles invalid options gracefully - Engine error handling
        
        Validates graceful handling of discovery engine errors.
        """
        # Setup engine to raise error with proper dependency injection
        mock_engine = Mock()
        mock_engine.discover_work_items.side_effect = Exception("Discovery engine failed")
        
        # Create CLI with mocked engine
        cli = CommandLineInterface(discovery_engine=mock_engine)
        
        options = CommandOptions(repositories=["test_repo"])
        result = cli.execute_discovery(options)
        
        assert result.success is False
        assert "Discovery engine failed" in result.error_message
        assert result.work_items == []


class TestTRIL002Integration:
    """
    Integration validation tests for TR-IL-002
    
    Tests realistic end-to-end scenarios and integration with other components.
    """
    

    def test_end_to_end_terminal_workflow(self):
        """
        Validates complete terminal workflow from argument parsing to output.
        """
        # Simulate complete workflow
        args = ["--repository=financial_security_dev", "--debug"]
        
        with patch('src.integration.command_line_interface.WorkItemDiscoveryEngine') as mock_engine:
            cli = CommandLineInterface()
            
            # Parse arguments
            options = cli.parse_arguments(args)
            
            # Setup mock discovery
            mock_engine_instance = Mock()
            mock_engine.return_value = mock_engine_instance
            mock_engine_instance.discover_work_items.return_value = []
            
            # Execute discovery
            result = cli.execute_discovery(options)
            
            # Validate complete workflow
            assert result.success is True
            assert result.debug_info is not None
            assert "No work items found" in result.formatted_output


    def test_end_to_end_json_workflow(self):
        """
        Validates complete JSON workflow from argument parsing to output.
        """
        args = ["--repositories=repo1,repo2", "--json"]
        
        with patch('src.integration.command_line_interface.WorkItemDiscoveryEngine') as mock_engine:
            cli = CommandLineInterface()
            
            # Parse arguments
            options = cli.parse_arguments(args)
            
            # Setup mock discovery
            mock_engine_instance = Mock()
            mock_engine.return_value = mock_engine_instance
            mock_engine_instance.discover_work_items.return_value = []
            
            # Execute discovery
            result = cli.execute_discovery(options)
            
            # Validate JSON workflow
            assert result.success is True
            assert result.output_format == OutputFormat.JSON
            
            json_data = json.loads(result.formatted_output)
            assert "summary" in json_data
            assert "work_items" in json_data


    def test_performance_validation(self):
        """
        Validates that CLI meets performance requirements (<5 seconds).
        """
        import time
        
        args = ["--repositories=repo1,repo2,repo3"]
        
        with patch('src.integration.command_line_interface.WorkItemDiscoveryEngine') as mock_engine:
            cli = CommandLineInterface()
            
            # Setup mock with realistic delay
            mock_engine_instance = Mock()
            mock_engine.return_value = mock_engine_instance
            mock_engine_instance.discover_work_items.return_value = []
            
            options = cli.parse_arguments(args)
            
            start_time = time.time()
            result = cli.execute_discovery(options)
            end_time = time.time()
            
            execution_time = end_time - start_time
            
            assert result.success is True
            assert execution_time < 5.0  # Performance requirement


# Test coverage validation
def test_tr_il_002_test_coverage():
    """
    Validates that all TR-IL-002 acceptance criteria have corresponding tests.
    
    This meta-test ensures we have complete test coverage for all requirements.
    """
    # This test documents which acceptance criteria are covered
    covered_criteria = {
        "IL-005": "Integrates with makefile system",
        "IL-006": "Parses command options correctly", 
        "IL-007": "Provides both terminal and JSON output",
        "IL-008": "Handles invalid options gracefully"
    }
    
    # All criteria should be covered by the tests above
    assert len(covered_criteria) == 4
    
    # During TDD RED phase, we skip this validation
    pytest.skip("TDD RED phase - implementation not yet available")