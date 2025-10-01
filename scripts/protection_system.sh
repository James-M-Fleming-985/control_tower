#!/bin/bash
# File Organization Protection System
# ===================================
# Comprehensive enforcement system for repository file organization

set -e

REPO_ROOT="/workspaces/control_tower"
SCRIPTS_DIR="$REPO_ROOT/scripts"
LOGS_DIR="$REPO_ROOT/protection_logs"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Ensure logs directory exists
mkdir -p "$LOGS_DIR"

print_header() {
    echo -e "${BLUE}"
    echo "🛡️  CONTROL TOWER FILE ORGANIZATION PROTECTION"
    echo "=============================================="
    echo -e "${NC}"
}

install_protection_system() {
    echo -e "${YELLOW}📦 Installing Protection System...${NC}"
    
    # Install watchdog if not present (for file monitoring)
    if ! python3 -c "import watchdog" 2>/dev/null; then
        echo "Installing watchdog for file monitoring..."
        pip install watchdog
    fi
    
    # Make scripts executable
    chmod +x "$SCRIPTS_DIR/repo_file_guard.py"
    chmod +x "$SCRIPTS_DIR/file_organization_monitor.py"
    chmod +x "$REPO_ROOT/.git/hooks/pre-commit"
    
    echo -e "${GREEN}✅ Protection system installed${NC}"
}

start_file_monitor() {
    echo -e "${YELLOW}🔍 Starting File Organization Monitor...${NC}"
    
    # Check if already running
    if pgrep -f "file_organization_monitor.py" > /dev/null; then
        echo -e "${YELLOW}⚠️  Monitor already running${NC}"
        return 0
    fi
    
    # Start monitor in background
    cd "$REPO_ROOT"
    nohup python3 "$SCRIPTS_DIR/file_organization_monitor.py" \
        > "$LOGS_DIR/monitor.log" 2>&1 &
    
    MONITOR_PID=$!
    echo $MONITOR_PID > "$LOGS_DIR/monitor.pid"
    
    # Wait a moment and check if it started successfully
    sleep 2
    if ps -p $MONITOR_PID > /dev/null; then
        echo -e "${GREEN}✅ File monitor started (PID: $MONITOR_PID)${NC}"
    else
        echo -e "${RED}❌ Failed to start file monitor${NC}"
        return 1
    fi
}

stop_file_monitor() {
    echo -e "${YELLOW}🛑 Stopping File Organization Monitor...${NC}"
    
    if [ -f "$LOGS_DIR/monitor.pid" ]; then
        PID=$(cat "$LOGS_DIR/monitor.pid")
        if ps -p $PID > /dev/null; then
            kill $PID
            rm "$LOGS_DIR/monitor.pid"
            echo -e "${GREEN}✅ File monitor stopped${NC}"
        else
            echo -e "${YELLOW}⚠️  Monitor not running${NC}"
            rm -f "$LOGS_DIR/monitor.pid"
        fi
    else
        # Try to find and kill any running monitors
        pkill -f "file_organization_monitor.py" || true
        echo -e "${YELLOW}⚠️  No PID file found, attempted cleanup${NC}"
    fi
}

check_protection_status() {
    echo -e "${BLUE}📊 Protection System Status${NC}"
    echo "========================="
    
    # Git hooks
    if [ -f "$REPO_ROOT/.git/hooks/pre-commit" ] && [ -x "$REPO_ROOT/.git/hooks/pre-commit" ]; then
        echo -e "${GREEN}✅ Git pre-commit hook: Active${NC}"
    else
        echo -e "${RED}❌ Git pre-commit hook: Missing/Inactive${NC}"
    fi
    
    # File monitor
    if pgrep -f "file_organization_monitor.py" > /dev/null; then
        PID=$(pgrep -f "file_organization_monitor.py")
        echo -e "${GREEN}✅ File monitor: Running (PID: $PID)${NC}"
    else
        echo -e "${RED}❌ File monitor: Not running${NC}"
    fi
    
    # Guard script
    if [ -f "$SCRIPTS_DIR/repo_file_guard.py" ] && [ -x "$SCRIPTS_DIR/repo_file_guard.py" ]; then
        echo -e "${GREEN}✅ File guard script: Available${NC}"
    else
        echo -e "${RED}❌ File guard script: Missing/Inactive${NC}"
    fi
    
    # Recent violations
    if [ -f "$LOGS_DIR/URGENT_FILE_VIOLATION.txt" ]; then
        echo -e "${RED}⚠️  Recent violations detected - check $LOGS_DIR/URGENT_FILE_VIOLATION.txt${NC}"
    else
        echo -e "${GREEN}✅ No recent violations${NC}"
    fi
    
    echo ""
}

test_protection_system() {
    echo -e "${YELLOW}🧪 Testing Protection System...${NC}"
    
    # Create test file in root (should be caught)
    TEST_FILE="$REPO_ROOT/test_violation_file.py"
    echo "# This is a PROJECT-003 TDD test file" > "$TEST_FILE"
    echo "# Should trigger violation detection" >> "$TEST_FILE"
    
    # Wait a moment for monitor to detect
    sleep 3
    
    # Check if violation was caught
    if [ -f "$LOGS_DIR/URGENT_FILE_VIOLATION.txt" ]; then
        echo -e "${GREEN}✅ Violation detection working${NC}"
        
        # Clean up test file
        rm -f "$TEST_FILE"
        
        # Check if auto-fix worked
        PROJECT_SRC_DIR="$REPO_ROOT/projects/PROJECT-003 TDD ENFORCER/src"
        if [ -f "$PROJECT_SRC_DIR/test_violation_file.py" ]; then
            echo -e "${GREEN}✅ Auto-fix working${NC}"
            rm -f "$PROJECT_SRC_DIR/test_violation_file.py"
        fi
        
        # Clean violation log
        rm -f "$LOGS_DIR/URGENT_FILE_VIOLATION.txt"
    else
        echo -e "${RED}❌ Violation detection not working${NC}"
        rm -f "$TEST_FILE"
    fi
}

show_usage() {
    echo "Usage: $0 {install|start|stop|status|test|restart}"
    echo ""
    echo "Commands:"
    echo "  install  - Install the protection system"
    echo "  start    - Start file monitoring"
    echo "  stop     - Stop file monitoring"
    echo "  status   - Show protection system status"
    echo "  test     - Test the protection system"
    echo "  restart  - Restart file monitoring"
}

main() {
    print_header
    
    case "${1:-status}" in
        install)
            install_protection_system
            start_file_monitor
            ;;
        start)
            start_file_monitor
            ;;
        stop)
            stop_file_monitor
            ;;
        status)
            check_protection_status
            ;;
        test)
            test_protection_system
            ;;
        restart)
            stop_file_monitor
            sleep 2
            start_file_monitor
            ;;
        *)
            show_usage
            exit 1
            ;;
    esac
}

main "$@"