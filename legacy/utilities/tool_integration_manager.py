#!/usr/bin/env python3
"""
Tool Integration Manager - Phase 2D Integration Layer

Implements TR-IL-004: External Tool Integration & Environment Management
Provides integration with external development tools, testing frameworks,
and development environment configuration for TDD workflow execution.

Key Features:
- Development environment setup and validation
- Testing framework integration (pytest, unittest, coverage)
- IDE/Editor configuration and integration
- External tool execution and monitoring
- Environment consistency validation
- Tool dependency management

Integration Points:
- Phase 2B TDD Workflow Engine: Provides tool execution for test running
- Git Safety Manager: Coordinates with git operations for tool execution
- Progress Formatter: Reports tool execution status and results
"""

import subprocess
import json
import os
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Callable
import shutil
import tempfile
import logging

# Control Tower imports
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from business_logic.work_item_model import WorkItem, Priority


class ToolType(Enum):
    """Types of external tools that can be integrated"""
    TESTING_FRAMEWORK = "testing_framework"
    LINTER = "linter"
    FORMATTER = "formatter"
    BUILD_TOOL = "build_tool"
    DEPENDENCY_MANAGER = "dependency_manager"
    IDE_EXTENSION = "ide_extension"
    DOCUMENTATION_TOOL = "documentation_tool"
    ANALYSIS_TOOL = "analysis_tool"


class ToolStatus(Enum):
    """Status of tool installation and availability"""
    AVAILABLE = "available"
    MISSING = "missing"
    OUTDATED = "outdated"
    CONFIGURED = "configured"
    MISCONFIGURED = "misconfigured"
    ERROR = "error"


class ExecutionResult(Enum):
    """Result of tool execution"""
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    ERROR = "error"
    INTERRUPTED = "interrupted"


@dataclass
class ToolInfo:
    """Information about an external tool"""
    name: str
    tool_type: ToolType
    version: Optional[str] = None
    executable_path: Optional[str] = None
    config_path: Optional[str] = None
    status: ToolStatus = ToolStatus.MISSING
    last_checked: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    installation_command: Optional[str] = None
    validation_command: Optional[str] = None


@dataclass
class ExecutionContext:
    """Context for tool execution"""
    working_directory: str
    environment_vars: Dict[str, str] = field(default_factory=dict)
    timeout_seconds: int = 300
    capture_output: bool = True
    shell: bool = True
    input_data: Optional[str] = None


@dataclass
class ToolExecutionResult:
    """Result of tool execution"""
    tool_name: str
    command: str
    result: ExecutionResult
    stdout: str = ""
    stderr: str = ""
    return_code: int = 0
    execution_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    context: Optional[ExecutionContext] = None
    error_details: Optional[str] = None


class ToolInterface(ABC):
    """Abstract base class for tool integrations"""
    
    @abstractmethod
    def validate_installation(self) -> ToolInfo:
        """Validate that the tool is properly installed and configured"""
        pass
    
    @abstractmethod
    def execute(self, command: str, context: ExecutionContext) -> ToolExecutionResult:
        """Execute a command using this tool"""
        pass
    
    @abstractmethod
    def get_version(self) -> Optional[str]:
        """Get the version of the installed tool"""
        pass


