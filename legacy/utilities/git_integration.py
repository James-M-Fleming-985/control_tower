"""
Git Integration Module for Control Tower Phase 1

This module implements TR-IL-001 Git Integration with safe git operations,
repository status checking, and comprehensive error handling.

Technical Requirements:
- TR-IL-001: Git Integration implementation
- Acceptance Criteria: IL-001 through IL-004 validation
- Safety: Read-only operations, no repository modifications
- Error Handling: Graceful handling of git errors and non-git directories

Author: Control Tower Development Team
Version: 1.0.0 (Phase 1 Integration Layer)
"""

import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class RepositoryStatus(Enum):
    """Git repository status enumeration."""
    CLEAN = "clean"
    UNCOMMITTED_CHANGES = "uncommitted_changes"
    NOT_GIT_REPOSITORY = "not_git_repository"
    ERROR = "error"


@dataclass
class GitRepositoryInfo:
    """
    Git repository information container.
    
    Attributes:
        path: Repository directory path
        is_git_repo: Whether directory is a git repository
        current_branch: Current git branch name
        has_uncommitted: Whether repository has uncommitted changes
        status: Overall repository status
        last_commit: Last commit hash (first 8 characters)
        remote_url: Remote origin URL if available
        error_message: Error message if status is ERROR
    """
    path: str
    is_git_repo: bool
    current_branch: Optional[str] = None
    has_uncommitted: bool = False
    status: RepositoryStatus = RepositoryStatus.NOT_GIT_REPOSITORY
    last_commit: Optional[str] = None
    remote_url: Optional[str] = None
    error_message: Optional[str] = None


