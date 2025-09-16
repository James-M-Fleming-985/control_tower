#!/usr/bin/env python3
"""
Test script for the new incremental backup system in Stage 5
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data_access.tdd_workflow_enforcer import TDDWorkflowEnforcer

def test_incremental_backup_system():
    """Test the new incremental backup and monitoring system"""
    
    print("🔧 Testing Incremental Backup System for Stage 5")
    print("=" * 60)
    
    # Initialize the enforcer
    enforcer = TDDWorkflowEnforcer()
    
    print("\n📋 1. Testing incremental monitoring...")
    
    # Run the incremental monitoring
    progress_data = enforcer.monitor_green_phase_progress("control_tower_failing_tests")
    
    print(f"\n📊 RESULTS:")
    print(f"   Total Tests: {progress_data.get('total_tests', 0)}")
    print(f"   Passing: {progress_data.get('passing_count', 0)}")
    print(f"   Failing: {progress_data.get('failing_count', 0)}")
    print(f"   Progress: {progress_data.get('progress_percentage', 0):.1f}%")
    print(f"   Backups Created: {len(progress_data.get('backup_paths', []))}")
    
    if progress_data.get('backup_paths'):
        print(f"\n💾 BACKUP FILES CREATED:")
        for backup_path in progress_data['backup_paths']:
            print(f"   📁 {os.path.basename(backup_path)}")
    
    print("\n📋 2. Testing Stage 5 with new backup system...")
    
    # Run Stage 5 with the new system
    stage5_result = enforcer.stage_gate_5_green_phase_implementation_quality_verification()
    
    print(f"\n🏁 STAGE 5 RESULT:")
    print(f"   Status: {stage5_result.status}")
    print(f"   Can Proceed: {stage5_result.can_proceed}")
    if hasattr(stage5_result, 'metadata') and stage5_result.metadata:
        metadata = stage5_result.metadata
        print(f"   Total Tests: {metadata.get('total_tests', 'N/A')}")
        print(f"   Passing: {metadata.get('passing_count', 'N/A')}")
        print(f"   Backups: {metadata.get('incremental_backups_created', 'N/A')}")
    
    print("\n✅ Incremental backup system test complete!")
    
    return progress_data, stage5_result

if __name__ == "__main__":
    test_incremental_backup_system()