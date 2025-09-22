"""
RED PHASE TESTS: TDD Phase Repository for RED-GREEN-REFACTOR Cycle Enforcer
==========================================================================

FEATURE: FEATURE-003-01-03 RED-GREEN-REFACTOR CYCLE ENFORCER
LAYER: DATA ACCESS LAYER (LAYER-003-01-03-001)
PHASE: RED (All tests should FAIL initially)

Core Functionality Under Test:
- REAL TDD phase state tracking and persistence
- REAL git checkpoint creation and management  
- REAL test execution result storage and verification
- REAL phase transition evidence collection

Performance Requirements:
- Response Time: < 200ms for phase state operations
- Throughput: 50+ phase transitions per minute
- Memory Usage: < 128MB for phase state cache
- Error Rate: < 0.05% for phase state operations

This test file implements the RED phase of TDD methodology.
ALL TESTS MUST FAIL INITIALLY to establish proper TDD workflow.
"""

import pytest
import sqlite3
import tempfile
import shutil
import json
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Import all required modules - GREEN phase implementation
from src.data_access.tdd_phase_repository import TDDPhaseRepository
from src.data_access.phase_models import (
    TDDPhase, PhaseState, PhaseTransition, PhaseEvidence
)
from src.data_access.git_checkpoint_models import (
    GitCheckpoint, CheckpointMetadata, GitOperation
)
from src.data_access.phase_data_interface import PhaseDataInterface
from src.data_access.git_operations import GitOperationsManager
from src.data_access.tdd_phase_repository import PhaseValidator


