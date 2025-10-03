"""
Test Suite for Security Dashboard Interface - TDD Iteration 15 REFACTOR Phase
Tests enhanced functionality including:
- Visual indicators and icons
- Actual time-based filtering
- Event enrichment and anomaly detection
- Alert deduplication and grouping
"""

import pytest
from datetime import datetime, timedelta
from security_dashboard_interface_refactored import SecurityDashboardInterface


class TestSecurityDashboardRefactored:
    """Test suite for REFACTOR phase enhancements."""
    
    @pytest.fixture
    def dashboard(self):
        """Create dashboard interface instance."""
        return SecurityDashboardInterface()
    
    # ========================================================================
    # SECURITY OVERVIEW TESTS
    # ========================================================================
    
    def test_render_security_overview_with_visual_indicators(self, dashboard):
        """Test security overview rendering with visual indicators."""
        security_overview = {
            'user_id': 'user123',
            'session_security': {
                'authentication_level': 'high',
                'session_status': 'active',
                'expires_at': '2025-10-03T15:00:00Z'
            },
            'system_security': {
                'encryption_status': 'enabled',
                'compliance_level': 'high',
                'security_alerts': []
            },
            'security_history': [0.8, 0.85, 0.9]
        }
        
        result = dashboard.render_security_overview(security_overview)
        
        # Verify basic fields
        assert result['overview_rendered'] is True
        assert result['user_id'] == 'user123'
        assert result['security_score'] == 1.0
        
        # Verify REFACTOR enhancements
        assert 'security_icon' in result
        assert result['security_icon'] == '🟢'  # high security
        assert 'auth_icon' in result
        assert result['auth_icon'] == '🔐'  # high auth
        assert 'encryption_icon' in result
        assert result['encryption_icon'] == '🔒'  # enabled
        
        # Verify score trend
        assert 'score_trend' in result
        assert result['score_trend'] in ['improving', 'stable', 'degrading']
        
        # Verify score breakdown
        assert 'score_breakdown' in result
        assert result['score_breakdown']['authentication'] == 0.4
        assert result['score_breakdown']['encryption'] == 0.3
        assert result['score_breakdown']['compliance'] == 0.3
        assert result['score_breakdown']['total'] == 1.0
        
        # Verify recommendations
        assert 'recommendations' in result
        assert isinstance(result['recommendations'], list)
        assert len(result['recommendations']) > 0
        
        # Verify session warning (None if not expiring soon)
        assert 'session_warning' in result
    
    def test_security_score_trend_calculation(self, dashboard):
        """Test security score trend calculation."""
        # Improving trend
        result_improving = dashboard._calculate_score_trend(0.9, [0.6, 0.65, 0.7])
        assert result_improving == 'improving'
        
        # Stable trend
        result_stable = dashboard._calculate_score_trend(0.7, [0.68, 0.69, 0.71])
        assert result_stable == 'stable'
        
        # Degrading trend
        result_degrading = dashboard._calculate_score_trend(0.5, [0.8, 0.85, 0.9])
        assert result_degrading == 'degrading'
        
        # No history
        result_no_history = dashboard._calculate_score_trend(0.8, [])
        assert result_no_history == 'stable'
    
    def test_session_expiration_warning(self, dashboard):
        """Test session expiration warning for sessions expiring soon."""
        # Session expiring in 30 minutes
        future_time = datetime.now() + timedelta(minutes=30)
        expires_at = future_time.isoformat() + 'Z'
        
        warning = dashboard._check_session_expiration(expires_at)
        
        if warning:  # Warning should be present if <1 hour
            assert warning['warning'] is True
            assert 'minutes_remaining' in warning
            assert warning['minutes_remaining'] < 60
            assert 'message' in warning
        
        # Session expiring in 2 hours (no warning)
        future_time_safe = datetime.now() + timedelta(hours=2)
        expires_at_safe = future_time_safe.isoformat() + 'Z'
        
        warning_safe = dashboard._check_session_expiration(expires_at_safe)
        assert warning_safe is None
    
    def test_security_recommendations_generation(self, dashboard):
        """Test security recommendations based on security posture."""
        # Low security score scenario
        low_security = {
            'user_id': 'user123',
            'session_security': {
                'authentication_level': 'low',
                'session_status': 'active',
                'expires_at': '2025-10-03T15:00:00Z'
            },
            'system_security': {
                'encryption_status': 'disabled',
                'compliance_level': 'low',
                'security_alerts': [
                    {'type': 'alert1'},
                    {'type': 'alert2'},
                    {'type': 'alert3'},
                    {'type': 'alert4'},
                    {'type': 'alert5'},
                    {'type': 'alert6'}
                ]
            }
        }
        
        recommendations = dashboard._generate_security_recommendations(low_security, 0.2)
        
        assert len(recommendations) > 0
        assert any('authentication' in rec.lower() for rec in recommendations)
        assert any('encryption' in rec.lower() for rec in recommendations)
        assert any('compliance' in rec.lower() for rec in recommendations)
        assert any('alert' in rec.lower() for rec in recommendations)
    
    # ========================================================================
    # AUDIT TRAIL TESTS
    # ========================================================================
    
    def test_display_audit_trail_with_time_filtering(self, dashboard):
        """Test audit trail with actual time-based filtering."""
        current_time = datetime.now()
        
        # Create events at different times
        events = [
            {
                'timestamp': (current_time - timedelta(minutes=30)).isoformat() + 'Z',
                'event': 'authentication',
                'status': 'success'
            },
            {
                'timestamp': (current_time - timedelta(hours=2)).isoformat() + 'Z',
                'event': 'data_access',
                'status': 'success'
            },
            {
                'timestamp': (current_time - timedelta(days=2)).isoformat() + 'Z',
                'event': 'command_execution',
                'status': 'success'
            },
            {
                'timestamp': (current_time - timedelta(days=10)).isoformat() + 'Z',
                'event': 'configuration_change',
                'status': 'success'
            }
        ]
        
        audit_data = {
            'user_id': 'user123',
            'time_range': 'last_24_hours',
            'audit_events': events,
            'current_time': current_time.isoformat() + 'Z'
        }
        
        result = dashboard.display_audit_trail(audit_data)
        
        # Verify filtering worked
        assert result['trail_displayed'] is True
        assert result['total_events'] == 2  # Only events within last 24 hours
        
        # Verify enriched events
        assert 'enriched_events' in result
        assert len(result['enriched_events']) == 2
        
        # Check enrichment fields
        for enriched in result['enriched_events']:
            assert 'event_icon' in enriched
            assert 'relative_time' in enriched
            assert 'risk_level' in enriched
        
        # Verify anomaly detection
        assert 'anomalies' in result
        
        # Verify additional REFACTOR fields
        assert 'available_filters' in result
        assert 'export_options' in result
    
    def test_time_filtering_all_ranges(self, dashboard):
        """Test all time range filtering options."""
        current_time = datetime.now()
        
        events = [
            {'timestamp': (current_time - timedelta(minutes=30)).isoformat() + 'Z',
             'event': 'event1', 'status': 'success'},
            {'timestamp': (current_time - timedelta(hours=12)).isoformat() + 'Z',
             'event': 'event2', 'status': 'success'},
            {'timestamp': (current_time - timedelta(days=3)).isoformat() + 'Z',
             'event': 'event3', 'status': 'success'},
            {'timestamp': (current_time - timedelta(days=15)).isoformat() + 'Z',
             'event': 'event4', 'status': 'success'}
        ]
        
        # Test last_hour
        filtered_hour = dashboard._filter_by_time_range(
            events, 'last_hour', current_time.isoformat() + 'Z'
        )
        assert len(filtered_hour) == 1
        
        # Test last_24_hours
        filtered_day = dashboard._filter_by_time_range(
            events, 'last_24_hours', current_time.isoformat() + 'Z'
        )
        assert len(filtered_day) == 2
        
        # Test last_week
        filtered_week = dashboard._filter_by_time_range(
            events, 'last_week', current_time.isoformat() + 'Z'
        )
        assert len(filtered_week) == 3
        
        # Test last_month
        filtered_month = dashboard._filter_by_time_range(
            events, 'last_month', current_time.isoformat() + 'Z'
        )
        assert len(filtered_month) == 4
        
        # Test all
        filtered_all = dashboard._filter_by_time_range(
            events, 'all', current_time.isoformat() + 'Z'
        )
        assert len(filtered_all) == 4
    
    def test_event_enrichment(self, dashboard):
        """Test event enrichment with icons and relative time."""
        current_time = datetime.now()
        
        event = {
            'timestamp': (current_time - timedelta(hours=2)).isoformat() + 'Z',
            'event': 'authentication',
            'status': 'success'
        }
        
        enriched = dashboard._enrich_event(event, current_time.isoformat() + 'Z')
        
        assert 'event_icon' in enriched
        assert enriched['event_icon'] == '🔐'  # authentication icon
        assert 'relative_time' in enriched
        assert 'hour' in enriched['relative_time'].lower()
        assert 'risk_level' in enriched
        assert enriched['risk_level'] in ['low', 'medium', 'high']
    
    def test_anomaly_detection_failed_auth(self, dashboard):
        """Test anomaly detection for failed authentication attempts."""
        events = [
            {'timestamp': '2025-10-03T10:00:00Z', 'event': 'authentication',
             'status': 'failure'},
            {'timestamp': '2025-10-03T10:01:00Z', 'event': 'authentication',
             'status': 'failure'},
            {'timestamp': '2025-10-03T10:02:00Z', 'event': 'authentication',
             'status': 'failure'},
            {'timestamp': '2025-10-03T10:03:00Z', 'event': 'data_access',
             'status': 'success'}
        ]
        
        anomalies = dashboard._detect_anomalies(events, 'user123')
        
        # Should detect multiple failed authentication attempts
        assert len(anomalies) > 0
        assert any(a['type'] == 'failed_authentication' for a in anomalies)
        assert any(a['type'] == 'multiple_failed_auth' for a in anomalies)
    
    # ========================================================================
    # SECURITY ALERTS TESTS
    # ========================================================================
    
    def test_show_security_alerts_with_deduplication(self, dashboard):
        """Test security alerts with deduplication."""
        alerts_data = {
            'active_alerts': [
                {'type': 'permission_escalation', 'severity': 'high',
                 'timestamp': '2025-10-03T10:00:00Z'},
                {'type': 'permission_escalation', 'severity': 'high',
                 'timestamp': '2025-10-03T10:05:00Z'},  # duplicate
                {'type': 'unauthorized_access', 'severity': 'medium',
                 'timestamp': '2025-10-03T10:10:00Z'}
            ],
            'resolved_alerts': [
                {'type': 'policy_violation', 'severity': 'low'}
            ],
            'alert_summary': {
                'high': 2,
                'medium': 1,
                'low': 0
            }
        }
        
        result = dashboard.show_security_alerts(alerts_data)
        
        # Verify basic fields
        assert result['alerts_displayed'] is True
        assert result['active_count'] == 3
        
        # Verify REFACTOR enhancements
        assert 'deduplicated_alerts' in result
        assert len(result['deduplicated_alerts']) == 2  # 2 unique alert types
        
        # Check occurrence count in deduplicated alerts
        perm_esc_alert = next(
            (a for a in result['deduplicated_alerts']
             if a['type'] == 'permission_escalation'), None
        )
        assert perm_esc_alert is not None
        assert perm_esc_alert['occurrence_count'] == 2
        
        # Verify grouping
        assert 'grouped_by_severity' in result
        assert 'high' in result['grouped_by_severity']
        assert len(result['grouped_by_severity']['high']) == 2
        
        assert 'grouped_by_type' in result
        assert 'permission_escalation' in result['grouped_by_type']
        
        # Verify remediation steps
        assert 'remediation_steps' in result
        assert 'permission_escalation' in result['remediation_steps']
        assert isinstance(result['remediation_steps']['permission_escalation'], list)
        
        # Verify alert velocity
        assert 'alert_velocity' in result
        assert 'resolution_rate' in result['alert_velocity']
    
    def test_alert_grouping_by_severity_and_type(self, dashboard):
        """Test alert grouping functionality."""
        alerts = [
            {'type': 'type1', 'severity': 'high'},
            {'type': 'type1', 'severity': 'medium'},
            {'type': 'type2', 'severity': 'high'},
            {'type': 'type2', 'severity': 'low'}
        ]
        
        # Group by severity
        by_severity = dashboard._group_alerts(alerts, 'severity')
        assert 'high' in by_severity
        assert len(by_severity['high']) == 2
        assert 'medium' in by_severity
        assert len(by_severity['medium']) == 1
        
        # Group by type
        by_type = dashboard._group_alerts(alerts, 'type')
        assert 'type1' in by_type
        assert len(by_type['type1']) == 2
        assert 'type2' in by_type
        assert len(by_type['type2']) == 2
    
    def test_remediation_steps_generation(self, dashboard):
        """Test remediation steps for different alert types."""
        alerts = [
            {'type': 'permission_escalation', 'severity': 'high'},
            {'type': 'unauthorized_access', 'severity': 'high'},
            {'type': 'unknown_type', 'severity': 'medium'}
        ]
        
        steps = dashboard._generate_remediation_steps(alerts)
        
        assert 'permission_escalation' in steps
        assert len(steps['permission_escalation']) > 0
        assert 'unauthorized_access' in steps
        assert len(steps['unauthorized_access']) > 0
        assert 'unknown_type' in steps
    
    def test_alert_velocity_calculation(self, dashboard):
        """Test alert velocity metrics."""
        active_alerts = [{'type': 'alert1'}, {'type': 'alert2'}]
        resolved_alerts = [
            {'type': 'alert3'},
            {'type': 'alert4'},
            {'type': 'alert5'}
        ]
        
        velocity = dashboard._calculate_alert_velocity(active_alerts, resolved_alerts)
        
        assert velocity['active_count'] == 2
        assert velocity['resolved_count'] == 3
        assert velocity['resolution_rate'] == 0.6  # 3 / (2 + 3)
        assert velocity['status'] == 'healthy'  # more resolved than active
        
        # Test attention needed scenario
        velocity_bad = dashboard._calculate_alert_velocity(
            [{'type': 'a'}, {'type': 'b'}, {'type': 'c'}],
            [{'type': 'd'}]
        )
        assert velocity_bad['status'] == 'attention_needed'
    
    # ========================================================================
    # INTEGRATION TESTS
    # ========================================================================
    
    def test_full_workflow_security_overview_to_alerts(self, dashboard):
        """Test complete workflow from overview to alerts."""
        # Step 1: Render security overview
        security_overview = {
            'user_id': 'user123',
            'session_security': {
                'authentication_level': 'high',
                'session_status': 'active',
                'expires_at': '2025-10-03T15:00:00Z'
            },
            'system_security': {
                'encryption_status': 'enabled',
                'compliance_level': 'high',
                'security_alerts': [
                    {'type': 'permission_escalation', 'severity': 'high'}
                ]
            }
        }
        
        overview_result = dashboard.render_security_overview(security_overview)
        assert overview_result['overview_rendered'] is True
        assert overview_result['active_alerts_count'] == 1
        
        # Step 2: Display audit trail
        current_time = datetime.now()
        audit_data = {
            'user_id': 'user123',
            'time_range': 'last_24_hours',
            'audit_events': [
                {
                    'timestamp': current_time.isoformat() + 'Z',
                    'event': 'authentication',
                    'status': 'success'
                }
            ],
            'current_time': current_time.isoformat() + 'Z'
        }
        
        trail_result = dashboard.display_audit_trail(audit_data)
        assert trail_result['trail_displayed'] is True
        
        # Step 3: Show security alerts
        alerts_data = {
            'active_alerts': [
                {'type': 'permission_escalation', 'severity': 'high'}
            ],
            'resolved_alerts': [],
            'alert_summary': {'high': 1, 'medium': 0, 'low': 0}
        }
        
        alerts_result = dashboard.show_security_alerts(alerts_data)
        assert alerts_result['alerts_displayed'] is True
        assert alerts_result['alert_trend'] == 'degrading'  # 1 active, 0 resolved


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
