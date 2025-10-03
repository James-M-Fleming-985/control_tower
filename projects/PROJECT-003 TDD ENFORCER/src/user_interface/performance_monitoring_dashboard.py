"""
Performance Monitoring Dashboard - TDD Iteration 16
Layer: User Interface Layer
Phase: GREEN (Minimal Implementation)
Created: 2025-10-03

This module provides the Performance Monitoring Dashboard Interface for displaying
performance metrics, trends, alerts, and real-time monitoring.
"""

from typing import Dict, Any


class PerformanceMonitoringDashboard:
    """
    User interface component for performance monitoring dashboard.
    
    Provides methods for:
    - Rendering performance overview with component metrics
    - Displaying performance trends over time
    - Showing performance alerts and thresholds
    - Rendering real-time metrics visualization
    """
    
    def render_performance_overview(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render performance overview with system and component metrics.
        
        Args:
            performance_data: Dictionary containing system_performance and component_performance
        
        Returns:
            Dictionary with performance overview data
        
        Raises:
            ValueError: If performance_data is invalid or missing required fields
        """
        # Validate input
        if not isinstance(performance_data, dict):
            raise ValueError("performance_data must be a dictionary")
        if 'system_performance' not in performance_data:
            raise ValueError("performance_data must contain 'system_performance'")
        if 'component_performance' not in performance_data:
            raise ValueError("performance_data must contain 'component_performance'")

        # Extract data
        system_perf = performance_data['system_performance']
        component_perf = performance_data['component_performance']

        # Validate system_performance fields
        required_fields = ['average_response_time_ms', 'target_response_time_ms', 'performance_score', 'status']
        for field in required_fields:
            if field not in system_perf:
                raise ValueError(f"system_performance must contain '{field}'")

        # Calculate performance metrics
        avg_response = system_perf['average_response_time_ms']
        target_response = system_perf['target_response_time_ms']
        perf_score = system_perf['performance_score']
        system_status = system_perf['status']

        # Identify components over threshold
        components_over_threshold = []
        for comp_name, comp_data in component_perf.items():
            if comp_data.get('response_time_ms', 0) > target_response:
                components_over_threshold.append(comp_name)

        # Count components
        components_count = len(component_perf)

        # Format display data
        display_data = {
            'system': system_perf,
            'components': [
                {
                    'name': name,
                    'response_time_ms': data.get('response_time_ms', 0),
                    'status': data.get('status', 'unknown')
                }
                for name, data in component_perf.items()
            ]
        }

        return {
            'overview_rendered': True,
            'system_status': system_status,
            'performance_score': perf_score,
            'average_response_time_ms': avg_response,
            'target_response_time_ms': target_response,
            'components_count': components_count,
            'components_over_threshold': components_over_threshold,
            'display_data': display_data
        }
    
    def display_performance_trends(self, trends_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Display performance trends over specified time range.
        
        Args:
            trends_data: Dictionary containing time_range, metrics, and target_line
        
        Returns:
            Dictionary with trends visualization data
        
        Raises:
            ValueError: If trends_data is invalid or missing required fields
        """
        # Validate input
        if not isinstance(trends_data, dict):
            raise ValueError("trends_data must be a dictionary")
        if 'time_range' not in trends_data:
            raise ValueError("trends_data must contain 'time_range'")
        if 'metrics' not in trends_data:
            raise ValueError("trends_data must contain 'metrics'")
        if 'target_line' not in trends_data:
            raise ValueError("trends_data must contain 'target_line'")

        # Extract data
        time_range = trends_data['time_range']
        metrics = trends_data['metrics']
        target_line = trends_data['target_line']

        # Validate metrics is a list
        if not isinstance(metrics, list):
            raise ValueError("metrics must be a list")

        # Calculate statistics
        data_points = len(metrics)

        if data_points == 0:
            return {
                'trends_displayed': True,
                'time_range': time_range,
                'data_points': 0,
                'trend_direction': 'stable',
                'min_response_time_ms': 0,
                'max_response_time_ms': 0,
                'avg_response_time_ms': 0,
                'target_line': target_line,
                'chart_data': []
            }

        response_times = [m.get('response_time_ms', 0) for m in metrics]
        min_response = min(response_times)
        max_response = max(response_times)
        avg_response = sum(response_times) / len(response_times)

        # Determine trend direction (simple: compare first half to second half)
        if data_points >= 2:
            mid = data_points // 2
            first_half_avg = sum(response_times[:mid]) / mid
            second_half_avg = sum(response_times[mid:]) / (data_points - mid)
            
            if second_half_avg < first_half_avg - 5:  # 5ms threshold
                trend_direction = 'improving'
            elif second_half_avg > first_half_avg + 5:
                trend_direction = 'degrading'
            else:
                trend_direction = 'stable'
        else:
            trend_direction = 'stable'

        # Format chart data
        chart_data = metrics

        return {
            'trends_displayed': True,
            'time_range': time_range,
            'data_points': data_points,
            'trend_direction': trend_direction,
            'min_response_time_ms': min_response,
            'max_response_time_ms': max_response,
            'avg_response_time_ms': avg_response,
            'target_line': target_line,
            'chart_data': chart_data
        }
    
    def show_performance_alerts(self, alerts_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Show performance alerts with active alerts and history.
        
        Args:
            alerts_data: Dictionary containing active_alerts, alert_history, and alert_summary
        
        Returns:
            Dictionary with performance alerts display data
        
        Raises:
            ValueError: If alerts_data is invalid or missing required fields
        """
        # Validate input
        if not isinstance(alerts_data, dict):
            raise ValueError("alerts_data must be a dictionary")
        if 'active_alerts' not in alerts_data:
            raise ValueError("alerts_data must contain 'active_alerts'")
        if 'alert_history' not in alerts_data:
            raise ValueError("alerts_data must contain 'alert_history'")
        if 'alert_summary' not in alerts_data:
            raise ValueError("alerts_data must contain 'alert_summary'")

        # Extract data
        active_alerts = alerts_data['active_alerts']
        alert_history = alerts_data['alert_history']
        alert_summary = alerts_data['alert_summary']

        # Validate active_alerts is a list
        if not isinstance(active_alerts, list):
            raise ValueError("active_alerts must be a list")

        # Count alerts
        active_count = len(active_alerts)

        # Sort alerts by severity (critical > warning > info)
        severity_order = {'critical': 0, 'warning': 1, 'info': 2}

        def get_severity_key(alert):
            # Extract severity from alert, default to 'info'
            severity = 'info'
            if isinstance(alert, dict):
                if 'severity' in alert:
                    severity = alert['severity']
                elif 'value' in alert and 'threshold' in alert:
                    # Calculate severity based on threshold breach
                    value = alert['value']
                    threshold = alert['threshold']
                    if value > threshold * 1.25:  # 25% over threshold
                        severity = 'critical'
                    elif value > threshold:
                        severity = 'warning'
            return severity_order.get(severity, 2)

        sorted_alerts = sorted(active_alerts, key=get_severity_key)

        # Generate recommended actions
        if active_count == 0:
            recommended_actions = ['Continue monitoring performance metrics']
        elif active_count == 1:
            recommended_actions = ['Investigate single performance alert']
        else:
            recommended_actions = [
                'Review all active performance alerts',
                'Investigate components exceeding thresholds',
                'Consider performance optimization'
            ]

        # Determine alert trend (simple: compare active to history)
        if isinstance(alert_history, list):
            if active_count > len(alert_history):
                alert_trend = 'increasing'
            else:
                alert_trend = 'stable'
        else:
            alert_trend = 'stable'

        return {
            'alerts_displayed': True,
            'active_count': active_count,
            'alert_summary': alert_summary,
            'sorted_alerts': sorted_alerts,
            'recommended_actions': recommended_actions,
            'alert_trend': alert_trend
        }
    
    def render_real_time_metrics(self, real_time_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render real-time metrics with live updates.
        
        Args:
            real_time_config: Dictionary containing refresh_interval, metrics, and visualization_type
        
        Returns:
            Dictionary with real-time metrics configuration
        
        Raises:
            ValueError: If real_time_config is invalid or missing required fields
        """
        # Validate input
        if not isinstance(real_time_config, dict):
            raise ValueError("real_time_config must be a dictionary")
        if 'refresh_interval_seconds' not in real_time_config:
            raise ValueError("real_time_config must contain 'refresh_interval_seconds'")
        if 'metrics_to_display' not in real_time_config:
            raise ValueError("real_time_config must contain 'metrics_to_display'")
        if 'visualization_type' not in real_time_config:
            raise ValueError("real_time_config must contain 'visualization_type'")

        # Extract data
        refresh_interval = real_time_config['refresh_interval_seconds']
        metrics_to_display = real_time_config['metrics_to_display']
        visualization_type = real_time_config['visualization_type']

        # Validate refresh_interval range
        if not isinstance(refresh_interval, (int, float)):
            raise ValueError("refresh_interval_seconds must be a number")
        if refresh_interval < 1 or refresh_interval > 60:
            raise ValueError("refresh_interval_seconds must be between 1 and 60")

        # Validate metrics_to_display is a list
        if not isinstance(metrics_to_display, list):
            raise ValueError("metrics_to_display must be a list")

        # Count metrics
        metrics_count = len(metrics_to_display)

        # Determine auto-refresh enabled (always True if refresh_interval valid)
        auto_refresh_enabled = True

        return {
            'metrics_rendered': True,
            'refresh_interval_seconds': refresh_interval,
            'metrics_count': metrics_count,
            'metrics_to_display': metrics_to_display,
            'visualization_type': visualization_type,
            'auto_refresh_enabled': auto_refresh_enabled
        }