class TestTDDPhaseRepository:
    """Test suite for TDD Phase Repository core functionality"""
    
    def setup_method(self):
        """Setup test environment with temporary database and git repo"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_phases.db"
        self.git_repo_path = Path(self.temp_dir) / "test_repo"
        self.git_repo_path.mkdir()
        
        # Initialize mock git repository
        self.mock_git_repo = Mock()
        self.mock_git_repo.working_dir = str(self.git_repo_path)
        
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_phase_repository_initialization(self):
        """Test TDD phase repository initialization with database and git integration"""
        # This test MUST FAIL initially (RED phase)
        assert TDDPhaseRepository is not None, "TDDPhaseRepository class not implemented"
        
        repository = TDDPhaseRepository(
            db_path=str(self.db_path),
            git_repo_path=str(self.git_repo_path)
        )
        
        assert repository is not None
        assert repository.db_path == str(self.db_path)
        assert repository.git_repo_path == str(self.git_repo_path)
        assert repository.is_connected() == True
    
    def test_create_phase_state_record(self):
        """Test creation of new TDD phase state record"""
        # This test MUST FAIL initially (RED phase)
        assert TDDPhaseRepository is not None, "TDDPhaseRepository not implemented"
        assert TDDPhase is not None, "TDDPhase model not implemented"
        
        repository = TDDPhaseRepository(str(self.db_path), str(self.git_repo_path))
        
        phase = TDDPhase(
            phase_id="phase_001",
            phase_type="RED",
            feature_id="FEATURE-003-01-03",
            layer_id="LAYER-003-01-03-001",
            started_at=datetime.now(),
            status="ACTIVE"
        )
        
        result = repository.create_phase(phase)
        
        assert result is not None
        assert result.phase_id == "phase_001"
        assert result.phase_type == "RED"
        assert result.status == "ACTIVE"
    
    def test_phase_state_transitions(self):
        """Test TDD phase state transitions (RED -> GREEN -> REFACTOR)"""
        # This test MUST FAIL initially (RED phase)
        assert PhaseTransition is not None, "PhaseTransition model not implemented"
        
        repository = TDDPhaseRepository(str(self.db_path), str(self.git_repo_path))
        
        # Create initial RED phase
        red_phase = TDDPhase(
            phase_id="transition_001",
            phase_type="RED",
            feature_id="FEATURE-003-01-03",
            layer_id="LAYER-003-01-03-001",
            started_at=datetime.now(),
            status="ACTIVE"
        )
        
        repository.create_phase(red_phase)
        
        # Transition to GREEN phase
        green_transition = PhaseTransition(
            from_phase="RED",
            to_phase="GREEN",
            phase_id="transition_001",
            transition_time=datetime.now(),
            trigger_event="TEST_PASS",
            evidence={"test_results": "all_passing"}
        )
        
        result = repository.transition_phase(green_transition)
        
        assert result.success == True
        assert result.new_phase_type == "GREEN"
        assert result.transition_evidence is not None
    
    def test_git_checkpoint_creation(self):
        """Test git checkpoint creation during phase transitions"""
        # This test MUST FAIL initially (RED phase)
        assert GitCheckpoint is not None, "GitCheckpoint model not implemented"
        assert GitOperationsManager is not None, "GitOperationsManager not implemented"
        
        repository = TDDPhaseRepository(str(self.db_path), str(self.git_repo_path))
        git_manager = GitOperationsManager(str(self.git_repo_path))
        
        checkpoint = GitCheckpoint(
            checkpoint_id="checkpoint_001",
            phase_id="phase_001",
            phase_type="RED",
            commit_hash="abc123def456",
            branch_name="feature/tdd-cycle",
            checkpoint_time=datetime.now(),
            metadata=CheckpointMetadata(
                feature_id="FEATURE-003-01-03",
                layer_id="LAYER-003-01-03-001",
                test_status="FAILING",
                files_changed=["test_file.py", "src_file.py"]
            )
        )
        
        result = git_manager.create_checkpoint(checkpoint)
        
        assert result.success == True
        assert result.commit_hash is not None
        assert result.checkpoint_time is not None
    
    def test_test_execution_result_storage(self):
        """Test storage of test execution results with phase evidence"""
        # This test MUST FAIL initially (RED phase)
        assert PhaseEvidence is not None, "PhaseEvidence model not implemented"
        
        repository = TDDPhaseRepository(str(self.db_path), str(self.git_repo_path))
        
        test_evidence = PhaseEvidence(
            evidence_id="evidence_001",
            phase_id="phase_001",
            evidence_type="TEST_EXECUTION",
            evidence_data={
                "test_command": "pytest tests/",
                "exit_code": 1,
                "test_results": {
                    "total_tests": 15,
                    "passed": 0,
                    "failed": 15,
                    "skipped": 0
                },
                "execution_time": 2.5,
                "test_output": "15 failed, 0 passed in 2.50s"
            },
            collected_at=datetime.now(),
            phase_type="RED"
        )
        
        result = repository.store_evidence(test_evidence)
        
        assert result.success == True
        assert result.evidence_id == "evidence_001"
        assert result.storage_location is not None
    
    def test_phase_validation_rules(self):
        """Test TDD phase validation rules and constraints"""
        # This test MUST FAIL initially (RED phase)
        assert PhaseValidator is not None, "PhaseValidator not implemented"
        
        validator = PhaseValidator()
        
        # Test RED phase validation
        red_phase_data = {
            "phase_type": "RED",
            "test_status": "FAILING",
            "implementation_status": "NOT_STARTED",
            "test_evidence": {"failed_tests": 15, "passed_tests": 0}
        }
        
        red_validation = validator.validate_phase(red_phase_data)
        assert red_validation.is_valid == True
        assert red_validation.phase_type == "RED"
        
        # Test invalid GREEN phase (tests not passing)
        invalid_green_data = {
            "phase_type": "GREEN",
            "test_status": "FAILING",  # Invalid for GREEN
            "implementation_status": "COMPLETE",
            "test_evidence": {"failed_tests": 5, "passed_tests": 10}
        }
        
        invalid_validation = validator.validate_phase(invalid_green_data)
        assert invalid_validation.is_valid == False
        assert "tests_must_pass" in invalid_validation.validation_errors
    
    def test_performance_requirements_phase_operations(self):
        """Test that phase operations meet <200ms performance requirement"""
        # This test MUST FAIL initially (RED phase)
        assert TDDPhaseRepository is not None, "TDDPhaseRepository not implemented"
        
        repository = TDDPhaseRepository(str(self.db_path), str(self.git_repo_path))
        
        # Test phase creation performance
        start_time = time.time()
        
        phase = TDDPhase(
            phase_id="perf_001",
            phase_type="RED",
            feature_id="FEATURE-003-01-03",
            layer_id="LAYER-003-01-03-001",
            started_at=datetime.now(),
            status="ACTIVE"
        )
        
        result = repository.create_phase(phase)
        creation_time = (time.time() - start_time) * 1000  # Convert to ms
        
        assert creation_time < 200, f"Phase creation took {creation_time}ms, exceeds 200ms requirement"
        assert result is not None
        
        # Test phase retrieval performance
        start_time = time.time()
        retrieved_phase = repository.get_phase("perf_001")
        retrieval_time = (time.time() - start_time) * 1000  # Convert to ms
        
        assert retrieval_time < 200, f"Phase retrieval took {retrieval_time}ms, exceeds 200ms requirement"
        assert retrieved_phase.phase_id == "perf_001"
    
    def test_concurrent_phase_operations(self):
        """Test concurrent phase operations for throughput requirements (50+ transitions/min)"""
        # This test MUST FAIL initially (RED phase)
        import threading
        import queue
        
        assert TDDPhaseRepository is not None, "TDDPhaseRepository not implemented"
        
        repository = TDDPhaseRepository(str(self.db_path), str(self.git_repo_path))
        results_queue = queue.Queue()
        
        def create_phase_concurrent(phase_index):
            """Create phase concurrently"""
            try:
                phase = TDDPhase(
                    phase_id=f"concurrent_{phase_index}",
                    phase_type="RED",
                    feature_id="FEATURE-003-01-03",
                    layer_id="LAYER-003-01-03-001",
                    started_at=datetime.now(),
                    status="ACTIVE"
                )
                result = repository.create_phase(phase)
                results_queue.put(("success", phase_index, result))
            except Exception as e:
                results_queue.put(("error", phase_index, str(e)))
        
        # Create 60 concurrent phase operations to test throughput
        start_time = time.time()
        threads = []
        
        for i in range(60):
            thread = threading.Thread(target=create_phase_concurrent, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time_minutes = (end_time - start_time) / 60
        
        # Verify all operations completed successfully
        success_count = 0
        while not results_queue.empty():
            result_type, _, _ = results_queue.get()
            if result_type == "success":
                success_count += 1
        
        operations_per_minute = success_count / total_time_minutes
        
        assert success_count == 60, f"Only {success_count}/60 operations succeeded"
        assert operations_per_minute >= 50, f"Throughput {operations_per_minute:.1f} ops/min below 50 requirement"
    
    def test_error_handling_git_failures(self):
        """Test error handling for git operation failures"""
        # This test MUST FAIL initially (RED phase)
        assert GitOperationsManager is not None, "GitOperationsManager not implemented"
        
        # Test with invalid git repository path
        invalid_git_manager = GitOperationsManager("/nonexistent/repo/path")
        
        checkpoint = GitCheckpoint(
            checkpoint_id="error_001",
            phase_id="phase_001",
            phase_type="RED",
            commit_hash=None,  # Will be generated
            branch_name="feature/test",
            checkpoint_time=datetime.now(),
            metadata=CheckpointMetadata(
                feature_id="FEATURE-003-01-03",
                layer_id="LAYER-003-01-03-001",
                test_status="FAILING",
                files_changed=[]
            )
        )
        
        result = invalid_git_manager.create_checkpoint(checkpoint)
        
        assert result.success == False
        assert result.error_type == "GIT_REPOSITORY_NOT_FOUND"
        assert "nonexistent" in result.error_message
    
    def test_data_integrity_phase_state_corruption_recovery(self):
        """Test data integrity and recovery from phase state corruption"""
        # This test MUST FAIL initially (RED phase)
        assert TDDPhaseRepository is not None, "TDDPhaseRepository not implemented"
        
        repository = TDDPhaseRepository(str(self.db_path), str(self.git_repo_path))
        
        # Create valid phase
        phase = TDDPhase(
            phase_id="integrity_001",
            phase_type="RED",
            feature_id="FEATURE-003-01-03",
            layer_id="LAYER-003-01-03-001",
            started_at=datetime.now(),
            status="ACTIVE"
        )
        
        repository.create_phase(phase)
        
        # Simulate database corruption by directly modifying the database
        with sqlite3.connect(str(self.db_path)) as conn:
            # Corrupt the phase data
            conn.execute("UPDATE phases SET phase_type = 'INVALID' WHERE phase_id = ?", 
                        ("integrity_001",))
            conn.commit()
        
        # Test corruption detection and recovery
        recovery_result = repository.validate_and_recover_phase("integrity_001")
        
        assert recovery_result.corruption_detected == True
        assert recovery_result.recovery_successful == True
        assert recovery_result.recovered_from_git_backup == True
        
        # Verify phase is restored to valid state
        recovered_phase = repository.get_phase("integrity_001")
        assert recovered_phase.phase_type == "RED"  # Should be restored from git backup


class TestPhaseDataInterface:
    """Test suite for Phase Data Interface layer"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.git_repo_path = Path(self.temp_dir) / "test_repo"
        self.git_repo_path.mkdir()
    
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_phase_data_interface_initialization(self):
        """Test phase data interface initialization and configuration"""
        # This test MUST FAIL initially (RED phase)
        assert PhaseDataInterface is not None, "PhaseDataInterface not implemented"
        
        interface = PhaseDataInterface(
            db_connection_string=f"sqlite:///{self.temp_dir}/test.db",
            git_repo_path=str(self.git_repo_path)
        )
        
        assert interface is not None
        assert interface.is_connected() == True
        assert interface.supports_transactions() == True
    
    def test_phase_query_operations(self):
        """Test phase data query operations and filtering"""
        # This test MUST FAIL initially (RED phase)
        assert PhaseDataInterface is not None, "PhaseDataInterface not implemented"
        
        interface = PhaseDataInterface(
            db_connection_string=f"sqlite:///{self.temp_dir}/test.db",
            git_repo_path=str(self.git_repo_path)
        )
        
        # Query active phases
        active_phases = interface.query_phases(status="ACTIVE")
        assert isinstance(active_phases, list)
        
        # Query phases by type
        red_phases = interface.query_phases(phase_type="RED")
        assert isinstance(red_phases, list)
        
        # Query phases by feature
        feature_phases = interface.query_phases(feature_id="FEATURE-003-01-03")
        assert isinstance(feature_phases, list)
    
    def test_transaction_management(self):
        """Test transaction management for phase operations"""
        # This test MUST FAIL initially (RED phase)
        assert PhaseDataInterface is not None, "PhaseDataInterface not implemented"
        
        interface = PhaseDataInterface(
            db_connection_string=f"sqlite:///{self.temp_dir}/test.db",
            git_repo_path=str(self.git_repo_path)
        )
        
        # Test transaction rollback on error
        with interface.transaction() as tx:
            phase1 = TDDPhase(
                phase_id="tx_001",
                phase_type="RED",
                feature_id="FEATURE-003-01-03",
                layer_id="LAYER-003-01-03-001",
                started_at=datetime.now(),
                status="ACTIVE"
            )
            
            tx.create_phase(phase1)
            
            # Simulate error condition
            try:
                tx.create_phase(phase1)  # Duplicate should cause error
                assert False, "Duplicate phase creation should fail"
            except Exception:
                tx.rollback()  # Explicit rollback
        
        # Verify no phases were created due to rollback
        phases = interface.query_phases(phase_id="tx_001")
        assert len(phases) == 0


