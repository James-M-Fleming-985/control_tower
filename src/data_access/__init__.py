"""
Data Access Layer Module

Provides file system scanning and repository access functionality
for the make what-next command.
"""

from .repository_scanner import RepositoryScanner
from .data_models import RawRequirement, RequirementMetadata

__all__ = [
    'RepositoryScanner',
    'RawRequirement', 
    'RequirementMetadata'
]