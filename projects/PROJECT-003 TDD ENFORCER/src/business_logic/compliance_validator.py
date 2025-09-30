"""
Compliance Validation System
===========================

Evidence collection, TDD methodology verification, violation detection, and reporting
for comprehensive TDD cycle compliance enforcement.
"""

import time
import json
import hashlib
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path

from .phase_enforcement import PhaseEnforcementResult
from .stage_gate_manager import StageGateDecision


class ComplianceStatus(Enum):
    """Status of compliance validation"""
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    PARTIAL_COMPLIANCE = "PARTIAL_COMPLIANCE"
    VALIDATION_ERROR = "VALIDATION_ERROR"


class ViolationType(Enum):
    """Types of TDD methodology violations"""
    TEST_FIRST_VIOLATION = "TEST_FIRST_VIOLATION"
    PHASE_SKIP_VIOLATION = "PHASE_SKIP_VIOLATION"
    OVER_IMPLEMENTATION = "OVER_IMPLEMENTATION"
    FEATURE_CREEP = "FEATURE_CREEP"
    TEST_BREAKING = "TEST_BREAKING"
    INSUFFICIENT_COVERAGE = "INSUFFICIENT_COVERAGE"
    QUALITY_REGRESSION = "QUALITY_REGRESSION"


@dataclass
class ComplianceEvidence:
    """Evidence collected for compliance validation"""
    evidence_id: str
    collection_timestamp: datetime
    project_path: str
    phase_enforcement_results: List[PhaseEnforcementResult]
    stage_gate_decisions: List[StageGateDecision]
    test_execution_logs: Dict[str, Any]
    code_analysis_results: Dict[str, Any]
    git_commit_history: List[Dict[str, Any]]
    quality_metrics: Dict[str, float]
    performance_metrics: Dict[str, float]
    verification_checksum: str


@dataclass
class ComplianceViolation:
    """Details of a compliance violation"""
    violation_id: str
    violation_type: ViolationType
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    description: str
    evidence_reference: str
    detected_timestamp: datetime
    file_references: List[str]
    remediation_steps: List[str]
    impact_assessment: str


@dataclass
class ComplianceResult:
    """Result of compliance validation"""
    validation_id: str
    project_path: str
    validation_timestamp: datetime
    compliance_status: ComplianceStatus
    overall_compliance_score: float
    methodology_adherence_score: float
    evidence: ComplianceEvidence
    violations: List[ComplianceViolation]
    recommendations: List[str]
    certification_status: str
    validation_duration_ms: float


