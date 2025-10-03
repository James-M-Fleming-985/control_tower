"""
End-to-End Test - Performance Regression Detection Workflow
Tests complete user workflow: Performance monitoring → Alert detection → Action tracking
"""

import pytest
from performance_monitoring_dashboard import PerformanceMonitoringDashboard


class TestPerformanceRegressionE2E:
    """E2E test for performance regression detection workflow"""
    
    def test_performance_regression_detection_workflow(self):
        """
        E2E: Tech lead detects performance regression through dashboard
        
        Workflow:
        1. Launch performance monitoring dashboard
        2. View current performance metrics (healthy)
        3. Execute test suite with performance regression
        4. Performance degradation detected
        5. UI displays performance alert
        6. View performance trends (shows degradation)
        7. Drill into component performance
        """
        dashboard = PerformanceMonitoringDashboard()
        
        # Step 1-2: Initial healthy performance overview
        initial_performance = {
            "system_performance": {
                "average_response_time_ms": 150,
                "target_response_time_ms": 200,
                "performance_score": 0.95,
                "status": "healthy"
            },
            "component_performance": {
                "context_engine": {"response_time_ms": 145, "status": "healthy"},
                "security_protocol": {"response_time_ms": 155, "status": "healthy"}
            }
        }
        
        overview = dashboard.render_performance_overview(initial_performance)
        assert overview['system_status'] == 'healthy'
        assert overview['components_count'] == 2
        assert len(overview['components_over_threshold']) == 0
        
        # Step 3-4: Performance regression occurs
        degraded_performance = {
            "system_performance": {
                "average_response_time_ms": 225,
                "target_response_time_ms": 200,
                "performance_score": 0.65,
                "status": "degraded"
            },
            "component_performance": {
                "context_engine": {"response_time_ms": 235, "status": "warning"},
                "security_protocol": {"response_time_ms": 215, "status": "warning"}
            }
        }
        
        degraded_overview = dashboard.render_performance_overview(degraded_performance)
        assert degraded_overview['system_status'] == 'degraded'
        assert len(degraded_overview['components_over_threshold']) == 2
        assert 'context_engine' in degraded_overview['components_over_threshold']
        assert 'security_protocol' in degraded_overview['components_over_threshold']
        
        # Step 5: Performance alert triggered
        alert_data = {
            "active_alerts": [
                {
                    "component": "context_engine",
                    "metric": "response_time",
                    "value": 235,
                    "threshold": 200,
                    "severity": "warning"
                },
                {
                    "component": "security_protocol",
                    "metric": "response_time",
                    "value": 215,
                    "threshold": 200,
                    "severity": "warning"
                }
            ],
            "alert_history": [],
            "alert_summary": {"critical": 0, "warning": 2, "info": 0}
        }
        
        alerts = dashboard.show_performance_alerts(alert_data)
        assert alerts['active_count'] == 2
        assert 'Investigate' in alerts['recommended_actions'][1]
        assert alerts['alert_trend'] == 'increasing'
        
        # Step 6: View performance trends showing degradation
        trend_data = {
            "time_range": "last_6_hours",
            "metrics": [
                {"timestamp": "2025-10-03T12:00:00Z", "response_time_ms": 150},
                {"timestamp": "2025-10-03T14:00:00Z", "response_time_ms": 180},
                {"timestamp": "2025-10-03T16:00:00Z", "response_time_ms": 210},
                {"timestamp": "2025-10-03T18:00:00Z", "response_time_ms": 225}
            ],
            "target_line": 200
        }
        
        trends = dashboard.display_performance_trends(trend_data)
        assert trends['trend_direction'] == 'degrading'
        assert trends['avg_response_time_ms'] == 191.25
        assert trends['max_response_time_ms'] == 225
        
        # Step 7: Real-time monitoring configured
        realtime_config = {
            "refresh_interval_seconds": 10,
            "metrics_to_display": [
                "response_time",
                "throughput",
                "error_rate",
                "context_engine_performance"
            ],
            "visualization_type": "live_chart"
        }
        
        realtime = dashboard.render_real_time_metrics(realtime_config)
        assert realtime['metrics_rendered'] is True
        assert realtime['refresh_interval_seconds'] == 10
        assert realtime['metrics_count'] == 4
        assert realtime['auto_refresh_enabled'] is True
        
        # Workflow validation complete
        print("✓ E2E Workflow: Performance regression detected and monitored")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
