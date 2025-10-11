"""
Pytest configuration to set up sys.path before any imports
"""
import sys
from pathlib import Path

# Get to control_tower root
# From tests/conftest.py: up to tests/ (parent) -> SYSTEM-004-01/ (parent) -> PROJECT-004/ (parent) -> projects/ (parent) -> control_tower/ (parent)
# That's 5 levels: .parent.parent.parent.parent.parent
control_tower_root = Path(__file__).parent.parent.parent.parent.parent
control_tower_root = control_tower_root.resolve()  # Make it absolute

# Force add to sys.path at module load time
if str(control_tower_root) not in sys.path:
    sys.path.insert(0, str(control_tower_root))
else:
    # Even if it's there, make sure it's first
    sys.path.remove(str(control_tower_root))
    sys.path.insert(0, str(control_tower_root))

print(f"✅ conftest.py: Ensured {control_tower_root} is first in sys.path")
print(f"   sys.path[0]: {sys.path[0]}")

def pytest_configure(config):
    """
    Pytest hook that runs very early - ensure control_tower is in sys.path
    """
    if str(control_tower_root) not in sys.path:
        sys.path.insert(0, str(control_tower_root))
    elif sys.path[0] != str(control_tower_root):
        sys.path.remove(str(control_tower_root))
        sys.path.insert(0, str(control_tower_root))
    print(f"✅ pytest_configure: control_tower_root at sys.path[0]")
