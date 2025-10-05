"""
Mobile UI Components - TDD Iteration 13
Layer: User Interface Layer
Phase: REFACTOR (Full Implementation)
Generated: 2025-10-05
Updated: 2025-10-05

Provides mobile-optimized UI components for command history, context engine
status, and security indicators with Integration Layer API integration.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone


class MobileUIComponents:
    """Mobile UI components for system monitoring and interaction."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize mobile UI components.

        Args:
            config: Configuration for mobile UI components
        """
        self.config = config or {}

    def render_command_history_view(
        self, view_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Render mobile command history view with timeline format and filtering.

        Args:
            view_config: View configuration containing:
                - user_id: User identifier
                - display_format: Display format (e.g., 'timeline')
                - filter_criteria: Filter criteria (e.g., {'layer': 'logic'})
                - page_size: Number of items per page

        Returns:
            Dict containing:
                - view_rendered: True if view successfully rendered
                - display_format: The format used
                - total_commands: Total commands matching filter
                - displayed_commands: Number of commands displayed
                - filter_applied: Filter criteria that was applied
                - user_id: User identifier for the view

        Raises:
            ValueError: If view_config structure is invalid
        """
        # Validation
        if not isinstance(view_config, dict):
            raise ValueError("view_config must be a dictionary")
        
        required_fields = [
            'user_id', 'display_format', 'filter_criteria', 'page_size'
        ]
        for field in required_fields:
            if field not in view_config:
                raise ValueError(f"view_config must contain '{field}'")
        
        user_id = view_config['user_id']
        display_format = view_config['display_format']
        filter_criteria = view_config['filter_criteria']
        page_size = view_config['page_size']
        
        # Validate types
        if not isinstance(user_id, str) or not user_id:
            raise ValueError("user_id must be a non-empty string")
        if not isinstance(display_format, str):
            raise ValueError("display_format must be a string")
        if not isinstance(filter_criteria, dict):
            raise ValueError("filter_criteria must be a dictionary")
        if not isinstance(page_size, int) or page_size <= 0:
            raise ValueError("page_size must be a positive integer")
        
        # Mock command history data (will integrate with mobile auth APIs)
        # In production: Call mobile_auth_integration_iteration_8 APIs
        mock_commands = self._generate_mock_commands(
            user_id, filter_criteria
        )
        
        total_commands = len(mock_commands)
        displayed_commands = min(total_commands, page_size)
        
        return {
            'view_rendered': True,
            'display_format': display_format,
            'total_commands': total_commands,
            'displayed_commands': displayed_commands,
            'filter_applied': filter_criteria,
            'user_id': user_id
        }

    def display_context_engine_status(
        self, status_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Display Context Engine synchronization and health status.

        Args:
            status_data: Status data containing:
                - sync_status: Synchronization status (e.g., 'synced')
                - last_sync: ISO timestamp of last sync
                - pending_changes: Number of pending changes
                - context_health: Health status (e.g., 'healthy')

        Returns:
            Dict containing:
                - status_displayed: True if status successfully displayed
                - sync_status: Sync status indicator
                - last_sync_time: Formatted last sync timestamp
                - pending_changes_count: Number of pending changes
                - health_indicator: Health status visualization
                - visual_elements: UI elements rendered

        Raises:
            ValueError: If status_data structure is invalid
        """
        # Validation
        if not isinstance(status_data, dict):
            raise ValueError("status_data must be a dictionary")
        
        required_fields = [
            'sync_status', 'last_sync', 'pending_changes', 'context_health'
        ]
        for field in required_fields:
            if field not in status_data:
                raise ValueError(f"status_data must contain '{field}'")
        
        sync_status = status_data['sync_status']
        last_sync = status_data['last_sync']
        pending_changes = status_data['pending_changes']
        context_health = status_data['context_health']
        
        # Validate types
        if not isinstance(sync_status, str):
            raise ValueError("sync_status must be a string")
        if not isinstance(last_sync, str):
            raise ValueError("last_sync must be a string")
        if not isinstance(pending_changes, int) or pending_changes < 0:
            raise ValueError("pending_changes must be non-negative integer")
        if context_health not in ['healthy', 'degraded', 'critical']:
            raise ValueError(
                "context_health must be 'healthy', 'degraded', or 'critical'"
            )
        
        # Format last sync time
        last_sync_time = self._format_timestamp(last_sync)
        
        # Create health indicator
        health_indicators = {
            'healthy': '🟢 Healthy',
            'degraded': '🟡 Degraded',
            'critical': '🔴 Critical'
        }
        health_indicator = health_indicators.get(
            context_health, '⚪ Unknown'
        )
        
        # Generate visual elements
        visual_elements = [
            f"Sync: {sync_status}",
            f"Last sync: {last_sync_time}",
            f"Pending: {pending_changes}",
            f"Health: {health_indicator}"
        ]
        
        return {
            'status_displayed': True,
            'sync_status': sync_status,
            'last_sync_time': last_sync_time,
            'pending_changes_count': pending_changes,
            'health_indicator': health_indicator,
            'visual_elements': visual_elements
        }

    def show_security_indicators(
        self, security_status: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Show security authentication and compliance indicators.

        Args:
            security_status: Security status containing:
                - authentication_level: Authentication level (e.g., 'high')
                - session_status: Session status (e.g., 'active')
                - security_alerts: Security alerts list
                - compliance_status: Compliance status (e.g., 'compliant')

        Returns:
            Dict containing:
                - indicators_shown: True if indicators successfully shown
                - authentication_display: Authentication level visualization
                - session_indicator: Session status display
                - alerts_count: Number of security alerts
                - compliance_indicator: Compliance status visualization
                - security_score: Overall security score (0.0-1.0)

        Raises:
            ValueError: If security_status structure is invalid
        """
        # Validation
        if not isinstance(security_status, dict):
            raise ValueError("security_status must be a dictionary")
        
        required_fields = [
            'authentication_level',
            'session_status',
            'security_alerts',
            'compliance_status'
        ]
        for field in required_fields:
            if field not in security_status:
                raise ValueError(f"security_status must contain '{field}'")
        
        auth_level = security_status['authentication_level']
        session_status = security_status['session_status']
        security_alerts = security_status['security_alerts']
        compliance_status = security_status['compliance_status']
        
        # Validate types
        if auth_level not in ['low', 'medium', 'high']:
            raise ValueError(
                "authentication_level must be 'low', 'medium', or 'high'"
            )
        if not isinstance(session_status, str):
            raise ValueError("session_status must be a string")
        if not isinstance(security_alerts, list):
            raise ValueError("security_alerts must be a list")
        if not isinstance(compliance_status, str):
            raise ValueError("compliance_status must be a string")
        
        # Create authentication display
        auth_displays = {
            'high': '🔒 High Security',
            'medium': '🔓 Medium Security',
            'low': '⚠️ Low Security'
        }
        authentication_display = auth_displays.get(
            auth_level, '❓ Unknown'
        )
        
        # Create session indicator
        session_indicator = (
            f"🟢 {session_status.title()}"
            if session_status == 'active'
            else f"⚫ {session_status.title()}"
        )
        
        # Count alerts
        alerts_count = len(security_alerts)
        
        # Create compliance indicator
        compliance_indicator = (
            "✅ Compliant"
            if compliance_status == 'compliant'
            else "⚠️ Non-Compliant"
        )
        
        # Calculate security score
        security_score = self._calculate_security_score(
            auth_level, session_status, alerts_count, compliance_status
        )
        
        return {
            'indicators_shown': True,
            'authentication_display': authentication_display,
            'session_indicator': session_indicator,
            'alerts_count': alerts_count,
            'compliance_indicator': compliance_indicator,
            'security_score': security_score
        }

    # Helper methods

    def _generate_mock_commands(
        self,
        user_id: str,
        filter_criteria: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate mock command history data."""
        # In production: Integrate with mobile_auth_integration_iteration_8
        mock_commands = [
            {
                'command_id': f'cmd_{i}',
                'user_id': user_id,
                'layer': filter_criteria.get('layer', 'business_logic'),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            for i in range(25)  # Mock 25 commands
        ]
        return mock_commands

    def _format_timestamp(self, iso_timestamp: str) -> str:
        """Format ISO timestamp to user-friendly string."""
        try:
            dt = datetime.fromisoformat(
                iso_timestamp.replace('Z', '+00:00')
            )
            now = datetime.now(timezone.utc)
            delta = now - dt
            
            if delta.days > 0:
                return f"{delta.days} days ago"
            elif delta.seconds >= 3600:
                hours = delta.seconds // 3600
                return f"{hours} hours ago"
            elif delta.seconds >= 60:
                minutes = delta.seconds // 60
                return f"{minutes} minutes ago"
            else:
                return "Just now"
        except (ValueError, AttributeError):
            return iso_timestamp

    def _calculate_security_score(
        self,
        auth_level: str,
        session_status: str,
        alerts_count: int,
        compliance_status: str
    ) -> float:
        """Calculate overall security score (0.0-1.0)."""
        score = 0.0
        
        # Authentication level contribution (40%)
        auth_scores = {'high': 0.4, 'medium': 0.25, 'low': 0.1}
        score += auth_scores.get(auth_level, 0.0)
        
        # Session status contribution (20%)
        if session_status == 'active':
            score += 0.2
        
        # Alerts contribution (20% - deducted for alerts)
        if alerts_count == 0:
            score += 0.2
        elif alerts_count <= 3:
            score += 0.1
        
        # Compliance contribution (20%)
        if compliance_status == 'compliant':
            score += 0.2
        
        return round(score, 2)
