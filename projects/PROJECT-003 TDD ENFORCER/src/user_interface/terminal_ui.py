"""
Terminal UI Module

Provides terminal-based user interface for pyramid validation results.

Requirements: REQ-UI-001 through REQ-UI-006
"""

from typing import Dict, Any, Optional


class TerminalUI:
    """Terminal-based UI for displaying pyramid validation results"""

    def display_test_counts(
        self, test_counts: Optional[Dict[str, int]]
    ) -> None:
        """
        Display test counts by pyramid level with aligned formatting.

        Args:
            test_counts: Dictionary with test counts per level.
                        Expected keys: 'Unit', 'Integration', 'E2E'
                        Values: Non-negative integers

        Example Input:
            {'Unit': 50, 'Integration': 20, 'E2E': 10}

        Example Output:
            =====================================
            TEST COUNTS
            =====================================
              Unit Tests:        50
              Integration Tests: 20
              E2E Tests:         10
              Total:             80
            -------------------------------------

        Edge Cases:
            - None input: Prints error message
            - Empty dict: Prints warning
            - Missing keys: Defaults to 0 using .get()
        """
        if test_counts is None:
            print("ERROR: No test count data available")
            return

        if not test_counts:
            print("WARNING: Test counts dictionary is empty")
            return

        print("=" * 80)
        print("TEST COUNTS")
        print("=" * 80)
        print(f"  Unit Tests:        {test_counts.get('Unit', 0)}")
        print(f"  Integration Tests: {test_counts.get('Integration', 0)}")
        print(f"  E2E Tests:         {test_counts.get('E2E', 0)}")
        total = sum(test_counts.values())
        print(f"  Total:             {total}")
        print("-" * 80)

    def display_pyramid_ratios(
        self, ratios: Optional[Dict[str, float]]
    ) -> None:
        """
        Display pyramid ratio percentages with formatted output.

        Args:
            ratios: Dictionary with percentage ratios for each level.
                   Expected keys: 'Unit', 'Integration', 'E2E'
                   Values: Float percentages (0.0-100.0)

        Example Input:
            {'Unit': 62.5, 'Integration': 25.0, 'E2E': 12.5}

        Example Output:
            =====================================
            PYRAMID RATIOS
            =====================================
              Unit:        62.5%
              Integration: 25.0%
              E2E:         12.5%
            -------------------------------------

        Edge Cases:
            - None input: Prints error message
            - Empty dict: Prints warning
            - Missing keys: Defaults to 0.0 using .get()
        """
        if ratios is None:
            print("ERROR: No ratio data available")
            return

        if not ratios:
            print("WARNING: Ratios dictionary is empty")
            return

        print("=" * 80)
        print("PYRAMID RATIOS")
        print("=" * 80)
        print(f"  Unit:        {ratios.get('Unit', 0.0):.1f}%")
        print(f"  Integration: {ratios.get('Integration', 0.0):.1f}%")
        print(f"  E2E:         {ratios.get('E2E', 0.0):.1f}%")
        print("-" * 80)

    def display_pass_rates(
        self, pass_rates: Optional[Dict[str, float]]
    ) -> None:
        """
        Display pass rates for each pyramid level with threshold indicators.

        Args:
            pass_rates: Dictionary with pass rate percentages.
                       Expected keys: 'Unit', 'Integration', 'E2E'
                       Values: Float percentages (0.0-100.0)

        Example Input:
            {'Unit': 95.0, 'Integration': 85.0, 'E2E': 75.0}

        Example Output:
            =====================================
            PASS RATES
            =====================================
              Unit          95.0% ✓
              Integration   85.0% ✓
              E2E           75.0% ✗  (below 80% threshold)
            -------------------------------------

        Edge Cases:
            - None input: Prints error message
            - Empty dict: Prints warning
            - Missing keys: Defaults to 0.0 using .get()

        Note:
            ✓ indicates rate >= 80%
            ✗ indicates rate < 80%
        """
        if pass_rates is None:
            print("ERROR: No pass rate data available")
            return

        if not pass_rates:
            print("WARNING: Pass rates dictionary is empty")
            return

        print("=" * 80)
        print("PASS RATES")
        print("=" * 80)
        for level in ["Unit", "Integration", "E2E"]:
            rate = pass_rates.get(level, 0.0)
            check = "✓" if rate >= 80.0 else "✗"
            print(f"  {level:12} {rate:5.1f}% {check}")
        print("-" * 80)

    def display_compliance_status(
        self, compliance_result: Optional[Dict[str, Any]]
    ) -> None:
        """
        Display overall compliance status with reasons.

        Args:
            compliance_result: Dictionary with compliance information.
                             Expected keys:
                             - 'is_compliant': bool
                             - 'reasons': list of str

        Example Input (Passing):
            {'is_compliant': True, 'reasons': ['All validations passed']}

        Example Output (Passing):
            =====================================
            COMPLIANCE STATUS
            =====================================
            Status: ✓ PASSING
              ✓ All validations passed
            -------------------------------------

        Example Input (Failing):
            {'is_compliant': False,
             'reasons': ['Pyramid shape invalid',
                        'Minimum test counts not met']}

        Example Output (Failing):
            =====================================
            COMPLIANCE STATUS
            =====================================
            Status: ✗ FAILING
              ✗ Pyramid shape invalid
              ✗ Minimum test counts not met
            -------------------------------------

        Edge Cases:
            - None input: Prints error message
            - Empty dict: Prints warning
            - Missing keys: Defaults to False and empty list
        """
        if compliance_result is None:
            print("ERROR: No compliance data available")
            return

        if not compliance_result:
            print("WARNING: Compliance result dictionary is empty")
            return

        is_compliant = compliance_result.get("is_compliant", False)
        reasons = compliance_result.get("reasons", [])

        status = "✓ PASSING" if is_compliant else "✗ FAILING"

        print("=" * 80)
        print("COMPLIANCE STATUS")
        print("=" * 80)
        print(f"Status: {status}")

        prefix = "  ✓" if is_compliant else "  ✗"
        for reason in reasons:
            print(f"{prefix} {reason}")
        print("-" * 80)

    def display_pyramid_shape_warning(self, is_inverted: bool) -> None:
        """
        Display warning if pyramid shape is inverted.

        Args:
            is_inverted: True if pyramid is inverted
                        (more E2E than Unit tests),
                        False if pyramid is healthy

        Example Output (Inverted):
            =====================================
            PYRAMID SHAPE WARNING
            =====================================
            ⚠ WARNING: Inverted Pyramid Detected!
              Your test suite has more E2E tests than Unit tests.
              Consider adding more unit tests for better maintainability.
            -------------------------------------

        Example Output (Healthy):
            =====================================
            PYRAMID SHAPE STATUS
            =====================================
            ✓ Pyramid shape is healthy
            -------------------------------------
        """
        if is_inverted:
            print("=" * 80)
            print("PYRAMID SHAPE WARNING")
            print("=" * 80)
            print("⚠ WARNING: Inverted Pyramid Detected!")
            print("  Your test suite has more E2E tests than Unit tests.")
            print(
                "  Consider adding more unit tests for "
                "better maintainability."
            )
            print("-" * 80)
        else:
            print("=" * 80)
            print("PYRAMID SHAPE STATUS")
            print("=" * 80)
            print("✓ Pyramid shape is healthy")
            print("-" * 80)

    def display_recommendations(
        self, validation_context: Optional[Dict[str, Any]]
    ) -> None:
        """
        Display actionable recommendations with specific targets.

        Args:
            validation_context: Dictionary with validation results and
                              test data.
                              Expected keys:
                              - 'pyramid_valid': bool
                              - 'pass_rates_valid': bool
                              - 'minimum_counts_valid': bool
                              - 'test_counts': dict (optional)
                              - 'pass_rates': dict (optional)

        Example Input (Inverted Pyramid):
            {'pyramid_valid': False,
             'test_counts': {'Unit': 10, 'Integration': 20, 'E2E': 30}}

        Example Output (Inverted Pyramid):
            =====================================
            RECOMMENDATIONS
            =====================================
              1. Add 32 more unit tests to fix inverted pyramid
                 - Current: 10 unit tests (16.7%)
                 - Target: 42 unit tests (70%)
            -------------------------------------

        Example Input (Low Pass Rates):
            {'pass_rates_valid': False,
             'pass_rates': {'Unit': 60.0, 'Integration': 50.0}}

        Example Output (Low Pass Rates):
            =====================================
            RECOMMENDATIONS
            =====================================
              2. Fix failing tests to improve pass rates
                 - Unit: 60.0% (target: ≥80%)
                 - Integration: 50.0% (target: ≥80%)
            -------------------------------------

        Edge Cases:
            - None input: Prints error message
            - Empty dict: Prints warning
            - No issues: Displays success message
        """
        if validation_context is None:
            print("ERROR: No validation context available")
            return

        if not validation_context:
            print("WARNING: Validation context dictionary is empty")
            return

        print("=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)

        has_recommendations = False

        # Check for inverted pyramid with specific targets
        if not validation_context.get("pyramid_valid", True):
            test_counts = validation_context.get("test_counts", {})
            unit_current = test_counts.get('Unit', 0)
            total = sum(test_counts.values())

            if total > 0:
                unit_target = int(total * 0.70)
                unit_gap = max(0, unit_target - unit_current)
                current_pct = (unit_current / total * 100)

                print(f"  1. Add {unit_gap} more unit tests to fix "
                      f"inverted pyramid")
                print(f"     - Current: {unit_current} unit tests "
                      f"({current_pct:.1f}%)")
                print(f"     - Target: {unit_target} unit tests (70%)")
            else:
                print("  1. Add more unit tests to fix inverted pyramid")
                print("     - Aim for 70% unit, 20% integration, 10% E2E")
            has_recommendations = True

        # Check for low pass rates with specific numbers
        if not validation_context.get("pass_rates_valid", True):
            pass_rates = validation_context.get("pass_rates", {})
            print("  2. Fix failing tests to improve pass rates")
            for level, rate in pass_rates.items():
                if rate < 80.0:
                    print(f"     - {level}: {rate:.1f}% (target: ≥80%)")
            has_recommendations = True

        # Check for minimum counts
        if not validation_context.get("minimum_counts_valid", True):
            print("  3. Add more tests to meet minimum requirements")
            print("     - Minimum: 10 unit, 5 integration, 2 E2E tests")
            has_recommendations = True

        if not has_recommendations:
            print("  No issues detected - test suite is well-balanced!")

        print("-" * 80)
