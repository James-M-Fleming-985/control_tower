"""
Tests for Testing Visualization - Iteration 22
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.user_interface.testing_visualization_refactored import (
    TestingVisualization
)


class TestTestingVisualization:
    """Test suite for Testing Visualization"""
    
    @pytest.fixture
    def viz(self):
        """Create TestingVisualization instance"""
        return TestingVisualization()
    
    def test_display_test_results_all(self, viz):
        """Should display all test results"""
        result = viz.display_test_results('all')
        
        assert result['total_tests'] == 4
        assert result['passed'] == 3
        assert result['failed'] == 1
        assert len(result['results']) == 4
        assert result['pass_rate'] == 75.0
    
    def test_display_test_results_passed_only(self, viz):
        """Should filter to show only passed tests"""
        result = viz.display_test_results('passed')
        
        assert len(result['results']) == 3
        assert all(r['status'] == 'passed' for r in result['results'])
    
    def test_display_test_results_failed_only(self, viz):
        """Should filter to show only failed tests"""
        result = viz.display_test_results('failed')
        
        assert len(result['results']) == 1
        assert result['results'][0]['status'] == 'failed'
    
    def test_get_test_details_passed(self, viz):
        """Should get details for passed test"""
        result = viz.get_test_details('test_success')
        
        assert result['test_name'] == 'test_success'
        assert result['status'] == 'passed'
        assert result['stack_trace'] is None
        assert result['coverage'] > 0
    
    def test_get_test_details_failed(self, viz):
        """Should get details for failed test with stack trace"""
        result = viz.get_test_details('test_fail')
        
        assert result['test_name'] == 'test_fail'
        assert result['status'] == 'failed'
        assert result['stack_trace'] is not None
        assert 'AssertionError' in result['stack_trace']
    
    def test_get_coverage_summary(self, viz):
        """Should get coverage summary"""
        result = viz.get_coverage_summary()
        
        assert result['overall_coverage'] > 0
        assert 'by_layer' in result
        assert len(result['by_layer']) == 4
        assert result['covered_lines'] + result['uncovered_lines'] == (
            result['total_lines']
        )
    
    def test_render_coverage_heatmap(self, viz):
        """Should render coverage heatmap data"""
        result = viz.render_coverage_heatmap()
        
        assert result['heatmap_type'] == 'layer_coverage'
        assert len(result['data']) == 4
        assert all('coverage' in d for d in result['data'])
        assert 'scale' in result
    
    def test_get_test_history(self, viz):
        """Should get test history"""
        result = viz.get_test_history('test_auth', days=7)
        
        assert result['test_name'] == 'test_auth'
        assert len(result['history']) <= 7
        assert all('status' in h for h in result['history'])
        assert 0 <= result['flaky_score'] <= 1
