"""
Stage Gate Manager Tests
=======================

Failing tests for stage gate management functionality including
transition validation, compliance enforcement, and evidence collection.
"""

import pytest
import tempfile
import json
from datetime import datetime
from unittest.mock import Mock, patch

from src.business_logic.stage_gate_manager import (
    StageGateManager,
    StageGateDecision,
    StageGateStatus,
    StageGateEvidence,
    TransitionType
)
from src.business_logic.phase_enforcement import PhaseEnforcementResult, PhaseValidationResult


class TestStageGateManagerCore:
    """Tests for core stage gate management functionality"""
    
    def setup_method(self):
        self.manager = StageGateManager(compliance_threshold=0.75, risk_tolerance="MEDIUM")
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_stage_gate_manager_initialization(self):
        """
        TEST: Should initialize with proper configuration and enforcers
        EXPECTED: Should fail - initialization logic not complete
        """
        with pytest.raises((AttributeError, AssertionError)):
            assert self.manager.compliance_threshold == 0.75
            assert self.manager.risk_tolerance == "MEDIUM"
            assert self.manager.red_enforcer is not None
            assert self.manager.green_enforcer is not None
            assert self.manager.refactor_enforcer is not None
            assert isinstance(self.manager.gate_history, list)
            assert len(self.manager.gate_history) == 0
    
    def test_determine_transition_type_correctly_maps_phases(self):
        """
        TEST: Should correctly determine transition type from phase pairs
        EXPECTED: Should fail - _determine_transition_type method not implemented
        """
        with pytest.raises(AttributeError):
            # Test valid transitions
            assert self.manager._determine_transition_type("RED", "GREEN") == TransitionType.RED_TO_GREEN
            assert self.manager._determine_transition_type("GREEN", "REFACTOR") == TransitionType.GREEN_TO_REFACTOR
            assert self.manager._determine_transition_type("REFACTOR", "RED") == TransitionType.REFACTOR_TO_RED
            
            # Test invalid transition
            assert self.manager._determine_transition_type("RED", "REFACTOR") == TransitionType.CYCLE_COMPLETE
    
    def test_enforce_current_phase_delegates_to_appropriate_enforcer(self):
        """
        TEST: Should delegate to appropriate phase enforcer
        EXPECTED: Should fail - _enforce_current_phase method not implemented
        """
        evidence = {"test_data": True}
        
        with pytest.raises(AttributeError):
            # Test RED phase enforcement
            result = self.manager._enforce_current_phase("RED", self.temp_dir, evidence)
            assert isinstance(result, PhaseEnforcementResult)
            assert result.phase_name == "RED"
            
            # Test GREEN phase enforcement
            result = self.manager._enforce_current_phase("GREEN", self.temp_dir, evidence)
            assert result.phase_name == "GREEN"
            
            # Test REFACTOR phase enforcement
            result = self.manager._enforce_current_phase("REFACTOR", self.temp_dir, evidence)
            assert result.phase_name == "REFACTOR"
    
    def test_collect_compliance_evidence_aggregates_data(self):
        """
        TEST: Should collect and aggregate compliance evidence
        EXPECTED: Should fail - _collect_compliance_evidence method not implemented
        """
        # Create mock enforcement result
        mock_result = Mock()
        mock_result.compliance_score = 0.80
        mock_result.validation_result = PhaseValidationResult.PASS
        mock_result.blocking_issues = []
        mock_result.warnings = ["Minor warning"]
        mock_result.execution_time_ms = 1500.0
        mock_result.evidence.validation_timestamp = datetime.now()
        
        additional_evidence = {"custom_metric": 0.90}
        
        with pytest.raises(AttributeError):
            compliance_evidence = self.manager._collect_compliance_evidence(
                mock_result, additional_evidence
            )
            
            assert compliance_evidence["enforcement_compliance"] == 0.80
            assert compliance_evidence["validation_result"] == "PASS"
            assert compliance_evidence["blocking_issues_count"] == 0
            assert compliance_evidence["warnings_count"] == 1
            assert compliance_evidence["custom_metric"] == 0.90
    
    def test_assess_quality_metrics_evaluates_project_quality(self):
        """
        TEST: Should assess quality metrics for project
        EXPECTED: Should fail - _assess_quality_metrics method not implemented
        """
        evidence = {
            "code_coverage": 0.85,
            "test_coverage": 0.90,
            "complexity_score": 0.40,
            "maintainability_index": 0.80
        }
        
        with pytest.raises(AttributeError):
            quality_metrics = self.manager._assess_quality_metrics(self.temp_dir, evidence)
            
            assert "code_coverage" in quality_metrics
            assert "test_coverage" in quality_metrics
            assert "complexity_score" in quality_metrics
            assert "maintainability_index" in quality_metrics
            assert quality_metrics["code_coverage"] == 0.85
    
    def test_assess_performance_metrics_evaluates_enforcement_performance(self):
        """
        TEST: Should assess performance metrics for enforcement
        EXPECTED: Should fail - _assess_performance_metrics method not implemented
        """
        mock_result = Mock()
        mock_result.execution_time_ms = 2500.0
        mock_result.compliance_score = 0.85
        
        with pytest.raises(AttributeError):
            performance_metrics = self.manager._assess_performance_metrics(mock_result)
            
            assert "enforcement_time_ms" in performance_metrics
            assert "compliance_score" in performance_metrics
            assert "validation_efficiency" in performance_metrics
            assert performance_metrics["enforcement_time_ms"] == 2500.0
    
    def test_assess_transition_risks_evaluates_risks_correctly(self):
        """
        TEST: Should assess risks associated with phase transition
        EXPECTED: Should fail - _assess_transition_risks method not implemented
        """
        mock_result = Mock()
        mock_result.validation_result = PhaseValidationResult.FAIL
        mock_result.compliance_score = 0.45
        mock_result.blocking_issues = ["Critical issue 1", "Critical issue 2", "Critical issue 3"]
        mock_result.warnings = ["Warning 1"]
        mock_result.execution_time_ms = 6000.0  # > 5 seconds
        
        evidence = {}
        
        with pytest.raises(AttributeError):
            risk_assessment = self.manager._assess_transition_risks(
                TransitionType.RED_TO_GREEN, mock_result, evidence
            )
            
            assert risk_assessment["technical_risk"] == "HIGH"  # Validation failed
            assert risk_assessment["quality_risk"] == "HIGH"    # Low compliance score
            assert risk_assessment["timeline_risk"] == "MEDIUM" # > 5 seconds
            assert risk_assessment["compliance_risk"] == "HIGH" # 3+ blocking issues


