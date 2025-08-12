#!/usr/bin/env python3
"""
Test script to verify the Documentation & Training phase slide fixes
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.append('/workspaces/control_tower')

from modules.milestone_management.reporting.safran_powerpoint_generator import SafranPowerPointGenerator

def main():
    """Generate a test PowerPoint with focus on the Documentation & Training phase slide"""
    print("🧪 TESTING: Documentation & Training Phase Slide Fixes")
    print("="*70)
    
    # Create a generator instance
    generator = SafranPowerPointGenerator()
    
    # Generate the presentation with current date
    report_path = generator.generate_safran_presentation()
    
    if report_path:
        print(f"\n✅ TEST SUCCESSFUL!")
        print(f"📄 Generated PowerPoint: {report_path}")
        print(f"📋 Please check that:")
        print(f"  1. Column headers are visible on all tables")
        print(f"  2. Row heights are appropriate (no wasted space)")
        print(f"  3. Text is properly sized and visible")
        print(f"  4. Milestone data appears correctly in all tables")
    else:
        print(f"❌ Test failed - could not generate PowerPoint")

if __name__ == "__main__":
    main()
