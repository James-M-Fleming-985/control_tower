"""
Context Visualization Interface - TDD Iteration 14 REFACTOR Phase Tests
Layer: User Interface Layer
Phase: REFACTOR (Testing Actual Implementation)
Created: 2025-10-03
"""

import pytest
from context_visualization_interface import ContextVisualizationInterface


class TestContextVisualizationInterfaceRefactored:
    
    def test_render_context_hierarchy_success(self):
        """REFACTOR: Context hierarchy rendering returns proper structure"""
        viz_interface = ContextVisualizationInterface()
        hierarchy_data = {
            "user_id": "user_123",
            "context_tree": {
                "project": "PROJECT-003",
                "system": "extended_validation",
                "feature": "validation_engine",
                "layers": ["data_access", "business_logic", "integration", "ui"]
            }
        }
        
        result = viz_interface.render_context_hierarchy(hierarchy_data)
        
        assert result['hierarchy_rendered'] is True
        assert result['user_id'] == "user_123"
        assert result['node_count'] == 7  # 1 + 1 + 1 + 4
        assert result['depth_levels'] == 4
        assert len(result['interactive_nodes']) == 7
        assert result['visualization_type'] == 'tree'
        assert 'tree_structure' in result
    
    def test_display_context_sync_status_success(self):
        """REFACTOR: Context sync status display returns proper structure"""
        viz_interface = ContextVisualizationInterface()
        sync_status = {
            "local_version": 5,
            "remote_version": 5,
            "sync_conflicts": [],
            "last_sync_time": "2025-09-29T12:30:00Z",
            "sync_health": "healthy"
        }
        
        result = viz_interface.display_context_sync_status(sync_status)
        
        assert result['status_displayed'] is True
        assert result['sync_state'] == 'synced'
        assert result['version_info'] == {'local': 5, 'remote': 5}
        assert result['conflict_count'] == 0
        assert '🟢' in result['health_indicator']
        assert isinstance(result['last_sync_display'], str)
        assert isinstance(result['sync_actions'], list)
    
    def test_show_context_change_timeline_success(self):
        """REFACTOR: Context change timeline returns proper structure"""
        viz_interface = ContextVisualizationInterface()
        timeline_data = {
            "changes": [
                {"timestamp": "2025-09-29T12:00:00Z", "type": "layer_switch", "details": {}},
                {"timestamp": "2025-09-29T12:15:00Z", "type": "test_result", "details": {}}
            ],
            "time_range": "all"
        }
        
        result = viz_interface.show_context_change_timeline(timeline_data)
        
        assert result['timeline_displayed'] is True
        assert result['total_changes'] == 2
        assert result['displayed_changes'] == 2
        assert result['time_range'] == 'all'
        assert len(result['event_types']) > 0
        assert len(result['timeline_events']) == 2
        assert 'filter_options' in result
