"""
Git Checkpoint Models for RED-GREEN-REFACTOR Cycle Enforcer
==========================================================

Models for git checkpoint management and git operations tracking.
Supports TDD phase-based git workflow with checkpoints and metadata.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import json


class CheckpointStatus(Enum):
    """Checkpoint status enumeration"""
    PENDING = "PENDING"
    CREATED = "CREATED"
    FAILED = "FAILED"
    RESTORED = "RESTORED"


class OperationType(Enum):
    """Git operation type enumeration"""
    COMMIT = "COMMIT"
    BRANCH = "BRANCH"
    MERGE = "MERGE"
    CHECKOUT = "CHECKOUT"
    RESTORE = "RESTORE"


@dataclass
class CheckpointMetadata:
    """Git checkpoint metadata"""
    feature_id: str
    layer_id: str
    test_status: str
    files_changed: List[str]
    code_coverage: float = 0.0
    test_results: Dict[str, Any] = field(default_factory=dict)
    
    def is_valid_for_phase(self, phase_type: str) -> bool:
        """Validate metadata for specific phase"""
        if phase_type == "RED":
            return self.test_status == "FAILING"
        elif phase_type == "GREEN":
            return self.test_status == "PASSING"
        return True
    
    def get_validation_errors(self, phase_type: str) -> List[str]:
        """Get validation errors for phase"""
        errors = []
        
        if phase_type == "GREEN" and self.test_status != "PASSING":
            errors.append("tests_must_pass_for_green")
        
        return errors


@dataclass
class GitCheckpoint:
    """Git checkpoint model"""
    checkpoint_id: str
    phase_id: str
    phase_type: str
    commit_hash: Optional[str]
    branch_name: str
    checkpoint_time: datetime
    metadata: CheckpointMetadata
    status: CheckpointStatus = CheckpointStatus.PENDING
    
    def __post_init__(self):
        """Post-initialization processing"""
        if isinstance(self.status, str):
            # Convert string to enum if needed
            self.status = CheckpointStatus(self.status)


@dataclass
class GitOperation:
    """Git operation model"""
    operation_id: str
    operation_type: OperationType
    checkpoint_id: str
    command: str
    result: Dict[str, Any]
    executed_at: datetime
    execution_time_ms: int
    
    def was_successful(self) -> bool:
        """Check if operation was successful"""
        return self.result.get("success", False)
    
    def __post_init__(self):
        """Post-initialization processing"""
        if isinstance(self.operation_type, str):
            self.operation_type = OperationType(self.operation_type)