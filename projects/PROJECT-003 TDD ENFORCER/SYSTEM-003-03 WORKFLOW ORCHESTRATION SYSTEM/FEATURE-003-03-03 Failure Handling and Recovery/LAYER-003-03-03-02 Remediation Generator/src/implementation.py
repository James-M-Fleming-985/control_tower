```python
"""Remediation Generator for Workflow Orchestration System

This module generates remediation options for workflow violations,
providing fix-and-retry and continue-with-warning options with
specific guidance for different violation types.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class RemediationActionType(Enum):
    """Types of remediation actions available."""
    FIX_AND_RETRY = "fix_and_retry"
    CONTINUE_WITH_WARNING = "continue_with_warning"
    MANUAL_INTERVENTION = "manual_intervention"
    ABORT = "abort"


@dataclass
class RemediationOption:
    """Represents a single remediation option for a violation."""
    action_type: RemediationActionType
    title: str
    description: str
    guidance: str
    auto_applicable: bool = False
    parameters: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert remediation option to dictionary format."""
        result = {
            "action_type": self.action_type.value,
            "title": self.title,
            "description": self.description,
            "guidance": self.guidance,
            "auto_applicable": self.auto_applicable
        }
        if self.parameters:
            result["parameters"] = self.parameters
        return result


class ViolationType(Enum):
    """Types of violations that can occur."""
    MISSING_DEPENDENCY = "missing_dependency"
    INVALID_INPUT = "invalid_input"
    RESOURCE_UNAVAILABLE = "resource_unavailable"
    TIMEOUT = "timeout"
    PERMISSION_DENIED = "permission_denied"
    VALIDATION_ERROR = "validation_error"
    CONSTRAINT_VIOLATION = "constraint_violation"
    UNKNOWN = "unknown"


class RemediationGenerator:
    """Generates remediation options for workflow violations."""
    
    def __init__(self):
        """Initialize the remediation generator."""
        self._violation_handlers = {
            ViolationType.MISSING_DEPENDENCY: self._handle_missing_dependency,
            ViolationType.INVALID_INPUT: self._handle_invalid_input,
            ViolationType.RESOURCE_UNAVAILABLE: self._handle_resource_unavailable,
            ViolationType.TIMEOUT: self._handle_timeout,
            ViolationType.PERMISSION_DENIED: self._handle_permission_denied,
            ViolationType.VALIDATION_ERROR: self._handle_validation_error,
            ViolationType.CONSTRAINT_VIOLATION: self._handle_constraint_violation,
        }
    
    def generate_options(self, violation: Dict[str, Any]) -> List[RemediationOption]:
        """Generate remediation options for a given violation.
        
        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation
                - message: Description of the violation
                - context: Additional context information (optional)
                
        Returns:
            List of RemediationOption objects
        """
        violation_type_str = violation.get("type", "unknown")
        try:
            violation_type = ViolationType(violation_type_str)
        except ValueError:
            violation_type = ViolationType.UNKNOWN
        
        handler = self._violation_handlers.get(
            violation_type,
            self._handle_unknown
        )
        
        return handler(violation)
    
    def format_for_presentation(self, options: List[RemediationOption]) -> Dict[str, Any]:
        """Format remediation options for presentation to user.
        
        Args:
            options: List of RemediationOption objects
            
        Returns:
            Dictionary with formatted options for UI presentation
        """
        formatted = {
            "total_options": len(options),
            "options": [opt.to_dict() for opt in options],
            "auto_applicable_count": sum(1 for opt in options if opt.auto_applicable)
        }
        
        # Group by action type
        by_type = {}
        for opt in options:
            action_type = opt.action_type.value
            if action_type not in by_type:
                by_type[action_type] = []
            by_type[action_type].append(opt.to_dict())
        
        formatted["by_action_type"] = by_type
        
        return formatted
    
    def _handle_missing_dependency(self, violation: Dict[str, Any]) -> List[RemediationOption]:
        """Handle missing dependency violations."""
        options = []
        
        context = violation.get("context", {})
        dependency_name = context.get("dependency", "required dependency")
        
        # Fix and retry option
        options.append(RemediationOption(
            action_type=RemediationActionType.FIX_AND_RETRY,
            title="Install Missing Dependency",
            description=f"Install {dependency_name} and retry the workflow",
            guidance=f"Ensure {dependency_name} is available and properly configured. "
                     f"Check version compatibility and installation requirements.",
            auto_applicable=False,
            parameters={"dependency": dependency_name}
        ))
        
        # Continue with warning option (if allowed)
        if context.get("optional", False):
            options.append(RemediationOption(
                action_type=RemediationActionType.CONTINUE_WITH_WARNING,
                title="Continue Without Dependency",
                description=f"Proceed without {dependency_name} (functionality may be limited)",
                guidance=f"{dependency_name} is optional. Continuing without it may reduce functionality.",
                auto_applicable=False,
                parameters={"skip_dependency": dependency_name}
            ))
        
        return options
    
    def _handle_invalid_input(self, violation: Dict[str, Any]) -> List[RemediationOption]:
        """Handle invalid input violations."""
        options = []
        
        context = violation.get("context", {})
        field = context.get("field", "input")
        expected = context.get("expected", "valid value")
        
        # Fix and retry option
        options.append(RemediationOption(
            action_type=RemediationActionType.FIX_AND_RETRY,
            title="Correct Input Value",
            description=f"Update {field} to a valid value and retry",
            guidance=f"The field '{field}' must be {expected}. "
                     f"Review the input validation rules and correct the value.",
            auto_applicable=False,
            parameters={"field": field, "expected": expected}
        ))
        
        # Manual intervention option
        options.append(RemediationOption(
            action_type=RemediationActionType.MANUAL_INTERVENTION,
            title="Manual Review Required",
            description=f"Review and correct {field} manually",
            guidance=f"This input requires manual review to ensure correctness. "
                     f"Consult documentation for valid values.",
            auto_applicable=False
        ))
        
        return options
    
    def _handle_resource_unavailable(self, violation: Dict[str, Any]) -> List[RemediationOption]:
        """Handle resource unavailable violations."""
        options = []
        
        context = violation.get("context", {})
        resource = context.get("resource", "resource")
        
        # Fix and retry option
        options.append(RemediationOption(
            action_type=RemediationActionType.FIX_AND_RETRY,
            title="Wait and Retry",
            description=f"Wait for {resource} to become available and retry",
            guidance=f"The resource '{resource}' is temporarily unavailable. "
                     f"Check resource status and retry when available.",
            auto_applicable=True,
            parameters={"resource": resource, "retry_delay": 30}
        ))
        
        # Continue with warning option
        options.append(RemediationOption(
            action_type=RemediationActionType.CONTINUE_WITH_WARNING,
            title="Use Alternative Resource",
            description=f"Continue using an alternative to {resource}",
            guidance=f"If an alternative resource is available, the workflow can continue. "
                     f"Results may differ from expected.",
            auto_applicable=False,
            parameters={"skip_resource": resource}
        ))
        
        return options
    
    def _handle_timeout(self, violation: Dict[str, Any]) -> List[RemediationOption]:
        """Handle timeout violations."""
        options = []
        
        context = violation.get("context", {})
        operation = context.get("operation", "operation")
        timeout = context.get("timeout", 60)
        
        # Fix and retry with increased timeout
        options.append(RemediationOption(
            action_type=RemediationActionType.FIX_AND_RETRY,
            title="Retry with Extended Timeout",
            description=f"Retry {operation} with increased timeout limit",
            guidance=f"The operation timed out after {timeout} seconds. "
                     f"Increase the timeout value and retry if the operation needs more time.",
            auto_applicable=True,
            parameters={
                "operation": operation,
                "new_timeout": timeout * 2
            }
        ))
        
        # Continue with warning option
        options.append(RemediationOption(
            action_type=RemediationActionType.CONTINUE_WITH_WARNING,
            title="Skip Timed Out Operation",
            description=f"Continue workflow without completing {operation}",
            guidance=f"Skip this operation and continue. Note that subsequent steps may fail "
                     f"if they depend on the results of this operation.",
            auto_applicable=False,
            parameters={"skip_operation": operation}
        ))
        
        return options
    
    def _handle_permission_denied(self, violation: Dict[str, Any]) -> List[RemediationOption]:
        """Handle permission denied violations."""
        options = []
        
        context = violation.get("context", {})
        resource = context.get("resource", "resource")
        required_permission = context.get("permission", "access")
        
        # Fix and retry option
        options.append(RemediationOption(
            action_type=RemediationActionType.FIX_AND_RETRY,
            title="Grant Required Permissions",
            description=f"Grant {required_permission} permission for {resource} and retry",
            guidance=f"The workflow requires {required_permission} permission for {resource}. "
                     f"Contact your administrator to grant the necessary permissions.",
            auto_applicable=False,
            parameters={
                "resource": resource,
                "permission": required_permission
            }
        ))
        
        # Manual intervention option
        options.append(RemediationOption(
            action_type=RemediationActionType.MANUAL_INTERVENTION,
            title="Administrator Intervention Required",
            description="Request administrator to complete this action",
            guidance="This action requires elevated privileges. "
                     "An administrator must complete this step manually.",
            auto_applicable=False
        ))
        
        return options
    
    def _handle_validation_error(self, violation: Dict[str, Any]) -> List[RemediationOption]:
        """Handle validation error violations."""
        options = []
        
        context = violation.get("context", {})
        field = context.get("field", "data")
        rule = context.get("rule", "validation rule")
        
        # Fix and retry option
        options.append(RemediationOption(
            action_type=RemediationActionType.FIX_AND_RETRY,
            title="Correct Validation Error",
            description=f"Fix {field} to satisfy {rule} and retry",
            guidance=f"The field '{field}' failed validation rule: {rule}. "
                     f"Review the data and correct any validation errors.",
            auto_applicable=False,
            parameters={"field": field, "rule": rule}
        ))
        
        # Continue with warning option (if non-critical)
        if context.get("severity", "high") == "low":
            options.append(RemediationOption(
                action_type=RemediationActionType.CONTINUE_WITH_WARNING,
                title="Continue Despite Validation Warning",
                description="Continue workflow with validation warning",
                guidance="This is a non-critical validation error. "
                         "The workflow can continue, but data quality may be affected.",
                auto_applicable=False,
                parameters={"skip_validation": field}
            ))
        
        return options
    
    def _handle_constraint_violation(self, violation: Dict[str, Any]) -> List[RemediationOption]:
        """Handle constraint violation violations."""
        options = []
        
        context = violation.get("context", {})
        constraint = context.get("constraint", "constraint")
        
        # Fix and retry option
        options.append(RemediationOption(
            action_type=RemediationActionType.FIX_AND_RETRY,
            title="Resolve Constraint Violation",
            description=f"Adjust data to satisfy {constraint} and retry",
            guidance=f"The constraint '{constraint}' was violated. "
                     f"Review the constraint requirements and adjust the data accordingly.",
            auto_applicable=False,
            parameters={"constraint": constraint}
        ))
        
        # Manual intervention option
        options.append(RemediationOption(
            action_type=RemediationActionType.MANUAL_INTERVENTION,
            title="Manual Resolution Required",
            description="Manually resolve the constraint conflict",
            guidance="This constraint violation requires careful manual resolution. "
                     "Review the business rules and data dependencies.",
            auto_applicable=False
        ))
        
        return options
    
    def _handle_unknown(self, violation: Dict[str, Any]) -> List[RemediationOption]:
        """Handle unknown violation types."""
        options = []
        
        # Generic fix and retry option
        options.append(RemediationOption(
            action_type=RemediationActionType.FIX_AND_RETRY,
            title="Review and Retry",
            description="Review the error details and retry the workflow",
            guidance="An unexpected error occurred. Review the error message and logs, "
                     "address any issues, and retry the workflow.",
            auto_applicable=False
        ))
        
        # Manual intervention option
        options.append(RemediationOption(
            action_type=RemediationActionType.MANUAL_INTERVENTION,
            title="Manual Investigation Required",
            description="Investigate the issue manually",
            guidance="This error type is not recognized. Manual investigation is required. "
                     "Check logs and system status for more information.",
            auto_applicable=False
        ))
        
        # Abort option
        options.append(RemediationOption(
            action_type=RemediationActionType.ABORT,
            title="Abort Workflow",
            description="Stop the workflow execution",
            guidance="If the error cannot be resolved, abort the workflow to prevent "
                     "further issues or data corruption.",
            auto_applicable=False
        ))
        
        return options


def create_remediation_generator() -> RemediationGenerator:
    """Factory function to create a RemediationGenerator instance.
    
    Returns:
        RemediationGenerator instance
    """
    return RemediationGenerator()
```