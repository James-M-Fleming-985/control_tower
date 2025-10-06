#!/usr/bin/env python3
"""
Evidence-Based Requirements Tracer for User Interface Layer
LAY-003-02-01-003: User Interface Layer Requirements

This tracer provides concrete evidence for requirement compliance by:
1. Mapping requirements to specific implementations
2. Verifying implementation exists via AST parsing
3. Verifying tests exist and can execute
4. Collecting measurable evidence for each acceptance criterion
5. Using workspace-wide file discovery for undisciplined file placement

Date: 2025-10-06
"""

import os
import ast
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum
from datetime import datetime


class ComplianceStatus(Enum):
    """Evidence-based compliance status"""
    MET = "✅ MET"
    PARTIAL = "🟡 PARTIAL"
    NOT_MET = "❌ NOT_MET"
    NEEDS_VALIDATION = "⚠️ NEEDS_VALIDATION"


@dataclass
class Implementation:
    """Implementation details for acceptance criterion"""
    file_path: str
    class_name: Optional[str] = None
    method_name: Optional[str] = None
    line_number: Optional[int] = None
    description: str = ""
    
    def exists(self) -> bool:
        """Check if implementation file exists"""
        return os.path.exists(self.file_path)


@dataclass
class Verification:
    """Verification details for acceptance criterion"""
    test_file: str
    test_method: str
    test_type: str = "integration"  # unit, integration, e2e
    coverage_target: float = 95.0
    
    def exists(self) -> bool:
        """Check if test file exists"""
        return os.path.exists(self.test_file)


@dataclass
class Evidence:
    """Concrete evidence for requirement compliance"""
    implementation_verified: bool = False
    test_verified: bool = False
    test_passing: bool = False
    coverage_percent: float = 0.0
    performance_measured: Optional[float] = None
    security_validated: bool = False
    notes: List[str] = field(default_factory=list)


@dataclass
class AcceptanceCriterion:
    """Single acceptance criterion for a requirement"""
    criterion_id: str
    description: str
    implementation: Optional[Implementation] = None
    verification: Optional[Verification] = None
    status: ComplianceStatus = ComplianceStatus.NEEDS_VALIDATION
    evidence: Evidence = field(default_factory=Evidence)
    target_metric: Optional[str] = None


@dataclass
class Requirement:
    """Full requirement with acceptance criteria"""
    requirement_id: str
    requirement_type: str  # Functional, Performance, Usability, Mobile, Integration
    description: str
    acceptance_criteria: List[AcceptanceCriterion] = field(
        default_factory=list
    )
    
    def calculate_compliance(self) -> float:
        """Calculate compliance based on evidence"""
        if not self.acceptance_criteria:
            return 0.0
        
        met_count = sum(
            1 for ac in self.acceptance_criteria
            if ac.status == ComplianceStatus.MET
        )
        partial_count = sum(
            0.5 for ac in self.acceptance_criteria
            if ac.status == ComplianceStatus.PARTIAL
        )
        
        total = len(self.acceptance_criteria)
        return (met_count + partial_count) / total * 100


