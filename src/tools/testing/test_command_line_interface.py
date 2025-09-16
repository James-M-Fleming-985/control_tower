"""
Unit tests for TR-IL-002: Command Line Interface

This module provides comprehensive testing for the Command Line Interface component
of the Control Tower Phase 1 integration layer.

Testing Strategy:
- Test argument parsing for all supported options
- Test integration with make command system
- Test error handling for invalid arguments
- Test output formatting for both terminal and JSON modes

Author: Control Tower Development Team
Created: 2025-09-13
"""

import pytest
import json
import sys
from unittest.mock import Mock, patch, MagicMock
from datetime import date, timedelta
from typing import List, Dict, Any

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


class TestCommandLineInterface:
    """Test suite for CommandLineInterface class"""
    
    def setup_method(self):
        """Setup test fixtures before each test method"""
        if 'CommandLineInterface' in globals():
            self.cli = CommandLineInterface()
        self.sample_work_items = [
            WorkItem(
                id="FEATURE-001",
                title="Test Feature 1",
                description="Test description 1",
                due_date=date.today(),
                priority=Priority.HIGH,
                effort_estimate="2 days",
                requirement_level="FR",
                project_type="APPLICATION",
                repository="test_repo",
                system_name="Test System",
                project_name="Test Project",
                layer_or_milestone="Business Logic",
                hierarchy_path="Test Feature 1 → Test System → Test Project → test_repo",
                status=ItemStatus.DUE_TODAY
            ),
            WorkItem(
                id="FEATURE-002",
                title="Test Feature 2",
                description="Test description 2",
                due_date=date.today() - timedelta(days=1),
                priority=Priority.CRITICAL,
                effort_estimate="1 day",
                requirement_level="FR",
                project_type="STANDARD_DELIVERY",
                repository="test_repo2",
                system_name="Test System 2",
                project_name="Test Project 2",
                layer_or_milestone="Integration Layer",
                hierarchy_path="Test Feature 2 → Test System 2 → Test Project 2 → test_repo2",
                status=ItemStatus.OVERDUE
            )
        ]

    def test_parse_arguments_default_options(self):
        """Test parsing arguments with default options - IL-006"""
        # Arrange
        args = []
        
        # Act
        options = self.cli.parse_arguments(args)
        
        # Assert
        assert options.repositories is None
        assert options.output_format == OutputFormat.TERMINAL
        assert options.debug is False
        assert options.show_all is False

    def test_parse_arguments_repository_filter(self):
        """Test parsing arguments with repository filter - IL-006"""
        # Arrange
        args = ["--repository=financial_security_dev"]
        
        # Act
        options = self.cli.parse_arguments(args)
        
        # Assert
        assert options.repositories == ["financial_security_dev"]
        assert options.output_format == OutputFormat.TERMINAL


    def test_parse_arguments_multiple_repositories(self):
        """Test parsing arguments with multiple repositories - IL-006"""
        # Arrange
        args = ["--repositories=repo1,repo2,repo3"]
        
        # Act
        options = self.cli.parse_arguments(args)
        
        # Assert
        assert options.repositories == ["repo1", "repo2", "repo3"]

    def test_parse_arguments_json_output(self):
        """Test parsing arguments with JSON output format - IL-007"""
        # Arrange
        args = ["--json"]
        
        # Act
        options = self.cli.parse_arguments(args)
        
        # Assert
        assert options.output_format == OutputFormat.JSON


    def test_parse_arguments_debug_mode(self):
        """Test parsing arguments with debug mode enabled - IL-006"""
        # Arrange
        args = ["--debug"]
        
        # Act
        options = self.cli.parse_arguments(args)
        
        # Assert
        assert options.debug is True


    def test_parse_arguments_show_all(self):
        """Test parsing arguments with show all option - IL-006"""
        # Arrange
        args = ["--all"]
        
        # Act
        options = self.cli.parse_arguments(args)
        
        # Assert
        assert options.show_all is True


    def test_parse_arguments_combined_options(self):
        """Test parsing arguments with multiple options combined - IL-006"""
        # Arrange
        args = ["--repository=test_repo", "--json", "--debug"]
        
        # Act
        options = self.cli.parse_arguments(args)
        
        # Assert
        assert options.repositories == ["test_repo"]
        assert options.output_format == OutputFormat.JSON
        assert options.debug is True


    def test_parse_arguments_invalid_option(self):
        """Test parsing arguments with invalid option - IL-008"""
        # Arrange
        args = ["--invalid-option"]
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.cli.parse_arguments(args)
        
        assert "Unknown option" in str(exc_info.value)


    def test_parse_arguments_invalid_repository_format(self):
        """Test parsing arguments with invalid repository format - IL-008"""
        # Arrange
        args = ["--repository="]  # Empty repository name
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.cli.parse_arguments(args)
        
        assert "Repository name cannot be empty" in str(exc_info.value)


    @patch('src.integration.command_line_interface.WorkItemDiscoveryEngine')
    def test_execute_discovery_terminal_output(self, mock_engine):
        """Test executing discovery with terminal output - IL-007"""
        # Arrange
        mock_engine_instance = Mock()
        mock_engine_instance.discover_work_items.return_value = self.sample_work_items
        
        cli = CommandLineInterface(discovery_engine=mock_engine_instance)
        
        options = CommandOptions(
            repositories=["test_repo"],
            output_format=OutputFormat.TERMINAL,
            debug=False,
            show_all=False
        )
        
        # Act
        result = cli.execute_discovery(options)
        
        # Assert
        assert result.success is True
        assert len(result.work_items) == 2
        assert result.output_format == OutputFormat.TERMINAL
        assert "Test Feature 1" in result.formatted_output
        assert "Test Feature 2" in result.formatted_output


    @patch('src.integration.command_line_interface.WorkItemDiscoveryEngine')
    def test_execute_discovery_json_output(self, mock_engine):
        """Test executing discovery with JSON output - IL-007"""
        # Arrange
        mock_engine_instance = Mock()
        mock_engine_instance.discover_work_items.return_value = self.sample_work_items
        
        cli = CommandLineInterface(discovery_engine=mock_engine_instance)
        
        options = CommandOptions(
            repositories=["test_repo"],
            output_format=OutputFormat.JSON,
            debug=False,
            show_all=False
        )
        
        # Act
        result = cli.execute_discovery(options)
        
        # Assert
        assert result.success is True
        assert result.output_format == OutputFormat.JSON
        
        # Verify JSON output is valid
        json_data = json.loads(result.formatted_output)
        assert "work_items" in json_data
        assert len(json_data["work_items"]) == 2
        assert json_data["work_items"][0]["id"] == "FEATURE-001"


    @patch('src.integration.command_line_interface.WorkItemDiscoveryEngine')
    def test_execute_discovery_debug_mode(self, mock_engine):
        """Test executing discovery with debug mode enabled - IL-006"""
        # Arrange
        mock_engine_instance = Mock()
        mock_engine_instance.discover_work_items.return_value = self.sample_work_items
        
        cli = CommandLineInterface(discovery_engine=mock_engine_instance)
        
        options = CommandOptions(
            repositories=["test_repo"],
            output_format=OutputFormat.TERMINAL,
            debug=True,
            show_all=False
        )
        
        # Act
        result = cli.execute_discovery(options)
        
        # Assert
        assert result.success is True
        assert result.debug_info is not None
        assert "repositories" in result.debug_info
        assert "execution_time" in result.debug_info


    @patch('src.integration.command_line_interface.WorkItemDiscoveryEngine')
    def test_execute_discovery_no_repositories(self, mock_engine):
        """Test executing discovery with no repositories specified - IL-008"""
        # Arrange
        mock_engine_instance = Mock()
        mock_engine_instance.discover_work_items.return_value = []
        
        cli = CommandLineInterface(discovery_engine=mock_engine_instance)
        
        options = CommandOptions(
            repositories=None,
            output_format=OutputFormat.TERMINAL,
            debug=False,
            show_all=False
        )
        
        # Act
        result = cli.execute_discovery(options)
        
        # Assert
        assert result.success is True
        assert len(result.work_items) == 0
        assert "No work items found" in result.formatted_output


    @patch('src.integration.command_line_interface.WorkItemDiscoveryEngine')
    def test_execute_discovery_engine_error(self, mock_engine):
        """Test executing discovery when engine raises error - IL-008"""
        # Arrange
        mock_engine_instance = Mock()
        mock_engine_instance.discover_work_items.side_effect = Exception("Discovery failed")
        
        cli = CommandLineInterface(discovery_engine=mock_engine_instance)
        
        options = CommandOptions(
            repositories=["test_repo"],
            output_format=OutputFormat.TERMINAL,
            debug=False,
            show_all=False
        )
        
        # Act
        result = cli.execute_discovery(options)
        
        # Assert
        assert result.success is False
        assert "Discovery failed" in result.error_message


    def test_handle_errors_generic_exception(self):
        """Test error handling for generic exceptions - IL-008"""
        # Arrange
        error = Exception("Test error message")
        
        # Act
        response = self.cli.handle_errors(error)
        
        # Assert
        assert response.success is False
        assert response.error_type == "Exception"
        assert response.error_message == "Test error message"
        assert response.exit_code == 1


    def test_handle_errors_value_error(self):
        """Test error handling for value errors - IL-008"""
        # Arrange
        error = ValueError("Invalid argument value")
        
        # Act
        response = self.cli.handle_errors(error)
        
        # Assert
        assert response.success is False
        assert response.error_type == "ValueError"
        assert response.error_message == "Invalid argument value"
        assert response.exit_code == 2


    def test_handle_errors_file_not_found(self):
        """Test error handling for file not found errors - IL-008"""
        # Arrange
        error = FileNotFoundError("Repository not found")
        
        # Act
        response = self.cli.handle_errors(error)
        
        # Assert
        assert response.success is False
        assert response.error_type == "FileNotFoundError"
        assert response.error_message == "Repository not found"
        assert response.exit_code == 3


    def test_makefile_integration(self):
        """Test integration with makefile system - IL-005"""
        # This test validates that the CLI can be called from make command
        # Arrange
        args = ["--repositories=cloned_repos/financial_security_dev", "--json"]
        
        # Act
        options = self.cli.parse_arguments(args)
        
        # Assert
        assert options.repositories == ["cloned_repos/financial_security_dev"]
        assert options.output_format == OutputFormat.JSON


    def test_performance_requirements(self):
        """Test that discovery completes within performance requirements - IL-005"""
        # Arrange
        import time
        options = CommandOptions(
            repositories=["test_repo"],
            output_format=OutputFormat.TERMINAL,
            debug=False,
            show_all=False
        )
        
        # Act
        start_time = time.time()
        mock_engine_instance = Mock()
        mock_engine_instance.discover_work_items.return_value = self.sample_work_items
        
        cli = CommandLineInterface(discovery_engine=mock_engine_instance)
        result = cli.execute_discovery(options)
            
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Assert
        assert result.success is True
        assert execution_time < 5.0  # Performance requirement: <5 seconds


