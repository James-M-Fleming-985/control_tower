#!/usr/bin/env python3
"""
Performance Tests for User Interface Layer

Tests quality requirements Q1-Q3:
- Q1: Response Time < 50ms for display updates
- Q2: Throughput > 100 display updates per second  
- Q3: Memory Usage < 64MB for display cache

Part of LAYER-003-01-02-003: User Interface Layer Testing
Created: 2025-09-18
"""

import unittest
import time
import threading
import psutil
import os
from datetime import datetime
from unittest.mock import Mock

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from user_interface.progress_display import RealTimeProgressDisplay, VerificationProgressTracker
from user_interface.stage_gate_visualization import StageGateVisualizer, TDDWorkflowVisualizer, TDDStage


class TestUIPerformanceRequirements:
    """Performance tests for UI layer quality requirements"""
    
    def setup_method(self):
        """Setup performance test environment"""
        self.progress_display = RealTimeProgressDisplay()
        self.stage_visualizer = StageGateVisualizer()
        self.performance_results = []
    
    def test_q1_response_time_under_50ms(self):
        """Test Q1: Response Time < 50ms for display updates"""
        # Start progress tracking
        self.progress_display.start_progress(total_steps=100)
        
        response_times = []
        
        # Test 100 display updates
        for i in range(100):
            start_time = time.time()
            
            result = self.progress_display.update_progress(
                step=i,
                stage="TESTING",
                message=f"Performance test update {i}"
            )
            
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            response_times.append(response_time_ms)
            
            # Verify individual update meets requirement
            assert result['meets_requirement'] == True, f"Update {i} took {response_time_ms:.2f}ms (>50ms)"
        
        # Stop progress and get final metrics
        final_metrics = self.progress_display.stop_progress()
        
        # Verify Q1 requirement metrics
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        assert avg_response_time < 50.0, f"Average response time {avg_response_time:.2f}ms exceeds 50ms requirement"
        assert max_response_time < 100.0, f"Maximum response time {max_response_time:.2f}ms too high"
        assert final_metrics['performance_requirements_met']['response_time_ok'] == True
        
        print(f"✅ Q1 PASSED: Avg response time: {avg_response_time:.2f}ms, Max: {max_response_time:.2f}ms")
    
    def test_q2_throughput_over_100_updates_per_second(self):
        """Test Q2: Throughput > 100 display updates per second"""
        update_count = 0
        start_time = time.time()
        test_duration = 2.0  # Test for 2 seconds
        
        # Start progress tracking
        self.progress_display.start_progress(total_steps=1000)
        
        # Rapid updates for 2 seconds
        while time.time() - start_time < test_duration:
            self.progress_display.update_progress(
                step=update_count,
                stage="THROUGHPUT_TEST",
                message=f"High frequency update {update_count}"
            )
            update_count += 1
            
            # Small delay to prevent overwhelming the system
            time.sleep(0.001)  # 1ms delay
        
        # Calculate actual throughput
        actual_duration = time.time() - start_time
        throughput = update_count / actual_duration
        
        # Stop progress and verify metrics
        final_metrics = self.progress_display.stop_progress()
        
        assert throughput >= 100.0, f"Throughput {throughput:.1f} updates/sec < 100 requirement"
        assert final_metrics['performance_requirements_met']['throughput_ok'] == True
        
        print(f"✅ Q2 PASSED: Throughput: {throughput:.1f} updates/sec ({update_count} updates in {actual_duration:.2f}s)")
    
    def test_q3_memory_usage_under_64mb(self):
        """Test Q3: Memory Usage < 64MB for display cache"""
        # Get baseline memory usage
        process = psutil.Process(os.getpid())
        baseline_memory = process.memory_info().rss / (1024 * 1024)  # MB
        
        # Create multiple display components to test memory usage
        displays = []
        visualizers = []
        
        # Create 100 display components with active progress tracking
        for i in range(100):
            display = RealTimeProgressDisplay()
            visualizer = StageGateVisualizer()
            
            # Start progress tracking with some data
            display.start_progress(total_steps=1000, initial_message=f"Memory test {i}")
            
            # Add some progress updates to build up cache
            for j in range(50):
                display.update_progress(j, f"STAGE_{j%3}", f"Memory test update {i}-{j}")
                visualizer.start_stage(TDDStage.RED, f"Memory test stage {i}-{j}")
                visualizer.update_stage_status(j, 100-j, f"Status update {i}-{j}")
            
            displays.append(display)
            visualizers.append(visualizer)
        
        # Measure peak memory usage
        peak_memory = process.memory_info().rss / (1024 * 1024)  # MB
        memory_used_by_displays = peak_memory - baseline_memory
        
        # Clean up displays
        for display in displays:
            display.stop_progress()
        
        # Verify Q3 requirement
        assert memory_used_by_displays < 64.0, f"Display memory usage {memory_used_by_displays:.1f}MB exceeds 64MB requirement"
        
        print(f"✅ Q3 PASSED: Display memory usage: {memory_used_by_displays:.1f}MB (baseline: {baseline_memory:.1f}MB, peak: {peak_memory:.1f}MB)")
    
    def test_stage_gate_visualization_performance(self):
        """Test stage gate visualization performance"""
        stage_times = []
        
        # Test rapid stage transitions
        for i in range(50):
            start_time = time.time()
            
            # Cycle through TDD stages
            stages = [TDDStage.RED, TDDStage.GREEN, TDDStage.REFACTOR]
            stage = stages[i % 3]
            
            self.stage_visualizer.start_stage(stage, f"Performance test stage {i}")
            self.stage_visualizer.update_stage_status(
                tests_failing=i % 5,
                tests_passing=(10 - i % 5),
                message=f"Stage performance test {i}"
            )
            
            # Generate display output
            display_output = self.stage_visualizer.display_current_stage()
            timeline_output = self.stage_visualizer.display_stage_timeline()
            
            end_time = time.time()
            stage_time_ms = (end_time - start_time) * 1000
            stage_times.append(stage_time_ms)
            
            assert len(display_output) > 0, "Stage display should produce output"
            assert len(timeline_output) > 0, "Timeline display should produce output"
        
        # Verify stage visualization performance
        avg_stage_time = sum(stage_times) / len(stage_times)
        max_stage_time = max(stage_times)
        
        assert avg_stage_time < 10.0, f"Average stage visualization time {avg_stage_time:.2f}ms too slow"
        assert max_stage_time < 25.0, f"Maximum stage visualization time {max_stage_time:.2f}ms too slow"
        
        print(f"✅ Stage Visualization Performance: Avg: {avg_stage_time:.2f}ms, Max: {max_stage_time:.2f}ms")
    
    def test_concurrent_display_performance(self):
        """Test performance with concurrent display operations"""
        def progress_worker(worker_id: int, results: list):
            """Worker function for concurrent testing"""
            display = RealTimeProgressDisplay()
            worker_times = []
            
            display.start_progress(total_steps=50)
            
            for i in range(50):
                start_time = time.time()
                display.update_progress(i, f"WORKER_{worker_id}", f"Concurrent test {worker_id}-{i}")
                end_time = time.time()
                
                worker_times.append((end_time - start_time) * 1000)
            
            display.stop_progress()
            results.append({
                'worker_id': worker_id,
                'avg_time_ms': sum(worker_times) / len(worker_times),
                'max_time_ms': max(worker_times),
                'update_count': len(worker_times)
            })
        
        # Start 5 concurrent workers
        results = []
        threads = []
        
        start_time = time.time()
        
        for worker_id in range(5):
            thread = threading.Thread(target=progress_worker, args=(worker_id, results))
            threads.append(thread)
            thread.start()
        
        # Wait for all workers to complete
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # Verify concurrent performance
        assert len(results) == 5, "All workers should complete"
        
        total_updates = sum(r['update_count'] for r in results)
        overall_throughput = total_updates / total_time
        
        avg_response_times = [r['avg_time_ms'] for r in results]
        max_response_times = [r['max_time_ms'] for r in results]
        
        overall_avg_response = sum(avg_response_times) / len(avg_response_times)
        overall_max_response = max(max_response_times)
        
        assert overall_avg_response < 75.0, f"Concurrent avg response {overall_avg_response:.2f}ms too slow"
        assert overall_throughput >= 50.0, f"Concurrent throughput {overall_throughput:.1f} updates/sec too low"
        
        print(f"✅ Concurrent Performance: {overall_throughput:.1f} updates/sec, Avg response: {overall_avg_response:.2f}ms")


