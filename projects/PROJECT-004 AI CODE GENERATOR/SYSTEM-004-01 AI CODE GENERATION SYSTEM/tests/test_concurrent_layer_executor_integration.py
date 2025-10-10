"""Integration tests for Concurrent Layer Executor."""
import sys
from pathlib import Path

# Add PROJECT-004 src to path
project_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(project_src))

from concurrent_layer_executor import (
    ConcurrentLayerExecutor,
    ProgressReporter
)


def test_integration_concurrent_execution_and_progress():
    """Test integrated concurrent execution with progress reporting."""
    executor = ConcurrentLayerExecutor(max_concurrent=5)
    reporter = ProgressReporter(executor)

    layers = [1, 2, 3, 4, 5]

    # Execute layers
    results = executor.execute_layers(layers)

    # Verify execution
    assert len(results) == 5

    # Get progress report
    progress_report = reporter.report_real_time()
    assert progress_report["percentage"] == 100.0

    # Get concurrent report
    concurrent_report = reporter.report_concurrent()
    assert concurrent_report["concurrent_limit"] == 5
    assert concurrent_report["queue_status"]["completed"] == 5
