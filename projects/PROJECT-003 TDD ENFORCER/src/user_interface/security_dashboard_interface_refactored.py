"""
Security Dashboard Interface - TDD Iteration 15
Layer: User Interface Layer
Phase: REFACTOR (Enhanced Implementation)
Created: 2025-10-03

This module provides the enhanced Security Dashboard Interface with:
- Visual indicators and icons
- Actual time-based filtering
- Event enrichment and anomaly detection
- Alert deduplication and grouping
- Performance optimizations
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import time


class SecurityDashboardInterface:
    """
    Enhanced user interface component for security dashboard visualization.
    
    Provides methods for:
    - Rendering security overview with visual indicators and recommendations
    - Displaying audit trail with actual time filtering and enrichment
    - Showing security alerts with deduplication and grouping
    """
    
    def __init__(self):
        """Initialize security dashboard with caching."""
        self._security_cache: Dict[str, Any] = {}
        self._cache_ttl = 60  # seconds
    
    # ============================================================================
    # SECURITY OVERVIEW METHODS
    # ============================================================================
    
    def render_security_overview(self, security_overview: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render enhanced security overview with visual indicators and recommendations.
        
        Args:
            security_overview: Dictionary containing user_id, session_security, and system_security
                              Optional: security_history for trend analysis
        
        Returns:
            Dictionary with overview data, visual indicators, trends, and recommendations
        
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
        security_history = security_overview.get('security_history', [])
        
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
        
        # REFACTOR: Add visual indicators
        security_icon = self._get_security_icon(system_security_level)
        auth_icon = self._get_auth_icon(session_sec['authentication_level'])
        encryption_icon = "🔒" if system_sec['encryption_status'] == 'enabled' else "🔓"
        
        # REFACTOR: Calculate score trend
        score_trend = self._calculate_score_trend(security_score, security_history)
        
        # REFACTOR: Generate score breakdown
        score_breakdown = {
            'authentication': auth_score,
            'encryption': encryption_score,
            'compliance': compliance_score,
            'total': security_score
        }
        
        # REFACTOR: Generate security recommendations
        recommendations = self._generate_security_recommendations(
            security_overview, security_score
        )
        
        # REFACTOR: Check session expiration
        session_warning = self._check_session_expiration(session_sec['expires_at'])
        
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
            },
            # REFACTOR enhancements
            'security_icon': security_icon,
            'auth_icon': auth_icon,
            'encryption_icon': encryption_icon,
            'score_trend': score_trend,
            'score_breakdown': score_breakdown,
            'recommendations': recommendations,
            'session_warning': session_warning
        }
    
    def _get_security_icon(self, security_level: str) -> str:
        """Map security level to visual icon."""
        icons = {
            'high': '🟢',
            'medium': '🟡',
            'low': '🔴'
        }
        return icons.get(security_level, '⚪')
    
    def _get_auth_icon(self, auth_level: str) -> str:
        """Map authentication level to visual icon."""
        icons = {
            'high': '🔐',
            'medium': '🔑',
            'low': '🔓'
        }
        return icons.get(auth_level, '❓')
    
    def _calculate_score_trend(self, current_score: float, history: List[float]) -> str:
        """Determine security score trend from history."""
        if not history or len(history) < 2:
            return 'stable'
        
        # Calculate average of recent history
        avg_history = sum(history[-3:]) / len(history[-3:])
        
        if current_score > avg_history + 0.1:
            return 'improving'
        elif current_score < avg_history - 0.1:
            return 'degrading'
        else:
            return 'stable'
    
    def _generate_security_recommendations(
        self, security_overview: Dict[str, Any], security_score: float
    ) -> List[str]:
        """Generate actionable security recommendations."""
        recommendations = []
        
        session_sec = security_overview['session_security']
        system_sec = security_overview['system_security']
        
        # Low security score
        if security_score < 0.5:
            recommendations.append("⚠️ Critical: Security score below acceptable threshold")
        
        # Authentication level
        if session_sec['authentication_level'] == 'low':
            recommendations.append("🔐 Enable multi-factor authentication for better security")
        elif session_sec['authentication_level'] == 'medium':
            recommendations.append("🔑 Consider upgrading to high-security authentication")
        
        # Encryption status
        if system_sec['encryption_status'] != 'enabled':
            recommendations.append("🔒 Enable encryption to protect sensitive data")
        
        # Compliance level
        if system_sec['compliance_level'] == 'low':
            recommendations.append("📋 Review and improve compliance policies")
        elif system_sec['compliance_level'] == 'medium':
            recommendations.append("✅ Maintain current compliance standards")
        
        # Active alerts
        alert_count = len(system_sec['security_alerts'])
        if alert_count > 5:
            recommendations.append(f"🚨 Address {alert_count} active security alerts")
        elif alert_count > 0:
            recommendations.append(f"⚡ Review {alert_count} security alerts")
        
        # Default recommendation
        if not recommendations:
            recommendations.append("✨ Security posture is strong - continue monitoring")
        
        return recommendations
    
    def _check_session_expiration(self, expires_at: str) -> Optional[Dict[str, Any]]:
        """Check if session is expiring soon."""
        try:
            expiry_time = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            current_time = datetime.now(expiry_time.tzinfo)
            time_remaining = expiry_time - current_time
            
            # Warn if less than 1 hour remaining
            if time_remaining.total_seconds() < 3600 and time_remaining.total_seconds() > 0:
                minutes_remaining = int(time_remaining.total_seconds() / 60)
                return {
                    'warning': True,
                    'message': f"Session expires in {minutes_remaining} minutes",
                    'minutes_remaining': minutes_remaining,
                    'expires_at': expires_at
                }
        except (ValueError, AttributeError):
            pass
        
        return None
    
    # ============================================================================
    # AUDIT TRAIL METHODS
    # ============================================================================
    
    def display_audit_trail(self, audit_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Display enhanced audit trail with actual time filtering and enrichment.
        
        Args:
            audit_data: Dictionary containing user_id, time_range, and audit_events list
                       Optional: current_time for testing
        
        Returns:
            Dictionary with trail data, enriched events, and anomaly detection
        
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
        current_time = audit_data.get('current_time')
        
        # Validate events structure
        for event in audit_events:
            if not isinstance(event, dict):
                raise ValueError("Each audit_event must be a dictionary")
            required_event_fields = ['timestamp', 'event', 'status']
            for field in required_event_fields:
                if field not in event:
                    raise ValueError(f"Each audit_event must contain '{field}'")
        
        # REFACTOR: Implement actual time-based filtering
        filtered_events = self._filter_by_time_range(
            audit_events, time_range, current_time
        )
        
        # REFACTOR: Enrich events with icons and relative time
        enriched_events = [self._enrich_event(event, current_time) for event in filtered_events]
        
        # Count events
        total_events = len(filtered_events)
        
        # Generate event summary
        event_summary = {}
        for event in filtered_events:
            event_type = event['event']
            event_summary[event_type] = event_summary.get(event_type, 0) + 1
        
        # REFACTOR: Detect anomalies
        anomalies = self._detect_anomalies(filtered_events, user_id)
        
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
            },
            # REFACTOR enhancements
            'enriched_events': enriched_events,
            'anomalies': anomalies,
            'available_filters': ['event_type', 'status', 'time_range'],
            'export_options': ['csv', 'json']
        }
    
    def _filter_by_time_range(
        self, events: List[Dict], time_range: str, current_time: Optional[str] = None
    ) -> List[Dict]:
        """Filter events based on time range."""
        if time_range == 'all':
            return events
        
        # Parse current time or use now (ensure timezone-aware)
        if current_time:
            try:
                now = datetime.fromisoformat(current_time.replace('Z', '+00:00'))
            except ValueError:
                from datetime import timezone
                now = datetime.now(timezone.utc)
        else:
            from datetime import timezone
            now = datetime.now(timezone.utc)
        
        # Calculate cutoff time
        time_deltas = {
            'last_hour': timedelta(hours=1),
            'last_24_hours': timedelta(days=1),
            'last_week': timedelta(days=7),
            'last_month': timedelta(days=30)
        }
        
        cutoff = now - time_deltas.get(time_range, timedelta(days=1))
        
        # Filter events
        filtered = []
        for event in events:
            try:
                event_time = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
                if event_time >= cutoff:
                    filtered.append(event)
            except (ValueError, AttributeError):
                # Include events with invalid timestamps in 'all' range
                pass
        
        return filtered
    
    def _enrich_event(self, event: Dict[str, Any], current_time: Optional[str] = None) -> Dict[str, Any]:
        """Add computed fields to event."""
        enriched = dict(event)
        
        # Add event icon
        event_icons = {
            'authentication': '🔐',
            'login': '🔐',
            'logout': '🚪',
            'command_execution': '⚙️',
            'data_access': '📁',
            'file_access': '📁',
            'api_call': '🔌',
            'configuration_change': '⚙️'
        }
        event_type = event.get('event', '').lower()
        enriched['event_icon'] = event_icons.get(event_type, '📝')
        
        # Add relative timestamp (ensure timezone-aware)
        try:
            if current_time:
                now = datetime.fromisoformat(current_time.replace('Z', '+00:00'))
            else:
                from datetime import timezone
                now = datetime.now(timezone.utc)
            
            event_time = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
            delta = now - event_time
            
            if delta.total_seconds() < 60:
                enriched['relative_time'] = 'just now'
            elif delta.total_seconds() < 3600:
                minutes = int(delta.total_seconds() / 60)
                enriched['relative_time'] = f'{minutes} minute{"s" if minutes != 1 else ""} ago'
            elif delta.total_seconds() < 86400:
                hours = int(delta.total_seconds() / 3600)
                enriched['relative_time'] = f'{hours} hour{"s" if hours != 1 else ""} ago'
            else:
                days = int(delta.total_seconds() / 86400)
                enriched['relative_time'] = f'{days} day{"s" if days != 1 else ""} ago'
        except (ValueError, AttributeError):
            enriched['relative_time'] = 'unknown'
        
        # Add risk level based on status
        if event.get('status') == 'failure':
            enriched['risk_level'] = 'high'
        elif event_type in ['authentication', 'login', 'configuration_change']:
            enriched['risk_level'] = 'medium'
        else:
            enriched['risk_level'] = 'low'
        
        return enriched
    
    def _detect_anomalies(self, events: List[Dict], user_id: str) -> List[Dict]:
        """Detect anomalous events in trail."""
        anomalies = []
        
        # Detect failed authentication attempts
        failed_auth_count = 0
        for event in events:
            event_type = event.get('event', '').lower()
            status = event.get('status', '')
            
            if 'authentication' in event_type or 'login' in event_type:
                if status == 'failure':
                    failed_auth_count += 1
                    anomalies.append({
                        'type': 'failed_authentication',
                        'event': event,
                        'severity': 'high',
                        'message': 'Failed authentication attempt detected'
                    })
        
        # Flag if multiple failed attempts
        if failed_auth_count >= 3:
            anomalies.append({
                'type': 'multiple_failed_auth',
                'count': failed_auth_count,
                'severity': 'critical',
                'message': f'{failed_auth_count} failed authentication attempts detected'
            })
        
        # Detect unusual event frequency (simplified)
        if len(events) > 100:
            anomalies.append({
                'type': 'high_event_frequency',
                'count': len(events),
                'severity': 'medium',
                'message': 'Unusually high number of events detected'
            })
        
        return anomalies
    
    # ============================================================================
    # SECURITY ALERTS METHODS
    # ============================================================================
    
    def show_security_alerts(self, alerts_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Show enhanced security alerts with deduplication and grouping.
        
        Args:
            alerts_data: Dictionary containing active_alerts, resolved_alerts lists,
                        and alert_summary with severity counts
        
        Returns:
            Dictionary with alerts data, deduplication, grouping, and remediation
        
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
        
        # REFACTOR: Deduplicate alerts
        deduplicated_alerts = self._deduplicate_alerts(active_alerts)
        
        # REFACTOR: Group alerts by severity
        grouped_by_severity = self._group_alerts(active_alerts, 'severity')
        
        # REFACTOR: Group alerts by type
        grouped_by_type = self._group_alerts(active_alerts, 'type')
        
        # REFACTOR: Generate remediation steps
        remediation_steps = self._generate_remediation_steps(active_alerts)
        
        # REFACTOR: Calculate alert velocity
        alert_velocity = self._calculate_alert_velocity(active_alerts, resolved_alerts)
        
        return {
            'alerts_displayed': True,
            'active_count': active_count,
            'resolved_count': resolved_count,
            'prioritized_alerts': prioritized_alerts,
            'severity_breakdown': severity_breakdown,
            'recommended_actions': recommended_actions,
            'alert_trend': alert_trend,
            # REFACTOR enhancements
            'deduplicated_alerts': deduplicated_alerts,
            'grouped_by_severity': grouped_by_severity,
            'grouped_by_type': grouped_by_type,
            'remediation_steps': remediation_steps,
            'alert_velocity': alert_velocity
        }
    
    def _deduplicate_alerts(self, alerts: List[Dict]) -> List[Dict]:
        """Remove duplicate alerts and track occurrences."""
        alert_map = {}
        
        for alert in alerts:
            alert_type = alert.get('type', 'unknown')
            alert_key = f"{alert_type}_{alert.get('severity', 'medium')}"
            
            if alert_key in alert_map:
                alert_map[alert_key]['occurrence_count'] += 1
                # Track last seen
                if 'timestamp' in alert:
                    alert_map[alert_key]['last_seen'] = alert['timestamp']
            else:
                alert_copy = dict(alert)
                alert_copy['occurrence_count'] = 1
                alert_copy['first_seen'] = alert.get('timestamp', 'unknown')
                alert_copy['last_seen'] = alert.get('timestamp', 'unknown')
                alert_map[alert_key] = alert_copy
        
        return list(alert_map.values())
    
    def _group_alerts(self, alerts: List[Dict], group_by: str) -> Dict[str, List[Dict]]:
        """Group alerts by specified criteria."""
        grouped = {}
        
        for alert in alerts:
            key = alert.get(group_by, 'unknown')
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(alert)
        
        return grouped
    
    def _generate_remediation_steps(self, alerts: List[Dict]) -> Dict[str, List[str]]:
        """Generate remediation steps for alert types."""
        remediation_map = {
            'permission_escalation': [
                'Review user permissions immediately',
                'Verify legitimacy of permission changes',
                'Revoke unauthorized permissions',
                'Update access control policies'
            ],
            'unauthorized_access': [
                'Identify affected resources',
                'Review access logs',
                'Strengthen authentication requirements',
                'Enable additional monitoring'
            ],
            'suspicious_activity': [
                'Investigate user activity patterns',
                'Review recent system changes',
                'Check for compromised credentials',
                'Enable enhanced logging'
            ],
            'policy_violation': [
                'Review security policy compliance',
                'Notify affected users',
                'Update policy documentation',
                'Implement automated policy checks'
            ],
            'default': [
                'Review alert details',
                'Investigate root cause',
                'Apply appropriate security measures',
                'Document resolution steps'
            ]
        }
        
        steps = {}
        for alert in alerts:
            alert_type = alert.get('type', 'unknown')
            if alert_type not in steps:
                steps[alert_type] = remediation_map.get(alert_type, remediation_map['default'])
        
        return steps
    
    def _calculate_alert_velocity(
        self, active_alerts: List[Dict], resolved_alerts: List[Dict]
    ) -> Dict[str, Any]:
        """Calculate rate of new alerts over time."""
        return {
            'active_count': len(active_alerts),
            'resolved_count': len(resolved_alerts),
            'resolution_rate': (
                len(resolved_alerts) / (len(active_alerts) + len(resolved_alerts))
                if (len(active_alerts) + len(resolved_alerts)) > 0
                else 0.0
            ),
            'status': 'healthy' if len(resolved_alerts) >= len(active_alerts) else 'attention_needed'
        }
