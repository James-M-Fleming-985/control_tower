#!/usr/bin/env python3
"""
Simplified UI Layer Requirements Tracer
LAY-003-02-01-003: User Interface Layer (SIMPLIFIED - Terminal Only)

This tracer validates the SIMPLIFIED terminal-only UI requirements.
Mobile, dashboard, and WebSocket features have been moved to SYS-003-04 (DEFERRED).

Date: 2025-10-06
"""

import os
import ast
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
from datetime import datetime


class ComplianceStatus(Enum):
    """Evidence-based compliance status"""
    MET = "✅ MET"
    PARTIAL = "🟡 PARTIAL"
    NOT_MET = "❌ NOT_MET"


@dataclass
class Implementation:
    """Implementation details for acceptance criterion"""
    file_path: str
    class_name: Optional[str] = None
    method_name: Optional[str] = None
    description: str = ""
    
    def exists(self) -> bool:
        return os.path.exists(self.file_path)


@dataclass
class Verification:
    """Verification details for acceptance criterion"""
    test_file: str
    test_method: str
    
    def exists(self) -> bool:
        return os.path.exists(self.test_file)


@dataclass
class Evidence:
    """Concrete evidence for requirement compliance"""
    implementation_verified: bool = False
    test_verified: bool = False
    notes: List[str] = field(default_factory=list)


@dataclass
class AcceptanceCriterion:
    """Single acceptance criterion for a requirement"""
    criterion_id: str
    description: str
    implementation: Optional[Implementation] = None
    verification: Optional[Verification] = None
    status: ComplianceStatus = ComplianceStatus.NOT_MET
    evidence: Evidence = field(default_factory=Evidence)


@dataclass
class Requirement:
    """Full requirement with acceptance criteria"""
    requirement_id: str
    requirement_type: str
    description: str
    acceptance_criteria: List[AcceptanceCriterion] = field(default_factory=list)
    
    def calculate_compliance(self) -> float:
        if not self.acceptance_criteria:
            return 0.0
        met_count = sum(1 for ac in self.acceptance_criteria if ac.status == ComplianceStatus.MET)
        partial_count = sum(0.5 for ac in self.acceptance_criteria if ac.status == ComplianceStatus.PARTIAL)
        total = len(self.acceptance_criteria)
        return (met_count + partial_count) / total * 100


