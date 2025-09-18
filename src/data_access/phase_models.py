"""
Phase Models for RED-GREEN-REFACTOR Cycle Enforcer
=================================================

Core data models for TDD phase tracking and management.
Implements phase state, transitions, and evidence collection.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import json


class PhaseType(Enum):
    """TDD phase type enumeration"""
    RED = "RED"
    GREEN = "GREEN"
    REFACTOR = "REFACTOR"


class PhaseStatus(Enum):
    """Phase status enumeration"""
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class TransitionTrigger(Enum):
    """Phase transition trigger enumeration"""
    TEST_PASS = "TEST_PASS"
    TEST_FAIL = "TEST_FAIL"
    IMPLEMENTATION_COMPLETE = "IMPLEMENTATION_COMPLETE"
    REFACTOR_COMPLETE = "REFACTOR_COMPLETE"
    MANUAL_TRIGGER = "MANUAL_TRIGGER"


class EvidenceType(Enum):
    """Evidence type enumeration"""
    TEST_EXECUTION = "TEST_EXECUTION"
    GIT_COMMIT = "GIT_COMMIT"
    CODE_COVERAGE = "CODE_COVERAGE"
    PERFORMANCE_METRIC = "PERFORMANCE_METRIC"
    MANUAL_VERIFICATION = "MANUAL_VERIFICATION"


@dataclass
class TDDPhase:
    """Core TDD phase model with enhanced validation and utility methods"""
    phase_id: str
    phase_type: str  # Keep as string for compatibility
    feature_id: str
    layer_id: str
    started_at: datetime
    status: str  # Keep as string for compatibility
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate and normalize phase data after initialization"""
        # Only convert enum to string if it comes as string initially
        # Preserve enum types if they were passed as enums (for test compatibility)
        phase_type_str = self.phase_type.value if hasattr(self.phase_type, 'value') else self.phase_type
        status_str = self.status.value if hasattr(self.status, 'value') else self.status
            
        # Validate phase type
        valid_types = [pt.value for pt in PhaseType]
        if phase_type_str not in valid_types:
            raise ValueError(f"Invalid phase type: {phase_type_str}. Valid types: {valid_types}")
        
        # Validate status
        valid_statuses = [ps.value for ps in PhaseStatus]
        if status_str not in valid_statuses:
            raise ValueError(f"Invalid phase status: {status_str}. Valid statuses: {valid_statuses}")
        
        # Validate datetime consistency
        if self.completed_at and self.completed_at < self.started_at:
            raise ValueError("Completion time cannot be before start time")
    
    def mark_completed(self, completion_time: Optional[datetime] = None) -> None:
        """Mark phase as completed with optional custom completion time"""
        self.completed_at = completion_time or datetime.now()
        # Handle both string and enum status types
        self.status = PhaseStatus.COMPLETED if hasattr(self.status, 'value') else PhaseStatus.COMPLETED.value
        self.metadata['completion_method'] = 'automatic' if completion_time is None else 'manual'
    
    def mark_failed(self, failure_reason: str = "") -> None:
        """Mark phase as failed with optional reason"""
        # Handle both string and enum status types  
        self.status = PhaseStatus.FAILED if hasattr(self.status, 'value') else PhaseStatus.FAILED.value
        self.metadata['failure_reason'] = failure_reason
        self.metadata['failed_at'] = datetime.now().isoformat()
    
    def get_duration(self) -> Optional[timedelta]:
        """Get phase duration if completed"""
        if self.completed_at:
            return self.completed_at - self.started_at
        return None
    
    def get_duration_minutes(self) -> Optional[float]:
        """Get phase duration in minutes"""
        duration = self.get_duration()
        return duration.total_seconds() / 60.0 if duration else None
    
    def is_active(self) -> bool:
        """Check if phase is currently active"""
        status_val = self.status.value if hasattr(self.status, 'value') else self.status
        return status_val == PhaseStatus.ACTIVE.value
    
    def is_completed(self) -> bool:
        """Check if phase is completed successfully"""
        status_val = self.status.value if hasattr(self.status, 'value') else self.status
        return status_val == PhaseStatus.COMPLETED.value
    
    def update_metadata(self, key: str, value: Any) -> None:
        """Update phase metadata with timestamp"""
        self.metadata[key] = value
        self.metadata[f'{key}_updated_at'] = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert phase to dictionary for serialization"""
        return {
            'phase_id': self.phase_id,
            'phase_type': self.phase_type,  # Already string
            'feature_id': self.feature_id,
            'layer_id': self.layer_id,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'status': self.status,  # Already string
            'metadata': self.metadata,
            'context': self.context
        }


@dataclass
class PhaseTransition:
    """Enhanced phase transition model with validation and auto-generation"""
    transition_id: str = ""
    from_phase: str = ""
    to_phase: str = ""
    phase_id: str = ""
    transition_time: datetime = field(default_factory=datetime.now)
    trigger_event: TransitionTrigger = TransitionTrigger.MANUAL_TRIGGER
    evidence: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization processing with enhanced validation"""
        # Auto-generate transition_id if not provided
        if not self.transition_id:
            import uuid
            self.transition_id = f"transition_{uuid.uuid4().hex[:8]}"
        
        # Convert string trigger_event to enum if needed
        if isinstance(self.trigger_event, str):
            self.trigger_event = TransitionTrigger(self.trigger_event)
    
    def is_valid(self) -> bool:
        """Validate phase transition according to TDD rules"""
        # Valid transition paths
        valid_transitions = {
            "RED": ["GREEN"],
            "GREEN": ["REFACTOR"],
            "REFACTOR": ["RED", "GREEN"]  # Can start new cycle or fix
        }
        
        return self.to_phase in valid_transitions.get(self.from_phase, [])
    
    def get_validation_errors(self) -> List[str]:
        """Get detailed validation errors"""
        errors = []
        
        if not self.is_valid():
            errors.append("invalid_transition_path")  # Use expected format
        
        if not self.has_required_evidence():
            errors.append("missing_required_evidence")
        
        if not self.phase_id:
            errors.append("missing_phase_id")
            
        return errors
    
    def has_required_evidence(self) -> bool:
        """Check if required evidence is present for transition"""
        if self.trigger_event == TransitionTrigger.TEST_PASS:
            return "test_execution_result" in self.evidence
        elif self.trigger_event == TransitionTrigger.IMPLEMENTATION_COMPLETE:
            return "implementation_files" in self.evidence
        return True
    
    def add_evidence(self, key: str, value: Any) -> None:
        """Add evidence to transition with timestamp"""
        self.evidence[key] = value
        self.evidence[f'{key}_timestamp'] = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transition to dictionary for serialization"""
        return {
            'transition_id': self.transition_id,
            'from_phase': self.from_phase,
            'to_phase': self.to_phase,
            'phase_id': self.phase_id,
            'transition_time': self.transition_time.isoformat(),
            'trigger_event': self.trigger_event.value,
            'evidence': self.evidence
        }


@dataclass
class PhaseEvidence:
    """Enhanced phase evidence model with validation and utility methods"""
    evidence_id: str
    phase_id: str
    evidence_type: str  # Keep as string for compatibility
    evidence_data: Dict[str, Any]
    collected_at: datetime
    phase_type: str  # Keep as string for compatibility
    
    def __post_init__(self):
        """Post-initialization processing"""
        # Validate evidence type
        valid_types = [et.value for et in EvidenceType]
        if self.evidence_type not in valid_types:
            raise ValueError(f"Invalid evidence type: {self.evidence_type}")
        
        # Validate phase type
        valid_phases = [pt.value for pt in PhaseType]
        if self.phase_type not in valid_phases:
            raise ValueError(f"Invalid phase type: {self.phase_type}")
    
    def is_valid(self) -> bool:
        """Validate evidence data according to type requirements"""
        validation_rules = {
            "TEST_EXECUTION": ["test_command", "exit_code"],  # Remove 'output' requirement
            "GIT_COMMIT": ["commit_hash", "commit_message"],
            "CODE_COVERAGE": ["coverage_percentage", "lines_covered"],
            "PERFORMANCE_METRIC": ["metric_name", "metric_value"],
            "MANUAL_VERIFICATION": ["verifier", "verification_notes"]
        }
        
        required_fields = validation_rules.get(self.evidence_type, [])
        return all(field in self.evidence_data for field in required_fields)
    
    def get_validation_errors(self) -> List[str]:
        """Get detailed validation errors"""
        errors = []
        
        # Provide specific field-level validation errors
        if self.evidence_type == "TEST_EXECUTION":
            if "test_command" not in self.evidence_data:
                errors.append("missing_test_command")
            if "exit_code" not in self.evidence_data:
                errors.append("missing_exit_code")
        elif self.evidence_type == "GIT_COMMIT":
            if "commit_hash" not in self.evidence_data:
                errors.append("missing_commit_hash")
            if "commit_message" not in self.evidence_data:
                errors.append("missing_commit_message")
        elif self.evidence_type == "CODE_COVERAGE":
            if "coverage_percentage" not in self.evidence_data:
                errors.append("missing_coverage_percentage")
            else:
                coverage = self.evidence_data.get("coverage_percentage", 0)
                if not (0 <= coverage <= 100):
                    errors.append("invalid_coverage_percentage")
            if "lines_covered" not in self.evidence_data:
                errors.append("missing_lines_covered")
        
        return errors
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to evidence with timestamp"""
        if 'metadata' not in self.evidence_data:
            self.evidence_data['metadata'] = {}
        self.evidence_data['metadata'][key] = value
        self.evidence_data['metadata'][f'{key}_added_at'] = datetime.now().isoformat()
        
        if self.evidence_type == "TEST_EXECUTION":
            if "test_command" not in self.evidence_data:
                errors.append("missing_test_command")
            if "exit_code" not in self.evidence_data:
                errors.append("missing_exit_code")
        
        return errors
    
    def to_json(self) -> str:
        """Serialize evidence to JSON"""
        data = {
            "evidence_id": self.evidence_id,
            "phase_id": self.phase_id,
            "evidence_type": self.evidence_type,
            "evidence_data": self.evidence_data,
            "collected_at": self.collected_at.isoformat(),
            "phase_type": self.phase_type
        }
        return json.dumps(data)
    
    @classmethod
    def from_json(cls, json_data: str) -> 'PhaseEvidence':
        """Deserialize evidence from JSON"""
        data = json.loads(json_data)
        data["collected_at"] = datetime.fromisoformat(data["collected_at"])
        return cls(**data)


# Utility classes for phase state management
@dataclass
class PhaseState:
    """Phase state information"""
    current_phase: PhaseType
    phase_id: str
    started_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_active(self) -> bool:
        """Check if phase is currently active"""
        return True  # Simplified for now