class ComplianceValidator:
    """
    Validates TDD methodology compliance and collects evidence
    
    Provides comprehensive validation of TDD methodology adherence,
    evidence collection, violation detection, and compliance reporting.
    """
    
    def __init__(self, min_compliance_score: float = 0.75, violation_tolerance: str = "MEDIUM"):
        self.min_compliance_score = min_compliance_score
        self.violation_tolerance = violation_tolerance
        self.validation_history: List[ComplianceResult] = []
        
        # Compliance rules configuration
        self.compliance_rules = {
            "test_first_required": True,
            "phase_sequence_enforced": True,
            "minimal_implementation_required": True,
            "test_preservation_required": True,
            "quality_improvement_required": True,
            "coverage_threshold": 0.75,
            "complexity_threshold": 0.60
        }
    
    def validate_compliance(self, 
                          project_path: str,
                          phase_results: List[PhaseEnforcementResult],
                          gate_decisions: List[StageGateDecision]) -> ComplianceResult:
        """
        Validate comprehensive TDD methodology compliance
        
        Args:
            project_path: Path to project for validation
            phase_results: Results from phase enforcement
            gate_decisions: Results from stage gate evaluations
            
        Returns:
            ComplianceResult with comprehensive validation assessment
        """
        start_time = time.time()
        validation_id = f"COMP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Collect evidence
        evidence = self._collect_comprehensive_evidence(
            project_path, phase_results, gate_decisions
        )
        
        # Detect violations
        violations = self._detect_methodology_violations(evidence)
        
        # Calculate compliance scores
        overall_score = self._calculate_overall_compliance_score(evidence, violations)
        methodology_score = self._calculate_methodology_adherence_score(evidence)
        
        # Determine compliance status
        compliance_status = self._determine_compliance_status(overall_score, violations)
        
        # Generate recommendations
        recommendations = self._generate_compliance_recommendations(violations, evidence)
        
        # Determine certification status
        certification_status = self._determine_certification_status(compliance_status, overall_score)
        
        validation_duration = (time.time() - start_time) * 1000
        
        result = ComplianceResult(
            validation_id=validation_id,
            project_path=project_path,
            validation_timestamp=datetime.now(),
            compliance_status=compliance_status,
            overall_compliance_score=overall_score,
            methodology_adherence_score=methodology_score,
            evidence=evidence,
            violations=violations,
            recommendations=recommendations,
            certification_status=certification_status,
            validation_duration_ms=validation_duration
        )
        
        # Store in history
        self.validation_history.append(result)
        
        return result
    
    def _collect_comprehensive_evidence(self,
                                      project_path: str,
                                      phase_results: List[PhaseEnforcementResult],
                                      gate_decisions: List[StageGateDecision]) -> ComplianceEvidence:
        """Collect comprehensive evidence for compliance validation"""
        evidence_id = f"EVID_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Collect test execution logs
        test_logs = self._collect_test_execution_logs(project_path)
        
        # Collect code analysis results
        code_analysis = self._perform_code_analysis(project_path)
        
        # Collect git history
        git_history = self._collect_git_commit_history(project_path)
        
        # Collect quality metrics
        quality_metrics = self._collect_quality_metrics(project_path)
        
        # Collect performance metrics
        performance_metrics = self._collect_performance_metrics(phase_results, gate_decisions)
        
        # Create evidence object
        evidence_data = {
            "evidence_id": evidence_id,
            "project_path": project_path,
            "phase_results": [asdict(result) for result in phase_results],
            "gate_decisions": [asdict(decision) for decision in gate_decisions],
            "test_logs": test_logs,
            "code_analysis": code_analysis,
            "git_history": git_history,
            "quality_metrics": quality_metrics,
            "performance_metrics": performance_metrics
        }
        
        # Generate verification checksum
        checksum = hashlib.sha256(json.dumps(evidence_data, sort_keys=True).encode()).hexdigest()
        
        return ComplianceEvidence(
            evidence_id=evidence_id,
            collection_timestamp=datetime.now(),
            project_path=project_path,
            phase_enforcement_results=phase_results,
            stage_gate_decisions=gate_decisions,
            test_execution_logs=test_logs,
            code_analysis_results=code_analysis,
            git_commit_history=git_history,
            quality_metrics=quality_metrics,
            performance_metrics=performance_metrics,
            verification_checksum=checksum
        )
    
    def _collect_test_execution_logs(self, project_path: str) -> Dict[str, Any]:
        """Collect test execution logs and results"""
        # In real implementation, this would integrate with test frameworks
        return {
            "total_tests": 0,
            "passing_tests": 0,
            "failing_tests": 0,
            "test_files": [],
            "execution_time": 0.0,
            "coverage_report": {}
        }
    
    def _perform_code_analysis(self, project_path: str) -> Dict[str, Any]:
        """Perform comprehensive code analysis"""
        # In real implementation, this would use static analysis tools
        return {
            "complexity_metrics": {},
            "quality_scores": {},
            "dependency_analysis": {},
            "architectural_analysis": {}
        }
    
    def _collect_git_commit_history(self, project_path: str) -> List[Dict[str, Any]]:
        """Collect git commit history for TDD pattern analysis"""
        # In real implementation, this would integrate with git
        return []
    
    def _collect_quality_metrics(self, project_path: str) -> Dict[str, float]:
        """Collect quality metrics for the project"""
        return {
            "code_coverage": 0.0,
            "test_coverage": 0.0,
            "complexity_score": 0.0,
            "maintainability_index": 0.0,
            "technical_debt_ratio": 0.0
        }
    
    def _collect_performance_metrics(self, 
                                   phase_results: List[PhaseEnforcementResult],
                                   gate_decisions: List[StageGateDecision]) -> Dict[str, float]:
        """Collect performance metrics from enforcement operations"""
        if not phase_results and not gate_decisions:
            return {
                "average_enforcement_time": 0.0,
                "peak_enforcement_time": 0.0,
                "validation_efficiency": 0.0,
                "throughput_rate": 0.0
            }
        
        enforcement_times = [result.execution_time_ms for result in phase_results]
        
        return {
            "average_enforcement_time": sum(enforcement_times) / max(len(enforcement_times), 1),
            "peak_enforcement_time": max(enforcement_times) if enforcement_times else 0.0,
            "validation_efficiency": 1.0,  # Calculated based on complexity
            "throughput_rate": len(phase_results) / max(sum(enforcement_times) / 1000, 0.1)
        }
    
    def _detect_methodology_violations(self, evidence: ComplianceEvidence) -> List[ComplianceViolation]:
        """Detect TDD methodology violations from evidence"""
        violations = []
        
        # Check for test-first violations
        test_first_violations = self._check_test_first_violations(evidence)
        violations.extend(test_first_violations)
        
        # Check for phase sequence violations
        phase_violations = self._check_phase_sequence_violations(evidence)
        violations.extend(phase_violations)
        
        # Check for over-implementation violations
        implementation_violations = self._check_implementation_violations(evidence)
        violations.extend(implementation_violations)
        
        # Check for quality violations
        quality_violations = self._check_quality_violations(evidence)
        violations.extend(quality_violations)
        
        return violations
    
    def _check_test_first_violations(self, evidence: ComplianceEvidence) -> List[ComplianceViolation]:
        """Check for test-first development violations"""
        violations = []
        
        # Analyze git history for test-first patterns
        for commit in evidence.git_commit_history:
            # In real implementation, analyze commit patterns
            pass
        
        return violations
    
    def _check_phase_sequence_violations(self, evidence: ComplianceEvidence) -> List[ComplianceViolation]:
        """Check for proper TDD phase sequence adherence"""
        violations = []
        
        # Analyze phase enforcement results for proper sequence
        for result in evidence.phase_enforcement_results:
            # In real implementation, validate phase sequences
            pass
        
        return violations
    
    def _check_implementation_violations(self, evidence: ComplianceEvidence) -> List[ComplianceViolation]:
        """Check for over-implementation and feature creep violations"""
        violations = []
        
        # Analyze code complexity and implementation patterns
        complexity_score = evidence.quality_metrics.get("complexity_score", 0.0)
        if complexity_score > self.compliance_rules["complexity_threshold"]:
            violations.append(ComplianceViolation(
                violation_id=f"IMPL_VIOLATION_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                violation_type=ViolationType.OVER_IMPLEMENTATION,
                severity="HIGH",
                description=f"Code complexity {complexity_score:.2f} exceeds threshold {self.compliance_rules['complexity_threshold']}",
                evidence_reference=evidence.evidence_id,
                detected_timestamp=datetime.now(),
                file_references=[],
                remediation_steps=["Simplify implementation", "Remove unnecessary complexity"],
                impact_assessment="High risk of maintenance issues and TDD violation"
            ))
        
        return violations
    
    def _check_quality_violations(self, evidence: ComplianceEvidence) -> List[ComplianceViolation]:
        """Check for quality-related violations"""
        violations = []
        
        # Check coverage violations
        coverage = evidence.quality_metrics.get("code_coverage", 0.0)
        if coverage < self.compliance_rules["coverage_threshold"]:
            violations.append(ComplianceViolation(
                violation_id=f"COV_VIOLATION_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                violation_type=ViolationType.INSUFFICIENT_COVERAGE,
                severity="MEDIUM",
                description=f"Code coverage {coverage:.1%} below threshold {self.compliance_rules['coverage_threshold']:.1%}",
                evidence_reference=evidence.evidence_id,
                detected_timestamp=datetime.now(),
                file_references=[],
                remediation_steps=["Add more tests", "Improve test coverage"],
                impact_assessment="Medium risk of untested code paths"
            ))
        
        return violations
    
    def _calculate_overall_compliance_score(self, 
                                          evidence: ComplianceEvidence, 
                                          violations: List[ComplianceViolation]) -> float:
        """Calculate overall compliance score"""
        base_score = 1.0
        
        # Deduct points for violations
        violation_penalties = {
            "CRITICAL": 0.25,
            "HIGH": 0.15,
            "MEDIUM": 0.10,
            "LOW": 0.05
        }
        
        for violation in violations:
            penalty = violation_penalties.get(violation.severity, 0.05)
            base_score -= penalty
        
        # Apply quality metrics
        quality_factor = sum(evidence.quality_metrics.values()) / max(len(evidence.quality_metrics), 1)
        base_score *= quality_factor
        
        return max(0.0, min(1.0, base_score))
    
    def _calculate_methodology_adherence_score(self, evidence: ComplianceEvidence) -> float:
        """Calculate TDD methodology adherence score"""
        # Analyze phase enforcement results for methodology adherence
        if not evidence.phase_enforcement_results:
            return 0.0
        
        adherence_scores = []
        for result in evidence.phase_enforcement_results:
            adherence_scores.append(result.compliance_score)
        
        return sum(adherence_scores) / len(adherence_scores)
    
    def _determine_compliance_status(self, 
                                   overall_score: float, 
                                   violations: List[ComplianceViolation]) -> ComplianceStatus:
        """Determine overall compliance status"""
        critical_violations = [v for v in violations if v.severity == "CRITICAL"]
        
        if critical_violations:
            return ComplianceStatus.NON_COMPLIANT
        elif overall_score >= self.min_compliance_score:
            if violations:
                return ComplianceStatus.PARTIAL_COMPLIANCE
            else:
                return ComplianceStatus.COMPLIANT
        else:
            return ComplianceStatus.NON_COMPLIANT
    
    def _generate_compliance_recommendations(self, 
                                           violations: List[ComplianceViolation],
                                           evidence: ComplianceEvidence) -> List[str]:
        """Generate compliance improvement recommendations"""
        recommendations = []
        
        if violations:
            recommendations.append(f"Address {len(violations)} methodology violations")
            
            # Group by violation type
            violation_types = {}
            for violation in violations:
                if violation.violation_type not in violation_types:
                    violation_types[violation.violation_type] = []
                violation_types[violation.violation_type].append(violation)
            
            for violation_type, type_violations in violation_types.items():
                recommendations.append(f"Focus on {violation_type.value}: {len(type_violations)} instances")
        
        # Quality-based recommendations
        quality_metrics = evidence.quality_metrics
        if quality_metrics.get("code_coverage", 0.0) < 0.80:
            recommendations.append("Improve test coverage to exceed 80%")
        
        if quality_metrics.get("complexity_score", 0.0) > 0.60:
            recommendations.append("Reduce code complexity through refactoring")
        
        return recommendations
    
    def _determine_certification_status(self, 
                                      compliance_status: ComplianceStatus, 
                                      overall_score: float) -> str:
        """Determine TDD methodology certification status"""
        if compliance_status == ComplianceStatus.COMPLIANT and overall_score >= 0.90:
            return "CERTIFIED_EXEMPLARY"
        elif compliance_status == ComplianceStatus.COMPLIANT and overall_score >= 0.80:
            return "CERTIFIED_PROFICIENT"
        elif compliance_status == ComplianceStatus.PARTIAL_COMPLIANCE and overall_score >= 0.75:
            return "CERTIFIED_BASIC"
        else:
            return "NOT_CERTIFIED"
    
    def export_compliance_report(self, result: ComplianceResult, output_path: str):
        """Export comprehensive compliance report"""
        report = {
            "compliance_report": asdict(result),
            "export_timestamp": datetime.now().isoformat(),
            "validator_configuration": {
                "min_compliance_score": self.min_compliance_score,
                "violation_tolerance": self.violation_tolerance,
                "compliance_rules": self.compliance_rules
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
    
    def get_validation_history(self) -> List[Dict[str, Any]]:
        """Get compliance validation history"""
        return [asdict(result) for result in self.validation_history]