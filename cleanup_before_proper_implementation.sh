#!/bin/bash
# Cleanup script - removes simplified/manual files before proper implementation
# Run this AFTER reviewing SYSTEM_BUILD_REQUIREMENTS.yaml

echo "=========================================="
echo "Cleaning up simplified implementation"
echo "=========================================="
echo ""

# 1. Backup current simplified build_system.py
if [ -f "/workspaces/control_tower/build_system.py" ]; then
    echo "✓ Backing up simplified build_system.py..."
    mv /workspaces/control_tower/build_system.py \
       /workspaces/control_tower/build_system_v2_simplified.py.backup
    echo "  → Saved as build_system_v2_simplified.py.backup"
fi

# 2. Remove manually created app files (keep main.py for reference)
echo ""
echo "✓ Removing manually created files..."

if [ -f "/workspaces/business_ventures/Causal_affect/SYSTEM-CA-006_feedback_iteration/src/backend/app/__init__.py" ]; then
    rm /workspaces/business_ventures/Causal_affect/SYSTEM-CA-006_feedback_iteration/src/backend/app/__init__.py
    echo "  → Deleted app/__init__.py (manually created)"
fi

if [ -f "/workspaces/business_ventures/Causal_affect/SYSTEM-CA-006_feedback_iteration/src/backend/app/config.py" ]; then
    rm /workspaces/business_ventures/Causal_affect/SYSTEM-CA-006_feedback_iteration/src/backend/app/config.py
    echo "  → Deleted app/config.py (manually created)"
fi

if [ -f "/workspaces/business_ventures/Causal_affect/SYSTEM-CA-006_feedback_iteration/src/backend/app/database.py" ]; then
    rm /workspaces/business_ventures/Causal_affect/SYSTEM-CA-006_feedback_iteration/src/backend/app/database.py
    echo "  → Deleted app/database.py (manually created)"
fi

# 3. Keep main.py for reference but move it
if [ -f "/workspaces/business_ventures/Causal_affect/SYSTEM-CA-006_feedback_iteration/src/backend/app/main.py" ]; then
    echo ""
    echo "✓ Preserving AI-generated main.py as reference..."
    mkdir -p /workspaces/business_ventures/Causal_affect/SYSTEM-CA-006_feedback_iteration/src/backend_reference
    mv /workspaces/business_ventures/Causal_affect/SYSTEM-CA-006_feedback_iteration/src/backend/app/main.py \
       /workspaces/business_ventures/Causal_affect/SYSTEM-CA-006_feedback_iteration/src/backend_reference/main.py.reference
    echo "  → Saved as backend_reference/main.py.reference"
fi

# 4. Remove empty backend directory
if [ -d "/workspaces/business_ventures/Causal_affect/SYSTEM-CA-006_feedback_iteration/src/backend/app" ]; then
    rmdir /workspaces/business_ventures/Causal_affect/SYSTEM-CA-006_feedback_iteration/src/backend/app 2>/dev/null || true
fi

if [ -d "/workspaces/business_ventures/Causal_affect/SYSTEM-CA-006_feedback_iteration/src/backend" ]; then
    rmdir /workspaces/business_ventures/Causal_affect/SYSTEM-CA-006_feedback_iteration/src/backend 2>/dev/null || true
fi

echo ""
echo "=========================================="
echo "Cleanup Complete!"
echo "=========================================="
echo ""
echo "Backups created:"
echo "  - build_system_v1_template_based.py.backup (old template version)"
echo "  - build_system_v2_simplified.py.backup (recent simplified version)"
echo "  - backend_reference/main.py.reference (AI-generated sample)"
echo ""
echo "Ready for proper implementation following SYSTEM_BUILD_REQUIREMENTS.yaml"
echo ""
