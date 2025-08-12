# Auto-Launch MS Project with Latest Updates
# ==========================================
# PowerShell script for Windows users

Write-Host ""
Write-Host "🚀 MS PROJECT AUTO-LAUNCHER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get the script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Change to script directory
Set-Location $ScriptDir

# Run the Python auto-launch script
try {
    python auto_launch_msproject.py @args
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Success!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  See output above for details" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Error running script: $_" -ForegroundColor Red
    Write-Host "💡 Make sure Python is installed and in PATH" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to close..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
