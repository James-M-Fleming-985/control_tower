#!/bin/bash
# Full Batch Refactoring Automation - All 11 Batches
# Created: 2025-10-08
# Purpose: Execute complete RED-GREEN-REFACTOR cycle for all batches

set -e  # Exit on error

SCRIPT_DIR="/workspaces/control_tower/tools"
AUTOMATION_TOOL="$SCRIPT_DIR/batch_refactoring_automation.py"
LOG_FILE="/workspaces/control_tower/projects/PROJECT-003 TDD ENFORCER/SYSTEM-003-02 EXTENDED VALIDATION ENGINE/FEATURE-003-02-01 TESTING PYRAMID VALIDATION ENGINE/Batch Refactoring Results/full_automation_log.txt"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "🚀 FULL BATCH REFACTORING AUTOMATION - ALL 11 BATCHES"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
echo "Start Time: $(date)"
echo "Log File: $LOG_FILE"
echo ""

# Initialize log file
echo "Full Batch Refactoring Automation Log" > "$LOG_FILE"
echo "Started: $(date)" >> "$LOG_FILE"
echo "═══════════════════════════════════════════════════════════════════════════════" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Track overall progress
TOTAL_BATCHES=11
COMPLETED_BATCHES=0
FAILED_BATCHES=0

# Function to run a single batch through all phases
run_batch() {
    local batch_num=$1
    
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}📦 BATCH $batch_num - Starting All Phases${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    echo "BATCH $batch_num - Starting" >> "$LOG_FILE"
    
    # RED Phase
    echo -e "${YELLOW}🔴 RED Phase - Generating Failing Tests${NC}"
    if python "$AUTOMATION_TOOL" --batch "$batch_num" --phase RED >> "$LOG_FILE" 2>&1; then
        echo -e "${GREEN}✅ RED Phase Complete${NC}"
        echo "  RED Phase: SUCCESS" >> "$LOG_FILE"
    else
        echo -e "${RED}❌ RED Phase Failed${NC}"
        echo "  RED Phase: FAILED" >> "$LOG_FILE"
        return 1
    fi
    echo ""
    
    # GREEN Phase
    echo -e "${YELLOW}🟢 GREEN Phase - Refactoring to Validator${NC}"
    if python "$AUTOMATION_TOOL" --batch "$batch_num" --phase GREEN >> "$LOG_FILE" 2>&1; then
        echo -e "${GREEN}✅ GREEN Phase Complete${NC}"
        echo "  GREEN Phase: SUCCESS" >> "$LOG_FILE"
    else
        echo -e "${RED}❌ GREEN Phase Failed${NC}"
        echo "  GREEN Phase: FAILED" >> "$LOG_FILE"
        return 1
    fi
    echo ""
    
    # REFACTOR Phase
    echo -e "${YELLOW}🔵 REFACTOR Phase - Final Validation${NC}"
    if python "$AUTOMATION_TOOL" --batch "$batch_num" --phase REFACTOR >> "$LOG_FILE" 2>&1; then
        echo -e "${GREEN}✅ REFACTOR Phase Complete${NC}"
        echo "  REFACTOR Phase: SUCCESS" >> "$LOG_FILE"
    else
        echo -e "${RED}❌ REFACTOR Phase Failed${NC}"
        echo "  REFACTOR Phase: FAILED" >> "$LOG_FILE"
        return 1
    fi
    echo ""
    
    echo -e "${GREEN}✅ BATCH $batch_num COMPLETE${NC}"
    echo "BATCH $batch_num: COMPLETE" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    
    return 0
}

# Execute all 11 batches
for batch in {1..11}; do
    if run_batch "$batch"; then
        ((COMPLETED_BATCHES++))
        echo -e "${GREEN}Progress: $COMPLETED_BATCHES/$TOTAL_BATCHES batches completed${NC}"
    else
        ((FAILED_BATCHES++))
        echo -e "${RED}⚠️  Batch $batch failed - continuing with next batch${NC}"
    fi
    echo ""
    sleep 2  # Brief pause between batches
done

# Final Summary
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "📊 FULL AUTOMATION COMPLETE"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
echo "End Time: $(date)"
echo "Completed Batches: $COMPLETED_BATCHES/$TOTAL_BATCHES"
echo "Failed Batches: $FAILED_BATCHES"
echo ""

# Write summary to log
echo "" >> "$LOG_FILE"
echo "═══════════════════════════════════════════════════════════════════════════════" >> "$LOG_FILE"
echo "FINAL SUMMARY" >> "$LOG_FILE"
echo "═══════════════════════════════════════════════════════════════════════════════" >> "$LOG_FILE"
echo "Completed: $(date)" >> "$LOG_FILE"
echo "Completed Batches: $COMPLETED_BATCHES/$TOTAL_BATCHES" >> "$LOG_FILE"
echo "Failed Batches: $FAILED_BATCHES" >> "$LOG_FILE"

if [ "$FAILED_BATCHES" -eq 0 ]; then
    echo -e "${GREEN}✅ ALL BATCHES COMPLETED SUCCESSFULLY!${NC}"
    echo "STATUS: SUCCESS" >> "$LOG_FILE"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some batches failed - see log for details${NC}"
    echo "STATUS: PARTIAL SUCCESS" >> "$LOG_FILE"
    exit 1
fi
