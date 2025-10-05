"""
Progression Tracking - Iteration 21
Layer: User Interface Layer
Phase: REFACTOR (Enhanced Implementation)
Created: 2025-10-05

Provides progression tracking for layer/feature development status.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


class ProgressionTracker:
    """Track and display development progression across layers/features."""
    
    def __init__(self, workflow_api=None):
        """
        Initialize progression tracker.
        
        Args:
            workflow_api: Workflow API client (optional)
        """
        self.workflow_api = workflow_api
        self._cache = {}
    
    def get_layer_progression(
        self,
        layer_id: str
    ) -> Dict[str, Any]:
        """
        Get progression status for a specific layer.
        
        Args:
            layer_id: Layer identifier (e.g., 'ui', 'business_logic')
        
        Returns:
            Dict containing:
                - layer_id: str
                - status: str (not_started, in_progress, complete)
                - progress_percentage: float (0-100)
                - features_total: int
                - features_complete: int
                - last_updated: str (ISO timestamp)
        """
        # Mock data for demonstration
        mock_data = {
            'ui': {'total': 8, 'complete': 4, 'status': 'in_progress'},
            'business_logic': {'total': 12, 'complete': 12, 'status': 'complete'},
            'data_access': {'total': 6, 'complete': 5, 'status': 'in_progress'},
            'integration': {'total': 10, 'complete': 8, 'status': 'in_progress'}
        }
        
        data = mock_data.get(layer_id, {'total': 0, 'complete': 0, 'status': 'not_started'})
        total = data['total']
        complete = data['complete']
        
        return {
            'layer_id': layer_id,
            'status': data['status'],
            'progress_percentage': (complete / total * 100) if total > 0 else 0,
            'features_total': total,
            'features_complete': complete,
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
    
    def get_overall_progression(self) -> Dict[str, Any]:
        """
        Get overall system progression.
        
        Returns:
            Dict containing:
                - total_layers: int
                - layers_complete: int
                - overall_progress: float (0-100)
                - layers: List of layer statuses
        """
        layers = ['ui', 'business_logic', 'data_access', 'integration']
        layer_data = [self.get_layer_progression(layer) for layer in layers]
        
        total_features = sum(l['features_total'] for l in layer_data)
        complete_features = sum(l['features_complete'] for l in layer_data)
        layers_complete = sum(1 for l in layer_data if l['status'] == 'complete')
        
        return {
            'total_layers': len(layers),
            'layers_complete': layers_complete,
            'overall_progress': (complete_features / total_features * 100) 
                if total_features > 0 else 0,
            'total_features': total_features,
            'complete_features': complete_features,
            'layers': layer_data
        }
    
    def get_feature_milestones(
        self,
        feature_id: str
    ) -> Dict[str, Any]:
        """
        Get milestone tracking for a feature.
        
        Args:
            feature_id: Feature identifier
        
        Returns:
            Dict containing:
                - feature_id: str
                - milestones: List of milestones
                - current_milestone: str
                - completion_eta: str (ISO timestamp)
        """
        # Mock milestones
        milestones = [
            {'name': 'Requirements', 'status': 'complete', 'date': '2025-09-01'},
            {'name': 'Design', 'status': 'complete', 'date': '2025-09-15'},
            {'name': 'Implementation', 'status': 'in_progress', 'date': None},
            {'name': 'Testing', 'status': 'not_started', 'date': None},
            {'name': 'Deployment', 'status': 'not_started', 'date': None}
        ]
        
        current = next((m for m in milestones if m['status'] == 'in_progress'), None)
        
        return {
            'feature_id': feature_id,
            'milestones': milestones,
            'current_milestone': current['name'] if current else 'Complete',
            'completion_eta': '2025-10-15T00:00:00Z'
        }
    
    def render_progress_bar(
        self,
        progress: float,
        width: int = 50
    ) -> str:
        """
        Render ASCII progress bar.
        
        Args:
            progress: Progress percentage (0-100)
            width: Width of progress bar in characters
        
        Returns:
            ASCII progress bar string
        """
        filled = int(width * progress / 100)
        empty = width - filled
        bar = '=' * filled + '-' * empty
        return f"[{bar}] {progress:.1f}%"
