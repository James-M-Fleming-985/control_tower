"""
RED PHASE TESTS: Phase Models for RED-GREEN-REFACTOR Cycle Enforcer
================================================================

LAYER: DATA ACCESS LAYER (LAYER-003-01-03-001)
PHASE: RED (All tests should FAIL initially)

Models Under Test:
- TDDPhase: Core phase state model
- PhaseState: Phase status and metadata
- PhaseTransition: Phase change tracking
- PhaseEvidence: Test execution evidence
- GitCheckpoint: Git checkpoint metadata
- CheckpointMetadata: Git checkpoint details

These tests define the data models required for TDD phase tracking.
ALL TESTS MUST FAIL INITIALLY to establish proper TDD workflow.
"""

import pytest
import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any

# Import all required modules - GREEN phase implementation
from src.data_access.phase_models import (
    TDDPhase, PhaseState, PhaseTransition, PhaseEvidence,
    PhaseType, PhaseStatus, TransitionTrigger, EvidenceType
)
from src.data_access.git_checkpoint_models import (
    GitCheckpoint, CheckpointMetadata, GitOperation,
    CheckpointStatus, OperationType
)


class TestTDDPhaseModel:
    """Test suite for TDD Phase model"""
    
    def test_tdd_phase_creation(self):
        """Test TDD phase model creation with required fields"""
        # This test MUST FAIL initially (RED phase)
        assert TDDPhase is not None, "TDDPhase model not implemented"
        
        phase = TDDPhase(
            phase_id="phase_model_001",
            phase_type="RED",
            feature_id="FEATURE-003-01-03",
            layer_id="LAYER-003-01-03-001",
            started_at=datetime.now(),
            status="ACTIVE"
        )
        
        assert phase.phase_id == "phase_model_001"
        assert phase.phase_type == "RED"
        assert phase.feature_id == "FEATURE-003-01-03"
        assert phase.layer_id == "LAYER-003-01-03-001"
        assert phase.status == "ACTIVE"
        assert isinstance(phase.started_at, datetime)
    
    def test_tdd_phase_type_enumeration(self):
        """Test TDD phase type enumeration and validation"""
        # This test MUST FAIL initially (RED phase)
        assert PhaseType is not None, "PhaseType enumeration not implemented"
        
        # Test all valid phase types
        assert PhaseType.RED in PhaseType
        assert PhaseType.GREEN in PhaseType
        assert PhaseType.REFACTOR in PhaseType
        
        # Test phase type values
        assert PhaseType.RED.value == "RED"
        assert PhaseType.GREEN.value == "GREEN"
        assert PhaseType.REFACTOR.value == "REFACTOR"
        
        # Test invalid phase type handling
        with pytest.raises(ValueError):
            invalid_phase = TDDPhase(
                phase_id="invalid_001",
                phase_type="INVALID_PHASE",  # Should raise error
                feature_id="FEATURE-003-01-03",
                layer_id="LAYER-003-01-03-001",
                started_at=datetime.now(),
                status="ACTIVE"
            )
    
    def test_phase_status_enumeration(self):
        """Test phase status enumeration and lifecycle"""
        # This test MUST FAIL initially (RED phase)
        assert PhaseStatus is not None, "PhaseStatus enumeration not implemented"
        
        # Test all valid phase statuses
        assert PhaseStatus.ACTIVE in PhaseStatus
        assert PhaseStatus.COMPLETED in PhaseStatus
        assert PhaseStatus.FAILED in PhaseStatus
        assert PhaseStatus.CANCELLED in PhaseStatus
        
        # Test status lifecycle transitions
        phase = TDDPhase(
            phase_id="status_001",
            phase_type="RED",
            feature_id="FEATURE-003-01-03",
            layer_id="LAYER-003-01-03-001",
            started_at=datetime.now(),
            status=PhaseStatus.ACTIVE
        )
        
        assert phase.status == PhaseStatus.ACTIVE
        
        # Test status transition methods
        phase.mark_completed(datetime.now())
        assert phase.status == PhaseStatus.COMPLETED
        assert phase.completed_at is not None
    
    def test_phase_duration_calculation(self):
        """Test phase duration calculation and timing"""
        # This test MUST FAIL initially (RED phase)
        assert TDDPhase is not None, "TDDPhase model not implemented"
        
        start_time = datetime.now()
        phase = TDDPhase(
            phase_id="duration_001",
            phase_type="RED",
            feature_id="FEATURE-003-01-03",
            layer_id="LAYER-003-01-03-001",
            started_at=start_time,
            status="ACTIVE"
        )
        
        # Simulate phase completion after 5 minutes
        end_time = start_time + timedelta(minutes=5)
        phase.mark_completed(end_time)
        
        duration = phase.get_duration()
        assert duration.total_seconds() == 300  # 5 minutes = 300 seconds
        assert phase.get_duration_minutes() == 5.0
    
    def test_phase_metadata_and_context(self):
        """Test phase metadata storage and context information"""
        # This test MUST FAIL initially (RED phase)
        assert TDDPhase is not None, "TDDPhase model not implemented"
        
        metadata = {
            "developer": "test_developer",
            "branch": "feature/red-green-refactor",
            "test_framework": "pytest",
            "environment": "development",
            "performance_target": "sub_200ms"
        }
        
        context = {
            "previous_phase": None,
            "iteration_number": 1,
            "total_tests": 15,
            "failed_tests": 15,
            "test_files": ["test_phase_models.py"]
        }
        
        phase = TDDPhase(
            phase_id="metadata_001",
            phase_type="RED",
            feature_id="FEATURE-003-01-03",
            layer_id="LAYER-003-01-03-001",
            started_at=datetime.now(),
            status="ACTIVE",
            metadata=metadata,
            context=context
        )
        
        assert phase.metadata["developer"] == "test_developer"
        assert phase.metadata["test_framework"] == "pytest"
        assert phase.context["total_tests"] == 15
        assert phase.context["failed_tests"] == 15
        
        # Test metadata updates
        phase.update_metadata("commit_hash", "abc123def456")
        assert phase.metadata["commit_hash"] == "abc123def456"


