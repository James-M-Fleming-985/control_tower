# Auto Export MS Project to XML
# Run this on your Windows machine to sync the latest project data
# 
# Usage: Right-click and "Run with PowerShell" or run from PowerShell:
# .\auto_export_xml.ps1

# Configuration
$MSProjectFile = "D:\Downloads\ZnNi Line Development Plan-08.mpp"
$OutputXMLPath = "C:\control_tower\xml_workspace\ZnNi Line Development Plan-08.xml"
$BackupPath = "C:\control_tower\backups"

Write-Host "🔄 Auto-exporting MS Project to XML..." -ForegroundColor Cyan

# Create directories if they don't exist
$OutputDir = Split-Path $OutputXMLPath -Parent
$BackupDir = $BackupPath
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null

# Create backup if XML already exists
if (Test-Path $OutputXMLPath) {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = Join-Path $BackupDir "ZnNi Line Development Plan-08.xml.backup.$timestamp"
    Copy-Item $OutputXMLPath $backupFile
    Write-Host "✅ Backup created: $backupFile" -ForegroundColor Green
}

try {
    # Check if MS Project file exists
    if (-not (Test-Path $MSProjectFile)) {
        Write-Host "❌ MS Project file not found: $MSProjectFile" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }

    # Open MS Project and export to XML
    Add-Type -AssemblyName "Microsoft.Office.Interop.MSProject"
    $msp = New-Object -ComObject MSProject.Application
    $msp.Visible = $false

    Write-Host "📂 Opening MS Project file..." -ForegroundColor Yellow
    $project = $msp.FileOpen($MSProjectFile)
    
    Write-Host "💾 Exporting to XML format..." -ForegroundColor Yellow
    $project.SaveAs($OutputXMLPath, 9)  # 9 = XML format
    
    $project.Close($false)
    $msp.Quit()
    
    # Verify the export
    if (Test-Path $OutputXMLPath) {
        $fileInfo = Get-Item $OutputXMLPath
        Write-Host "✅ Export successful!" -ForegroundColor Green
        Write-Host "📁 File: $OutputXMLPath" -ForegroundColor Green
        Write-Host "📊 Size: $([math]::Round($fileInfo.Length / 1MB, 2)) MB" -ForegroundColor Green
        Write-Host "⏰ Modified: $($fileInfo.LastWriteTime)" -ForegroundColor Green
        
        # Copy to network location if configured
        $NetworkPath = "\\172.22.177.213\c$\control_tower\xml_workspace\ZnNi Line Development Plan-08.xml"
        try {
            Copy-Item $OutputXMLPath $NetworkPath -Force
            Write-Host "🌐 Copied to network location: $NetworkPath" -ForegroundColor Green
        } catch {
            Write-Host "⚠️  Network copy failed (this is optional): $($_.Exception.Message)" -ForegroundColor Yellow
        }
        
        Write-Host "`n🎯 Next steps:" -ForegroundColor Cyan
        Write-Host "1. Your XML is now current and ready" -ForegroundColor White
        Write-Host "2. Run your Control Tower reports - they will now show current data" -ForegroundColor White
        Write-Host "3. Rerun this script whenever you make changes in MS Project" -ForegroundColor White
        
    } else {
        Write-Host "❌ Export failed - XML file not created" -ForegroundColor Red
    }

} catch {
    Write-Host "❌ Error during export: $($_.Exception.Message)" -ForegroundColor Red
    if ($msp) {
        try { $msp.Quit() } catch { }
    }
}

Write-Host "`nPress Enter to exit..." -ForegroundColor Gray
Read-Host
