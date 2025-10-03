"""
Context Visualization Interface - TDD Iteration 14
Layer: User Interface Layer
Phase: REFACTOR (Full Implementation)
Created: 2025-10-03
Refactored: 2025-10-03
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta


class ContextVisualizationInterface:
    """Context visualization interface for hierarchy, sync status, and change timeline
    
    This class provides:
    - Context hierarchy tree visualization
    - Sync status monitoring with version tracking
    - Change timeline with event history
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize context visualization interface
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
    
    def render_context_hierarchy(self, hierarchy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Render context hierarchy with tree visualization
        
        Args:
            hierarchy_data: Hierarchy configuration with user_id and context_tree
                Expected structure:
                {
                    "user_id": "user_123",
                    "context_tree": {
                        "project": "PROJECT-003",
                        "system": "extended_validation",
                        "feature": "validation_engine",
                        "layers": ["data_access", "business_logic", "integration", "ui"]
                    }
                }
        
        Returns:
            Dict containing hierarchy visualization details:
            {
                "hierarchy_rendered": bool,
                "user_id": str,
                "tree_structure": Dict[str, Any],
                "node_count": int,
                "depth_levels": int,
                "interactive_nodes": List[str],
                "visualization_type": str
            }
        
        Raises:
            ValueError: If hierarchy_data structure is invalid
        """
        # Validation
        if not isinstance(hierarchy_data, dict):
            raise ValueError("hierarchy_data must be a dictionary")
        if 'user_id' not in hierarchy_data or not hierarchy_data['user_id']:
            raise ValueError("hierarchy_data must contain non-empty 'user_id'")
        if 'context_tree' not in hierarchy_data:
            raise ValueError("hierarchy_data must contain 'context_tree'")
        
        user_id = hierarchy_data['user_id']
        context_tree = hierarchy_data['context_tree']
        
        if not isinstance(context_tree, dict):
            raise ValueError("context_tree must be a dictionary")
        
        # Extract components
        project = context_tree.get('project', 'Unknown')
        system = context_tree.get('system', 'Unknown')
        feature = context_tree.get('feature', 'Unknown')
        layers = context_tree.get('layers', [])
        
        if not isinstance(layers, list) or len(layers) == 0:
            raise ValueError("context_tree.layers must be a non-empty list")
        
        # Calculate metrics
        node_count = 1 + 1 + 1 + len(layers)  # project + system + feature + layers
        depth_levels = 4
        
        # Generate interactive nodes
        interactive_nodes = [
            f"project_{project}",
            f"system_{system}",
            f"feature_{feature}"
        ] + [f"layer_{layer}" for layer in layers]
        
        # Build tree structure
        tree_structure = {
            'project': {
                'name': project,
                'children': {
                    'system': {
                        'name': system,
                        'children': {
                            'feature': {
                                'name': feature,
                                'children': {
                                    'layers': layers
                                }
                            }
                        }
                    }
                }
            }
        }
        
        return {
            'hierarchy_rendered': True,
            'user_id': user_id,
            'tree_structure': tree_structure,
            'node_count': node_count,
            'depth_levels': depth_levels,
            'interactive_nodes': interactive_nodes,
            'visualization_type': 'tree'
        }
    
    def display_context_sync_status(self, sync_status: Dict[str, Any]) -> Dict[str, Any]:
        """Display context sync status with version tracking
        
        Args:
            sync_status: Sync status with versions, conflicts, and health
                Expected structure:
                {
                    "local_version": 5,
                    "remote_version": 5,
                    "sync_conflicts": [],
                    "last_sync_time": "2025-09-29T12:30:00Z",
                    "sync_health": "healthy"
                }
        
        Returns:
            Dict containing sync status visualization details:
            {
                "status_displayed": bool,
                "sync_state": str,
                "version_info": Dict[str, int],
                "conflict_count": int,
                "last_sync_display": str,
                "health_indicator": str,
                "sync_actions": List[str]
            }
        
        Raises:
            ValueError: If sync_status structure is invalid
        """
        # Validation
        if not isinstance(sync_status, dict):
            raise ValueError("sync_status must be a dictionary")
        
        if 'local_version' not in sync_status:
            raise ValueError("sync_status must contain 'local_version'")
        if 'remote_version' not in sync_status:
            raise ValueError("sync_status must contain 'remote_version'")
        if 'sync_conflicts' not in sync_status:
            raise ValueError("sync_status must contain 'sync_conflicts'")
        if 'last_sync_time' not in sync_status:
            raise ValueError("sync_status must contain 'last_sync_time'")
        if 'sync_health' not in sync_status:
            raise ValueError("sync_status must contain 'sync_health'")
        
        local_version = sync_status['local_version']
        remote_version = sync_status['remote_version']
        sync_conflicts = sync_status['sync_conflicts']
        last_sync_time = sync_status['last_sync_time']
        sync_health = sync_status['sync_health']
        
        # Validate types and values
        if not isinstance(local_version, int) or local_version < 0:
            raise ValueError("local_version must be a non-negative integer")
        if not isinstance(remote_version, int) or remote_version < 0:
            raise ValueError("remote_version must be a non-negative integer")
        if not isinstance(sync_conflicts, list):
            raise ValueError("sync_conflicts must be a list")
        if sync_health not in ['healthy', 'degraded', 'critical']:
            raise ValueError("sync_health must be one of: 'healthy', 'degraded', 'critical'")
        
        # Determine sync state
        conflict_count = len(sync_conflicts)
        if conflict_count > 0:
            sync_state = 'conflict'
        elif local_version == remote_version:
            sync_state = 'synced'
        else:
            sync_state = 'out_of_sync'
        
        # Format timestamp
        last_sync_display = self._format_relative_time(last_sync_time)
        
        # Create health indicator
        health_indicators = {
            'healthy': '🟢 Healthy',
            'degraded': '🟡 Degraded',
            'critical': '🔴 Critical'
        }
        health_indicator = health_indicators.get(sync_health, '⚪ Unknown')
        
        # Determine sync actions
        sync_actions = []
        if local_version < remote_version:
            sync_actions.append('pull')
        if local_version > remote_version:
            sync_actions.append('push')
        if conflict_count > 0:
            sync_actions.append('resolve_conflicts')
        
        return {
            'status_displayed': True,
            'sync_state': sync_state,
            'version_info': {'local': local_version, 'remote': remote_version},
            'conflict_count': conflict_count,
            'last_sync_display': last_sync_display,
            'health_indicator': health_indicator,
            'sync_actions': sync_actions
        }
    
    def show_context_change_timeline(self, timeline_data: Dict[str, Any]) -> Dict[str, Any]:
        """Show context change timeline with event history
        
        Args:
            timeline_data: Timeline data with changes and time_range filter
                Expected structure:
                {
                    "changes": [
                        {"timestamp": "2025-09-29T12:00:00Z", "type": "layer_switch", "details": {}},
                        {"timestamp": "2025-09-29T12:15:00Z", "type": "test_result", "details": {}}
                    ],
                    "time_range": "last_hour"
                }
        
        Returns:
            Dict containing timeline visualization details:
            {
                "timeline_displayed": bool,
                "total_changes": int,
                "displayed_changes": int,
                "time_range": str,
                "event_types": List[str],
                "timeline_events": List[Dict[str, Any]],
                "filter_options": List[str]
            }
        
        Raises:
            ValueError: If timeline_data structure is invalid
        """
        # Validation
        if not isinstance(timeline_data, dict):
            raise ValueError("timeline_data must be a dictionary")
        if 'changes' not in timeline_data:
            raise ValueError("timeline_data must contain 'changes'")
        if 'time_range' not in timeline_data:
            raise ValueError("timeline_data must contain 'time_range'")
        
        changes = timeline_data['changes']
        time_range = timeline_data['time_range']
        
        if not isinstance(changes, list):
            raise ValueError("changes must be a list")
        
        valid_time_ranges = ['last_hour', 'last_day', 'last_week', 'all']
        if time_range not in valid_time_ranges:
            raise ValueError(f"time_range must be one of: {', '.join(valid_time_ranges)}")
        
        # Validate change events
        for change in changes:
            if not isinstance(change, dict):
                raise ValueError("Each change must be a dictionary")
            if 'timestamp' not in change or 'type' not in change or 'details' not in change:
                raise ValueError("Each change must contain: timestamp, type, details")
        
        # Sort changes chronologically (most recent first)
        sorted_changes = sorted(changes, key=lambda x: x['timestamp'], reverse=True)
        
        # Apply time range filter
        filtered_changes = self._filter_changes_by_time_range(sorted_changes, time_range)
        
        # Extract unique event types
        event_types = list(set(change['type'] for change in changes))
        
        # Format timeline events
        timeline_events = [
            {
                'timestamp': change['timestamp'],
                'type': change['type'],
                'type_icon': self._get_event_icon(change['type']),
                'details': change['details'],
                'time_ago': self._format_relative_time(change['timestamp'])
            }
            for change in filtered_changes
        ]
        
        return {
            'timeline_displayed': True,
            'total_changes': len(changes),
            'displayed_changes': len(filtered_changes),
            'time_range': time_range,
            'event_types': event_types,
            'timeline_events': timeline_events,
            'filter_options': valid_time_ranges
        }
    
    def _format_relative_time(self, iso_timestamp: str) -> str:
        """Format ISO timestamp as relative time
        
        Args:
            iso_timestamp: ISO 8601 timestamp string
            
        Returns:
            Relative time string (e.g., '5 minutes ago', 'just now')
        """
        try:
            # Parse ISO timestamp
            if iso_timestamp.endswith('Z'):
                iso_timestamp = iso_timestamp[:-1] + '+00:00'
            
            timestamp = datetime.fromisoformat(iso_timestamp)
            now = datetime.now(timestamp.tzinfo) if timestamp.tzinfo else datetime.now()
            
            # Calculate time difference
            delta = now - timestamp
            
            # Format as relative time
            if delta.total_seconds() < 60:
                return "just now"
            elif delta.total_seconds() < 3600:
                minutes = int(delta.total_seconds() / 60)
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            elif delta.total_seconds() < 86400:
                hours = int(delta.total_seconds() / 3600)
                return f"{hours} hour{'s' if hours != 1 else ''} ago"
            elif delta.days < 7:
                return f"{delta.days} day{'s' if delta.days != 1 else ''} ago"
            elif delta.days < 30:
                weeks = delta.days // 7
                return f"{weeks} week{'s' if weeks != 1 else ''} ago"
            else:
                months = delta.days // 30
                return f"{months} month{'s' if months != 1 else ''} ago"
        except Exception:
            return iso_timestamp  # Fallback to original timestamp
    
    def _filter_changes_by_time_range(self, changes: List[Dict[str, Any]], time_range: str) -> List[Dict[str, Any]]:
        """Filter changes based on time range
        
        Args:
            changes: List of change events
            time_range: Time range filter
            
        Returns:
            Filtered list of changes
        """
        if time_range == 'all':
            return changes
        
        now = datetime.now()
        time_deltas = {
            'last_hour': timedelta(hours=1),
            'last_day': timedelta(days=1),
            'last_week': timedelta(weeks=1)
        }
        
        cutoff_time = now - time_deltas.get(time_range, timedelta(days=1))
        
        filtered = []
        for change in changes:
            try:
                timestamp_str = change['timestamp']
                if timestamp_str.endswith('Z'):
                    timestamp_str = timestamp_str[:-1] + '+00:00'
                
                timestamp = datetime.fromisoformat(timestamp_str)
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=cutoff_time.tzinfo)
                
                if timestamp >= cutoff_time:
                    filtered.append(change)
            except Exception:
                # If timestamp parsing fails, include the change
                filtered.append(change)
        
        return filtered
    
    def _get_event_icon(self, event_type: str) -> str:
        """Get icon for event type
        
        Args:
            event_type: Type of event
            
        Returns:
            Icon/emoji for the event type
        """
        icons = {
            'layer_switch': '🔄',
            'test_result': '✅',
            'commit': '💾',
            'deploy': '🚀',
            'merge': '🔀',
            'rollback': '⏪',
            'error': '⚠️'
        }
        return icons.get(event_type, '📝')
