"""Integration tests for Concurrent Layer Executor."""
import pytest
from src.concurrent_layer_executor import (
    ConcurrentLayerExecutor,
    ProgressReporter
)


def test_integration_concurrent_execution_and_progress():
    """Test integrated concurrent execution with progress reporting."""
    executor = ConcurrentLayerExecutor(max_concurrent=5)
    reporter = ProgressReporter(executor)

    layers = [1, 2, 3, 4, 5]
    results = executor.execute_layers(layers)

    # Verify execution results
    assert len(results) == 5
    assert all(idx in results for idx in range(5))

    # Verify real-time reporting
    real_time_report = reporter.report_real_time()
    assert real_time_report["progress"]["total"] == 5
    assert real_time_report["progress"]["completed"] == 5
    assert real_time_report["percentage"] == 100.0

    # Verify concurrent reporting
    concurrent_report = reporter.report_concurrent()
    assert concurrent_report["concurrent_limit"] == 5
    assert concurrent_report["currently_running"] == 0
    assert concurrent_report["queue_status"]["completed"] == 5

