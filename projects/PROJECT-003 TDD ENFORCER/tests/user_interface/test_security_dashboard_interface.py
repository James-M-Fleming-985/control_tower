"""
Security Dashboard Interface - TDD Iteration 15 REFACTOR Phase Tests
Layer: User Interface Layer
Phase: REFACTOR (Full Implementation Tests)
Created: 2025-10-03
Updated: 2025-10-05
"""

from src.user_interface.security_dashboard_interface_refactored import (
    SecurityDashboardInterface
)


class TestSecurityDashboardInterface:
    
    def test_render_security_overview_works_after_implementation(self):
        """REFACTOR: Security overview rendering should work with full implementation"""
        dashboard_interface = SecurityDashboardInterface()
        security_overview = {
            "user_id": "user_123",
            "session_security": {
                "authentication_level": "high",
                "session_status": "active",
                "expires_at": "2025-09-29T20:00:00Z"
            },
            "system_security": {
                "encryption_status": "enabled",
                "compliance_level": "high",
                "security_alerts": []
            }
        }
        
        # This should work - full implementation exists
        result = dashboard_interface.render_security_overview(security_overview)
        
        # Verify return structure
        assert result["overview_rendered"] is True
        assert result["user_id"] == "user_123"
        assert "session_status" in result
        assert "system_security_level" in result
        assert "active_alerts_count" in result
        assert "security_score" in result
    
    def test_display_audit_trail_works_after_implementation(self):
        """REFACTOR: Audit trail display should work with full implementation"""
        from datetime import datetime, timezone, timedelta
        
        dashboard_interface = SecurityDashboardInterface()
        
        # Use recent timestamps (within last hour)
        now = datetime.now(timezone.utc)
        recent_time_1 = (now - timedelta(minutes=30)).isoformat().replace('+00:00', 'Z')
        recent_time_2 = (now - timedelta(minutes=15)).isoformat().replace('+00:00', 'Z')
        
        audit_data = {
            "user_id": "user_123",
            "time_range": "last_24_hours",
            "audit_events": [
                {"timestamp": recent_time_1, "event": "authentication", "status": "success"},
                {"timestamp": recent_time_2, "event": "command_execution", "status": "success"}
            ]
        }
        
        # This should work - full implementation exists
        result = dashboard_interface.display_audit_trail(audit_data)
        
        # REFACTOR: Verify the implementation works correctly
        assert result["trail_displayed"] is True
        assert "user_id" in result
        assert "time_range" in result
        assert "total_events" in result  # Fixed key name
        assert result["total_events"] == 2
    
    def test_show_security_alerts_works_after_implementation(self):
        """REFACTOR: Security alerts display should work with full implementation"""
        dashboard_interface = SecurityDashboardInterface()
        alerts_data = {
            "active_alerts": [],
            "resolved_alerts": [
                {"id": "alert_001", "type": "permission_escalation", "resolved_at": "2025-09-29T09:00:00Z"}
            ],
            "alert_summary": {"high": 0, "medium": 0, "low": 0}
        }
        
        # This should work - full implementation exists
        result = dashboard_interface.show_security_alerts(alerts_data)
        
        # Verify return structure
        assert result["alerts_displayed"] is True
        assert "active_count" in result
        assert "resolved_count" in result
        assert result["active_count"] == 0
        assert result["resolved_count"] == 1
