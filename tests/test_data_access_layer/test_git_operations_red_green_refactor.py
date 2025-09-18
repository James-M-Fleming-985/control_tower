"""
RED PHASE TESTS: Git Operations for RED-GREEN-REFACTOR Cycle Enforcer  
====================================================================

LAYER: DATA ACCESS LAYER (LAYER-003-01-03-001)
PHASE: RED (All tests should FAIL initially)

Git Operations Under Test:
- GitOperationsManager: Core git repository management
- Branch management for TDD phases
- Checkpoint commit creation and management
- Git repository validation and initialization
- Performance requirements for git operations

These tests verify git integration functionality for TDD phase tracking.
ALL TESTS MUST FAIL INITIALLY to establish proper TDD workflow.
"""

import pytest
import tempfile
import shutil
import os
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import git  # gitpython library

# Import all required modules - GREEN phase implementation
from src.data_access.git_operations import (
    GitOperationsManager, GitRepositoryError, GitBranchManager,
    GitCheckpointManager, GitPerformanceMonitor
)
from src.data_access.git_checkpoint_models import (
    GitCheckpoint, CheckpointMetadata, GitOperation,
    OperationType, CheckpointStatus
)


class TestGitOperationsManager:
    """Test suite for Git Operations Manager core functionality"""
    
    def setup_method(self):
        """Setup test environment with temporary git repository"""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir) / "test_repo"
        self.repo_path.mkdir()
        
        # Initialize a real git repository for testing
        self.git_repo = git.Repo.init(str(self.repo_path))
        
        # Create initial commit
        readme_file = self.repo_path / "README.md"
        readme_file.write_text("# Test Repository for TDD Cycle Enforcer")
        self.git_repo.index.add([str(readme_file)])
        self.git_repo.index.commit("Initial commit")
        
    def teardown_method(self):
        """Cleanup test environment"""
        if hasattr(self, 'git_repo'):
            self.git_repo.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_git_operations_manager_initialization(self):
        """Test git operations manager initialization and validation"""
        # This test MUST FAIL initially (RED phase)
        assert GitOperationsManager is not None, "GitOperationsManager not implemented"
        
        manager = GitOperationsManager(str(self.repo_path))
        
        assert manager is not None
        assert manager.repo_path == str(self.repo_path)
        assert manager.is_valid_repository() == True
        assert manager.get_current_branch() is not None
        assert manager.is_git_available() == True
    
    def test_invalid_repository_handling(self):
        """Test handling of invalid git repository paths"""
        # This test MUST FAIL initially (RED phase)
        assert GitOperationsManager is not None, "GitOperationsManager not implemented"
        assert GitRepositoryError is not None, "GitRepositoryError not implemented"
        
        # Test with non-existent path
        with pytest.raises(GitRepositoryError) as exc_info:
            invalid_manager = GitOperationsManager("/nonexistent/repo/path")
            invalid_manager.validate_repository()
        
        assert "repository_not_found" in str(exc_info.value)
        
        # Test with non-git directory
        non_git_dir = Path(self.temp_dir) / "not_git"
        non_git_dir.mkdir()
        
        with pytest.raises(GitRepositoryError) as exc_info:
            invalid_manager = GitOperationsManager(str(non_git_dir))
            invalid_manager.validate_repository()
        
        assert "not_git_repository" in str(exc_info.value)
    
    def test_repository_status_and_health(self):
        """Test git repository status and health checks"""
        # This test MUST FAIL initially (RED phase)
        assert GitOperationsManager is not None, "GitOperationsManager not implemented"
        
        manager = GitOperationsManager(str(self.repo_path))
        
        # Test repository health
        health_status = manager.get_repository_health()
        assert health_status.is_healthy == True
        assert health_status.has_commits == True
        assert health_status.has_working_directory == True
        assert health_status.is_clean_working_tree == True
        
        # Test repository statistics
        repo_stats = manager.get_repository_statistics()
        assert repo_stats.total_commits >= 1  # At least initial commit
        assert repo_stats.total_branches >= 1  # At least main/master branch
        assert repo_stats.repository_size_mb > 0
    
    def test_git_configuration_management(self):
        """Test git configuration for TDD cycle tracking"""
        # This test MUST FAIL initially (RED phase)
        assert GitOperationsManager is not None, "GitOperationsManager not implemented"
        
        manager = GitOperationsManager(str(self.repo_path))
        
        # Configure for TDD workflow
        tdd_config = {
            "user.name": "TDD Cycle Enforcer",
            "user.email": "tdd@control-tower.dev",
            "commit.template": ".tdd-commit-template",
            "branch.autosetupmerge": "always",
            "branch.autosetuprebase": "always"
        }
        
        result = manager.configure_for_tdd_workflow(tdd_config)
        assert result.success == True
        
        # Verify configuration was applied
        config_verification = manager.verify_tdd_configuration()
        assert config_verification.user_configured == True
        assert config_verification.template_configured == True
        assert config_verification.branch_strategy_configured == True


