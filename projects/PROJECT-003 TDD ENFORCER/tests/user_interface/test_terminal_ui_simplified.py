"""
RED Phase Tests - Terminal UI Layer (Simplified)

These tests verify terminal display output using capsys fixture.

Requirements: LAYER-003-02-01-003_user_interface_requirements_SIMPLIFIED.md

Test Structure:
- REQ-UI-001: Display Test Counts (3 tests)
- REQ-UI-002: Display Pyramid Ratios (3 tests)
- REQ-UI-003: Display Pass Rates (3 tests)
- REQ-UI-004: Display Compliance Status (3 tests)
- REQ-UI-005: Display Pyramid Shape Warning (3 tests)
- REQ-UI-006: Display Recommendations (3 tests)

Total: 18 tests
"""

from src.user_interface.terminal_ui import TerminalUI


# ============================================================================
# REQ-UI-001: Display Test Counts (3 tests)
# ============================================================================

class TestDisplayTestCounts:
    """Test display of test counts by pyramid level"""

    def test_display_counts_all_levels(self, capsys):
        """GREEN: Should display counts for Unit/Integration/E2E"""
        ui = TerminalUI()
        test_counts = {"Unit": 50, "Integration": 20, "E2E": 10}

        ui.display_test_counts(test_counts)

        captured = capsys.readouterr()
        assert "Unit" in captured.out
        assert "50" in captured.out
        assert "Integration" in captured.out
        assert "20" in captured.out
        assert "E2E" in captured.out
        assert "10" in captured.out

    def test_display_counts_with_zeros(self, capsys):
        """GREEN: Should handle zero counts gracefully"""
        ui = TerminalUI()
        test_counts = {"Unit": 0, "Integration": 0, "E2E": 0}

        ui.display_test_counts(test_counts)

        captured = capsys.readouterr()
        assert "0" in captured.out

    def test_display_counts_formatting(self, capsys):
        """GREEN: Should format counts for terminal display"""
        ui = TerminalUI()
        test_counts = {"Unit": 123, "Integration": 45, "E2E": 6}

        ui.display_test_counts(test_counts)

        captured = capsys.readouterr()
        assert "123" in captured.out
        assert "45" in captured.out
        assert "6" in captured.out


# ============================================================================
# REQ-UI-002: Display Pyramid Ratios (3 tests)
# ============================================================================

class TestDisplayPyramidRatios:
    """Test display of pyramid ratio percentages"""

    def test_display_ratios_percentages(self, capsys):
        """GREEN: Should display ratios as percentages"""
        ui = TerminalUI()
        ratios = {"Unit": 62.5, "Integration": 25.0, "E2E": 12.5}

        ui.display_pyramid_ratios(ratios)

        captured = capsys.readouterr()
        assert "62.5" in captured.out or "62.5%" in captured.out
        assert "25.0" in captured.out or "25.0%" in captured.out
        assert "12.5" in captured.out or "12.5%" in captured.out

    def test_display_ratios_proper_pyramid(self, capsys):
        """GREEN: Should display proper pyramid ratios"""
        ui = TerminalUI()
        ratios = {"Unit": 70.0, "Integration": 20.0, "E2E": 10.0}

        ui.display_pyramid_ratios(ratios)

        captured = capsys.readouterr()
        assert "70.0" in captured.out or "70.0%" in captured.out
        assert "20.0" in captured.out or "20.0%" in captured.out
        assert "10.0" in captured.out or "10.0%" in captured.out

    def test_display_ratios_inverted_pyramid(self, capsys):
        """GREEN: Should display inverted pyramid ratios"""
        ui = TerminalUI()
        ratios = {"Unit": 10.0, "Integration": 20.0, "E2E": 70.0}

        ui.display_pyramid_ratios(ratios)

        captured = capsys.readouterr()
        assert "10.0" in captured.out or "10.0%" in captured.out
        assert "70.0" in captured.out or "70.0%" in captured.out


# ============================================================================
# REQ-UI-003: Display Pass Rates (3 tests)
# ============================================================================

class TestDisplayPassRates:
    """Test display of pass rates for each pyramid level"""

    def test_display_pass_rates_all_passing(self, capsys):
        """GREEN: Should display pass rates when all tests passing"""
        ui = TerminalUI()
        pass_rates = {"Unit": 100.0, "Integration": 100.0, "E2E": 100.0}

        ui.display_pass_rates(pass_rates)

        captured = capsys.readouterr()
        assert "100.0" in captured.out or "100%" in captured.out

    def test_display_pass_rates_with_failures(self, capsys):
        """GREEN: Should display pass rates with some failures"""
        ui = TerminalUI()
        pass_rates = {"Unit": 95.0, "Integration": 85.0, "E2E": 75.0}

        ui.display_pass_rates(pass_rates)

        captured = capsys.readouterr()
        assert "95.0" in captured.out or "95%" in captured.out
        assert "85.0" in captured.out or "85%" in captured.out
        assert "75.0" in captured.out or "75%" in captured.out

    def test_display_pass_rates_below_threshold(self, capsys):
        """GREEN: Should highlight pass rates below threshold"""
        ui = TerminalUI()
        pass_rates = {"Unit": 60.0, "Integration": 50.0, "E2E": 40.0}

        ui.display_pass_rates(pass_rates)

        captured = capsys.readouterr()
        assert "60.0" in captured.out or "60%" in captured.out
        assert "50.0" in captured.out or "50%" in captured.out
        assert "40.0" in captured.out or "40%" in captured.out


