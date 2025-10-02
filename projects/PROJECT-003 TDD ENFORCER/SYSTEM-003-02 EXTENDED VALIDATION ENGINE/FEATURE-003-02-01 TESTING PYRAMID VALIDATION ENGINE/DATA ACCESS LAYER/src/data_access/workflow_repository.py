"""
Workflow Repository for Data Access Layer - LAY-003-02-01-001
Handles PROJECT-002 workflow progression tracking and automatic layer progression.
"""
import json
from typing import Dict, Any, List, Literal
from datetime import datetime
from pathlib import Path

ProgressionStatus = Literal['ready', 'in_progress', 'completed', 'blocked']

class WorkflowRepository:
    """Repository for PROJECT-002 workflow progression tracking"""
    
    def __init__(self, storage_path: str = "./data/workflows"):
        """Initialize WorkflowRepository with file-based storage"""
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
    def store_workflow_data(self, workflow_data: Dict[str, Any]) -> bool:
        """
        Store PROJECT-002 workflow progression data
        
        Args:
            workflow_data: Dictionary containing workflow progression information
            
        Returns:
            True if storage successful, False otherwise
        """
        try:
            # Generate filename from workflow_id
            workflow_id = workflow_data.get('workflow_id', f'workflow_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
            filename = f"{workflow_id}.json"
            filepath = self.storage_path / filename
            
            # Add storage timestamp
            workflow_data['last_updated'] = datetime.now().isoformat()
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(workflow_data, f, indent=2)
                
            return True
            
        except Exception as e:
            print(f"Error storing workflow data: {e}")
            return False
    
    def get_progression_status(self, workflow_id: str) -> ProgressionStatus:
        """
        Get current progression status for PROJECT-002
        
        Args:
            workflow_id: ID of the workflow to check
            
        Returns:
            Current progression status
        """
        try:
            filename = f"{workflow_id}.json"
            filepath = self.storage_path / filename
            
            if not filepath.exists():
                return 'ready'
                
            # Load workflow data
            with open(filepath, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)
                
            # Get status with default fallback
            status = workflow_data.get('progression_status', 'ready')
            
            # Validate status is one of allowed values
            allowed_statuses = ['ready', 'in_progress', 'completed', 'blocked']
            if status not in allowed_statuses:
                return 'ready'
                
            return status
            
        except Exception as e:
            print(f"Error getting progression status: {e}")
            return 'ready'
    
    def check_progression_readiness(self, layer: str) -> bool:
        """
        Check if layer is ready for PROJECT-002 progression
        
        Args:
            layer: The layer to check readiness for
            
        Returns:
            True if layer is ready for progression, False otherwise
        """
        try:
            # Check for layer-specific readiness file
            readiness_file = self.storage_path / f"{layer}_readiness.json"
            
            if readiness_file.exists():
                with open(readiness_file, 'r', encoding='utf-8') as f:
                    readiness_data = json.load(f)
                    return readiness_data.get('ready', False)
            
            # Default logic: check if any workflow in this layer is completed
            for filepath in self.storage_path.glob("*.json"):
                if filepath.name.endswith('_readiness.json'):
                    continue
                    
                with open(filepath, 'r', encoding='utf-8') as f:
                    workflow_data = json.load(f)
                    
                if (workflow_data.get('current_layer') == layer and 
                    workflow_data.get('progression_status') == 'completed'):
                    return True
                    
            return False
            
        except Exception as e:
            print(f"Error checking progression readiness: {e}")
            return False
    
    def trigger_progression(self, from_layer: str, to_layer: str) -> bool:
        """
        Trigger automatic progression to next layer
        
        Args:
            from_layer: Current layer
            to_layer: Next layer to progress to
            
        Returns:
            True if progression triggered successfully, False otherwise
        """
        try:
            # Create progression record
            progression_data = {
                'progression_id': f"prog_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'from_layer': from_layer,
                'to_layer': to_layer,
                'triggered_at': datetime.now().isoformat(),
                'status': 'completed',
                'trigger_type': 'automatic'
            }
            
            # Store progression record
            filename = f"progression_{from_layer}_to_{to_layer}.json"
            filepath = self.storage_path / "progressions" / filename
            filepath.parent.mkdir(exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(progression_data, f, indent=2)
                
            # Update target layer readiness
            readiness_file = self.storage_path / f"{to_layer}_readiness.json"
            readiness_data = {
                'layer': to_layer,
                'ready': True,
                'triggered_from': from_layer,
                'updated_at': datetime.now().isoformat()
            }
            
            with open(readiness_file, 'w', encoding='utf-8') as f:
                json.dump(readiness_data, f, indent=2)
                
            return True
            
        except Exception as e:
            print(f"Error triggering progression: {e}")
            return False
    
    def get_workflow_history(self, workflow_id: str) -> List[Dict[str, Any]]:
        """
        Get PROJECT-002 workflow progression history
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            List of workflow history entries
        """
        history = []
        
        try:
            # Look for workflow file
            filename = f"{workflow_id}.json"
            filepath = self.storage_path / filename
            
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    workflow_data = json.load(f)
                    
                # Add current state as history entry
                history.append({
                    'timestamp': workflow_data.get('last_updated', datetime.now().isoformat()),
                    'action': 'current_state',
                    'layer': workflow_data.get('current_layer', ''),
                    'status': workflow_data.get('progression_status', 'ready'),
                    'data': workflow_data
                })
            
            # Look for progression history
            progressions_dir = self.storage_path / "progressions"
            if progressions_dir.exists():
                for prog_file in progressions_dir.glob(f"*{workflow_id}*.json"):
                    with open(prog_file, 'r', encoding='utf-8') as f:
                        prog_data = json.load(f)
                        history.append({
                            'timestamp': prog_data.get('triggered_at', ''),
                            'action': 'progression',
                            'from_layer': prog_data.get('from_layer', ''),
                            'to_layer': prog_data.get('to_layer', ''),
                            'status': prog_data.get('status', ''),
                            'data': prog_data
                        })
            
            # Sort by timestamp
            history.sort(key=lambda x: x.get('timestamp', ''))
            
        except Exception as e:
            print(f"Error retrieving workflow history: {e}")
            
        return history