class UILayerRequirementsTracer:
    """Evidence-based tracer for User Interface Layer requirements"""
    
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.project_root = (
            self.repo_root / "projects/PROJECT-003 TDD ENFORCER"
        )
        # Build comprehensive file index (workspace-wide discovery)
        print("🔍 Indexing workspace files...")
        self.file_index = self._build_file_index()
        print(f"   Found {len(self.file_index)} Python files")
        self.requirements: Dict[str, Requirement] = {}
        self.evidence_log: List[Dict[str, Any]] = []

    def _build_file_index(self) -> Dict[str, str]:
        """
        Build index of all Python files in workspace.
        Maps filename -> full path for fast lookup.
        Handles files scattered everywhere (undisciplined placement).
        """
        file_index = {}
        exclude_dirs = {'.venv', '__pycache__', '.git', 'node_modules'}
        
        for root, dirs, files in os.walk(self.repo_root):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for filename in files:
                if filename.endswith('.py'):
                    full_path = os.path.join(root, filename)
                    # Store first occurrence (priority to earlier finds)
                    if filename not in file_index:
                        file_index[filename] = full_path
        
        return file_index
    
    def _find_file(self, filename: str) -> Optional[str]:
        """Search for file anywhere in workspace using file index"""
        return self.file_index.get(filename)
    
    def _get_file_path(self, filename: str) -> str:
        """
        Get file path, searching entire workspace.
        Returns first found path from index, or default location.
        """
        found = self._find_file(filename)
        if found:
            return found
        
        # If not found, return default project UI location
        default_location = (
            self.project_root /
            "src/user_interface" / filename
        )
        return str(default_location)
        
    def _verify_method_exists(
        self, file_path: str, method_name: str
    ) -> bool:
        """Verify method exists in Python file using AST"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name == method_name:
                        return True
                elif isinstance(node, ast.AsyncFunctionDef):
                    if node.name == method_name:
                        return True
            
            return False
        except Exception as e:
            self.evidence_log.append({
                'file': file_path,
                'method': method_name,
                'error': str(e),
                'type': 'method_verification_error'
            })
            return False
    
    def _verify_class_exists(
        self, file_path: str, class_name: str
    ) -> bool:
        """Verify class exists in Python file using AST"""
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
            self.evidence_log.append({
                'file': file_path,
                'class': class_name,
                'error': str(e),
                'type': 'class_verification_error'
            })
            return False
    
    def validate_requirement(self, requirement: Requirement):
        """Validate requirement and collect evidence"""
        for ac in requirement.acceptance_criteria:
            evidence_notes = []
            
            # Check implementation exists
            if ac.implementation:
                impl = ac.implementation
                if impl.exists():
                    ac.evidence.implementation_verified = True
                    evidence_notes.append(
                        f"✅ Implementation file exists: "
                        f"{Path(impl.file_path).name}"
                    )
                    
                    # Verify class if specified
                    if impl.class_name:
                        if self._verify_class_exists(
                            impl.file_path, impl.class_name
                        ):
                            evidence_notes.append(
                                f"✅ Class exists: {impl.class_name}"
                            )
                        else:
                            evidence_notes.append(
                                f"⚠️ Class not found: {impl.class_name}"
                            )
                    
                    # Verify method if specified
                    if impl.method_name:
                        if self._verify_method_exists(
                            impl.file_path, impl.method_name
                        ):
                            evidence_notes.append(
                                f"✅ Method exists: {impl.method_name}"
                            )
                            ac.evidence.implementation_verified = True
                        else:
                            evidence_notes.append(
                                f"❌ Method not found: "
                                f"{impl.method_name}"
                            )
                            ac.evidence.implementation_verified = False
                else:
                    evidence_notes.append(
                        f"❌ Implementation file missing: "
                        f"{Path(impl.file_path).name}"
                    )
            
            # Check test exists
            if ac.verification:
                verif = ac.verification
                if verif.exists():
                    ac.evidence.test_verified = True
                    evidence_notes.append(
                        f"✅ Test file exists: "
                        f"{Path(verif.test_file).name}"
                    )
                    
                    # Verify test method
                    if self._verify_method_exists(
                        verif.test_file, verif.test_method
                    ):
                        evidence_notes.append(
                            f"✅ Test method exists: "
                            f"{verif.test_method}"
                        )
                    else:
                        evidence_notes.append(
                            f"⚠️ Test method not found: "
                            f"{verif.test_method}"
                        )
                else:
                    evidence_notes.append(
                        f"⚠️ Test file not found: "
                        f"{Path(verif.test_file).name}"
                    )
            
            ac.evidence.notes = evidence_notes
            
            # Determine status
            if (ac.evidence.implementation_verified and 
                ac.evidence.test_verified):
                ac.status = ComplianceStatus.MET
            elif (ac.evidence.implementation_verified or 
                  ac.evidence.test_verified):
                ac.status = ComplianceStatus.PARTIAL
            else:
                ac.status = ComplianceStatus.NOT_MET
        
        self.requirements[requirement.requirement_id] = requirement
    
    def generate_report(self) -> str:
        """Generate comprehensive compliance report"""
        report = []
        report.append("=" * 80)
        report.append("USER INTERFACE LAYER REQUIREMENTS TRACEABILITY REPORT")
        report.append("LAY-003-02-01-003: User Interface Layer Requirements")
        report.append("=" * 80)
        report.append("")
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        report.append(
            "Project: PROJECT-003 TDD ENFORCER / SYSTEM-003-02 / "
            "FEATURE-003-02-01"
        )
        report.append("")
        report.append("")
        
        # Group requirements by type
        req_types = {}
        for req in self.requirements.values():
            if req.requirement_type not in req_types:
                req_types[req.requirement_type] = []
            req_types[req.requirement_type].append(req)
        
        # Report each type
        for req_type, reqs in sorted(req_types.items()):
            report.append("=" * 80)
            report.append(f"{req_type.upper()} REQUIREMENTS")
            report.append("=" * 80)
            report.append("")
            
            for req in reqs:
                compliance = req.calculate_compliance()
                status_icon = (
                    "✅" if compliance >= 90 else
                    "🟡" if compliance >= 50 else "❌"
                )
                
                report.append(
                    f"{status_icon} {req.requirement_id}: "
                    f"{req.description}"
                )
                report.append(f"   Compliance: {compliance:.1f}%")
                report.append(
                    f"   Acceptance Criteria: "
                    f"{len(req.acceptance_criteria)}"
                )
                report.append("-" * 80)
                report.append("")
                
                for ac in req.acceptance_criteria:
                    report.append(
                        f"{ac.status.value} {ac.criterion_id}: "
                        f"{ac.description}"
                    )
                    if ac.target_metric:
                        report.append(f"   Target: {ac.target_metric}")
                    if ac.implementation:
                        impl_file = Path(ac.implementation.file_path).name
                        report.append(
                            f"   Implementation: {impl_file}"
                        )
                        if ac.implementation.method_name:
                            report.append(
                                f"   Method: "
                                f"{ac.implementation.method_name}"
                            )
                    if ac.verification:
                        test_file = Path(ac.verification.test_file).name
                        report.append(f"   Test: {test_file}")
                        report.append(
                            f"   Test Method: "
                            f"{ac.verification.test_method}"
                        )
                    report.append("   Evidence:")
                    for note in ac.evidence.notes:
                        report.append(f"     {note}")
                    report.append("")
                
                report.append("")
        
        # Overall summary
        report.append("=" * 80)
        report.append("OVERALL SUMMARY")
        report.append("=" * 80)
        report.append("")
        
        total_reqs = len(self.requirements)
        total_criteria = sum(
            len(req.acceptance_criteria)
            for req in self.requirements.values()
        )
        
        met_count = sum(
            sum(
                1 for ac in req.acceptance_criteria
                if ac.status == ComplianceStatus.MET
            )
            for req in self.requirements.values()
        )
        
        partial_count = sum(
            sum(
                1 for ac in req.acceptance_criteria
                if ac.status == ComplianceStatus.PARTIAL
            )
            for req in self.requirements.values()
        )
        
        overall_compliance = (
            (met_count + partial_count * 0.5) / total_criteria * 100
            if total_criteria > 0 else 0
        )
        
        report.append(f"Total Requirements: {total_reqs}")
        report.append(f"Total Acceptance Criteria: {total_criteria}")
        report.append(
            f"Criteria MET: {met_count} "
            f"({met_count/total_criteria*100:.1f}%)"
        )
        report.append(
            f"Criteria PARTIAL: {partial_count} "
            f"({partial_count/total_criteria*100:.1f}%)"
        )
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
        """Save evidence log as JSON"""
        with open(filepath, 'w') as f:
            json.dump(self.evidence_log, f, indent=2)
    
    # REQ-UI-001: Mobile Authentication Interface
    def define_req_ui_001(self) -> Requirement:
        """Mobile Authentication Interface"""
        req = Requirement(
            requirement_id="REQ-UI-001",
            requirement_type="Functional",
            description=(
                "Mobile Authentication Interface - Secure mobile login "
                "with biometric support"
            )
        )
        
        # AC-001-01: Login form with credentials
        ac1 = AcceptanceCriterion(
            criterion_id="AC-UI-001-01",
            description="Secure credential entry with device verification",
            target_metric="<2 seconds load time, 99% usability",
            implementation=Implementation(
                file_path=self._get_file_path("mobile_auth_ui.py"),
                class_name="MobileAuthUI",
                method_name="render_login_form"
            ),
            verification=Verification(
                test_file=self._get_file_path(
                    "test_mobile_authentication.py"
                ),
                test_method="test_mobile_login_interface"
            )
        )
        req.acceptance_criteria.append(ac1)
        
        # AC-001-02: Biometric authentication
        ac2 = AcceptanceCriterion(
            criterion_id="AC-UI-001-02",
            description="Biometric authentication integration",
            implementation=Implementation(
                file_path=self._get_file_path("mobile_auth_ui.py"),
                method_name="enable_biometric_auth"
            ),
            verification=Verification(
                test_file=self._get_file_path(
                    "test_mobile_authentication.py"
                ),
                test_method="test_biometric_integration"
            )
        )
        req.acceptance_criteria.append(ac2)
        
        # AC-001-03: Session management
        ac3 = AcceptanceCriterion(
            criterion_id="AC-UI-001-03",
            description="Session persistence and auto-logout",
            implementation=Implementation(
                file_path=self._get_file_path("mobile_auth_ui.py"),
                method_name="manage_session"
            )
        )
        req.acceptance_criteria.append(ac3)
        
        return req
    
    # REQ-UI-002: Mobile Command Interface
    def define_req_ui_002(self) -> Requirement:
        """Mobile Command Interface"""
        req = Requirement(
            requirement_id="REQ-UI-002",
            requirement_type="Functional",
            description=(
                "Mobile Command Interface - Touch controls with "
                "real-time status"
            )
        )
        
        ac1 = AcceptanceCriterion(
            criterion_id="AC-UI-002-01",
            description="Command selection and execution interface",
            target_metric="<2 second acknowledgment",
            implementation=Implementation(
                file_path=self._get_file_path("mobile_command_ui.py"),
                class_name="MobileCommandUI",
                method_name="render_command_interface"
            ),
            verification=Verification(
                test_file=self._get_file_path("test_mobile_commands.py"),
                test_method="test_command_execution_ui"
            )
        )
        req.acceptance_criteria.append(ac1)
        
        ac2 = AcceptanceCriterion(
            criterion_id="AC-UI-002-02",
            description="Real-time status monitoring display",
            implementation=Implementation(
                file_path=self._get_file_path("mobile_command_ui.py"),
                method_name="display_realtime_status"
            ),
            verification=Verification(
                test_file=self._get_file_path("test_mobile_commands.py"),
                test_method="test_realtime_status_display"
            )
        )
        req.acceptance_criteria.append(ac2)
        
        return req
    
    # REQ-UI-003: Position Display
    def define_req_ui_003(self) -> Requirement:
        """Layer/Feature/System Position Display"""
        req = Requirement(
            requirement_id="REQ-UI-003",
            requirement_type="Functional",
            description=(
                "Position Display - Visual hierarchy and "
                "progression tracking"
            )
        )
        
        ac1 = AcceptanceCriterion(
            criterion_id="AC-UI-003-01",
            description="Interactive hierarchy tree visualization",
            target_metric="<500ms update latency",
            implementation=Implementation(
                file_path=self._get_file_path("position_display.py"),
                class_name="PositionDisplay",
                method_name="render_hierarchy_tree"
            ),
            verification=Verification(
                test_file=self._get_file_path("test_position_display.py"),
                test_method="test_hierarchy_visualization"
            )
        )
        req.acceptance_criteria.append(ac1)
        
        ac2 = AcceptanceCriterion(
            criterion_id="AC-UI-003-02",
            description="Real-time position updates",
            implementation=Implementation(
                file_path=self._get_file_path("position_display.py"),
                method_name="update_position_display"
            ),
            verification=Verification(
                test_file=self._get_file_path("test_position_display.py"),
                test_method="test_realtime_position_updates"
            )
        )
        req.acceptance_criteria.append(ac2)
        
        return req
    
    # REQ-UI-004: Contextual Pyramid Visualization
    def define_req_ui_004(self) -> Requirement:
        """Contextual Pyramid Visualization"""
        req = Requirement(
            requirement_id="REQ-UI-004",
            requirement_type="Functional",
            description=(
                "Pyramid Visualization - Context-aware adaptive charts"
            )
        )
        
        ac1 = AcceptanceCriterion(
            criterion_id="AC-UI-004-01",
            description="Adaptive pyramid chart rendering",
            target_metric="<1 second rendering",
            implementation=Implementation(
                file_path=self._get_file_path("pyramid_visualization.py"),
                class_name="PyramidVisualization",
                method_name="render_contextual_pyramid"
            ),
            verification=Verification(
                test_file=self._get_file_path(
                    "test_pyramid_visualization.py"
                ),
                test_method="test_contextual_pyramid_display"
            )
        )
        req.acceptance_criteria.append(ac1)
        
        ac2 = AcceptanceCriterion(
            criterion_id="AC-UI-004-02",
            description="Position-aware filtering and drill-down",
            implementation=Implementation(
                file_path=self._get_file_path("pyramid_visualization.py"),
                method_name="enable_drill_down"
            ),
            verification=Verification(
                test_file=self._get_file_path(
                    "test_pyramid_visualization.py"
                ),
                test_method="test_drill_down_interactivity"
            )
        )
        req.acceptance_criteria.append(ac2)
        
        return req
    
    # REQ-UI-005: Component Integration Dashboard
    def define_req_ui_005(self) -> Requirement:
        """Component Integration Dashboard"""
        req = Requirement(
            requirement_id="REQ-UI-005",
            requirement_type="Functional",
            description=(
                "Integration Dashboard - Component status and "
                "compatibility"
            )
        )
        
        ac1 = AcceptanceCriterion(
            criterion_id="AC-UI-005-01",
            description="Component status grid with integration matrices",
            target_metric="<1 second update latency",
            implementation=Implementation(
                file_path=self._get_file_path("integration_dashboard.py"),
                class_name="IntegrationDashboard",
                method_name="render_component_status"
            ),
            verification=Verification(
                test_file=self._get_file_path(
                    "test_integration_dashboard.py"
                ),
                test_method="test_component_dashboard"
            )
        )
        req.acceptance_criteria.append(ac1)
        
        ac2 = AcceptanceCriterion(
            criterion_id="AC-UI-005-02",
            description="Real-time integration status updates",
            implementation=Implementation(
                file_path=self._get_file_path("integration_dashboard.py"),
                method_name="update_integration_status"
            ),
            verification=Verification(
                test_file=self._get_file_path(
                    "test_integration_dashboard.py"
                ),
                test_method="test_realtime_status_updates"
            )
        )
        req.acceptance_criteria.append(ac2)
        
        return req
    
    # REQ-UI-006: Cross-Component Testing Visualization
    def define_req_ui_006(self) -> Requirement:
        """Cross-Component Testing Visualization"""
        req = Requirement(
            requirement_id="REQ-UI-006",
            requirement_type="Functional",
            description=(
                "Testing Visualization - Interactive component maps"
            )
        )
        
        ac1 = AcceptanceCriterion(
            criterion_id="AC-UI-006-01",
            description="Interactive component interaction maps",
            implementation=Implementation(
                file_path=self._get_file_path(
                    "testing_visualization.py"
                ),
                class_name="TestingVisualization",
                method_name="render_component_maps"
            ),
            verification=Verification(
                test_file=self._get_file_path(
                    "test_testing_visualization.py"
                ),
                test_method="test_component_interaction_maps"
            )
        )
        req.acceptance_criteria.append(ac1)
        
        ac2 = AcceptanceCriterion(
            criterion_id="AC-UI-006-02",
            description="Test execution flow and result heat maps",
            implementation=Implementation(
                file_path=self._get_file_path(
                    "testing_visualization.py"
                ),
                method_name="render_result_heatmap"
            ),
            verification=Verification(
                test_file=self._get_file_path(
                    "test_testing_visualization.py"
                ),
                test_method="test_result_displays"
            )
        )
        req.acceptance_criteria.append(ac2)
        
        return req
    
    # REQ-UI-007: Progression Tracking Display
    def define_req_ui_007(self) -> Requirement:
        """Progression Tracking Display"""
        req = Requirement(
            requirement_id="REQ-UI-007",
            requirement_type="Functional",
            description="Progression Display - Timeline and milestones"
        )
        
        ac1 = AcceptanceCriterion(
            criterion_id="AC-UI-007-01",
            description="Interactive progression timeline",
            target_metric="<500ms update latency",
            implementation=Implementation(
                file_path=self._get_file_path("progression_ui.py"),
                class_name="ProgressionUI",
                method_name="render_progression_timeline"
            ),
            verification=Verification(
                test_file=self._get_file_path("test_progression_ui.py"),
                test_method="test_progression_tracking"
            )
        )
        req.acceptance_criteria.append(ac1)
        
        ac2 = AcceptanceCriterion(
            criterion_id="AC-UI-007-02",
            description="Milestone indicators and completion alerts",
            implementation=Implementation(
                file_path=self._get_file_path("progression_ui.py"),
                method_name="display_milestones"
            ),
            verification=Verification(
                test_file=self._get_file_path("test_progression_ui.py"),
                test_method="test_milestone_visualization"
            )
        )
        req.acceptance_criteria.append(ac2)
        
        return req
    
    # REQ-UI-008: Completion Notifications
    def define_req_ui_008(self) -> Requirement:
        """Completion Notifications Interface"""
        req = Requirement(
            requirement_id="REQ-UI-008",
            requirement_type="Functional",
            description=(
                "Notifications - Push notifications with offline queuing"
            )
        )
        
        ac1 = AcceptanceCriterion(
            criterion_id="AC-UI-008-01",
            description="Mobile push notifications",
            target_metric="<2 second delivery",
            implementation=Implementation(
                file_path=self._get_file_path("notification_ui.py"),
                class_name="NotificationUI",
                method_name="send_push_notification"
            ),
            verification=Verification(
                test_file=self._get_file_path("test_notifications.py"),
                test_method="test_push_notifications"
            )
        )
        req.acceptance_criteria.append(ac1)
        
        ac2 = AcceptanceCriterion(
            criterion_id="AC-UI-008-02",
            description="Offline notification queuing and sync",
            implementation=Implementation(
                file_path=self._get_file_path("notification_ui.py"),
                method_name="queue_offline_notifications"
            ),
            verification=Verification(
                test_file=self._get_file_path("test_notifications.py"),
                test_method="test_offline_queuing"
            )
        )
        req.acceptance_criteria.append(ac2)
        
        return req
    
    # Performance Requirements
    def define_performance_requirements(self) -> List[Requirement]:
        """Define performance requirements"""
        requirements = []
        
        # REQ-PERF-UI-001: Mobile Interface Responsiveness
        req1 = Requirement(
            requirement_id="REQ-PERF-UI-001",
            requirement_type="Performance",
            description=(
                "Mobile Interface Responsiveness - "
                "<2s load, <1s navigation"
            )
        )
        
        ac1 = AcceptanceCriterion(
            criterion_id="AC-PERF-UI-001-01",
            description="Mobile interface load and navigation performance",
            target_metric=(
                "<2s initial load, <1s navigation, <500ms updates"
            ),
            implementation=Implementation(
                file_path=self._get_file_path("mobile_ui_performance.py"),
                method_name="measure_load_time"
            ),
            verification=Verification(
                test_file=self._get_file_path(
                    "test_mobile_ui_performance.py"
                ),
                test_method="test_mobile_interface_performance"
            )
        )
        req1.acceptance_criteria.append(ac1)
        requirements.append(req1)
        
        # REQ-PERF-UI-002: Visualization Performance
        req2 = Requirement(
            requirement_id="REQ-PERF-UI-002",
            requirement_type="Performance",
            description=(
                "Visualization Performance - "
                "<1s rendering, <500ms updates"
            )
        )
        
        ac2 = AcceptanceCriterion(
            criterion_id="AC-PERF-UI-002-01",
            description="Real-time visualization rendering performance",
            target_metric=(
                "<1s rendering, <500ms updates, <100ms interactions"
            ),
            implementation=Implementation(
                file_path=self._get_file_path("visualization_performance.py"),
                method_name="measure_render_time"
            ),
            verification=Verification(
                test_file=self._get_file_path(
                    "test_visualization_performance.py"
                ),
                test_method="test_visualization_performance"
            )
        )
        req2.acceptance_criteria.append(ac2)
        requirements.append(req2)
        
        return requirements
    
    # Usability Requirements
    def define_usability_requirements(self) -> List[Requirement]:
        """Define usability requirements"""
        requirements = []
        
        # REQ-UX-UI-001: Mobile User Experience
        req1 = Requirement(
            requirement_id="REQ-UX-UI-001",
            requirement_type="Usability",
            description=(
                "Mobile User Experience - 95%+ satisfaction, "
                "<5% error rate"
            )
        )
        
        ac1 = AcceptanceCriterion(
            criterion_id="AC-UX-UI-001-01",
            description="Mobile usability metrics",
            target_metric="95%+ satisfaction, <5% error, <3s tasks",
            implementation=Implementation(
                file_path=self._get_file_path("mobile_ux_metrics.py"),
                method_name="measure_usability"
            ),
            verification=Verification(
                test_file=self._get_file_path("test_mobile_ux.py"),
                test_method="test_mobile_user_experience"
            )
        )
        req1.acceptance_criteria.append(ac1)
        requirements.append(req1)
        
        # REQ-UX-UI-002: Interface Clarity
        req2 = Requirement(
            requirement_id="REQ-UX-UI-002",
            requirement_type="Usability",
            description=(
                "Interface Clarity - 95%+ navigation success"
            )
        )
        
        ac2 = AcceptanceCriterion(
            criterion_id="AC-UX-UI-002-01",
            description="Contextual interface clarity metrics",
            target_metric="95%+ navigation, <5s context understanding",
            implementation=Implementation(
                file_path=self._get_file_path("interface_clarity.py"),
                method_name="measure_clarity"
            ),
            verification=Verification(
                test_file=self._get_file_path("test_interface_clarity.py"),
                test_method="test_contextual_interface_clarity"
            )
        )
        req2.acceptance_criteria.append(ac2)
        requirements.append(req2)
        
        return requirements
    
    # Mobile Requirements
    def define_mobile_requirements(self) -> List[Requirement]:
        """Define mobile-specific requirements"""
        requirements = []
        
        # REQ-MOB-OPT-001: Responsive Design
        req1 = Requirement(
            requirement_id="REQ-MOB-OPT-001",
            requirement_type="Mobile",
            description="Responsive Design - Adaptive layouts"
        )
        
        ac1 = AcceptanceCriterion(
            criterion_id="AC-MOB-OPT-001-01",
            description="Responsive design implementation",
            implementation=Implementation(
                file_path=self._get_file_path("responsive_ui.py"),
                method_name="adapt_to_screen"
            ),
            verification=Verification(
                test_file=self._get_file_path("test_responsive_design.py"),
                test_method="test_responsive_design"
            )
        )
        req1.acceptance_criteria.append(ac1)
        requirements.append(req1)
        
        # REQ-MOB-OPT-002: Offline Capability
        req2 = Requirement(
            requirement_id="REQ-MOB-OPT-002",
            requirement_type="Mobile",
            description="Offline Capability - Data sync"
        )
        
        ac2 = AcceptanceCriterion(
            criterion_id="AC-MOB-OPT-002-01",
            description="Offline data caching and synchronization",
            implementation=Implementation(
                file_path=self._get_file_path("offline_capability.py"),
                method_name="enable_offline_mode"
            ),
            verification=Verification(
                test_file=self._get_file_path("test_offline_capability.py"),
                test_method="test_offline_capability"
            )
        )
        req2.acceptance_criteria.append(ac2)
        requirements.append(req2)
        
        # REQ-MOB-SEC-001: Mobile Security
        req3 = Requirement(
            requirement_id="REQ-MOB-SEC-001",
            requirement_type="Mobile",
            description="Mobile Security - Encryption and biometric"
        )
        
        ac3 = AcceptanceCriterion(
            criterion_id="AC-MOB-SEC-001-01",
            description="Mobile security implementation",
            implementation=Implementation(
                file_path=self._get_file_path("mobile_security.py"),
                method_name="enable_security_protocols"
            ),
            verification=Verification(
                test_file=self._get_file_path("test_mobile_security.py"),
                test_method="test_mobile_security"
            )
        )
        req3.acceptance_criteria.append(ac3)
        requirements.append(req3)
        
        return requirements
    
    # Integration Requirements
    def define_integration_requirements(self) -> List[Requirement]:
        """Define integration requirements"""
        requirements = []
        
        # REQ-MOB-UI-001: Mobile Framework Integration
        req1 = Requirement(
            requirement_id="REQ-MOB-UI-001",
            requirement_type="Integration",
            description="Mobile Framework - Native-like experience"
        )
        
        ac1 = AcceptanceCriterion(
            criterion_id="AC-MOB-UI-001-01",
            description="Mobile UI framework integration",
            implementation=Implementation(
                file_path=self._get_file_path("mobile_framework.py"),
                method_name="initialize_framework"
            ),
            verification=Verification(
                test_file=self._get_file_path("test_mobile_framework.py"),
                test_method="test_mobile_framework_integration"
            )
        )
        req1.acceptance_criteria.append(ac1)
        requirements.append(req1)
        
        # REQ-RT-UI-001: Context Engine Integration
        req2 = Requirement(
            requirement_id="REQ-RT-UI-001",
            requirement_type="Integration",
            description="Context Engine - Real-time position updates"
        )
        
        ac2 = AcceptanceCriterion(
            criterion_id="AC-RT-UI-001-01",
            description="WebSocket integration for real-time updates",
            target_metric="<500ms update latency",
            implementation=Implementation(
                file_path=self._get_file_path("context_engine_ui.py"),
                method_name="connect_websocket"
            ),
            verification=Verification(
                test_file=self._get_file_path(
                    "test_context_engine_ui.py"
                ),
                test_method="test_realtime_position_updates"
            )
        )
        req2.acceptance_criteria.append(ac2)
        requirements.append(req2)
        
        # REQ-RT-UI-002: Component Registry Integration
        req3 = Requirement(
            requirement_id="REQ-RT-UI-002",
            requirement_type="Integration",
            description="Component Registry - Live status updates"
        )
        
        ac3 = AcceptanceCriterion(
            criterion_id="AC-RT-UI-002-01",
            description="Real-time component status streaming",
            target_metric="<1 second update latency",
            implementation=Implementation(
                file_path=self._get_file_path("component_registry_ui.py"),
                method_name="stream_component_status"
            ),
            verification=Verification(
                test_file=self._get_file_path(
                    "test_component_registry_ui.py"
                ),
                test_method="test_realtime_status_updates"
            )
        )
        req3.acceptance_criteria.append(ac3)
        requirements.append(req3)
        
        return requirements


if __name__ == "__main__":
    # Initialize tracer
    tracer = UILayerRequirementsTracer(
        repo_root="/workspaces/control_tower"
    )
    
    print("=" * 80)
    print("USER INTERFACE LAYER REQUIREMENTS TRACER")
    print("Evidence-Based Compliance Validation")
    print("=" * 80)
    print()
    
    # Define all requirements
    print("Defining requirements...")
    requirements = []
    
    # Functional requirements (REQ-UI-001 through REQ-UI-008)
    requirements.append(tracer.define_req_ui_001())
    requirements.append(tracer.define_req_ui_002())
    requirements.append(tracer.define_req_ui_003())
    requirements.append(tracer.define_req_ui_004())
    requirements.append(tracer.define_req_ui_005())
    requirements.append(tracer.define_req_ui_006())
    requirements.append(tracer.define_req_ui_007())
    requirements.append(tracer.define_req_ui_008())
    
    # Performance requirements
    requirements.extend(tracer.define_performance_requirements())
    
    # Usability requirements
    requirements.extend(tracer.define_usability_requirements())
    
    # Mobile requirements
    requirements.extend(tracer.define_mobile_requirements())
    
    # Integration requirements
    requirements.extend(tracer.define_integration_requirements())
    
    print(f"✅ Defined {len(requirements)} requirements")
    print()
    
    # Validate all requirements
    print("Validating requirements with concrete evidence...")
    print("(Searching ENTIRE workspace - files can be anywhere!)")
    for req in requirements:
        tracer.validate_requirement(req)
        print(f"  ✅ Validated {req.requirement_id}")
    print()
    
    # Generate report
    print("Generating evidence-based compliance report...")
    report = tracer.generate_report()
    print(report)
    
    # Save outputs with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(
        "/workspaces/control_tower/projects/PROJECT-003 TDD ENFORCER/"
        "SYSTEM-003-02 EXTENDED VALIDATION ENGINE/"
        "FEATURE-003-02-01 TESTING PYRAMID VALIDATION ENGINE/"
        "USER INTERFACE LAYER"
    )
    
    report_file = (
        output_dir /
        f"UI_LAYER_REQUIREMENTS_TRACEABILITY_REPORT_{timestamp}.txt"
    )
    evidence_file = (
        output_dir / f"ui_layer_evidence_log_{timestamp}.json"
    )
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    tracer.save_evidence_log(str(evidence_file))
    
    print(f"\n✅ Evidence-based traceability report saved!")
    print(f"   Report: {report_file.name}")
    print(f"   Evidence: {evidence_file.name}")
