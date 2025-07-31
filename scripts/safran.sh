#!/bin/bash
# Safran Workflow - Single Command Execution
# Usage: ./scripts/safran.sh [options]

cd /workspaces/control_tower
python scripts/safran_workflow.py "$@"