class SimplifiedUILayerTracer:
    """Simplified tracer for terminal-only UI Layer requirements"""
    
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.project_root = self.repo_root / "projects/PROJECT-003 TDD ENFORCER"
        print("🔍 Indexing workspace files...")
        self.file_index = self._build_file_index()
        print(f"   Found {len(self.file_index)} Python files")
        self.requirements: Dict[str, Requirement] = {}
        self.evidence_log: List[Dict[str, Any]] = []
    
    def _build_file_index(self) -> Dict[str, str]:
        """Build index of all Python files in workspace"""
        file_index = {}
        exclude_dirs = {'.venv', '__pycache__', '.git', 'node_modules'}
        for root, dirs, files in os.walk(self.repo_root):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for filename in files:
                if filename.endswith('.py'):
                    full_path = os.path.join(root, filename)
                    if filename not in file_index:
                        file_index[filename] = full_path
        return file_index
    
    def _find_file(self, filename: str) -> Optional[str]:
        return self.file_index.get(filename)
    
    def _get_file_path(self, filename: str) -> str:
        found = self._find_file(filename)
        if found:
            return found
        default_location = self.project_root / "src/user_interface" / filename
        return str(default_location)
    
    def _verify_method_exists(self, file_path: str, method_name: str) -> bool:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.name == method_name:
                        return True
            return False
        except Exception as e:
            self.evidence_log.append({'file': file_path, 'method': method_name, 'error': str(e), 'type': 'method_verification_error'})
            return False
    
    def _verify_class_exists(self, file_path: str, class_name: str) -> bool:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if node.name == class_name:
                        return True
            return False
        except Exception as e:
            self.evidence_log.append({'file': file_path, 'class': class_name, 'error': str(e), 'type': 'class_verification_error'})
            return False
    
    def validate_requirement(self, requirement: Requirement):
        """Validate requirement and collect evidence"""
        for ac in requirement.acceptance_criteria:
            evidence_notes = []
            
            if ac.implementation:
                impl = ac.implementation
                if impl.exists():
                    ac.evidence.implementation_verified = True
                    evidence_notes.append(f"✅ Implementation file exists: {Path(impl.file_path).name}")
                    
                    if impl.class_name:
                        if self._verify_class_exists(impl.file_path, impl.class_name):
                            evidence_notes.append(f"✅ Class exists: {impl.class_name}")
                        else:
                            evidence_notes.append(f"⚠️ Class not found: {impl.class_name}")
                    
                    if impl.method_name:
                        if self._verify_method_exists(impl.file_path, impl.method_name):
                            evidence_notes.append(f"✅ Method exists: {impl.method_name}")
                            ac.evidence.implementation_verified = True
                        else:
                            evidence_notes.append(f"❌ Method not found: {impl.method_name}")
                            ac.evidence.implementation_verified = False
                else:
                    evidence_notes.append(f"❌ Implementation file missing: {Path(impl.file_path).name}")
            
            if ac.verification:
                verif = ac.verification
                if verif.exists():
                    ac.evidence.test_verified = True
                    evidence_notes.append(f"✅ Test file exists: {Path(verif.test_file).name}")
                    if self._verify_method_exists(verif.test_file, verif.test_method):
                        evidence_notes.append(f"✅ Test method exists: {verif.test_method}")
                    else:
                        evidence_notes.append(f"⚠️ Test method not found: {verif.test_method}")
                else:
                    evidence_notes.append(f"⚠️ Test file not found: {Path(verif.test_file).name}")
            
            ac.evidence.notes = evidence_notes
            
            if ac.evidence.implementation_verified and ac.evidence.test_verified:
                ac.status = ComplianceStatus.MET
            elif ac.evidence.implementation_verified or ac.evidence.test_verified:
                ac.status = ComplianceStatus.PARTIAL
            else:
                ac.status = ComplianceStatus.NOT_MET
        
        self.requirements[requirement.requirement_id] = requirement
    
    def generate_report(self) -> str:
        """Generate comprehensive compliance report"""
        report = []
        report.append("=" * 80)
        report.append("UI LAYER REQUIREMENTS TRACEABILITY REPORT (SIMPLIFIED)")
        report.append("LAY-003-02-01-003: User Interface Layer (Terminal-Only)")
        report.append("=" * 80)
        report.append("")
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        report.append("Project: PROJECT-003 TDD ENFORCER / SYSTEM-003-02 / FEATURE-003-02-01")
        report.append("")
        report.append("NOTE: Mobile, dashboard, and WebSocket features moved to SYS-003-04 (DEFERRED)")
        report.append("")
        report.append("")
        
        req_types = {}
        for req in self.requirements.values():
            if req.requirement_type not in req_types:
                req_types[req.requirement_type] = []
            req_types[req.requirement_type].append(req)
        
        for req_type, reqs in sorted(req_types.items()):
            report.append("=" * 80)
            report.append(f"{req_type.upper()} REQUIREMENTS")
            report.append("=" * 80)
            report.append("")
            
            for req in reqs:
                compliance = req.calculate_compliance()
                status_icon = "✅" if compliance >= 90 else "🟡" if compliance >= 50 else "❌"
                
                report.append(f"{status_icon} {req.requirement_id}: {req.description}")
                report.append(f"   Compliance: {compliance:.1f}%")
                report.append(f"   Acceptance Criteria: {len(req.acceptance_criteria)}")
                report.append("-" * 80)
                report.append("")
                
                for ac in req.acceptance_criteria:
                    report.append(f"{ac.status.value} {ac.criterion_id}: {ac.description}")
                    if ac.implementation:
                        impl_file = Path(ac.implementation.file_path).name
                        report.append(f"   Implementation: {impl_file}")
                        if ac.implementation.method_name:
                            report.append(f"   Method: {ac.implementation.method_name}")
                    if ac.verification:
                        test_file = Path(ac.verification.test_file).name
                        report.append(f"   Test: {test_file}")
                        report.append(f"   Test Method: {ac.verification.test_method}")
                    report.append("   Evidence:")
                    for note in ac.evidence.notes:
                        report.append(f"     {note}")
                    report.append("")
                
                report.append("")
        
        report.append("=" * 80)
        report.append("OVERALL SUMMARY")
        report.append("=" * 80)
        report.append("")
        
        total_reqs = len(self.requirements)
        total_criteria = sum(len(req.acceptance_criteria) for req in self.requirements.values())
        met_count = sum(sum(1 for ac in req.acceptance_criteria if ac.status == ComplianceStatus.MET) for req in self.requirements.values())
        partial_count = sum(sum(1 for ac in req.acceptance_criteria if ac.status == ComplianceStatus.PARTIAL) for req in self.requirements.values())
        overall_compliance = (met_count + partial_count * 0.5) / total_criteria * 100 if total_criteria > 0 else 0
        
        report.append(f"Total Requirements: {total_reqs}")
        report.append(f"Total Acceptance Criteria: {total_criteria}")
        report.append(f"Criteria MET: {met_count} ({met_count/total_criteria*100:.1f}%)")
        report.append(f"Criteria PARTIAL: {partial_count} ({partial_count/total_criteria*100:.1f}%)")
        report.append(f"Overall Compliance: {overall_compliance:.1f}%")
        report.append("")
        
        if overall_compliance >= 90:
            rating = "✅ EXCELLENT - Ready for deployment"
        elif overall_compliance >= 70:
            rating = "🟡 GOOD - Minor gaps to address"
        elif overall_compliance >= 50:
            rating = "⚠️ FAIR - Significant work needed"
        else:
            rating = "❌ POOR - Major implementation gaps"
        
        report.append(f"Compliance Rating: {rating}")
        report.append("")
        
        return "\n".join(report)
    
    def save_evidence_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump(self.evidence_log, f, indent=2)
    
    # SIMPLIFIED REQUIREMENTS (Terminal-Only)
    
    def define_req_ui_001(self) -> Requirement:
        """Validation Start Display"""
        req = Requirement(
            requirement_id="REQ-UI-001",
            requirement_type="Functional",
            description="Validation Start Display - Terminal output with context"
        )
        ac = AcceptanceCriterion(
            criterion_id="AC-UI-001-01",
            description="Display validation start message with layer/feature/system context",
            implementation=Implementation(
                file_path=self._get_file_path("terminal_output.py"),
                class_name="TerminalUI",
                method_name="display_validation_start"
            ),
            verification=Verification(
                test_file=self._get_file_path("test_terminal_output.py"),
                test_method="test_validation_start_display"
            )
        )
        req.acceptance_criteria.append(ac)
        return req
    
    def define_req_ui_002(self) -> Requirement:
        """Test Progress Indicators"""
        req = Requirement(
            requirement_id="REQ-UI-002",
            requirement_type="Functional",
            description="Test Progress Indicators - Real-time test result display"
        )
        ac = AcceptanceCriterion(
            criterion_id="AC-UI-002-01",
            description="Display test results as they complete with pass/fail icons",
            implementation=Implementation(
                file_path=self._get_file_path("terminal_output.py"),
                method_name="display_test_result"
            ),
            verification=Verification(
                test_file=self._get_file_path("test_terminal_output.py"),
                test_method="test_test_result_display"
            )
        )
        req.acceptance_criteria.append(ac)
        return req
    
    def define_req_ui_003(self) -> Requirement:
        """Pyramid Statistics Display"""
        req = Requirement(
            requirement_id="REQ-UI-003",
            requirement_type="Functional",
            description="Pyramid Statistics Display - Text-based pyramid summary"
        )
        ac = AcceptanceCriterion(
            criterion_id="AC-UI-003-01",
            description="Display test counts by pyramid level with pass rates",
            implementation=Implementation(
                file_path=self._get_file_path("terminal_output.py"),
                method_name="display_pyramid_summary"
            ),
            verification=Verification(
                test_file=self._get_file_path("test_terminal_output.py"),
                test_method="test_pyramid_summary_display"
            )
        )
        req.acceptance_criteria.append(ac)
        return req
    
    def define_req_ui_004(self) -> Requirement:
        """Compliance Status Display"""
        req = Requirement(
            requirement_id="REQ-UI-004",
            requirement_type="Functional",
            description="Compliance Status Display - Clear pass/fail result"
        )
        ac = AcceptanceCriterion(
            criterion_id="AC-UI-004-01",
            description="Display validation result with reasoning",
            implementation=Implementation(
                file_path=self._get_file_path("terminal_output.py"),
                method_name="display_validation_result"
            ),
            verification=Verification(
                test_file=self._get_file_path("test_terminal_output.py"),
                test_method="test_validation_result_display"
            )
        )
        req.acceptance_criteria.append(ac)
        return req
    
    def define_req_ui_005(self) -> Requirement:
        """Error Message Display"""
        req = Requirement(
            requirement_id="REQ-UI-005",
            requirement_type="Functional",
            description="Error Message Display - Clear error reporting"
        )
        ac = AcceptanceCriterion(
            criterion_id="AC-UI-005-01",
            description="Display clear error messages with actionable guidance",
            implementation=Implementation(
                file_path=self._get_file_path("terminal_output.py"),
                method_name="display_error"
            ),
            verification=Verification(
                test_file=self._get_file_path("test_terminal_output.py"),
                test_method="test_error_display"
            )
        )
        req.acceptance_criteria.append(ac)
        return req
    
    def define_req_ui_006(self) -> Requirement:
        """Execution Summary"""
        req = Requirement(
            requirement_id="REQ-UI-006",
            requirement_type="Functional",
            description="Execution Summary - Complete validation overview"
        )
        ac = AcceptanceCriterion(
            criterion_id="AC-UI-006-01",
            description="Display comprehensive summary with timing and totals",
            implementation=Implementation(
                file_path=self._get_file_path("terminal_output.py"),
                method_name="display_execution_summary"
            ),
            verification=Verification(
                test_file=self._get_file_path("test_terminal_output.py"),
                test_method="test_execution_summary_display"
            )
        )
        req.acceptance_criteria.append(ac)
        return req


