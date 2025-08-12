#!/bin/bash
# Download Latest PowerPoint Report
# Creates a download link for the latest PowerPoint presentation
# Usage: ./reports/download_latest_powerpoint.sh

echo "📥 DOWNLOAD LATEST POWERPOINT"
echo "============================"
echo "📅 Date: $(date '+%B %d, %Y')"
echo ""

# Find the latest PowerPoint file
LATEST_PPT=$(find /workspaces/control_tower/cloned_repos/ -name "*.pptx" -type f -printf "%T@ %p\n" | sort -n | tail -1 | cut -d' ' -f2-)

if [ -z "$LATEST_PPT" ]; then
    echo "❌ No PowerPoint files found in the workspace."
    exit 1
fi

FILE_SIZE=$(du -h "$LATEST_PPT" | cut -f1)
FILE_DATE=$(stat -c "%y" "$LATEST_PPT" | cut -d'.' -f1)
FILE_NAME=$(basename "$LATEST_PPT")

echo "📊 Found latest PowerPoint presentation:"
echo "   📄 Filename: $FILE_NAME"
echo "   📅 Created: $FILE_DATE"
echo "   📦 Size: $FILE_SIZE"
echo ""
echo "📂 Path: $LATEST_PPT"
echo ""
echo "🔄 To view and download:"
echo "1. Use File Explorer in VS Code sidebar"
echo "2. Navigate to: $LATEST_PPT"
echo "3. Right-click and select 'Download...'"
echo ""
echo "✅ Done!"
