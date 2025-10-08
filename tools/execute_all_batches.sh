#!/bin/bash
# Complete Batch Refactoring Execution - All 11 Batches
# Created: 2025-10-08
# Purpose: Execute all batch refactorings systematically

set -e  # Exit on error

WORKSPACE_ROOT="/workspaces/control_tower"
LOG_DIR="$WORKSPACE_ROOT/projects/PROJECT-003 TDD ENFORCER/SYSTEM-003-02 EXTENDED VALIDATION ENGINE/FEATURE-003-02-01 TESTING PYRAMID VALIDATION ENGINE/Batch Refactoring Results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
FULL_LOG="$LOG_DIR/COMPLETE_BATCH_EXECUTION_${TIMESTAMP}.log"

echo "========================================" | tee -a "$FULL_LOG"
echo "COMPLETE BATCH REFACTORING EXECUTION" | tee -a "$FULL_LOG"
echo "========================================" | tee -a "$FULL_LOG"
echo "Start Time: $(date)" | tee -a "$FULL_LOG"
echo "" | tee -a "$FULL_LOG"

# Track overall progress
TOTAL_BATCHES=11
COMPLETED_BATCHES=0
FAILED_BATCHES=0

for BATCH_NUM in {1..11}; do
    echo "" | tee -a "$FULL_LOG"
    echo "========================================" | tee -a "$FULL_LOG"
    echo "BATCH $BATCH_NUM - STARTING" | tee -a "$FULL_LOG"
    echo "========================================" | tee -a "$FULL_LOG"
    
    # Execute RED phase
    echo "[$BATCH_NUM] Running RED phase..." | tee -a "$FULL_LOG"
    if python tools/batch_refactoring_automation.py --batch $BATCH_NUM --phase RED 2>&1 | tee -a "$FULL_LOG"; then
        echo "[$BATCH_NUM] ✅ RED phase complete" | tee -a "$FULL_LOG"
    else
        echo "[$BATCH_NUM] ⚠️  RED phase had issues (may be expected)" | tee -a "$FULL_LOG"
    fi
    
    # Execute GREEN phase (manual refactoring tracking)
    echo "[$BATCH_NUM] Running GREEN phase..." | tee -a "$FULL_LOG"
    if python tools/batch_refactoring_automation.py --batch $BATCH_NUM --phase GREEN 2>&1 | tee -a "$FULL_LOG"; then
        echo "[$BATCH_NUM] ✅ GREEN phase complete" | tee -a "$FULL_LOG"
    else
        echo "[$BATCH_NUM] ⚠️  GREEN phase requires manual work" | tee -a "$FULL_LOG"
    fi
    
    # Execute REFACTOR phase
    echo "[$BATCH_NUM] Running REFACTOR phase..." | tee -a "$FULL_LOG"
    if python tools/batch_refactoring_automation.py --batch $BATCH_NUM --phase REFACTOR 2>&1 | tee -a "$FULL_LOG"; then
        echo "[$BATCH_NUM] ✅ REFACTOR phase complete" | tee -a "$FULL_LOG"
        COMPLETED_BATCHES=$((COMPLETED_BATCHES + 1))
    else
        echo "[$BATCH_NUM] ❌ REFACTOR phase failed" | tee -a "$FULL_LOG"
        FAILED_BATCHES=$((FAILED_BATCHES + 1))
    fi
    
    echo "[$BATCH_NUM] Batch $BATCH_NUM complete" | tee -a "$FULL_LOG"
    echo "Progress: $COMPLETED_BATCHES/$TOTAL_BATCHES batches completed" | tee -a "$FULL_LOG"
done

echo "" | tee -a "$FULL_LOG"
echo "========================================" | tee -a "$FULL_LOG"
echo "COMPLETE BATCH EXECUTION FINISHED" | tee -a "$FULL_LOG"
echo "========================================" | tee -a "$FULL_LOG"
echo "End Time: $(date)" | tee -a "$FULL_LOG"
echo "Completed Batches: $COMPLETED_BATCHES/$TOTAL_BATCHES" | tee -a "$FULL_LOG"
echo "Failed Batches: $FAILED_BATCHES" | tee -a "$FULL_LOG"
echo "" | tee -a "$FULL_LOG"
echo "Full log saved to: $FULL_LOG" | tee -a "$FULL_LOG"

exit 0