class TestPhaseTransitionModel:
    """Test suite for Phase Transition model"""
    
    def test_phase_transition_creation(self):
        """Test phase transition model creation and validation"""
        # This test MUST FAIL initially (RED phase)
        assert PhaseTransition is not None, "PhaseTransition model not implemented"
        assert TransitionTrigger is not None, "TransitionTrigger enumeration not implemented"
        
        transition = PhaseTransition(
            transition_id="trans_001",
            from_phase="RED",
            to_phase="GREEN",
            phase_id="phase_001",
            transition_time=datetime.now(),
            trigger_event=TransitionTrigger.TEST_PASS,
            evidence={"test_results": "all_passing", "commit_hash": "abc123"}
        )
        
        assert transition.transition_id == "trans_001"
        assert transition.from_phase == "RED"
        assert transition.to_phase == "GREEN"
        assert transition.trigger_event == TransitionTrigger.TEST_PASS
        assert transition.evidence["test_results"] == "all_passing"
    
    def test_transition_trigger_enumeration(self):
        """Test transition trigger enumeration and validation"""
        # This test MUST FAIL initially (RED phase)
        assert TransitionTrigger is not None, "TransitionTrigger enumeration not implemented"
        
        # Test all valid triggers
        assert TransitionTrigger.TEST_PASS in TransitionTrigger
        assert TransitionTrigger.TEST_FAIL in TransitionTrigger
        assert TransitionTrigger.IMPLEMENTATION_COMPLETE in TransitionTrigger
        assert TransitionTrigger.REFACTOR_COMPLETE in TransitionTrigger
        assert TransitionTrigger.MANUAL_TRIGGER in TransitionTrigger
        
        # Test trigger values
        assert TransitionTrigger.TEST_PASS.value == "TEST_PASS"
        assert TransitionTrigger.IMPLEMENTATION_COMPLETE.value == "IMPLEMENTATION_COMPLETE"
    
    def test_transition_validation_rules(self):
        """Test phase transition validation rules"""
        # This test MUST FAIL initially (RED phase)
        assert PhaseTransition is not None, "PhaseTransition model not implemented"
        
        # Valid RED -> GREEN transition
        valid_transition = PhaseTransition(
            transition_id="valid_001",
            from_phase="RED",
            to_phase="GREEN",
            phase_id="phase_001",
            transition_time=datetime.now(),
            trigger_event=TransitionTrigger.TEST_PASS,
            evidence={"tests_passing": True}
        )
        
        assert valid_transition.is_valid() == True
        
        # Invalid RED -> REFACTOR transition (must go through GREEN)
        invalid_transition = PhaseTransition(
            transition_id="invalid_001",
            from_phase="RED",
            to_phase="REFACTOR",  # Invalid direct transition
            phase_id="phase_001",
            transition_time=datetime.now(),
            trigger_event=TransitionTrigger.MANUAL_TRIGGER,
            evidence={}
        )
        
        assert invalid_transition.is_valid() == False
        assert "invalid_transition_path" in invalid_transition.get_validation_errors()
    
    def test_transition_evidence_requirements(self):
        """Test transition evidence requirements for different trigger types"""
        # This test MUST FAIL initially (RED phase)
        assert PhaseTransition is not None, "PhaseTransition model not implemented"
        
        # TEST_PASS trigger requires test evidence
        test_pass_transition = PhaseTransition(
            transition_id="evidence_001",
            from_phase="RED",
            to_phase="GREEN",
            phase_id="phase_001",
            transition_time=datetime.now(),
            trigger_event=TransitionTrigger.TEST_PASS,
            evidence={
                "test_execution_result": {
                    "total_tests": 15,
                    "passed": 15,
                    "failed": 0,
                    "exit_code": 0
                },
                "commit_hash": "abc123def456"
            }
        )
        
        assert test_pass_transition.has_required_evidence() == True
        
        # IMPLEMENTATION_COMPLETE trigger requires implementation evidence
        impl_complete_transition = PhaseTransition(
            transition_id="evidence_002",
            from_phase="GREEN",
            to_phase="REFACTOR",
            phase_id="phase_001",
            transition_time=datetime.now(),
            trigger_event=TransitionTrigger.IMPLEMENTATION_COMPLETE,
            evidence={
                "implementation_files": ["src/data_access/models.py"],
                "code_coverage": 95.5,
                "implementation_commit": "def456ghi789"
            }
        )
        
        assert impl_complete_transition.has_required_evidence() == True


