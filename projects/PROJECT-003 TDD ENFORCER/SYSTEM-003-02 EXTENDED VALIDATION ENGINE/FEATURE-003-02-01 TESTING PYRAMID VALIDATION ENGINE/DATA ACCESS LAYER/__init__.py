"""
PROJECT-003 TDD ENFORCER - Data Access Layer Package

This package contains the data access layer implementations for the TDD Enforcer system,
following the hierarchical project structure:

PROJECT-003 TDD ENFORCER
├── SYSTEM-003-02 EXTENDED VALIDATION ENGINE  
│   ├── FEATURE-003-02-01 TESTING PYRAMID VALIDATION ENGINE
│   │   ├── DATA ACCESS LAYER (this package)
│   │   │   ├── src/data_access/         # Implementation modules
│   │   │   ├── tests/                   # Test suites organized by TDD iteration
│   │   │   │   ├── tdd_iteration_1/     # Basic storage functionality
│   │   │   │   ├── tdd_iteration_2/     # Context correlation functionality  
│   │   │   │   └── tdd_iteration_3/     # Audit trail persistence (future)

Key Modules:
- mobile_command_history_repository: Core repository for mobile command history storage
"""

# Version information
__version__ = "1.0.0"
__author__ = "Control Tower Development Team"
__date__ = "2025-09-30"

# Package metadata
__all__ = [
    "data_access",
]