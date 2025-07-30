"""
Core milestone management components
"""

from .repository_scanner import RepositoryScanner
from .milestone_detector import MilestoneChangeDetector

__all__ = ['RepositoryScanner', 'MilestoneChangeDetector']