class TestUIArchitectureRequirements:
    """Tests for architecture requirements A1-A4"""
    
    def setup_method(self):
        """Setup architecture test environment"""
        self.progress_display = RealTimeProgressDisplay()
        self.workflow_visualizer = TDDWorkflowVisualizer()
    
    def test_a1_observer_pattern_implementation(self):
        """Test A1: Observer Pattern for real-time updates"""
        # Test observer pattern through callback mechanism
        update_events = []
        
        def test_observer(state):
            update_events.append({
                'timestamp': time.time(),
                'stage': state.get('stage', 'unknown'),
                'percentage': state.get('percentage', 0),
                'message': state.get('message', '')
            })
        
        # Create display with observer callback
        display = RealTimeProgressDisplay(update_callback=test_observer)
        
        # Start progress and trigger updates
        display.start_progress(total_steps=10)
        
        for i in range(5):
            display.update_progress(i, f"STAGE_{i}", f"Observer test {i}")
            time.sleep(0.1)  # Allow observer updates
        
        display.stop_progress()
        
        # Verify observer pattern worked
        assert len(update_events) >= 5, f"Observer should receive multiple updates, got {len(update_events)}"
        
        # Verify update events have proper structure
        for event in update_events:
            assert 'timestamp' in event
            assert 'stage' in event
            assert 'percentage' in event
            assert 'message' in event
        
        print(f"✅ A1 PASSED: Observer pattern working with {len(update_events)} events")
    
    def test_a2_mvc_pattern_separation(self):
        """Test A2: MVC pattern with view layer responsibility"""
        # Verify clear separation of concerns
        
        # Model: Data structures
        assert hasattr(self.progress_display, 'state'), "Model component missing"
        
        # View: Display generation
        display_output = self.workflow_visualizer.display_workflow_status()
        assert isinstance(display_output, str), "View should generate string output"
        assert len(display_output) > 0, "View should produce visible output"
        
        # Controller: Update logic
        self.workflow_visualizer.start_workflow(TDDStage.RED)
        result = self.workflow_visualizer.update_workflow(TDDStage.GREEN, 0, 5, "MVC test")
        
        assert isinstance(result, dict), "Controller should return structured data"
        assert 'status' in result, "Controller should provide status information"
        
        print("✅ A2 PASSED: MVC pattern separation verified")


if __name__ == '__main__':
    # Run performance tests
    test_instance = TestUIPerformanceRequirements()
    test_instance.setup_method()
    
    print("🏃‍♂️ Running UI Performance Tests...")
    print("=" * 50)
    
    try:
        test_instance.test_q1_response_time_under_50ms()
        test_instance.test_q2_throughput_over_100_updates_per_second()
        test_instance.test_q3_memory_usage_under_64mb()
        test_instance.test_stage_gate_visualization_performance()
        test_instance.test_concurrent_display_performance()
        
        print("=" * 50)
        print("🎉 ALL PERFORMANCE TESTS PASSED!")
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        raise