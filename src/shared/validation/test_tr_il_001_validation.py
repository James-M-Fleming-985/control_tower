"""
Validation Tests for TR-IL-001 Git Integration

This module provides acceptance criteria validation tests for TR-IL-001 Git Integration,
ensuring all requirements IL-001 through IL-004 are properly implemented and validated
against real-world scenarios.

Validation Coverage:
- IL-001: Validates git repository status
- IL-002: Reports uncommitted changes safely
- IL-003: Handles non-git directories gracefully
- IL-004: Provides repository connectivity status

Author: Control Tower Development Team
Version: 1.0.0 (Phase 1 Integration Layer Validation)
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, Mock
import subprocess

from src.integration.git_integration import (
    GitIntegration, 
    GitRepositoryInfo, 
    RepositoryStatus,
    GitCommandResult
)


class TestTR_IL_001_Validation(unittest.TestCase):
    """Validation test suite for TR-IL-001 Git Integration acceptance criteria."""
    
    def setUp(self):
        """Set up validation test fixtures."""
        self.git_integration = GitIntegration()
        self.temp_dir = tempfile.mkdtemp()
        self.mock_repo_path = str(Path(self.temp_dir) / "mock_git_repo")
        self.non_git_path = str(Path(self.temp_dir) / "regular_directory")
        self.invalid_path = "/completely/invalid/path/that/does/not/exist"
        
        # Create test directories
        Path(self.mock_repo_path).mkdir(parents=True)
        Path(self.non_git_path).mkdir(parents=True)
        
        # Create mock .git directory ONLY in mock_repo_path
        (Path(self.mock_repo_path) / '.git').mkdir()
        
        # Ensure non_git_path does NOT have .git directory
        non_git_git_dir = Path(self.non_git_path) / '.git'
        if non_git_git_dir.exists():
            shutil.rmtree(non_git_git_dir)
    
    def tearDown(self):
        """Clean up validation test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_IL_001_validates_git_repository_status(self):
        """
        Validation Test: IL-001 - Validates git repository status
        
        Requirements:
        - Must correctly identify git repositories
        - Must extract current branch information
        - Must determine overall repository status
        - Must handle repository metadata safely
        """
        with patch.object(self.git_integration, '_run_git_command') as mock_git:
            # Mock a complete, clean git repository
            mock_git.side_effect = [
                GitCommandResult(True, "main", "", 0),  # current branch
                GitCommandResult(True, "", "", 0),      # no staged changes
                GitCommandResult(True, "", "", 0),      # no unstaged changes
                GitCommandResult(True, "", "", 0),      # no untracked files
                GitCommandResult(True, "a1b2c3d4", "", 0),  # last commit hash
                GitCommandResult(True, "https://github.com/control-tower/test.git", "", 0)  # remote url
            ]
            
            # Execute repository status validation
            result = self.git_integration.check_repository_status(self.mock_repo_path)
            
            # Validate IL-001 requirements
            self.assertIsInstance(result, GitRepositoryInfo, "Must return GitRepositoryInfo object")
            self.assertTrue(result.is_git_repo, "Must correctly identify git repository")
            self.assertEqual(result.current_branch, "main", "Must extract current branch name")
            self.assertEqual(result.status, RepositoryStatus.CLEAN, "Must determine clean repository status")
            self.assertEqual(result.path, self.mock_repo_path, "Must preserve repository path")
            self.assertEqual(result.last_commit, "a1b2c3d4", "Must extract commit hash")
            self.assertEqual(result.remote_url, "https://github.com/control-tower/test.git", "Must extract remote URL")
            self.assertIsNone(result.error_message, "Must not have error for valid repository")
            
            print("✅ IL-001: Repository status validation PASSED")
    
    def test_IL_002_reports_uncommitted_changes_safely(self):
        """
        Validation Test: IL-002 - Reports uncommitted changes safely
        
        Requirements:
        - Must detect staged changes
        - Must detect unstaged changes  
        - Must detect untracked files
        - Must not modify repository state
        - Must handle git command failures gracefully
        """
        with patch.object(self.git_integration, '_run_git_command') as mock_git:
            # Test Case 1: Repository with staged changes
            mock_git.side_effect = [
                GitCommandResult(False, "", "", 1),  # has staged changes (diff --cached returns 1)
                GitCommandResult(True, "", "", 0),   # no unstaged changes
                GitCommandResult(True, "", "", 0),   # no untracked files
            ]
            
            result = self.git_integration.has_uncommitted_changes(self.mock_repo_path)
            self.assertTrue(result, "Must detect staged changes")
            
            # Test Case 2: Repository with unstaged changes
            mock_git.side_effect = [
                GitCommandResult(True, "", "", 0),   # no staged changes
                GitCommandResult(False, "", "", 1),  # has unstaged changes (diff returns 1)
                GitCommandResult(True, "", "", 0),   # no untracked files
            ]
            
            result = self.git_integration.has_uncommitted_changes(self.mock_repo_path)
            self.assertTrue(result, "Must detect unstaged changes")
            
            # Test Case 3: Repository with untracked files
            mock_git.side_effect = [
                GitCommandResult(True, "", "", 0),   # no staged changes
                GitCommandResult(True, "", "", 0),   # no unstaged changes
                GitCommandResult(True, "new_file.py\ntemp.txt\n", "", 0),  # has untracked files
            ]
            
            result = self.git_integration.has_uncommitted_changes(self.mock_repo_path)
            self.assertTrue(result, "Must detect untracked files")
            
            # Test Case 4: Clean repository
            mock_git.side_effect = [
                GitCommandResult(True, "", "", 0),   # no staged changes
                GitCommandResult(True, "", "", 0),   # no unstaged changes
                GitCommandResult(True, "", "", 0),   # no untracked files
            ]
            
            result = self.git_integration.has_uncommitted_changes(self.mock_repo_path)
            self.assertFalse(result, "Must correctly identify clean repository")
            
            # Test Case 5: Repository status with uncommitted changes
            mock_git.side_effect = [
                GitCommandResult(True, "feature/development", "", 0),  # current branch
                GitCommandResult(False, "", "", 1),  # has staged changes
                GitCommandResult(True, "", "", 0),   # no unstaged changes
                GitCommandResult(True, "", "", 0),   # no untracked files
                GitCommandResult(True, "b2c3d4e5", "", 0),  # last commit
                GitCommandResult(True, "https://github.com/control-tower/test.git", "", 0)  # remote
            ]
            
            status = self.git_integration.check_repository_status(self.mock_repo_path)
            self.assertEqual(status.status, RepositoryStatus.UNCOMMITTED_CHANGES, "Must report uncommitted changes in status")
            self.assertTrue(status.has_uncommitted, "Must set has_uncommitted flag")
            
            print("✅ IL-002: Uncommitted changes detection PASSED")
    
    def test_IL_003_handles_non_git_directories_gracefully(self):
        """
        Validation Test: IL-003 - Handles non-git directories gracefully
        
        Requirements:
        - Must correctly identify non-git directories
        - Must handle invalid paths without crashing
        - Must return appropriate status for non-git directories
        - Must not attempt git operations on non-git directories
        """
        # Test Case 1: Regular directory (not git repository)
        result = self.git_integration.check_repository_status(self.non_git_path)
        
        self.assertIsInstance(result, GitRepositoryInfo, "Must return GitRepositoryInfo for non-git directory")
        self.assertFalse(result.is_git_repo, "Must correctly identify non-git directory")
        self.assertEqual(result.status, RepositoryStatus.NOT_GIT_REPOSITORY, "Must set appropriate status")
        self.assertIsNone(result.current_branch, "Must not have branch for non-git directory")
        self.assertFalse(result.has_uncommitted, "Must not report uncommitted changes for non-git directory")
        self.assertEqual(result.path, self.non_git_path, "Must preserve directory path")
        
        # Test Case 2: Invalid/non-existent path
        result = self.git_integration.check_repository_status(self.invalid_path)
        
        self.assertFalse(result.is_git_repo, "Must handle invalid path gracefully")
        self.assertEqual(result.status, RepositoryStatus.ERROR, "Must report error status for invalid path")
        self.assertIsNotNone(result.error_message, "Must provide error message for invalid path")
        self.assertIn("does not exist", result.error_message, "Must indicate path does not exist")
        
        # Test Case 3: is_git_repository method with non-git directory
        is_git = self.git_integration.is_git_repository(self.non_git_path)
        self.assertFalse(is_git, "is_git_repository must return False for non-git directory")
        
        # Test Case 4: is_git_repository method with invalid path
        is_git = self.git_integration.is_git_repository(self.invalid_path)
        self.assertFalse(is_git, "is_git_repository must return False for invalid path")
        
        # Test Case 5: has_uncommitted_changes with non-git directory
        has_changes = self.git_integration.has_uncommitted_changes(self.non_git_path)
        self.assertFalse(has_changes, "has_uncommitted_changes must return False for non-git directory")
        
        # Test Case 6: get_current_branch with non-git directory
        branch = self.git_integration.get_current_branch(self.non_git_path)
        self.assertIsNone(branch, "get_current_branch must return None for non-git directory")
        
        print("✅ IL-003: Non-git directory handling PASSED")
    
    def test_IL_004_provides_repository_connectivity_status(self):
        """
        Validation Test: IL-004 - Provides repository connectivity status
        
        Requirements:
        - Must check for remote repository configuration
        - Must test remote connectivity safely
        - Must determine sync status with remote
        - Must handle connectivity failures gracefully
        - Must not modify repository state during connectivity checks
        """
        with patch.object(self.git_integration, '_run_git_command') as mock_git:
            # Test Case 1: Repository with reachable remote
            mock_git.side_effect = [
                GitCommandResult(True, "https://github.com/control-tower/test.git", "", 0),  # remote url
                GitCommandResult(True, "refs/heads/main", "", 0),  # ls-remote (reachable)
                GitCommandResult(True, "main", "", 0),  # get current branch for sync check
                GitCommandResult(True, "0\t2", "", 0),  # rev-list --count (ahead=0, behind=2)
            ]
            
            connectivity = self.git_integration.get_repository_connectivity_status(self.mock_repo_path)
            
            self.assertIsInstance(connectivity, dict, "Must return dictionary")
            self.assertTrue(connectivity['has_remote'], "Must detect remote configuration")
            self.assertTrue(connectivity['remote_reachable'], "Must detect reachable remote")
            self.assertEqual(connectivity['remote_url'], "https://github.com/control-tower/test.git", "Must provide remote URL")
            self.assertTrue(connectivity['behind_remote'], "Must detect behind status")
            self.assertFalse(connectivity['ahead_remote'], "Must correctly report not ahead")
            self.assertIsNone(connectivity.get('error'), "Must not have error for successful check")
            
            # Test Case 2: Repository with unreachable remote
            mock_git.side_effect = [
                GitCommandResult(True, "https://github.com/private/unreachable.git", "", 0),  # remote url
                GitCommandResult(False, "", "fatal: unable to access", 128),  # ls-remote fails
            ]
            
            connectivity = self.git_integration.get_repository_connectivity_status(self.mock_repo_path)
            
            self.assertTrue(connectivity['has_remote'], "Must detect remote configuration even if unreachable")
            self.assertFalse(connectivity['remote_reachable'], "Must detect unreachable remote")
            self.assertEqual(connectivity['remote_url'], "https://github.com/private/unreachable.git", "Must provide remote URL even if unreachable")
            
            # Test Case 3: Repository without remote
            mock_git.side_effect = [
                GitCommandResult(False, "", "fatal: No such remote 'origin'", 128),  # no remote
            ]
            
            connectivity = self.git_integration.get_repository_connectivity_status(self.mock_repo_path)
            
            self.assertFalse(connectivity['has_remote'], "Must detect absence of remote")
            self.assertFalse(connectivity['remote_reachable'], "Must report not reachable when no remote")
            self.assertIsNone(connectivity['remote_url'], "Must not provide URL when no remote")
            
            # Test Case 4: Repository ahead of remote
            mock_git.side_effect = [
                GitCommandResult(True, "https://github.com/control-tower/test.git", "", 0),  # remote url
                GitCommandResult(True, "refs/heads/main", "", 0),  # ls-remote (reachable)
                GitCommandResult(True, "main", "", 0),  # get current branch for sync check
                GitCommandResult(True, "3\t0", "", 0),  # rev-list --count (ahead=3, behind=0)
            ]
            
            connectivity = self.git_integration.get_repository_connectivity_status(self.mock_repo_path)
            
            self.assertFalse(connectivity['behind_remote'], "Must correctly report not behind")
            self.assertTrue(connectivity['ahead_remote'], "Must detect ahead status")
            
            # Test Case 5: Non-git directory connectivity check
            connectivity = self.git_integration.get_repository_connectivity_status(self.non_git_path)
            
            self.assertIn('error', connectivity, "Must report error for non-git directory")
            self.assertEqual(connectivity['error'], 'Not a git repository', "Must provide specific error message")
            
            print("✅ IL-004: Repository connectivity status PASSED")
    
    def test_integration_git_operations_error_handling(self):
        """
        Integration Test: Complete error handling validation
        
        Requirements:
        - Must handle git command timeouts gracefully
        - Must handle subprocess errors without crashing
        - Must provide meaningful error messages
        - Must maintain system stability under error conditions
        """
        # Test git command timeout handling
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.side_effect = subprocess.TimeoutExpired(['git', 'status'], 5)
            
            result = self.git_integration._run_git_command(['status'], cwd=self.mock_repo_path, timeout=1)
            
            self.assertFalse(result.success, "Must report failure for timeout")
            self.assertIn("timed out", result.stderr, "Must provide timeout error message")
            self.assertEqual(result.return_code, -1, "Must use consistent error return code")
        
        # Test subprocess error handling
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.side_effect = OSError("Git command not found")
            
            result = self.git_integration._run_git_command(['status'], cwd=self.mock_repo_path)
            
            self.assertFalse(result.success, "Must report failure for subprocess error")
            self.assertIn("Git command not found", result.stderr, "Must preserve original error message")
            self.assertEqual(result.return_code, -1, "Must use consistent error return code")
        
        # Test repository status with git command failure
        with patch.object(self.git_integration, 'get_current_branch') as mock_branch:
            mock_branch.side_effect = Exception("Simulated git failure")
            
            result = self.git_integration.check_repository_status(self.mock_repo_path)
            
            self.assertEqual(result.status, RepositoryStatus.ERROR, "Must report error status for git failures")
            self.assertIsNotNone(result.error_message, "Must provide error message")
            self.assertIn("Simulated git failure", result.error_message, "Must include original error")
        
        print("✅ Error handling validation PASSED")
    
    def test_integration_complete_tr_il_001_workflow(self):
        """
        Integration Test: Complete TR-IL-001 workflow validation
        
        This test validates the complete git integration workflow covering
        all acceptance criteria IL-001 through IL-004 in a realistic scenario.
        """
        # Test 1: Repository identification (IL-001, IL-003)
        self.assertTrue(self.git_integration.is_git_repository(self.mock_repo_path))
        
        # Test non-git directory
        with patch.object(self.git_integration, '_run_git_command') as mock_git_check:
            mock_git_check.return_value = GitCommandResult(False, "", "fatal: not a git repository", 128)
            self.assertFalse(self.git_integration.is_git_repository(self.non_git_path))
        
        # Test 2: Repository status check (IL-001, IL-002)
        with patch.object(self.git_integration, '_run_git_command') as mock_git:
            mock_git.side_effect = [
                GitCommandResult(True, "feature/tr-il-001-implementation", "", 0),  # current branch
                GitCommandResult(False, "", "", 1),  # has staged changes
                GitCommandResult(True, "", "", 0),   # no unstaged changes
                GitCommandResult(True, "new_test.py\n", "", 0),  # has untracked files
                GitCommandResult(True, "f1a2b3c4", "", 0),  # last commit
                GitCommandResult(True, "https://github.com/control-tower/main.git", "", 0),  # remote
            ]
            
            status = self.git_integration.check_repository_status(self.mock_repo_path)
            self.assertTrue(status.is_git_repo)
            self.assertEqual(status.current_branch, "feature/tr-il-001-implementation")
            self.assertEqual(status.status, RepositoryStatus.UNCOMMITTED_CHANGES)
            self.assertTrue(status.has_uncommitted)
        
        # Test 3: Uncommitted changes detection (IL-002)
        with patch.object(self.git_integration, '_run_git_command') as mock_git:
            mock_git.side_effect = [
                GitCommandResult(False, "", "", 1),  # has staged changes
                GitCommandResult(True, "", "", 0),   # no unstaged changes
                GitCommandResult(True, "new_test.py\n", "", 0),  # has untracked files
            ]
            
            has_changes = self.git_integration.has_uncommitted_changes(self.mock_repo_path)
            self.assertTrue(has_changes)
        
        # Test 4: Connectivity status (IL-004)
        with patch.object(self.git_integration, '_run_git_command') as mock_git:
            mock_git.side_effect = [
                GitCommandResult(True, "https://github.com/control-tower/main.git", "", 0),  # remote url
                GitCommandResult(True, "refs/heads/main\nrefs/heads/feature/tr-il-001", "", 0),  # ls-remote
                GitCommandResult(True, "feature/tr-il-001-implementation", "", 0),  # get current branch
                GitCommandResult(True, "2\t1", "", 0),  # rev-list --count (ahead 2, behind 1)
            ]
            
            connectivity = self.git_integration.get_repository_connectivity_status(self.mock_repo_path)
            self.assertTrue(connectivity['has_remote'])
            self.assertTrue(connectivity['remote_reachable'])
            self.assertTrue(connectivity['ahead_remote'])
            self.assertTrue(connectivity['behind_remote'])
        
        # Validate all data is consistent and complete
        self.assertIsNone(connectivity.get('error'))
        
        print("✅ Complete TR-IL-001 workflow validation PASSED")
        print("🎯 All TR-IL-001 acceptance criteria (IL-001 through IL-004) validated successfully")


if __name__ == '__main__':
    # Run validation tests with detailed output
    unittest.main(verbosity=2)