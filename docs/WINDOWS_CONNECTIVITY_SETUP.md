# Windows Connectivity Setup Guide

## Overview
This guide helps you establish connectivity between Linux/Codespaces and your Windows machine for automated MS Project workflows.

## Connection Methods

### Method 1: Network Shares (Admin Shares)
**Best for:** Local network connectivity

#### Windows Setup:
1. **Enable Admin Shares (C$)**:
   ```cmd
   net share c$=c:\ /grant:everyone,full
   ```

2. **Enable File and Printer Sharing**:
   - Open Control Panel → Network and Sharing Center
   - Click "Change advanced sharing settings"
   - Turn on "File and printer sharing"
   - Turn on "Network discovery"

3. **Configure Windows Firewall**:
   - Allow "File and Printer Sharing" through firewall
   - Or temporarily disable firewall for testing

4. **Test Access**:
   ```cmd
   # From another Windows machine
   dir \\172.22.177.213\c$
   ```

#### Linux/Codespaces Setup:
```bash
# Install SMB client tools (if needed)
sudo apt-get update
sudo apt-get install smbclient cifs-utils

# Test connectivity
smbclient //172.22.177.213/c$ -N -c "ls"
```

### Method 2: SSH/SCP Access
**Best for:** Secure remote access

#### Windows Setup:
1. **Install OpenSSH Server**:
   ```powershell
   # Run as Administrator
   Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
   Start-Service sshd
   Set-Service -Name sshd -StartupType 'Automatic'
   ```

2. **Configure SSH**:
   ```powershell
   # Allow SSH through firewall
   New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
   ```

3. **Test SSH**:
   ```bash
   ssh username@172.22.177.213
   ```

### Method 3: Cloud File Sync
**Best for:** Internet connectivity, simple setup

#### Setup Options:
1. **OneDrive/Google Drive**:
   - Install sync client on Windows
   - Point control_tower directories to synced folders
   - Files automatically sync between machines

2. **Manual Transfer**:
   - Copy files manually when needed
   - Use USB drives, email, etc.

## Current Configuration

Your `windows_target.conf` is set up for:
- **Host**: 172.22.177.213
- **Username**: James Fleming
- **Method**: Network Shares (Admin Shares)
- **Directories**:
  - MS Project: `C:\control_tower\ms_project\`
  - XML Workspace: `C:\control_tower\xml_workspace\`

## Testing Connectivity

Run the enhanced workflow to test all methods:
```bash
cd /workspaces/control_tower
python control_tower.py ms-project --action remote-sync
```

The system will automatically try:
1. UNC Network Shares (`//172.22.177.213/c$`)
2. SMB Client (if available)
3. SSH/SCP (if configured)
4. Manual fallback instructions

## Troubleshooting

### Network Shares Not Working
- Verify Windows file sharing is enabled
- Check firewall settings
- Ensure admin shares are accessible
- Try accessing `\\172.22.177.213\c$` from Windows Explorer

### SSH Not Working
- Verify OpenSSH server is running on Windows
- Check SSH port 22 is open in firewall
- Test SSH connection manually

### Network Issues
- Verify IP address is correct: `ipconfig` on Windows
- Check if machines are on same network
- Try ping test (if available)

## Production Recommendations

1. **For Security**: Use SSH/SCP method with key-based authentication
2. **For Simplicity**: Use network shares on trusted networks
3. **For Reliability**: Setup both methods as fallbacks
4. **For Cloud**: Use OneDrive/Google Drive sync

## Manual Workflow Fallback

If automated transfer fails, the system provides manual steps:
1. Copy the XML file from Linux to Windows manually
2. Import to MS Project using the enhanced execution layer
3. Export updated data back to Linux

The workflow continues with change management and PowerPoint generation regardless of connectivity method.
