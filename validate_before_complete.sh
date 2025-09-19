#!/bin/bash
# MANDATORY VALIDATION SCRIPT - Run Before Any "Complete" Claims
# ================================================================
#
# This script MUST be run before claiming any feature/requirement is complete.
# NO EXCEPTIONS until the TDD enforcer is built.
#
# Usage: ./validate_before_complete.sh FEATURE-003-01-03

set -e

FEATURE_ID=${1:-"003-01-03"}

echo "🚨 FRAUD PREVENTION CHECK - FEATURE-${FEATURE_ID}"
echo "=" * 60

# 1. Run requirements validator
echo "📋 Step 1: Running requirements validator..."
python tools/validate_requirements.py --feature ${FEATURE_ID}

# 2. Check if validation passes
echo ""
echo "📊 Step 2: Checking validation results..."
COVERAGE=$(python tools/validate_requirements.py --feature ${FEATURE_ID} | grep "Actual (Validation):" | grep -o '[0-9]*\.[0-9]*')

if [ -z "$COVERAGE" ]; then
    echo "❌ FRAUD ALERT: Could not extract coverage percentage"
    exit 1
fi

# Use awk for floating point comparison instead of bc
BELOW_THRESHOLD=$(echo "$COVERAGE 75.0" | awk '{print ($1 < $2)}')

if [ "$BELOW_THRESHOLD" = "1" ]; then
    echo "❌ FRAUD ALERT: Actual coverage ($COVERAGE%) is below Grade B (75%)"
    echo "🚫 BLOCKING: Cannot claim completion until requirements are actually implemented"
    echo ""
    echo "🔧 REQUIRED ACTIONS:"
    echo "   1. Implement missing methods identified in validation report"
    echo "   2. Run failing tests (RED phase)"
    echo "   3. Implement code to pass tests (GREEN phase)"
    echo "   4. Re-run this validation script"
    echo ""
    exit 1
fi

echo "✅ VALIDATION PASSED: Actual coverage ($COVERAGE%) meets Grade B requirements"
echo "🎉 APPROVED: Feature can be marked as complete"
echo ""
echo "📝 NEXT STEPS:"
echo "   1. Update documentation to reflect ACTUAL status"
echo "   2. Create evidence package with test results"
echo "   3. Submit for review"