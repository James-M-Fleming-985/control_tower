#!/usr/bin/env python3
"""
PROJECT-003 TDD ENFORCER Package

Main package for Test-Driven Development enforcement system.
Provides comprehensive TDD methodology validation and automation.

Structure:
- current/: Live production code for active development
- archived/: Historical versions and legacy implementations

Import Examples:
    from tdd_enforcer.current.mobile_command_history import MobileCommandHistoryRepository
    from tdd_enforcer.current.mobile_command_history.data_access import repository
"""

__version__ = "1.0.0"
__author__ = "Control Tower Development Team"
__status__ = "Production"

# Main package imports
from . import current
try:
    from . import archived
except ImportError:
    # Archived modules may not always be available
    pass

__all__ = ["current", "archived"]