"""
Feature Integration Module for Failure Handling and Recovery System
FEATURE ID: FEATURE-003-03-03

This module orchestrates the interaction between:
- Violation Detector (LAYER-003-03-03-01)
- Remediation Generator (LAYER-003-03-03-02)
- Recovery State Manager (LAYER-003-03-03-03)
"""

from pathlib import Path
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import from Violation Detector Layer
from LAYER_003_03_03_01.src.implementation import (
    ViolationType,
    Severity,
    Violation,
    ViolationDetector
)

# Import from Remediation Generator Layer
from LAYER_003_03_03_02.src.implementation import (
    RemediationActionType,
    RemediationOption,
    RemediationGenerator
)

# Import from Recovery State Manager Layer
from LAYER_003_03_03_03.src.implementation import (
    RecoveryStateManager
)


class FeatureStatus(Enum):
    """Status of feature operations."""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    ERROR = "error"


@dataclass
class FeatureConfig:
    """Configuration for the Failure Handling and Recovery System."""
    auto_remediation: bool = True
    max_remediation_attempts: int = 3
    severity_threshold: Optional[Severity] = None
    enable_state_persistence: bool = True
    violation_detection_enabled: bool = True
    remediation_generation_enabled: bool = True
    recovery_state_tracking_enabled: bool = True
    
    def __post_init__(self):
        """Validate configuration parameters."""
        if self.max_remediation_attempts < 1:
            raise ValueError("max_remediation_attempts must be at least 1")


@dataclass
class FeatureResponse:
    """Unified response structure for feature operations."""
    status: FeatureStatus
    message: str
    violations: List[Violation] = field(default_factory=list)
    remediations: Dict[str, List[RemediationOption]] = field(default_factory=dict)
    recovery_state: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def add_error(self, error: str) -> None:
        """Add an error message to the response."""
        self.errors.append(error)
        if self.status == FeatureStatus.SUCCESS:
            self.status = FeatureStatus.PARTIAL_SUCCESS
    
    def has_errors(self) -> bool:
        """Check if response contains errors."""
        return len(self.errors) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            "status": self.status.value,
            "message": self.message,
            "violations": [
                {
                    "id": v.violation_id,
                    "type": v.violation_type.value,
                    "severity": v.severity.value,
                    "message": v.message,
                    "context": v.context
                }
                for v in self.violations
            ],
            "remediations": {
                vid: [
                    {
                        "action_type": opt.action_type.value,
                        "description": opt.description,
                        "priority": opt.priority,
                        "estimated_effort": opt.estimated_effort
                    }
                    for opt in options
                ]
                for vid, options in self.remediations.items()
            },
            "recovery_state": self.recovery_state,
            "errors": self.errors,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


