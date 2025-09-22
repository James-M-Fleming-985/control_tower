"""
Data Access Layer Package for RED-GREEN-REFACTOR Cycle Enforcer
==============================================================

This package provides data access functionality for TDD phase tracking,
git checkpoint management, and evidence storage.
"""

from .phase_models import (
    TDDPhase, PhaseState, PhaseTransition, PhaseEvidence,
    PhaseType, PhaseStatus, TransitionTrigger, EvidenceType
)

from .git_checkpoint_models import (
    GitCheckpoint, CheckpointMetadata, GitOperation,
    CheckpointStatus, OperationType
)

from .git_operations import (
    GitOperationsManager, GitBranchManager, GitCheckpointManager,
    GitPerformanceMonitor, GitRepositoryError
)

# Temporarily commented out due to syntax issue: 
# from .tdd_phase_repository import TDDPhaseRepository, PhaseValidator

from .phase_data_interface import PhaseDataInterface

__all__ = [
    # Phase Models
    'TDDPhase', 'PhaseState', 'PhaseTransition', 'PhaseEvidence',
    'PhaseType', 'PhaseStatus', 'TransitionTrigger', 'EvidenceType',
    
    # Git Models
    'GitCheckpoint', 'CheckpointMetadata', 'GitOperation',
    'CheckpointStatus', 'OperationType',
    
    # Git Operations
    'GitOperationsManager', 'GitBranchManager', 'GitCheckpointManager',
    'GitPerformanceMonitor', 'GitRepositoryError',
    
    # Repository
    'TDDPhaseRepository', 'PhaseValidator',
    
    # Data Interface
    'PhaseDataInterface'
]