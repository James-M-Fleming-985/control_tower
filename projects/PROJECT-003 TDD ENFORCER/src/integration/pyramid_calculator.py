"""
Pyramid Ratio Calculator Module

Calculates pyramid ratios to validate proper test distribution.

Requirements: REQ-INT-004
"""

from typing import Dict


class PyramidRatioCalculator:
    """Calculate and validate testing pyramid ratios"""
    
    def calculate_ratios(
        self, test_counts: Dict[str, int]
    ) -> Dict[str, float]:
        """
        Calculate test count ratios for pyramid levels
        
        Args:
            test_counts: Dict with unit/integration/e2e counts
            
        Returns:
            Ratios dict with percentages
        """
        total = sum(test_counts.values())
        if total == 0:
            return {category: 0.0 for category in test_counts}
        
        return {
            category: (count / total) * 100.0
            for category, count in test_counts.items()
        }
    
    def validate_pyramid_shape(self, test_counts: Dict[str, int]) -> bool:
        """
        Determine if test distribution forms proper pyramid
        
        Args:
            test_counts: Dict with unit/integration/e2e counts
            
        Returns:
            True if proper pyramid, False if inverted
        """
        unit = test_counts.get('Unit', 0)
        integration = test_counts.get('Integration', 0)
        e2e = test_counts.get('E2E', 0)
        
        return unit > integration and integration > e2e
    
    def detect_inverted_pyramid(self, test_counts: Dict[str, int]) -> bool:
        """
        Detect inverted pyramid (too many integration/e2e tests)
        
        Args:
            test_counts: Dict with unit/integration/e2e counts
            
        Returns:
            Inverted status with reason and recommendation
        """
        unit = test_counts.get('Unit', 0)
        integration = test_counts.get('Integration', 0)
        e2e = test_counts.get('E2E', 0)
        
        return e2e > integration or e2e > unit
