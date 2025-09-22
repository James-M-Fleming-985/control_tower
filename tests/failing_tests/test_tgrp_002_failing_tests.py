"""
PERFORMANCE REQUIREMENT TEST - TGRP-002
Memory Usage Under 256MB
"""
import pytest
import psutil
import os

class TestTGRP002:
    """Test Memory Usage Optimization under 256MB"""
    
    def test_memory_usage_under_256mb_fails(self):
        """Test REAL memory usage optimization under 256MB during operations"""
        from src.data_access.test_memory_manager import TestMemoryManager
        
        memory_manager = TestMemoryManager()
        
        # Get baseline memory usage
        process = psutil.Process(os.getpid())
        baseline_memory = process.memory_info().rss / 1024 / 1024  # Convert to MB
        
        # Test large dataset operations with memory optimization
        large_dataset_size = 10000
        memory_manager.load_large_test_dataset(large_dataset_size)
        
        # Check memory usage during operations
        current_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = current_memory - baseline_memory
        
        assert memory_increase < 256, f"Memory usage increased by {memory_increase:.2f}MB, should be under 256MB"
        
        # Test memory-efficient batch processing
        batch_results = memory_manager.process_tests_in_batches(batch_size=100)
        assert len(batch_results) > 0, "Batch processing should return results"
        
        # Check memory usage after batch processing
        batch_memory = process.memory_info().rss / 1024 / 1024
        batch_memory_increase = batch_memory - baseline_memory
        
        assert batch_memory_increase < 256, f"Batch processing memory usage {batch_memory_increase:.2f}MB, should be under 256MB"
        
        # Test memory cleanup
        cleanup_success = memory_manager.cleanup_memory()
        assert cleanup_success, "Memory cleanup should succeed"
        
        # Verify memory is released
        post_cleanup_memory = process.memory_info().rss / 1024 / 1024
        memory_after_cleanup = post_cleanup_memory - baseline_memory
        
        # Memory should be significantly reduced after cleanup
        assert memory_after_cleanup < batch_memory_increase * 0.5, "Memory should be reduced after cleanup"
        
        # Test memory monitoring
        memory_stats = memory_manager.get_memory_statistics()
        assert 'current_usage_mb' in memory_stats, "Memory stats should include current usage"
        assert 'peak_usage_mb' in memory_stats, "Memory stats should include peak usage"
        assert 'baseline_usage_mb' in memory_stats, "Memory stats should include baseline usage"
        
        peak_usage = memory_stats['peak_usage_mb']
        assert peak_usage < 256, f"Peak memory usage {peak_usage:.2f}MB should be under 256MB"