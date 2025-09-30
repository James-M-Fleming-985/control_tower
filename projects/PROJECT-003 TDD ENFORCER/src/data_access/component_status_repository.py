"""
Component Status Repository for Data Access Layer - LAY-003-02-01-001
Enhanced with enum validation, metrics tracking, and batch operations.
"""
import json
import logging
from typing import Dict, Any, List, Literal, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

StatusType = Literal['ready', 'not_ready', 'in_progress', 'blocked', 'testing']


class ComponentStatus(Enum):
    """Enumerated component status types with validation"""
    READY = "ready"
    NOT_READY = "not_ready"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    TESTING = "testing"


@dataclass
class ComponentStatusData:
    """Structured component status data"""
    component_id: str
    status: ComponentStatus
    position: str
    updated_at: str
    last_updated: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'component_id': self.component_id,
            'status': self.status.value,
            'position': self.position,
            'updated_at': self.updated_at,
            'last_updated': self.last_updated,
            'metadata': self.metadata or {}
        }


class ComponentStatusRepository:
    """Enhanced repository for component development status tracking"""
    
    def __init__(self, storage_path: str = "./data/components", 
                 enable_metrics: bool = True):
        """Initialize with optional metrics collection"""
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.enable_metrics = enable_metrics
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Status transition metrics
        self.metrics = {
            'status_changes': {},
            'readiness_checks': 0,
            'batch_operations': 0,
            'error_count': 0
        } if enable_metrics else {}
        
    def store_status(self, status_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Store component development status with enhanced validation
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Validate required fields
            required_fields = ['component_id', 'status', 'position']
            missing_fields = [field for field in required_fields 
                            if field not in status_data]
            
            if missing_fields:
                error_msg = f"Missing required fields: {', '.join(missing_fields)}"
                return False, error_msg
            
            # Validate status enum
            try:
                status_enum = ComponentStatus(status_data['status'])
            except ValueError:
                valid_statuses = [s.value for s in ComponentStatus]
                error_msg = f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                return False, error_msg
            
            # Create structured data
            component_data = ComponentStatusData(
                component_id=status_data['component_id'],
                status=status_enum,
                position=status_data['position'],
                updated_at=status_data.get('updated_at', 
                                         datetime.now().isoformat()),
                last_updated=datetime.now().isoformat(),
                metadata=status_data.get('metadata', {})
            )
            
            # Check for status transition
            previous_status = self._get_previous_status(
                component_data.component_id)
            if previous_status and self.enable_metrics:
                transition = f"{previous_status} -> {status_enum.value}"
                current_count = self.metrics['status_changes'].get(
                    transition, 0)
                self.metrics['status_changes'][transition] = current_count + 1
            
            # Store to file
            filename = f"{component_data.component_id}_status.json"
            filepath = self.storage_path / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(component_data.to_dict(), f, indent=2)
            
            msg = f"Status updated for component {component_data.component_id}: {status_enum.value}"
            self.logger.info(msg)
            return True, f"Status updated successfully to {status_enum.value}"
            
        except Exception as e:
            if self.enable_metrics:
                self.metrics['error_count'] += 1
            self.logger.error(f"Error storing component status: {e}")
            return False, f"Storage error: {str(e)}"
    
    def _get_previous_status(self, component_id: str) -> Optional[str]:
        """Get previous status for status transition tracking"""
        try:
            filename = f"{component_id}_status.json"
            filepath = self.storage_path / filename
            
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    status_data = json.load(f)
                    return status_data.get('status')
                    
        except Exception as e:
            self.logger.debug(f"Could not get previous status for "
                              f"{component_id}: {e}")
            
        return None

    def check_readiness(self, component_id: str) -> Tuple[
            ComponentStatus, Dict[str, Any]]:
        """
        Enhanced readiness checking with detailed information
        
        Returns:
            Tuple of (status: ComponentStatus, info: Dict)
        """
        try:
            if self.enable_metrics:
                self.metrics['readiness_checks'] += 1
                
            filename = f"{component_id}_status.json"
            filepath = self.storage_path / filename
            
            if not filepath.exists():
                return ComponentStatus.NOT_READY, {
                    'message': 'Component not found',
                    'checked_at': datetime.now().isoformat()
                }
                
            # Load status data
            with open(filepath, 'r', encoding='utf-8') as f:
                status_data = json.load(f)
                
            status = ComponentStatus(status_data.get('status', 'not_ready'))
            
            # Calculate time since last update
            last_updated = status_data.get('last_updated')
            time_since_update = None
            if last_updated:
                try:
                    last_update_time = datetime.fromisoformat(last_updated)
                    time_diff = datetime.now() - last_update_time
                    time_since_update = time_diff.total_seconds()
                except ValueError:
                    pass
            
            info = {
                'status': status.value,
                'position': status_data.get('position', 'unknown'),
                'last_updated': last_updated,
                'time_since_update_seconds': time_since_update,
                'metadata': status_data.get('metadata', {}),
                'checked_at': datetime.now().isoformat()
            }
            
            return status, info
            
        except Exception as e:
            if self.enable_metrics:
                self.metrics['error_count'] += 1
            self.logger.error(f"Error checking component readiness: {e}")
            return ComponentStatus.NOT_READY, {
                'error': str(e),
                'checked_at': datetime.now().isoformat()
            }
    
    def get_components_by_status(
            self, status: StatusType) -> List[Dict[str, Any]]:
        """Get all components with specific status"""
        components = []
        
        try:
            for filepath in self.storage_path.glob("*_status.json"):
                with open(filepath, 'r', encoding='utf-8') as f:
                    status_data = json.load(f)
                    
                if status_data.get('status') == status:
                    components.append(status_data)
                    
        except Exception as e:
            print(f"Error retrieving components by status: {e}")
            
        return components
