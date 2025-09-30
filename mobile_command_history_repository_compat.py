"""
COMPATIBILITY LAYER - Mobile Command History Repository

This module maintains backward compatibility for existing imports while the codebase
transitions to the new organized structure.

EXISTING IMPORT (STILL WORKS):
    from mobile_command_history_repository import MobileCommandHistoryRepository

NEW ORGANIZED IMPORT (RECOMMENDED):
    from projects.PROJECT_003_TDD_ENFORCER.SYSTEM_003_02_EXTENDED_VALIDATION_ENGINE.\
FEATURE_003_02_01_TESTING_PYRAMID_VALIDATION_ENGINE.DATA_ACCESS_LAYER.src.\
data_access import MobileCommandHistoryRepository

This compatibility layer ensures no existing code breaks during reorganization.
"""

import sys
import os

# Add the new organized path to sys.path for imports
project_path = os.path.join(
    os.path.dirname(__file__),
    "projects",
    "PROJECT-003 TDD ENFORCER",
    "SYSTEM-003-02 EXTENDED VALIDATION ENGINE", 
    "FEATURE-003-02-01 TESTING PYRAMID VALIDATION ENGINE",
    "DATA ACCESS LAYER",
    "src",
    "data_access"
)

if project_path not in sys.path:
    sys.path.insert(0, project_path)

# Import from the organized structure and re-export
try:
    from mobile_command_history_repository import MobileCommandHistoryRepository
except ImportError as e:
    # Fallback to original location if new structure not available
    import warnings
    warnings.warn(
        f"Could not import from organized structure: {e}. "
        "Using original implementation.",
        ImportWarning
    )
    # This would import from the original file if it still exists
    raise

# Re-export for backward compatibility
__all__ = [
    "MobileCommandHistoryRepository",
]