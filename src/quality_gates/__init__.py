#!/usr/bin/env python3
"""
Quality Gate Base Classes - TR-QG-001
Automated Professional Standards Enforcement

This module provides the foundation for automated quality gates
that prevent progression without professional standards compliance.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import datetime
import json
from pathlib import Path


class QualityGateStatus(Enum):
    """Status of quality gate execution"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress" 
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class QualityGateResult:
    """Result of quality gate execution"""
    gate_name: str
    status: QualityGateStatus
    timestamp: datetime.datetime
    validation_results: Dict[str, Any]
    evidence_files: List[str]
    violations: List[str]
    recommendations: List[str]
    blocking_issues: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "gate_name": self.gate_name,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "validation_results": self.validation_results,
            "evidence_files": self.evidence_files,
            "violations": self.violations,
            "recommendations": self.recommendations,
            "blocking_issues": self.blocking_issues
        }


class ProfessionalStandardsViolation(Exception):
    """Exception raised when professional standards are violated"""
    
    def __init__(self, message: str, violations: List[str] = None, gate_name: str = None):
        super().__init__(message)
        self.violations = violations or []
        self.gate_name = gate_name


class QualityGate(ABC):
    """
    Abstract base class for all quality gates
    
    Quality gates enforce professional standards at specific points
    in the development workflow, preventing progression when standards
    are not met.
    """
    
    def __init__(self, gate_name: str, workspace_root: str = "/workspaces/control_tower"):
        self.gate_name = gate_name
        self.workspace_root = Path(workspace_root)
        self.evidence_dir = self.workspace_root / "evidence" / "quality_gates"
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        
    @abstractmethod
    def validate_pre_execution(self, context: Dict[str, Any]) -> QualityGateResult:
        """Validate conditions before execution"""
        pass
    
    @abstractmethod
    def monitor_execution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor execution for quality violations"""
        pass
    
    @abstractmethod
    def validate_post_execution(self, context: Dict[str, Any]) -> QualityGateResult:
        """Validate results after execution"""
        pass
    
    def execute_quality_gate(self, context: Dict[str, Any]) -> QualityGateResult:
        """
        Execute complete quality gate with pre/monitor/post validation
        
        This is the main entry point that orchestrates the quality gate execution
        and ensures professional standards are met before allowing progression.
        """
        print(f"🔐 QUALITY GATE: {self.gate_name}")
        print("-" * 50)
        
        try:
            # Pre-execution validation
            print("  🔍 Pre-execution validation...")
            pre_result = self.validate_pre_execution(context)
            if pre_result.status == QualityGateStatus.FAILED:
                return self._create_failed_result("Pre-execution validation failed", pre_result.violations)
            
            # Monitor execution
            print("  📊 Monitoring execution...")
            monitoring_data = self.monitor_execution(context)
            context.update(monitoring_data)
            
            # Post-execution validation
            print("  ✅ Post-execution validation...")
            post_result = self.validate_post_execution(context)
            
            # Generate evidence
            evidence_file = self._generate_evidence(context, pre_result, post_result)
            post_result.evidence_files.append(evidence_file)
            
            # Display results
            self._display_gate_results(post_result)
            
            return post_result
            
        except Exception as e:
            error_result = self._create_failed_result(f"Quality gate execution error: {str(e)}", [str(e)])
            self._display_gate_results(error_result)
            return error_result
    
    def _create_failed_result(self, message: str, violations: List[str]) -> QualityGateResult:
        """Create a failed quality gate result"""
        return QualityGateResult(
            gate_name=self.gate_name,
            status=QualityGateStatus.FAILED,
            timestamp=datetime.datetime.now(),
            validation_results={"error": message},
            evidence_files=[],
            violations=violations,
            recommendations=[f"Fix violations in {self.gate_name} before proceeding"],
            blocking_issues=violations
        )
    
    def _generate_evidence(self, context: Dict[str, Any], pre_result: QualityGateResult, post_result: QualityGateResult) -> str:
        """Generate immutable evidence file for quality gate execution"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        evidence_filename = f"{self.gate_name}_{timestamp}_evidence.json"
        evidence_path = self.evidence_dir / evidence_filename
        
        evidence_data = {
            "gate_name": self.gate_name,
            "execution_timestamp": timestamp,
            "context": {k: str(v) for k, v in context.items()},  # Convert to strings for JSON
            "pre_validation": pre_result.to_dict(),
            "post_validation": post_result.to_dict(),
            "professional_standards_compliance": post_result.status == QualityGateStatus.PASSED
        }
        
        with open(evidence_path, 'w') as f:
            json.dump(evidence_data, f, indent=2, default=str)
        
        return str(evidence_path)
    
    def _display_gate_results(self, result: QualityGateResult):
        """Display quality gate results"""
        if result.status == QualityGateStatus.PASSED:
            print(f"  ✅ {self.gate_name}: PROFESSIONAL STANDARDS MET")
        else:
            print(f"  ❌ {self.gate_name}: STANDARDS VIOLATION")
            for violation in result.violations:
                print(f"    🔥 {violation}")
            for recommendation in result.recommendations:
                print(f"    💡 {recommendation}")


