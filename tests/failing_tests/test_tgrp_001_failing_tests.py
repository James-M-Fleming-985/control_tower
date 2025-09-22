"""
PERFORMANCE REQUIREMENT TEST - TGRP-001
Database Query Performance
"""
import pytest
import time
import tempfile
import os

class TestTGRP001:
    """Test Database Query Performance under 100ms"""
    
    def test_database_query_performance_under_100ms_fails(self):
        """Test REAL database query performance optimization under 100ms"""
        from src.data_access.test_query_optimizer import TestQueryOptimizer
        
        # Setup temporary database with test data
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            query_optimizer = TestQueryOptimizer(db_path)
            
            # Initialize with sample test data
            query_optimizer.setup_test_data(num_records=1000)
            
            # Test simple query performance
            start_time = time.time()
            results = query_optimizer.query_test_cases_by_name('test_%')
            end_time = time.time()
            
            query_time_ms = (end_time - start_time) * 1000
            assert query_time_ms < 100, f"Query took {query_time_ms:.2f}ms, should be under 100ms"
            assert len(results) > 0, "Query should return results"
            
            # Test complex query with joins performance
            start_time = time.time()
            complex_results = query_optimizer.query_test_results_with_metadata()
            end_time = time.time()
            
            complex_query_time_ms = (end_time - start_time) * 1000
            assert complex_query_time_ms < 100, f"Complex query took {complex_query_time_ms:.2f}ms, should be under 100ms"
            
            # Test indexed query performance
            start_time = time.time()
            indexed_results = query_optimizer.query_by_indexed_field('category', 'unit')
            end_time = time.time()
            
            indexed_query_time_ms = (end_time - start_time) * 1000
            assert indexed_query_time_ms < 50, f"Indexed query took {indexed_query_time_ms:.2f}ms, should be under 50ms"
            
            # Test aggregation query performance
            start_time = time.time()
            agg_results = query_optimizer.get_test_statistics()
            end_time = time.time()
            
            agg_query_time_ms = (end_time - start_time) * 1000
            assert agg_query_time_ms < 100, f"Aggregation query took {agg_query_time_ms:.2f}ms, should be under 100ms"
            assert 'total_tests' in agg_results, "Statistics should include total tests"
            assert 'avg_execution_time' in agg_results, "Statistics should include average execution time"
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)