class PytestIntegration(ToolInterface):
    """Integration with pytest testing framework"""
    
    def __init__(self):
        self.name = "pytest"
        self.tool_type = ToolType.TESTING_FRAMEWORK
        
    def validate_installation(self) -> ToolInfo:
        """Validate pytest installation"""
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version = result.stdout.strip().split()[-1] if result.stdout else None
                executable_path = shutil.which("pytest") or "python -m pytest"
                
                return ToolInfo(
                    name=self.name,
                    tool_type=self.tool_type,
                    version=version,
                    executable_path=executable_path,
                    status=ToolStatus.AVAILABLE,
                    last_checked=datetime.now(),
                    validation_command="python -m pytest --version"
                )
            else:
                return ToolInfo(
                    name=self.name,
                    tool_type=self.tool_type,
                    status=ToolStatus.MISSING,
                    last_checked=datetime.now(),
                    installation_command="pip install pytest",
                    validation_command="python -m pytest --version"
                )
                
        except Exception as e:
            return ToolInfo(
                name=self.name,
                tool_type=self.tool_type,
                status=ToolStatus.ERROR,
                last_checked=datetime.now()
            )
    
    def execute(self, command: str, context: ExecutionContext) -> ToolExecutionResult:
        """Execute pytest command"""
        start_time = datetime.now()
        
        try:
            # Ensure pytest is in the command
            if not command.startswith("pytest") and "pytest" not in command:
                command = f"python -m pytest {command}"
            
            result = subprocess.run(
                command,
                cwd=context.working_directory,
                env={**os.environ, **context.environment_vars},
                capture_output=context.capture_output,
                text=True,
                shell=context.shell,
                timeout=context.timeout_seconds,
                input=context.input_data
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            execution_result = ExecutionResult.SUCCESS if result.returncode == 0 else ExecutionResult.FAILURE
            
            return ToolExecutionResult(
                tool_name=self.name,
                command=command,
                result=execution_result,
                stdout=result.stdout or "",
                stderr=result.stderr or "",
                return_code=result.returncode,
                execution_time=execution_time,
                context=context
            )
            
        except subprocess.TimeoutExpired:
            execution_time = (datetime.now() - start_time).total_seconds()
            return ToolExecutionResult(
                tool_name=self.name,
                command=command,
                result=ExecutionResult.TIMEOUT,
                execution_time=execution_time,
                context=context,
                error_details="Command timed out"
            )
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return ToolExecutionResult(
                tool_name=self.name,
                command=command,
                result=ExecutionResult.ERROR,
                execution_time=execution_time,
                context=context,
                error_details=str(e)
            )
    
    def get_version(self) -> Optional[str]:
        """Get pytest version"""
        info = self.validate_installation()
        return info.version


class CoverageIntegration(ToolInterface):
    """Integration with coverage.py for test coverage analysis"""
    
    def __init__(self):
        self.name = "coverage"
        self.tool_type = ToolType.ANALYSIS_TOOL
        
    def validate_installation(self) -> ToolInfo:
        """Validate coverage installation"""
        try:
            result = subprocess.run(
                ["python", "-m", "coverage", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version = result.stdout.strip().split()[-1] if result.stdout else None
                
                return ToolInfo(
                    name=self.name,
                    tool_type=self.tool_type,
                    version=version,
                    executable_path="python -m coverage",
                    status=ToolStatus.AVAILABLE,
                    last_checked=datetime.now()
                )
            else:
                return ToolInfo(
                    name=self.name,
                    tool_type=self.tool_type,
                    status=ToolStatus.MISSING,
                    last_checked=datetime.now(),
                    installation_command="pip install coverage"
                )
                
        except Exception:
            return ToolInfo(
                name=self.name,
                tool_type=self.tool_type,
                status=ToolStatus.ERROR,
                last_checked=datetime.now()
            )
    
    def execute(self, command: str, context: ExecutionContext) -> ToolExecutionResult:
        """Execute coverage command"""
        start_time = datetime.now()
        
        try:
            # Ensure coverage is in the command
            if not command.startswith("coverage") and "coverage" not in command:
                command = f"python -m coverage {command}"
            
            result = subprocess.run(
                command,
                cwd=context.working_directory,
                env={**os.environ, **context.environment_vars},
                capture_output=context.capture_output,
                text=True,
                shell=context.shell,
                timeout=context.timeout_seconds
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            execution_result = ExecutionResult.SUCCESS if result.returncode == 0 else ExecutionResult.FAILURE
            
            return ToolExecutionResult(
                tool_name=self.name,
                command=command,
                result=execution_result,
                stdout=result.stdout or "",
                stderr=result.stderr or "",
                return_code=result.returncode,
                execution_time=execution_time,
                context=context
            )
            
        except subprocess.TimeoutExpired:
            execution_time = (datetime.now() - start_time).total_seconds()
            return ToolExecutionResult(
                tool_name=self.name,
                command=command,
                result=ExecutionResult.TIMEOUT,
                execution_time=execution_time,
                context=context,
                error_details="Command timed out"
            )
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return ToolExecutionResult(
                tool_name=self.name,
                command=command,
                result=ExecutionResult.ERROR,
                execution_time=execution_time,
                context=context,
                error_details=str(e)
            )
    
    def get_version(self) -> Optional[str]:
        """Get coverage version"""
        info = self.validate_installation()
        return info.version


class ToolIntegrationManager:
    """
    Tool Integration Manager - TR-IL-004 Implementation
    
    Manages integration with external development tools and provides
    a unified interface for tool execution within TDD workflows.
    """
    
    def __init__(self, workspace_path: str):
        """
        Initialize Tool Integration Manager
        
        Args:
            workspace_path: Path to the workspace/project directory
        """
        self.workspace_path = Path(workspace_path)
        self.tools: Dict[str, ToolInterface] = {}
        self.tool_info_cache: Dict[str, ToolInfo] = {}
        self.execution_history: List[ToolExecutionResult] = []
        
        # Initialize default tool integrations
        self._initialize_default_tools()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def _initialize_default_tools(self):
        """Initialize default tool integrations"""
        self.tools["pytest"] = PytestIntegration()
        self.tools["coverage"] = CoverageIntegration()
    
    def register_tool(self, name: str, tool: ToolInterface):
        """Register a new tool integration"""
        self.tools[name] = tool
        # Clear cached info for this tool
        if name in self.tool_info_cache:
            del self.tool_info_cache[name]
    
    def validate_environment(self) -> Dict[str, ToolInfo]:
        """
        Validate the development environment and tool availability
        
        Returns:
            Dictionary mapping tool names to their validation info
        """
        environment_status = {}
        
        for name, tool in self.tools.items():
            try:
                info = tool.validate_installation()
                self.tool_info_cache[name] = info
                environment_status[name] = info
                
                self.logger.info(f"Tool '{name}' validation: {info.status.value}")
                
            except Exception as e:
                error_info = ToolInfo(
                    name=name,
                    tool_type=tool.tool_type,
                    status=ToolStatus.ERROR,
                    last_checked=datetime.now()
                )
                self.tool_info_cache[name] = error_info
                environment_status[name] = error_info
                
                self.logger.error(f"Error validating tool '{name}': {e}")
        
        return environment_status
    
    def execute_tool_command(self, tool_name: str, command: str, 
                           context: Optional[ExecutionContext] = None) -> ToolExecutionResult:
        """
        Execute a command using a specific tool
        
        Args:
            tool_name: Name of the tool to use
            command: Command to execute
            context: Execution context (optional)
            
        Returns:
            Result of tool execution
        """
        if tool_name not in self.tools:
            return ToolExecutionResult(
                tool_name=tool_name,
                command=command,
                result=ExecutionResult.ERROR,
                error_details=f"Tool '{tool_name}' not registered"
            )
        
        # Use default context if none provided
        if context is None:
            context = ExecutionContext(
                working_directory=str(self.workspace_path)
            )
        
        try:
            tool = self.tools[tool_name]
            result = tool.execute(command, context)
            
            # Store execution history
            self.execution_history.append(result)
            
            # Log execution
            self.logger.info(f"Executed {tool_name}: {command} -> {result.result.value}")
            
            return result
            
        except Exception as e:
            error_result = ToolExecutionResult(
                tool_name=tool_name,
                command=command,
                result=ExecutionResult.ERROR,
                error_details=f"Execution error: {e}",
                context=context
            )
            
            self.execution_history.append(error_result)
            self.logger.error(f"Tool execution error for {tool_name}: {e}")
            
            return error_result
    
    def run_tests(self, test_path: Optional[str] = None, 
                  coverage: bool = False, **kwargs) -> ToolExecutionResult:
        """
        Run tests using the configured testing framework
        
        Args:
            test_path: Specific test file or directory to run
            coverage: Whether to run with coverage analysis
            **kwargs: Additional pytest arguments
            
        Returns:
            Test execution result
        """
        # Build pytest command
        command_parts = []
        
        if test_path:
            command_parts.append(test_path)
        
        # Add additional arguments
        for key, value in kwargs.items():
            if key.startswith('_'):
                continue
            key = key.replace('_', '-')
            if value is True:
                command_parts.append(f"--{key}")
            elif value is not False and value is not None:
                command_parts.append(f"--{key}={value}")
        
        command = " ".join(command_parts) if command_parts else ""
        
        # Execute with or without coverage
        if coverage and "coverage" in self.tools:
            # Run with coverage
            coverage_command = f"run -m pytest {command}"
            return self.execute_tool_command("coverage", coverage_command)
        else:
            # Run tests directly
            return self.execute_tool_command("pytest", command)
    
    def generate_coverage_report(self, format_type: str = "term") -> ToolExecutionResult:
        """
        Generate test coverage report
        
        Args:
            format_type: Report format (term, html, xml, json)
            
        Returns:
            Coverage report generation result
        """
        if format_type == "term":
            command = "report"
        else:
            command = f"{format_type}"
        
        return self.execute_tool_command("coverage", command)
    
    def get_tool_info(self, tool_name: str) -> Optional[ToolInfo]:
        """Get cached information about a tool"""
        return self.tool_info_cache.get(tool_name)
    
    def get_available_tools(self) -> List[str]:
        """Get list of available (properly installed) tools"""
        available = []
        for name, info in self.tool_info_cache.items():
            if info.status in [ToolStatus.AVAILABLE, ToolStatus.CONFIGURED]:
                available.append(name)
        return available
    
    def get_execution_history(self, tool_name: Optional[str] = None, 
                            limit: Optional[int] = None) -> List[ToolExecutionResult]:
        """
        Get execution history
        
        Args:
            tool_name: Filter by specific tool (optional)
            limit: Limit number of results (optional)
            
        Returns:
            List of execution results
        """
        history = self.execution_history
        
        if tool_name:
            history = [r for r in history if r.tool_name == tool_name]
        
        if limit:
            history = history[-limit:]
        
        return history
    
    def install_missing_tools(self) -> Dict[str, bool]:
        """
        Attempt to install missing tools
        
        Returns:
            Dictionary mapping tool names to installation success
        """
        installation_results = {}
        
        for name, info in self.tool_info_cache.items():
            if info.status == ToolStatus.MISSING and info.installation_command:
                try:
                    result = subprocess.run(
                        info.installation_command,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=300  # 5 minute timeout for installation
                    )
                    
                    installation_results[name] = result.returncode == 0
                    
                    if result.returncode == 0:
                        self.logger.info(f"Successfully installed {name}")
                        # Re-validate after installation
                        self.tools[name].validate_installation()
                    else:
                        self.logger.error(f"Failed to install {name}: {result.stderr}")
                        
                except Exception as e:
                    installation_results[name] = False
                    self.logger.error(f"Exception installing {name}: {e}")
            else:
                installation_results[name] = info.status in [ToolStatus.AVAILABLE, ToolStatus.CONFIGURED]
        
        return installation_results
    
    def create_execution_context(self, **kwargs) -> ExecutionContext:
        """
        Create an execution context with workspace defaults
        
        Args:
            **kwargs: Override default context values
            
        Returns:
            Configured execution context
        """
        defaults = {
            "working_directory": str(self.workspace_path),
            "environment_vars": {},
            "timeout_seconds": 300,
            "capture_output": True,
            "shell": True
        }
        
        defaults.update(kwargs)
        return ExecutionContext(**defaults)
    
    def get_environment_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive summary of the development environment
        
        Returns:
            Environment summary including tool status, versions, and capabilities
        """
        summary = {
            "workspace_path": str(self.workspace_path),
            "tools": {},
            "available_tools": self.get_available_tools(),
            "missing_tools": [],
            "error_tools": [],
            "last_validation": datetime.now().isoformat()
        }
        
        for name, info in self.tool_info_cache.items():
            summary["tools"][name] = {
                "status": info.status.value,
                "version": info.version,
                "type": info.tool_type.value,
                "last_checked": info.last_checked.isoformat() if info.last_checked else None
            }
            
            if info.status == ToolStatus.MISSING:
                summary["missing_tools"].append(name)
            elif info.status == ToolStatus.ERROR:
                summary["error_tools"].append(name)
        
        return summary