class TestGitBranchManager:
    """Test suite for Git Branch Manager for TDD phases"""
    
    def setup_method(self):
        """Setup test environment with git repository"""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir) / "branch_test_repo"
        self.repo_path.mkdir()
        
        # Initialize git repository
        self.git_repo = git.Repo.init(str(self.repo_path))
        
        # Create initial commit
        initial_file = self.repo_path / "initial.py"
        initial_file.write_text("# Initial implementation")
        self.git_repo.index.add([str(initial_file)])
        self.git_repo.index.commit("Initial implementation")
        
    def teardown_method(self):
        """Cleanup test environment"""
        if hasattr(self, 'git_repo'):
            self.git_repo.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_tdd_branch_creation(self):
        """Test creation of TDD-specific branches"""
        # This test MUST FAIL initially (RED phase)
        assert GitBranchManager is not None, "GitBranchManager not implemented"
        
        branch_manager = GitBranchManager(str(self.repo_path))
        
        # Create feature branch for TDD cycle
        feature_branch_result = branch_manager.create_feature_branch(
            feature_id="FEATURE-003-01-03",
            layer_id="LAYER-003-01-03-001"
        )
        
        assert feature_branch_result.success == True
        assert feature_branch_result.branch_name == "feature/003-01-03/layer-003-01-03-001"
        assert feature_branch_result.branch_type == "feature"
        
        # Create phase-specific branches
        red_branch_result = branch_manager.create_phase_branch("RED", "FEATURE-003-01-03")
        assert red_branch_result.success == True
        assert red_branch_result.branch_name.endswith("-red")
        
        green_branch_result = branch_manager.create_phase_branch("GREEN", "FEATURE-003-01-03")
        assert green_branch_result.success == True
        assert green_branch_result.branch_name.endswith("-green")
        
        refactor_branch_result = branch_manager.create_phase_branch("REFACTOR", "FEATURE-003-01-03")
        assert refactor_branch_result.success == True
        assert refactor_branch_result.branch_name.endswith("-refactor")
    
    def test_branch_switching_for_phases(self):
        """Test branch switching during TDD phase transitions"""
        # This test MUST FAIL initially (RED phase)
        assert GitBranchManager is not None, "GitBranchManager not implemented"
        
        branch_manager = GitBranchManager(str(self.repo_path))
        
        # Create branches for all phases
        feature_branch = branch_manager.create_feature_branch("FEATURE-003-01-03", "LAYER-003-01-03-001")
        red_branch = branch_manager.create_phase_branch("RED", "FEATURE-003-01-03")
        green_branch = branch_manager.create_phase_branch("GREEN", "FEATURE-003-01-03")
        
        # Test switching to RED phase
        red_switch_result = branch_manager.switch_to_phase("RED", "FEATURE-003-01-03")
        assert red_switch_result.success == True
        assert red_switch_result.current_branch == red_branch.branch_name
        assert red_switch_result.previous_branch is not None
        
        # Test switching to GREEN phase
        green_switch_result = branch_manager.switch_to_phase("GREEN", "FEATURE-003-01-03")
        assert green_switch_result.success == True
        assert green_switch_result.current_branch == green_branch.branch_name
        assert green_switch_result.previous_branch == red_branch.branch_name
    
    def test_branch_validation_and_protection(self):
        """Test branch validation and protection rules"""
        # This test MUST FAIL initially (RED phase)
        assert GitBranchManager is not None, "GitBranchManager not implemented"
        
        branch_manager = GitBranchManager(str(self.repo_path))
        
        # Test branch naming validation
        valid_branch_name = branch_manager.validate_branch_name("feature/003-01-03/layer-001")
        assert valid_branch_name.is_valid == True
        assert valid_branch_name.follows_naming_convention == True
        
        invalid_branch_name = branch_manager.validate_branch_name("invalid_branch_name!")
        assert invalid_branch_name.is_valid == False
        assert "invalid_characters" in invalid_branch_name.validation_errors
        
        # Test branch protection rules
        protection_result = branch_manager.apply_branch_protection("main")
        assert protection_result.protection_applied == True
        assert "direct_push_blocked" in protection_result.protection_rules
        
        # Test phase transition rules
        transition_validation = branch_manager.validate_phase_transition("RED", "GREEN")
        assert transition_validation.is_valid == True
        
        invalid_transition = branch_manager.validate_phase_transition("RED", "REFACTOR")
        assert invalid_transition.is_valid == False
        assert "must_go_through_green" in invalid_transition.validation_errors
    
    def test_branch_cleanup_and_maintenance(self):
        """Test branch cleanup and maintenance operations"""
        # This test MUST FAIL initially (RED phase)
        assert GitBranchManager is not None, "GitBranchManager not implemented"
        
        branch_manager = GitBranchManager(str(self.repo_path))
        
        # Create multiple phase branches
        feature_id = "FEATURE-003-01-03"
        branch_manager.create_feature_branch(feature_id, "LAYER-003-01-03-001")
        branch_manager.create_phase_branch("RED", feature_id)
        branch_manager.create_phase_branch("GREEN", feature_id)
        branch_manager.create_phase_branch("REFACTOR", feature_id)
        
        # Test branch listing and categorization
        all_branches = branch_manager.list_all_branches()
        assert len(all_branches.feature_branches) >= 1
        assert len(all_branches.phase_branches) >= 3
        
        # Test cleanup of completed phases
        cleanup_result = branch_manager.cleanup_completed_phases(feature_id)
        assert cleanup_result.branches_cleaned >= 0
        assert cleanup_result.cleanup_successful == True
        
        # Test branch archival
        archive_result = branch_manager.archive_feature_branches(feature_id, "COMPLETED")
        assert archive_result.archival_successful == True
        assert archive_result.archived_branches_count >= 0


