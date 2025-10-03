"""
UI Layer Interface Contract Validation
Tests that UI layer correctly implements expected interface contracts
"""

import pytest
from performance_monitoring_dashboard import PerformanceMonitoringDashboard


class TestUIInterfaceContracts:
    """Validate UI layer adheres to interface contracts"""
    
    def test_performance_dashboard_interface_contract(self):
        """Validate PerformanceMonitoringDashboard interface contract"""
        dashboard = PerformanceMonitoringDashboard()
        
        # Verify all required methods exist
        assert hasattr(dashboard, 'render_performance_overview')
        assert hasattr(dashboard, 'display_performance_trends')
        assert hasattr(dashboard, 'show_performance_alerts')
        assert hasattr(dashboard, 'render_real_time_metrics')
        
        # Verify methods are callable
        assert callable(dashboard.render_performance_overview)
        assert callable(dashboard.display_performance_trends)
        assert callable(dashboard.show_performance_alerts)
        assert callable(dashboard.render_real_time_metrics)
    
    def test_render_performance_overview_contract(self):
        """Validate render_performance_overview method contract"""
        dashboard = PerformanceMonitoringDashboard()
        
        # Test input contract: accepts Dict[str, Any]
        valid_input = {
            "system_performance": {
                "average_response_time_ms": 150,
                "target_response_time_ms": 200,
                "performance_score": 0.95,
                "status": "healthy"
            },
            "component_performance": {}
        }
        
        result = dashboard.render_performance_overview(valid_input)
        
        # Test output contract: returns Dict[str, Any]
        assert isinstance(result, dict)
        
        # Verify required output fields
        required_fields = [
            'overview_rendered',
            'system_status',
            'performance_score',
            'average_response_time_ms',
            'target_response_time_ms',
            'components_count',
            'components_over_threshold',
            'display_data'
        ]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Verify field types
        assert isinstance(result['overview_rendered'], bool)
        assert isinstance(result['system_status'], str)
        assert isinstance(result['performance_score'], (int, float))
        assert isinstance(result['components_count'], int)
        assert isinstance(result['components_over_threshold'], list)
        assert isinstance(result['display_data'], dict)
    
    def test_display_performance_trends_contract(self):
        """Validate display_performance_trends method contract"""
        dashboard = PerformanceMonitoringDashboard()
        
        valid_input = {
            "time_range": "1h",
            "metrics": [{"response_time_ms": 100}],
            "target_line": 200
        }
        
        result = dashboard.display_performance_trends(valid_input)
        
        # Verify required output fields
        required_fields = [
            'trends_displayed',
            'time_range',
            'data_points',
            'trend_direction',
            'min_response_time_ms',
            'max_response_time_ms',
            'avg_response_time_ms',
            'target_line',
            'chart_data'
        ]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Verify trend_direction enum values
        assert result['trend_direction'] in ['improving', 'stable', 'degrading']
    
    def test_show_performance_alerts_contract(self):
        """Validate show_performance_alerts method contract"""
        dashboard = PerformanceMonitoringDashboard()
        
        valid_input = {
            "active_alerts": [],
            "alert_history": [],
            "alert_summary": {}
        }
        
        result = dashboard.show_performance_alerts(valid_input)
        
        # Verify required output fields
        required_fields = [
            'alerts_displayed',
            'active_count',
            'alert_summary',
            'sorted_alerts',
            'recommended_actions',
            'alert_trend'
        ]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Verify alert_trend enum values
        assert result['alert_trend'] in ['stable', 'increasing']
        
        # Verify recommended_actions is non-empty list
        assert isinstance(result['recommended_actions'], list)
        assert len(result['recommended_actions']) > 0
    
    def test_render_real_time_metrics_contract(self):
        """Validate render_real_time_metrics method contract"""
        dashboard = PerformanceMonitoringDashboard()
        
        valid_input = {
            "refresh_interval_seconds": 5,
            "metrics_to_display": ["metric1"],
            "visualization_type": "chart"
        }
        
        result = dashboard.render_real_time_metrics(valid_input)
        
        # Verify required output fields
        required_fields = [
            'metrics_rendered',
            'refresh_interval_seconds',
            'metrics_count',
            'metrics_to_display',
            'visualization_type',
            'auto_refresh_enabled'
        ]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Verify refresh_interval range constraint
        assert 1 <= result['refresh_interval_seconds'] <= 60
    
    def test_error_handling_contract(self):
        """Validate error handling adheres to contract"""
        dashboard = PerformanceMonitoringDashboard()
        
        # Test ValueError raised for invalid inputs
        with pytest.raises(ValueError):
            dashboard.render_performance_overview("invalid")
        
        with pytest.raises(ValueError):
            dashboard.display_performance_trends({"time_range": "1h"})
        
        with pytest.raises(ValueError):
            dashboard.show_performance_alerts({"active_alerts": "invalid"})
        
        with pytest.raises(ValueError):
            dashboard.render_real_time_metrics({"refresh_interval_seconds": 0})


class TestBackwardCompatibility:
    """Validate backward compatibility with existing UI components"""
    
    def test_performance_dashboard_does_not_interfere(self):
        """Test that performance dashboard doesn't affect other UI components"""
        # Performance dashboard is isolated and doesn't depend on globals
        dashboard1 = PerformanceMonitoringDashboard()
        dashboard2 = PerformanceMonitoringDashboard()
        
        # Both instances independent
        assert dashboard1 is not dashboard2
        
        # No shared state
        data = {
            "system_performance": {
                "average_response_time_ms": 100,
                "target_response_time_ms": 200,
                "performance_score": 0.95,
                "status": "healthy"
            },
            "component_performance": {}
        }
        
        result1 = dashboard1.render_performance_overview(data)
        result2 = dashboard2.render_performance_overview(data)
        
        # Results identical but independent
        assert result1 == result2
        assert result1 is not result2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
