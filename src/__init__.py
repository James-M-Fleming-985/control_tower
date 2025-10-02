"""Source Package"""
import sys
from pathlib import Path

# Add src/ui/components to path for mobile_ui_components import
components_dir = str(Path(__file__).parent / 'ui' / 'components')
if components_dir not in sys.path:
    sys.path.insert(0, components_dir)