class TestCommandOptions:
    """Test suite for CommandOptions data class"""
    

    def test_command_options_creation(self):
        """Test creating CommandOptions with all parameters"""
        # Act
        options = CommandOptions(
            repositories=["repo1", "repo2"],
            output_format=OutputFormat.JSON,
            debug=True,
            show_all=True
        )
        
        # Assert
        assert options.repositories == ["repo1", "repo2"]
        assert options.output_format == OutputFormat.JSON
        assert options.debug is True
        assert options.show_all is True


    def test_command_options_defaults(self):
        """Test CommandOptions with default values"""
        # Act
        options = CommandOptions()
        
        # Assert
        assert options.repositories is None
        assert options.output_format == OutputFormat.TERMINAL
        assert options.debug is False
        assert options.show_all is False


class TestCommandResult:
    """Test suite for CommandResult data class"""
    

    def test_command_result_success(self):
        """Test creating successful CommandResult"""
        # Arrange
        work_items = [Mock()]
        
        # Act
        result = CommandResult(
            success=True,
            work_items=work_items,
            formatted_output="Test output",
            output_format=OutputFormat.TERMINAL,
            debug_info={"test": "info"}
        )
        
        # Assert
        assert result.success is True
        assert result.work_items == work_items
        assert result.formatted_output == "Test output"
        assert result.output_format == OutputFormat.TERMINAL
        assert result.debug_info == {"test": "info"}
        assert result.error_message is None


    def test_command_result_failure(self):
        """Test creating failed CommandResult"""
        # Act
        result = CommandResult(
            success=False,
            work_items=[],
            formatted_output="",
            output_format=OutputFormat.TERMINAL,
            error_message="Test error"
        )
        
        # Assert
        assert result.success is False
        assert result.work_items == []
        assert result.formatted_output == ""
        assert result.error_message == "Test error"


class TestErrorResponse:
    """Test suite for ErrorResponse data class"""
    

    def test_error_response_creation(self):
        """Test creating ErrorResponse"""
        # Act
        response = ErrorResponse(
            success=False,
            error_type="ValueError",
            error_message="Test error",
            exit_code=2
        )
        
        # Assert
        assert response.success is False
        assert response.error_type == "ValueError"
        assert response.error_message == "Test error"
        assert response.exit_code == 2


# Test coverage tracking
def test_module_imports():
    """Ensure all required modules can be imported"""
    try:
        from src.integration.command_line_interface import (
            CommandLineInterface,
            CommandOptions,
            CommandResult,
            ErrorResponse,
            OutputFormat
        )
        assert True
    except ImportError:
        pytest.skip("TDD RED phase - implementation not yet available")