if __name__ == "__main__":
    tracer = SimplifiedUILayerTracer(repo_root="/workspaces/control_tower")
    
    print("=" * 80)
    print("SIMPLIFIED UI LAYER REQUIREMENTS TRACER (Terminal-Only)")
    print("Evidence-Based Compliance Validation")
    print("=" * 80)
    print()
    
    print("Defining simplified requirements...")
    requirements = [
        tracer.define_req_ui_001(),
        tracer.define_req_ui_002(),
        tracer.define_req_ui_003(),
        tracer.define_req_ui_004(),
        tracer.define_req_ui_005(),
        tracer.define_req_ui_006(),
    ]
    print(f"✅ Defined {len(requirements)} requirements (down from 18)")
    print()
    
    print("Validating requirements with concrete evidence...")
    for req in requirements:
        tracer.validate_requirement(req)
        print(f"  ✅ Validated {req.requirement_id}")
    print()
    
    print("Generating evidence-based compliance report...")
    report = tracer.generate_report()
    print(report)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(
        "/workspaces/control_tower/projects/PROJECT-003 TDD ENFORCER/"
        "SYSTEM-003-02 EXTENDED VALIDATION ENGINE/"
        "FEATURE-003-02-01 TESTING PYRAMID VALIDATION ENGINE/"
        "USER INTERFACE LAYER"
    )
    
    report_file = output_dir / f"UI_LAYER_SIMPLIFIED_TRACEABILITY_REPORT_{timestamp}.txt"
    evidence_file = output_dir / f"ui_layer_simplified_evidence_log_{timestamp}.json"
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    tracer.save_evidence_log(str(evidence_file))
    
    print(f"\n✅ Simplified traceability report saved!")
    print(f"   Report: {report_file.name}")
    print(f"   Evidence: {evidence_file.name}")