class TestPhaseEvidenceModel:
    """Test suite for Phase Evidence model"""
    
    def test_phase_evidence_creation(self):
        """Test phase evidence model creation and storage"""
        # This test MUST FAIL initially (RED phase)
        assert PhaseEvidence is not None, "PhaseEvidence model not implemented"
        
        evidence = PhaseEvidence(
            evidence_id="evidence_001",
            phase_id="phase_001",
            evidence_type="TEST_EXECUTION",
            evidence_data={
                "test_command": "pytest tests/test_models.py -v",
                "exit_code": 1,
                "stdout": "15 failed, 0 passed in 2.50s",
                "stderr": "",
                "test_results": {
                    "total": 15,
                    "passed": 0,
                    "failed": 15,
                    "skipped": 0
                },
                "execution_time": 2.5,
                "timestamp": datetime.now().isoformat()
            },
            collected_at=datetime.now(),
            phase_type="RED"
        )
        
        assert evidence.evidence_id == "evidence_001"
        assert evidence.phase_id == "phase_001"
        assert evidence.evidence_type == "TEST_EXECUTION"
        assert evidence.phase_type == "RED"
        assert evidence.evidence_data["exit_code"] == 1
    
    def test_evidence_type_enumeration(self):
        """Test evidence type enumeration and validation"""
        # This test MUST FAIL initially (RED phase)
        from src.data_access.phase_models import EvidenceType
        
        assert EvidenceType is not None, "EvidenceType enumeration not implemented"
        
        # Test all evidence types
        assert EvidenceType.TEST_EXECUTION in EvidenceType
        assert EvidenceType.GIT_COMMIT in EvidenceType
        assert EvidenceType.CODE_COVERAGE in EvidenceType
        assert EvidenceType.PERFORMANCE_METRIC in EvidenceType
        assert EvidenceType.MANUAL_VERIFICATION in EvidenceType
        
        # Test evidence type values
        assert EvidenceType.TEST_EXECUTION.value == "TEST_EXECUTION"
        assert EvidenceType.GIT_COMMIT.value == "GIT_COMMIT"
    
    def test_evidence_serialization(self):
        """Test evidence data serialization and deserialization"""
        # This test MUST FAIL initially (RED phase)
        assert PhaseEvidence is not None, "PhaseEvidence model not implemented"
        
        original_evidence = PhaseEvidence(
            evidence_id="serial_001",
            phase_id="phase_001",
            evidence_type="TEST_EXECUTION",
            evidence_data={
                "complex_data": {
                    "nested_object": {"value": 42},
                    "array": [1, 2, 3],
                    "timestamp": datetime.now().isoformat()
                }
            },
            collected_at=datetime.now(),
            phase_type="RED"
        )
        
        # Test JSON serialization
        json_data = original_evidence.to_json()
        assert isinstance(json_data, str)
        
        # Test deserialization
        deserialized_evidence = PhaseEvidence.from_json(json_data)
        assert deserialized_evidence.evidence_id == "serial_001"
        assert deserialized_evidence.evidence_data["complex_data"]["nested_object"]["value"] == 42
        assert deserialized_evidence.evidence_data["complex_data"]["array"] == [1, 2, 3]
    
    def test_evidence_validation(self):
        """Test evidence data validation and schema compliance"""
        # This test MUST FAIL initially (RED phase)
        assert PhaseEvidence is not None, "PhaseEvidence model not implemented"
        
        # Valid test execution evidence
        valid_evidence = PhaseEvidence(
            evidence_id="valid_evidence_001",
            phase_id="phase_001",
            evidence_type="TEST_EXECUTION",
            evidence_data={
                "test_command": "pytest",
                "exit_code": 0,
                "test_results": {"passed": 15, "failed": 0}
            },
            collected_at=datetime.now(),
            phase_type="GREEN"
        )
        
        assert valid_evidence.is_valid() == True
        
        # Invalid evidence (missing required fields)
        invalid_evidence = PhaseEvidence(
            evidence_id="invalid_evidence_001",
            phase_id="phase_001",
            evidence_type="TEST_EXECUTION",
            evidence_data={
                "incomplete_data": "missing required fields"
            },
            collected_at=datetime.now(),
            phase_type="RED"
        )
        
        assert invalid_evidence.is_valid() == False
        validation_errors = invalid_evidence.get_validation_errors()
        assert "missing_test_command" in validation_errors
        assert "missing_exit_code" in validation_errors


