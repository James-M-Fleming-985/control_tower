#!/usr/bin/env python3
"""
Git Safety Manager - Integration Layer Implementation for Phase 2D

Implements TR-IL-003: Git Safety & Automation requirements.
Provides comprehensive git safety and automation for TDD workflow execution.

This component ensures:
- Safe repository state before starting work
- Automated branch management and safety checkpoints
- Structured commit messages with workflow traceability
- Recovery mechanisms for failed operations
"""

import os
import subprocess
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from enum import Enum

# Import Phase 2B models for workflow integration
from src.business_logic.work_item_model import WorkItem


class GitState(Enum):
    """Git repository states"""
    CLEAN = "clean"
    DIRTY = "dirty" 
    MERGE_CONFLICT = "merge_conflict"
    DETACHED_HEAD = "detached_head"
    UNKNOWN = "unknown"


class BranchType(Enum):
    """Branch types for workflow management"""
    SAFETY = "safety"
    FEATURE = "feature"
    HOTFIX = "hotfix"
    EXPERIMENT = "experiment"


@dataclass
class GitSafetyCheckpoint:
    """Git safety checkpoint information"""
    checkpoint_id: str
    branch_name: str
    commit_hash: str
    created_at: datetime
    work_item_id: str
    original_branch: str
    checkpoint_message: str
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now()


@dataclass
class BranchInfo:
    """Git branch information"""
    name: str
    branch_type: BranchType
    work_item_id: str
    created_at: datetime
    tracking_remote: Optional[str] = None
    parent_branch: str = "main"
    description: str = ""


@dataclass
class CommitInfo:
    """Structured commit information"""
    commit_type: str  # feat, fix, refactor, test, docs, etc.
    scope: str        # work item ID or component
    description: str  # brief description
    body: str = ""    # detailed description
    breaking_change: bool = False
    work_item_id: str = ""
    workflow_stage: str = ""  # RED, GREEN, REFACTOR, VALIDATION, etc.
    
    def generate_message(self) -> str:
        """Generate conventional commit message"""
        # Header: type(scope): description
        header = f"{self.commit_type}"
        if self.scope:
            header += f"({self.scope})"
        if self.breaking_change:
            header += "!"
        header += f": {self.description}"
        
        # Body with workflow context
        body_parts = []
        if self.body:
            body_parts.append(self.body)
        
        if self.work_item_id:
            body_parts.append(f"Work Item: {self.work_item_id}")
            
        if self.workflow_stage:
            body_parts.append(f"TDD Stage: {self.workflow_stage}")
        
        # Combine header and body
        if body_parts:
            return f"{header}\n\n" + "\n".join(body_parts)
        else:
            return header


@dataclass
class GitOperationResult:
    """Result of git operation"""
    success: bool
    message: str
    operation: str
    details: Dict[str, Any] = None
    recovery_suggestions: List[str] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}
        if self.recovery_suggestions is None:
            self.recovery_suggestions = []


