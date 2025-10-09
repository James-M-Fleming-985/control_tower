"""
Configuration for pytest in SYSTEM-004-01 AI CODE GENERATION SYSTEM
"""
import sys
from pathlib import Path

# Add the system root to Python path to allow 'from src...' imports
system_root = Path(__file__).parent
if str(system_root) not in sys.path:
    sys.path.insert(0, str(system_root))

print(f"✅ Added SYSTEM-004-01 root to sys.path: {system_root}")
