#!/usr/bin/env python3
"""
LAYER-003-01-03-001: Data Access Layer - Git Operations Manager
FEATURE-003-01-03: RED GREEN REFACTOR CYCLE ENFORCER

Provides git operations management for TDD cycle enforcement with
checkpoint creation, branch management, and state tracking.

B-Grade Requirements:
- 90%+ test coverage
- Performance: git operations <2000ms
- Error handling for all git operations
- Checkpoint management for TDD cycle phases
"""

import subprocess
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class GitCheckpointData:
    """Data structure for git checkpoint information"""
    
    def __init__(self, checkpoint_id: str, branch_name: str, commit_hash: str, phase: str):
        self.checkpoint_id = checkpoint_id
        self.branch_name = branch_name  
        self.commit_hash = commit_hash
        self.phase = phase  # RED, GREEN, REFACTOR
        self.timestamp = datetime.now().isoformat()

class GitOperationsManager:
    """
    Manages git operations for TDD cycle enforcement including
    checkpoint creation, branch management, and state tracking.
    """
    
    def __init__(self, repo_path: Optional[str] = None):
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self.checkpoints: Dict[str, GitCheckpointData] = {}
        self.current_feature_branch: Optional[str] = None
        
    def create_checkpoint(self, checkpoint_id: str, phase: str) -> bool:
        """
        Create a git checkpoint for TDD cycle phase.
        
        Args:
            checkpoint_id: Unique identifier for checkpoint
            phase: TDD phase (RED, GREEN, REFACTOR)
            
        Returns:
            bool: Success status
        """
        try:
            start_time = time.time()
            
            # Get current branch
            result = self._run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
            if not result:
                return False
                
            current_branch = result.strip()
            
            # Get current commit hash
            result = self._run_git_command(["git", "rev-parse", "HEAD"])
            if not result:
                return False
                
            commit_hash = result.strip()
            
            # Create checkpoint data
            checkpoint = GitCheckpointData(checkpoint_id, current_branch, commit_hash, phase)
            self.checkpoints[checkpoint_id] = checkpoint
            
            # Check performance requirement (<2000ms)
            elapsed = (time.time() - start_time) * 1000
            if elapsed > 2000:
                logger.warning(f"Checkpoint creation took {elapsed:.2f}ms (>2000ms)")
                
            logger.info(f"Created checkpoint {checkpoint_id} for {phase} phase")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create checkpoint {checkpoint_id}: {e}")
            return False
    
    def create_feature_branch(self, feature_name: str) -> bool:
        """
        Create a new feature branch for TDD cycle.
        
        Args:
            feature_name: Name of the feature branch
            
        Returns:
            bool: Success status
        """
        try:
            start_time = time.time()
            
            branch_name = f"feature/{feature_name}"
            
            # Create and checkout new branch
            if not self._run_git_command(["git", "checkout", "-b", branch_name]):
                return False
                
            self.current_feature_branch = branch_name
            
            # Check performance requirement
            elapsed = (time.time() - start_time) * 1000
            if elapsed > 2000:
                logger.warning(f"Branch creation took {elapsed:.2f}ms (>2000ms)")
                
            logger.info(f"Created feature branch: {branch_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create feature branch {feature_name}: {e}")
            return False
    
    def create_checkpoint_commit(self, checkpoint_id: str, message: str) -> bool:
        """
        Create a commit for a specific checkpoint.
        
        Args:
            checkpoint_id: Checkpoint identifier
            message: Commit message
            
        Returns:
            bool: Success status
        """
        try:
            start_time = time.time()
            
            # Stage all changes
            if not self._run_git_command(["git", "add", "."]):
                return False
            
            # Create commit
            commit_message = f"[{checkpoint_id}] {message}"
            if not self._run_git_command(["git", "commit", "-m", commit_message]):
                return False
            
            # Get new commit hash
            result = self._run_git_command(["git", "rev-parse", "HEAD"])
            if result and checkpoint_id in self.checkpoints:
                self.checkpoints[checkpoint_id].commit_hash = result.strip()
            
            # Check performance requirement
            elapsed = (time.time() - start_time) * 1000
            if elapsed > 2000:
                logger.warning(f"Checkpoint commit took {elapsed:.2f}ms (>2000ms)")
                
            logger.info(f"Created checkpoint commit for {checkpoint_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create checkpoint commit {checkpoint_id}: {e}")
            return False
    
    def get_git_status(self) -> Dict[str, Any]:
        """
        Get current git repository status.
        
        Returns:
            Dict containing git status information
        """
        try:
            # Get current branch
            branch_result = self._run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
            current_branch = branch_result.strip() if branch_result else "unknown"
            
            # Get commit hash
            hash_result = self._run_git_command(["git", "rev-parse", "HEAD"])
            commit_hash = hash_result.strip() if hash_result else "unknown"
            
            # Get status
            status_result = self._run_git_command(["git", "status", "--porcelain"])
            has_changes = bool(status_result and status_result.strip())
            
            return {
                "current_branch": current_branch,
                "commit_hash": commit_hash,
                "has_uncommitted_changes": has_changes,
                "feature_branch": self.current_feature_branch,
                "checkpoints_count": len(self.checkpoints)
            }
            
        except Exception as e:
            logger.error(f"Failed to get git status: {e}")
            return {"error": str(e)}
    
    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """
        List all created checkpoints.
        
        Returns:
            List of checkpoint information
        """
        checkpoints_list = []
        for checkpoint_id, checkpoint in self.checkpoints.items():
            checkpoints_list.append({
                "checkpoint_id": checkpoint.checkpoint_id,
                "branch_name": checkpoint.branch_name,
                "commit_hash": checkpoint.commit_hash,
                "phase": checkpoint.phase,
                "timestamp": checkpoint.timestamp
            })
        return checkpoints_list
    
    def _run_git_command(self, command: List[str]) -> Optional[str]:
        """
        Execute a git command safely.
        
        Args:
            command: Git command as list of strings
            
        Returns:
            Command output or None if failed
        """
        try:
            result = subprocess.run(
                command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                logger.error(f"Git command failed: {' '.join(command)}")
                logger.error(f"Error: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error(f"Git command timed out: {' '.join(command)}")
            return None
        except Exception as e:
            logger.error(f"Git command error: {e}")
            return None

if __name__ == "__main__":
    # Basic functionality test
    git_ops = GitOperationsManager()
    status = git_ops.get_git_status()
    print(f"Git Status: {json.dumps(status, indent=2)}")