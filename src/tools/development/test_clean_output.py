#!/usr/bin/env python3
"""
🧪 TEST CLEAN OUTPUT FORMATTER
Test the clean output system to ensure it provides proper user journey messaging
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from output.clean_formatter import CleanOutput, StatusType, OutputLevel

def test_clean_output():
    """Test the clean output formatter"""
    
    print("🧪 Testing Clean Output Formatter")
    print("=" * 50)
    
    # Test different output levels
    for level in [OutputLevel.NORMAL, OutputLevel.VERBOSE]:
        print(f"\n--- Testing {level.name} Level ---")
        
        formatter = CleanOutput(level)
        
        # Test header
        formatter.header("Discovery Results", "Scanning North Star repositories")
        
        # Test different status types
        formatter.status(StatusType.SUCCESS, "Repository scan complete")
        formatter.status(StatusType.WARNING, "Some items overdue", "Check PROJECT-004 timeline")
        formatter.status(StatusType.ERROR, "Missing requirements file", "PROJECT-005 requirements not found")
        formatter.status(StatusType.DUE, "SYSTEM-003-02 due today")
        formatter.status(StatusType.OVERDUE, "PROJECT-004 Review (2 days overdue)")
        formatter.status(StatusType.UPCOMING, "SYSTEM-005-01 Planning (due Monday)")
        
        # Test work items
        formatter.section_break()
        formatter.work_item("SYSTEM-003-02", "Investment Portfolio Rebalancing", "2025-09-13", "High", "In Progress")
        formatter.work_item("PROJECT-004", "Debt Elimination Strategy", "2025-09-11", "Critical", "Overdue")
        formatter.work_item("SYSTEM-005-01", "Real Estate Platform", "2025-09-16", "Medium", "Not Started")
        
        # Test next action
        formatter.next_action("make work-on ITEM=SYSTEM-003-02", "Start work on highest priority item")
        
        # Test progress
        formatter.section_break()
        formatter.progress_update(3, 8, "Investment Strategy systems")
        
        # Test user journey messages
        formatter.section_break()
        formatter.user_journey_message("discovery", "Found 15 work items across 6 repositories")
        formatter.user_journey_message("work_setup", "Environment ready for development")
        formatter.user_journey_message("completion", "Feature shipped to production")
        
        # Test summary
        test_items = [
            {"status": "Overdue", "id": "PROJECT-004"},
            {"status": "Due Today", "id": "SYSTEM-003-02"},
            {"status": "In Progress", "id": "SYSTEM-002-01"},
            {"status": "Upcoming", "id": "SYSTEM-005-01"}
        ]
        formatter.summary(test_items)
        
        print("\n" + "=" * 50)
    
    # Test quiet mode
    print(f"\n--- Testing {OutputLevel.QUIET.name} Level ---")
    formatter = CleanOutput(OutputLevel.QUIET)
    formatter.header("This should not appear in quiet mode")
    formatter.status(StatusType.DUE, "This should appear (DUE)")
    formatter.status(StatusType.ERROR, "This should appear (ERROR)")
    formatter.status(StatusType.SUCCESS, "This should not appear in quiet mode")
    
    print("\n✅ Clean output formatter test complete!")

if __name__ == "__main__":
    test_clean_output()