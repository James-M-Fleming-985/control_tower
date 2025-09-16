#!/usr/bin/env python3
"""
Control Tower Milestone Management Module
Universal milestone change detection and reporting across all repositories

This module provides:
- Multi-repository XML file discovery
- Universal milestone change detection
- Cross-project PowerPoint reporting
- Automated workflow management
"""

from .core.repository_scanner import RepositoryScanner
from .core.milestone_detector import MilestoneChangeDetector
from .reporting.safran_powerpoint_generator import SafranPowerPointGenerator
from .automation.workflow_manager import WorkflowManager

__version__ = "1.0.0"
__author__ = "Control Tower System"

# Main classes for easy import
__all__ = [
    'RepositoryScanner',
    'MilestoneChangeDetector', 
    'PowerPointGenerator',
    'WorkflowManager'
]

def get_version():
    """Get the module version"""
    return __version__

def scan_all_repositories():
    """Quick function to scan all repositories for XML files"""
    scanner = RepositoryScanner()
    return scanner.scan_all_repositories()

def detect_changes_across_repos():
    """Quick function to detect changes across all repositories"""
    detector = MilestoneChangeDetector()
    return detector.scan_all_repositories_for_changes()