class TestGitCheckpointManager:
    """Test suite for Git Checkpoint Manager"""
    
    def setup_method(self):
        """Setup test environment with git repository"""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir) / "checkpoint_test_repo"
        self.repo_path.mkdir()
        
        # Initialize git repository
        self.git_repo = git.Repo.init(str(self.repo_path))
        
        # Create initial files and commit
        self.create_test_files()
        
    def teardown_method(self):
        """Cleanup test environment"""
        if hasattr(self, 'git_repo'):
            self.git_repo.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_files(self):
        """Create test files for checkpoint testing"""
        test_file = self.repo_path / "test_checkpoint.py"
        test_file.write_text("""
# RED phase test file
def test_failing_implementation():
    assert False, "RED phase - test should fail"

def test_another_failing():
    assert 1 == 0, "RED phase - another failing test"
""")
        
        src_file = self.repo_path / "src_implementation.py"
        src_file.write_text("""
# Implementation file - empty in RED phase
pass
""")
        
        self.git_repo.index.add([str(test_file), str(src_file)])
        self.git_repo.index.commit("Initial test files")
    
    def test_checkpoint_creation_red_phase(self):
        """Test creation of git checkpoints during RED phase"""
        # This test MUST FAIL initially (RED phase)
        assert GitCheckpointManager is not None, "GitCheckpointManager not implemented"
        assert GitCheckpoint is not None, "GitCheckpoint model not implemented"
        
        checkpoint_manager = GitCheckpointManager(str(self.repo_path))
        
        # Create RED phase checkpoint
        red_metadata = CheckpointMetadata(
            feature_id="FEATURE-003-01-03",
            layer_id="LAYER-003-01-03-001",
            test_status="FAILING",
            files_changed=["test_checkpoint.py"],
            code_coverage=0.0,
            test_results={"total": 2, "passed": 0, "failed": 2}
        )
        
        red_checkpoint = GitCheckpoint(
            checkpoint_id="red_checkpoint_001",
            phase_id="phase_001",
            phase_type="RED",
            commit_hash=None,  # Will be generated
            branch_name="feature/003-01-03-red",
            checkpoint_time=datetime.now(),
            metadata=red_metadata
        )
        
        checkpoint_result = checkpoint_manager.create_checkpoint(red_checkpoint)
        
        assert checkpoint_result.success == True
        assert checkpoint_result.commit_hash is not None
        assert len(checkpoint_result.commit_hash) >= 40  # Git SHA length
        assert checkpoint_result.checkpoint_time is not None
        assert checkpoint_result.files_committed == ["test_checkpoint.py"]
    
    def test_checkpoint_creation_green_phase(self):
        """Test creation of git checkpoints during GREEN phase"""
        # This test MUST FAIL initially (RED phase)
        assert GitCheckpointManager is not None, "GitCheckpointManager not implemented"
        
        checkpoint_manager = GitCheckpointManager(str(self.repo_path))
        
        # Modify files to simulate GREEN phase (passing tests)
        test_file = self.repo_path / "test_checkpoint.py"
        test_file.write_text("""
# GREEN phase test file - tests now pass
def test_passing_implementation():
    assert True, "GREEN phase - test passes"

def test_another_passing():
    assert 1 == 1, "GREEN phase - another passing test"
""")
        
        src_file = self.repo_path / "src_implementation.py"
        src_file.write_text("""
# Implementation file - minimal implementation for GREEN phase
def implementation_function():
    return True
""")
        
        # Create GREEN phase checkpoint
        green_metadata = CheckpointMetadata(
            feature_id="FEATURE-003-01-03",
            layer_id="LAYER-003-01-03-001",
            test_status="PASSING",
            files_changed=["test_checkpoint.py", "src_implementation.py"],
            code_coverage=85.5,
            test_results={"total": 2, "passed": 2, "failed": 0}
        )
        
        green_checkpoint = GitCheckpoint(
            checkpoint_id="green_checkpoint_001",
            phase_id="phase_001",
            phase_type="GREEN",
            commit_hash=None,
            branch_name="feature/003-01-03-green",
            checkpoint_time=datetime.now(),
            metadata=green_metadata
        )
        
        checkpoint_result = checkpoint_manager.create_checkpoint(green_checkpoint)
        
        assert checkpoint_result.success == True
        assert checkpoint_result.commit_hash is not None
        assert checkpoint_result.metadata.test_status == "PASSING"
        assert checkpoint_result.metadata.code_coverage > 80.0
    
    def test_checkpoint_retrieval_and_restoration(self):
        """Test checkpoint retrieval and restoration functionality"""
        # This test MUST FAIL initially (RED phase)
        assert GitCheckpointManager is not None, "GitCheckpointManager not implemented"
        
        checkpoint_manager = GitCheckpointManager(str(self.repo_path))
        
        # Create a checkpoint first
        metadata = CheckpointMetadata(
            feature_id="FEATURE-003-01-03",
            layer_id="LAYER-003-01-03-001",
            test_status="FAILING",
            files_changed=["test_file.py"],
            code_coverage=0.0,
            test_results={"passed": 0, "failed": 1}
        )
        
        checkpoint = GitCheckpoint(
            checkpoint_id="retrieval_test_001",
            phase_id="phase_001",
            phase_type="RED",
            commit_hash=None,
            branch_name="feature/retrieval-test",
            checkpoint_time=datetime.now(),
            metadata=metadata
        )
        
        create_result = checkpoint_manager.create_checkpoint(checkpoint)
        assert create_result.success == True
        
        # Test checkpoint retrieval
        retrieved_checkpoint = checkpoint_manager.get_checkpoint("retrieval_test_001")
        assert retrieved_checkpoint is not None
        assert retrieved_checkpoint.checkpoint_id == "retrieval_test_001"
        assert retrieved_checkpoint.phase_type == "RED"
        
        # Test checkpoint restoration
        restoration_result = checkpoint_manager.restore_to_checkpoint("retrieval_test_001")
        assert restoration_result.success == True
        assert restoration_result.restored_commit_hash == create_result.commit_hash
        assert restoration_result.restored_files is not None
    
    def test_checkpoint_performance_requirements(self):
        """Test checkpoint operations meet performance requirements"""
        # This test MUST FAIL initially (RED phase)
        assert GitCheckpointManager is not None, "GitCheckpointManager not implemented"
        
        checkpoint_manager = GitCheckpointManager(str(self.repo_path))
        
        # Test checkpoint creation performance (should be < 200ms)
        start_time = time.time()
        
        metadata = CheckpointMetadata(
            feature_id="FEATURE-003-01-03",
            layer_id="LAYER-003-01-03-001",
            test_status="FAILING",
            files_changed=["perf_test.py"],
            code_coverage=0.0,
            test_results={"passed": 0, "failed": 1}
        )
        
        checkpoint = GitCheckpoint(
            checkpoint_id="perf_test_001",
            phase_id="phase_001",
            phase_type="RED",
            commit_hash=None,
            branch_name="feature/perf-test",
            checkpoint_time=datetime.now(),
            metadata=metadata
        )
        
        result = checkpoint_manager.create_checkpoint(checkpoint)
        creation_time = (time.time() - start_time) * 1000  # Convert to ms
        
        assert result.success == True
        assert creation_time < 200, f"Checkpoint creation took {creation_time}ms, exceeds 200ms requirement"
        
        # Test checkpoint retrieval performance
        start_time = time.time()
        retrieved = checkpoint_manager.get_checkpoint("perf_test_001")
        retrieval_time = (time.time() - start_time) * 1000  # Convert to ms
        
        assert retrieved is not None
        assert retrieval_time < 200, f"Checkpoint retrieval took {retrieval_time}ms, exceeds 200ms requirement"


