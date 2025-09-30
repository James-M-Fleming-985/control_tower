"""
Stage Gate Management System
============================

Manages the stage gates between TDD phases, enforces compliance requirements,
and validates transition readiness with comprehensive evidence collection.
"""

import time
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from .constants import COMPLIANCE_THRESHOLDS

from .phase_enforcement import (
    PhaseEnforcementResult, 
    PhaseValidationResult,
    RedPhaseEnforcer,
    GreenPhaseEnforcer, 
    RefactorPhaseEnforcer
)


class StageGateStatus(Enum):
    """Status of stage gate validation"""
    OPEN = "OPEN"           # Gate is open, transition allowed
    CLOSED = "CLOSED"       # Gate is closed, transition blocked
    WARNING = "WARNING"     # Gate open with warnings
    PENDING = "PENDING"     # Gate validation in progress


class TransitionType(Enum):
    """Types of phase transitions"""
    RED_TO_GREEN = "RED_TO_GREEN"
    GREEN_TO_REFACTOR = "GREEN_TO_REFACTOR"
    REFACTOR_TO_RED = "REFACTOR_TO_RED"
    CYCLE_COMPLETE = "CYCLE_COMPLETE"


@dataclass
class StageGateEvidence:
    """Evidence required for stage gate passage"""
    phase_enforcement_result: PhaseEnforcementResult
    compliance_evidence: Dict[str, Any]
    quality_metrics: Dict[str, float]
    performance_metrics: Dict[str, float]
    risk_assessment: Dict[str, str]
    approval_criteria_met: List[str]
    blocking_criteria: List[str]


@dataclass
class StageGateDecision:
    """Decision made at a stage gate"""
    gate_id: str
    transition_type: TransitionType
    status: StageGateStatus
    decision_timestamp: datetime
    evidence: StageGateEvidence
    compliance_score: float
    risk_level: str
    recommendations: List[str]
    next_actions: List[str]
    approval_authority: str


