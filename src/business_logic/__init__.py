"""
Business Logic Package for FEATURE-003-01-03 RED-GREEN-REFACTOR Cycle Enforcer
==============================================================================

This package implements the core business logic for TDD cycle enforcement,
including phase validation, stage gate management, and compliance verification.
"""

from .tdd_cycle_enforcer import TDDCycleEnforcer
from .phase_enforcement import (
    RedPhaseEnforcer,
    GreenPhaseEnforcer,
    RefactorPhaseEnforcer,
    PhaseEnforcementResult
)
from .stage_gate_manager import StageGateManager, StageGateDecision
from .compliance_validator import ComplianceValidator, ComplianceResult

__all__ = [
    'TDDCycleEnforcer',
    'RedPhaseEnforcer',
    'GreenPhaseEnforcer', 
    'RefactorPhaseEnforcer',
    'PhaseEnforcementResult',
    'StageGateManager',
    'StageGateDecision',
    'ComplianceValidator',
    'ComplianceResult'
]

__version__ = '1.0.0'
__author__ = 'TDD Cycle Enforcer Team'