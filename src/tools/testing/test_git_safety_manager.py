#!/usr/bin/env python3
"""
Test Suite for Git Safety Manager - Phase 2D Integration Layer

Comprehensive testing for TR-IL-003: Git Safety & Automation
Tests the Git Safety Manager's ability to provide safe git operations
for TDD workflow execution.
"""

import pytest
import tempfile
import subprocess
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add src to path for imports
import sys
# Import (using root src - not PROJECT-003 specific)
sys.path.append('/workspaces/control_tower/src')

from integration.git_safety_manager import (
    GitSafetyManager, GitState, BranchType, GitSafetyCheckpoint,
    BranchInfo, CommitInfo, GitOperationResult
)
from business_logic.work_item_model import WorkItem, ItemStatus, ProjectType, Priority, RequirementLevel


class TestGitSafetyManager:
    """Test suite for Git Safety Manager"""
    
    @pytest.fixture
    def temp_git_repo(self):
        """Create temporary git repository for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            
            # Initialize git repository
            subprocess.run(["git", "init"], cwd=repo_path, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_path, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_path, capture_output=True)
            
            # Create initial commit
            test_file = repo_path / "README.md"
            test_file.write_text("# Test Repository")
            subprocess.run(["git", "add", "README.md"], cwd=repo_path, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, capture_output=True)
            
            yield repo_path
    
    @pytest.fixture
    def git_manager(self, temp_git_repo):
        """Create GitSafetyManager instance with test repository"""
        return GitSafetyManager(str(temp_git_repo))
    
    @pytest.fixture
    def sample_work_item(self):
        """Create sample work item for testing"""
        return WorkItem(
            id="FEATURE-001-05-02",
            title="Automated Rebalancing Execution",
            description="Test feature for automated rebalancing",
            due_date=None,
            priority=Priority.MEDIUM,
            effort_estimate="5 days",
            requirement_level=RequirementLevel.FR,
            project_type=ProjectType.APPLICATION,
            repository="test_repo",
            system_name="Test System",
            project_name="Test Project",
            layer_or_milestone="Feature Layer",
            hierarchy_path="NSR/PR/SR/FR",
            status=ItemStatus.NOT_DUE
        )

    def test_git_manager_initialization(self, temp_git_repo):
        """Test GitSafetyManager initialization"""
        manager = GitSafetyManager(str(temp_git_repo))
        
        assert manager.repository_path == temp_git_repo
        assert manager.safety_checkpoints == []
        assert manager.active_branches == {}

    def test_git_manager_initialization_invalid_repo(self):
        """Test GitSafetyManager initialization with invalid repository"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Non-git directory
            with pytest.raises(ValueError, match="Not a git repository"):
                GitSafetyManager(temp_dir)

    def test_is_git_repository(self, git_manager, temp_git_repo):
        """Test git repository detection"""
        assert git_manager._is_git_repository() is True
        
        # Test with non-git directory
        with tempfile.TemporaryDirectory() as non_git_dir:
            non_git_manager = GitSafetyManager.__new__(GitSafetyManager)
            non_git_manager.repository_path = Path(non_git_dir)
            assert non_git_manager._is_git_repository() is False

    def test_run_git_command_success(self, git_manager):
        """Test successful git command execution"""
        success, output = git_manager._run_git_command(["status", "--porcelain"])
        
        assert success is True
        assert isinstance(output, str)

    def test_run_git_command_failure(self, git_manager):
        """Test failed git command execution"""
        success, output = git_manager._run_git_command(["invalid-command"])
        
        assert success is False
        assert "unknown" in output.lower() or "not a git command" in output.lower()

    def test_get_repository_state_clean(self, git_manager):
        """Test getting clean repository state"""
        state = git_manager.get_repository_state()
        
        assert state == GitState.CLEAN

    def test_get_repository_state_dirty(self, git_manager, temp_git_repo):
        """Test getting dirty repository state"""
        # Create uncommitted changes
        test_file = temp_git_repo / "dirty_file.txt"
        test_file.write_text("Uncommitted changes")
        
        state = git_manager.get_repository_state()
        
        assert state == GitState.DIRTY

    def test_get_current_branch(self, git_manager):
        """Test getting current branch name"""
        branch = git_manager.get_current_branch()
        
        # Should be main or master (default branch)
        assert branch in ["main", "master"]

    def test_validate_repository_safety_clean(self, git_manager):
        """Test repository safety validation with clean state"""
        result = git_manager.validate_repository_safety()
        
        assert result.success is True
        assert "safe for workflow execution" in result.message
        assert result.operation == "validate_safety"
        assert "state" in result.details
        assert "branch" in result.details

    def test_validate_repository_safety_dirty(self, git_manager, temp_git_repo):
        """Test repository safety validation with dirty state"""
        # Create uncommitted changes
        test_file = temp_git_repo / "dirty_file.txt"
        test_file.write_text("Uncommitted changes")
        
        result = git_manager.validate_repository_safety()
        
        assert result.success is False
        assert "uncommitted changes" in result.message.lower()
        assert len(result.recovery_suggestions) > 0
        assert any("commit" in suggestion.lower() for suggestion in result.recovery_suggestions)

    def test_create_safety_checkpoint_success(self, git_manager, sample_work_item):
        """Test successful safety checkpoint creation"""
        result = git_manager.create_safety_checkpoint(sample_work_item)
        
        assert result.success is True
        assert "Safety checkpoint created" in result.message
        assert result.operation == "create_checkpoint"
        assert "checkpoint_id" in result.details
        assert "branch" in result.details
        assert "commit_hash" in result.details
        
        # Verify checkpoint was recorded
        assert len(git_manager.safety_checkpoints) == 1
        checkpoint = git_manager.safety_checkpoints[0]
        assert checkpoint.work_item_id == sample_work_item.id
        assert checkpoint.branch_name.startswith("safety/")

    def test_create_safety_checkpoint_dirty_repo(self, git_manager, sample_work_item, temp_git_repo):
        """Test safety checkpoint creation with dirty repository"""
        # Create uncommitted changes
        test_file = temp_git_repo / "dirty_file.txt"
        test_file.write_text("Uncommitted changes")
        
        result = git_manager.create_safety_checkpoint(sample_work_item)
        
        assert result.success is False
        assert "repository not safe" in result.message
        assert len(result.recovery_suggestions) > 0

    def test_create_feature_branch_success(self, git_manager, sample_work_item):
        """Test successful feature branch creation"""
        result = git_manager.create_feature_branch(sample_work_item)
        
        assert result.success is True
        assert "Feature branch created" in result.message
        assert result.operation == "create_feature_branch"
        assert "branch_name" in result.details
        assert "work_item_id" in result.details
        
        # Verify branch was recorded
        branch_name = result.details["branch_name"]
        assert branch_name in git_manager.active_branches
        branch_info = git_manager.active_branches[branch_name]
        assert branch_info.work_item_id == sample_work_item.id
        assert branch_info.branch_type == BranchType.FEATURE

    def test_commit_info_message_generation(self):
        """Test CommitInfo structured message generation"""
        commit_info = CommitInfo(
            commit_type="feat",
            scope="FEATURE-001",
            description="Implement automated rebalancing",
            body="Add core rebalancing logic",
            work_item_id="FEATURE-001-05-02",
            workflow_stage="GREEN"
        )
        
        message = commit_info.generate_message()
        
        assert message.startswith("feat(FEATURE-001): Implement automated rebalancing")
        assert "Add core rebalancing logic" in message
        assert "Work Item: FEATURE-001-05-02" in message
        assert "TDD Stage: GREEN" in message

    def test_commit_info_breaking_change(self):
        """Test CommitInfo with breaking change"""
        commit_info = CommitInfo(
            commit_type="feat",
            scope="API",
            description="Change authentication method",
            breaking_change=True
        )
        
        message = commit_info.generate_message()
        
        assert message.startswith("feat(API)!: Change authentication method")

    def test_commit_workflow_stage_success(self, git_manager, sample_work_item, temp_git_repo):
        """Test successful workflow stage commit"""
        # Create feature branch first
        git_manager.create_feature_branch(sample_work_item)
        
        # Make some changes
        test_file = temp_git_repo / "implementation.py"
        test_file.write_text("# Implementation code")
        
        result = git_manager.commit_workflow_stage(
            work_item=sample_work_item,
            stage="GREEN",
            description="Implement core functionality",
            files_changed=["implementation.py"]
        )
        
        assert result.success is True
        assert "Committed GREEN stage" in result.message
        assert result.operation == "commit_stage"
        assert "stage" in result.details
        assert "commit_hash" in result.details

    def test_commit_workflow_stage_no_changes(self, git_manager, sample_work_item):
        """Test workflow stage commit with no changes"""
        result = git_manager.commit_workflow_stage(
            work_item=sample_work_item,
            stage="GREEN",
            description="Implement core functionality"
        )
        
        assert result.success is False
        assert "No staged changes" in result.message
        assert len(result.recovery_suggestions) > 0

    def test_recover_from_checkpoint_success(self, git_manager, sample_work_item):
        """Test successful checkpoint recovery"""
        # Create checkpoint first
        checkpoint_result = git_manager.create_safety_checkpoint(sample_work_item)
        assert checkpoint_result.success is True
        
        checkpoint_id = checkpoint_result.details["checkpoint_id"]
        
        # Recover from checkpoint
        result = git_manager.recover_from_checkpoint(checkpoint_id)
        
        assert result.success is True
        assert f"Repository recovered to checkpoint {checkpoint_id}" in result.message
        assert result.operation == "recover_checkpoint"
        assert "checkpoint_id" in result.details

    def test_recover_from_checkpoint_not_found(self, git_manager):
        """Test checkpoint recovery with invalid checkpoint ID"""
        result = git_manager.recover_from_checkpoint("nonexistent-checkpoint")
        
        assert result.success is False
        assert "Safety checkpoint not found" in result.message
        assert len(result.recovery_suggestions) > 0

    def test_cleanup_workflow_branches_success(self, git_manager, sample_work_item):
        """Test successful workflow branch cleanup"""
        # Create checkpoint and feature branch
        git_manager.create_safety_checkpoint(sample_work_item)
        git_manager.create_feature_branch(sample_work_item)
        
        # Verify branches exist
        assert len(git_manager.safety_checkpoints) == 1
        assert len(git_manager.active_branches) == 1
        
        # Cleanup branches
        result = git_manager.cleanup_workflow_branches(sample_work_item.id)
        
        assert result.success is True
        assert "Cleaned up" in result.message
        assert result.operation == "cleanup_branches"
        assert len(result.details["cleaned_branches"]) >= 1
        
        # Verify cleanup
        work_item_checkpoints = [cp for cp in git_manager.safety_checkpoints if cp.work_item_id == sample_work_item.id]
        work_item_branches = [name for name, info in git_manager.active_branches.items() if info.work_item_id == sample_work_item.id]
        
        assert len(work_item_checkpoints) == 0
        assert len(work_item_branches) == 0

    def test_cleanup_workflow_branches_no_branches(self, git_manager, sample_work_item):
        """Test cleanup with no branches to clean"""
        result = git_manager.cleanup_workflow_branches(sample_work_item.id)
        
        assert result.success is True
        assert "No branches found" in result.message
        assert len(result.details["cleaned_branches"]) == 0

    def test_get_workflow_status(self, git_manager, sample_work_item):
        """Test workflow status retrieval"""
        # Create checkpoint and feature branch
        git_manager.create_safety_checkpoint(sample_work_item)
        git_manager.create_feature_branch(sample_work_item)
        
        status = git_manager.get_workflow_status(sample_work_item.id)
        
        assert status["work_item_id"] == sample_work_item.id
        assert "repository_state" in status
        assert "current_branch" in status
        assert len(status["safety_checkpoints"]) == 1
        assert len(status["active_branches"]) == 1
        
        # Verify checkpoint details
        checkpoint = status["safety_checkpoints"][0]
        assert "id" in checkpoint
        assert "branch" in checkpoint
        assert "created_at" in checkpoint
        assert "commit_hash" in checkpoint
        
        # Verify branch details
        branch = status["active_branches"][0]
        assert "name" in branch
        assert "type" in branch
        assert "created_at" in branch

    def test_git_operation_result_structure(self):
        """Test GitOperationResult data structure"""
        result = GitOperationResult(
            success=True,
            message="Operation completed",
            operation="test_operation",
            details={"key": "value"},
            recovery_suggestions=["suggestion1", "suggestion2"]
        )
        
        assert result.success is True
        assert result.message == "Operation completed"
        assert result.operation == "test_operation"
        assert result.details == {"key": "value"}
        assert result.recovery_suggestions == ["suggestion1", "suggestion2"]

    def test_git_operation_result_defaults(self):
        """Test GitOperationResult with default values"""
        result = GitOperationResult(
            success=False,
            message="Operation failed",
            operation="test_operation"
        )
        
        assert result.details == {}
        assert result.recovery_suggestions == []

    def test_branch_info_structure(self):
        """Test BranchInfo data structure"""
        branch_info = BranchInfo(
            name="feature/test-branch",
            branch_type=BranchType.FEATURE,
            work_item_id="TEST-001",
            created_at=datetime.now(),
            tracking_remote="origin",
            parent_branch="main",
            description="Test branch"
        )
        
        assert branch_info.name == "feature/test-branch"
        assert branch_info.branch_type == BranchType.FEATURE
        assert branch_info.work_item_id == "TEST-001"
        assert branch_info.tracking_remote == "origin"
        assert branch_info.parent_branch == "main"
        assert branch_info.description == "Test branch"

    def test_git_safety_checkpoint_structure(self):
        """Test GitSafetyCheckpoint data structure"""
        checkpoint = GitSafetyCheckpoint(
            checkpoint_id="TEST-001-20250914",
            branch_name="safety/TEST-001-20250914",
            commit_hash="abc123def456",
            created_at=datetime.now(),
            work_item_id="TEST-001",
            original_branch="main",
            checkpoint_message="Safety checkpoint for test"
        )
        
        assert checkpoint.checkpoint_id == "TEST-001-20250914"
        assert checkpoint.branch_name == "safety/TEST-001-20250914"
        assert checkpoint.commit_hash == "abc123def456"
        assert checkpoint.work_item_id == "TEST-001"
        assert checkpoint.original_branch == "main"
        assert checkpoint.checkpoint_message == "Safety checkpoint for test"

    @patch('subprocess.run')
    def test_git_command_timeout_handling(self, mock_run, git_manager):
        """Test git command timeout handling"""
        mock_run.side_effect = subprocess.TimeoutExpired("git", 30)
        
        success, output = git_manager._run_git_command(["status"])
        
        assert success is False
        assert "timed out" in output.lower()

    @patch('subprocess.run')
    def test_git_command_exception_handling(self, mock_run, git_manager):
        """Test git command exception handling"""
        mock_run.side_effect = Exception("Test exception")
        
        success, output = git_manager._run_git_command(["status"])
        
        assert success is False
        assert "Test exception" in output


