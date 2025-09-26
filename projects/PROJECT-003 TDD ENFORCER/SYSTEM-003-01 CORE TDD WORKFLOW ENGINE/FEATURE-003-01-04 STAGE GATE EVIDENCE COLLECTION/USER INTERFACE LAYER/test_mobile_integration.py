"""
Mobile Integration Tests
Post-Refactor Layer Testing - Mobile Interface Integration
Generated from: Prompts/TDD Prompts/4. Post-Refactor Layer Testing.md
Execution Date: September 26, 2025
"""

import pytest
import sys

# Add the layers to Python path for imports
ui_layer = ("/workspaces/control_tower/projects/PROJECT-003 TDD ENFORCER/"
           "SYSTEM-003-01 CORE TDD WORKFLOW ENGINE/"
           "FEATURE-003-01-04 STAGE GATE EVIDENCE COLLECTION/"
           "USER INTERFACE LAYER")

sys.path.insert(0, ui_layer)

from evidence_display_interface import EvidenceDisplayInterface


class TestMobileIntegration:
    """Mobile Integration Tests for UI Layer"""

    def test_responsive_display_with_business_logic_data(self):
        """Test responsive display works with business logic data"""
        display = EvidenceDisplayInterface()
        
        # Large compliance dataset from business logic
        business_data = {
            'overall_score': 87.5,
            'stage_scores': {
                'red_stage': 90,
                'green_stage': 85,
                'refactor_stage': 87
            },
            'detailed_metrics': {
                'test_coverage': 95.0,
                'code_quality': 80.0,
                'maintainability': 85.0
            },
            'recommendations': [f'Recommendation {i}' for i in range(15)]
        }
        
        # Test mobile formatting
        mobile_content = display.format_for_mobile(
            business_data, 
            screen_width=320
        )
        
        # Verify mobile-specific formatting
        assert mobile_content['display_config']['device_type'] == 'mobile'
        assert mobile_content['display_config']['compact_display'] is True
        assert mobile_content['display_config']['screen_width'] == 320
        
        # Should limit recommendations for mobile
        assert len(mobile_content.get('recommendations', [])) <= 5

    def test_touch_interface_optimization(self):
        """Test touch interface optimization for mobile devices"""
        display = EvidenceDisplayInterface()
        
        # Generate responsive CSS for mobile
        mobile_css = display.generate_responsive_layout_css('mobile')
        
        # Verify touch-friendly elements
        assert '@media (max-width: 320px)' in mobile_css
        assert 'touch-target' in mobile_css
        assert 'min-height: 44px' in mobile_css  # iOS touch target size
        
        # Verify mobile-specific styling
        assert 'font-size: 16px' in mobile_css  # Prevent zoom on iOS
        assert 'tap-highlight-color' in mobile_css
        
        # Test button configuration for touch
        touch_config = display.get_mobile_touch_configuration()
        assert touch_config['button_min_size'] >= 44  # Accessibility standard
        assert touch_config['touch_targets_spaced'] is True

    def test_mobile_performance_integration(self):
        """Test mobile performance meets requirements"""
        display = EvidenceDisplayInterface()
        
        # Large dataset to test mobile optimization
        large_dataset = {
            'compliance_data': [f'item_{i}' for i in range(100)],
            'test_results': [f'test_{i}' for i in range(50)],
            'metrics': {f'metric_{i}': i * 10 for i in range(20)}
        }
        
        # Time mobile formatting
        import time
        start_time = time.time()
        
        mobile_package = display.format_for_mobile(
            large_dataset,
            screen_width=375  # iPhone standard
        )
        
        execution_time = (time.time() - start_time) * 1000
        
        # Should complete mobile formatting quickly
        assert execution_time < 300  # Under 300ms for mobile
        
        # Verify data is appropriately compressed for mobile
        assert len(mobile_package.get('compliance_data', [])) <= 10
        assert len(mobile_package.get('test_results', [])) <= 10

    def test_responsive_css_generation(self):
        """Test responsive CSS generation for different screen sizes"""
        display = EvidenceDisplayInterface()
        
        # Test different device breakpoints
        mobile_css = display.generate_responsive_layout_css('mobile')
        tablet_css = display.generate_responsive_layout_css('tablet')
        
        # Mobile CSS (320px and up)
        assert '@media (max-width: 320px)' in mobile_css
        assert 'grid-template-columns: 1fr' in mobile_css  # Single column
        
        # Tablet CSS (768px and up)
        assert '@media (min-width: 768px)' in tablet_css
        assert 'grid-template-columns: 1fr 1fr' in tablet_css  # Two columns
        
        # Verify CSS contains required mobile optimizations
        assert '.compliance-dashboard' in mobile_css
        assert '.stage-scores' in mobile_css
        assert 'touch-action: manipulation' in mobile_css
        
        # Test CSS validation
        css_validation = display.validate_responsive_css(mobile_css)
        assert css_validation['valid'] is True
        assert css_validation['mobile_optimized'] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])