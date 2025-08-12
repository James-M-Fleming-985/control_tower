#!/usr/bin/env python3
"""
Remote Execution Utilities for Auto Sync
Simple utilities for remote Windows execution from Linux/Codespaces
"""

import subprocess
import os

def execute_remote_sync(config, local_xml_file, description):
    """
    Execute remote sync using the push_project_update.py framework
    
    Args:
        config: Windows target configuration
        local_xml_file: Local XML file path
        description: Description for the sync operation
        
    Returns:
        bool: True if successful
    """
    try:
        # Use the existing push_project_update.py remote execution
        cmd = f'python /workspaces/control_tower/push_project_update.py --description "{description}" --project "ZnNi Line Development Plan"'
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd='/workspaces/control_tower')
        
        if result.returncode == 0:
            return True
        else:
            print(f"Remote sync failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Remote sync error: {e}")
        return False

def copy_xml_to_windows(local_xml_file, config):
    """Copy XML file to Windows machine using SCP"""
    try:
        windows_xml_path = config['main_project_file']
        
        if config['use_admin_shares']:
            # Use Windows Admin Shares
            unc_path = windows_xml_path.replace('C:', f'//{config["host"]}/c$').replace('\\', '/')
            copy_command = f"cp '{local_xml_file}' '{unc_path}'"
        else:
            # Use SCP
            if config['username']:
                scp_target = f"{config['username']}@{config['host']}:{windows_xml_path}"
            else:
                scp_target = f"{config['host']}:{windows_xml_path}"
            
            copy_command = f"scp -i {config['ssh_key']} '{local_xml_file}' '{scp_target}'"
        
        result = subprocess.run(copy_command, shell=True, capture_output=True, text=True)
        return result.returncode == 0
        
    except Exception:
        return False

def copy_xml_from_windows(config, local_xml_file):
    """Copy updated XML file back from Windows machine"""
    try:
        windows_xml_path = config['main_project_file']
        
        if config['use_admin_shares']:
            # Use Windows Admin Shares
            unc_path = windows_xml_path.replace('C:', f'//{config["host"]}/c$').replace('\\', '/')
            copy_command = f"cp '{unc_path}' '{local_xml_file}'"
        else:
            # Use SCP
            if config['username']:
                scp_source = f"{config['username']}@{config['host']}:{windows_xml_path}"
            else:
                scp_source = f"{config['host']}:{windows_xml_path}"
            
            copy_command = f"scp -i {config['ssh_key']} '{scp_source}' '{local_xml_file}'"
        
        result = subprocess.run(copy_command, shell=True, capture_output=True, text=True)
        return result.returncode == 0
        
    except Exception:
        return False
