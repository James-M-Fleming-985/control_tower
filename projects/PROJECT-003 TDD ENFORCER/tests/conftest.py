"""
Pytest configuration for PROJECT-003 TDD ENFORCER tests.
Adds workspace root to sys.path for src imports.
"""
import sys
from pathlib import Path

# Add workspace root to Python path to allow 'from src.ui...' imports
workspace_root = Path(__file__).parent.parent.parent.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))
