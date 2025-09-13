"""
Unit Tests for TR-IL-001 Git Integration

This module provides comprehensive unit testing for the Git Integration component,
covering all acceptance criteria IL-001 through IL-004 with mock git operations
and error scenario validation.

Test Coverage:
- Repository status checking (IL-001)
- Uncommitted changes detection (IL-002) 
- Non-git directory handling (IL-003)
- Repository connectivity status (IL-004)
- Error handling and graceful degradation
- Edge cases and boundary conditions

Author: Control Tower Development Team
Version: 1.0.0 (Phase 1 Integration Layer Tests)
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil
from pathlib import Path
import subprocess

from src.integration.git_integration import (
    GitIntegration, 
    GitRepositoryInfo, 
    RepositoryStatus,
    GitCommandResult
)


class TestGitIntegration(unittest.TestCase):
    """Test suite for Git Integration functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.git_integration = GitIntegration()
        self.temp_dir = tempfile.mkdtemp()
        self.test_repo_path = str(Path(self.temp_dir) / "test_repo")
        self.non_git_path = str(Path(self.temp_dir) / "non_git")
        
        # Create directories
        Path(self.test_repo_path).mkdir(parents=True)
        Path(self.non_git_path).mkdir(parents=True)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    # IL-001: Validates git repository status
    def test_check_repository_status_valid_git_repo(self):
        """Test repository status checking for valid git repository."""
        # Create mock git repository
        git_dir = Path(self.test_repo_path) / '.git'
        git_dir.mkdir()
        
        with patch.object(self.git_integration, '_run_git_command') as mock_git:
            # Mock git commands for a clean repository
            mock_git.side_effect = [
                GitCommandResult(True, "main", "", 0),  # get current branch
                GitCommandResult(True, "", "", 0),      # diff --cached --quiet (no staged)
                GitCommandResult(True, "", "", 0),      # diff --quiet (no unstaged)
                GitCommandResult(True, "", "", 0),      # ls-files --others (no untracked)
                GitCommandResult(True, "abc12345", "", 0),  # rev-parse --short HEAD
                GitCommandResult(True, "https://github.com/test/repo.git", "", 0)  # remote get-url
            ]
            
            result = self.git_integration.check_repository_status(self.test_repo_path)
            
            self.assertIsInstance(result, GitRepositoryInfo)
            self.assertTrue(result.is_git_repo)
            self.assertEqual(result.status, RepositoryStatus.CLEAN)
            self.assertEqual(result.current_branch, "main")
            self.assertFalse(result.has_uncommitted)
            self.assertEqual(result.path, self.test_repo_path)
    
    def test_check_repository_status_with_uncommitted_changes(self):
        """Test repository status with uncommitted changes."""
        git_dir = Path(self.test_repo_path) / '.git'
        git_dir.mkdir()
        
        with patch.object(self.git_integration, '_run_git_command') as mock_git:
            # Mock git commands showing uncommitted changes
            mock_git.side_effect = [
                GitCommandResult(True, "feature/test", "", 0),  # current branch
                GitCommandResult(False, "", "", 1),  # diff --cached --quiet (has staged)
                GitCommandResult(True, "", "", 0),   # diff --quiet (no unstaged)
                GitCommandResult(True, "", "", 0),   # ls-files --others (no untracked)
                GitCommandResult(True, "def67890", "", 0),  # last commit
                GitCommandResult(True, "https://github.com/test/repo.git", "", 0)  # remote
            ]
            
            result = self.git_integration.check_repository_status(self.test_repo_path)
            
            self.assertTrue(result.is_git_repo)
            self.assertEqual(result.status, RepositoryStatus.UNCOMMITTED_CHANGES)
            self.assertEqual(result.current_branch, "feature/test")
            self.assertTrue(result.has_uncommitted)
    
    def test_check_repository_status_invalid_path(self):
        """Test repository status checking for invalid path."""
        invalid_path = "/non/existent/path"
        
        result = self.git_integration.check_repository_status(invalid_path)
        
        self.assertFalse(result.is_git_repo)
        self.assertEqual(result.status, RepositoryStatus.ERROR)
        self.assertIn("does not exist", result.error_message)
        self.assertEqual(result.path, invalid_path)
    
    # IL-002: Reports uncommitted changes safely
    def test_has_uncommitted_changes_staged_files(self):
        """Test detection of staged uncommitted changes."""
        git_dir = Path(self.test_repo_path) / '.git'
        git_dir.mkdir()
        
        with patch.object(self.git_integration, '_run_git_command') as mock_git:
            mock_git.side_effect = [
                GitCommandResult(False, "", "", 1),  # diff --cached --quiet (has staged)
                GitCommandResult(True, "", "", 0),   # diff --quiet (no unstaged)  
                GitCommandResult(True, "", "", 0),   # ls-files --others (no untracked)
            ]
            
            result = self.git_integration.has_uncommitted_changes(self.test_repo_path)
            self.assertTrue(result)
    
    def test_has_uncommitted_changes_unstaged_files(self):
        """Test detection of unstaged uncommitted changes."""
        git_dir = Path(self.test_repo_path) / '.git'
        git_dir.mkdir()
        
        with patch.object(self.git_integration, '_run_git_command') as mock_git:
            mock_git.side_effect = [
                GitCommandResult(True, "", "", 0),   # diff --cached --quiet (no staged)
                GitCommandResult(False, "", "", 1),  # diff --quiet (has unstaged)
                GitCommandResult(True, "", "", 0),   # ls-files --others (no untracked)
            ]
            
            result = self.git_integration.has_uncommitted_changes(self.test_repo_path)
            self.assertTrue(result)
    
    def test_has_uncommitted_changes_untracked_files(self):
        """Test detection of untracked files."""
        git_dir = Path(self.test_repo_path) / '.git'
        git_dir.mkdir()
        
        with patch.object(self.git_integration, '_run_git_command') as mock_git:
            mock_git.side_effect = [
                GitCommandResult(True, "", "", 0),   # diff --cached --quiet (no staged)
                GitCommandResult(True, "", "", 0),   # diff --quiet (no unstaged)
                GitCommandResult(True, "new_file.txt\n", "", 0),  # ls-files --others (has untracked)
            ]
            
            result = self.git_integration.has_uncommitted_changes(self.test_repo_path)
            self.assertTrue(result)
    
    def test_has_uncommitted_changes_clean_repo(self):
        """Test clean repository with no uncommitted changes."""
        git_dir = Path(self.test_repo_path) / '.git'
        git_dir.mkdir()
        
        with patch.object(self.git_integration, '_run_git_command') as mock_git:
            mock_git.side_effect = [
                GitCommandResult(True, "", "", 0),   # diff --cached --quiet (no staged)
                GitCommandResult(True, "", "", 0),   # diff --quiet (no unstaged)
                GitCommandResult(True, "", "", 0),   # ls-files --others (no untracked)
            ]
            
            result = self.git_integration.has_uncommitted_changes(self.test_repo_path)
            self.assertFalse(result)
    
    # IL-003: Handles non-git directories gracefully
    def test_is_git_repository_with_git_dir(self):
        """Test git repository detection with .git directory."""
        git_dir = Path(self.test_repo_path) / '.git'
        git_dir.mkdir()
        
        result = self.git_integration.is_git_repository(self.test_repo_path)
        self.assertTrue(result)
    
    def test_is_git_repository_with_git_file(self):
        """Test git repository detection with .git file (submodule/worktree)."""
        git_file = Path(self.test_repo_path) / '.git'
        git_file.write_text("gitdir: /path/to/actual/git/dir")
        
        result = self.git_integration.is_git_repository(self.test_repo_path)
        self.assertTrue(result)
    
    def test_is_git_repository_non_git_directory(self):
        """Test non-git directory detection."""
        result = self.git_integration.is_git_repository(self.non_git_path)
        self.assertFalse(result)
    
    def test_is_git_repository_invalid_path(self):
        """Test git repository detection with invalid path."""
        result = self.git_integration.is_git_repository("/non/existent/path")
        self.assertFalse(result)
    
    def test_check_repository_status_non_git_directory(self):
        """Test repository status for non-git directory."""
        result = self.git_integration.check_repository_status(self.non_git_path)
        
        self.assertFalse(result.is_git_repo)
        self.assertEqual(result.status, RepositoryStatus.NOT_GIT_REPOSITORY)
        self.assertIsNone(result.current_branch)
        self.assertFalse(result.has_uncommitted)
    
    # IL-004: Provides repository connectivity status
    def test_get_repository_connectivity_status_with_remote(self):
        """Test connectivity status for repository with remote."""
        git_dir = Path(self.test_repo_path) / '.git'
        git_dir.mkdir()
        
        with patch.object(self.git_integration, '_run_git_command') as mock_git:
            mock_git.side_effect = [
                GitCommandResult(True, "https://github.com/test/repo.git", "", 0),  # remote get-url
                GitCommandResult(True, "origin/main\n", "", 0),  # ls-remote
                GitCommandResult(True, "0\t0", "", 0),  # rev-list --count --left-right
            ]
            
            result = self.git_integration.get_repository_connectivity_status(self.test_repo_path)
            
            self.assertTrue(result['has_remote'])
            self.assertTrue(result['remote_reachable'])
            self.assertFalse(result['behind_remote'])
            self.assertFalse(result['ahead_remote'])
            self.assertEqual(result['remote_url'], "https://github.com/test/repo.git")
    
    def test_get_repository_connectivity_status_no_remote(self):
        """Test connectivity status for repository without remote."""
        git_dir = Path(self.test_repo_path) / '.git'
        git_dir.mkdir()
        
        with patch.object(self.git_integration, '_run_git_command') as mock_git:
            mock_git.side_effect = [
                GitCommandResult(False, "", "fatal: No such remote 'origin'", 128),  # no remote
            ]
            
            result = self.git_integration.get_repository_connectivity_status(self.test_repo_path)
            
            self.assertFalse(result['has_remote'])
            self.assertFalse(result['remote_reachable'])
            self.assertIsNone(result['remote_url'])
    
    def test_get_repository_connectivity_status_unreachable_remote(self):
        """Test connectivity status for unreachable remote."""
        git_dir = Path(self.test_repo_path) / '.git'
        git_dir.mkdir()
        
        with patch.object(self.git_integration, '_run_git_command') as mock_git:
            mock_git.side_effect = [
                GitCommandResult(True, "https://github.com/test/repo.git", "", 0),  # remote get-url
                GitCommandResult(False, "", "fatal: unable to access", 128),  # ls-remote fails
            ]
            
            result = self.git_integration.get_repository_connectivity_status(self.test_repo_path)
            
            self.assertTrue(result['has_remote'])
            self.assertFalse(result['remote_reachable'])
            self.assertEqual(result['remote_url'], "https://github.com/test/repo.git")
    
    def test_get_repository_connectivity_status_non_git_repo(self):
        """Test connectivity status for non-git repository."""
        result = self.git_integration.get_repository_connectivity_status(self.non_git_path)
        
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'Not a git repository')
    
    # Current branch detection tests
    def test_get_current_branch_normal_branch(self):
        """Test getting current branch name."""
        git_dir = Path(self.test_repo_path) / '.git'
        git_dir.mkdir()
        
        with patch.object(self.git_integration, '_run_git_command') as mock_git:
            mock_git.return_value = GitCommandResult(True, "feature/new-feature", "", 0)
            
            result = self.git_integration.get_current_branch(self.test_repo_path)
            self.assertEqual(result, "feature/new-feature")
    
    def test_get_current_branch_detached_head(self):
        """Test getting branch name for detached HEAD."""
        git_dir = Path(self.test_repo_path) / '.git'
        git_dir.mkdir()
        
        with patch.object(self.git_integration, '_run_git_command') as mock_git:
            mock_git.side_effect = [
                GitCommandResult(True, "", "", 0),  # branch --show-current (empty for detached)
                GitCommandResult(True, "HEAD", "", 0),  # rev-parse --abbrev-ref HEAD
            ]
            
            result = self.git_integration.get_current_branch(self.test_repo_path)
            self.assertEqual(result, "detached HEAD")
    
    def test_get_current_branch_non_git_repo(self):
        """Test getting current branch for non-git repository."""
        result = self.git_integration.get_current_branch(self.non_git_path)
        self.assertIsNone(result)
    
    # Error handling tests
    def test_git_command_timeout(self):
        """Test git command timeout handling."""
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.side_effect = subprocess.TimeoutExpired(['git', 'status'], 5)
            
            result = self.git_integration._run_git_command(['status'], cwd=self.test_repo_path, timeout=1)
            
            self.assertFalse(result.success)
            self.assertIn("timed out", result.stderr)
            self.assertEqual(result.return_code, -1)
    
    def test_git_command_subprocess_error(self):
        """Test git command subprocess error handling."""
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.side_effect = OSError("Command not found")
            
            result = self.git_integration._run_git_command(['status'], cwd=self.test_repo_path)
            
            self.assertFalse(result.success)
            self.assertIn("Command not found", result.stderr)
            self.assertEqual(result.return_code, -1)
    
    def test_git_command_non_zero_exit(self):
        """Test git command with non-zero exit code."""
        with patch('subprocess.run') as mock_subprocess:
            mock_result = Mock()
            mock_result.returncode = 128
            mock_result.stdout = ""
            mock_result.stderr = "fatal: not a git repository"
            mock_subprocess.return_value = mock_result
            
            result = self.git_integration._run_git_command(['status'], cwd=self.test_repo_path)
            
            self.assertFalse(result.success)
            self.assertEqual(result.return_code, 128)
            self.assertIn("not a git repository", result.stderr)
    
    # Integration test covering complete workflow
    def test_complete_git_integration_workflow(self):
        """Test complete git integration workflow with all operations."""
        git_dir = Path(self.test_repo_path) / '.git'
        git_dir.mkdir()
        
        with patch.object(self.git_integration, '_run_git_command') as mock_git:
            # Mock complete workflow: status check -> connectivity -> branch info
            mock_git.side_effect = [
                # Repository status check calls
                GitCommandResult(True, "main", "", 0),  # current branch
                GitCommandResult(True, "", "", 0),      # no staged changes
                GitCommandResult(True, "", "", 0),      # no unstaged changes  
                GitCommandResult(True, "", "", 0),      # no untracked files
                GitCommandResult(True, "abc12345", "", 0),  # last commit
                GitCommandResult(True, "https://github.com/test/repo.git", "", 0),  # remote url
                
                # Connectivity check calls
                GitCommandResult(True, "https://github.com/test/repo.git", "", 0),  # remote url
                GitCommandResult(True, "origin/main\n", "", 0),  # ls-remote (reachable)
                GitCommandResult(True, "main", "", 0),  # get current branch for sync check
                GitCommandResult(True, "1\t0", "", 0),  # rev-list (ahead=1, behind=0)
            ]
            
            # Test repository status
            status = self.git_integration.check_repository_status(self.test_repo_path)
            self.assertEqual(status.status, RepositoryStatus.CLEAN)
            self.assertEqual(status.current_branch, "main")
            
            # Test connectivity
            connectivity = self.git_integration.get_repository_connectivity_status(self.test_repo_path)
            self.assertTrue(connectivity['has_remote'])
            self.assertTrue(connectivity['remote_reachable'])
            self.assertFalse(connectivity['behind_remote'])  # ahead=1, behind=0
            self.assertTrue(connectivity['ahead_remote'])
            
            # Verify repository is recognized as git
            self.assertTrue(self.git_integration.is_git_repository(self.test_repo_path))
            
            # Verify no uncommitted changes
            mock_git.side_effect = [
                GitCommandResult(True, "", "", 0),   # no staged
                GitCommandResult(True, "", "", 0),   # no unstaged
                GitCommandResult(True, "", "", 0),   # no untracked
            ]
            self.assertFalse(self.git_integration.has_uncommitted_changes(self.test_repo_path))


if __name__ == '__main__':
    unittest.main()