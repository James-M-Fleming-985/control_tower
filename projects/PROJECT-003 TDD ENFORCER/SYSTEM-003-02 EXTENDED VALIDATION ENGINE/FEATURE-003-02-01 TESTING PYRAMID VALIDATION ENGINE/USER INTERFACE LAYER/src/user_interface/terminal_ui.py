"""
User Interface Layer - Terminal UI Implementation
RED PHASE: Stub implementation with NotImplementedError

Requirements: LAYER-003-02-01-003_user_interface_requirements_SIMPLIFIED.md
Status: NOT IMPLEMENTED (RED Phase)
"""


class TerminalUI:
    """Terminal-based user interface for TDD Enforcer validation output
    
    Provides text-based display methods for validation results, test progress,
    pyramid statistics, compliance status, error messages, and execution summaries.
    
    Requirements Mapping:
    - REQ-UI-001: Validation Start Display → display_validation_start()
    - REQ-UI-002: Test Progress Indicators → display_test_result()
    - REQ-UI-003: Pyramid Statistics Display → display_pyramid_summary()
    - REQ-UI-004: Compliance Status Display → display_validation_result()
    - REQ-UI-005: Error Message Display → display_error()
    - REQ-UI-006: Execution Summary → display_execution_summary()
    """
    
    def display_validation_start(self, context):
        """Display validation start header with context information
        
        REQ-UI-001: Validation Start Display
        
        Args:
            context (dict): Validation context containing:
                - type (str): "layer", "feature", or "system"
                - name (str): Human-readable name
                - identifier (str): Unique identifier (e.g., LAY-003-02-01-002)
        
        Acceptance Criteria:
        - AC-UI-001.1: Display header, layer/feature/system, timestamp
        - AC-UI-001.2: Include visual separator for readability
        - AC-UI-001.3: Terminal text output format
        """
        raise NotImplementedError("display_validation_start not implemented")
    
    def display_test_result(self, test_name, status, duration_ms):
        """Display individual test result with progress indicator
        
        REQ-UI-002: Test Progress Indicators
        
        Args:
            test_name (str): Name of the test
            status (str): "pass", "fail", or "running"
            duration_ms (int): Test execution duration in milliseconds
        
        Acceptance Criteria:
        - AC-UI-002.1: Display test count (X/Y) and current test name
        - AC-UI-002.2: Status icons (✅ pass, ❌ fail, ⏳ running)
        - AC-UI-002.3: Real-time progress during test execution
        """
        raise NotImplementedError("display_test_result not implemented")
    
    def display_pyramid_summary(self, results):
        """Display test pyramid statistics in formatted table
        
        REQ-UI-003: Pyramid Statistics Display
        
        Args:
            results (dict): Pyramid analysis results containing:
                - pyramid (dict): Nested dict with unit/integration/e2e counts
                    - unit/integration/e2e (dict): total, passed, failed
        
        Acceptance Criteria:
        - AC-UI-003.1: Display unit/integration/e2e test counts
        - AC-UI-003.2: Show pass/fail breakdown for each category
        - AC-UI-003.3: Text-based formatted table output
        """
        raise NotImplementedError("display_pyramid_summary not implemented")
    
    def display_validation_result(self, compliant, reason):
        """Display validation compliance result
        
        REQ-UI-004: Compliance Status Display
        
        Args:
            compliant (bool): Whether validation passed
            reason (str): Explanation of validation result
        
        Acceptance Criteria:
        - AC-UI-004.1: Clear pass/fail validation result
        - AC-UI-004.2: Display compliance percentage and reasoning
        - AC-UI-004.3: Show recommendations for failed validations
        """
        raise NotImplementedError("display_validation_result not implemented")
    
    def display_error(self, error_type, message, suggestions):
        """Display error message with suggested actions
        
        REQ-UI-005: Error Message Display
        
        Args:
            error_type (str): Type of error (e.g., "ValidationError")
            message (str): Error message text
            suggestions (list): List of suggested actions to resolve error
        
        Acceptance Criteria:
        - AC-UI-005.1: Display error type and message clearly
        - AC-UI-005.2: Provide suggested actions for common errors
        - AC-UI-005.3: Format errors for terminal readability
        """
        raise NotImplementedError("display_error not implemented")
    
    def display_execution_summary(self, summary):
        """Display final execution summary
        
        REQ-UI-006: Execution Summary
        
        Args:
            summary (dict): Execution summary containing:
                - total_time_ms (int): Total execution time
                - total_tests (int): Total number of tests
                - passed (int): Number of passed tests
                - failed (int): Number of failed tests
                - outcome (str): Final outcome ("PASS" or "FAIL")
        
        Acceptance Criteria:
        - AC-UI-006.1: Display total execution time
        - AC-UI-006.2: Show test totals and pass rates
        - AC-UI-006.3: Display final validation outcome
        """
        raise NotImplementedError("display_execution_summary not implemented")
