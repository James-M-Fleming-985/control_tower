#!/usr/bin/env python3
"""
Quick Windows Connection Test
Test connectivity to your configured Windows machine
"""

import os
import configparser
import subprocess
import platform

def test_windows_connection():
    """Test connection to Windows machine with current configuration"""
    print("🔍 TESTING WINDOWS CONNECTION")
    print("=" * 50)
    
    # Read current config
    config_path = "/workspaces/control_tower/config/windows_target.conf"
    config = configparser.ConfigParser()
    config.read(config_path)
    
    host = config['windows_machine']['host'].strip('"')
    username = config['windows_machine']['username'].strip('"')
    use_shares = config.getboolean('network', 'use_admin_shares')
    
    print(f"📋 Configuration:")
    print(f"   Host: {host}")
    print(f"   Username: {username}")
    print(f"   Method: {'Network Shares' if use_shares else 'SSH'}")
    print()
    
    # Test basic connectivity
    print("🌐 Testing network connectivity...")
    try:
        result = subprocess.run(['ping', '-c', '2', host], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Ping successful!")
        else:
            print("❌ Ping failed")
            print(f"Error: {result.stderr}")
    except Exception as e:
        print(f"❌ Ping test failed: {e}")
    
    if use_shares:
        # Test SMB/CIFS connectivity
        print("\n📂 Testing network share access...")
        share_path = f"\\\\{host}\\c$"
        
        try:
            # Try to access the share path
            test_cmd = ['smbclient', '-L', host, '-U', username, '-N']
            result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                print("✅ SMB shares accessible!")
            else:
                print("⚠️  SMB access needs authentication")
                print("💡 You may need to provide credentials when accessing shares")
        except FileNotFoundError:
            print("⚠️  smbclient not available, but shares may still work")
        except Exception as e:
            print(f"⚠️  SMB test inconclusive: {e}")
    
    print("\n🎯 NEXT STEPS:")
    print("1. Ensure Windows machine has:")
    print("   - File and Printer Sharing enabled")
    print("   - C:\\control_tower\\xml_workspace directory created")
    print("   - C:\\control_tower\\ms_project directory created")
    print("2. Test the full workflow with: python control_tower.py ms-project --action remote-sync")
    
    return True

if __name__ == "__main__":
    test_windows_connection()