class TestGitOperationsManager:
    """Test suite for Git Operations Manager"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.git_repo_path = Path(self.temp_dir) / "test_repo"
        self.git_repo_path.mkdir()
    
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_git_repository_initialization(self):
        """Test git repository initialization and validation"""
        # This test MUST FAIL initially (RED phase)
        assert GitOperationsManager is not None, "GitOperationsManager not implemented"
        
        git_manager = GitOperationsManager(str(self.git_repo_path))
        
        assert git_manager is not None
        assert git_manager.repo_path == str(self.git_repo_path)
        assert git_manager.is_valid_repository() == True
    
    def test_branch_management_for_tdd_phases(self):
        """Test branch creation and management for TDD phases"""
        # This test MUST FAIL initially (RED phase)
        assert GitOperationsManager is not None, "GitOperationsManager not implemented"
        
        git_manager = GitOperationsManager(str(self.git_repo_path))
        
        # Create feature branch for TDD cycle
        branch_result = git_manager.create_feature_branch(
            feature_id="FEATURE-003-01-03",
            layer_id="LAYER-003-01-03-001"
        )
        
        assert branch_result.success == True
        assert branch_result.branch_name.startswith("feature/")
        assert "003-01-03" in branch_result.branch_name
        
        # Test branch switching for phase transitions
        switch_result = git_manager.switch_to_phase_branch("RED")
        assert switch_result.success == True
        assert switch_result.current_branch.endswith("-red")
    
    def test_checkpoint_commit_creation(self):
        """Test creation of checkpoint commits during phase transitions"""
        # This test MUST FAIL initially (RED phase)
        assert GitOperationsManager is not None, "GitOperationsManager not implemented"
        
        git_manager = GitOperationsManager(str(self.git_repo_path))
        
        # Create test files to commit
        test_file = self.git_repo_path / "test_example.py"
        test_file.write_text("# RED phase test file\ndef test_failing():\n    assert False")
        
        commit_result = git_manager.create_checkpoint_commit(
            phase_type="RED",
            message="RED phase checkpoint: failing tests implemented",
            files=["test_example.py"]
        )
        
        assert commit_result.success == True
        assert commit_result.commit_hash is not None
        assert len(commit_result.commit_hash) >= 40  # Git hash length
        assert "RED phase" in commit_result.commit_message


# Integration Tests
class TestDataAccessLayerIntegration:
    """Integration tests for complete data access layer functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_phases.db"
        self.git_repo_path = Path(self.temp_dir) / "test_repo"
        self.git_repo_path.mkdir()
    
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_complete_tdd_cycle_data_flow(self):
        """Test complete TDD cycle data flow through data access layer"""
        # This test MUST FAIL initially (RED phase)
        assert TDDPhaseRepository is not None, "TDDPhaseRepository not implemented"
        assert GitOperationsManager is not None, "GitOperationsManager not implemented"
        assert PhaseValidator is not None, "PhaseValidator not implemented"
        
        # Initialize all components
        repository = TDDPhaseRepository(str(self.db_path), str(self.git_repo_path))
        git_manager = GitOperationsManager(str(self.git_repo_path))
        validator = PhaseValidator()
        
        # RED Phase: Create failing tests
        red_phase = TDDPhase(
            phase_id="cycle_001",
            phase_type="RED",
            feature_id="FEATURE-003-01-03",
            layer_id="LAYER-003-01-03-001",
            started_at=datetime.now(),
            status="ACTIVE"
        )
        
        # Store RED phase
        red_result = repository.create_phase(red_phase)
        assert red_result.phase_id == "cycle_001"
        
        # Create git checkpoint for RED phase
        red_checkpoint = git_manager.create_checkpoint_commit(
            phase_type="RED",
            message="RED: Failing tests implemented",
            files=[]
        )
        assert red_checkpoint.success == True
        
        # Store test execution evidence (failing)
        red_evidence = PhaseEvidence(
            evidence_id="cycle_001_red",
            phase_id="cycle_001",
            evidence_type="TEST_EXECUTION",
            evidence_data={
                "test_results": {"passed": 0, "failed": 5},
                "exit_code": 1
            },
            collected_at=datetime.now(),
            phase_type="RED"
        )
        
        evidence_result = repository.store_evidence(red_evidence)
        assert evidence_result.success == True
        
        # Validate complete cycle data integrity
        cycle_validation = repository.validate_complete_cycle("cycle_001")
        assert cycle_validation.red_phase_complete == True
        assert cycle_validation.has_valid_git_checkpoints == True
        assert cycle_validation.has_test_evidence == True


if __name__ == "__main__":
    # This will FAIL in RED phase - expected behavior
    pytest.main([__file__, "-v", "--tb=short"])