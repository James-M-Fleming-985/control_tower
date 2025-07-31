#!/bin/bash
# PowerPoint Reports Overview
# Shows all powerpoint_reports folders across repos and their contents
# Usage: ./reports/show_powerpoint_reports.sh

echo "📊 POWERPOINT REPORTS OVERVIEW"
echo "============================="
echo "📅 Date: $(date '+%B %d, %Y')"
echo ""

cd /workspaces/control_tower/cloned_repos

echo "📂 Repository PowerPoint Reports Structure:"
echo ""

for repo in */; do
    if [ -d "$repo/powerpoint_reports" ]; then
        echo "📁 $repo"
        echo "   Location: cloned_repos/$repo/powerpoint_reports/"
        
        # Count files (excluding README)
        file_count=$(find "$repo/powerpoint_reports" -name "*.pptx" | wc -l)
        
        if [ $file_count -gt 0 ]; then
            echo "   📊 Presentations: $file_count"
            # Show presentation files
            find "$repo/powerpoint_reports" -name "*.pptx" -exec basename {} \; | sed 's/^/      /'
        else
            echo "   📊 Presentations: 0 (ready for future generation)"
        fi
        echo ""
    fi
done

echo "🎯 Usage:"
echo "• Download presentations from respective powerpoint_reports folders"
echo "• Each repo organized separately for easy access"
echo "• All generators centralized in Control Tower /reports"
