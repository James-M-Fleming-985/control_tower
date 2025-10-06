"""
Validation Logic Module

Determines overall pyramid compliance based on results and ratios.

Requirements: REQ-INT-006
"""

from typing import Dict, Tuple, Any


class ValidationLogic:
    """Validation logic for pyramid compliance determination"""
    
    def validate_minimum_counts(
        self,
        test_counts: Dict[str, int],
        minimum_requirements: Dict[str, int]
    ) -> Tuple[bool, str]:
        """
        Check if minimum test counts are met for each level
        
        Args:
            test_counts: Dict with actual test counts
            minimum_requirements: Dict with minimum required counts
            
        Returns:
            True if all minimums met, False otherwise
        """
        for category, minimum in minimum_requirements.items():
            actual = test_counts.get(category, 0)
            if actual < minimum:
                msg = (
                    f"{category} has {actual} tests, "
                    f"minimum {minimum} required"
                )
                return (False, msg)
        return (True, "All minimum counts met")
    
    def validate_pass_rates(
        self,
        pass_rates: Dict[str, float],
        thresholds: Dict[str, float]
    ) -> Tuple[bool, str]:
        """
        Check if pass rates meet threshold requirements
        
        Args:
            pass_rates: Dict with actual pass rates
            thresholds: Dict with threshold requirements
            
        Returns:
            True if all thresholds met, False otherwise
        """
        for category, threshold in thresholds.items():
            actual = pass_rates.get(category, 0.0)
            if actual < threshold:
                msg = (
                    f"{category} pass rate {actual:.1f}% "
                    f"below threshold {threshold}%"
                )
                return (False, msg)
        return (True, "All pass rate thresholds met")
    
    def determine_compliance(
        self, validation_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine overall compliance (pass/fail) with detailed reasoning
        
        Args:
            validation_context: Dict with pyramid shape, minimums, pass rates
            
        Returns:
            Compliance result with detailed reason
        """
        checks = [
            validation_context.get('pyramid_valid', False),
            validation_context.get('minimum_counts_valid', False),
            validation_context.get('pass_rates_valid', False)
        ]
        is_compliant = all(checks)
        
        reasons = []
        if not validation_context.get('pyramid_valid'):
            reasons.append("Pyramid shape invalid")
        if not validation_context.get('minimum_counts_valid'):
            reasons.append("Minimum test counts not met")
        if not validation_context.get('pass_rates_valid'):
            reasons.append("Pass rate thresholds not met")
        
        return {
            'is_compliant': is_compliant,
            'reasons': (
                reasons if not is_compliant
                else ['All validations passed']
            )
        }