class TestGitPerformanceMonitor:
    """Test suite for Git Performance Monitoring"""
    
    def test_git_operation_performance_tracking(self):
        """Test performance tracking for git operations"""
        # This test MUST FAIL initially (RED phase)
        assert GitPerformanceMonitor is not None, "GitPerformanceMonitor not implemented"
        
        performance_monitor = GitPerformanceMonitor()
        
        # Track a git operation
        with performance_monitor.track_operation("COMMIT", "checkpoint_creation") as tracker:
            # Simulate git operation
            time.sleep(0.05)  # 50ms operation
        
        # Verify performance tracking
        operation_stats = performance_monitor.get_operation_stats("COMMIT")
        assert operation_stats.total_operations >= 1
        assert operation_stats.average_duration_ms < 200  # Should meet requirement
        assert operation_stats.max_duration_ms >= 50  # Should capture our test operation
        
        # Test performance thresholds
        threshold_violations = performance_monitor.get_threshold_violations()
        assert isinstance(threshold_violations, list)
        
        # Test performance reporting
        performance_report = performance_monitor.generate_performance_report()
        assert performance_report.total_operations >= 1
        assert performance_report.average_response_time_ms is not None
        assert performance_report.operations_meeting_sla_percentage >= 0
    
    def test_git_memory_usage_monitoring(self):
        """Test memory usage monitoring for git operations"""
        # This test MUST FAIL initially (RED phase)
        assert GitPerformanceMonitor is not None, "GitPerformanceMonitor not implemented"
        
        performance_monitor = GitPerformanceMonitor()
        
        # Monitor memory usage during git operations
        memory_baseline = performance_monitor.get_memory_usage()
        assert memory_baseline.current_usage_mb >= 0
        
        # Simulate memory-intensive git operation
        with performance_monitor.track_memory_usage() as memory_tracker:
            # Simulate some memory usage
            large_data = ["test"] * 10000  # Small memory allocation
        
        memory_stats = memory_tracker.get_final_stats()
        assert memory_stats.peak_usage_mb >= memory_baseline.current_usage_mb
        assert memory_stats.peak_usage_mb < 128  # Should meet requirement
    
    def test_git_throughput_monitoring(self):
        """Test throughput monitoring for git operations"""
        # This test MUST FAIL initially (RED phase)
        assert GitPerformanceMonitor is not None, "GitPerformanceMonitor not implemented"
        
        performance_monitor = GitPerformanceMonitor()
        
        # Simulate multiple git operations for throughput testing
        start_time = time.time()
        
        for i in range(10):
            with performance_monitor.track_operation("CHECKPOINT", f"throughput_test_{i}"):
                time.sleep(0.01)  # 10ms per operation
        
        end_time = time.time()
        total_time_minutes = (end_time - start_time) / 60
        
        # Calculate operations per minute
        throughput_stats = performance_monitor.get_throughput_stats()
        operations_per_minute = throughput_stats.operations_per_minute
        
        assert operations_per_minute >= 50, f"Throughput {operations_per_minute:.1f} ops/min below 50 requirement"
        assert throughput_stats.total_operations >= 10


