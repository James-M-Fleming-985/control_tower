"""
Performance Monitoring Integration Tests - TDD Iteration 11
REFACTOR Phase: Enhanced tests with validation and edge cases
Layer: Integration Layer
Requirement: Performance Target Validation (<200ms)
"""

import pytest
from src.integration.performance_monitoring_integration_iteration_11 import (
    PerformanceMonitoringIntegration
)


class TestPerformanceMonitoringIntegrationRefactor:
    """
    REFACTOR Phase Tests for Performance Monitoring Integration.
    
    Validates:
    - All GREEN phase tests continue passing
    - Input validation works correctly
    - Error handling for edge cases
    - Logging improvements
    - Code quality enhancements
    """
    
    def setup_method(self):
        """Set up test fixtures"""
        self.integration = PerformanceMonitoringIntegration()
    
    # ========================================================================
    # GREEN PHASE TESTS (Must Continue Passing)
    # ========================================================================
    
    def test_integrate_performance_monitoring_returns_valid_response(self):
        """Test that integrate_performance_monitoring returns correct structure"""
        # Arrange
        monitoring_config = {
            "performance_targets": {
                "response_time_ms": 200,
                "throughput_requests_per_second": 100,
                "error_rate_percentage": 0.1
            },
            "monitoring_systems": [
                "prometheus",
                "grafana",
                "jaeger"
            ]
        }
        
        # Act
        result = self.integration.integrate_performance_monitoring(
            monitoring_config
        )
        
        # Assert - Response structure
        assert isinstance(result, dict)
        assert "integration_status" in result
        assert "systems_configured" in result
        assert "targets_enabled" in result
        assert "integration_timestamp" in result
        
        # Assert - Integration status
        assert result["integration_status"] == "success"
        
        # Assert - Systems configured
        assert isinstance(result["systems_configured"], list)
        assert len(result["systems_configured"]) == 3
        assert "prometheus" in result["systems_configured"]
        assert "grafana" in result["systems_configured"]
        assert "jaeger" in result["systems_configured"]
        
        # Assert - Targets enabled
        assert isinstance(result["targets_enabled"], dict)
        assert "response_time_ms" in result["targets_enabled"]
        assert "throughput_requests_per_second" in result["targets_enabled"]
        assert "error_rate_percentage" in result["targets_enabled"]
        assert result["targets_enabled"]["response_time_ms"] == 200
        assert result["targets_enabled"]["throughput_requests_per_second"] == 100
        assert result["targets_enabled"]["error_rate_percentage"] == 0.1
        
        # Assert - Timestamp
        assert isinstance(result["integration_timestamp"], str)
        assert len(result["integration_timestamp"]) > 0
    
    def test_validate_performance_targets_returns_valid_response(self):
        """Test that validate_performance_targets returns correct structure"""
        # Arrange
        performance_data = {
            "component": "api_gateway",
            "response_time_ms": 175.3,
            "timestamp": "2025-10-04T20:00:00Z"
        }
        
        # Act
        result = self.integration.validate_performance_targets(
            performance_data
        )
        
        # Assert - Response structure
        assert isinstance(result, dict)
        assert "validation_passed" in result
        assert "target_response_time_ms" in result
        assert "actual_response_time_ms" in result
        assert "variance_ms" in result
        assert "validation_timestamp" in result
        
        # Assert - Validation passed (175.3 < 200)
        assert result["validation_passed"] is True
        
        # Assert - Target and actual values
        assert result["target_response_time_ms"] == 200
        assert result["actual_response_time_ms"] == 175.3
        
        # Assert - Variance calculation
        expected_variance = 175.3 - 200
        assert abs(result["variance_ms"] - expected_variance) < 0.01
        
        # Assert - Timestamp
        assert isinstance(result["validation_timestamp"], str)
        assert len(result["validation_timestamp"]) > 0
    
    def test_collect_performance_metrics_returns_valid_response(self):
        """Test that collect_performance_metrics returns correct structure"""
        # Arrange
        component = "payment_service"
        
        # Act
        result = self.integration.collect_performance_metrics(component)
        
        # Assert - Response structure
        assert isinstance(result, dict)
        assert "component" in result
        assert "metrics" in result
        assert "collection_timestamp" in result
        assert "status" in result
        
        # Assert - Component
        assert result["component"] == "payment_service"
        
        # Assert - Metrics
        assert isinstance(result["metrics"], dict)
        assert "response_time_ms" in result["metrics"]
        assert "throughput_rps" in result["metrics"]
        assert "error_rate" in result["metrics"]
        assert "uptime_percentage" in result["metrics"]
        
        # Assert - Metric values are plausible
        assert isinstance(result["metrics"]["response_time_ms"], float)
        assert isinstance(result["metrics"]["throughput_rps"], float)
        assert isinstance(result["metrics"]["error_rate"], float)
        assert isinstance(result["metrics"]["uptime_percentage"], float)
        assert 0 < result["metrics"]["response_time_ms"] < 1000
        assert 0 < result["metrics"]["throughput_rps"] < 10000
        assert 0 <= result["metrics"]["error_rate"] <= 1
        assert 0 <= result["metrics"]["uptime_percentage"] <= 100
        
        # Assert - Status
        assert result["status"] == "success"
        
        # Assert - Timestamp
        assert isinstance(result["collection_timestamp"], str)
        assert len(result["collection_timestamp"]) > 0
    
    # ========================================================================
    # INPUT VALIDATION TESTS (New in REFACTOR)
    # ========================================================================
    
    def test_integrate_monitoring_rejects_invalid_config_type(self):
        """Test that invalid monitoring_config type raises TypeError"""
        # Arrange
        invalid_configs = ["string", 123, None, [], True]
        
        # Act & Assert
        for invalid_config in invalid_configs:
            with pytest.raises(TypeError, match="monitoring_config must be a dictionary"):
                self.integration.integrate_performance_monitoring(invalid_config)
    
    def test_integrate_monitoring_rejects_invalid_targets_type(self):
        """Test that invalid performance_targets type raises TypeError"""
        # Arrange
        monitoring_config = {
            "performance_targets": "invalid",
            "monitoring_systems": ["prometheus"]
        }
        
        # Act & Assert
        with pytest.raises(TypeError, match="performance_targets must be a dictionary"):
            self.integration.integrate_performance_monitoring(monitoring_config)
    
    def test_integrate_monitoring_rejects_invalid_systems_type(self):
        """Test that invalid monitoring_systems type raises TypeError"""
        # Arrange
        monitoring_config = {
            "performance_targets": {},
            "monitoring_systems": "invalid"
        }
        
        # Act & Assert
        with pytest.raises(TypeError, match="monitoring_systems must be a list"):
            self.integration.integrate_performance_monitoring(monitoring_config)
    
    def test_integrate_monitoring_rejects_non_string_systems(self):
        """Test that non-string monitoring systems raise ValueError"""
        # Arrange
        monitoring_config = {
            "performance_targets": {},
            "monitoring_systems": ["prometheus", 123, "grafana"]
        }
        
        # Act & Assert
        with pytest.raises(ValueError, match="All monitoring systems must be strings"):
            self.integration.integrate_performance_monitoring(monitoring_config)
    
    def test_validate_targets_rejects_invalid_data_type(self):
        """Test that invalid performance_data type raises TypeError"""
        # Arrange
        invalid_data = ["list", 123, None, "string"]
        
        # Act & Assert
        for invalid in invalid_data:
            with pytest.raises(TypeError, match="performance_data must be a dictionary"):
                self.integration.validate_performance_targets(invalid)
    
    def test_validate_targets_rejects_missing_component(self):
        """Test that missing component raises ValueError"""
        # Arrange
        performance_data = {
            "response_time_ms": 150
        }
        
        # Act & Assert
        with pytest.raises(ValueError, match="component must be a non-empty string"):
            self.integration.validate_performance_targets(performance_data)
    
    def test_validate_targets_rejects_empty_component(self):
        """Test that empty component raises ValueError"""
        # Arrange
        performance_data = {
            "component": "",
            "response_time_ms": 150
        }
        
        # Act & Assert
        with pytest.raises(ValueError, match="component must be a non-empty string"):
            self.integration.validate_performance_targets(performance_data)
    
    def test_validate_targets_rejects_missing_response_time(self):
        """Test that missing response_time_ms raises ValueError"""
        # Arrange
        performance_data = {
            "component": "test_component"
        }
        
        # Act & Assert
        with pytest.raises(ValueError, match="response_time_ms is required"):
            self.integration.validate_performance_targets(performance_data)
    
    def test_validate_targets_rejects_invalid_response_time_type(self):
        """Test that invalid response_time_ms type raises TypeError"""
        # Arrange
        performance_data = {
            "component": "test_component",
            "response_time_ms": "invalid"
        }
        
        # Act & Assert
        with pytest.raises(TypeError, match="response_time_ms must be a number"):
            self.integration.validate_performance_targets(performance_data)
    
    def test_validate_targets_rejects_negative_response_time(self):
        """Test that negative response_time_ms raises ValueError"""
        # Arrange
        performance_data = {
            "component": "test_component",
            "response_time_ms": -50
        }
        
        # Act & Assert
        with pytest.raises(ValueError, match="response_time_ms cannot be negative"):
            self.integration.validate_performance_targets(performance_data)
    
    def test_collect_metrics_rejects_empty_component(self):
        """Test that empty component raises ValueError"""
        # Act & Assert
        with pytest.raises(ValueError, match="component must be a non-empty string"):
            self.integration.collect_performance_metrics("")
    
    def test_collect_metrics_rejects_invalid_component_type(self):
        """Test that invalid component type raises ValueError"""
        # Arrange
        invalid_components = [123, None, [], {}]
        
        # Act & Assert
        for invalid in invalid_components:
            with pytest.raises(ValueError, match="component must be a non-empty string"):
                self.integration.collect_performance_metrics(invalid)
    
    # ========================================================================
    # EDGE CASE TESTS (New in REFACTOR)
    # ========================================================================
    
    def test_validate_targets_with_exact_threshold(self):
        """Test validation with response time exactly at 200ms threshold"""
        # Arrange
        performance_data = {
            "component": "api_gateway",
            "response_time_ms": 200
        }
        
        # Act
        result = self.integration.validate_performance_targets(performance_data)
        
        # Assert
        assert result["validation_passed"] is True
        assert result["actual_response_time_ms"] == 200
        assert result["variance_ms"] == 0
    
    def test_validate_targets_exceeds_threshold(self):
        """Test validation with response time exceeding 200ms threshold"""
        # Arrange
        performance_data = {
            "component": "slow_service",
            "response_time_ms": 250
        }
        
        # Act
        result = self.integration.validate_performance_targets(performance_data)
        
        # Assert
        assert result["validation_passed"] is False
        assert result["actual_response_time_ms"] == 250
        assert result["variance_ms"] == 50
    
    def test_validate_targets_very_fast_performance(self):
        """Test validation with very fast response time (<50ms)"""
        # Arrange
        performance_data = {
            "component": "fast_cache",
            "response_time_ms": 25.5
        }
        
        # Act
        result = self.integration.validate_performance_targets(performance_data)
        
        # Assert
        assert result["validation_passed"] is True
        assert result["actual_response_time_ms"] == 25.5
        assert result["variance_ms"] == 25.5 - 200
    
    def test_validate_targets_very_slow_performance(self):
        """Test validation with very slow response time (>10000ms)"""
        # Arrange
        performance_data = {
            "component": "slow_batch",
            "response_time_ms": 15000
        }
        
        # Act
        result = self.integration.validate_performance_targets(performance_data)
        
        # Assert
        assert result["validation_passed"] is False
        assert result["actual_response_time_ms"] == 15000
        assert result["variance_ms"] == 14800
    
    def test_integrate_monitoring_with_empty_systems_list(self):
        """Test integration with empty monitoring_systems list"""
        # Arrange
        monitoring_config = {
            "performance_targets": {},
            "monitoring_systems": []
        }
        
        # Act
        result = self.integration.integrate_performance_monitoring(monitoring_config)
        
        # Assert
        assert result["integration_status"] == "failed"
        assert result["systems_configured"] == []
        assert result["targets_enabled"] == {}
    
    def test_integrate_monitoring_uses_default_targets(self):
        """Test that default targets are used when not provided"""
        # Arrange
        monitoring_config = {
            "monitoring_systems": ["prometheus"]
        }
        
        # Act
        result = self.integration.integrate_performance_monitoring(monitoring_config)
        
        # Assert
        assert result["targets_enabled"]["response_time_ms"] == 200
        assert result["targets_enabled"]["throughput_requests_per_second"] == 100
        assert result["targets_enabled"]["error_rate_percentage"] == 0.1
    
    def test_collect_metrics_different_components(self):
        """Test metrics collection for different component names"""
        # Arrange
        components = ["api", "database", "cache", "auth_service"]
        
        # Act & Assert
        for component in components:
            result = self.integration.collect_performance_metrics(component)
            assert result["component"] == component
            assert result["status"] == "success"
            assert "metrics" in result