class TestGitCheckpointModel:
    """Test suite for Git Checkpoint model"""
    
    def test_git_checkpoint_creation(self):
        """Test git checkpoint model creation and metadata"""
        # This test MUST FAIL initially (RED phase)
        assert GitCheckpoint is not None, "GitCheckpoint model not implemented"
        assert CheckpointMetadata is not None, "CheckpointMetadata model not implemented"
        
        metadata = CheckpointMetadata(
            feature_id="FEATURE-003-01-03",
            layer_id="LAYER-003-01-03-001",
            test_status="FAILING",
            files_changed=["test_models.py", "src/models.py"],
            code_coverage=0.0,
            test_results={
                "total": 15,
                "passed": 0,
                "failed": 15
            }
        )
        
        checkpoint = GitCheckpoint(
            checkpoint_id="checkpoint_001",
            phase_id="phase_001",
            phase_type="RED",
            commit_hash="abc123def456ghi789",
            branch_name="feature/red-green-refactor",
            checkpoint_time=datetime.now(),
            metadata=metadata
        )
        
        assert checkpoint.checkpoint_id == "checkpoint_001"
        assert checkpoint.phase_type == "RED"
        assert checkpoint.commit_hash == "abc123def456ghi789"
        assert checkpoint.metadata.feature_id == "FEATURE-003-01-03"
        assert checkpoint.metadata.test_status == "FAILING"
        assert len(checkpoint.metadata.files_changed) == 2
    
    def test_checkpoint_status_enumeration(self):
        """Test checkpoint status enumeration and lifecycle"""
        # This test MUST FAIL initially (RED phase)
        assert CheckpointStatus is not None, "CheckpointStatus enumeration not implemented"
        
        # Test all valid checkpoint statuses
        assert CheckpointStatus.PENDING in CheckpointStatus
        assert CheckpointStatus.CREATED in CheckpointStatus
        assert CheckpointStatus.FAILED in CheckpointStatus
        assert CheckpointStatus.RESTORED in CheckpointStatus
        
        # Test status values
        assert CheckpointStatus.PENDING.value == "PENDING"
        assert CheckpointStatus.CREATED.value == "CREATED"
        assert CheckpointStatus.FAILED.value == "FAILED"
    
    def test_git_operation_model(self):
        """Test git operation model for checkpoint management"""
        # This test MUST FAIL initially (RED phase)
        assert GitOperation is not None, "GitOperation model not implemented"
        assert OperationType is not None, "OperationType enumeration not implemented"
        
        operation = GitOperation(
            operation_id="op_001",
            operation_type=OperationType.COMMIT,
            checkpoint_id="checkpoint_001",
            command="git commit -m 'RED phase checkpoint'",
            result={
                "success": True,
                "commit_hash": "abc123def456",
                "files_committed": ["test_models.py"]
            },
            executed_at=datetime.now(),
            execution_time_ms=150
        )
        
        assert operation.operation_type == OperationType.COMMIT
        assert operation.result["success"] == True
        assert operation.execution_time_ms == 150
        assert operation.was_successful() == True
    
    def test_checkpoint_metadata_validation(self):
        """Test checkpoint metadata validation and requirements"""
        # This test MUST FAIL initially (RED phase)
        assert CheckpointMetadata is not None, "CheckpointMetadata model not implemented"
        
        # Valid RED phase metadata
        valid_red_metadata = CheckpointMetadata(
            feature_id="FEATURE-003-01-03",
            layer_id="LAYER-003-01-03-001",
            test_status="FAILING",
            files_changed=["tests/test_new.py"],
            code_coverage=0.0,
            test_results={"passed": 0, "failed": 5}
        )
        
        assert valid_red_metadata.is_valid_for_phase("RED") == True
        
        # Invalid GREEN phase metadata (tests should be passing)
        invalid_green_metadata = CheckpointMetadata(
            feature_id="FEATURE-003-01-03",
            layer_id="LAYER-003-01-03-001",
            test_status="FAILING",  # Invalid for GREEN phase
            files_changed=["src/implementation.py"],
            code_coverage=85.0,
            test_results={"passed": 10, "failed": 5}
        )
        
        assert invalid_green_metadata.is_valid_for_phase("GREEN") == False
        validation_errors = invalid_green_metadata.get_validation_errors("GREEN")
        assert "tests_must_pass_for_green" in validation_errors


