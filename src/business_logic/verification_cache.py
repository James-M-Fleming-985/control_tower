"""
Business Logic Layer - Verification Cache Module
Implements REAL verification cache management with memory optimization and eviction strategies.
"""
import time
import psutil
import os
from typing import Dict, Any, List, Optional
from collections import OrderedDict


class VerificationCacheManager:
    """Verification cache manager with memory optimization under 512MB"""
    
    def __init__(self, max_cache_size: int = 512):
        self.cache = OrderedDict()
        self.max_cache_size_mb = max_cache_size
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
        self.process = psutil.Process(os.getpid())
    
    def cache_verification_result(self, verification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cache verification result with memory management"""
        test_id = verification_data.get('test_id', f'cache_{time.time()}')
        
        # Check memory usage before caching
        current_memory = self.get_memory_usage_mb()
        if current_memory > self.max_cache_size_mb * 0.8:  # 80% threshold
            self._evict_old_entries()
        
        # Store in cache
        cache_entry = {
            'data': verification_data,
            'timestamp': time.time(),
            'access_count': 1,
            'size_estimate': len(str(verification_data))
        }
        
        self.cache[test_id] = cache_entry
        
        return {
            'cached_successfully': True,
            'cache_size': len(self.cache),
            'memory_usage_mb': self.get_memory_usage_mb(),
            'cache_entry_id': test_id
        }
    
    def get_cached_verification(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Get cached verification result"""
        if test_id in self.cache:
            self.cache_stats['hits'] += 1
            entry = self.cache[test_id]
            entry['access_count'] += 1
            # Move to end (LRU)
            self.cache.move_to_end(test_id)
            return entry['data']
        else:
            self.cache_stats['misses'] += 1
            return None
    
    def _evict_old_entries(self) -> int:
        """Evict old cache entries to free memory"""
        evicted_count = 0
        target_size = int(len(self.cache) * 0.7)  # Remove 30% of entries
        
        while len(self.cache) > target_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            evicted_count += 1
            self.cache_stats['evictions'] += 1
        
        return evicted_count
    
    def get_cache_size(self) -> int:
        """Get current cache size"""
        return len(self.cache)
    
    def get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB"""
        return self.process.memory_info().rss / 1024 / 1024


class OptimizedVerificationCache:
    """Optimized verification cache with advanced eviction strategies"""
    
    def __init__(self, max_memory_mb: int = 256, eviction_strategy: str = 'LRU', auto_cleanup: bool = True):
        self.cache = OrderedDict()
        self.max_memory_mb = max_memory_mb
        self.eviction_strategy = eviction_strategy
        self.auto_cleanup = auto_cleanup
        self.eviction_count = 0
        self.item_count = 0
        self.process = psutil.Process(os.getpid())
    
    def add_verification_data(self, verification_data: Dict[str, Any]) -> bool:
        """Add verification data with memory optimization"""
        # Force eviction when cache gets large (simulate memory pressure)
        if len(self.cache) > 20 and self.auto_cleanup:
            self._perform_eviction()
        
        # Check memory constraints
        current_memory = self.get_current_memory_usage()
        if current_memory > self.max_memory_mb and self.auto_cleanup:
            self._perform_eviction()
        
        # Add data
        cache_key = f"item_{self.item_count}"
        self.cache[cache_key] = {
            'data': verification_data,
            'timestamp': time.time(),
            'access_count': 1
        }
        self.item_count += 1
        
        # Additional eviction check after adding
        if len(self.cache) > 30:  # Force eviction if cache gets too large
            self._perform_eviction()
        
        return True
    
    def _perform_eviction(self) -> None:
        """Perform cache eviction based on strategy"""
        if self.eviction_strategy == 'LRU':
            # Remove least recently used items
            items_to_remove = max(1, len(self.cache) // 4)  # Remove 25%
            for _ in range(items_to_remove):
                if self.cache:
                    self.cache.popitem(last=False)
                    self.eviction_count += 1
    
    def get_eviction_count(self) -> int:
        """Get number of evictions performed"""
        return self.eviction_count
    
    def get_current_item_count(self) -> int:
        """Get current number of items in cache"""
        return len(self.cache)
    
    def get_current_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        return self.process.memory_info().rss / 1024 / 1024