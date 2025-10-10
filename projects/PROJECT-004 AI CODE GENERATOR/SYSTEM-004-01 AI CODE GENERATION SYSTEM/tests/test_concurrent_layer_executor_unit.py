"""Unit tests for Concurrent Layer Executor."""
import pytest
import sys
from pathlib import Path

# Add PROJECT-004 src to path
project_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(project_src))

from concurrent_layer_executor import (
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


# NEW TESTS: Edge cases for coverage improvement
def test_execute_layers_empty_list():
    """Test execution with empty layer list."""
    executor = ConcurrentLayerExecutor()
    results = executor.execute_layers([])
    assert results == {}
    progress = executor.get_progress()
    assert progress["total"] == 0


def test_executor_invalid_max_concurrent():
    """Test executor rejects invalid max_concurrent values."""
    with pytest.raises(ValueError):
        ConcurrentLayerExecutor(max_concurrent=0)
    with pytest.raises(ValueError):
        ConcurrentLayerExecutor(max_concurrent=11)


def test_progress_reporter_no_executor():
    """Test progress reporter works without executor."""
    reporter = ProgressReporter(executor=None)
    report = reporter.report_real_time()
    assert report["percentage"] == 0
    assert report["progress"]["total"] == 0


def test_report_concurrent_no_executor():
    """Test concurrent report without executor."""
    reporter = ProgressReporter(executor=None)
    report = reporter.report_concurrent()
    assert report["concurrent_limit"] == 0
    assert report["currently_running"] == 0