class TestStageGateEvaluation:
    """Tests for stage gate evaluation logic"""
    
    def setup_method(self):
        self.manager = StageGateManager()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_evaluate_stage_gate_comprehensive_evaluation(self):
        """
        TEST: Should perform comprehensive stage gate evaluation
        EXPECTED: Should fail - evaluate_stage_gate method not implemented
        """
        current_phase = "RED"
        target_phase = "GREEN"
        evidence = {
            "tests_exist": True,
            "tests_failing": True,
            "compliance_score": 0.80
        }
        
        with pytest.raises(AttributeError):
            decision = self.manager.evaluate_stage_gate(
                current_phase, target_phase, self.temp_dir, evidence
            )
            
            assert isinstance(decision, StageGateDecision)
            assert decision.transition_type == TransitionType.RED_TO_GREEN
            assert decision.status in [StageGateStatus.OPEN, StageGateStatus.CLOSED, StageGateStatus.WARNING]
            assert decision.compliance_score >= 0.0
            assert decision.risk_level in ["LOW", "MEDIUM", "HIGH"]
    
    def test_check_approval_criteria_validates_transition_requirements(self):
        """
        TEST: Should check approval criteria for each transition type
        EXPECTED: Should fail - _check_approval_criteria method not implemented
        """
        # Create mock enforcement result
        mock_result = Mock()
        mock_result.evidence.test_files = ["test1.py"]
        mock_result.evidence.test_results = {"test1.py": False}  # Failing test (good for RED)
        mock_result.evidence.complexity_score = 0.30  # Low complexity (good)
        mock_result.evidence.code_coverage = 0.80  # Good coverage
        
        compliance_evidence = {"tests_exist": True, "tests_failing": True}
        
        with pytest.raises(AttributeError):
            approval_criteria_met, blocking_criteria = self.manager._check_approval_criteria(
                TransitionType.RED_TO_GREEN, mock_result, compliance_evidence
            )
            
            assert isinstance(approval_criteria_met, list)
            assert isinstance(blocking_criteria, list)
            assert "tests_exist" in approval_criteria_met
            assert "tests_failing" in approval_criteria_met
    
    def test_evaluate_criterion_correctly_evaluates_individual_criteria(self):
        """
        TEST: Should correctly evaluate individual approval criteria
        EXPECTED: Should fail - _evaluate_criterion method not implemented
        """
        # Create mock enforcement result
        mock_result = Mock()
        mock_result.evidence.test_files = ["test1.py", "test2.py"]
        mock_result.evidence.test_results = {"test1.py": True, "test2.py": True}
        mock_result.evidence.complexity_score = 0.30
        mock_result.evidence.code_coverage = 0.85
        
        compliance_evidence = {"new_features_added": False}
        
        with pytest.raises(AttributeError):
            # Test positive criteria
            assert self.manager._evaluate_criterion("tests_exist", mock_result, compliance_evidence) == True
            assert self.manager._evaluate_criterion("tests_passing", mock_result, compliance_evidence) == True
            assert self.manager._evaluate_criterion("minimal_implementation", mock_result, compliance_evidence) == True
            assert self.manager._evaluate_criterion("coverage_adequate", mock_result, compliance_evidence) == True
            assert self.manager._evaluate_criterion("no_feature_creep", mock_result, compliance_evidence) == True
    
    def test_make_gate_decision_creates_comprehensive_decision(self):
        """
        TEST: Should create comprehensive gate decision with all required data
        EXPECTED: Should fail - _make_gate_decision method not implemented
        """
        # Create mock evidence
        mock_evidence = Mock()
        mock_evidence.phase_enforcement_result.compliance_score = 0.85
        mock_evidence.phase_enforcement_result.warnings = []
        mock_evidence.blocking_criteria = []
        mock_evidence.risk_assessment = {"technical_risk": "LOW", "quality_risk": "LOW", "timeline_risk": "LOW", "compliance_risk": "LOW"}
        
        with pytest.raises(AttributeError):
            decision = self.manager._make_gate_decision(TransitionType.GREEN_TO_REFACTOR, mock_evidence)
            
            assert isinstance(decision, StageGateDecision)
            assert decision.gate_id.startswith("GATE_GREEN_TO_REFACTOR")
            assert decision.transition_type == TransitionType.GREEN_TO_REFACTOR
            assert decision.status == StageGateStatus.OPEN  # Good evidence should open gate
            assert decision.compliance_score == 0.85
            assert decision.risk_level == "LOW"
            assert decision.approval_authority == "TDD_CYCLE_ENFORCER"


