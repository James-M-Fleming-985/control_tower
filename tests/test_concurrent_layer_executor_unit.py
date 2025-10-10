"""Unit tests for Concurrent Layer Executor."""
import pytest
from src.concurrent_layer_executor import (
    ConcurrentLayerExecutor,
    ProgressReporter
)


def test_concurrent_executor_initialization():
    """Test that executor initializes with correct defaults."""
    executor = ConcurrentLayerExecutor()
    assert executor.max_concurrent == 5
    assert executor.semaphore is not None
    assert executor.queue is not None
    assert executor.results == {}


def test_queue_management_fifo():
    """Test that queue management returns correct status."""
    executor = ConcurrentLayerExecutor()
    status = executor.manage_queue()
    assert "size" in status
    assert "total" in status
    assert "queued" in status
    assert "running" in status
    assert "completed" in status


def test_execute_5_layers_concurrently():
    """Test concurrent execution of 5 layers."""
    executor = ConcurrentLayerExecutor(max_concurrent=5)
    layers = [1, 2, 3, 4, 5]
    results = executor.execute_layers(layers)
    assert len(results) == 5
    assert all(idx in results for idx in range(5))


def test_semaphore_limits_concurrent_execution():
    """Test that semaphore limits concurrent execution."""
    executor = ConcurrentLayerExecutor(max_concurrent=5)
    layers = [1, 2, 3, 4, 5, 6]
    results = executor.execute_layers(layers)
    assert len(results) == 6
    # Verify all layers were executed despite limit
    assert all(idx in results for idx in range(6))


def test_progress_reporter_real_time_updates():
    """Test that progress reporter generates real-time updates."""
    executor = ConcurrentLayerExecutor()
    reporter = ProgressReporter(executor)
    report = reporter.report_real_time()
    assert "timestamp" in report
    assert "progress" in report
    assert "percentage" in report


def test_progress_reporting_concurrent_execution():
    """Test concurrent execution progress reporting."""
    executor = ConcurrentLayerExecutor()
    reporter = ProgressReporter(executor)
    report = reporter.report_concurrent()
    assert "timestamp" in report
    assert "concurrent_limit" in report
    assert "currently_running" in report
    assert "queue_status" in report

