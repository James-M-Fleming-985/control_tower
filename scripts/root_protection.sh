#!/bin/bash
# Root Protection System
# ====================
# 
# Prevents accidental file creation in repository root
# Provides warnings and redirects for proper file organization

# ANSI color codes for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if we're in repo root
check_repo_root() {
    if [ "$(pwd)" = "/workspaces/control_tower" ]; then
        return 0  # True - we are in root
    else
        return 1  # False - we are not in root
    fi
}

# Function to suggest proper location for different file types
suggest_proper_location() {
    local filename="$1"
    local extension="${filename##*.}"
    
    case "$extension" in
        "md")
            if [[ "$filename" == *"PROJECT-003"* ]] || [[ "$filename" == *"TDD"* ]]; then
                echo "projects/PROJECT-003 TDD ENFORCER/docs/"
            else
                echo "docs/"
            fi
            ;;
        "py")
            if [[ "$filename" == *"test_"* ]]; then
                echo "tests/"
            elif [[ "$filename" == *"PROJECT-003"* ]]; then
                echo "projects/PROJECT-003 TDD ENFORCER/src/"
            else
                echo "src/"
            fi
            ;;
        "json")
            echo "config/"
            ;;
        "sh")
            echo "scripts/"
            ;;
        *)
            echo "appropriate subdirectory"
            ;;
    esac
}

# Function to warn about root saves
warn_root_save() {
    local filename="$1"
    local suggested_location=$(suggest_proper_location "$filename")
    
    echo -e "${RED}⚠️  ROOT SAVE WARNING ⚠️${NC}"
    echo -e "${YELLOW}Attempting to save '${filename}' to repository root!${NC}"
    echo -e "${BLUE}Suggested location: ${suggested_location}${NC}"
    echo -e "${GREEN}Use: mkdir -p ${suggested_location} && mv ${filename} ${suggested_location}${NC}"
    echo ""
}

# Function to check for root save attempts
check_save_attempt() {
    if check_repo_root; then
        warn_root_save "$1"
        return 1
    fi
    return 0
}

# Export functions for use in other scripts
export -f check_repo_root
export -f suggest_proper_location
export -f warn_root_save
export -f check_save_attempt

echo -e "${GREEN}✅ Root Protection System loaded${NC}"
echo -e "${BLUE}Use 'check_save_attempt <filename>' before creating files${NC}"