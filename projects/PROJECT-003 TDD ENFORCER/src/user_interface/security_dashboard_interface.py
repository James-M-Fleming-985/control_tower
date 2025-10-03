"""
Security Dashboard Interface - TDD Iteration 15
Layer: User Interface Layer
Phase: GREEN (Minimal Implementation)
Created: 2025-10-03

This module provides the Security Dashboard Interface for displaying security status,
audit trails, and security alerts.
"""

from typing import Dict, Any


class SecurityDashboardInterface:
    """
    User interface component for security dashboard visualization.
    
    Provides methods for:
    - Rendering security overview (session + system security)
    - Displaying audit trail events
    - Showing security alerts
    """
    
    def render_security_overview(self, security_overview: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render security overview with session and system security status.
        
        Args:
            security_overview: Dictionary containing user_id, session_security, and system_security
                              with authentication levels, encryption status, and compliance info
        
        Returns:
            Dictionary with overview_rendered flag, security status, alerts, and display data
        
        Raises:
            ValueError: If security_overview is invalid or missing required fields
        """
        # Validate required fields
        if not isinstance(security_overview, dict):
            raise ValueError("security_overview must be a dictionary")
        if 'user_id' not in security_overview:
            raise ValueError("security_overview must contain 'user_id'")
        if 'session_security' not in security_overview:
            raise ValueError("security_overview must contain 'session_security'")
        if 'system_security' not in security_overview:
            raise ValueError("security_overview must contain 'system_security'")
        
        # Extract data
        user_id = security_overview['user_id']
        session_sec = security_overview['session_security']
        system_sec = security_overview['system_security']
        
        # Validate nested fields
        required_session = ['authentication_level', 'session_status', 'expires_at']
        for field in required_session:
            if field not in session_sec:
                raise ValueError(f"session_security must contain '{field}'")
        
        required_system = ['encryption_status', 'compliance_level', 'security_alerts']
        for field in required_system:
            if field not in system_sec:
                raise ValueError(f"system_security must contain '{field}'")
        
        # Calculate security score (0.0-1.0)
        auth_score = {'high': 0.4, 'medium': 0.2, 'low': 0.1}.get(
            session_sec['authentication_level'], 0.0
        )
        encryption_score = 0.3 if system_sec['encryption_status'] == 'enabled' else 0.0
        compliance_score = {'high': 0.3, 'medium': 0.15, 'low': 0.05}.get(
            system_sec['compliance_level'], 0.0
        )
        security_score = auth_score + encryption_score + compliance_score
        
        # Count active alerts
        active_alerts_count = len(system_sec['security_alerts'])
        
        # Determine system security level
        if (system_sec['compliance_level'] == 'high' and 
            system_sec['encryption_status'] == 'enabled'):
            system_security_level = 'high'
        elif system_sec['compliance_level'] == 'medium':
            system_security_level = 'medium'
        else:
            system_security_level = 'low'
        
        return {
            'overview_rendered': True,
            'user_id': user_id,
            'session_status': session_sec['session_status'],
            'system_security_level': system_security_level,
            'active_alerts_count': active_alerts_count,
            'security_score': security_score,
            'display_data': {
                'authentication': session_sec['authentication_level'],
                'encryption': system_sec['encryption_status'],
                'compliance': system_sec['compliance_level'],
                'session_expires': session_sec['expires_at']
            }
        }
    
    def display_audit_trail(self, audit_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Display audit trail with user events over specified time range.
        
        Args:
            audit_data: Dictionary containing user_id, time_range, and audit_events list
                       with timestamps, event types, and status information
        
        Returns:
            Dictionary with trail_displayed flag, event count, filtered events, and summary
        
        Raises:
            ValueError: If audit_data is invalid or missing required fields
        """
        # Validate required fields
        if not isinstance(audit_data, dict):
            raise ValueError("audit_data must be a dictionary")
        if 'user_id' not in audit_data:
            raise ValueError("audit_data must contain 'user_id'")
        if 'time_range' not in audit_data:
            raise ValueError("audit_data must contain 'time_range'")
        if 'audit_events' not in audit_data:
            raise ValueError("audit_data must contain 'audit_events'")
        
        # Validate time_range
        valid_ranges = ['last_hour', 'last_24_hours', 'last_week', 'last_month', 'all']
        if audit_data['time_range'] not in valid_ranges:
            raise ValueError(f"time_range must be one of {valid_ranges}")
        
        # Extract data
        user_id = audit_data['user_id']
        time_range = audit_data['time_range']
        audit_events = audit_data['audit_events']
        
        # Validate events structure
        for event in audit_events:
            if not isinstance(event, dict):
                raise ValueError("Each audit_event must be a dictionary")
            required_event_fields = ['timestamp', 'event', 'status']
            for field in required_event_fields:
                if field not in event:
                    raise ValueError(f"Each audit_event must contain '{field}'")
        
        # For GREEN phase: accept all events if time_range='all' or 'last_24_hours'
        filtered_events = audit_events
        
        # Count events
        total_events = len(filtered_events)
        
        # Generate event summary
        event_summary = {}
        for event in filtered_events:
            event_type = event['event']
            event_summary[event_type] = event_summary.get(event_type, 0) + 1
        
        # Pagination
        page_size = 20
        total_pages = (total_events + page_size - 1) // page_size if total_events > 0 else 1
        
        return {
            'trail_displayed': True,
            'user_id': user_id,
            'time_range': time_range,
            'total_events': total_events,
            'filtered_events': filtered_events,
            'event_summary': event_summary,
            'pagination': {
                'page_size': page_size,
                'current_page': 1,
                'total_pages': total_pages
            }
        }
    
    def show_security_alerts(self, alerts_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Show security alerts with active and resolved alert information.
        
        Args:
            alerts_data: Dictionary containing active_alerts, resolved_alerts lists,
                        and alert_summary with severity counts
        
        Returns:
            Dictionary with alerts_displayed flag, alert counts, prioritized alerts, and actions
        
        Raises:
            ValueError: If alerts_data is invalid or missing required fields
        """
        # Validate required fields
        if not isinstance(alerts_data, dict):
            raise ValueError("alerts_data must be a dictionary")
        if 'active_alerts' not in alerts_data:
            raise ValueError("alerts_data must contain 'active_alerts'")
        if 'resolved_alerts' not in alerts_data:
            raise ValueError("alerts_data must contain 'resolved_alerts'")
        if 'alert_summary' not in alerts_data:
            raise ValueError("alerts_data must contain 'alert_summary'")
        
        # Validate alert_summary structure
        alert_summary = alerts_data['alert_summary']
        required_severity = ['high', 'medium', 'low']
        for severity in required_severity:
            if severity not in alert_summary:
                raise ValueError(f"alert_summary must contain '{severity}'")
        
        # Extract data
        active_alerts = alerts_data['active_alerts']
        resolved_alerts = alerts_data['resolved_alerts']
        
        # Count alerts
        active_count = len(active_alerts)
        resolved_count = len(resolved_alerts)
        
        # Prioritize alerts (high → medium → low)
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        prioritized_alerts = sorted(
            active_alerts,
            key=lambda x: severity_order.get(x.get('severity', 'medium'), 1)
        )
        
        # Copy severity breakdown
        severity_breakdown = dict(alert_summary)
        
        # Generate recommended actions
        if active_count == 0:
            recommended_actions = ['Continue monitoring security status']
        else:
            recommended_actions = [
                'Review active alerts',
                'Investigate high priority items',
                'Update security policies'
            ]
        
        # Determine alert trend
        if active_count < resolved_count:
            alert_trend = 'improving'
        elif active_count == resolved_count:
            alert_trend = 'stable'
        else:
            alert_trend = 'degrading'
        
        return {
            'alerts_displayed': True,
            'active_count': active_count,
            'resolved_count': resolved_count,
            'prioritized_alerts': prioritized_alerts,
            'severity_breakdown': severity_breakdown,
            'recommended_actions': recommended_actions,
            'alert_trend': alert_trend
        }
