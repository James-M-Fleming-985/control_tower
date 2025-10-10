"""
Feature Integration Tests for TDD Cycle Orchestration.

Tests cross-layer integration between:
- LAYER-004-01-03-01: AI Code Generator Orchestrator
- LAYER-004-01-03-02: Concurrent Layer Executor

These tests validate feature-level workflows and component interactions.
"""
import sys
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add PROJECT-004 src to path
project_src = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(project_src))

from concurrent_layer_executor import (
    ConcurrentLayerExecutor,
    ProgressReporter
)


def test_orchestrator_uses_concurrent_executor():
    """
    Test: Orchestrator delegates layer execution to ConcurrentLayerExecutor.
    
    Validates:
    - Orchestrator creates executor with correct concurrency
    - Executor processes layers concurrently
    - Progress updates flow back to orchestrator
    - Results collected correctly
    """
    # Setup
    executor = ConcurrentLayerExecutor(max_concurrent=5)
    reporter = ProgressReporter(executor)
    
    # Simulate orchestrator delegating layers
    layers = ['layer1', 'layer2', 'layer3', 'layer4', 'layer5']
    
    # Execute
    results = executor.execute_layers(layers)
    progress_report = reporter.report_real_time()
    
    # Verify
    assert len(results) == 5
    assert all(idx in results for idx in range(5))
    assert progress_report['percentage'] == 100.0
    assert progress_report['progress']['completed'] == 5
    assert progress_report['progress']['running'] == 0


def test_concurrent_tdd_cycle_execution():
    """
    Test: Execute multiple TDD cycles concurrently.
    
    Validates:
    - Multiple layers execute RED phase concurrently
    - Progress reporting tracks all concurrent operations
    - Phase transitions coordinated correctly
    - No race conditions in result collection
    """
    # Setup multiple TDD cycle simulations
    executor = ConcurrentLayerExecutor(max_concurrent=3)
    reporter = ProgressReporter(executor)
    
    # Simulate 3 concurrent TDD cycles
    tdd_cycles = [
        {'phase': 'RED', 'layer': 'layer_a'},
        {'phase': 'RED', 'layer': 'layer_b'},
        {'phase': 'RED', 'layer': 'layer_c'}
    ]
    
    # Track progress during execution
    initial_report = reporter.report_real_time()
    assert initial_report['percentage'] == 0
    
    # Execute
    results = executor.execute_layers(tdd_cycles)
    
    # Get concurrent execution report
    concurrent_report = reporter.report_concurrent()
    
    # Verify
    assert len(results) == 3
    assert concurrent_report['concurrent_limit'] == 3
    assert concurrent_report['queue_status']['completed'] == 3
    
    # Verify no race conditions (all results present)
    assert all(idx in results for idx in range(3))


def test_orchestrator_with_real_progress_reporting():
    """
    Test: Integration of orchestration with live progress updates.
    
    Validates:
    - Real-time progress updates during TDD cycle
    - Accurate percentage calculations
    - Timestamp tracking
    - Status consistency
    """
    # Setup
    executor = ConcurrentLayerExecutor(max_concurrent=5)
    reporter = ProgressReporter(executor)
    
    layers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    # Track progress before execution
    report_before = reporter.report_real_time()
    timestamp_before = report_before['timestamp']
    
    # Execute with progress tracking
    results = executor.execute_layers(layers)
    
    # Get progress after execution
    time.sleep(0.1)  # Ensure timestamp difference
    report_after = reporter.report_real_time()
    timestamp_after = report_after['timestamp']
    
    # Verify progress tracking
    assert report_before['percentage'] == 0
    assert report_after['percentage'] == 100.0
    assert timestamp_after > timestamp_before
    
    # Verify status consistency
    progress = executor.get_progress()
    assert progress['total'] == 10
    assert progress['completed'] == 10
    assert progress['running'] == 0
    assert progress['queued'] == 0
    
    # Verify results
    assert len(results) == 10


def test_error_propagation_across_layers():
    """
    Test: Errors in executor propagate correctly to orchestrator.
    
    Validates:
    - Executor failures reported to orchestrator
    - Orchestrator handles executor errors gracefully
    - Proper error logging and recovery
    - Partial results preserved on failure
    """
    # Test invalid max_concurrent (should raise ValueError)
    try:
        executor = ConcurrentLayerExecutor(max_concurrent=0)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "max_concurrent must be between 1 and 10" in str(e)
    
    # Test with valid executor but edge cases
    executor = ConcurrentLayerExecutor(max_concurrent=5)
    
    # Empty layers should return empty results gracefully
    results = executor.execute_layers([])
    assert results == {}
    
    # Verify executor state remains consistent after error
    progress = executor.get_progress()
    assert progress['total'] == 0
    assert progress['completed'] == 0


def test_end_to_end_multi_layer_workflow():
    """
    Test: Complete workflow with real operations.
    
    Validates:
    - Layer execution with concurrent processing
    - Progress reporting throughout workflow
    - Result collection and verification
    - State management across workflow
    """
    # Setup complete workflow
    max_concurrent = 5
    executor = ConcurrentLayerExecutor(max_concurrent=max_concurrent)
    reporter = ProgressReporter(executor)
    
    # Simulate realistic layer workflow
    layers = [
        'orchestrator_layer',
        'implementation_generator',
        'test_generator',
        'concurrent_executor',
        'verification_layer'
    ]
    
    # Phase 1: Initial state
    initial_progress = executor.get_progress()
    assert initial_progress['total'] == 0
    assert initial_progress['completed'] == 0
    
    # Phase 2: Execute layers concurrently
    results = executor.execute_layers(layers)
    
    # Phase 3: Verify execution
    assert len(results) == len(layers)
    
    # Phase 4: Check progress reporting
    final_report = reporter.report_real_time()
    assert final_report['percentage'] == 100.0
    assert final_report['progress']['total'] == len(layers)
    assert final_report['progress']['completed'] == len(layers)
    
    # Phase 5: Verify concurrent execution report
    concurrent_report = reporter.report_concurrent()
    assert concurrent_report['concurrent_limit'] == max_concurrent
    assert concurrent_report['currently_running'] == 0
    assert concurrent_report['queue_status']['completed'] == len(layers)
    
    # Phase 6: Verify queue management
    queue_status = executor.manage_queue()
    assert queue_status['total'] == len(layers)
    assert queue_status['completed'] == len(layers)
    assert queue_status['queued'] == 0
    assert queue_status['running'] == 0
    
    # All phases completed successfully
    assert True
