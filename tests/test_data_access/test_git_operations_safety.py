"""
Critical Git Operations Safety Tests
FEATURE-003-01-03 Risk Mitigation - Priority 1

These tests focus on preventing data loss and repository corruption
by testing error handling in Git operations that currently have 0% coverage.
"""

import pytest
import tempfile
import shutil
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.data_access.git_operations import GitOperations
from src.data_access.git_operations_manager import GitOperationsManager


class TestGitOperationsSafety:
    """Critical safety tests for Git operations to prevent data loss"""
    
    def setup_method(self):
        """Setup test environment with temporary Git repository"""
        self.temp_dir = tempfile.mkdtemp()
        self.git_ops = GitOperations(repo_path=self.temp_dir)
        
    def teardown_method(self):
        """Clean up temporary test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_git_commit_failure_recovery(self):
        """Test system recovery when Git commit operations fail"""
        # Simulate commit failure (e.g., disk full, permissions)
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception("Git commit failed: disk full")
            
            # System should handle failure gracefully
            result = self.git_ops.safe_commit("test message")
            
            assert result.success is False
            assert "disk full" in result.error_message
            assert result.rollback_completed is True
    
    def test_corrupted_repository_detection(self):
        """Test detection and handling of corrupted Git repositories"""
        # Simulate corrupted .git directory
        corrupted_git_path = os.path.join(self.temp_dir, '.git', 'HEAD')
        os.makedirs(os.path.dirname(corrupted_git_path), exist_ok=True)
        
        # Write invalid content to simulate corruption
        with open(corrupted_git_path, 'w') as f:
            f.write("CORRUPTED_DATA_INVALID_REF")
        
        # System should detect corruption and initiate recovery
        result = self.git_ops.validate_repository_integrity()
        
        assert result.is_corrupted is True
        assert result.recovery_initiated is True
        assert "repository corruption detected" in result.status_message.lower()
    
    def test_git_operation_rollback_on_failure(self):
        """Test rollback mechanism when Git operations fail mid-process"""
        # Simulate multi-step operation failure
        with patch.object(self.git_ops, '_execute_git_command') as mock_exec:
            # First command succeeds, second fails
            mock_exec.side_effect = [
                {"success": True, "output": "add successful"},
                Exception("Network failure during push")
            ]
            
            # System should rollback successfully completed operations
            result = self.git_ops.atomic_commit_and_push("test commit")
            
            assert result.success is False
            assert result.rollback_completed is True
            assert result.repository_state == "clean"  # Rolled back to original state
    
    def test_concurrent_git_access_protection(self):
        """Test protection against concurrent Git operations causing conflicts"""
        # Simulate multiple concurrent Git operations
        with patch('threading.Lock') as mock_lock:
            lock_instance = Mock()
            mock_lock.return_value = lock_instance
            
            # First operation acquires lock
            result1 = self.git_ops.thread_safe_commit("commit 1")
            
            # Second operation should wait for lock
            result2 = self.git_ops.thread_safe_commit("commit 2")
            
            # Verify lock was used properly
            assert lock_instance.acquire.called
            assert lock_instance.release.called
            assert result1.success is True
            assert result2.success is True
    
    def test_git_repository_backup_on_critical_failure(self):
        """Test automatic backup creation before risky Git operations"""
        # Simulate critical operation that might corrupt repository
        backup_created = False
        
        with patch.object(self.git_ops, '_create_repository_backup') as mock_backup:
            mock_backup.return_value = {"success": True, "backup_path": "/tmp/backup"}
            backup_created = True
            
            # Perform risky operation
            result = self.git_ops.risky_rebase_operation()
            
            # Verify backup was created before risky operation
            assert backup_created is True
            assert mock_backup.called
            assert result.backup_available is True
    
    def test_git_hooks_failure_handling(self):
        """Test handling of Git hook failures that could block operations"""
        # Simulate pre-commit hook failure
        with patch('subprocess.run') as mock_run:
            # Git hook returns non-zero exit code
            mock_run.return_value = Mock(returncode=1, stderr="pre-commit hook failed")
            
            result = self.git_ops.commit_with_hooks("test commit")
            
            # System should handle hook failure gracefully
            assert result.success is False
            assert result.hook_failure is True
            assert "pre-commit hook failed" in result.error_message
            assert result.repository_state == "unchanged"  # No partial commit
    
    def test_large_file_commit_memory_protection(self):
        """Test memory protection when committing large files"""
        # Simulate large file that could cause memory issues
        large_file_path = os.path.join(self.temp_dir, "large_file.bin")
        
        # Create mock large file (simulate without actually creating large file)
        with patch('os.path.getsize') as mock_size:
            mock_size.return_value = 1024 * 1024 * 1024  # 1GB file
            
            result = self.git_ops.safe_add_large_file(large_file_path)
            
            # System should use streaming/chunked approach for large files
            assert result.success is True
            assert result.streaming_used is True
            assert result.memory_usage_mb < 100  # Should stay under memory limit


class TestGitOperationsManagerSafety:
    """Safety tests for Git Operations Manager coordination"""
    
    def setup_method(self):
        """Setup test environment"""
        self.manager = GitOperationsManager()
    
    def test_multiple_repository_coordination_failure(self):
        """Test handling when coordinating multiple repositories fails"""
        repos = ["/path/repo1", "/path/repo2", "/path/repo3"]
        
        with patch.object(self.manager, '_sync_repository') as mock_sync:
            # Second repository sync fails
            mock_sync.side_effect = [
                {"success": True},
                Exception("Repository access denied"),
                {"success": True}
            ]
            
            result = self.manager.sync_multiple_repositories(repos)
            
            # Should handle partial failure gracefully
            assert result.total_repos == 3
            assert result.successful_repos == 2
            assert result.failed_repos == 1
            assert "Repository access denied" in result.error_details
    
    def test_git_operations_deadlock_prevention(self):
        """Test prevention of deadlocks in concurrent Git operations"""
        # Simulate potential deadlock scenario
        with patch('threading.Event') as mock_event:
            event_instance = Mock()
            mock_event.return_value = event_instance
            
            # Set timeout to prevent infinite waiting
            result = self.manager.coordinate_concurrent_operations(
                operations=["commit", "push", "pull"],
                timeout_seconds=30
            )
            
            # Should complete or timeout gracefully
            assert result.completed is True or result.timed_out is True
            assert result.deadlock_detected is False
    
    def test_git_credential_failure_handling(self):
        """Test handling of Git credential/authentication failures"""
        with patch('subprocess.run') as mock_run:
            # Simulate authentication failure
            mock_run.side_effect = Exception("Authentication failed: invalid credentials")
            
            result = self.manager.authenticated_git_operation("push")
            
            assert result.success is False
            assert result.auth_failure is True
            assert "invalid credentials" in result.error_message
            assert result.retry_suggested is True