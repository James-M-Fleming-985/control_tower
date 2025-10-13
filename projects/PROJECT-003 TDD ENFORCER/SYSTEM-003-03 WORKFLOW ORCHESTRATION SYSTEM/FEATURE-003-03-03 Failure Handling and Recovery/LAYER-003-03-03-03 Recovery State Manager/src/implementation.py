```python
import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path


class RecoveryStateManager:
    """Manages workflow state persistence and recovery."""
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the RecoveryStateManager.
        
        Args:
            storage_path: Path to store state files. Defaults to './workflow_states'
        """
        self.storage_path = Path(storage_path) if storage_path else Path('./workflow_states')
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._states: Dict[str, Dict[str, Any]] = {}
    
    def _get_state_file_path(self, workflow_id: str) -> Path:
        """Get the file path for a workflow state."""
        return self.storage_path / f"{workflow_id}.json"
    
    def persist_state(self, workflow_id: str, stage: str, state_data: Dict[str, Any]) -> bool:
        """
        Persist workflow state at stage completion.
        
        Args:
            workflow_id: Unique identifier for the workflow
            stage: Current stage name
            state_data: State data to persist
            
        Returns:
            bool: True if persistence was successful
        """
        try:
            if workflow_id not in self._states:
                self._states[workflow_id] = {
                    'workflow_id': workflow_id,
                    'stages': [],
                    'current_stage': stage,
                    'created_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat(),
                    'state_data': {}
                }
            
            workflow_state = self._states[workflow_id]
            
            # Add stage if not already in stages list
            if stage not in workflow_state['stages']:
                workflow_state['stages'].append(stage)
            
            workflow_state['current_stage'] = stage
            workflow_state['updated_at'] = datetime.utcnow().isoformat()
            workflow_state['state_data'][stage] = state_data
            
            # Write to file
            state_file = self._get_state_file_path(workflow_id)
            with open(state_file, 'w') as f:
                json.dump(workflow_state, f, indent=2)
            
            return True
        except Exception as e:
            return False
    
    def get_last_successful_stage(self, workflow_id: str) -> Optional[str]:
        """
        Get the last successful stage for a workflow.
        
        Args:
            workflow_id: Unique identifier for the workflow
            
        Returns:
            Optional[str]: Name of the last successful stage or None
        """
        workflow_state = self._load_state(workflow_id)
        if workflow_state and workflow_state.get('stages'):
            return workflow_state['stages'][-1]
        return None
    
    def _load_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Load workflow state from storage."""
        if workflow_id in self._states:
            return self._states[workflow_id]
        
        state_file = self._get_state_file_path(workflow_id)
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    self._states[workflow_id] = state
                    return state
            except Exception:
                return None
        return None
    
    def validate_state(self, workflow_id: str) -> bool:
        """
        Validate state integrity before restoration.
        
        Args:
            workflow_id: Unique identifier for the workflow
            
        Returns:
            bool: True if state is valid
        """
        workflow_state = self._load_state(workflow_id)
        
        if not workflow_state:
            return False
        
        # Check required fields
        required_fields = ['workflow_id', 'stages', 'current_stage', 'state_data']
        if not all(field in workflow_state for field in required_fields):
            return False
        
        # Validate workflow_id matches
        if workflow_state['workflow_id'] != workflow_id:
            return False
        
        # Validate stages is a list
        if not isinstance(workflow_state['stages'], list):
            return False
        
        # Validate current_stage is in stages
        if workflow_state['stages'] and workflow_state['current_stage'] not in workflow_state['stages']:
            return False
        
        # Validate state_data is a dict
        if not isinstance(workflow_state['state_data'], dict):
            return False
        
        # Validate each stage in stages has corresponding state_data
        for stage in workflow_state['stages']:
            if stage not in workflow_state['state_data']:
                return False
        
        return True
    
    def restore_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Restore workflow state from last successful stage.
        
        Args:
            workflow_id: Unique identifier for the workflow
            
        Returns:
            Optional[Dict[str, Any]]: Restored workflow state or None
        """
        if not self.validate_state(workflow_id):
            return None
        
        return self._load_state(workflow_id)
    
    def get_state_response(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get workflow state in JSON response format.
        
        Args:
            workflow_id: Unique identifier for the workflow
            
        Returns:
            Dict[str, Any]: Workflow state response
        """
        workflow_state = self._load_state(workflow_id)
        
        if not workflow_state:
            return {
                'workflow_id': workflow_id,
                'status': 'not_found',
                'state': None
            }
        
        return {
            'workflow_id': workflow_id,
            'status': 'success',
            'state': workflow_state
        }
    
    def clear_state(self, workflow_id: str) -> bool:
        """
        Clear workflow state.
        
        Args:
            workflow_id: Unique identifier for the workflow
            
        Returns:
            bool: True if state was cleared successfully
        """
        try:
            if workflow_id in self._states:
                del self._states[workflow_id]
            
            state_file = self._get_state_file_path(workflow_id)
            if state_file.exists():
                state_file.unlink()
            
            return True
        except Exception:
            return False
    
    def get_all_stages(self, workflow_id: str) -> List[str]:
        """
        Get all completed stages for a workflow.
        
        Args:
            workflow_id: Unique identifier for the workflow
            
        Returns:
            List[str]: List of completed stages
        """
        workflow_state = self._load_state(workflow_id)
        if workflow_state:
            return workflow_state.get('stages', [])
        return []
    
    def get_stage_data(self, workflow_id: str, stage: str) -> Optional[Dict[str, Any]]:
        """
        Get state data for a specific stage.
        
        Args:
            workflow_id: Unique identifier for the workflow
            stage: Stage name
            
        Returns:
            Optional[Dict[str, Any]]: Stage state data or None
        """
        workflow_state = self._load_state(workflow_id)
        if workflow_state:
            return workflow_state.get('state_data', {}).get(stage)
        return None
```