class QualityGateOrchestrator:
    """
    Orchestrates execution of multiple quality gates in sequence
    
    Ensures that all quality gates pass before allowing workflow progression.
    Provides centralized evidence collection and professional standards enforcement.
    """
    
    def __init__(self, workspace_root: str = "/workspaces/control_tower"):
        self.workspace_root = Path(workspace_root)
        self.evidence_dir = self.workspace_root / "evidence" / "orchestrator"
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.gates: List[QualityGate] = []
    
    def add_gate(self, gate: QualityGate):
        """Add a quality gate to the orchestrator"""
        self.gates.append(gate)
    
    def execute_all_gates(self, context: Dict[str, Any]) -> Dict[str, QualityGateResult]:
        """
        Execute all quality gates in sequence
        
        If any gate fails, execution stops and the failure is reported.
        This enforces the professional standards requirement that ALL
        quality gates must pass before progression is allowed.
        """
        print("🛡️ EXECUTING PROFESSIONAL STANDARDS QUALITY GATES")
        print("=" * 60)
        
        results = {}
        
        for gate in self.gates:
            result = gate.execute_quality_gate(context)
            results[gate.gate_name] = result
            
            # Stop on first failure - no progression allowed
            if result.status == QualityGateStatus.FAILED:
                print(f"\n❌ QUALITY GATE FAILURE: {gate.gate_name}")
                print("🚫 BLOCKING FURTHER EXECUTION")
                raise ProfessionalStandardsViolation(
                    f"Quality gate {gate.gate_name} failed professional standards",
                    result.violations,
                    gate.gate_name
                )
        
        # All gates passed
        print("\n✅ ALL QUALITY GATES PASSED")
        print("✅ PROFESSIONAL STANDARDS MET")
        print("✅ PROGRESSION ALLOWED")
        
        # Generate orchestrator evidence
        self._generate_orchestrator_evidence(context, results)
        
        return results
    
    def _generate_orchestrator_evidence(self, context: Dict[str, Any], results: Dict[str, QualityGateResult]):
        """Generate evidence for complete orchestrator execution"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        evidence_filename = f"orchestrator_{timestamp}_evidence.json"
        evidence_path = self.evidence_dir / evidence_filename
        
        evidence_data = {
            "orchestrator_execution": timestamp,
            "context": {k: str(v) for k, v in context.items()},
            "gate_results": {name: result.to_dict() for name, result in results.items()},
            "overall_status": "PASSED" if all(r.status == QualityGateStatus.PASSED for r in results.values()) else "FAILED",
            "professional_standards_compliance": True
        }
        
        with open(evidence_path, 'w') as f:
            json.dump(evidence_data, f, indent=2, default=str)
        
        print(f"📄 Orchestrator Evidence: {evidence_path}")


def create_professional_standards_context(**kwargs) -> Dict[str, Any]:
    """Create a context dictionary for quality gate execution"""
    return {
        "timestamp": datetime.datetime.now(),
        "workspace_root": "/workspaces/control_tower",
        "professional_standards_version": "1.0",
        "code_quality_validation": True,
        "test_pyramid_validation": True,
        **kwargs
    }


# Import code quality validator functions
try:
    from .code_quality_validator import CodeQualityValidator, validate_test_pyramid_component
    
    def validate_component_quality(component_path: str, component_name: str) -> QualityGateResult:
        """
        Validate component code quality as part of professional standards
        
        This integrates code quality validation (imports, syntax, dependencies)
        into our professional standards forcing function framework.
        """
        return validate_test_pyramid_component(component_path, component_name)
        
except ImportError:
    # Fallback if code quality validator not available
    def validate_component_quality(component_path: str, component_name: str) -> QualityGateResult:
        return QualityGateResult(
            gate_name=f"CodeQuality_{component_name}",
            status=QualityGateStatus.FAILED,
            timestamp=datetime.datetime.now(),
            validation_results={},
            evidence_files=[],
            violations=["Code quality validator not available"],
            recommendations=["Install code quality validator"],
            blocking_issues=["Missing validation framework"]
        )