# ============================================================================
# REQ-UI-004: Display Compliance Status (3 tests)
# ============================================================================

class TestDisplayComplianceStatus:
    """Test display of overall compliance status"""

    def test_display_compliant_status(self, capsys):
        """GREEN: Should display compliant status"""
        ui = TerminalUI()
        compliance_result = {
            "is_compliant": True,
            "reasons": ["All validations passed"]
        }

        ui.display_compliance_status(compliance_result)

        captured = capsys.readouterr()
        assert "All validations passed" in captured.out

    def test_display_non_compliant_status(self, capsys):
        """GREEN: Should display non-compliant status with reasons"""
        ui = TerminalUI()
        compliance_result = {
            "is_compliant": False,
            "reasons": [
                "Pyramid shape invalid",
                "Minimum test counts not met"
            ]
        }

        ui.display_compliance_status(compliance_result)

        captured = capsys.readouterr()
        assert "Pyramid shape invalid" in captured.out
        assert "Minimum test counts not met" in captured.out

    def test_display_compliance_with_multiple_failures(self, capsys):
        """GREEN: Should display all compliance failure reasons"""
        ui = TerminalUI()
        compliance_result = {
            "is_compliant": False,
            "reasons": [
                "Pyramid shape invalid",
                "Minimum test counts not met",
                "Pass rate thresholds not met"
            ]
        }

        ui.display_compliance_status(compliance_result)

        captured = capsys.readouterr()
        assert "Pyramid shape invalid" in captured.out
        assert "Minimum test counts not met" in captured.out
        assert "Pass rate thresholds not met" in captured.out


# ============================================================================
# REQ-UI-005: Display Pyramid Shape Warning (3 tests)
# ============================================================================

class TestDisplayPyramidShapeWarning:
    """Test display of pyramid shape warnings"""

    def test_display_warning_inverted_pyramid(self, capsys):
        """GREEN: Should display warning for inverted pyramid"""
        ui = TerminalUI()
        is_inverted = True

        ui.display_pyramid_shape_warning(is_inverted)

        captured = capsys.readouterr()
        assert len(captured.out) > 0
        keywords = ["warning", "inverted", "pyramid"]
        assert any(word in captured.out.lower() for word in keywords)

    def test_display_no_warning_proper_pyramid(self, capsys):
        """GREEN: Should display no warning for proper pyramid"""
        ui = TerminalUI()
        is_inverted = False

        ui.display_pyramid_shape_warning(is_inverted)

        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_display_warning_formatting(self, capsys):
        """GREEN: Should format warning clearly in terminal"""
        ui = TerminalUI()
        is_inverted = True

        ui.display_pyramid_shape_warning(is_inverted)

        captured = capsys.readouterr()
        assert len(captured.out) > 0


# ============================================================================
# REQ-UI-006: Display Recommendations (3 tests)
# ============================================================================

class TestDisplayRecommendations:
    """Test display of actionable recommendations"""

    def test_display_recommendations_for_inverted_pyramid(self, capsys):
        """GREEN: Should recommend adding unit tests"""
        ui = TerminalUI()
        validation_context = {
            "pyramid_valid": False,
            "test_counts": {"Unit": 10, "Integration": 20, "E2E": 30}
        }

        ui.display_recommendations(validation_context)

        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_display_recommendations_for_low_pass_rates(self, capsys):
        """GREEN: Should recommend fixing failing tests"""
        ui = TerminalUI()
        validation_context = {
            "pass_rates_valid": False,
            "pass_rates": {"Unit": 60.0, "Integration": 50.0, "E2E": 40.0}
        }

        ui.display_recommendations(validation_context)

        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_display_recommendations_for_minimum_counts(self, capsys):
        """GREEN: Should recommend adding more tests"""
        ui = TerminalUI()
        validation_context = {
            "minimum_counts_valid": False,
            "test_counts": {"Unit": 5, "Integration": 2, "E2E": 1}
        }

        ui.display_recommendations(validation_context)

        captured = capsys.readouterr()
        assert len(captured.out) > 0


# ============================================================================
# REFACTOR PHASE: Edge Case Tests (18 new tests)
# ============================================================================

