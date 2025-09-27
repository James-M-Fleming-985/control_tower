"""
Evidence Validator for FEATURE-003-01-04 Stage Gate Evidence Collection
Enhanced with RED stage validation criteria and complete TDD cycle validation.
"""
from typing import Dict, Any, List
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Validation result with TDD cycle information"""
    is_valid: bool
    cycle_complete: bool
    completed_phases: List[str]
    validation_errors: List[str] = None
    
    def __post_init__(self):
        if self.validation_errors is None:
            self.validation_errors = []


@dataclass
class ComplianceReport:
    """Compliance report with TDD violation details"""
    violations_found: bool
    violation_types: List[str]
    violation_details: List[str]
    overall_compliance_score: float


class EvidenceValidator:
    """Evidence validator with enhanced TDD workflow validation"""
    
    def __init__(self):
        """Initialize evidence validator"""
        self.validation_history = []
    
    def validate_complete_tdd_cycle(self, cycle_evidence: List[Dict[str, Any]]) -> ValidationResult:
        """Validate complete RED→GREEN→REFACTOR cycle"""
        
        completed_phases = []
        errors = []
        
        # Check for RED phase
        red_found = False
        for evidence in cycle_evidence:
            if evidence.get('stage') == 'red' and evidence.get('tests_failing', 0) > 0:
                red_found = True
                completed_phases.append('RED')
                break
        
        if not red_found:
            errors.append('RED phase not found or no failing tests')
        
        # Check for GREEN phase
        green_found = False
        for evidence in cycle_evidence:
            if (evidence.get('stage') == 'green' and 
                evidence.get('tests_passing', 0) > 0 and 
                evidence.get('implementation') == 'complete'):
                green_found = True
                completed_phases.append('GREEN')
                break
        
        if not green_found:
            errors.append('GREEN phase not found or incomplete implementation')
        
        # Check for REFACTOR phase
        refactor_found = False
        for evidence in cycle_evidence:
            if (evidence.get('stage') == 'refactor' and 
                evidence.get('code_quality') == 'improved'):
                refactor_found = True
                completed_phases.append('REFACTOR')
                break
        
        if not refactor_found:
            errors.append('REFACTOR phase not found or code quality not improved')
        
        # Cycle is complete if all three phases found
        cycle_complete = red_found and green_found and refactor_found
        is_valid = cycle_complete
        
        return ValidationResult(
            is_valid=is_valid,
            cycle_complete=cycle_complete,
            completed_phases=completed_phases,
            validation_errors=errors
        )
    
    def verify_tdd_compliance(self, workflow: Dict[str, Any]) -> ComplianceReport:
        """
        Verify TDD compliance and detect process violations with severity-weighted scoring
        """
        violations_found = False
        violation_types = []
        violation_details = []
        
        # Check for Red phase violations (implementation before tests) - CRITICAL
        if workflow.get('implementation_before_tests', False):
            violations_found = True
            violation_types.append('RED_PHASE_VIOLATION')
            violation_details.append('Implementation created before failing tests')
            
        # Check for Green phase violations (excessive implementation) - HIGH
        if workflow.get('excessive_implementation', False):
            violations_found = True
            violation_types.append('GREEN_PHASE_VIOLATION')
            violation_details.append('Non-minimal implementation')
            
        # Check for Refactor phase violations (test changes) - MEDIUM
        if workflow.get('tests_changed_during_refactor', False):
            violations_found = True
            violation_types.append('REFACTOR_PHASE_VIOLATION')
            violation_details.append('Tests modified during refactor')
        
        # Calculate severity-weighted compliance score
        compliance_score = 100.0  # Start with perfect score
        
        # Apply severity-based penalties
        for violation_type in violation_types:
            if violation_type == 'RED_PHASE_VIOLATION':
                compliance_score -= 50.0  # Critical violation: -50 points
            elif violation_type == 'GREEN_PHASE_VIOLATION':
                compliance_score -= 30.0  # High violation: -30 points
            elif violation_type == 'REFACTOR_PHASE_VIOLATION':
                compliance_score -= 20.0  # Medium violation: -20 points
        
        # Ensure score doesn't go below 0
        compliance_score = max(0.0, compliance_score)
        
        return ComplianceReport(
            violations_found=violations_found,
            violation_types=violation_types,
            violation_details=violation_details,
            overall_compliance_score=compliance_score
        )
    
    def validate_red_stage_acceptance(self, test_data: Dict[str, Any]) -> bool:
        """
        Validate RED stage with proper failing test acceptance criteria
        More lenient criteria to accept proper failing test scenarios
        """
        # Accept if we have failing tests (proper RED phase)
        if test_data.get('tests_failing', 0) > 0:
            return True
        
        # Accept if tests exist but are not yet implemented (preparation phase)
        if test_data.get('tests_written', False) and not test_data.get('implementation_exists', False):
            return True
        
        # Accept if we have test placeholders ready for implementation
        if 'test_cases' in test_data and len(test_data['test_cases']) > 0:
            return True
        
        # Reject only if no testing activity at all
        return False