"""
Tests for Progression Tracking - Iteration 21
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.user_interface.progression_tracking_refactored import ProgressionTracker


class TestProgressionTracker:
    """Test suite for Progression Tracker"""
    
    @pytest.fixture
    def tracker(self):
        """Create ProgressionTracker instance"""
        return ProgressionTracker()
    
    def test_get_layer_progression_ui(self, tracker):
        """Should get UI layer progression"""
        result = tracker.get_layer_progression('ui')
        
        assert result['layer_id'] == 'ui'
        assert result['status'] == 'in_progress'
        assert result['features_total'] == 8
        assert result['features_complete'] == 4
        assert result['progress_percentage'] == 50.0
        assert 'last_updated' in result
    
    def test_get_layer_progression_complete_layer(self, tracker):
        """Should show complete status for finished layer"""
        result = tracker.get_layer_progression('business_logic')
        
        assert result['status'] == 'complete'
        assert result['progress_percentage'] == 100.0
        assert result['features_complete'] == result['features_total']
    
    def test_get_overall_progression(self, tracker):
        """Should get overall system progression"""
        result = tracker.get_overall_progression()
        
        assert result['total_layers'] == 4
        assert result['layers_complete'] >= 1
        assert 0 <= result['overall_progress'] <= 100
        assert len(result['layers']) == 4
        assert result['total_features'] > 0
        assert result['complete_features'] <= result['total_features']
    
    def test_get_feature_milestones(self, tracker):
        """Should get feature milestone tracking"""
        result = tracker.get_feature_milestones('feature_001')
        
        assert result['feature_id'] == 'feature_001'
        assert len(result['milestones']) == 5
        assert result['current_milestone'] in [
            'Requirements', 'Design', 'Implementation', 
            'Testing', 'Deployment', 'Complete'
        ]
        assert 'completion_eta' in result
    
    def test_render_progress_bar_zero(self, tracker):
        """Should render empty progress bar"""
        result = tracker.render_progress_bar(0, width=20)
        
        assert result == '[--------------------] 0.0%'
    
    def test_render_progress_bar_fifty(self, tracker):
        """Should render half-filled progress bar"""
        result = tracker.render_progress_bar(50, width=20)
        
        assert result == '[==========----------] 50.0%'
    
    def test_render_progress_bar_complete(self, tracker):
        """Should render full progress bar"""
        result = tracker.render_progress_bar(100, width=20)
        
        assert result == '[====================] 100.0%'
