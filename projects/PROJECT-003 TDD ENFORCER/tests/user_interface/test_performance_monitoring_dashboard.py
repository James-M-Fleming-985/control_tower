"""
Test Suite for Performance Monitoring Dashboard - TDD Iteration 16 REFACTOR Phase
Tests that methods work correctly with full implementation.
Updated: 2025-10-05
"""

from src.user_interface.performance_monitoring_dashboard import (
    PerformanceMonitoringDashboard
)


class TestPerformanceMonitoringDashboard:
    """Test suite for REFACTOR phase - all tests validate working implementations."""
    
    def test_render_performance_overview_works_after_implementation(self):
        """REFACTOR: Performance overview rendering should work with full implementation"""
        dashboard = PerformanceMonitoringDashboard()
        performance_data = {
            "system_performance": {
                "average_response_time_ms": 180,
                "target_response_time_ms": 200,
                "performance_score": 0.90,
                "status": "healthy"
            },
            "component_performance": {
                "mobile_command_history": {"response_time_ms": 150, "status": "healthy"},
                "context_engine": {"response_time_ms": 220, "status": "warning"},
                "validation_engine": {"response_time_ms": 170, "status": "healthy"}
            }
        }
        
        # This should work - full implementation exists
        result = dashboard.render_performance_overview(performance_data)
        
        # Verify return structure
        assert result["overview_rendered"] is True
        assert "system_status" in result
        assert "components_count" in result  # Fixed key name
        assert "performance_score" in result
    
    def test_display_performance_trends_works_after_implementation(self):
        """REFACTOR: Performance trends display should work with full implementation"""
        dashboard = PerformanceMonitoringDashboard()
        trends_data = {
            "time_range": "last_24_hours",
            "metrics": [
                {"timestamp": "2025-09-29T10:00:00Z", "response_time_ms": 180},
                {"timestamp": "2025-09-29T11:00:00Z", "response_time_ms": 190},
                {"timestamp": "2025-09-29T12:00:00Z", "response_time_ms": 170}
            ],
            "target_line": 200
        }
        
        # This should work - full implementation exists
        result = dashboard.display_performance_trends(trends_data)
        
        # Verify return structure
        assert result["trends_displayed"] is True
        assert "time_range" in result
        assert "data_points" in result  # Fixed key name
        assert result["data_points"] == 3
    
    def test_show_performance_alerts_works_after_implementation(self):
        """REFACTOR: Performance alerts display should work with full implementation"""
        dashboard = PerformanceMonitoringDashboard()
        alerts_data = {
            "active_alerts": [
                {"component": "context_engine", "metric": "response_time", "value": 220, "threshold": 200}
            ],
            "alert_history": [],
            "alert_summary": {"critical": 0, "warning": 1, "info": 0}
        }
        
        # This should work - full implementation exists
        result = dashboard.show_performance_alerts(alerts_data)
        
        # Verify return structure
        assert result["alerts_displayed"] is True
        assert "active_count" in result
        assert result["active_count"] == 1
    
    def test_render_real_time_metrics_works_after_implementation(self):
        """REFACTOR: Real-time metrics rendering should work with full implementation"""
        dashboard = PerformanceMonitoringDashboard()
        real_time_config = {
            "refresh_interval_seconds": 5,
            "metrics_to_display": ["response_time", "throughput", "error_rate"],
            "visualization_type": "live_chart"
        }
        
        # This should work - full implementation exists
        result = dashboard.render_real_time_metrics(real_time_config)
        
        # Verify return structure
        assert result["metrics_rendered"] is True
        assert "refresh_interval_seconds" in result  # Fixed key name
        assert "visualization_type" in result
        assert result["refresh_interval_seconds"] == 5