class TestGitSafetyManagerIntegration:
    """Integration tests for Git Safety Manager with real git operations"""
    
    def test_complete_workflow_simulation(self, temp_git_repo, sample_work_item):
        """Test complete TDD workflow with git safety"""
        manager = GitSafetyManager(str(temp_git_repo))
        
        # 1. Validate repository safety
        safety_result = manager.validate_repository_safety()
        assert safety_result.success is True
        
        # 2. Create safety checkpoint
        checkpoint_result = manager.create_safety_checkpoint(sample_work_item)
        assert checkpoint_result.success is True
        
        # 3. Create feature branch
        branch_result = manager.create_feature_branch(sample_work_item)
        assert branch_result.success is True
        
        # 4. Simulate TDD workflow stages
        stages = ["RED", "GREEN", "REFACTOR"]
        
        for i, stage in enumerate(stages):
            # Create test file for this stage
            test_file = temp_git_repo / f"stage_{stage.lower()}.py"
            test_file.write_text(f"# {stage} phase implementation")
            
            # Commit stage
            commit_result = manager.commit_workflow_stage(
                work_item=sample_work_item,
                stage=stage,
                description=f"Implement {stage} phase",
                files_changed=[f"stage_{stage.lower()}.py"]
            )
            assert commit_result.success is True
        
        # 5. Get workflow status
        status = manager.get_workflow_status(sample_work_item.id)
        assert len(status["safety_checkpoints"]) == 1
        assert len(status["active_branches"]) == 1
        
        # 6. Cleanup workflow
        cleanup_result = manager.cleanup_workflow_branches(sample_work_item.id)
        assert cleanup_result.success is True
        
        print("✅ Complete Git Safety Workflow: All stages completed successfully")

    @pytest.fixture
    def temp_git_repo(self):
        """Create temporary git repository for integration testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            
            # Initialize git repository
            subprocess.run(["git", "init"], cwd=repo_path, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_path, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_path, capture_output=True)
            
            # Create initial commit
            test_file = repo_path / "README.md"
            test_file.write_text("# Test Repository")
            subprocess.run(["git", "add", "README.md"], cwd=repo_path, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, capture_output=True)
            
            yield repo_path
    
    @pytest.fixture
    def sample_work_item(self):
        """Create sample work item for integration testing"""
        return WorkItem(
            id="FEATURE-001-05-02",
            title="Automated Rebalancing Execution",
            description="Test feature for automated rebalancing",
            due_date=None,
            priority=Priority.MEDIUM,
            effort_estimate="5 days",
            requirement_level=RequirementLevel.FR,
            project_type=ProjectType.APPLICATION,
            repository="test_repo",
            system_name="Test System",
            project_name="Test Project",
            layer_or_milestone="Feature Layer",
            hierarchy_path="NSR/PR/SR/FR",
            status=ItemStatus.NOT_DUE
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])