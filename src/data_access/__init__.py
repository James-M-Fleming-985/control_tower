"""
Data Access Layer Module

Provides requirements parsing, test generation, and file system access
functionality for the Control Tower Requirements Management System.

This package implements the foundational data access layer with FR-002
compliance including forcing functions and verification at each stage.
"""

# Legacy imports for compatibility
from .repository_scanner import RepositoryScanner
from .data_models import RawRequirement, RequirementMetadata

# New Requirements Parser & Test Generator Layer imports
from .interfaces import (
    ParsedRequirement,
    GeneratedTest,
    AcceptanceCriteria,
    ValidationResult,
    TraceabilityData,
    TestValidationResult,
    FailureValidation,
    TestFile,
    RequirementsParserInterface,
    TestGeneratorInterface,
    FileSystemInterface,
)

from .config import (
    LayerConfiguration,
    get_config,
    validate_startup_configuration,
    EnvironmentType,
)

from .utils import (
    MarkdownParser,
    RequirementValidator,
    TestCodeGenerator,
    FileSystemUtils,
    TimestampUtils,
    IDGenerator,
    format_terminal_output,
    measure_execution_time,
)

__all__ = [
    # Legacy exports
    'RepositoryScanner',
    'RawRequirement', 
    'RequirementMetadata',
    
    # Interface exports
    'ParsedRequirement',
    'GeneratedTest',
    'AcceptanceCriteria',
    'ValidationResult',
    'TraceabilityData',
    'TestValidationResult',
    'FailureValidation',
    'TestFile',
    'RequirementsParserInterface',
    'TestGeneratorInterface',
    'FileSystemInterface',
    
    # Configuration exports
    'LayerConfiguration',
    'get_config',
    'validate_startup_configuration',
    'EnvironmentType',
    
    # Utility exports
    'MarkdownParser',
    'RequirementValidator',
    'TestCodeGenerator',
    'FileSystemUtils',
    'TimestampUtils',
    'IDGenerator',
    'format_terminal_output',
    'measure_execution_time',
]