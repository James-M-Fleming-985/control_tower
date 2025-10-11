"""
Orchestrator Layer
Coordinates TDD cycle execution for AI code generation.
"""
import sys
from pathlib import Path

# Add control_tower root to sys.path for AI provider import
# This must happen before importing ai_code_generator_orchestrator
control_tower_root = Path(__file__).parent.parent.parent.parent.parent.parent
if str(control_tower_root) not in sys.path:
    sys.path.insert(0, str(control_tower_root))

# Import using relative import (since we're in src/layer/orchestrator/)
from .ai_code_generator_orchestrator import AICodeGeneratorOrchestrator

__all__ = ['AICodeGeneratorOrchestrator']
