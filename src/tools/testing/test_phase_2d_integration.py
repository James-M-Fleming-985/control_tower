#!/usr/bin/env python3
"""
Integration Tests for Phase 2D - Integration Layer

Tests the complete Phase 2D Integration Layer implementation including:
- TR-IL-003: Git Safety Manager
- TR-IL-004: Tool Integration Manager
- Integration between both components

This validates that Phase 2D provides the required integration capabilities
for external tool coordination and git safety operations.
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
sys.path.append('/workspaces/control_tower/src')

from integration.git_safety_manager import GitSafetyManager, GitState, BranchType
from integration.tool_integration_manager import (
    ToolIntegrationManager, ToolType, ToolStatus, ExecutionResult
)
from business_logic.work_item_model import WorkItem, ItemStatus, ProjectType, Priority, RequirementLevel


class TestPhase2DIntegration:
    """Integration tests for complete Phase 2D functionality"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace with git repository"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize git repository
            subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=temp_dir)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_dir)
            
            # Create initial commit
            test_file = Path(temp_dir) / "README.md"
            test_file.write_text("# Test Repository")
            subprocess.run(["git", "add", "README.md"], cwd=temp_dir)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=temp_dir)
            
            yield temp_dir
    
    @pytest.fixture
    def git_manager(self, temp_workspace):
        """Create GitSafetyManager instance"""
        return GitSafetyManager(temp_workspace)
    
    @pytest.fixture
    def tool_manager(self, temp_workspace):
        """Create ToolIntegrationManager instance"""
        return ToolIntegrationManager(temp_workspace)
    
    @pytest.fixture
    def sample_work_item(self):
        """Create sample work item for testing"""
        return WorkItem(
            id="TR-IL-005",
            title="Integration Test Work Item",
            description="Test work item for Phase 2D integration testing",
            due_date=None,
            priority=Priority.MEDIUM,
            effort_estimate="2 days",
            requirement_level=RequirementLevel.TR,
            project_type=ProjectType.APPLICATION,
            repository="test_repo",
            system_name="Control Tower",
            project_name="Phase 2D Integration",
            layer_or_milestone="Integration Layer",
            hierarchy_path="NSR/PR/SR/FR/TR",
            status=ItemStatus.NOT_DUE
        )
    
    def test_git_safety_and_tool_integration_initialization(self, git_manager, tool_manager, temp_workspace):
        """Test that both integration managers initialize correctly"""
        # Test Git Safety Manager
        assert git_manager.repository_path == Path(temp_workspace)
        assert git_manager._is_git_repository()
        
        # Test Tool Integration Manager
        assert tool_manager.workspace_path == Path(temp_workspace)
        assert "pytest" in tool_manager.tools
        assert "coverage" in tool_manager.tools
    
    def test_environment_validation_workflow(self, git_manager, tool_manager, sample_work_item):
        """Test complete environment validation workflow"""
        # Mock git operations to ensure they work
        with patch.object(git_manager, 'get_current_branch', return_value='main'):
            # 1. Validate git repository safety
            safety_result = git_manager.validate_repository_safety()
            assert safety_result.success
            
            # 2. Validate development tools
            environment_status = tool_manager.validate_environment()
            assert "pytest" in environment_status
            assert "coverage" in environment_status
            
            # 3. Get comprehensive environment summary
            summary = tool_manager.get_environment_summary()
            assert summary["workspace_path"] == str(tool_manager.workspace_path)
            assert "tools" in summary
    
    @patch('subprocess.run')
    def test_tdd_workflow_integration(self, mock_git_run, git_manager, tool_manager, sample_work_item, temp_workspace):
        """Test TDD workflow integration with git safety and tool execution"""
        # Mock git operations
        mock_git_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        with patch.object(git_manager, 'get_current_branch', return_value='main'):
            # 1. Create safety checkpoint before starting work
            checkpoint_result = git_manager.create_safety_checkpoint(sample_work_item)
            assert checkpoint_result.success
            
            # 2. Create feature branch for work
            branch_result = git_manager.create_feature_branch(sample_work_item)
            assert branch_result.success
            
            # 3. Execute a tool command to test integration
            with patch.object(tool_manager.tools['pytest'], 'execute') as mock_pytest_execute:
                mock_pytest_execute.return_value = MagicMock(
                    tool_name="pytest",
                    result=ExecutionResult.SUCCESS,
                    stdout="2 passed",
                    return_code=0
                )
                
                test_result = tool_manager.execute_tool_command("pytest", "test.py")
                assert test_result.result == ExecutionResult.SUCCESS
            
            # 4. Check execution history
            history = tool_manager.get_execution_history()
            assert len(history) >= 1
            assert history[-1].tool_name == "pytest"
            
            # 5. Get current workflow status
            workflow_status = git_manager.get_workflow_status(sample_work_item)
            assert isinstance(workflow_status, dict)
    
    @patch('subprocess.run')
    def test_git_operations_with_tool_validation(self, mock_run, git_manager, tool_manager, sample_work_item):
        """Test git operations coordinated with tool validation"""
        # Mock git operations
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="",
            stderr=""
        )
        
        with patch.object(git_manager, 'get_current_branch', return_value='main'):
            # 1. Validate environment before git operations
            environment_status = tool_manager.validate_environment()
            
            # 2. Create checkpoint with validated environment
            checkpoint_result = git_manager.create_safety_checkpoint(sample_work_item)
            assert checkpoint_result.success
            
            # 3. Perform commit workflow stage
            commit_result = git_manager.commit_workflow_stage(
                sample_work_item,
                stage="RED",
                description="Add failing test"
            )
            assert commit_result.success
            
            # 4. Verify git commands were executed
            assert mock_run.called
    
    def test_error_recovery_workflow(self, git_manager, tool_manager, sample_work_item):
        """Test error recovery workflow using both managers"""
        with patch.object(git_manager, 'get_current_branch', return_value='main'), \
             patch('subprocess.run') as mock_run:
            
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            
            # 1. Create checkpoint for recovery point
            checkpoint_result = git_manager.create_safety_checkpoint(sample_work_item)
            assert checkpoint_result.success
            
            # 2. Simulate tool execution failure
            with patch.object(tool_manager, 'execute_tool_command') as mock_execute:
                mock_execute.return_value = MagicMock(
                    result=ExecutionResult.FAILURE,
                    error_details="Test failed"
                )
                
                # Execute failing command
                result = tool_manager.execute_tool_command("pytest", "test_broken.py")
                assert result.result == ExecutionResult.FAILURE
            
            # 3. Recovery using git checkpoint
            recovery_result = git_manager.recover_from_checkpoint(sample_work_item)
            assert recovery_result.success
            
            # 4. Verify execution history recorded the failure
            history = tool_manager.get_execution_history()
            assert len(history) >= 1
            assert any(r.result == ExecutionResult.FAILURE for r in history)
    
    def test_cleanup_workflow(self, git_manager, tool_manager, sample_work_item):
        """Test cleanup workflow for both git and tool resources"""
        with patch.object(git_manager, 'get_current_branch', return_value='main'), \
             patch('subprocess.run') as mock_run:
            
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            
            # 1. Create resources that need cleanup
            checkpoint_result = git_manager.create_safety_checkpoint(sample_work_item)
            assert checkpoint_result.success
            
            branch_result = git_manager.create_feature_branch(sample_work_item)
            assert branch_result.success
            
            # 2. Execute some tool commands to create history
            with patch.object(tool_manager, 'execute_tool_command') as mock_execute:
                mock_execute.return_value = MagicMock(
                    result=ExecutionResult.SUCCESS
                )
                tool_manager.run_tests()
            
            # 3. Cleanup git branches
            cleanup_result = git_manager.cleanup_workflow_branches(sample_work_item)
            assert cleanup_result.success
            
            # 4. Verify execution history is maintained
            history = tool_manager.get_execution_history()
            assert len(history) >= 1
    
    def test_comprehensive_status_reporting(self, git_manager, tool_manager, sample_work_item):
        """Test comprehensive status reporting across both managers"""
        with patch.object(git_manager, 'get_current_branch', return_value='main'):
            # 1. Get git workflow status
            git_status = git_manager.get_workflow_status(sample_work_item)
            assert isinstance(git_status, dict)  # get_workflow_status returns dict, not GitOperationResult
            
            # 2. Get tool environment summary
            tool_summary = tool_manager.get_environment_summary()
            assert "tools" in tool_summary
            assert "available_tools" in tool_summary
            
            # 3. Validate that both provide complementary information
            assert isinstance(git_status, dict)
            assert isinstance(tool_summary, dict)
            
            # Both should contain workspace/repository information
            assert str(tool_manager.workspace_path) in tool_summary["workspace_path"]
    
    @patch('subprocess.run')
    def test_full_tdd_cycle_integration(self, mock_git_run, git_manager, tool_manager, sample_work_item):
        """Test complete TDD cycle with both git safety and tool integration"""
        # Mock successful git operations
        mock_git_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        with patch.object(git_manager, 'get_current_branch', return_value='main'), \
             patch.object(tool_manager.tools['pytest'], 'execute') as mock_pytest_execute:
            
            # Mock test execution phases
            test_results = [
                MagicMock(tool_name="pytest", result=ExecutionResult.FAILURE, stdout="1 failed"),  # RED
                MagicMock(tool_name="pytest", result=ExecutionResult.SUCCESS, stdout="1 passed"),  # GREEN
                MagicMock(tool_name="pytest", result=ExecutionResult.SUCCESS, stdout="1 passed"),  # REFACTOR
            ]
            mock_pytest_execute.side_effect = test_results
            
            # 1. Initialize workflow
            checkpoint_result = git_manager.create_safety_checkpoint(sample_work_item)
            assert checkpoint_result.success
            
            branch_result = git_manager.create_feature_branch(sample_work_item)
            assert branch_result.success
            
            # 2. RED Phase
            red_test_result = tool_manager.execute_tool_command("pytest", "test.py")
            assert red_test_result.result == ExecutionResult.FAILURE
            
            red_commit = git_manager.commit_workflow_stage(sample_work_item, "RED", "Add failing test")
            assert red_commit.success
            
            # 3. GREEN Phase
            green_test_result = tool_manager.execute_tool_command("pytest", "test.py")
            assert green_test_result.result == ExecutionResult.SUCCESS
            
            green_commit = git_manager.commit_workflow_stage(sample_work_item, "GREEN", "Make test pass")
            assert green_commit.success
            
            # 4. REFACTOR Phase
            refactor_test_result = tool_manager.execute_tool_command("pytest", "test.py")
            assert refactor_test_result.result == ExecutionResult.SUCCESS
            
            refactor_commit = git_manager.commit_workflow_stage(sample_work_item, "REFACTOR", "Improve code quality")
            assert refactor_commit.success
            
            # 5. Verify complete workflow
            workflow_status = git_manager.get_workflow_status(sample_work_item)
            assert isinstance(workflow_status, dict)
            
            execution_history = tool_manager.get_execution_history()
            assert len(execution_history) == 3  # Three test executions
            
            # Verify all phases were executed
            assert mock_pytest_execute.call_count == 3
        
    def test_phase_2d_capability_verification(self, git_manager, tool_manager):
        """Verify that Phase 2D provides all required integration capabilities"""
        # TR-IL-003: Git Safety & Automation
        git_capabilities = [
            hasattr(git_manager, 'validate_repository_safety'),
            hasattr(git_manager, 'create_safety_checkpoint'),
            hasattr(git_manager, 'create_feature_branch'),
            hasattr(git_manager, 'commit_workflow_stage'),
            hasattr(git_manager, 'recover_from_checkpoint'),
            hasattr(git_manager, 'cleanup_workflow_branches'),
            hasattr(git_manager, 'get_workflow_status')
        ]
        assert all(git_capabilities), "Missing Git Safety capabilities"
        
        # TR-IL-004: Tool Integration & Environment Management
        tool_capabilities = [
            hasattr(tool_manager, 'validate_environment'),
            hasattr(tool_manager, 'execute_tool_command'),
            hasattr(tool_manager, 'run_tests'),
            hasattr(tool_manager, 'generate_coverage_report'),
            hasattr(tool_manager, 'install_missing_tools'),
            hasattr(tool_manager, 'get_execution_history'),
            hasattr(tool_manager, 'get_environment_summary')
        ]
        assert all(tool_capabilities), "Missing Tool Integration capabilities"
        
        # Integration capabilities
        assert git_manager.repository_path.exists()
        assert tool_manager.workspace_path.exists()
        assert str(git_manager.repository_path) == str(tool_manager.workspace_path)


