"""UI Components Package"""
import sys
from pathlib import Path

# Add src directory to path
src_dir = str(Path(__file__).parent.parent.parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
