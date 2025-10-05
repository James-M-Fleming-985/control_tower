"""
Root conftest.py for pytest configuration.
Adds workspace root to sys.path for all tests.
"""
import sys
from pathlib import Path

# Add workspace root to Python path to allow 'from src.ui...' imports
workspace_root = Path(__file__).parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

print(f"✅ Added {workspace_root} to sys.path")
