"""
BLRP-003: Memory Usage Optimization < 512MB during verification cache operations
Tests for memory usage optimization during verification operations.
This test MUST fail until memory optimization is properly implemented.
"""
import pytest
import psutil
import os
import time
from pathlib import Path


class TestMemoryUsageOptimization:
    """Test memory usage optimization requirements during verification"""
    
    def test_memory_usage_under_512mb_during_verification(self):
        """Test that verification cache operations stay within 512MB memory limit"""
        try:
            from src.business_logic.verification_cache import VerificationCacheManager
            
            # Get initial memory usage
            process = psutil.Process(os.getpid())
            initial_memory_mb = process.memory_info().rss / 1024 / 1024
            
            cache_manager = VerificationCacheManager(max_cache_size=512)
            
            # Fill cache with verification data to test memory limits
            for i in range(1000):
                verification_data = {
                    'test_id': f'memory_test_{i}',
                    'test_content': f'def test_{i}(): {"assert True; " * 100}',  # Larger content
                    'verification_result': {
                        'status': 'PASSED',
                        'metrics': {'coverage': 95.0, 'quality': 8.5},
                        'analysis': f'Analysis data for test {i}' * 50  # Substantial data
                    }
                }
                cache_manager.cache_verification_result(verification_data)
            
            # Check memory usage during cache operations
            peak_memory_mb = process.memory_info().rss / 1024 / 1024
            memory_used_for_cache = peak_memory_mb - initial_memory_mb
            
            assert cache_manager is not None, "Verification cache manager must be instantiated"
            assert memory_used_for_cache < 512, f"Memory usage {memory_used_for_cache:.2f}MB exceeds 512MB limit"
            assert cache_manager.get_cache_size() > 0, "Cache must contain verification data"
            assert cache_manager.get_memory_usage_mb() < 512, "Cache must report memory usage under limit"
            
        except ImportError:
            pytest.fail("VerificationCacheManager not implemented in src.business_logic.verification_cache")
        except AttributeError as e:
            pytest.fail(f"Missing cache management method: {e}")
    
    def test_memory_optimization_with_cache_eviction(self):
        """Test that memory optimization includes proper cache eviction strategies"""
        try:
            from src.business_logic.verification_cache import OptimizedVerificationCache
            
            process = psutil.Process(os.getpid())
            initial_memory_mb = process.memory_info().rss / 1024 / 1024
            
            # Create cache with aggressive memory limits
            optimized_cache = OptimizedVerificationCache(
                max_memory_mb=256,  # Tighter limit
                eviction_strategy='LRU',
                auto_cleanup=True
            )
            
            # Add data until cache should trigger eviction
            added_items = 0
            for i in range(2000):
                large_verification_data = {
                    'verification_id': f'optimize_test_{i}',
                    'heavy_analysis': {
                        'code_analysis': 'x' * 10000,  # 10KB per item
                        'performance_metrics': list(range(1000)),
                        'quality_assessment': {'details': 'y' * 5000}
                    },
                    'timestamp': time.time()
                }
                
                success = optimized_cache.add_verification_data(large_verification_data)
                if success:
                    added_items += 1
                
                # Check memory during additions
                current_memory_mb = process.memory_info().rss / 1024 / 1024
                cache_memory_usage = current_memory_mb - initial_memory_mb
                
                if cache_memory_usage > 256:  # Should trigger eviction before this
                    break
            
            final_memory_mb = process.memory_info().rss / 1024 / 1024
            final_cache_memory = final_memory_mb - initial_memory_mb
            
            assert added_items > 100, "Cache must allow reasonable amount of data before eviction"
            assert final_cache_memory < 512, f"Final memory usage {final_cache_memory:.2f}MB exceeds 512MB limit"
            assert optimized_cache.get_eviction_count() > 0, "Cache must perform evictions to stay within limits"
            assert optimized_cache.get_current_item_count() < 2000, "Cache must evict items, not store everything"
            
        except ImportError:
            pytest.fail("OptimizedVerificationCache not implemented in src.business_logic.verification_cache")
        except AttributeError as e:
            pytest.fail(f"Missing cache optimization method: {e}")
    
    def test_memory_leak_prevention_during_verification(self):
        """Test that verification operations don't cause memory leaks"""
        try:
            from src.business_logic.verification_service import MemoryEfficientVerificationService
            
            process = psutil.Process(os.getpid())
            
            # Baseline memory measurement
            baseline_memory_mb = process.memory_info().rss / 1024 / 1024
            
            service = MemoryEfficientVerificationService()
            
            # Perform multiple verification cycles to detect leaks
            memory_measurements = []
            
            for cycle in range(10):
                # Process a batch of verifications
                batch_data = []
                for i in range(50):
                    batch_data.append({
                        'test_data': f'def test_cycle_{cycle}_{i}(): assert True',
                        'metadata': {'cycle': cycle, 'test_num': i}
                    })
                
                # Process and measure
                cycle_start_memory = process.memory_info().rss / 1024 / 1024
                
                results = service.process_verification_batch(batch_data)
                
                # Force cleanup
                service.cleanup_verification_resources()
                
                cycle_end_memory = process.memory_info().rss / 1024 / 1024
                memory_measurements.append(cycle_end_memory - baseline_memory_mb)
                
                assert len(results) == len(batch_data), f"Cycle {cycle}: Must process all verifications"
            
            # Analyze memory growth
            final_memory_usage = memory_measurements[-1]
            max_memory_usage = max(memory_measurements)
            memory_growth = memory_measurements[-1] - memory_measurements[0]
            
            assert final_memory_usage < 512, f"Final memory usage {final_memory_usage:.2f}MB exceeds 512MB limit"
            assert max_memory_usage < 512, f"Peak memory usage {max_memory_usage:.2f}MB exceeds 512MB limit"
            assert memory_growth < 100, f"Memory growth {memory_growth:.2f}MB indicates potential leak"
            
        except ImportError:
            pytest.fail("MemoryEfficientVerificationService not implemented in src.business_logic.verification_service")
        except AttributeError as e:
            pytest.fail(f"Missing memory efficient verification method: {e}")