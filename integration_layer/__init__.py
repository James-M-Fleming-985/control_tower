"""
TDD Enforcer Integration Layer
==============================

Simple facade pattern implementation that hides the complexity of 41 business logic classes
behind a simple 4-method interface.

Main class: TDDIntegration
- verify_tests(test_files: List[str]) -> bool
- check_stage_gate(phase: str) -> bool  
- get_compliance_score() -> int
- run_quality_check() -> Dict[str, Any]

Usage:
    from integration_layer import TDDIntegration
    
    tdd = TDDIntegration()
    result = tdd.verify_tests(["test_file.py"])
    gate_ok = tdd.check_stage_gate("RED")
    score = tdd.get_compliance_score()
    quality = tdd.run_quality_check()
"""

from .tdd_integration import TDDIntegration

__all__ = ['TDDIntegration']
__version__ = '1.0.0'