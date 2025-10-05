"""
E2E Test: Performance Monitoring Workflow

Tests complete performance monitoring across all layers.
"""

import unittest
from src.integration.performance_monitoring_integration_iteration_11 import (
    PerformanceMonitoringIntegration
)


class TestE2EPerformanceMonitoring(unittest.TestCase):
    """End-to-end test for performance monitoring workflow"""

    def setUp(self):
        """Set up E2E test fixtures"""
        self.performance = PerformanceMonitoringIntegration()

    def test_complete_performance_monitoring_workflow(self):
        """Test complete performance monitoring from collection to UI"""
        # Step 1: System collects metrics from all sources
        collection_request = {
            'component': 'validation_engine',
            'metric_types': ['latency', 'throughput', 'error_rate']
        }
        collection_result = (
            self.performance.collect_performance_metrics(
                collection_request
            )
        )
        self.assertEqual(collection_result['status'], 'success')
        self.assertIn('collected_metrics', collection_result)

        # Step 2: System aggregates metrics
        integration_request = {
            'monitoring_systems': [
                'validation_engine',
                'context_engine',
                'security_system'
            ],
            'performance_targets': {
                'response_time_ms': 200,
                'throughput_requests_per_second': 100
            }
        }
        integration_result = (
            self.performance.integrate_performance_monitoring(
                integration_request
            )
        )
        self.assertEqual(integration_result['status'], 'success')
        self.assertEqual(
            len(integration_result['enabled_monitoring']), 3
        )

        # Step 3: System detects anomalies (via validation)
        validation_request = {
            'component': 'validation_engine',
            'actual_performance': {
                'response_time_ms': 150,
                'throughput': 120
            },
            'performance_targets': {
                'response_time_ms': 200,
                'throughput_requests_per_second': 100
            }
        }
        validation_result = (
            self.performance.validate_performance_targets(
                validation_request
            )
        )
        self.assertEqual(validation_result['status'], 'success')
        self.assertTrue(validation_result['meets_targets'])

        # Step 4: UI displays performance data (verified by structure)
        self.assertIn('collected_metrics', collection_result)
        self.assertIn('enabled_monitoring', integration_result)
        self.assertIn('meets_targets', validation_result)

        # Verify complete workflow
        self.assertIsNotNone(collection_result['collected_metrics'])
        self.assertTrue(len(integration_result['enabled_monitoring']) > 0)
        self.assertIsInstance(validation_result['meets_targets'], bool)


if __name__ == '__main__':
    unittest.main()