# Integration Tests
class TestGitOperationsIntegration:
    """Integration tests for complete git operations workflow"""
    
    def setup_method(self):
        """Setup integrated test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir) / "integration_repo"
        self.repo_path.mkdir()
        
        # Initialize git repository
        self.git_repo = git.Repo.init(str(self.repo_path))
        
        # Create initial structure
        readme = self.repo_path / "README.md"
        readme.write_text("# TDD Cycle Integration Test")
        self.git_repo.index.add([str(readme)])
        self.git_repo.index.commit("Initial commit")
    
    def teardown_method(self):
        """Cleanup integrated test environment"""
        if hasattr(self, 'git_repo'):
            self.git_repo.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_complete_tdd_cycle_git_workflow(self):
        """Test complete TDD cycle git workflow integration"""
        # This test MUST FAIL initially (RED phase)
        assert GitOperationsManager is not None, "GitOperationsManager not implemented"
        assert GitBranchManager is not None, "GitBranchManager not implemented"
        assert GitCheckpointManager is not None, "GitCheckpointManager not implemented"
        
        # Initialize all managers
        ops_manager = GitOperationsManager(str(self.repo_path))
        branch_manager = GitBranchManager(str(self.repo_path))
        checkpoint_manager = GitCheckpointManager(str(self.repo_path))
        
        feature_id = "FEATURE-003-01-03"
        layer_id = "LAYER-003-01-03-001"
        
        # 1. Create feature branch
        feature_branch = branch_manager.create_feature_branch(feature_id, layer_id)
        assert feature_branch.success == True
        
        # 2. Create RED phase branch and checkpoint
        red_branch = branch_manager.create_phase_branch("RED", feature_id)
        assert red_branch.success == True
        
        # Switch to RED phase branch
        red_switch = branch_manager.switch_to_phase("RED", feature_id)
        assert red_switch.success == True
        
        # Create RED phase files
        test_file = self.repo_path / "test_integration.py"
        test_file.write_text("def test_failing(): assert False")
        
        # Create RED checkpoint
        red_metadata = CheckpointMetadata(
            feature_id=feature_id,
            layer_id=layer_id,
            test_status="FAILING",
            files_changed=["test_integration.py"],
            code_coverage=0.0,
            test_results={"passed": 0, "failed": 1}
        )
        
        red_checkpoint = GitCheckpoint(
            checkpoint_id="integration_red",
            phase_id="integration_phase",
            phase_type="RED",
            commit_hash=None,
            branch_name=red_branch.branch_name,
            checkpoint_time=datetime.now(),
            metadata=red_metadata
        )
        
        red_checkpoint_result = checkpoint_manager.create_checkpoint(red_checkpoint)
        assert red_checkpoint_result.success == True
        
        # 3. Transition to GREEN phase
        green_branch = branch_manager.create_phase_branch("GREEN", feature_id)
        green_switch = branch_manager.switch_to_phase("GREEN", feature_id)
        assert green_switch.success == True
        
        # Update files for GREEN phase
        test_file.write_text("def test_passing(): assert True")
        src_file = self.repo_path / "src_integration.py"
        src_file.write_text("def implementation(): return True")
        
        # Create GREEN checkpoint
        green_metadata = CheckpointMetadata(
            feature_id=feature_id,
            layer_id=layer_id,
            test_status="PASSING",
            files_changed=["test_integration.py", "src_integration.py"],
            code_coverage=95.0,
            test_results={"passed": 1, "failed": 0}
        )
        
        green_checkpoint = GitCheckpoint(
            checkpoint_id="integration_green",
            phase_id="integration_phase",
            phase_type="GREEN",
            commit_hash=None,
            branch_name=green_branch.branch_name,
            checkpoint_time=datetime.now(),
            metadata=green_metadata
        )
        
        green_checkpoint_result = checkpoint_manager.create_checkpoint(green_checkpoint)
        assert green_checkpoint_result.success == True
        
        # Verify complete workflow
        workflow_validation = ops_manager.validate_tdd_workflow_integrity(feature_id)
        assert workflow_validation.red_phase_complete == True
        assert workflow_validation.green_phase_complete == True
        assert workflow_validation.all_checkpoints_valid == True
        assert workflow_validation.branch_strategy_correct == True


if __name__ == "__main__":
    # This will FAIL in RED phase - expected behavior
    pytest.main([__file__, "-v", "--tb=short"])