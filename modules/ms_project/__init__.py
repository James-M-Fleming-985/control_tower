"""
MS Project Integration Module
Handles MS Project XML parsing, task management, and automation
"""

from .ms_project_integration import MSProjectIntegration
from .contract_project_manager import ContractProjectManager

# Note: AutoSyncScheduler requires 'schedule' package - import only when needed
# from .auto_sync_scheduler import AutoSyncScheduler

__all__ = ['MSProjectIntegration', 'ContractProjectManager']
