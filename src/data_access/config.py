"""
Configuration Management for Requirements Parser & Test Generator Layer

Provides environment-aware configuration with validation and forcing functions
as required by FR-002 compliance.

Created: 2025-09-15
Layer: Data Access (Requirements Parser & Test Generator)
TDD Phase: Architecture Definition (Pre-RED)
"""

import os
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum

from .interfaces import ValidationResult


class EnvironmentType(Enum):
    """Supported environment types"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class ParsingConfig:
    """Configuration for requirements parsing"""
    supported_file_extensions: List[str] = field(default_factory=lambda: ['.md', '.markdown'])
    max_file_size_mb: int = 10
    encoding: str = 'utf-8'
    timeout_seconds: int = 30
    
    # Regex patterns for extraction
    requirement_id_patterns: List[str] = field(default_factory=lambda: [
        r'\*\*Requirement\s+ID\*\*:\s*([A-Z]+-[A-Z]+-[A-Z]+-\d+)',
        r'Requirement\s+ID:\s*([A-Z]+-[A-Z]+-\w+-\d+)',
        r'ID:\s*([A-Z]+-\d+-\d+(?:-\d+)?)'
    ])
    
    acceptance_criteria_patterns: List[str] = field(default_factory=lambda: [
        r'- \[([ x])\] \*\*([^*]+)\*\*:\s*(.+)',
        r'^\s*[-*+]\s+(.+)',
        r'^\s*\d+\.\s+(.+)'
    ])


@dataclass
class TestGenerationConfig:
    """Configuration for test generation"""
    test_framework: str = "pytest"
    test_file_prefix: str = "test_"
    test_function_prefix: str = "test_"
    output_directory: str = "tests/generated"
    
    # Test templates
    test_templates_directory: str = "templates/tests"
    default_imports: List[str] = field(default_factory=lambda: [
        "import pytest",
        "from unittest.mock import Mock, patch, MagicMock",
        "from pathlib import Path"
    ])
    
    # Coverage requirements
    minimum_coverage_percentage: float = 95.0
    coverage_fail_under: bool = True
    
    # Performance thresholds
    max_test_execution_time_seconds: float = 5.0
    max_memory_usage_mb: int = 100


@dataclass
class QualityGatesConfig:
    """Configuration for quality gates and forcing functions"""
    enforce_red_phase_verification: bool = True
    enforce_green_phase_verification: bool = True
    enforce_refactor_phase_verification: bool = True
    
    # Verification timeouts
    verification_timeout_seconds: int = 60
    max_retry_attempts: int = 3
    
    # Terminal output requirements
    require_terminal_output: bool = True
    terminal_output_format: str = "structured"  # structured, plain, json


@dataclass
class FileSystemConfig:
    """Configuration for file system operations"""
    base_workspace_path: str = "/workspaces/control_tower"
    requirements_directory: str = "requirements"
    tests_directory: str = "tests"
    source_directory: str = "src"
    
    # File patterns
    requirement_file_patterns: List[str] = field(default_factory=lambda: [
        "FEATURE-*.md",
        "LAYER-*.md", 
        "MILESTONE-*.md"
    ])
    
    # Backup and versioning
    enable_backups: bool = True
    backup_directory: str = "backups"
    max_backup_files: int = 10


@dataclass
class LoggingConfig:
    """Configuration for logging"""
    log_level: str = "INFO"
    log_format: str = "%(asctime)s [%(levelname)8s] %(name)s: %(message)s"
    log_file: str = "logs/requirements_parser.log"
    enable_console_logging: bool = True
    enable_file_logging: bool = True
    max_log_file_size_mb: int = 10
    max_log_files: int = 5


class LayerConfiguration:
    """Main configuration class for the Requirements Parser & Test Generator layer"""
    
    def __init__(self, environment: EnvironmentType = EnvironmentType.DEVELOPMENT):
        """Initialize configuration for specified environment"""
        self.environment = environment
        self.config_loaded = False
        self.validation_result: Optional[ValidationResult] = None
        
        # Initialize configuration components
        self.parsing = ParsingConfig()
        self.test_generation = TestGenerationConfig()
        self.quality_gates = QualityGatesConfig()
        self.file_system = FileSystemConfig()
        self.logging = LoggingConfig()
        
        # Load configuration from environment and files
        self._load_configuration()
    
    def _load_configuration(self) -> None:
        """Load configuration from environment variables and config files"""
        try:
            # Load from environment variables
            self._load_from_environment()
            
            # Load from configuration files
            self._load_from_config_files()
            
            # Validate configuration
            self.validation_result = self.validate()
            
            if self.validation_result.is_valid:
                self.config_loaded = True
                print(f"✅ Configuration loaded successfully for {self.environment.value} environment")
            else:
                self.config_loaded = False
                print(f"❌ Configuration validation failed: {', '.join(self.validation_result.error_messages)}")
                
        except Exception as e:
            self.config_loaded = False
            print(f"❌ Configuration loading failed: {str(e)}")
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables"""
        # File system paths
        if base_path := os.getenv('CONTROL_TOWER_BASE_PATH'):
            self.file_system.base_workspace_path = base_path
        
        if req_dir := os.getenv('CONTROL_TOWER_REQUIREMENTS_DIR'):
            self.file_system.requirements_directory = req_dir
        
        if tests_dir := os.getenv('CONTROL_TOWER_TESTS_DIR'):
            self.file_system.tests_directory = tests_dir
        
        # Test generation settings
        if test_framework := os.getenv('CONTROL_TOWER_TEST_FRAMEWORK'):
            self.test_generation.test_framework = test_framework
        
        if coverage_threshold := os.getenv('CONTROL_TOWER_COVERAGE_THRESHOLD'):
            try:
                self.test_generation.minimum_coverage_percentage = float(coverage_threshold)
            except ValueError:
                pass
        
        # Quality gates
        if enforce_verification := os.getenv('CONTROL_TOWER_ENFORCE_VERIFICATION'):
            enforce = enforce_verification.lower() in ('true', '1', 'yes', 'on')
            self.quality_gates.enforce_red_phase_verification = enforce
            self.quality_gates.enforce_green_phase_verification = enforce
            self.quality_gates.enforce_refactor_phase_verification = enforce
        
        # Logging
        if log_level := os.getenv('CONTROL_TOWER_LOG_LEVEL'):
            self.logging.log_level = log_level.upper()
    
    def _load_from_config_files(self) -> None:
        """Load configuration from JSON config files"""
        config_file_path = Path(self.file_system.base_workspace_path) / "config" / f"{self.environment.value}.json"
        
        if config_file_path.exists():
            try:
                with open(config_file_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Update configuration from file
                if 'parsing' in config_data:
                    self._update_dataclass_from_dict(self.parsing, config_data['parsing'])
                
                if 'test_generation' in config_data:
                    self._update_dataclass_from_dict(self.test_generation, config_data['test_generation'])
                
                if 'quality_gates' in config_data:
                    self._update_dataclass_from_dict(self.quality_gates, config_data['quality_gates'])
                
                if 'file_system' in config_data:
                    self._update_dataclass_from_dict(self.file_system, config_data['file_system'])
                
                if 'logging' in config_data:
                    self._update_dataclass_from_dict(self.logging, config_data['logging'])
                    
            except Exception as e:
                print(f"⚠️ Warning: Could not load config file {config_file_path}: {e}")
    
    def _update_dataclass_from_dict(self, dataclass_instance: Any, data: Dict[str, Any]) -> None:
        """Update dataclass instance with values from dictionary"""
        for key, value in data.items():
            if hasattr(dataclass_instance, key):
                setattr(dataclass_instance, key, value)
    
    def validate(self) -> ValidationResult:
        """Validate configuration with forcing function compliance"""
        result = ValidationResult(is_valid=True)
        
        # Validate file system paths
        base_path = Path(self.file_system.base_workspace_path)
        if not base_path.exists():
            result.add_error(f"Base workspace path does not exist: {base_path}")
        
        # Validate requirements directory
        req_path = base_path / self.file_system.requirements_directory
        if not req_path.exists():
            result.add_warning(f"Requirements directory does not exist: {req_path}")
        
        # Validate tests directory
        tests_path = base_path / self.file_system.tests_directory
        if not tests_path.exists():
            result.add_warning(f"Tests directory does not exist: {tests_path}")
        
        # Validate test generation config
        if self.test_generation.minimum_coverage_percentage < 0 or self.test_generation.minimum_coverage_percentage > 100:
            result.add_error("Coverage percentage must be between 0 and 100")
        
        if self.test_generation.max_test_execution_time_seconds <= 0:
            result.add_error("Max test execution time must be positive")
        
        # Validate parsing config
        if self.parsing.max_file_size_mb <= 0:
            result.add_error("Max file size must be positive")
        
        if self.parsing.timeout_seconds <= 0:
            result.add_error("Parsing timeout must be positive")
        
        # Validate supported file extensions
        if not self.parsing.supported_file_extensions:
            result.add_error("At least one supported file extension must be specified")
        
        # Set forcing function result
        if result.is_valid:
            output = f"✅ Configuration validation passed - all settings valid for {self.environment.value}"
        else:
            output = f"❌ Configuration validation failed - {len(result.error_messages)} errors found"
        
        result.set_forcing_function_result(result.is_valid, output)
        
        return result
    
    def get_absolute_path(self, relative_path: str) -> Path:
        """Get absolute path from relative path"""
        return Path(self.file_system.base_workspace_path) / relative_path
    
    def get_requirements_path(self) -> Path:
        """Get absolute path to requirements directory"""
        return self.get_absolute_path(self.file_system.requirements_directory)
    
    def get_tests_path(self) -> Path:
        """Get absolute path to tests directory"""
        return self.get_absolute_path(self.file_system.tests_directory)
    
    def get_source_path(self) -> Path:
        """Get absolute path to source directory"""
        return self.get_absolute_path(self.file_system.source_directory)
    
    def get_test_output_path(self, requirement_id: str) -> Path:
        """Get absolute path for test output file"""
        tests_path = self.get_tests_path()
        filename = f"{self.test_generation.test_file_prefix}{requirement_id.lower().replace('-', '_')}.py"
        return tests_path / "generated" / filename
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for serialization"""
        return {
            'environment': self.environment.value,
            'config_loaded': self.config_loaded,
            'parsing': self.parsing.__dict__,
            'test_generation': self.test_generation.__dict__,
            'quality_gates': self.quality_gates.__dict__,
            'file_system': self.file_system.__dict__,
            'logging': self.logging.__dict__
        }
    
    def save_to_file(self, file_path: Optional[str] = None) -> bool:
        """Save configuration to JSON file"""
        if not file_path:
            config_dir = self.get_absolute_path("config")
            config_dir.mkdir(exist_ok=True)
            file_path = config_dir / f"{self.environment.value}.json"
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2)
            
            print(f"✅ Configuration saved to {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save configuration: {e}")
            return False


# Global configuration instance
_config_instance: Optional[LayerConfiguration] = None


def get_config(environment: EnvironmentType = EnvironmentType.DEVELOPMENT) -> LayerConfiguration:
    """Get the global configuration instance"""
    global _config_instance
    
    if _config_instance is None or _config_instance.environment != environment:
        _config_instance = LayerConfiguration(environment)
    
    return _config_instance


def validate_startup_configuration() -> ValidationResult:
    """Validate configuration at startup with forcing function"""
    config = get_config()
    
    if not config.config_loaded:
        result = ValidationResult(is_valid=False)
        result.add_error("Configuration failed to load")
        result.set_forcing_function_result(False, "❌ Startup configuration validation failed - config not loaded")
        return result
    
    validation_result = config.validate()
    
    if validation_result.is_valid:
        output = f"✅ Startup configuration validated - {config.environment.value} environment ready"
    else:
        output = f"❌ Startup configuration failed - cannot proceed without valid configuration"
    
    validation_result.set_forcing_function_result(validation_result.is_valid, output)
    return validation_result