class StageGateManager:
    """
    Manages stage gates between TDD phases
    
    Enforces compliance requirements and validates readiness for phase transitions
    with comprehensive evidence collection and risk assessment.
    """
    
    def __init__(self, compliance_threshold: float = COMPLIANCE_THRESHOLDS["ACCEPTABLE"], risk_tolerance: str = "MEDIUM"):
        self.compliance_threshold = compliance_threshold
        self.risk_tolerance = risk_tolerance
        
        # Initialize phase enforcers
        self.red_enforcer = RedPhaseEnforcer()
        self.green_enforcer = GreenPhaseEnforcer()
        self.refactor_enforcer = RefactorPhaseEnforcer()
        
        # Stage gate history
        self.gate_history: List[StageGateDecision] = []
        
        # Compliance criteria
        self.approval_criteria = {
            TransitionType.RED_TO_GREEN: [
                "tests_exist",
                "tests_failing", 
                "minimal_implementation",
                "test_quality_adequate"
            ],
            TransitionType.GREEN_TO_REFACTOR: [
                "tests_passing",
                "minimal_implementation_complete",
                "coverage_adequate",
                "no_feature_creep"
            ],
            TransitionType.REFACTOR_TO_RED: [
                "tests_still_passing",
                "quality_improved",
                "no_new_functionality",
                "technical_debt_reduced"
            ]
        }
    
    def evaluate_stage_gate(self, 
                           project_path: str,
                           evidence: Dict[str, Any],
                           current_phase: str = None,
                           target_phase: str = None) -> StageGateDecision:
        """
        Evaluate stage gate for phase transition
        
        Args:
            current_phase: Current TDD phase (RED, GREEN, REFACTOR)
            target_phase: Target TDD phase for transition
            project_path: Path to project for validation
            evidence: Additional evidence for validation
            
        Returns:
            StageGateDecision with validation results and recommendations
        """
        start_time = time.time()
        
        # Extract phases from evidence if not provided as parameters
        if current_phase is None:
            current_phase = evidence.get('current_phase')
        if target_phase is None:
            target_phase = evidence.get('target_phase')
            
        # Convert PhaseType enums to strings if needed
        if hasattr(current_phase, 'value'):
            current_phase = current_phase.value
        if hasattr(target_phase, 'value'):
            target_phase = target_phase.value
        
        # Determine transition type
        transition_type = self._determine_transition_type(current_phase, target_phase)
        
        # Get appropriate phase enforcer
        enforcement_result = self._enforce_current_phase(current_phase, project_path, evidence)
        
        # Collect compliance evidence
        compliance_evidence = self._collect_compliance_evidence(enforcement_result, evidence)
        
        # Assess quality metrics
        quality_metrics = self._assess_quality_metrics(project_path, evidence)
        
        # Assess performance metrics
        performance_metrics = self._assess_performance_metrics(enforcement_result)
        
        # Assess risks
        risk_assessment = self._assess_transition_risks(transition_type, enforcement_result, evidence)
        
        # Check approval criteria
        approval_criteria_met, blocking_criteria = self._check_approval_criteria(
            transition_type, enforcement_result, compliance_evidence
        )
        
        # Create stage gate evidence
        gate_evidence = StageGateEvidence(
            phase_enforcement_result=enforcement_result,
            compliance_evidence=compliance_evidence,
            quality_metrics=quality_metrics,
            performance_metrics=performance_metrics,
            risk_assessment=risk_assessment,
            approval_criteria_met=approval_criteria_met,
            blocking_criteria=blocking_criteria
        )
        
        # Make gate decision
        gate_decision = self._make_gate_decision(transition_type, gate_evidence)
        
        # Record in history
        self.gate_history.append(gate_decision)
        
        return gate_decision
    
    def _determine_transition_type(self, current_phase: str, target_phase: str) -> TransitionType:
        """Determine the type of transition being requested"""
        transition_map = {
            ("RED", "GREEN"): TransitionType.RED_TO_GREEN,
            ("GREEN", "REFACTOR"): TransitionType.GREEN_TO_REFACTOR,
            ("REFACTOR", "RED"): TransitionType.REFACTOR_TO_RED
        }
        
        return transition_map.get((current_phase, target_phase), TransitionType.CYCLE_COMPLETE)
    
    def _enforce_current_phase(self, 
                              current_phase: str, 
                              project_path: str, 
                              evidence: Dict[str, Any]) -> PhaseEnforcementResult:
        """Enforce current phase requirements"""
        if current_phase == "RED":
            return self.red_enforcer.enforce_red_phase(project_path, evidence)
        elif current_phase == "GREEN":
            return self.green_enforcer.enforce_green_phase(project_path, evidence)
        elif current_phase == "REFACTOR":
            return self.refactor_enforcer.enforce_refactor_phase(project_path, evidence)
        else:
            raise ValueError(f"Unknown phase: {current_phase}")
    
    def _collect_compliance_evidence(self, 
                                   enforcement_result: PhaseEnforcementResult,
                                   additional_evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Collect compliance evidence for validation"""
        compliance_evidence = {
            "enforcement_compliance": enforcement_result.compliance_score,
            "validation_result": enforcement_result.validation_result.value,
            "blocking_issues_count": len(enforcement_result.blocking_issues),
            "warnings_count": len(enforcement_result.warnings),
            "execution_time_ms": enforcement_result.execution_time_ms,
            "evidence_timestamp": enforcement_result.evidence.validation_timestamp.isoformat()
        }
        
        # Add additional evidence
        compliance_evidence.update(additional_evidence)
        
        return compliance_evidence
    
    def _assess_quality_metrics(self, project_path: str, evidence: Dict[str, Any]) -> Dict[str, float]:
        """Assess quality metrics for the project"""
        # In real implementation, this would integrate with quality tools
        quality_metrics = {
            "code_coverage": evidence.get("code_coverage", 0.75),
            "test_coverage": evidence.get("test_coverage", 0.80),
            "complexity_score": evidence.get("complexity_score", 0.60),
            "maintainability_index": evidence.get("maintainability_index", 0.70),
            "technical_debt_ratio": evidence.get("technical_debt_ratio", 0.20)
        }
        
        return quality_metrics
    
    def _assess_performance_metrics(self, enforcement_result: PhaseEnforcementResult) -> Dict[str, float]:
        """Assess performance metrics for enforcement"""
        performance_metrics = {
            "enforcement_time_ms": enforcement_result.execution_time_ms,
            "compliance_score": enforcement_result.compliance_score,
            "validation_efficiency": 1.0 / max(enforcement_result.execution_time_ms / 1000, 0.1),
            "evidence_completeness": 0.90  # Simulated completeness score
        }
        
        return performance_metrics
    
    def _assess_transition_risks(self, 
                               transition_type: TransitionType,
                               enforcement_result: PhaseEnforcementResult,
                               evidence: Dict[str, Any]) -> Dict[str, str]:
        """Assess risks associated with phase transition"""
        risk_assessment = {
            "technical_risk": "LOW",
            "quality_risk": "LOW", 
            "timeline_risk": "LOW",
            "compliance_risk": "LOW"
        }
        
        # Assess technical risk
        if enforcement_result.validation_result == PhaseValidationResult.FAIL:
            risk_assessment["technical_risk"] = "HIGH"
        elif enforcement_result.blocking_issues:
            risk_assessment["technical_risk"] = "MEDIUM"
        
        # Assess quality risk
        if enforcement_result.compliance_score < 0.60:
            risk_assessment["quality_risk"] = "HIGH"
        elif enforcement_result.compliance_score < 0.75:
            risk_assessment["quality_risk"] = "MEDIUM"
        
        # Assess timeline risk
        if enforcement_result.execution_time_ms > 5000:  # > 5 seconds
            risk_assessment["timeline_risk"] = "MEDIUM"
        
        # Assess compliance risk
        if len(enforcement_result.blocking_issues) > 2:
            risk_assessment["compliance_risk"] = "HIGH"
        elif enforcement_result.warnings:
            risk_assessment["compliance_risk"] = "MEDIUM"
        
        return risk_assessment
    
    def _check_approval_criteria(self, 
                               transition_type: TransitionType,
                               enforcement_result: PhaseEnforcementResult,
                               compliance_evidence: Dict[str, Any]) -> tuple[List[str], List[str]]:
        """Check approval criteria for transition"""
        required_criteria = self.approval_criteria.get(transition_type, [])
        
        approval_criteria_met = []
        blocking_criteria = []
        
        for criterion in required_criteria:
            if self._evaluate_criterion(criterion, enforcement_result, compliance_evidence):
                approval_criteria_met.append(criterion)
            else:
                blocking_criteria.append(criterion)
        
        return approval_criteria_met, blocking_criteria
    
    def _evaluate_criterion(self, 
                          criterion: str,
                          enforcement_result: PhaseEnforcementResult,
                          compliance_evidence: Dict[str, Any]) -> bool:
        """Evaluate individual approval criterion"""
        criterion_evaluators = {
            "tests_exist": lambda: len(enforcement_result.evidence.test_files) > 0,
            "tests_failing": lambda: any(not result for result in enforcement_result.evidence.test_results.values()),
            "tests_passing": lambda: all(enforcement_result.evidence.test_results.values()),
            "minimal_implementation": lambda: enforcement_result.evidence.complexity_score < 0.5,
            "test_quality_adequate": lambda: enforcement_result.evidence.code_coverage >= 0.70,
            "coverage_adequate": lambda: enforcement_result.evidence.code_coverage >= self.compliance_threshold,
            "no_feature_creep": lambda: compliance_evidence.get("new_features_added", False) == False,
            "quality_improved": lambda: compliance_evidence.get("quality_improvement", 0) > 0,
            "no_new_functionality": lambda: compliance_evidence.get("new_functionality_added", False) == False,
            "technical_debt_reduced": lambda: compliance_evidence.get("complexity_reduction", 0) > 0,
            "tests_still_passing": lambda: all(enforcement_result.evidence.test_results.values()),
            "minimal_implementation_complete": lambda: enforcement_result.compliance_score >= 0.75
        }
        
        evaluator = criterion_evaluators.get(criterion)
        if evaluator:
            try:
                return evaluator()
            except Exception:
                return False
        
        return False
    
    def _make_gate_decision(self, 
                          transition_type: TransitionType,
                          evidence: StageGateEvidence) -> StageGateDecision:
        """Make final stage gate decision"""
        # Calculate overall compliance score
        compliance_score = evidence.phase_enforcement_result.compliance_score
        
        # Determine gate status
        if evidence.blocking_criteria and compliance_score < COMPLIANCE_THRESHOLDS["EXCELLENT"]:
            # Only block if there are blocking criteria AND compliance is not excellent
            status = StageGateStatus.CLOSED
        elif compliance_score >= self.compliance_threshold:
            if evidence.phase_enforcement_result.warnings:
                status = StageGateStatus.WARNING
            else:
                status = StageGateStatus.OPEN
        else:
            status = StageGateStatus.CLOSED
        
        # Assess overall risk
        high_risks = [risk for risk in evidence.risk_assessment.values() if risk == "HIGH"]
        if high_risks:
            risk_level = "HIGH"
        elif any(risk == "MEDIUM" for risk in evidence.risk_assessment.values()):
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        # Generate recommendations
        recommendations = self._generate_recommendations(status, evidence)
        
        # Generate next actions
        next_actions = self._generate_next_actions(status, transition_type, evidence)
        
        # Create decision
        gate_id = f"GATE_{transition_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return StageGateDecision(
            gate_id=gate_id,
            transition_type=transition_type,
            status=status,
            decision_timestamp=datetime.now(),
            evidence=evidence,
            compliance_score=compliance_score,
            risk_level=risk_level,
            recommendations=recommendations,
            next_actions=next_actions,
            approval_authority="TDD_CYCLE_ENFORCER"
        )
    
    def _generate_recommendations(self, 
                                status: StageGateStatus, 
                                evidence: StageGateEvidence) -> List[str]:
        """Generate recommendations based on gate status"""
        recommendations = []
        
        if status == StageGateStatus.CLOSED:
            recommendations.append("Address all blocking criteria before attempting transition")
            for criterion in evidence.blocking_criteria:
                recommendations.append(f"Resolve: {criterion}")
        
        if evidence.phase_enforcement_result.warnings:
            recommendations.append("Address warnings to improve transition quality")
        
        if evidence.phase_enforcement_result.compliance_score < 0.9:
            recommendations.append("Improve compliance score for smoother transitions")
        
        return recommendations
    
    def _generate_next_actions(self, 
                             status: StageGateStatus,
                             transition_type: TransitionType,
                             evidence: StageGateEvidence) -> List[str]:
        """Generate next actions based on gate decision"""
        next_actions = []
        
        if status == StageGateStatus.OPEN:
            if transition_type == TransitionType.RED_TO_GREEN:
                next_actions.append("Proceed to GREEN phase: Implement minimal code to make tests pass")
            elif transition_type == TransitionType.GREEN_TO_REFACTOR:
                next_actions.append("Proceed to REFACTOR phase: Improve code quality without breaking tests")
            elif transition_type == TransitionType.REFACTOR_TO_RED:
                next_actions.append("Proceed to RED phase: Write next failing test")
        
        elif status == StageGateStatus.CLOSED:
            next_actions.append("Remain in current phase until blocking issues resolved")
            for issue in evidence.phase_enforcement_result.blocking_issues:
                next_actions.append(f"Fix: {issue}")
        
        elif status == StageGateStatus.WARNING:
            next_actions.append("Proceed with caution - monitor warnings closely")
        
        return next_actions
    
    def get_gate_history(self) -> List[Dict[str, Any]]:
        """Get stage gate decision history"""
        return [asdict(decision) for decision in self.gate_history]
    
    def export_compliance_report(self, output_path: str):
        """Export compliance report to file"""
        report = {
            "report_timestamp": datetime.now().isoformat(),
            "compliance_threshold": self.compliance_threshold,
            "risk_tolerance": self.risk_tolerance,
            "total_gates_evaluated": len(self.gate_history),
            "gate_decisions": self.get_gate_history()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
    
    def check_compliance(self, evidence: Dict[str, Any]) -> bool:
        """Check if evidence meets compliance requirements"""
        compliance_score = evidence.get('compliance_score', 0.0)
        return compliance_score >= self.compliance_threshold
    
    def assess_risk_level(self, evidence: Dict[str, Any]) -> str:
        """Assess risk level based on evidence"""
        compliance_score = evidence.get('compliance_score', 0.0)
        
        if compliance_score >= 0.9:
            return "LOW"
        elif compliance_score >= 0.75:
            return "MEDIUM"
        elif compliance_score >= 0.5:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def determine_gate_status(self, evidence: Dict[str, Any]) -> StageGateStatus:
        """Determine gate status based on evidence"""
        compliance_score = evidence.get('compliance_score', 0.0)
        
        if compliance_score >= self.compliance_threshold:
            if compliance_score >= 0.9:
                return StageGateStatus.OPEN
            else:
                return StageGateStatus.WARNING
        else:
            return StageGateStatus.CLOSED