```python
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ViolationType(Enum):
    BUDGET_EXCEEDED = "budget_exceeded"
    RESOURCE_UNAVAILABLE = "resource_unavailable"
    PERMISSION_DENIED = "permission_denied"
    INVALID_INPUT = "invalid_input"
    TIMEOUT = "timeout"
    DEPENDENCY_FAILURE = "dependency_failure"
    RATE_LIMIT = "rate_limit"
    DATA_VALIDATION = "data_validation"


class OptionType(Enum):
    FIX_AND_RETRY = "fix_and_retry"
    CONTINUE_WITH_WARNING = "continue_with_warning"
    ABORT = "abort"
    ESCALATE = "escalate"


@dataclass
class RemediationOption:
    """Represents a remediation option for a violation."""
    
    option_type: OptionType
    title: str
    description: str
    guidance: str
    auto_fixable: bool = False
    parameters: Dict[str, Any] = field(default_factory=dict)
    estimated_time: Optional[str] = None
    risk_level: str = "medium"


@dataclass
class Violation:
    """Represents a violation that needs remediation."""
    
    violation_type: ViolationType
    message: str
    severity: str
    context: Dict[str, Any] = field(default_factory=dict)


class RemediationOptionsGenerator:
    """Generates remediation options for various violation types."""
    
    def __init__(self):
        self._option_generators = {
            ViolationType.BUDGET_EXCEEDED: self._generate_budget_exceeded_options,
            ViolationType.RESOURCE_UNAVAILABLE: self._generate_resource_unavailable_options,
            ViolationType.PERMISSION_DENIED: self._generate_permission_denied_options,
            ViolationType.INVALID_INPUT: self._generate_invalid_input_options,
            ViolationType.TIMEOUT: self._generate_timeout_options,
            ViolationType.DEPENDENCY_FAILURE: self._generate_dependency_failure_options,
            ViolationType.RATE_LIMIT: self._generate_rate_limit_options,
            ViolationType.DATA_VALIDATION: self._generate_data_validation_options,
        }
    
    def generate_options(self, violation: Violation) -> List[RemediationOption]:
        """
        Generate remediation options for a given violation.
        
        Args:
            violation: The violation to generate options for
            
        Returns:
            List of remediation options
        """
        generator = self._option_generators.get(violation.violation_type)
        if not generator:
            logger.warning(f"No generator found for violation type: {violation.violation_type}")
            return self._generate_default_options(violation)
        
        try:
            options = generator(violation)
            logger.info(f"Generated {len(options)} options for {violation.violation_type}")
            return options
        except Exception as e:
            logger.error(f"Error generating options: {e}")
            return self._generate_default_options(violation)
    
    def _generate_budget_exceeded_options(self, violation: Violation) -> List[RemediationOption]:
        """Generate options for budget exceeded violations."""
        options = []
        
        # Fix and retry option
        options.append(RemediationOption(
            option_type=OptionType.FIX_AND_RETRY,
            title="Request Budget Increase",
            description="Request additional budget allocation to complete the operation",
            guidance="Submit a budget increase request with justification. Approval may take 1-2 business days.",
            auto_fixable=False,
            parameters={"action": "request_budget_increase"},
            estimated_time="1-2 days",
            risk_level="low"
        ))
        
        # Continue with warning option
        options.append(RemediationOption(
            option_type=OptionType.CONTINUE_WITH_WARNING,
            title="Continue with Reduced Scope",
            description="Proceed with a reduced scope that fits within budget constraints",
            guidance="Operation will continue with limited resources. Some features may be unavailable.",
            auto_fixable=True,
            parameters={"action": "reduce_scope", "budget_limit": violation.context.get("budget_limit")},
            estimated_time="immediate",
            risk_level="medium"
        ))
        
        return options
    
    def _generate_resource_unavailable_options(self, violation: Violation) -> List[RemediationOption]:
        """Generate options for resource unavailable violations."""
        options = []
        
        # Fix and retry option
        options.append(RemediationOption(
            option_type=OptionType.FIX_AND_RETRY,
            title="Wait for Resource Availability",
            description="Wait for the required resource to become available",
            guidance="Monitor resource status and retry automatically when available. Set up notification for status changes.",
            auto_fixable=True,
            parameters={"action": "wait_and_retry", "max_wait_time": "30m"},
            estimated_time="5-30 minutes",
            risk_level="low"
        ))
        
        # Continue with warning option
        options.append(RemediationOption(
            option_type=OptionType.CONTINUE_WITH_WARNING,
            title="Use Alternative Resource",
            description="Continue using an alternative resource with similar capabilities",
            guidance="Alternative resource may have different performance characteristics. Review compatibility before proceeding.",
            auto_fixable=False,
            parameters={"action": "use_alternative"},
            estimated_time="immediate",
            risk_level="medium"
        ))
        
        return options
    
    def _generate_permission_denied_options(self, violation: Violation) -> List[RemediationOption]:
        """Generate options for permission denied violations."""
        options = []
        
        # Fix and retry option
        options.append(RemediationOption(
            option_type=OptionType.FIX_AND_RETRY,
            title="Request Required Permissions",
            description="Request the necessary permissions from system administrator",
            guidance="Submit permission request with business justification. Include specific permissions needed and use case.",
            auto_fixable=False,
            parameters={"action": "request_permissions", "required_permissions": violation.context.get("required_permissions", [])},
            estimated_time="1-3 days",
            risk_level="low"
        ))
        
        # Escalate option
        options.append(RemediationOption(
            option_type=OptionType.ESCALATE,
            title="Escalate to Administrator",
            description="Escalate this issue to system administrator for immediate resolution",
            guidance="Use this option for time-sensitive operations. Administrator will be notified immediately.",
            auto_fixable=False,
            parameters={"action": "escalate", "escalation_level": "admin"},
            estimated_time="1-4 hours",
            risk_level="low"
        ))
        
        return options
    
    def _generate_invalid_input_options(self, violation: Violation) -> List[RemediationOption]:
        """Generate options for invalid input violations."""
        options = []
        
        # Fix and retry option
        options.append(RemediationOption(
            option_type=OptionType.FIX_AND_RETRY,
            title="Correct Input and Retry",
            description="Provide corrected input that meets validation requirements",
            guidance=f"Review validation errors and provide correct input. {violation.context.get('validation_details', 'Check input format and constraints.')}",
            auto_fixable=False,
            parameters={"action": "fix_input", "validation_errors": violation.context.get("validation_errors", [])},
            estimated_time="immediate",
            risk_level="low"
        ))
        
        # Auto-fix option if possible
        if violation.context.get("auto_fixable"):
            options.append(RemediationOption(
                option_type=OptionType.FIX_AND_RETRY,
                title="Apply Automatic Correction",
                description="Automatically correct common input issues and retry",
                guidance="System will attempt to automatically correct the input based on known patterns.",
                auto_fixable=True,
                parameters={"action": "auto_correct_input"},
                estimated_time="immediate",
                risk_level="low"
            ))
        
        return options
    
    def _generate_timeout_options(self, violation: Violation) -> List[RemediationOption]:
        """Generate options for timeout violations."""
        options = []
        
        # Fix and retry option
        options.append(RemediationOption(
            option_type=OptionType.FIX_AND_RETRY,
            title="Retry with Extended Timeout",
            description="Retry the operation with a longer timeout period",
            guidance="Increase timeout limit to allow operation to complete. Monitor performance to identify bottlenecks.",
            auto_fixable=True,
            parameters={"action": "retry_with_timeout", "timeout_multiplier": 2},
            estimated_time="varies",
            risk_level="medium"
        ))
        
        # Continue with warning option
        options.append(RemediationOption(
            option_type=OptionType.CONTINUE_WITH_WARNING,
            title="Continue with Partial Results",
            description="Continue with whatever results were obtained before timeout",
            guidance="Operation completed partially. Results may be incomplete. Review carefully before using.",
            auto_fixable=True,
            parameters={"action": "use_partial_results"},
            estimated_time="immediate",
            risk_level="high"
        ))
        
        return options
    
    def _generate_dependency_failure_options(self, violation: Violation) -> List[RemediationOption]:
        """Generate options for dependency failure violations."""
        options = []
        
        # Fix and retry option
        options.append(RemediationOption(
            option_type=OptionType.FIX_AND_RETRY,
            title="Retry After Dependency Recovery",
            description="Wait for dependency to recover and retry the operation",
            guidance="Monitor dependency health status. Automatic retry will occur when dependency is restored.",
            auto_fixable=True,
            parameters={"action": "wait_for_dependency", "max_retries": 3},
            estimated_time="5-15 minutes",
            risk_level="low"
        ))
        
        # Continue with warning option
        options.append(RemediationOption(
            option_type=OptionType.CONTINUE_WITH_WARNING,
            title="Continue with Degraded Functionality",
            description="Continue operation without the failed dependency",
            guidance="Some features will be unavailable. Operation will proceed with reduced functionality.",
            auto_fixable=True,
            parameters={"action": "degrade_gracefully"},
            estimated_time="immediate",
            risk_level="medium"
        ))
        
        return options
    
    def _generate_rate_limit_options(self, violation: Violation) -> List[RemediationOption]:
        """Generate options for rate limit violations."""
        options = []
        
        # Fix and retry option
        options.append(RemediationOption(
            option_type=OptionType.FIX_AND_RETRY,
            title="Wait and Retry",
            description="Wait for rate limit window to reset and retry",
            guidance="Rate limit will reset automatically. Operation will retry when limit is restored.",
            auto_fixable=True,
            parameters={"action": "wait_for_rate_limit", "wait_time": violation.context.get("reset_time", "60s")},
            estimated_time=violation.context.get("reset_time", "60 seconds"),
            risk_level="low"
        ))
        
        # Continue with warning option
        options.append(RemediationOption(
            option_type=OptionType.CONTINUE_WITH_WARNING,
            title="Throttle and Continue",
            description="Reduce request rate and continue with throttled operations",
            guidance="Operations will proceed at a reduced rate. Overall completion time will increase.",
            auto_fixable=True,
            parameters={"action": "throttle_requests", "rate_reduction": 0.5},
            estimated_time="extended",
            risk_level="low"
        ))
        
        return options
    
    def _generate_data_validation_options(self, violation: Violation) -> List[RemediationOption]:
        """Generate options for data validation violations."""
        options = []
        
        # Fix and retry option
        options.append(RemediationOption(
            option_type=OptionType.FIX_AND_RETRY,
            title="Correct Data and Retry",
            description="Fix data validation issues and retry the operation",
            guidance=f"Review and correct the following validation errors: {', '.join(violation.context.get('errors', ['data format issues']))}",
            auto_fixable=False,
            parameters={"action": "fix_data", "errors": violation.context.get("errors", [])},
            estimated_time="immediate",
            risk_level="low"
        ))
        
        # Continue with warning option
        if violation.context.get("allow_skip"):
            options.append(RemediationOption(
                option_type=OptionType.CONTINUE_WITH_WARNING,
                title="Skip Invalid Data",
                description="Continue processing while skipping invalid data entries",
                guidance="Invalid data will be logged and skipped. Review logs to identify data quality issues.",
                auto_fixable=True,
                parameters={"action": "skip_invalid_data"},
                estimated_time="immediate",
                risk_level="medium"
            ))
        
        return options
    
    def _generate_default_options(self, violation: Violation) -> List[RemediationOption]:
        """Generate default options when no specific generator is available."""
        return [
            RemediationOption(
                option_type=OptionType.FIX_AND_RETRY,
                title="Retry Operation",
                description="Retry the operation after reviewing the error",
                guidance="Review the error details and retry the operation. Contact support if issue persists.",
                auto_fixable=False,
                parameters={"action": "retry"},
                estimated_time="immediate",
                risk_level="medium"
            ),
            RemediationOption(
                option_type=OptionType.ABORT,
                title="Abort Operation",
                description="Cancel the operation and roll back changes",
                guidance="Operation will be cancelled. Any partial changes will be rolled back.",
                auto_fixable=True,
                parameters={"action": "abort"},
                estimated_time="immediate",
                risk_level="low"
            )
        ]
    
    def format_options_for_presentation(self, options: List[RemediationOption]) -> List[Dict[str, Any]]:
        """
        Format remediation options for presentation to user/actor.
        
        Args:
            options: List of remediation options
            
        Returns:
            List of formatted option dictionaries
        """
        formatted_options = []
        
        for idx, option in enumerate(options, 1):
            formatted = {
                "id": idx,
                "type": option.option_type.value,
                "title": option.title,
                "description": option.description,
                "guidance": option.guidance,
                "auto_fixable": option.auto_fixable,
                "estimated_time": option.estimated_time,
                "risk_level": option.risk_level,
                "parameters": option.parameters
            }
            formatted_options.append(formatted)
        
        return formatted_options


def generate_remediation_options(violation: Violation) -> List[RemediationOption]:
    """
    Convenience function to generate remediation options for a violation.
    
    Args:
        violation: The violation to generate options for
        
    Returns:
        List of remediation options
    """
    generator = RemediationOptionsGenerator()
    return generator.generate_options(violation)


def format_options(options: List[RemediationOption]) -> List[Dict[str, Any]]:
    """
    Convenience function to format options for presentation.
    
    Args:
        options: List of remediation options
        
    Returns: