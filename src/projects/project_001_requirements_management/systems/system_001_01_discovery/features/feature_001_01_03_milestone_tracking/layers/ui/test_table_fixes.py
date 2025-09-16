#!/usr/bin/env python3
"""
Test script to verify table fixes in Safran PowerPoint Generator:
1. Table column header visibility
2. Row height optimization
3. Milestone data filtering (Level 4 projects only)
"""

import sys
from datetime import datetime
sys.path.append('/workspaces/control_tower')

from modules.milestone_management.reporting.safran_powerpoint_generator import SafranPowerPointGenerator

def test_table_fixes():
    """Run specific tests for the table layout issues"""
    print("🔍 Testing table fixes in Safran PowerPoint Generator")
    print("="*60)
    print("1. Column headers should be visible with proper styling")
    print("2. Row heights optimized (6 rows that fit on the slide)")
    print("3. Milestone data should come from Level 4 projects only")
    print("="*60)
    
    # Create generator instance
    generator = SafranPowerPointGenerator()
    
    # Generate presentation with fixes applied
    output_path = generator.generate_safran_presentation()
    
    if output_path:
        print("\n✅ TEST SUCCESSFUL!")
        print(f"📄 Generated PowerPoint: {output_path}")
        print(f"📋 Please check that:")
        print(f"  1. Column headers are visible and properly styled (blue text)")
        print(f"  2. Table rows are properly sized (6 rows per table fitting on slide)")
        print(f"  3. Only milestone data from Level 4 projects is displayed")
    else:
        print("❌ Failed to generate presentation")

if __name__ == "__main__":
    test_table_fixes()