class TestStageGateDecisionLogic:
    """Tests for stage gate decision logic and blocking mechanisms"""
    
    def setup_method(self):
        self.manager = StageGateManager(compliance_threshold=0.75)
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_stage_gate_blocks_transitions_with_blocking_criteria(self):
        """
        TEST: Should block transitions when blocking criteria exist
        EXPECTED: Should fail - blocking logic not implemented
        """
        current_phase = "RED"
        target_phase = "GREEN"
        evidence = {
            "tests_exist": False,  # Should block transition
            "tests_failing": False,  # Should block transition
            "compliance_score": 0.50  # Below threshold
        }
        
        with pytest.raises(AttributeError):
            decision = self.manager.evaluate_stage_gate(
                current_phase, target_phase, self.temp_dir, evidence
            )
            
            assert decision.status == StageGateStatus.CLOSED
            assert len(decision.evidence.blocking_criteria) > 0
    
    def test_stage_gate_opens_with_sufficient_compliance(self):
        """
        TEST: Should open gate when compliance threshold is met
        EXPECTED: Should fail - approval logic not implemented
        """
        current_phase = "GREEN"
        target_phase = "REFACTOR"
        evidence = {
            "tests_passing": True,
            "coverage_adequate": True,
            "no_feature_creep": True,
            "compliance_score": 0.85  # Above threshold
        }
        
        with pytest.raises(AttributeError):
            decision = self.manager.evaluate_stage_gate(
                current_phase, target_phase, self.temp_dir, evidence
            )
            
            assert decision.status == StageGateStatus.OPEN
            assert decision.compliance_score >= 0.75
    
    def test_stage_gate_warns_with_partial_compliance(self):
        """
        TEST: Should warn when compliance is adequate but warnings exist
        EXPECTED: Should fail - warning logic not implemented
        """
        current_phase = "REFACTOR"
        target_phase = "RED"
        evidence = {
            "tests_still_passing": True,
            "quality_improved": True,
            "compliance_score": 0.80,  # Above threshold
            "minor_warnings": True  # Should trigger warning status
        }
        
        with pytest.raises(AttributeError):
            decision = self.manager.evaluate_stage_gate(
                current_phase, target_phase, self.temp_dir, evidence
            )
            
            assert decision.status == StageGateStatus.WARNING
            assert decision.compliance_score >= 0.75
    
    def test_generate_recommendations_provides_actionable_guidance(self):
        """
        TEST: Should generate actionable recommendations based on gate status
        EXPECTED: Should fail - _generate_recommendations method not implemented
        """
        # Test with blocked gate
        mock_evidence = Mock()
        mock_evidence.blocking_criteria = ["tests_not_failing", "coverage_low"]
        mock_evidence.phase_enforcement_result.warnings = ["Implementation complex"]
        mock_evidence.phase_enforcement_result.compliance_score = 0.60
        
        with pytest.raises(AttributeError):
            recommendations = self.manager._generate_recommendations(
                StageGateStatus.CLOSED, mock_evidence
            )
            
            assert isinstance(recommendations, list)
            assert any("Address all blocking criteria" in rec for rec in recommendations)
            assert any("tests_not_failing" in rec for rec in recommendations)
    
    def test_generate_next_actions_provides_clear_steps(self):
        """
        TEST: Should generate clear next actions based on gate decision
        EXPECTED: Should fail - _generate_next_actions method not implemented
        """
        mock_evidence = Mock()
        mock_evidence.phase_enforcement_result.blocking_issues = ["Critical issue"]
        
        with pytest.raises(AttributeError):
            # Test for open gate
            next_actions = self.manager._generate_next_actions(
                StageGateStatus.OPEN, TransitionType.RED_TO_GREEN, mock_evidence
            )
            assert any("Proceed to GREEN phase" in action for action in next_actions)
            
            # Test for closed gate
            next_actions = self.manager._generate_next_actions(
                StageGateStatus.CLOSED, TransitionType.RED_TO_GREEN, mock_evidence
            )
            assert any("Remain in current phase" in action for action in next_actions)


class TestStageGateReportingAndHistory:
    """Tests for stage gate reporting and history management"""
    
    def setup_method(self):
        self.manager = StageGateManager()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_get_gate_history_returns_decision_history(self):
        """
        TEST: Should return comprehensive gate decision history
        EXPECTED: Should fail - get_gate_history method not implemented
        """
        with pytest.raises(AttributeError):
            history = self.manager.get_gate_history()
            assert isinstance(history, list)
            # Initially empty
            assert len(history) == 0
    
    def test_export_compliance_report_creates_comprehensive_report(self):
        """
        TEST: Should export comprehensive compliance report
        EXPECTED: Should fail - export_compliance_report method not implemented
        """
        output_path = str(Path(self.temp_dir) / "compliance_report.json")
        
        with pytest.raises(AttributeError):
            self.manager.export_compliance_report(output_path)
            
            # Verify report file created
            assert Path(output_path).exists()
            
            # Verify report content
            with open(output_path, 'r') as f:
                report = json.load(f)
            
            assert "report_timestamp" in report
            assert "compliance_threshold" in report
            assert "risk_tolerance" in report
            assert "total_gates_evaluated" in report
            assert "gate_decisions" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])