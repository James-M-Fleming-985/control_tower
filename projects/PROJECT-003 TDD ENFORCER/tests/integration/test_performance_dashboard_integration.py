"""
UI Layer Integration Test - Performance Dashboard ↔ Verification Service
Tests integration between Performance Monitoring Dashboard and Business Logic
"""

import pytest
from unittest.mock import Mock, patch
from performance_monitoring_dashboard import PerformanceMonitoringDashboard


class TestPerformanceDashboardIntegration:
    """Integration tests for Performance Dashboard with Business Logic layer"""
    
    def test_performance_dashboard_with_verification_service(self):
        """Test performance dashboard receives data from verification service"""
        dashboard = PerformanceMonitoringDashboard()
        
        # Simulate verification service response
        verification_data = {
            "system_performance": {
                "average_response_time_ms": 180,
                "target_response_time_ms": 200,
                "performance_score": 0.90,
                "status": "healthy"
            },
            "component_performance": {
                "context_engine": {"response_time_ms": 175, "status": "healthy"},
                "security_protocol": {"response_time_ms": 185, "status": "healthy"},
                "test_repository": {"response_time_ms": 190, "status": "healthy"}
            }
        }
        
        result = dashboard.render_performance_overview(verification_data)
        
        # Verify integration
        assert result['overview_rendered'] is True
        assert result['system_status'] == 'healthy'
        assert result['performance_score'] == 0.90
        assert result['components_count'] == 3
        assert len(result['components_over_threshold']) == 0  # All under 200ms
    
    def test_performance_trends_from_business_logic(self):
        """Test performance trends integration with business logic metrics"""
        dashboard = PerformanceMonitoringDashboard()
        
        # Simulate business logic trend data
        trends_data = {
            "time_range": "last_24_hours",
            "metrics": [
                {"timestamp": "2025-10-03T10:00:00Z", "response_time_ms": 200},
                {"timestamp": "2025-10-03T14:00:00Z", "response_time_ms": 185},
                {"timestamp": "2025-10-03T18:00:00Z", "response_time_ms": 170}
            ],
            "target_line": 200
        }
        
        result = dashboard.display_performance_trends(trends_data)
        
        # Verify trend direction calculation
        assert result['trends_displayed'] is True
        assert result['trend_direction'] == 'improving'  # Performance getting better
        assert result['avg_response_time_ms'] == 185.0
        assert result['min_response_time_ms'] == 170
        assert result['max_response_time_ms'] == 200
    
    def test_performance_alerts_from_security_protocol(self):
        """Test performance alerts integration with security protocol events"""
        dashboard = PerformanceMonitoringDashboard()
        
        # Simulate security protocol generating performance alerts
        alerts_data = {
            "active_alerts": [
                {
                    "component": "security_protocol",
                    "metric": "encryption_time",
                    "value": 250,
                    "threshold": 200,
                    "severity": "critical"
                }
            ],
            "alert_history": [],
            "alert_summary": {"critical": 1, "warning": 0, "info": 0}
        }
        
        result = dashboard.show_performance_alerts(alerts_data)
        
        # Verify alert processing
        assert result['alerts_displayed'] is True
        assert result['active_count'] == 1
        assert 'Investigate' in result['recommended_actions'][0]
        assert result['sorted_alerts'][0]['severity'] == 'critical'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
