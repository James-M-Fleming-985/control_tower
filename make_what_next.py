#!/usr/bin/env python3
"""
Control Tower Phase 1 - Main Entry Point

This is the main entry point for the Control Tower Phase 1 "make what-next" command.
It integrates all 4 layers (UI, Business Logic, Data Access, Integration) to provide
a unified interface for discovering and prioritizing work items across repositories.

Phase 1 Integration:
- UI Layer (TR-UI-001): Terminal Output Formatter
- Business Logic Layer (TR-BL-001, TR-BL-002): Discovery Engine + Priority Calculator
- Data Access Layer (TR-DA-001, TR-DA-002): Repository Scanner + File System Interface
- Integration Layer (TR-IL-001, TR-IL-002): Git Integration + Command Line Interface

Usage:
    python make_what_next.py [options]
    make what-next [options]

Options:
    --repository=<name>     Filter to specific repository
    --repositories=<list>   Comma-separated list of repositories
    --json                  Output in JSON format
    --debug                 Enable debug mode
    --all                   Show all work items (not just due/overdue)

Examples:
    python make_what_next.py
    python make_what_next.py --repository=financial_security_dev
    python make_what_next.py --json --debug
    make what-next --repositories=financial_security_dev,investment_strategy

Author: Control Tower Development Team
Created: 2025-09-13
Phase: Phase 1 - Core Discovery
Status: Production Ready
"""

import sys
import os
import logging
from pathlib import Path

# Add src directory to Python path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from integration.command_line_interface import CommandLineInterface, main as cli_main


def setup_logging(debug: bool = False) -> None:
    """
    Set up logging configuration for the Control Tower system.
    
    Args:
        debug: Enable debug level logging if True
    """
    if debug:
        # Technical logging for debug mode
        log_level = logging.DEBUG
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    else:
        # User-friendly logging for normal mode
        log_level = logging.INFO
        log_format = '%(message)s'
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/control_tower.log', mode='a') if os.path.exists('logs') else logging.NullHandler()
        ]
    )


def validate_environment() -> bool:
    """
    Validate that the Control Tower environment is properly set up.
    
    Returns:
        bool: True if environment is valid, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    # Check if we're in the correct directory structure
    required_dirs = ['src', 'tests', 'cloned_repos']
    missing_dirs = [d for d in required_dirs if not os.path.exists(d)]
    
    if missing_dirs:
        logger.error(f"Missing required directories: {missing_dirs}")
        logger.error("Please run from the Control Tower root directory")
        return False
    
    # Check if source modules are available
    try:
        from business_logic.work_item_discovery_engine import WorkItemDiscoveryEngine
        from data_access.repository_scanner import RepositoryScanner
        from ui.terminal_formatter import TerminalFormatter
        from integration.git_integration import GitIntegration
        logger.debug("All source modules imported successfully")
        return True
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        return False


def print_banner() -> None:
    """Print the Control Tower banner"""
    banner = """
┌─────────────────────────────────────────────────────────────┐
│                    🏗️  CONTROL TOWER                        │
│                   Phase 1 - What Next                       │
│                                                             │
│  Intelligent Work Item Discovery & Prioritization System   │
│  Built with Professional TDD Methodology                   │
└─────────────────────────────────────────────────────────────┘
"""
    print(banner)


def main() -> int:
    """
    Main entry point for the Control Tower Phase 1 system.
    
    This function coordinates the entire Phase 1 workflow:
    1. Environment validation
    2. Logging setup
    3. Command line argument processing
    4. Integration layer execution
    5. Error handling and exit code management
    
    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    # Determine if debug mode is requested (quick check for banner/logging setup)
    debug_mode = '--debug' in sys.argv
    
    # Set up logging
    setup_logging(debug_mode)
    logger = logging.getLogger(__name__)
    
    try:
        # Print banner for non-JSON output
        if '--json' not in sys.argv:
            print_banner()
        
        # Validate environment
        if not validate_environment():
            logger.error("Environment validation failed")
            return 1
        
        logger.info("🔍 Scanning repositories for work items...")
        logger.debug(f"Command line arguments: {sys.argv[1:]}")
        
        # Delegate to the Integration Layer (TR-IL-002 Command Line Interface)
        # This demonstrates the 4-layer architecture working together:
        # CLI -> Business Logic -> Data Access -> File System/Git Integration
        exit_code = cli_main()
        
        if debug_mode:
            logger.info(f"Control Tower Phase 1 completed with exit code: {exit_code}")
        return exit_code
        
    except KeyboardInterrupt:
        logger.info("Control Tower interrupted by user")
        print("\n🛑 Control Tower interrupted by user", file=sys.stderr)
        return 130  # POSIX standard for SIGINT
        
    except Exception as e:
        logger.error(f"Unexpected error in Control Tower main: {e}", exc_info=True)
        print(f"🚨 Control Tower encountered an unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    """
    Entry point when called directly.
    
    This allows the Control Tower to be executed in multiple ways:
    1. python make_what_next.py [options]
    2. python -m make_what_next [options]  
    3. make what-next [options] (via Makefile)
    """
    exit_code = main()
    sys.exit(exit_code)