#!/usr/bin/env python3
"""
Integration Layer - Data Models

Data models and structures for LAYER-003-01-02-004: Integration Layer
GREEN phase model definitions.

Created: 2025-09-18
Phase: TDD GREEN phase - Data models
Target: Support Integration Layer functionality
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Union
from enum import Enum
import time


class WorkflowPhase(Enum):
    """TDD workflow phases"""
    RED = "red"
    GREEN = "green"
    REFACTOR = "refactor"
    COMPLETE = "complete"


class StageGateResult(Enum):
    """Stage gate evaluation results"""
    PROCEED = "PROCEED"
    BLOCKED = "BLOCKED"
    PENDING = "PENDING"
    ERROR = "ERROR"


class IntegrationStatus(Enum):
    """Integration operation status"""
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    PENDING = "PENDING"
    TIMEOUT = "TIMEOUT"


@dataclass
class WorkflowEvent:
    """
    Workflow event data structure for event-driven coordination
    """
    event_id: str
    event_type: str
    workflow_id: str
    timestamp: float
    event_data: Dict[str, Any]
    source_system: Optional[str] = None
    target_system: Optional[str] = None
    priority: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "workflow_id": self.workflow_id,
            "timestamp": self.timestamp,
            "event_data": self.event_data,
            "source_system": self.source_system,
            "target_system": self.target_system,
            "priority": self.priority
        }


@dataclass
class StageGateStatus:
    """
    Stage gate status information for workflow blocking
    """
    stage: str
    status: StageGateResult
    can_proceed: bool
    blocking_reasons: List[str]
    verification_id: str
    evaluation_timestamp: float = None
    retry_count: int = 0
    
    def __post_init__(self):
        if self.evaluation_timestamp is None:
            self.evaluation_timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "stage": self.stage,
            "status": self.status.value if isinstance(self.status, StageGateResult) else self.status,
            "can_proceed": self.can_proceed,
            "blocking_reasons": self.blocking_reasons,
            "verification_id": self.verification_id,
            "evaluation_timestamp": self.evaluation_timestamp,
            "retry_count": self.retry_count
        }


@dataclass
class IntegrationResult:
    """
    Integration operation result with comprehensive details
    """
    integration_successful: bool
    integration_id: str
    timestamp: float
    details: Dict[str, Any]
    status: IntegrationStatus = IntegrationStatus.SUCCESS
    error_message: Optional[str] = None
    performance_metrics: Optional[Dict[str, float]] = None
    
    def __post_init__(self):
        if self.performance_metrics is None:
            self.performance_metrics = {}
        
        # Set status based on success
        if self.integration_successful:
            self.status = IntegrationStatus.SUCCESS
        else:
            self.status = IntegrationStatus.FAILURE
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "integration_successful": self.integration_successful,
            "integration_id": self.integration_id,
            "timestamp": self.timestamp,
            "details": self.details,
            "status": self.status.value if isinstance(self.status, IntegrationStatus) else self.status,
            "error_message": self.error_message,
            "performance_metrics": self.performance_metrics
        }


@dataclass
class ExternalSystemConfig:
    """
    External system configuration for API integration
    """
    system_name: str
    endpoint: str
    authentication: Dict[str, Any]
    timeout: float
    retry_config: Optional[Dict[str, Any]] = None
    health_check_endpoint: Optional[str] = None
    rate_limit: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.retry_config is None:
            self.retry_config = {
                "max_retries": 3,
                "backoff_factor": 2.0,
                "retry_on_status": [500, 502, 503, 504]
            }
        
        if self.rate_limit is None:
            self.rate_limit = {
                "requests_per_second": 10,
                "burst_limit": 50
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "system_name": self.system_name,
            "endpoint": self.endpoint,
            "authentication": self.authentication,
            "timeout": self.timeout,
            "retry_config": self.retry_config,
            "health_check_endpoint": self.health_check_endpoint,
            "rate_limit": self.rate_limit
        }


@dataclass
class WorkflowState:
    """
    Workflow state representation for state management
    """
    workflow_id: str
    current_phase: WorkflowPhase
    phase_progress: float
    stage_gate_status: str
    external_system_states: Dict[str, Any]
    start_timestamp: float = None
    last_update_timestamp: float = None
    completion_timestamp: Optional[float] = None
    
    def __post_init__(self):
        if self.start_timestamp is None:
            self.start_timestamp = time.time()
        if self.last_update_timestamp is None:
            self.last_update_timestamp = time.time()
    
    def update_progress(self, progress: float, phase: Optional[WorkflowPhase] = None):
        """Update workflow progress"""
        self.phase_progress = progress
        if phase is not None:
            self.current_phase = phase
        self.last_update_timestamp = time.time()
    
    def mark_complete(self):
        """Mark workflow as complete"""
        self.current_phase = WorkflowPhase.COMPLETE
        self.phase_progress = 100.0
        self.completion_timestamp = time.time()
        self.last_update_timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "workflow_id": self.workflow_id,
            "current_phase": self.current_phase.value if isinstance(self.current_phase, WorkflowPhase) else self.current_phase,
            "phase_progress": self.phase_progress,
            "stage_gate_status": self.stage_gate_status,
            "external_system_states": self.external_system_states,
            "start_timestamp": self.start_timestamp,
            "last_update_timestamp": self.last_update_timestamp,
            "completion_timestamp": self.completion_timestamp
        }


@dataclass
class SystemEventOrder:
    """
    Event ordering configuration for external system coordination
    """
    system: str
    event: str
    order: int
    dependencies: List[str] = None
    timeout: float = 5.0
    retry_on_failure: bool = True
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "system": self.system,
            "event": self.event,
            "order": self.order,
            "dependencies": self.dependencies,
            "timeout": self.timeout,
            "retry_on_failure": self.retry_on_failure
        }


@dataclass
class CoordinationRequest:
    """
    Coordination request for multi-system synchronization
    """
    coordination_id: str
    systems: List[str]
    event_sequence: List[SystemEventOrder]
    synchronization_timeout: float = 10.0
    failure_strategy: str = "abort"  # abort, continue, retry
    priority: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "coordination_id": self.coordination_id,
            "systems": self.systems,
            "event_sequence": [event.to_dict() for event in self.event_sequence],
            "synchronization_timeout": self.synchronization_timeout,
            "failure_strategy": self.failure_strategy,
            "priority": self.priority
        }


@dataclass
class PerformanceMetrics:
    """
    Performance metrics for integration operations
    """
    operation_id: str
    start_time: float
    end_time: float
    duration: float = None
    throughput: Optional[float] = None
    error_rate: float = 0.0
    success_rate: float = 100.0
    
    def __post_init__(self):
        if self.duration is None:
            self.duration = self.end_time - self.start_time
    
    def calculate_throughput(self, operation_count: int) -> float:
        """Calculate operations per second"""
        if self.duration > 0:
            self.throughput = operation_count / self.duration
        return self.throughput or 0.0
    
    def update_rates(self, total_operations: int, failed_operations: int):
        """Update success and error rates"""
        if total_operations > 0:
            self.error_rate = (failed_operations / total_operations) * 100
            self.success_rate = ((total_operations - failed_operations) / total_operations) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "operation_id": self.operation_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "throughput": self.throughput,
            "error_rate": self.error_rate,
            "success_rate": self.success_rate
        }


@dataclass  
class SecurityConfiguration:
    """
    Security configuration for external system authentication
    """
    api_key: str
    encryption: str
    authentication_method: str
    secure_transmission: bool
    certificate_path: Optional[str] = None
    token_refresh_interval: int = 3600  # 1 hour default
    
    def validate(self) -> Dict[str, Any]:
        """Validate security configuration"""
        validation_result = {
            "authentication_valid": bool(self.api_key and self.authentication_method),
            "encryption_enabled": self.encryption == "AES256",
            "transmission_secure": self.secure_transmission,
            "security_level": "high"
        }
        
        # Determine security level
        security_checks = [
            validation_result["authentication_valid"],
            validation_result["encryption_enabled"],
            validation_result["transmission_secure"]
        ]
        
        if all(security_checks):
            validation_result["security_level"] = "high"
        elif sum(security_checks) >= 2:
            validation_result["security_level"] = "medium"
        else:
            validation_result["security_level"] = "low"
        
        return validation_result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excluding sensitive data)"""
        return {
            "api_key": "***REDACTED***",
            "encryption": self.encryption,
            "authentication_method": self.authentication_method,
            "secure_transmission": self.secure_transmission,
            "certificate_path": self.certificate_path,
            "token_refresh_interval": self.token_refresh_interval
        }