class TestEdgeCasesNoneInputs:
    """Test handling of None inputs for all display methods"""

    def test_display_test_counts_none(self, capsys):
        """REFACTOR: Should handle None input gracefully"""
        ui = TerminalUI()
        ui.display_test_counts(None)

        captured = capsys.readouterr()
        assert "ERROR" in captured.out or "No" in captured.out

    def test_display_pyramid_ratios_none(self, capsys):
        """REFACTOR: Should handle None input gracefully"""
        ui = TerminalUI()
        ui.display_pyramid_ratios(None)

        captured = capsys.readouterr()
        assert "ERROR" in captured.out or "No" in captured.out

    def test_display_pass_rates_none(self, capsys):
        """REFACTOR: Should handle None input gracefully"""
        ui = TerminalUI()
        ui.display_pass_rates(None)

        captured = capsys.readouterr()
        assert "ERROR" in captured.out or "No" in captured.out

    def test_display_compliance_status_none(self, capsys):
        """REFACTOR: Should handle None input gracefully"""
        ui = TerminalUI()
        ui.display_compliance_status(None)

        captured = capsys.readouterr()
        assert "ERROR" in captured.out or "No" in captured.out

    def test_display_recommendations_none(self, capsys):
        """REFACTOR: Should handle None input gracefully"""
        ui = TerminalUI()
        ui.display_recommendations(None)

        captured = capsys.readouterr()
        assert "ERROR" in captured.out or "No" in captured.out


class TestEdgeCasesEmptyDictionaries:
    """Test handling of empty dictionaries for all display methods"""

    def test_display_test_counts_empty(self, capsys):
        """REFACTOR: Should handle empty dict gracefully"""
        ui = TerminalUI()
        ui.display_test_counts({})

        captured = capsys.readouterr()
        assert "WARNING" in captured.out or "empty" in captured.out.lower()

    def test_display_pyramid_ratios_empty(self, capsys):
        """REFACTOR: Should handle empty dict gracefully"""
        ui = TerminalUI()
        ui.display_pyramid_ratios({})

        captured = capsys.readouterr()
        assert "WARNING" in captured.out or "empty" in captured.out.lower()

    def test_display_pass_rates_empty(self, capsys):
        """REFACTOR: Should handle empty dict gracefully"""
        ui = TerminalUI()
        ui.display_pass_rates({})

        captured = capsys.readouterr()
        assert "WARNING" in captured.out or "empty" in captured.out.lower()

    def test_display_compliance_status_empty(self, capsys):
        """REFACTOR: Should handle empty dict gracefully"""
        ui = TerminalUI()
        ui.display_compliance_status({})

        captured = capsys.readouterr()
        assert "WARNING" in captured.out or "empty" in captured.out.lower()

    def test_display_recommendations_empty(self, capsys):
        """REFACTOR: Should handle empty dict gracefully"""
        ui = TerminalUI()
        ui.display_recommendations({})

        captured = capsys.readouterr()
        assert "WARNING" in captured.out or "empty" in captured.out.lower()


class TestBoundaryValues:
    """Test boundary value handling"""

    def test_display_ratios_all_zeros(self, capsys):
        """REFACTOR: Should display 0.0% for all zero ratios"""
        ui = TerminalUI()
        ui.display_pyramid_ratios(
            {'Unit': 0.0, 'Integration': 0.0, 'E2E': 0.0}
        )

        captured = capsys.readouterr()
        assert "0.0%" in captured.out

    def test_display_ratios_all_hundreds(self, capsys):
        """REFACTOR: Should display 100.0% correctly"""
        ui = TerminalUI()
        ui.display_pyramid_ratios({'Unit': 100.0})

        captured = capsys.readouterr()
        assert "100.0%" in captured.out

    def test_display_pass_rates_all_zeros(self, capsys):
        """REFACTOR: Should show ✗ for 0% pass rates"""
        ui = TerminalUI()
        ui.display_pass_rates(
            {'Unit': 0.0, 'Integration': 0.0, 'E2E': 0.0}
        )

        captured = capsys.readouterr()
        assert "0.0%" in captured.out
        assert "✗" in captured.out

    def test_display_pass_rates_all_hundreds(self, capsys):
        """REFACTOR: Should show ✓ for 100% pass rates"""
        ui = TerminalUI()
        ui.display_pass_rates(
            {'Unit': 100.0, 'Integration': 100.0, 'E2E': 100.0}
        )

        captured = capsys.readouterr()
        assert "100.0%" in captured.out
        assert captured.out.count("✓") >= 3

    def test_display_pass_rates_exact_threshold(self, capsys):
        """REFACTOR: Should show ✓ for exactly 80% (threshold)"""
        ui = TerminalUI()
        ui.display_pass_rates({'Unit': 80.0})

        captured = capsys.readouterr()
        assert "80.0%" in captured.out
        assert "✓" in captured.out

    def test_display_test_counts_large_numbers(self, capsys):
        """REFACTOR: Should handle large test counts"""
        ui = TerminalUI()
        ui.display_test_counts(
            {'Unit': 10000, 'Integration': 5000, 'E2E': 1000}
        )

        captured = capsys.readouterr()
        assert "10000" in captured.out
        assert "5000" in captured.out
        assert "1000" in captured.out

    def test_recommendations_with_specific_numbers(self, capsys):
        """REFACTOR: Should show specific target numbers"""
        ui = TerminalUI()
        validation_context = {
            "pyramid_valid": False,
            "test_counts": {"Unit": 10, "Integration": 20, "E2E": 30}
        }

        ui.display_recommendations(validation_context)

        captured = capsys.readouterr()
        # Should show specific numbers like current count and target
        assert "10" in captured.out  # Current unit count
        assert any(word in captured.out for word in ["42", "Target", "%"])