class GitIntegration:
    """
    Git Integration service for safe repository operations.
    
    This class provides read-only git operations for repository status checking,
    branch information, and connectivity validation. All operations are designed
    to be safe and non-destructive.
    
    Acceptance Criteria Mapping:
    - IL-001: Validates git repository status
    - IL-002: Reports uncommitted changes safely
    - IL-003: Handles non-git directories gracefully
    - IL-004: Provides repository connectivity status
    
    Design Patterns:
    - Command Pattern: Git operations encapsulated as methods
    - Error Handling: Comprehensive exception handling with graceful degradation
    - Immutable Results: All operations return immutable data structures
    """
    
    def __init__(self):
        """Initialize Git Integration service."""
        self.logger = logging.getLogger(__name__)
        self._git_command_timeout = 10  # seconds
    
    def check_repository_status(self, repo_path: str) -> GitRepositoryInfo:
        """
        Check comprehensive git repository status.
        
        Args:
            repo_path: Path to repository directory
            
        Returns:
            GitRepositoryInfo with complete repository status
            
        Acceptance Criteria: IL-001, IL-002, IL-003, IL-004
        """
        try:
            repo_info = GitRepositoryInfo(path=repo_path, is_git_repo=False)
            
            # Step 1: Validate path exists
            if not self._validate_path(repo_path):
                repo_info.status = RepositoryStatus.ERROR
                repo_info.error_message = f"Repository path does not exist: {repo_path}"
                return repo_info
            
            # Step 2: Check if git repository
            if not self.is_git_repository(repo_path):
                repo_info.status = RepositoryStatus.NOT_GIT_REPOSITORY
                return repo_info
            
            # Step 3: Repository is git - gather information
            repo_info.is_git_repo = True
            
            # Try to gather git information - if critical operations fail, mark as error
            try:
                repo_info.current_branch = self.get_current_branch(repo_path)
                repo_info.has_uncommitted = self.has_uncommitted_changes(repo_path)
                repo_info.last_commit = self._get_last_commit_hash(repo_path)
                repo_info.remote_url = self._get_remote_url(repo_path)
                
                # Step 4: Determine overall status
                if repo_info.has_uncommitted:
                    repo_info.status = RepositoryStatus.UNCOMMITTED_CHANGES
                else:
                    repo_info.status = RepositoryStatus.CLEAN
                    
            except Exception as git_error:
                # If git operations fail critically, mark as error
                repo_info.status = RepositoryStatus.ERROR
                repo_info.error_message = f"Git operations failed: {git_error}"
            
            self.logger.info(f"Repository status checked: {repo_path} -> {repo_info.status.value}")
            return repo_info
            
        except Exception as e:
            self.logger.error(f"Error checking repository status for {repo_path}: {e}")
            return GitRepositoryInfo(
                path=repo_path,
                is_git_repo=False,
                status=RepositoryStatus.ERROR,
                error_message=str(e)
            )
    
    def is_git_repository(self, path: str) -> bool:
        """
        Check if directory is a git repository.
        
        Args:
            path: Directory path to check
            
        Returns:
            True if directory is a git repository, False otherwise
            
        Acceptance Criteria: IL-003
        """
        try:
            if not self._validate_path(path):
                return False
            
            git_dir = Path(path) / '.git'
            if git_dir.is_dir():
                # Standard git repository
                return True
            elif git_dir.is_file():
                # Git worktree or submodule
                return True
            else:
                # Check if we're in a git repository using git command
                result = self._run_git_command(['rev-parse', '--git-dir'], cwd=path)
                return result.success
                
        except Exception as e:
            self.logger.debug(f"Error checking if {path} is git repository: {e}")
            return False
    
    def get_current_branch(self, repo_path: str) -> Optional[str]:
        """
        Get current git branch name.
        
        Args:
            repo_path: Repository directory path
            
        Returns:
            Current branch name or None if error
            
        Acceptance Criteria: IL-001
        """
        try:
            if not self.is_git_repository(repo_path):
                return None
            
            # Try to get branch name from git
            result = self._run_git_command(['branch', '--show-current'], cwd=repo_path)
            if result.success and result.stdout.strip():
                return result.stdout.strip()
            
            # Fallback: try rev-parse for detached HEAD
            result = self._run_git_command(['rev-parse', '--abbrev-ref', 'HEAD'], cwd=repo_path)
            if result.success and result.stdout.strip():
                branch_name = result.stdout.strip()
                return branch_name if branch_name != 'HEAD' else 'detached HEAD'
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error getting current branch for {repo_path}: {e}")
            return None
    
    def has_uncommitted_changes(self, repo_path: str) -> bool:
        """
        Check if repository has uncommitted changes.
        
        Args:
            repo_path: Repository directory path
            
        Returns:
            True if there are uncommitted changes, False otherwise
            
        Acceptance Criteria: IL-002
        """
        try:
            if not self.is_git_repository(repo_path):
                return False
            
            # Check for staged changes
            result = self._run_git_command(['diff', '--cached', '--quiet'], cwd=repo_path)
            has_staged = not result.success  # diff --quiet returns 1 if differences exist
            
            # Check for unstaged changes
            result = self._run_git_command(['diff', '--quiet'], cwd=repo_path)
            has_unstaged = not result.success
            
            # Check for untracked files
            result = self._run_git_command(['ls-files', '--others', '--exclude-standard'], cwd=repo_path)
            has_untracked = result.success and bool(result.stdout.strip())
            
            return has_staged or has_unstaged or has_untracked
            
        except Exception as e:
            self.logger.warning(f"Error checking uncommitted changes for {repo_path}: {e}")
            return False
    
    def get_repository_connectivity_status(self, repo_path: str) -> Dict[str, Any]:
        """
        Get repository connectivity and remote status.
        
        Args:
            repo_path: Repository directory path
            
        Returns:
            Dictionary with connectivity information
            
        Acceptance Criteria: IL-004
        """
        try:
            status = {
                'has_remote': False,
                'remote_reachable': False,
                'behind_remote': False,
                'ahead_remote': False,
                'remote_url': None,
                'last_fetch': None,
                'error': None
            }
            
            if not self.is_git_repository(repo_path):
                status['error'] = 'Not a git repository'
                return status
            
            # Get remote URL
            remote_url = self._get_remote_url(repo_path)
            if remote_url:
                status['has_remote'] = True
                status['remote_url'] = remote_url
                
                # Test remote connectivity (with timeout)
                status['remote_reachable'] = self._test_remote_connectivity(repo_path)
                
                # Check if behind/ahead of remote (if reachable)
                if status['remote_reachable']:
                    behind, ahead = self._check_remote_sync_status(repo_path)
                    status['behind_remote'] = behind
                    status['ahead_remote'] = ahead
            
            return status
            
        except Exception as e:
            self.logger.warning(f"Error checking connectivity for {repo_path}: {e}")
            return {'error': str(e)}
    
    def _validate_path(self, path: str) -> bool:
        """Validate that path exists and is accessible."""
        try:
            path_obj = Path(path)
            return path_obj.exists() and path_obj.is_dir()
        except Exception:
            return False
    
    def _run_git_command(self, cmd: List[str], cwd: str, timeout: Optional[int] = None) -> 'GitCommandResult':
        """
        Run git command safely with timeout and error handling.
        
        Args:
            cmd: Git command arguments (without 'git')
            cwd: Working directory for command
            timeout: Command timeout in seconds
            
        Returns:
            GitCommandResult with success status and output
        """
        timeout = timeout or self._git_command_timeout
        full_cmd = ['git'] + cmd
        
        try:
            result = subprocess.run(
                full_cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False  # Don't raise exception on non-zero exit
            )
            
            return GitCommandResult(
                success=(result.returncode == 0),
                stdout=result.stdout,
                stderr=result.stderr,
                return_code=result.returncode
            )
            
        except subprocess.TimeoutExpired:
            self.logger.warning(f"Git command timed out: {' '.join(full_cmd)}")
            return GitCommandResult(
                success=False,
                stdout="",
                stderr=f"Command timed out after {timeout} seconds",
                return_code=-1
            )
        except Exception as e:
            self.logger.warning(f"Error running git command {' '.join(full_cmd)}: {e}")
            return GitCommandResult(
                success=False,
                stdout="",
                stderr=str(e),
                return_code=-1
            )
    
    def _get_last_commit_hash(self, repo_path: str) -> Optional[str]:
        """Get last commit hash (short form)."""
        try:
            result = self._run_git_command(['rev-parse', '--short', 'HEAD'], cwd=repo_path)
            return result.stdout.strip() if result.success else None
        except Exception:
            return None
    
    def _get_remote_url(self, repo_path: str) -> Optional[str]:
        """Get remote origin URL."""
        try:
            result = self._run_git_command(['remote', 'get-url', 'origin'], cwd=repo_path)
            return result.stdout.strip() if result.success else None
        except Exception:
            return None
    
    def _test_remote_connectivity(self, repo_path: str) -> bool:
        """Test if remote repository is reachable."""
        try:
            # Use ls-remote to test connectivity without fetching
            result = self._run_git_command(['ls-remote', '--exit-code', 'origin'], cwd=repo_path, timeout=5)
            return result.success
        except Exception:
            return False
    
    def _check_remote_sync_status(self, repo_path: str) -> tuple[bool, bool]:
        """Check if local branch is behind or ahead of remote."""
        try:
            # Get current branch
            branch = self.get_current_branch(repo_path)
            if not branch or branch == 'detached HEAD':
                return False, False
            
            # Check behind/ahead status using rev-list
            result = self._run_git_command(['rev-list', '--count', '--left-right', f'{branch}...origin/{branch}'], cwd=repo_path)
            if result.success and result.stdout.strip():
                parts = result.stdout.strip().split('\t')
                if len(parts) == 2:
                    ahead_count = int(parts[0])  # Local commits ahead of remote
                    behind_count = int(parts[1])  # Remote commits ahead of local
                    return behind_count > 0, ahead_count > 0  # (behind, ahead)
            
            return False, False
        except Exception:
            return False, False


@dataclass
class GitCommandResult:
    """Result of a git command execution."""
    success: bool
    stdout: str
    stderr: str
    return_code: int