class GitSafetyManager:
    """
    Git Safety Manager - Ensures safe TDD workflow execution
    
    Provides comprehensive git safety and automation including:
    - Repository state validation and safety checkpoints
    - Automated branch management with naming conventions
    - Structured commit messages with workflow traceability
    - Recovery mechanisms for failed operations
    
    Implements TR-IL-003: Git Safety & Automation requirements.
    """
    
    def __init__(self, repository_path: Optional[str] = None):
        """
        Initialize Git Safety Manager
        
        Args:
            repository_path: Path to git repository (defaults to current directory)
        """
        self.repository_path = Path(repository_path) if repository_path else Path.cwd()
        self.safety_checkpoints: List[GitSafetyCheckpoint] = []
        self.active_branches: Dict[str, BranchInfo] = {}
        
        # Validate repository
        if not self._is_git_repository():
            raise ValueError(f"Not a git repository: {self.repository_path}")
    
    def _is_git_repository(self) -> bool:
        """Check if current directory is a git repository"""
        git_dir = self.repository_path / ".git"
        return git_dir.exists()
    
    def _run_git_command(self, command: List[str], capture_output: bool = True) -> Tuple[bool, str]:
        """
        Run git command safely
        
        Args:
            command: Git command arguments
            capture_output: Whether to capture command output
            
        Returns:
            Tuple of (success, output/error_message)
        """
        try:
            full_command = ["git"] + command
            result = subprocess.run(
                full_command,
                cwd=self.repository_path,
                capture_output=capture_output,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            if result.returncode == 0:
                return True, result.stdout.strip() if capture_output else "Success"
            else:
                return False, result.stderr.strip() if capture_output else "Failed"
                
        except subprocess.TimeoutExpired:
            return False, "Git command timed out"
        except Exception as e:
            return False, f"Git command failed: {str(e)}"
    
    def get_repository_state(self) -> GitState:
        """
        Get current repository state
        
        Returns:
            Current git repository state
        """
        # Check for detached HEAD
        success, output = self._run_git_command(["symbolic-ref", "-q", "HEAD"])
        if not success:
            return GitState.DETACHED_HEAD
        
        # Check for merge conflicts
        success, output = self._run_git_command(["status", "--porcelain"])
        if not success:
            return GitState.UNKNOWN
            
        # Check for conflicts (UU status)
        if "UU " in output:
            return GitState.MERGE_CONFLICT
        
        # Check for uncommitted changes
        if output.strip():
            return GitState.DIRTY
        
        return GitState.CLEAN
    
    def get_current_branch(self) -> Optional[str]:
        """Get current branch name"""
        success, output = self._run_git_command(["branch", "--show-current"])
        return output if success else None
    
    def validate_repository_safety(self) -> GitOperationResult:
        """
        Validate repository is in safe state for workflow
        
        Returns:
            Validation result with safety status
        """
        issues = []
        suggestions = []
        
        # Check repository state
        state = self.get_repository_state()
        
        if state == GitState.DETACHED_HEAD:
            issues.append("Repository is in detached HEAD state")
            suggestions.append("Checkout a branch: git checkout main")
        
        elif state == GitState.MERGE_CONFLICT:
            issues.append("Repository has unresolved merge conflicts")
            suggestions.append("Resolve conflicts and complete merge")
        
        elif state == GitState.DIRTY:
            issues.append("Repository has uncommitted changes")
            suggestions.append("Commit or stash changes before starting workflow")
        
        elif state == GitState.UNKNOWN:
            issues.append("Unable to determine repository state")
            suggestions.append("Check git status manually")
        
        # Check for valid branch
        current_branch = self.get_current_branch()
        if not current_branch:
            issues.append("Unable to determine current branch")
            suggestions.append("Ensure repository is in valid state")
        
        # Success if no issues
        if not issues:
            return GitOperationResult(
                success=True,
                message="Repository is safe for workflow execution",
                operation="validate_safety",
                details={"state": state.value, "branch": current_branch}
            )
        else:
            return GitOperationResult(
                success=False,
                message=f"Repository safety validation failed: {'; '.join(issues)}",
                operation="validate_safety",
                details={"state": state.value, "branch": current_branch, "issues": issues},
                recovery_suggestions=suggestions
            )
    
    def create_safety_checkpoint(self, work_item: WorkItem) -> GitOperationResult:
        """
        Create safety checkpoint before starting work
        
        Args:
            work_item: Work item being processed
            
        Returns:
            Safety checkpoint creation result
        """
        # Validate repository safety first
        safety_check = self.validate_repository_safety()
        if not safety_check.success:
            return GitOperationResult(
                success=False,
                message="Cannot create checkpoint: repository not safe",
                operation="create_checkpoint",
                details=safety_check.details,
                recovery_suggestions=safety_check.recovery_suggestions
            )
        
        current_branch = self.get_current_branch()
        if not current_branch:
            return GitOperationResult(
                success=False,
                message="Cannot determine current branch for checkpoint",
                operation="create_checkpoint",
                recovery_suggestions=["Check git status and ensure valid branch"]
            )
        
        # Generate checkpoint branch name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_branch = f"safety/{work_item.id}-{timestamp}"
        
        # Create safety branch
        success, output = self._run_git_command(["checkout", "-b", checkpoint_branch])
        if not success:
            return GitOperationResult(
                success=False,
                message=f"Failed to create safety branch: {output}",
                operation="create_checkpoint",
                recovery_suggestions=["Check branch name validity", "Ensure clean repository state"]
            )
        
        # Get current commit hash
        success, commit_hash = self._run_git_command(["rev-parse", "HEAD"])
        if not success:
            # Rollback: delete the branch we just created
            self._run_git_command(["checkout", current_branch])
            self._run_git_command(["branch", "-D", checkpoint_branch])
            
            return GitOperationResult(
                success=False,
                message="Failed to get current commit hash",
                operation="create_checkpoint",
                recovery_suggestions=["Check repository integrity"]
            )
        
        # Switch back to original branch
        success, output = self._run_git_command(["checkout", current_branch])
        if not success:
            return GitOperationResult(
                success=False,
                message=f"Failed to switch back to original branch: {output}",
                operation="create_checkpoint",
                recovery_suggestions=[f"Manually checkout {current_branch}", "Check branch status"]
            )
        
        # Create checkpoint record
        checkpoint = GitSafetyCheckpoint(
            checkpoint_id=f"{work_item.id}-{timestamp}",
            branch_name=checkpoint_branch,
            commit_hash=commit_hash,
            created_at=datetime.now(),
            work_item_id=work_item.id,
            original_branch=current_branch,
            checkpoint_message=f"Safety checkpoint for {work_item.title}"
        )
        
        self.safety_checkpoints.append(checkpoint)
        
        return GitOperationResult(
            success=True,
            message=f"Safety checkpoint created: {checkpoint_branch}",
            operation="create_checkpoint",
            details={
                "checkpoint_id": checkpoint.checkpoint_id,
                "branch": checkpoint_branch,
                "commit_hash": commit_hash,
                "original_branch": current_branch
            }
        )
    
    def create_feature_branch(self, work_item: WorkItem) -> GitOperationResult:
        """
        Create feature branch for work item
        
        Args:
            work_item: Work item being processed
            
        Returns:
            Feature branch creation result
        """
        # Generate feature branch name
        # Format: feature/<work-item-id>-<descriptive-name>
        safe_title = re.sub(r'[^a-zA-Z0-9-]', '-', work_item.title.lower())
        safe_title = re.sub(r'-+', '-', safe_title).strip('-')[:50]  # Limit length
        feature_branch = f"feature/{work_item.id}-{safe_title}"
        
        # Ensure we're on the correct parent branch (usually main)
        current_branch = self.get_current_branch()
        parent_branch = "main"  # Could be configurable
        
        if current_branch != parent_branch:
            # Switch to parent branch
            success, output = self._run_git_command(["checkout", parent_branch])
            if not success:
                return GitOperationResult(
                    success=False,
                    message=f"Failed to checkout parent branch {parent_branch}: {output}",
                    operation="create_feature_branch",
                    recovery_suggestions=[f"Manually checkout {parent_branch}", "Check branch exists"]
                )
        
        # Pull latest changes from remote
        success, output = self._run_git_command(["pull", "origin", parent_branch])
        # Note: We don't fail if pull fails (might be offline), just warn
        
        # Create feature branch
        success, output = self._run_git_command(["checkout", "-b", feature_branch])
        if not success:
            return GitOperationResult(
                success=False,
                message=f"Failed to create feature branch: {output}",
                operation="create_feature_branch",
                recovery_suggestions=["Check branch name validity", "Ensure clean repository"]
            )
        
        # Set up remote tracking (if remote exists)
        success, output = self._run_git_command(["push", "-u", "origin", feature_branch])
        remote_tracking = success
        
        # Create branch info record
        branch_info = BranchInfo(
            name=feature_branch,
            branch_type=BranchType.FEATURE,
            work_item_id=work_item.id,
            created_at=datetime.now(),
            tracking_remote="origin" if remote_tracking else None,
            parent_branch=parent_branch,
            description=work_item.title
        )
        
        self.active_branches[feature_branch] = branch_info
        
        return GitOperationResult(
            success=True,
            message=f"Feature branch created: {feature_branch}",
            operation="create_feature_branch",
            details={
                "branch_name": feature_branch,
                "parent_branch": parent_branch,
                "remote_tracking": remote_tracking,
                "work_item_id": work_item.id
            }
        )
    
    def commit_workflow_stage(self, 
                             work_item: WorkItem, 
                             stage: str,
                             description: str,
                             files_changed: List[str] = None) -> GitOperationResult:
        """
        Commit workflow stage with structured message
        
        Args:
            work_item: Work item being processed
            stage: Workflow stage (RED, GREEN, REFACTOR, etc.)
            description: Commit description
            files_changed: List of files to commit (None for all)
            
        Returns:
            Commit operation result
        """
        # Stage files
        if files_changed:
            for file_path in files_changed:
                success, output = self._run_git_command(["add", file_path])
                if not success:
                    return GitOperationResult(
                        success=False,
                        message=f"Failed to stage file {file_path}: {output}",
                        operation="commit_stage",
                        recovery_suggestions=["Check file exists", "Verify file permissions"]
                    )
        else:
            # Stage all changes
            success, output = self._run_git_command(["add", "."])
            if not success:
                return GitOperationResult(
                    success=False,
                    message=f"Failed to stage changes: {output}",
                    operation="commit_stage",
                    recovery_suggestions=["Check repository state", "Verify file permissions"]
                )
        
        # Check if there are staged changes
        success, output = self._run_git_command(["diff", "--cached", "--name-only"])
        if not success or not output.strip():
            return GitOperationResult(
                success=False,
                message="No staged changes to commit",
                operation="commit_stage",
                recovery_suggestions=["Make changes before committing", "Check file modifications"]
            )
        
        # Create structured commit message
        commit_info = CommitInfo(
            commit_type="feat" if stage == "GREEN" else "refactor" if stage == "REFACTOR" else "test",
            scope=work_item.id,
            description=description,
            body=f"TDD workflow stage: {stage}",
            work_item_id=work_item.id,
            workflow_stage=stage
        )
        
        commit_message = commit_info.generate_message()
        
        # Commit changes
        success, output = self._run_git_command(["commit", "-m", commit_message])
        if not success:
            return GitOperationResult(
                success=False,
                message=f"Failed to commit changes: {output}",
                operation="commit_stage",
                recovery_suggestions=["Check commit message format", "Verify staged changes"]
            )
        
        # Get commit hash
        success, commit_hash = self._run_git_command(["rev-parse", "HEAD"])
        
        return GitOperationResult(
            success=True,
            message=f"Committed {stage} stage: {commit_hash[:8] if success else 'unknown'}",
            operation="commit_stage",
            details={
                "stage": stage,
                "commit_hash": commit_hash if success else None,
                "commit_message": commit_message,
                "files_staged": output.split('\n') if output else []
            }
        )
    
    def recover_from_checkpoint(self, checkpoint_id: str) -> GitOperationResult:
        """
        Recover repository state from safety checkpoint
        
        Args:
            checkpoint_id: Checkpoint identifier to recover from
            
        Returns:
            Recovery operation result
        """
        # Find checkpoint
        checkpoint = None
        for cp in self.safety_checkpoints:
            if cp.checkpoint_id == checkpoint_id:
                checkpoint = cp
                break
        
        if not checkpoint:
            return GitOperationResult(
                success=False,
                message=f"Safety checkpoint not found: {checkpoint_id}",
                operation="recover_checkpoint",
                recovery_suggestions=["List available checkpoints", "Verify checkpoint ID"]
            )
        
        # Checkout original branch
        success, output = self._run_git_command(["checkout", checkpoint.original_branch])
        if not success:
            return GitOperationResult(
                success=False,
                message=f"Failed to checkout original branch {checkpoint.original_branch}: {output}",
                operation="recover_checkpoint",
                recovery_suggestions=["Check branch exists", "Resolve any conflicts"]
            )
        
        # Reset to checkpoint commit
        success, output = self._run_git_command(["reset", "--hard", checkpoint.commit_hash])
        if not success:
            return GitOperationResult(
                success=False,
                message=f"Failed to reset to checkpoint: {output}",
                operation="recover_checkpoint",
                recovery_suggestions=["Check commit hash validity", "Verify repository integrity"]
            )
        
        return GitOperationResult(
            success=True,
            message=f"Repository recovered to checkpoint {checkpoint_id}",
            operation="recover_checkpoint",
            details={
                "checkpoint_id": checkpoint_id,
                "original_branch": checkpoint.original_branch,
                "commit_hash": checkpoint.commit_hash,
                "recovered_at": datetime.now().isoformat()
            }
        )
    
    def cleanup_workflow_branches(self, work_item_id: str) -> GitOperationResult:
        """
        Clean up branches created for workflow
        
        Args:
            work_item_id: Work item ID to clean up branches for
            
        Returns:
            Cleanup operation result
        """
        cleaned_branches = []
        errors = []
        
        # Find branches related to work item
        branches_to_clean = []
        for branch_name, branch_info in self.active_branches.items():
            if branch_info.work_item_id == work_item_id:
                branches_to_clean.append(branch_name)
        
        # Also check safety checkpoints
        for checkpoint in self.safety_checkpoints:
            if checkpoint.work_item_id == work_item_id:
                branches_to_clean.append(checkpoint.branch_name)
        
        if not branches_to_clean:
            return GitOperationResult(
                success=True,
                message=f"No branches found for work item {work_item_id}",
                operation="cleanup_branches",
                details={"cleaned_branches": []}
            )
        
        # Switch to main branch before cleanup
        current_branch = self.get_current_branch()
        if current_branch in branches_to_clean:
            success, output = self._run_git_command(["checkout", "main"])
            if not success:
                errors.append(f"Failed to checkout main branch: {output}")
        
        # Delete branches
        for branch_name in branches_to_clean:
            # Delete local branch
            success, output = self._run_git_command(["branch", "-D", branch_name])
            if success:
                cleaned_branches.append(branch_name)
                # Remove from active branches
                if branch_name in self.active_branches:
                    del self.active_branches[branch_name]
            else:
                errors.append(f"Failed to delete branch {branch_name}: {output}")
        
        # Remove from checkpoints
        self.safety_checkpoints = [
            cp for cp in self.safety_checkpoints 
            if cp.work_item_id != work_item_id
        ]
        
        if errors:
            return GitOperationResult(
                success=False,
                message=f"Cleanup completed with errors: {'; '.join(errors)}",
                operation="cleanup_branches",
                details={"cleaned_branches": cleaned_branches, "errors": errors},
                recovery_suggestions=["Manually delete remaining branches", "Check branch status"]
            )
        else:
            return GitOperationResult(
                success=True,
                message=f"Cleaned up {len(cleaned_branches)} branches for {work_item_id}",
                operation="cleanup_branches",
                details={"cleaned_branches": cleaned_branches}
            )
    
    def get_workflow_status(self, work_item_id: str) -> Dict[str, Any]:
        """
        Get workflow status for work item
        
        Args:
            work_item_id: Work item to get status for
            
        Returns:
            Dictionary with workflow status information
        """
        status = {
            "work_item_id": work_item_id,
            "repository_state": self.get_repository_state().value,
            "current_branch": self.get_current_branch(),
            "safety_checkpoints": [],
            "active_branches": [],
            "commits": []
        }
        
        # Find related checkpoints
        for checkpoint in self.safety_checkpoints:
            if checkpoint.work_item_id == work_item_id:
                status["safety_checkpoints"].append({
                    "id": checkpoint.checkpoint_id,
                    "branch": checkpoint.branch_name,
                    "created_at": checkpoint.created_at.isoformat(),
                    "commit_hash": checkpoint.commit_hash
                })
        
        # Find related branches  
        for branch_name, branch_info in self.active_branches.items():
            if branch_info.work_item_id == work_item_id:
                status["active_branches"].append({
                    "name": branch_name,
                    "type": branch_info.branch_type.value,
                    "created_at": branch_info.created_at.isoformat(),
                    "tracking_remote": branch_info.tracking_remote
                })
        
        return status