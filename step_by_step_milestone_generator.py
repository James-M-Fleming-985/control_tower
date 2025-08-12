#!/usr/bin/env python3
"""
Step-by-Step Milestone Generator
Implements the user's simplified approach: One table at a time with real data

USAGE:
    python step_by_step_milestone_generator.py [phase] [type]
    
EXAMPLES:
    python step_by_step_milestone_generator.py
    python step_by_step_milestone_generator.py "Documentation & Training" this_month
    python step_by_step_milestone_generator.py "Documentation & Training" last_month_completed
    python step_by_step_milestone_generator.py "Documentation & Training" next_month_planned
    python step_by_step_milestone_generator.py "Documentation & Training" upcoming
    python step_by_step_milestone_generator.py "Documentation & Training" risks

STEP-BY-STEP STRATEGY:
1. Start with Documentation & Training current month milestones
2. Perfect the table format and verify data quality
3. Add next month milestones on a separate slide  
4. Add completed milestones table
5. Add upcoming milestones table
6. Expand to other phases once approach is proven
"""

import sys
import os
from datetime import datetime

# Add the milestone management path
sys.path.append('/workspaces/control_tower/modules/milestone_management/reporting')

try:
    from safran_powerpoint_generator import SafranPowerPointGenerator
    GENERATOR_AVAILABLE = True
except ImportError as e:
    print(f"❌ Cannot import SafranPowerPointGenerator: {e}")
    GENERATOR_AVAILABLE = False

def main():
    """Main execution function"""
    
    if not GENERATOR_AVAILABLE:
        print("❌ SafranPowerPointGenerator not available")
        return
        
    # Parse command line arguments
    phase_name = "Documentation & Training"  # Default phase
    milestone_type = "this_month"  # Default type
    
    if len(sys.argv) > 1:
        phase_name = sys.argv[1]
    if len(sys.argv) > 2:
        milestone_type = sys.argv[2]
        
    # Validate milestone type
    valid_types = ["this_month", "last_month_completed", "next_month_planned", "upcoming", "risks"]
    if milestone_type not in valid_types:
        print(f"❌ Invalid milestone type: {milestone_type}")
        print(f"✅ Valid types: {', '.join(valid_types)}")
        return
        
    print("🎯 STEP-BY-STEP MILESTONE GENERATION")
    print("="*50)
    print(f"📋 Phase: {phase_name}")
    print(f"📅 Type: {milestone_type}")
    print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Set output path
    output_path = "/workspaces/control_tower/reports"
    
    # Create generator
    generator = SafranPowerPointGenerator(output_path=output_path)
    
    # Generate the slide
    result_path = generator.generate_simple_milestone_slide(
        phase_name=phase_name,
        milestone_type=milestone_type
    )
    
    if result_path:
        print(f"\n✅ SUCCESS!")
        print(f"📁 File: {result_path}")
        print(f"\n🎯 NEXT STEPS:")
        print(f"1. Review the generated table for data quality")
        print(f"2. Verify milestone information is accurate") 
        print(f"3. Once satisfied, generate next milestone type")
        print(f"4. Build incrementally: current → next → completed → upcoming")
        
        print(f"\n📋 SUGGESTED WORKFLOW:")
        print(f"Step 1: python step_by_step_milestone_generator.py 'Documentation & Training' this_month")
        print(f"Step 2: python step_by_step_milestone_generator.py 'Documentation & Training' last_month_completed")  
        print(f"Step 3: python step_by_step_milestone_generator.py 'Documentation & Training' next_month_planned")
        print(f"Step 4: python step_by_step_milestone_generator.py 'Documentation & Training' upcoming")
        print(f"Step 5: python step_by_step_milestone_generator.py 'Documentation & Training' risks")
        
    else:
        print("❌ Failed to generate milestone slide")

if __name__ == "__main__":
    main()
