#!/usr/bin/env python3
"""
Test Suite for Tool Integration Manager - Phase 2D Integration Layer

Comprehensive testing for TR-IL-004: External Tool Integration & Environment Management
Tests the Tool Integration Manager's ability to manage external development tools
and provide unified tool execution within TDD workflows.
"""

import pytest
import tempfile
import subprocess
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from datetime import datetime

# Add src to path for imports
import sys
# Import (using root src - not PROJECT-003 specific)
sys.path.append('/workspaces/control_tower/src')

from integration.tool_integration_manager import (
    ToolIntegrationManager, ToolType, ToolStatus, ExecutionResult,
    ToolInfo, ExecutionContext, ToolExecutionResult,
    PytestIntegration, CoverageIntegration
)


class TestToolInfo:
    """Test ToolInfo dataclass"""
    
    def test_tool_info_creation(self):
        """Test ToolInfo creation with defaults"""
        tool_info = ToolInfo(
            name="pytest",
            tool_type=ToolType.TESTING_FRAMEWORK
        )
        
        assert tool_info.name == "pytest"
        assert tool_info.tool_type == ToolType.TESTING_FRAMEWORK
        assert tool_info.version is None
        assert tool_info.status == ToolStatus.MISSING
        assert tool_info.dependencies == []
    
    def test_tool_info_full_creation(self):
        """Test ToolInfo creation with all fields"""
        now = datetime.now()
        tool_info = ToolInfo(
            name="pytest",
            tool_type=ToolType.TESTING_FRAMEWORK,
            version="7.4.0",
            executable_path="/usr/bin/pytest",
            config_path="/project/.pytest.ini",
            status=ToolStatus.AVAILABLE,
            last_checked=now,
            dependencies=["python"],
            installation_command="pip install pytest",
            validation_command="pytest --version"
        )
        
        assert tool_info.name == "pytest"
        assert tool_info.version == "7.4.0"
        assert tool_info.executable_path == "/usr/bin/pytest"
        assert tool_info.status == ToolStatus.AVAILABLE
        assert tool_info.last_checked == now
        assert tool_info.dependencies == ["python"]


class TestExecutionContext:
    """Test ExecutionContext dataclass"""
    
    def test_execution_context_defaults(self):
        """Test ExecutionContext creation with defaults"""
        context = ExecutionContext(working_directory="/test")
        
        assert context.working_directory == "/test"
        assert context.environment_vars == {}
        assert context.timeout_seconds == 300
        assert context.capture_output is True
        assert context.shell is True
        assert context.input_data is None
    
    def test_execution_context_custom(self):
        """Test ExecutionContext creation with custom values"""
        context = ExecutionContext(
            working_directory="/custom",
            environment_vars={"TEST": "value"},
            timeout_seconds=60,
            capture_output=False,
            shell=False,
            input_data="test input"
        )
        
        assert context.working_directory == "/custom"
        assert context.environment_vars == {"TEST": "value"}
        assert context.timeout_seconds == 60
        assert context.capture_output is False
        assert context.shell is False
        assert context.input_data == "test input"


class TestToolExecutionResult:
    """Test ToolExecutionResult dataclass"""
    
    def test_tool_execution_result_defaults(self):
        """Test ToolExecutionResult creation with defaults"""
        result = ToolExecutionResult(
            tool_name="pytest",
            command="pytest test.py",
            result=ExecutionResult.SUCCESS
        )
        
        assert result.tool_name == "pytest"
        assert result.command == "pytest test.py"
        assert result.result == ExecutionResult.SUCCESS
        assert result.stdout == ""
        assert result.stderr == ""
        assert result.return_code == 0
        assert result.execution_time == 0.0
        assert isinstance(result.timestamp, datetime)
        assert result.context is None
        assert result.error_details is None


