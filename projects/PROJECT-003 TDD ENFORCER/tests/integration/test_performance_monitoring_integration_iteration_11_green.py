"""
Performance Monitoring Integration - TDD Iteration 11 - GREEN Phase Tests
Tests for performance monitoring integration with <200ms target validation
"""

import pytest
import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent.parent.parent / "src" / "integration"
sys.path.insert(0, str(src_path))

from performance_monitoring_integration_iteration_11 import (
    PerformanceMonitoringIntegration
)


class TestPerformanceMonitoringIntegrationGreen:
    """GREEN Phase: Tests should pass with implementation"""
    
    def test_integrate_performance_monitoring_returns_valid_response(self):
        """GREEN: Performance monitoring integration returns valid response"""
        perf_integration = PerformanceMonitoringIntegration()
        monitoring_config = {
            "performance_targets": {
                "response_time_ms": 200,
                "throughput_requests_per_second": 100,
                "error_rate_percentage": 0.1
            },
            "monitoring_systems": ["prometheus", "grafana", "jaeger"]
        }
        
        result = perf_integration.integrate_performance_monitoring(
            monitoring_config
        )
        
        # Validate response structure
        assert isinstance(result, dict)
        assert "integration_status" in result
        assert "systems_configured" in result
        assert "targets_enabled" in result
        assert "integration_timestamp" in result
        
        # Validate integration status
        assert result["integration_status"] in ["success", "partial", "failed"]
        assert result["integration_status"] == "success"
        
        # Validate systems configured
        assert isinstance(result["systems_configured"], list)
        assert len(result["systems_configured"]) == 3
        assert "prometheus" in result["systems_configured"]
        assert "grafana" in result["systems_configured"]
        assert "jaeger" in result["systems_configured"]
        
        # Validate targets enabled
        assert isinstance(result["targets_enabled"], dict)
        assert "response_time_ms" in result["targets_enabled"]
        assert result["targets_enabled"]["response_time_ms"] == 200
        assert "throughput_requests_per_second" in result["targets_enabled"]
        assert (
            result["targets_enabled"]["throughput_requests_per_second"] == 100
        )
        assert "error_rate_percentage" in result["targets_enabled"]
        assert result["targets_enabled"]["error_rate_percentage"] == 0.1
        
        # Validate timestamp
        assert isinstance(result["integration_timestamp"], str)
        assert "T" in result["integration_timestamp"]
    
    def test_validate_performance_targets_returns_valid_response(self):
        """GREEN: Performance target validation returns valid response"""
        perf_integration = PerformanceMonitoringIntegration()
        performance_data = {
            "component": "mobile_command_history",
            "response_time_ms": 150,  # Under 200ms target
            "timestamp": "2025-09-29T12:00:00Z"
        }
        
        result = perf_integration.validate_performance_targets(
            performance_data
        )
        
        # Validate response structure
        assert isinstance(result, dict)
        assert "validation_passed" in result
        assert "target_response_time_ms" in result
        assert "actual_response_time_ms" in result
        assert "variance_ms" in result
        assert "validation_timestamp" in result
        
        # Validate validation passed
        assert isinstance(result["validation_passed"], bool)
        assert result["validation_passed"] is True  # 150ms < 200ms
        
        # Validate target
        assert isinstance(result["target_response_time_ms"], int)
        assert result["target_response_time_ms"] == 200
        
        # Validate actual
        assert result["actual_response_time_ms"] == 150
        
        # Validate variance
        assert result["variance_ms"] == -50  # 150 - 200 = -50
        
        # Validate timestamp
        assert isinstance(result["validation_timestamp"], str)
        assert "T" in result["validation_timestamp"]
    
    def test_collect_performance_metrics_returns_valid_response(self):
        """GREEN: Performance metrics collection returns valid response"""
        perf_integration = PerformanceMonitoringIntegration()
        
        result = perf_integration.collect_performance_metrics(
            "validation_engine"
        )
        
        # Validate response structure
        assert isinstance(result, dict)
        assert "component" in result
        assert "metrics" in result
        assert "collection_timestamp" in result
        assert "status" in result
        
        # Validate component
        assert isinstance(result["component"], str)
        assert result["component"] == "validation_engine"
        
        # Validate metrics
        assert isinstance(result["metrics"], dict)
        assert "response_time_ms" in result["metrics"]
        assert "throughput_rps" in result["metrics"]
        assert "error_rate" in result["metrics"]
        assert "uptime_percentage" in result["metrics"]
        
        # Validate status
        assert isinstance(result["status"], str)
        assert result["status"] in ["success", "failed"]
        assert result["status"] == "success"
        
        # Validate timestamp
        assert isinstance(result["collection_timestamp"], str)
        assert "T" in result["collection_timestamp"]
