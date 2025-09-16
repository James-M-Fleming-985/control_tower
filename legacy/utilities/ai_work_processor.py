#!/usr/bin/env python3
"""
AI Work Queue Processor
Monitors the work queue and helps AI process implementation requests
"""

import os
import time
import glob

def check_work_queue():
    """Check for pending implementation requests"""
    work_queue_dir = "/tmp/ai_work_queue"
    if not os.path.exists(work_queue_dir):
        print("No work queue directory found")
        return []
    
    request_files = glob.glob(os.path.join(work_queue_dir, "*.request"))
    return request_files

def show_request_details(request_file):
    """Show details of an implementation request"""
    with open(request_file, 'r') as f:
        content = f.read()
    
    print("=" * 60)
    print("IMPLEMENTATION REQUEST")
    print("=" * 60)
    print(content)
    print("=" * 60)

def mark_complete(request_file, status="SUCCESS"):
    """Mark an implementation request as complete"""
    base_name = os.path.basename(request_file).replace('.request', '')
    completion_file = os.path.join(os.path.dirname(request_file), f"{base_name}.complete")
    
    with open(completion_file, 'w') as f:
        f.write(status)
    
    print(f"Marked as complete: {completion_file}")

def main():
    """Main work queue processor"""
    print("🤖 AI Work Queue Processor")
    print("Checking for pending implementation requests...")
    
    requests = check_work_queue()
    
    if not requests:
        print("No pending requests found")
        return
    
    print(f"Found {len(requests)} pending request(s):")
    
    for i, request_file in enumerate(requests, 1):
        print(f"\n{i}. {os.path.basename(request_file)}")
        show_request_details(request_file)
        
        response = input(f"\nMark as complete? (y/n/s for skip): ").lower().strip()
        if response == 'y':
            mark_complete(request_file, "SUCCESS")
        elif response == 's':
            print("Skipping...")
            continue
        else:
            mark_complete(request_file, "FAILED")

if __name__ == "__main__":
    main()