class TestModelIntegration:
    """Integration tests for all phase models working together"""
    
    def test_complete_phase_lifecycle_models(self):
        """Test complete phase lifecycle using all models together"""
        # This test MUST FAIL initially (RED phase)
        assert all(cls is not None for cls in [TDDPhase, PhaseTransition, PhaseEvidence, GitCheckpoint]), \
            "Not all models implemented"
        
        # Create RED phase
        red_phase = TDDPhase(
            phase_id="lifecycle_001",
            phase_type="RED",
            feature_id="FEATURE-003-01-03",
            layer_id="LAYER-003-01-03-001",
            started_at=datetime.now(),
            status="ACTIVE"
        )
        
        # Create test execution evidence for RED phase
        red_evidence = PhaseEvidence(
            evidence_id="lifecycle_red_evidence",
            phase_id="lifecycle_001",
            evidence_type="TEST_EXECUTION",
            evidence_data={
                "test_command": "pytest",
                "exit_code": 1,
                "test_results": {"passed": 0, "failed": 15}
            },
            collected_at=datetime.now(),
            phase_type="RED"
        )
        
        # Create git checkpoint for RED phase
        red_checkpoint = GitCheckpoint(
            checkpoint_id="lifecycle_red_checkpoint",
            phase_id="lifecycle_001",
            phase_type="RED",
            commit_hash="red_abc123",
            branch_name="feature/lifecycle-test",
            checkpoint_time=datetime.now(),
            metadata=CheckpointMetadata(
                feature_id="FEATURE-003-01-03",
                layer_id="LAYER-003-01-03-001",
                test_status="FAILING",
                files_changed=["test_lifecycle.py"],
                code_coverage=0.0,
                test_results={"passed": 0, "failed": 15}
            )
        )
        
        # Create phase transition to GREEN
        red_to_green_transition = PhaseTransition(
            transition_id="lifecycle_red_to_green",
            from_phase="RED",
            to_phase="GREEN",
            phase_id="lifecycle_001",
            transition_time=datetime.now(),
            trigger_event=TransitionTrigger.TEST_PASS,
            evidence={
                "test_results": {"passed": 15, "failed": 0},
                "checkpoint_id": "lifecycle_red_checkpoint"
            }
        )
        
        # Verify all models are correctly linked
        assert red_phase.phase_id == red_evidence.phase_id
        assert red_phase.phase_id == red_checkpoint.phase_id
        assert red_phase.phase_id == red_to_green_transition.phase_id
        
        # Verify model consistency
        assert red_checkpoint.phase_type == red_phase.phase_type
        assert red_evidence.phase_type == red_phase.phase_type
        assert red_to_green_transition.from_phase == red_phase.phase_type
    
    def test_model_data_consistency(self):
        """Test data consistency across all models"""
        # This test MUST FAIL initially (RED phase)
        feature_id = "FEATURE-003-01-03"
        layer_id = "LAYER-003-01-03-001"
        phase_id = "consistency_001"
        
        # Create models with consistent data
        phase = TDDPhase(
            phase_id=phase_id,
            phase_type="RED",
            feature_id=feature_id,
            layer_id=layer_id,
            started_at=datetime.now(),
            status="ACTIVE"
        )
        
        evidence = PhaseEvidence(
            evidence_id="consistency_evidence",
            phase_id=phase_id,
            evidence_type="TEST_EXECUTION",
            evidence_data={"test_results": {"passed": 0, "failed": 5}},
            collected_at=datetime.now(),
            phase_type="RED"
        )
        
        checkpoint = GitCheckpoint(
            checkpoint_id="consistency_checkpoint",
            phase_id=phase_id,
            phase_type="RED",
            commit_hash="consistency_hash",
            branch_name="feature/consistency",
            checkpoint_time=datetime.now(),
            metadata=CheckpointMetadata(
                feature_id=feature_id,
                layer_id=layer_id,
                test_status="FAILING",
                files_changed=[],
                code_coverage=0.0,
                test_results={"passed": 0, "failed": 5}
            )
        )
        
        # Verify cross-model consistency
        assert phase.feature_id == checkpoint.metadata.feature_id
        assert phase.layer_id == checkpoint.metadata.layer_id
        assert evidence.evidence_data["test_results"] == checkpoint.metadata.test_results
        assert evidence.phase_type == checkpoint.phase_type == phase.phase_type


if __name__ == "__main__":
    # This will FAIL in RED phase - expected behavior
    pytest.main([__file__, "-v", "--tb=short"])