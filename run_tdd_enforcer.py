#!/usr/bin/env python3
"""
Wrapper to run TDD Workflow Enforcer with correct paths
"""
import sys
import os

# Add paths
sys.path.insert(0, '/workspaces/control_tower')
sys.path.insert(0, '/workspaces/control_tower/src')

# Set working directory
os.chdir('/workspaces/control_tower')

# Import and run the enforcer
from src.data_access.tdd_workflow_enforcer import main

if __name__ == "__main__":
    main()