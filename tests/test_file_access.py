#!/usr/bin/env python3
"""
Quick test to verify MS Project file access
"""
import os

# Test the exact path - try both Windows and WSL paths
windows_path = r"D:\Downloads\ZnNi Line Development Plan-08.mpp"
wsl_path = "/mnt/d/Downloads/ZnNi Line Development Plan-08.mpp"

print(f"Testing Windows path: {windows_path}")
print(f"File exists: {os.path.exists(windows_path)}")

print(f"\nTesting WSL path: {wsl_path}")
print(f"File exists: {os.path.exists(wsl_path)}")

# Check what paths are available
print(f"\nChecking mount points:")
if os.path.exists("/mnt"):
    print(f"Mount points available: {os.listdir('/mnt')}")
    
if os.path.exists("/mnt/d"):
    print(f"D: drive mounted: True")
    if os.path.exists("/mnt/d/Downloads"):
        print(f"Downloads directory exists")
        files = os.listdir("/mnt/d/Downloads")
        mpp_files = [f for f in files if f.endswith('.mpp')]
        print(f"Found .mpp files: {mpp_files}")
    else:
        print("Downloads directory not found in /mnt/d/")
else:
    print("D: drive not mounted")
