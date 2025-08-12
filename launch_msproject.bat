@echo off
REM Auto-Launch MS Project with Latest Updates
REM ==========================================
REM This batch file automatically integrates updates and launches MS Project

echo.
echo 🚀 MS PROJECT AUTO-LAUNCHER
echo ========================================
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Run the Python auto-launch script
python auto_launch_msproject.py %*

REM Keep window open to see results
echo.
echo Press any key to close...
pause >nul