class FeatureOrchestrator:
    """
    Main orchestrator for the Failure Handling and Recovery System.
    
    This class coordinates the interaction between violation detection,
    remediation generation, and recovery state management layers.
    """
    
    def __init__(self, config: Optional[FeatureConfig] = None):
        """
        Initialize the feature orchestrator.
        
        Args:
            config: Optional configuration for the feature
            
        Raises:
            RuntimeError: If layer initialization fails
        """
        self.config = config or FeatureConfig()
        self._initialize_layers()
    
    def _initialize_layers(self) -> None:
        """
        Initialize all layer components.
        
        Raises:
            RuntimeError: If any layer fails to initialize
        """
        try:
            # Initialize Violation Detector
            if self.config.violation_detection_enabled:
                self.violation_detector = ViolationDetector()
            else:
                self.violation_detector = None
            
            # Initialize Remediation Generator
            if self.config.remediation_generation_enabled:
                self.remediation_generator = RemediationGenerator()
            else:
                self.remediation_generator = None
            
            # Initialize Recovery State Manager
            if self.config.recovery_state_tracking_enabled:
                self.recovery_state_manager = RecoveryStateManager()
            else:
                self.recovery_state_manager = None
                
        except Exception as e:
            raise RuntimeError(f"Failed to initialize feature layers: {str(e)}")
    
    def detect_and_handle_violations(
        self,
        context: Dict[str, Any],
        auto_remediate: Optional[bool] = None
    ) -> FeatureResponse:
        """
        Detect violations and optionally generate remediations.
        
        Args:
            context: Context information for violation detection
            auto_remediate: Override config auto_remediation setting
            
        Returns:
            FeatureResponse with detection and remediation results
        """
        auto_remediate = auto_remediate if auto_remediate is not None else self.config.auto_remediation
        
        response = FeatureResponse(
            status=FeatureStatus.SUCCESS,
            message="Violation detection completed",
            metadata={"auto_remediate": auto_remediate}
        )
        
        try:
            # Step 1: Detect violations
            violations = self._detect_violations(context)
            response.violations = violations
            
            if not violations:
                response.message = "No violations detected"
                return response
            
            # Step 2: Filter by severity threshold if configured
            if self.config.severity_threshold:
                violations = self._filter_by_severity(violations)
                response.metadata["filtered_count"] = len(violations)
            
            # Step 3: Generate remediations if enabled
            if auto_remediate and violations:
                remediations = self._generate_remediations(violations)
                response.remediations = remediations
                response.message = f"Detected {len(violations)} violations with remediations"
            else:
                response.message = f"Detected {len(violations)} violations"
            
            # Step 4: Update recovery state
            if self.config.recovery_state_tracking_enabled:
                self._update_recovery_state(violations, response.remediations)
                response.recovery_state = self._get_recovery_state_summary()
            
        except Exception as e:
            response.status = FeatureStatus.ERROR
            response.add_error(f"Error during violation handling: {str(e)}")
        
        return response
    
    def _detect_violations(self, context: Dict[str, Any]) -> List[Violation]:
        """
        Detect violations using the violation detector layer.
        
        Args:
            context: Context for violation detection
            
        Returns:
            List of detected violations
        """
        if not self.violation_detector:
            return []
        
        violations = []
        
        # Check for various violation types based on context
        if "code" in context:
            violation = self.violation_detector.check_code_violation(
                context["code"],
                context.get("rules", [])
            )
            if violation:
                violations.append(violation)
        
        if "test_results" in context:
            violation = self.violation_detector.check_test_violation(
                context["test_results"]
            )
            if violation:
                violations.append(violation)
        
        if "workflow_state" in context:
            violation = self.violation_detector.check_workflow_violation(
                context["workflow_state"]
            )
            if violation:
                violations.append(violation)
        
        return violations
    
    def _filter_by_severity(self, violations: List[Violation]) -> List[Violation]:
        """
        Filter violations by severity threshold.
        
        Args:
            violations: List of violations to filter
            
        Returns:
            Filtered list of violations
        """
        if not self.config.severity_threshold:
            return violations
        
        severity_order = {
            Severity.LOW: 1,
            Severity.MEDIUM: 2,
            Severity.HIGH: 3,
            Severity.CRITICAL: 4
        }
        
        threshold_level = severity_order.get(self.config.severity_threshold, 0)
        
        return [
            v for v in violations
            if severity_order.get(v.severity, 0) >= threshold_level
        ]
    
    def _generate_remediations(
        self,
        violations: List[Violation]
    ) -> Dict[str, List[RemediationOption]]:
        """
        Generate remediations for detected violations.
        
        Args:
            violations: List of violations to remediate
            
        Returns:
            Dictionary mapping violation IDs to remediation options
        """
        if not self.remediation_generator:
            return {}
        
        remediations = {}
        
        for violation in violations:
            try:
                options = self.remediation_generator.generate_remediation(
                    violation.violation_type,
                    violation.context
                )
                remediations[violation.violation_id] = options
            except Exception as e:
                # Continue processing other violations
                remediations[violation.violation_id] = []
        
        return remediations
    
    def _update_recovery_state(
        self,
        violations: List[Violation],
        remediations: Dict[str, List[RemediationOption]]
    ) -> None:
        """
        Update recovery state with current violations and remediations.
        
        Args:
            violations: List of detected violations
            remediations: Dictionary of remediation options
        """
        if not self.recovery_state_manager:
            return
        
        for violation in violations:
            self.recovery_state_manager.record_violation(
                violation.violation_id,
                violation.violation_type,
                violation.severity
            )
            
            if violation.violation_id in remediations:
                for option in remediations[violation.violation_id]:
                    self.recovery_state_manager.record_remediation_attempt(
                        violation.violation_id,
                        option.action_type
                    )
    
    def _get_recovery_state_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current recovery state.
        
        Returns:
            Dictionary containing recovery state summary
        """
        if not self.recovery_state_manager:
            return {}
        
        return self.recovery_state_manager.get_state_summary()
    
    def apply_remediation(
        self,
        violation_id: str,
        remediation_option: RemediationOption
    ) -> FeatureResponse:
        """
        Apply a specific remediation option to a violation.
        
        Args:
            violation_id: ID of the violation to remediate
            remediation_option: The remediation option to apply
            
        Returns:
            FeatureResponse with application results
        """
        response = FeatureResponse(
            status=FeatureStatus.SUCCESS,
            message=f"Remediation applied for violation {violation_id}",
            metadata={
                "violation_id": violation_id,
                "action_type": remediation_option.action_type.value
            }
        )
        
        try:
            # Record the remediation attempt
            if self.recovery_state_manager:
                success = self.recovery_state_manager.record_remediation_attempt(
                    violation_id,
                    remediation_option.action_type
                )
                
                if not success:
                    response.status = FeatureStatus.FAILURE
                    response.add_error("Failed to record remediation attempt")
                
                response.recovery_state = self._get_recovery_state_summary()
            
        except Exception as e:
            response.status = FeatureStatus.ERROR
            response.add_error(f"Error applying remediation: {str(e)}")
        
        return response
    
    def get_violation_summary(self) -> FeatureResponse:
        """
        Get a summary of all violations and their remediation status.
        
        Returns:
            FeatureResponse with violation summary
        """
        response = FeatureResponse(
            status=FeatureStatus.SUCCESS,
            message="Violation summary retrieved"
        )
        
        try:
            if self.recovery_state_manager:
                summary = self.recovery_state_manager.get_state_summary()
                response.recovery_state = summary
                response.metadata["total_violations"] = summary.get("total_violations", 0)
            else:
                response.message = "Recovery state tracking not enabled"
                
        except Exception as e:
            response.status = FeatureStatus.ERROR
            response.add_error(f"Error retrieving violation summary: {str(e)}")
        
        return response
    
    def reset_recovery_state(self) -> FeatureResponse:
        """
        Reset the recovery state manager.
        
        Returns:
            FeatureResponse indicating reset status
        """
        response = FeatureResponse(
            status=FeatureStatus.SUCCESS,
            message="Recovery state reset"
        )
        
        try:
            if self.recovery_state_manager:
                self.recovery_state_manager.reset_state()
            else:
                response.message = "Recovery state tracking not enabled"
                
        except Exception as e:
            response.status = FeatureStatus.ERROR
            response.add_error(f"Error resetting recovery state: {str(e)}")
        
        return response
    
    def process_workflow_failure(
        self,
        workflow_context: Dict[str, Any],
        failure_details: Dict[str, Any]
    ) -> FeatureResponse:
        """
        Process a workflow failure end-to-end.
        
        This is a high-level method that:
        1. Detects violations from the failure
        2. Generates remediation options
        3. Updates recovery state
        4. Returns comprehensive response
        
        Args:
            workflow_context: Context of the failed workflow
            failure_details: Details about the failure
            
        Returns:
            FeatureResponse with complete failure handling results
        """
        # Combine context and failure details
        combined_context = {
            **workflow_context,
            "failure": failure_details
        }
        
        # Detect and handle violations
        response = self.detect_and_handle_violations(
            combined_context,
            auto_remediate=True
        )
        
        # Add failure-specific metadata
        response.metadata.update({
            "failure_type": failure_details.get("type", "unknown"),
            "workflow_stage": workflow_context.get("current_stage", "unknown"),
            "timestamp": datetime.now().isoformat()
        })
        
        return response
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on all layers.
        
        Returns:
            Dictionary with health status of each layer
        """
        health = {
            "feature": "Failure Handling and Recovery System",
            "status": "healthy",
            "layers": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Check Violation Detector
        health["layers"]["violation_detector"] = {
            "enabled": self.config.violation_detection_enabled,
            "initialized": self.violation_detector is not None,
            "status": "healthy" if self.violation_detector else "disabled"
        }
        
        # Check Remediation Generator
        health["layers"]["remediation_generator"] = {
            "enabled": self.config.remediation_generation_enabled,
            "initialized": self.remediation_generator is not None,
            "status": "healthy" if self.remediation_generator else "disabled"
        }
        
        # Check Recovery State Manager
        health["layers"]["recovery_state_manager"] = {
            "enabled": self.config.recovery_state_tracking_enabled,
            "initialized": self.recovery_state_manager is not None,
            "status": "healthy" if self.recovery_state_manager else "disabled"
        }
        
        # Update overall status
        all_healthy = all(
            layer["status"] in ["healthy", "disabled"]
            for layer in health["layers"].values()
        )
        health["status"] = "healthy" if all_healthy else "degraded"
        
        return health


# Convenience function for quick feature usage
def create_orchestrator(config: Optional[FeatureConfig] = None) -> FeatureOrchestrator:
    """
    Create and return a configured FeatureOrchestrator instance.
    
    Args:
        config: Optional configuration
        
    Returns:
        Initialized FeatureOrchestrator
    """
    return FeatureOrchestrator(config)


if __name__ == "__main__":
    # Example usage and basic testing
    print("Failure Handling and Recovery System - Feature Integration")
    print("=" * 60)
    
    # Create orchestrator with default config
    orchestrator = create_orchestrator()
    
    # Perform health check
    health = orchestrator.health_check()
    print(f"\nHealth Check: {health['status']}")
    for layer_name, layer_status in health['layers'].items():
        print(f"  {layer_name}: {layer_status['status']}")
    
    # Example: Process a workflow failure
    workflow_context = {
        "workflow_id": "test-workflow-001",
        "current_stage": "testing",
        "code": "def example(): pass"
    }
    
    failure_details = {
        "type": "test_failure",
        "message": "Test coverage below threshold"
    }
    
    result = orchestrator.process_workflow_failure(workflow_context, failure_details)
    print(f"\nWorkflow Failure Processing: {result.status.value}")
    print(f"Message: {result.message}")
    print(f"Violations detected: {len(result.violations)}")
    print(f"Remediations generated: {len(result.remediations)}")
    
    if result.has_errors():
        print("\nErrors:")
        for error in result.errors:
            print(f"  - {error}")