class TestPhase2DRequirementCompliance:
    """Test Phase 2D compliance with requirements TR-IL-003 and TR-IL-004"""
    
    def test_tr_il_003_compliance(self):
        """Verify TR-IL-003 Git Safety & Automation requirements"""
        # Import and verify Git Safety Manager exists
        from integration.git_safety_manager import GitSafetyManager
        
        # Verify required classes and enums
        from integration.git_safety_manager import GitState, BranchType, GitSafetyCheckpoint
        
        # Verify core methods exist
        required_methods = [
            'validate_repository_safety',
            'create_safety_checkpoint',
            'create_feature_branch',
            'commit_workflow_stage',
            'recover_from_checkpoint',
            'cleanup_workflow_branches',
            'get_workflow_status'
        ]
        
        for method in required_methods:
            assert hasattr(GitSafetyManager, method), f"Missing required method: {method}"
    
    def test_tr_il_004_compliance(self):
        """Verify TR-IL-004 Tool Integration & Environment Management requirements"""
        # Import and verify Tool Integration Manager exists
        from integration.tool_integration_manager import ToolIntegrationManager
        
        # Verify required classes and enums
        from integration.tool_integration_manager import ToolType, ToolStatus, ExecutionResult
        
        # Verify core methods exist
        required_methods = [
            'validate_environment',
            'execute_tool_command',
            'run_tests',
            'generate_coverage_report',
            'install_missing_tools',
            'get_execution_history',
            'get_environment_summary'
        ]
        
        for method in required_methods:
            assert hasattr(ToolIntegrationManager, method), f"Missing required method: {method}"
    
    def test_phase_2d_integration_layer_complete(self):
        """Verify Phase 2D Integration Layer is complete with both components"""
        # Both components should be importable
        from integration.git_safety_manager import GitSafetyManager
        from integration.tool_integration_manager import ToolIntegrationManager
        
        # Both should work with WorkItem from Phase 2B
        from business_logic.work_item_model import WorkItem
        
        # Integration should be possible - use current workspace which is a git repo
        workspace_dir = "/workspaces/control_tower"
        git_manager = GitSafetyManager(workspace_dir)
        tool_manager = ToolIntegrationManager(workspace_dir)
        
        # Both should reference the same workspace
        assert str(git_manager.repository_path) == str(tool_manager.workspace_path)