class TestPytestIntegration:
    """Test PytestIntegration tool interface"""
    
    @pytest.fixture
    def pytest_integration(self):
        """Create PytestIntegration instance"""
        return PytestIntegration()
    
    @patch('subprocess.run')
    def test_validate_installation_success(self, mock_run, pytest_integration):
        """Test successful pytest validation"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="pytest 7.4.0"
        )
        
        with patch('shutil.which', return_value="/usr/bin/pytest"):
            info = pytest_integration.validate_installation()
        
        assert info.name == "pytest"
        assert info.tool_type == ToolType.TESTING_FRAMEWORK
        assert info.version == "7.4.0"
        assert info.executable_path == "/usr/bin/pytest"
        assert info.status == ToolStatus.AVAILABLE
        assert isinstance(info.last_checked, datetime)
    
    @patch('subprocess.run')
    def test_validate_installation_missing(self, mock_run, pytest_integration):
        """Test pytest validation when tool is missing"""
        mock_run.return_value = MagicMock(returncode=1)
        
        info = pytest_integration.validate_installation()
        
        assert info.name == "pytest"
        assert info.status == ToolStatus.MISSING
        assert info.installation_command == "pip install pytest"
    
    @patch('subprocess.run')
    def test_validate_installation_error(self, mock_run, pytest_integration):
        """Test pytest validation with exception"""
        mock_run.side_effect = Exception("Command failed")
        
        info = pytest_integration.validate_installation()
        
        assert info.name == "pytest"
        assert info.status == ToolStatus.ERROR
    
    @patch('subprocess.run')
    def test_execute_success(self, mock_run, pytest_integration):
        """Test successful pytest execution"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="test output",
            stderr=""
        )
        
        context = ExecutionContext(working_directory="/test")
        result = pytest_integration.execute("test.py", context)
        
        assert result.tool_name == "pytest"
        assert result.result == ExecutionResult.SUCCESS
        assert result.stdout == "test output"
        assert result.return_code == 0
        assert result.context == context
    
    @patch('subprocess.run')
    def test_execute_failure(self, mock_run, pytest_integration):
        """Test pytest execution failure"""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="test failed"
        )
        
        context = ExecutionContext(working_directory="/test")
        result = pytest_integration.execute("test.py", context)
        
        assert result.tool_name == "pytest"
        assert result.result == ExecutionResult.FAILURE
        assert result.stderr == "test failed"
        assert result.return_code == 1
    
    @patch('subprocess.run')
    def test_execute_timeout(self, mock_run, pytest_integration):
        """Test pytest execution timeout"""
        mock_run.side_effect = subprocess.TimeoutExpired("pytest", 30)
        
        context = ExecutionContext(working_directory="/test")
        result = pytest_integration.execute("test.py", context)
        
        assert result.tool_name == "pytest"
        assert result.result == ExecutionResult.TIMEOUT
        assert result.error_details == "Command timed out"
    
    def test_execute_command_prefix(self, pytest_integration):
        """Test that pytest commands are properly prefixed"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            
            context = ExecutionContext(working_directory="/test")
            pytest_integration.execute("test.py", context)
            
            # Should call with python -m pytest prefix
            called_command = mock_run.call_args[0][0]
            assert "python -m pytest test.py" in called_command


class TestCoverageIntegration:
    """Test CoverageIntegration tool interface"""
    
    @pytest.fixture
    def coverage_integration(self):
        """Create CoverageIntegration instance"""
        return CoverageIntegration()
    
    @patch('subprocess.run')
    def test_validate_installation_success(self, mock_run, coverage_integration):
        """Test successful coverage validation"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="coverage, version 7.2.7"
        )
        
        info = coverage_integration.validate_installation()
        
        assert info.name == "coverage"
        assert info.tool_type == ToolType.ANALYSIS_TOOL
        assert info.version == "7.2.7"
        assert info.executable_path == "python -m coverage"
        assert info.status == ToolStatus.AVAILABLE
    
    @patch('subprocess.run')
    def test_execute_coverage_command(self, mock_run, coverage_integration):
        """Test coverage command execution"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="coverage output",
            stderr=""
        )
        
        context = ExecutionContext(working_directory="/test")
        result = coverage_integration.execute("report", context)
        
        assert result.tool_name == "coverage"
        assert result.result == ExecutionResult.SUCCESS
        assert result.stdout == "coverage output"
        
        # Should call with python -m coverage prefix
        called_command = mock_run.call_args[0][0]
        assert "python -m coverage report" in called_command


class TestToolIntegrationManager:
    """Test ToolIntegrationManager main class"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def tool_manager(self, temp_workspace):
        """Create ToolIntegrationManager instance"""
        return ToolIntegrationManager(temp_workspace)
    
    def test_initialization(self, tool_manager, temp_workspace):
        """Test ToolIntegrationManager initialization"""
        assert str(tool_manager.workspace_path) == temp_workspace
        assert "pytest" in tool_manager.tools
        assert "coverage" in tool_manager.tools
        assert tool_manager.execution_history == []
    
    def test_register_tool(self, tool_manager):
        """Test tool registration"""
        mock_tool = MagicMock()
        mock_tool.tool_type = ToolType.LINTER
        
        tool_manager.register_tool("custom_tool", mock_tool)
        
        assert "custom_tool" in tool_manager.tools
        assert tool_manager.tools["custom_tool"] == mock_tool
    
    @patch.object(PytestIntegration, 'validate_installation')
    @patch.object(CoverageIntegration, 'validate_installation')
    def test_validate_environment(self, mock_coverage_validate, mock_pytest_validate, tool_manager):
        """Test environment validation"""
        # Setup mock returns
        pytest_info = ToolInfo(
            name="pytest",
            tool_type=ToolType.TESTING_FRAMEWORK,
            status=ToolStatus.AVAILABLE,
            version="7.4.0"
        )
        coverage_info = ToolInfo(
            name="coverage",
            tool_type=ToolType.ANALYSIS_TOOL,
            status=ToolStatus.MISSING
        )
        
        mock_pytest_validate.return_value = pytest_info
        mock_coverage_validate.return_value = coverage_info
        
        environment_status = tool_manager.validate_environment()
        
        assert "pytest" in environment_status
        assert "coverage" in environment_status
        assert environment_status["pytest"].status == ToolStatus.AVAILABLE
        assert environment_status["coverage"].status == ToolStatus.MISSING
        
        # Check caching
        assert tool_manager.tool_info_cache["pytest"] == pytest_info
        assert tool_manager.tool_info_cache["coverage"] == coverage_info
    
    def test_execute_tool_command_unregistered(self, tool_manager):
        """Test executing command with unregistered tool"""
        result = tool_manager.execute_tool_command("nonexistent", "command")
        
        assert result.tool_name == "nonexistent"
        assert result.result == ExecutionResult.ERROR
        assert "not registered" in result.error_details
    
    @patch.object(PytestIntegration, 'execute')
    def test_execute_tool_command_success(self, mock_execute, tool_manager):
        """Test successful tool command execution"""
        expected_result = ToolExecutionResult(
            tool_name="pytest",
            command="test.py",
            result=ExecutionResult.SUCCESS
        )
        mock_execute.return_value = expected_result
        
        result = tool_manager.execute_tool_command("pytest", "test.py")
        
        assert result == expected_result
        assert result in tool_manager.execution_history
        
        # Check that default context was created
        call_args = mock_execute.call_args
        context = call_args[0][1]
        assert context.working_directory == str(tool_manager.workspace_path)
    
    @patch.object(PytestIntegration, 'execute')
    def test_execute_tool_command_with_context(self, mock_execute, tool_manager):
        """Test tool command execution with custom context"""
        custom_context = ExecutionContext(
            working_directory="/custom",
            timeout_seconds=60
        )
        
        expected_result = ToolExecutionResult(
            tool_name="pytest",
            command="test.py",
            result=ExecutionResult.SUCCESS
        )
        mock_execute.return_value = expected_result
        
        result = tool_manager.execute_tool_command("pytest", "test.py", custom_context)
        
        # Check that custom context was used
        call_args = mock_execute.call_args
        context = call_args[0][1]
        assert context == custom_context
    
    @patch.object(ToolIntegrationManager, 'execute_tool_command')
    def test_run_tests_basic(self, mock_execute, tool_manager):
        """Test basic test execution"""
        expected_result = ToolExecutionResult(
            tool_name="pytest",
            command="",
            result=ExecutionResult.SUCCESS
        )
        mock_execute.return_value = expected_result
        
        result = tool_manager.run_tests()
        
        mock_execute.assert_called_once_with("pytest", "")
        assert result == expected_result
    
    @patch.object(ToolIntegrationManager, 'execute_tool_command')
    def test_run_tests_with_path(self, mock_execute, tool_manager):
        """Test test execution with specific path"""
        tool_manager.run_tests(test_path="tests/test_module.py")
        
        mock_execute.assert_called_once_with("pytest", "tests/test_module.py")
    
    @patch.object(ToolIntegrationManager, 'execute_tool_command')
    def test_run_tests_with_coverage(self, mock_execute, tool_manager):
        """Test test execution with coverage"""
        # Setup coverage tool availability
        tool_manager.tools["coverage"] = CoverageIntegration()
        
        tool_manager.run_tests(coverage=True, test_path="tests/")
        
        mock_execute.assert_called_once_with("coverage", "run -m pytest tests/")
    
    @patch.object(ToolIntegrationManager, 'execute_tool_command')
    def test_run_tests_with_options(self, mock_execute, tool_manager):
        """Test test execution with pytest options"""
        tool_manager.run_tests(verbose=True, no_header=True, maxfail=3)
        
        # Should build command with pytest options
        call_args = mock_execute.call_args
        command = call_args[0][1]
        assert "--verbose" in command
        assert "--no-header" in command
        assert "--maxfail=3" in command
    
    @patch.object(ToolIntegrationManager, 'execute_tool_command')
    def test_generate_coverage_report(self, mock_execute, tool_manager):
        """Test coverage report generation"""
        tool_manager.generate_coverage_report("html")
        
        mock_execute.assert_called_once_with("coverage", "html")
    
    def test_get_tool_info(self, tool_manager):
        """Test getting cached tool info"""
        # Add some cached info
        info = ToolInfo(name="pytest", tool_type=ToolType.TESTING_FRAMEWORK)
        tool_manager.tool_info_cache["pytest"] = info
        
        result = tool_manager.get_tool_info("pytest")
        assert result == info
        
        result = tool_manager.get_tool_info("nonexistent")
        assert result is None
    
    def test_get_available_tools(self, tool_manager):
        """Test getting available tools list"""
        # Setup cache with mixed statuses
        tool_manager.tool_info_cache = {
            "pytest": ToolInfo(name="pytest", tool_type=ToolType.TESTING_FRAMEWORK, status=ToolStatus.AVAILABLE),
            "coverage": ToolInfo(name="coverage", tool_type=ToolType.ANALYSIS_TOOL, status=ToolStatus.MISSING),
            "linter": ToolInfo(name="linter", tool_type=ToolType.LINTER, status=ToolStatus.CONFIGURED)
        }
        
        available = tool_manager.get_available_tools()
        
        assert "pytest" in available
        assert "linter" in available
        assert "coverage" not in available
    
    def test_get_execution_history(self, tool_manager):
        """Test getting execution history"""
        # Add some execution history
        result1 = ToolExecutionResult(tool_name="pytest", command="test1", result=ExecutionResult.SUCCESS)
        result2 = ToolExecutionResult(tool_name="coverage", command="report", result=ExecutionResult.SUCCESS)
        result3 = ToolExecutionResult(tool_name="pytest", command="test2", result=ExecutionResult.FAILURE)
        
        tool_manager.execution_history = [result1, result2, result3]
        
        # Test full history
        history = tool_manager.get_execution_history()
        assert len(history) == 3
        
        # Test filtered by tool
        pytest_history = tool_manager.get_execution_history(tool_name="pytest")
        assert len(pytest_history) == 2
        assert all(r.tool_name == "pytest" for r in pytest_history)
        
        # Test with limit
        limited_history = tool_manager.get_execution_history(limit=2)
        assert len(limited_history) == 2
        assert limited_history == [result2, result3]  # Last 2
    
    @patch('subprocess.run')
    def test_install_missing_tools(self, mock_run, tool_manager):
        """Test installing missing tools"""
        # Setup cache with missing tool
        tool_manager.tool_info_cache = {
            "missing_tool": ToolInfo(
                name="missing_tool",
                tool_type=ToolType.LINTER,
                status=ToolStatus.MISSING,
                installation_command="pip install missing_tool"
            ),
            "available_tool": ToolInfo(
                name="available_tool",
                tool_type=ToolType.FORMATTER,
                status=ToolStatus.AVAILABLE
            )
        }
        
        # Mock successful installation
        mock_run.return_value = MagicMock(returncode=0)
        
        # Mock tool re-validation after installation
        mock_tool = MagicMock()
        tool_manager.tools["missing_tool"] = mock_tool
        
        results = tool_manager.install_missing_tools()
        
        assert results["missing_tool"] is True
        assert results["available_tool"] is True  # Already available
        
        # Check that installation command was called
        mock_run.assert_called_once_with(
            "pip install missing_tool",
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
    
    def test_create_execution_context(self, tool_manager):
        """Test creating execution context"""
        context = tool_manager.create_execution_context(
            timeout_seconds=60,
            capture_output=False
        )
        
        assert context.working_directory == str(tool_manager.workspace_path)
        assert context.timeout_seconds == 60
        assert context.capture_output is False
        assert context.shell is True  # Default maintained
    
    def test_get_environment_summary(self, tool_manager):
        """Test getting environment summary"""
        # Setup cache
        tool_manager.tool_info_cache = {
            "pytest": ToolInfo(
                name="pytest",
                tool_type=ToolType.TESTING_FRAMEWORK,
                status=ToolStatus.AVAILABLE,
                version="7.4.0",
                last_checked=datetime(2023, 1, 1)
            ),
            "missing": ToolInfo(
                name="missing",
                tool_type=ToolType.LINTER,
                status=ToolStatus.MISSING
            ),
            "error": ToolInfo(
                name="error",
                tool_type=ToolType.FORMATTER,
                status=ToolStatus.ERROR
            )
        }
        
        summary = tool_manager.get_environment_summary()
        
        assert summary["workspace_path"] == str(tool_manager.workspace_path)
        assert "pytest" in summary["available_tools"]
        assert "missing" in summary["missing_tools"]
        assert "error" in summary["error_tools"]
        
        assert summary["tools"]["pytest"]["status"] == "available"
        assert summary["tools"]["pytest"]["version"] == "7.4.0"
        assert summary["tools"]["pytest"]["type"] == "testing_framework"


class TestToolIntegrationManagerIntegration:
    """Integration tests for ToolIntegrationManager"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace with test files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a simple test file
            test_file = Path(temp_dir) / "test_sample.py"
            test_file.write_text("""
def test_sample():
    assert True

def test_another():
    assert 1 + 1 == 2
""")
            yield temp_dir
    
    @pytest.fixture
    def integration_manager(self, temp_workspace):
        """Create ToolIntegrationManager for integration testing"""
        return ToolIntegrationManager(temp_workspace)
    
    def test_complete_tool_workflow(self, integration_manager):
        """Test complete tool integration workflow"""
        # 1. Validate environment
        environment_status = integration_manager.validate_environment()
        assert "pytest" in environment_status
        assert "coverage" in environment_status
        
        # 2. Check available tools
        available_tools = integration_manager.get_available_tools()
        
        # 3. Get environment summary
        summary = integration_manager.get_environment_summary()
        assert "tools" in summary
        assert "available_tools" in summary
        
        # 4. Test execution (if pytest is available)
        if "pytest" in available_tools:
            # Create simple execution context
            context = integration_manager.create_execution_context(timeout_seconds=30)
            
            # Execute a simple command
            result = integration_manager.execute_tool_command("pytest", "--version", context)
            assert result.tool_name == "pytest"
            
            # Check execution history
            history = integration_manager.get_execution_history()
            assert len(history) >= 1
            assert history[-1].tool_name == "pytest"