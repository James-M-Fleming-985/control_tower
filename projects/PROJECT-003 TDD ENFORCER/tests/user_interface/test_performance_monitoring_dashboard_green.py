"""
Test Suite for Performance Monitoring Dashboard - TDD Iteration 16 GREEN Phase
Tests actual implementation with proper return values and input validation.
"""

import pytest
from performance_monitoring_dashboard import PerformanceMonitoringDashboard


class TestPerformanceMonitoringDashboardGreen:
    """Test suite for GREEN phase - all tests should pass with actual implementations."""
    
    def test_render_performance_overview_success(self):
        """GREEN: Performance overview rendering returns proper data structure"""
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
        
        result = dashboard.render_performance_overview(performance_data)
        
        # Verify structure
        assert result['overview_rendered'] is True
        assert result['system_status'] == 'healthy'
        assert result['performance_score'] == 0.90
        assert result['average_response_time_ms'] == 180
        assert result['target_response_time_ms'] == 200
        assert result['components_count'] == 3
        assert 'context_engine' in result['components_over_threshold']
        assert len(result['components_over_threshold']) == 1
        assert 'display_data' in result
    
    def test_render_performance_overview_invalid_input(self):
        """GREEN: Performance overview validates input data"""
        dashboard = PerformanceMonitoringDashboard()
        
        # Test non-dict input
        with pytest.raises(ValueError, match="performance_data must be a dictionary"):
            dashboard.render_performance_overview("invalid")
        
        # Test missing system_performance
        with pytest.raises(ValueError, match="must contain 'system_performance'"):
            dashboard.render_performance_overview({"component_performance": {}})
        
        # Test missing component_performance
        with pytest.raises(ValueError, match="must contain 'component_performance'"):
            dashboard.render_performance_overview({"system_performance": {}})
        
        # Test missing required field
        with pytest.raises(ValueError, match="must contain 'average_response_time_ms'"):
            dashboard.render_performance_overview({
                "system_performance": {
                    "target_response_time_ms": 200,
                    "performance_score": 0.90,
                    "status": "healthy"
                },
                "component_performance": {}
            })
    
    def test_display_performance_trends_success(self):
        """GREEN: Performance trends display returns proper data structure"""
        dashboard = PerformanceMonitoringDashboard()
        trends_data = {
            "time_range": "last_24_hours",
            "metrics": [
                {"timestamp": "2025-09-29T10:00:00Z", "response_time_ms": 180},
                {"timestamp": "2025-09-29T11:00:00Z", "response_time_ms": 190},
                {"timestamp": "2025-09-29T12:00:00Z", "response_time_ms": 170},
                {"timestamp": "2025-09-29T13:00:00Z", "response_time_ms": 160}
            ],
            "target_line": 200
        }
        
        result = dashboard.display_performance_trends(trends_data)
        
        # Verify structure
        assert result['trends_displayed'] is True
        assert result['time_range'] == 'last_24_hours'
        assert result['data_points'] == 4
        assert result['trend_direction'] == 'improving'  # 185 avg first half, 165 avg second half
        assert result['min_response_time_ms'] == 160
        assert result['max_response_time_ms'] == 190
        assert result['avg_response_time_ms'] == 175.0
        assert result['target_line'] == 200
        assert len(result['chart_data']) == 4
    
    def test_display_performance_trends_empty_metrics(self):
        """GREEN: Performance trends handles empty metrics list"""
        dashboard = PerformanceMonitoringDashboard()
        trends_data = {
            "time_range": "last_hour",
            "metrics": [],
            "target_line": 200
        }
        
        result = dashboard.display_performance_trends(trends_data)
        
        assert result['trends_displayed'] is True
        assert result['data_points'] == 0
        assert result['trend_direction'] == 'stable'
        assert result['min_response_time_ms'] == 0
        assert result['max_response_time_ms'] == 0
        assert result['avg_response_time_ms'] == 0
    
    def test_display_performance_trends_invalid_input(self):
        """GREEN: Performance trends validates input data"""
        dashboard = PerformanceMonitoringDashboard()
        
        # Test non-dict input
        with pytest.raises(ValueError, match="trends_data must be a dictionary"):
            dashboard.display_performance_trends("invalid")
        
        # Test missing time_range
        with pytest.raises(ValueError, match="must contain 'time_range'"):
            dashboard.display_performance_trends({"metrics": [], "target_line": 200})
        
        # Test missing metrics
        with pytest.raises(ValueError, match="must contain 'metrics'"):
            dashboard.display_performance_trends({"time_range": "1h", "target_line": 200})
        
        # Test non-list metrics
        with pytest.raises(ValueError, match="metrics must be a list"):
            dashboard.display_performance_trends({
                "time_range": "1h",
                "metrics": "invalid",
                "target_line": 200
            })
    
    def test_show_performance_alerts_success(self):
        """GREEN: Performance alerts display returns proper data structure"""
        dashboard = PerformanceMonitoringDashboard()
        alerts_data = {
            "active_alerts": [
                {"component": "context_engine", "metric": "response_time", "value": 220, "threshold": 200},
                {"component": "security_layer", "metric": "response_time", "value": 260, "threshold": 200, "severity": "critical"}
            ],
            "alert_history": [
                {"timestamp": "2025-09-29T09:00:00Z", "component": "validation_engine"}
            ],
            "alert_summary": {"critical": 1, "warning": 1, "info": 0}
        }
        
        result = dashboard.show_performance_alerts(alerts_data)
        
        # Verify structure
        assert result['alerts_displayed'] is True
        assert result['active_count'] == 2
        assert result['alert_summary'] == {"critical": 1, "warning": 1, "info": 0}
        assert len(result['sorted_alerts']) == 2
        # Critical alert should be first (severity sorting)
        assert result['sorted_alerts'][0]['component'] == 'security_layer'
        assert len(result['recommended_actions']) == 3
        assert result['alert_trend'] == 'increasing'
    
    def test_show_performance_alerts_no_alerts(self):
        """GREEN: Performance alerts handles zero active alerts"""
        dashboard = PerformanceMonitoringDashboard()
        alerts_data = {
            "active_alerts": [],
            "alert_history": [],
            "alert_summary": {"critical": 0, "warning": 0, "info": 0}
        }
        
        result = dashboard.show_performance_alerts(alerts_data)
        
        assert result['alerts_displayed'] is True
        assert result['active_count'] == 0
        assert len(result['sorted_alerts']) == 0
        assert 'Continue monitoring performance metrics' in result['recommended_actions']
        assert result['alert_trend'] == 'stable'
    
    def test_show_performance_alerts_invalid_input(self):
        """GREEN: Performance alerts validates input data"""
        dashboard = PerformanceMonitoringDashboard()
        
        # Test non-dict input
        with pytest.raises(ValueError, match="alerts_data must be a dictionary"):
            dashboard.show_performance_alerts("invalid")
        
        # Test missing active_alerts
        with pytest.raises(ValueError, match="must contain 'active_alerts'"):
            dashboard.show_performance_alerts({"alert_history": [], "alert_summary": {}})
        
        # Test non-list active_alerts
        with pytest.raises(ValueError, match="active_alerts must be a list"):
            dashboard.show_performance_alerts({
                "active_alerts": "invalid",
                "alert_history": [],
                "alert_summary": {}
            })
    
    def test_render_real_time_metrics_success(self):
        """GREEN: Real-time metrics rendering returns proper data structure"""
        dashboard = PerformanceMonitoringDashboard()
        real_time_config = {
            "refresh_interval_seconds": 5,
            "metrics_to_display": ["response_time", "throughput", "error_rate"],
            "visualization_type": "live_chart"
        }
        
        result = dashboard.render_real_time_metrics(real_time_config)
        
        # Verify structure
        assert result['metrics_rendered'] is True
        assert result['refresh_interval_seconds'] == 5
        assert result['metrics_count'] == 3
        assert result['metrics_to_display'] == ["response_time", "throughput", "error_rate"]
        assert result['visualization_type'] == 'live_chart'
        assert result['auto_refresh_enabled'] is True
    
    def test_render_real_time_metrics_invalid_input(self):
        """GREEN: Real-time metrics validates input data"""
        dashboard = PerformanceMonitoringDashboard()
        
        # Test non-dict input
        with pytest.raises(ValueError, match="real_time_config must be a dictionary"):
            dashboard.render_real_time_metrics("invalid")
        
        # Test missing refresh_interval_seconds
        with pytest.raises(ValueError, match="must contain 'refresh_interval_seconds'"):
            dashboard.render_real_time_metrics({
                "metrics_to_display": [],
                "visualization_type": "chart"
            })
        
        # Test invalid refresh_interval range (too low)
        with pytest.raises(ValueError, match="must be between 1 and 60"):
            dashboard.render_real_time_metrics({
                "refresh_interval_seconds": 0,
                "metrics_to_display": [],
                "visualization_type": "chart"
            })
        
        # Test invalid refresh_interval range (too high)
        with pytest.raises(ValueError, match="must be between 1 and 60"):
            dashboard.render_real_time_metrics({
                "refresh_interval_seconds": 61,
                "metrics_to_display": [],
                "visualization_type": "chart"
            })
        
        # Test non-numeric refresh_interval
        with pytest.raises(ValueError, match="must be a number"):
            dashboard.render_real_time_metrics({
                "refresh_interval_seconds": "invalid",
                "metrics_to_display": [],
                "visualization_type": "chart"
            })
        
        # Test non-list metrics_to_display
        with pytest.raises(ValueError, match="metrics_to_display must be a list"):
            dashboard.render_real_time_metrics({
                "refresh_interval_seconds": 5,
                "metrics_to_display": "invalid",
                "visualization_type": "chart"
            })


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
