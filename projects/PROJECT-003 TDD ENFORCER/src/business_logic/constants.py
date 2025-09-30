"""
Business Logic Constants
========================

Centralized configuration constants for the business logic layer.
"""

# Compliance and Quality Thresholds
COMPLIANCE_THRESHOLDS = {
    "EXCELLENT": 0.9,
    "GOOD": 0.8, 
    "ACCEPTABLE": 0.75,
    "WARNING": 0.5,
    "MINIMUM": 0.25
}

# Complexity Thresholds
COMPLEXITY_THRESHOLDS = {
    "RED_PHASE_MAX": 0.3,        # Maximum complexity allowed in RED phase
    "GREEN_PHASE_MAX": 0.6,      # Maximum complexity before over-implementation warning
    "REFACTOR_TARGET": 0.5,      # Target complexity after refactoring
    "MINIMAL_IMPLEMENTATION": 0.4  # Threshold for minimal implementation
}

# Performance Thresholds (milliseconds)
PERFORMANCE_THRESHOLDS = {
    "RED_PHASE_MAX_MS": 3000,    # 3 seconds
    "GREEN_PHASE_MAX_MS": 5000,  # 5 seconds  
    "REFACTOR_PHASE_MAX_MS": 8000, # 8 seconds
    "THROUGHPUT_MIN_PER_MINUTE": 20  # Minimum validations per minute
}

# Coverage Thresholds
COVERAGE_THRESHOLDS = {
    "MINIMUM": 0.75,             # 75% minimum coverage
    "GOOD": 0.85,                # 85% good coverage
    "EXCELLENT": 0.95            # 95% excellent coverage
}

# Risk Assessment Levels
RISK_LEVELS = {
    "LOW": "LOW",
    "MEDIUM": "MEDIUM", 
    "HIGH": "HIGH"
}

# Phase Validation Messages
PHASE_MESSAGES = {
    "RED": {
        "SUCCESS": "Excellent RED phase implementation. Ready for GREEN phase transition.",
        "NO_TESTS": "No failing tests found. RED phase requires at least one failing test.",
        "PREMATURE_IMPL": "Premature implementation detected. RED phase requires tests first.",
        "OVER_COMPLEXITY": "Implementation too complex for RED phase. Keep it simple."
    },
    "GREEN": {
        "SUCCESS": "Excellent GREEN phase implementation. Ready for REFACTOR phase transition.", 
        "NO_PASSING": "No passing tests found. GREEN phase requires tests to pass.",
        "OVER_IMPLEMENTATION": "Over-implementation detected. Keep implementation minimal.",
        "FEATURE_CREEP": "New features detected. GREEN phase should only make tests pass."
    },
    "REFACTOR": {
        "SUCCESS": "Excellent REFACTOR phase implementation. Code quality improved.",
        "TESTS_BROKEN": "Tests broken during refactoring. All tests must remain passing.",
        "NO_IMPROVEMENT": "No quality improvement detected. REFACTOR phase should improve code.",
        "NEW_FUNCTIONALITY": "New functionality added. REFACTOR phase should not add features."
    }
}