#!/usr/bin/env python3
"""
Debug UI Layer update_progress method
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import time
from src.user_interface.verification_display import RealTimeProgressDisplay, ProgressData

def test_update_progress():
    """Test the update_progress method in detail"""
    
    print("=== UI Layer update_progress Debug ===")
    
    display = RealTimeProgressDisplay()
    
    try:
        # Start tracking
        verification_id = 'debug_test'
        print(f"1. Starting tracking for {verification_id}")
        
        track_result = display.start_tracking(verification_id)
        print(f"   Track result: {track_result}")
        print(f"   Display running: {display.running}")
        
        # Create progress data
        progress = ProgressData(
            verification_id=verification_id,
            stage='test_stage',
            progress_percent=25.0,
            message='Debug test message',
            timestamp=time.time(),
            details={'debug': True}
        )
        
        print(f"2. Created progress data: {progress.verification_id}")
        
        # Call update_progress
        print("3. Calling update_progress...")
        
        try:
            result = display.update_progress(progress)
            print(f"   Update result: {result}")
            print(f"   Result type: {type(result)}")
            
        except Exception as e:
            print(f"   Exception: {e}")
            import traceback
            traceback.print_exc()
        
        # Check counters
        print(f"4. Counters after update:")
        print(f"   Error count: {display.error_count}")
        print(f"   Total updates: {display.total_updates}")
        
        # Test multiple updates
        print("5. Testing multiple quick updates...")
        
        successful = 0
        for i in range(10):
            progress.progress_percent = i * 10.0
            progress.message = f"Update {i}"
            
            result = display.update_progress(progress)
            if result:
                successful += 1
                
        print(f"   Successful updates: {successful}/10")
        
    finally:
        display.stop_display_engine()
        print("6. Display engine stopped")

if __name__ == "__main__":
    test_update_progress()