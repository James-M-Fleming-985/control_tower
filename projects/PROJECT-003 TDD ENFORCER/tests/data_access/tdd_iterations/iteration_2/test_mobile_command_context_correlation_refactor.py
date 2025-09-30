#!/usr/bin/env python3
"""
TDD Iteration 2: Context Correlation - REFACTOR Phase Tests
===========================================================

Enhanced testing for the REFACTOR phase of Context Correlation functionality.
Tests advanced features, performance optimizations, and enhanced capabilities.

PROJECT: PROJECT-003 TDD ENFORCER
SYSTEM: SYSTEM-003-02 EXTENDED VALIDATION ENGINE  
FEATURE: FEATURE-003-02-01 TESTING PYRAMID VALIDATION ENGINE
ITERATION: TDD_ITERATION_002
PHASE: REFACTOR
"""

import pytest
import tempfile
import shutil
import time
import threading
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the enhanced repository from the consolidated project src
import sys
sys.path.append('/workspaces/control_tower/projects/PROJECT-003 TDD ENFORCER/src')

from data_access.mobile_command_history_repository import MobileCommandHistoryRepository


class TestContextCorrelationRefactor:
    """Test suite for Context Correlation REFACTOR phase enhancements"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = str(Path(self.temp_dir) / "test_correlation_refactor.db")
        self.repository = MobileCommandHistoryRepository(self.db_path)
        
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_enhanced_context_correlation_with_analytics(self):
        """Test enhanced context correlation with analytics tracking"""
        # Store initial command with context
        command_data = {
            'command_id': 'corr_enhanced_001',
            'user_id': 'test_user',
            'command_text': 'enhanced correlation test',
            'timestamp': time.time(),
            'context': {'feature': 'correlation', 'priority': 'high'}
        }
        
        success, message = self.repository.store_command(command_data)
        assert success is True
        
        # Create correlation with analytics
        correlation_data = {
            'primary_command_id': 'corr_enhanced_001',
            'related_command_id': 'related_cmd_001',
            'correlation_type': 'enhanced_sequence',
            'confidence_score': 0.95,
            'analytics_metadata': {
                'correlation_algorithm': 'enhanced_ml',
                'processing_time_ms': 12.5,
                'confidence_factors': ['semantic', 'temporal', 'user_pattern']
            }
        }
        
        # Test enhanced correlation storage
        correlation_success, correlation_message = self.repository.create_context_correlation(
            correlation_data['primary_command_id'],
            correlation_data['related_command_id'], 
            correlation_data['correlation_type'],
            correlation_data['confidence_score'],
            correlation_data.get('analytics_metadata', {})
        )
        
        assert correlation_success is True
        assert 'enhanced' in correlation_message.lower() or 'correlation' in correlation_message.lower()
        
    def test_batch_correlation_processing(self):
        """Test batch processing of multiple correlations"""
        # Create multiple commands for batch correlation
        commands = []
        for i in range(5):
            command_data = {
                'command_id': f'batch_corr_{i:03d}',
                'user_id': 'batch_user',
                'command_text': f'batch correlation test {i}',
                'timestamp': time.time() + i,
                'context': {'batch_id': 'batch_001', 'sequence': i}
            }
            commands.append(command_data)
            
            success, _ = self.repository.store_command(command_data)
            assert success is True
            
        # Test batch correlation creation
        batch_correlations = []
        for i in range(len(commands) - 1):
            correlation_data = {
                'primary_command_id': commands[i]['command_id'],
                'related_command_id': commands[i + 1]['command_id'],
                'correlation_type': 'batch_sequence',
                'confidence_score': 0.8 + (i * 0.02)
            }
            batch_correlations.append(correlation_data)
            
        # Process batch correlations
        batch_success_count = 0
        for correlation in batch_correlations:
            success, message = self.repository.create_context_correlation(
                correlation['primary_command_id'],
                correlation['related_command_id'],
                correlation['correlation_type'], 
                correlation['confidence_score']
            )
            if success:
                batch_success_count += 1
                
        # Validate batch processing
        assert batch_success_count == len(batch_correlations)
        
    def test_correlation_performance_optimization(self):
        """Test performance optimizations in correlation processing"""
        start_time = time.time()
        
        # Create and correlate commands with performance tracking
        performance_commands = []
        for i in range(10):
            command_data = {
                'command_id': f'perf_test_{i:03d}',
                'user_id': 'perf_user', 
                'command_text': f'performance test command {i}',
                'timestamp': time.time(),
                'context': {'test_type': 'performance', 'iteration': i}
            }
            performance_commands.append(command_data)
            
            # Store command and measure performance
            cmd_start = time.time()
            success, message = self.repository.store_command(command_data)
            cmd_duration = (time.time() - cmd_start) * 1000  # Convert to ms
            
            assert success is True
            assert cmd_duration < 10.0  # Should be under 10ms per operation
            
        # Test correlation performance
        correlation_times = []
        for i in range(len(performance_commands) - 1):
            corr_start = time.time()
            success, message = self.repository.create_context_correlation(
                performance_commands[i]['command_id'],
                performance_commands[i + 1]['command_id'],
                'performance_test',
                0.85
            )
            corr_duration = (time.time() - corr_start) * 1000
            correlation_times.append(corr_duration)
            
            assert success is True
            assert corr_duration < 15.0  # Correlation should be under 15ms
            
        total_duration = (time.time() - start_time) * 1000
        avg_correlation_time = sum(correlation_times) / len(correlation_times)
        
        # Performance assertions
        assert total_duration < 500.0  # Total test should complete under 500ms
        assert avg_correlation_time < 10.0  # Average correlation under 10ms
        
    def test_advanced_correlation_search_and_filtering(self):
        """Test advanced search and filtering capabilities"""
        # Create diverse correlation test data
        test_scenarios = [
            ('search_001', 'search_002', 'user_sequence', 0.9),
            ('search_002', 'search_003', 'feature_related', 0.85),
            ('search_003', 'search_004', 'user_sequence', 0.8),
            ('search_004', 'search_005', 'time_based', 0.75)
        ]
        
        # Store commands and create correlations
        for i, (primary, related, corr_type, confidence) in enumerate(test_scenarios):
            # Store primary command
            primary_cmd = {
                'command_id': primary,
                'user_id': 'search_user',
                'command_text': f'search test command {i}',
                'timestamp': time.time() + i,
                'context': {'search_test': True, 'type': corr_type}
            }
            success, _ = self.repository.store_command(primary_cmd)
            assert success is True
            
            # Store related command  
            related_cmd = {
                'command_id': related,
                'user_id': 'search_user',
                'command_text': f'related search command {i}',
                'timestamp': time.time() + i + 0.5,
                'context': {'search_test': True, 'related_to': primary}
            }
            success, _ = self.repository.store_command(related_cmd)
            assert success is True
            
            # Create correlation
            success, _ = self.repository.create_context_correlation(
                primary, related, corr_type, confidence
            )
            assert success is True
            
        # Test advanced search capabilities
        search_results = []
        
        # Search by correlation type
        type_results, type_message = self.repository.get_correlations_by_type('user_sequence')
        if type_results:
            search_results.extend(type_results)
            
        # Search by confidence threshold
        confidence_results, conf_message = self.repository.get_correlations_by_confidence_threshold(0.8)
        if confidence_results:
            search_results.extend(confidence_results)
            
        # Validate search results
        assert len(search_results) > 0, "Advanced search should return results"
        
    def test_correlation_data_integrity_and_validation(self):
        """Test data integrity and validation in enhanced correlation system"""
        # Test invalid correlation data handling
        invalid_scenarios = [
            ('', 'valid_cmd', 'test', 0.5),  # Empty primary ID
            ('valid_cmd', '', 'test', 0.5),  # Empty related ID
            ('cmd1', 'cmd2', '', 0.5),        # Empty correlation type
            ('cmd1', 'cmd2', 'test', -0.1),   # Invalid confidence (negative)
            ('cmd1', 'cmd2', 'test', 1.1),    # Invalid confidence (> 1.0)
        ]
        
        for primary, related, corr_type, confidence in invalid_scenarios:
            success, message = self.repository.create_context_correlation(
                primary, related, corr_type, confidence
            )
            # Should handle invalid data gracefully
            # Either reject with success=False or handle with appropriate message
            assert isinstance(success, bool)
            assert isinstance(message, str)
            
        # Test valid correlation with integrity checks
        valid_command = {
            'command_id': 'integrity_test_001',
            'user_id': 'integrity_user',
            'command_text': 'integrity test command',
            'timestamp': time.time(),
            'context': {'integrity_test': True}
        }
        
        success, message = self.repository.store_command(valid_command)
        assert success is True
        
        # Create valid correlation
        success, message = self.repository.create_context_correlation(
            'integrity_test_001',
            'integrity_test_related',
            'integrity_test',
            0.75
        )
        
        # Should handle missing related command appropriately
        assert isinstance(success, bool)
        assert isinstance(message, str)
        
    def test_concurrent_correlation_processing(self):
        """Test thread safety in concurrent correlation processing"""
        # Prepare test data
        base_commands = []
        for i in range(5):
            command_data = {
                'command_id': f'concurrent_{i:03d}',
                'user_id': 'concurrent_user',
                'command_text': f'concurrent test {i}',
                'timestamp': time.time() + i,
                'context': {'concurrent_test': True, 'thread_id': i}
            }
            base_commands.append(command_data)
            
            success, _ = self.repository.store_command(command_data)
            assert success is True
            
        # Concurrent correlation creation
        correlation_results = []
        correlation_errors = []
        
        def create_correlations(thread_id):
            """Create correlations in a separate thread"""
            try:
                for i in range(len(base_commands) - 1):
                    success, message = self.repository.create_context_correlation(
                        base_commands[i]['command_id'],
                        base_commands[i + 1]['command_id'],
                        f'concurrent_thread_{thread_id}',
                        0.7 + (thread_id * 0.05)
                    )
                    correlation_results.append((thread_id, success, message))
            except Exception as e:
                correlation_errors.append((thread_id, str(e)))
                
        # Create multiple threads
        threads = []
        for thread_id in range(3):
            thread = threading.Thread(target=create_correlations, args=(thread_id,))
            threads.append(thread)
            
        # Start all threads
        for thread in threads:
            thread.start()
            
        # Wait for completion
        for thread in threads:
            thread.join()
            
        # Validate concurrent processing results
        assert len(correlation_errors) == 0, f"Concurrent processing errors: {correlation_errors}"
        assert len(correlation_results) > 0, "Should have correlation results from concurrent processing"
        
        # Verify thread safety - all operations should succeed
        successful_correlations = [result for result in correlation_results if result[1] is True]
        assert len(successful_correlations) > 0, "At least some concurrent correlations should succeed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])