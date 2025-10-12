```python
import json
import os
import hashlib
from typing import Any, Dict, Optional
from datetime import datetime
from pathlib import Path


class WorkflowStateManager:
    """Manages workflow state persistence and restoration."""
    
    def __init__(self, state_dir: str = ".workflow_states"):
        """
        Initialize the workflow state manager.
        
        Args:
            state_dir: Directory to store workflow state files
        """
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(exist_ok=True)
    
    def _get_state_path(self, workflow_id: str) -> Path:
        """Get the file path for a workflow state."""
        return self.state_dir / f"{workflow_id}.json"
    
    def _compute_checksum(self, data: Dict[str, Any]) -> str:
        """Compute checksum for state data integrity validation."""
        state_copy = data.copy()
        state_copy.pop('checksum', None)
        state_copy.pop('timestamp', None)
        json_str = json.dumps(state_copy, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def persist_state(self, workflow_id: str, stage: str, state_data: Dict[str, Any]) -> None:
        """
        Persist workflow state at stage completion.
        
        Args:
            workflow_id: Unique identifier for the workflow
            stage: Current stage name
            state_data: State data to persist
        """
        state = {
            'workflow_id': workflow_id,
            'stage': stage,
            'state_data': state_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        state['checksum'] = self._compute_checksum(state)
        
        state_path = self._get_state_path(workflow_id)
        with open(state_path, 'w') as f:
            json.dump(state, f, indent=2)
    
    def validate_state(self, state: Dict[str, Any]) -> bool:
        """
        Validate state integrity before restoration.
        
        Args:
            state: State dictionary to validate
            
        Returns:
            True if state is valid, False otherwise
        """
        if not state:
            return False
        
        required_fields = ['workflow_id', 'stage', 'state_data', 'checksum']
        if not all(field in state for field in required_fields):
            return False
        
        stored_checksum = state.get('checksum')
        computed_checksum = self._compute_checksum(state)
        
        return stored_checksum == computed_checksum
    
    def restore_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Restore workflow state from last successful stage.
        
        Args:
            workflow_id: Unique identifier for the workflow
            
        Returns:
            Restored state dictionary or None if not found or invalid
        """
        state_path = self._get_state_path(workflow_id)
        
        if not state_path.exists():
            return None
        
        try:
            with open(state_path, 'r') as f:
                state = json.load(f)
            
            if not self.validate_state(state):
                return None
            
            return state
        except (json.JSONDecodeError, IOError):
            return None
    
    def get_state_for_response(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get workflow state for inclusion in JSON response.
        
        Args:
            workflow_id: Unique identifier for the workflow
            
        Returns:
            State dictionary formatted for JSON response
        """
        state = self.restore_state(workflow_id)
        
        if state is None:
            return {
                'workflow_id': workflow_id,
                'stage': None,
                'state_data': None,
                'status': 'not_found'
            }
        
        return {
            'workflow_id': state['workflow_id'],
            'stage': state['stage'],
            'state_data': state['state_data'],
            'timestamp': state.get('timestamp'),
            'status': 'restored'
        }
    
    def delete_state(self, workflow_id: str) -> bool:
        """
        Delete workflow state.
        
        Args:
            workflow_id: Unique identifier for the workflow
            
        Returns:
            True if deleted, False if not found
        """
        state_path = self._get_state_path(workflow_id)
        
        if state_path.exists():
            state_path.unlink()
            return True
        
        return False


class WorkflowExecutor:
    """Executes workflows with state persistence and restart capabilities."""
    
    def __init__(self, state_manager: Optional[WorkflowStateManager] = None):
        """
        Initialize the workflow executor.
        
        Args:
            state_manager: State manager instance (creates default if None)
        """
        self.state_manager = state_manager or WorkflowStateManager()
    
    def execute_stage(self, workflow_id: str, stage: str, stage_func: callable, 
                     state_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a workflow stage and persist state on completion.
        
        Args:
            workflow_id: Unique identifier for the workflow
            stage: Stage name
            stage_func: Function to execute for this stage
            state_data: Initial state data
            
        Returns:
            Result dictionary with stage output and state
        """
        current_state = state_data or {}
        
        try:
            result = stage_func(current_state)
            
            if isinstance(result, dict):
                current_state.update(result)
            
            self.state_manager.persist_state(workflow_id, stage, current_state)
            
            return {
                'success': True,
                'stage': stage,
                'state': current_state
            }
        except Exception as e:
            return {
                'success': False,
                'stage': stage,
                'error': str(e),
                'state': current_state
            }
    
    def restart_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Restart workflow from last successful stage.
        
        Args:
            workflow_id: Unique identifier for the workflow
            
        Returns:
            Restored state or None if cannot restart
        """
        return self.state_manager.restore_state(workflow_id)
    
    def get_workflow_response(self, workflow_id: str) -> str:
        """
        Get workflow state as JSON response for actor.
        
        Args:
            workflow_id: Unique identifier for the workflow
            
        Returns:
            JSON string with workflow state
        """
        state_response = self.state_manager.get_state_for_response(workflow_id)
        return json.dumps(state_response, indent=2)


def create_workflow_state_manager(state_dir: str = ".workflow_states") -> WorkflowStateManager:
    """
    Factory function to create a workflow state manager.
    
    Args:
        state_dir: Directory to store workflow state files
        
    Returns:
        WorkflowStateManager instance
    """
    return WorkflowStateManager(state_dir)


def create_workflow_executor(state_manager: Optional[WorkflowStateManager] = None) -> WorkflowExecutor:
    """
    Factory function to create a workflow executor.
    
    Args:
        state_manager: Optional state manager instance
        
    Returns:
        WorkflowExecutor instance
    """
    return WorkflowExecutor(state_manager)
```