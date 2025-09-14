"""
Work Item Discovery Engine - TR-BL-001 implementation

Core business logic for discovering, processing, and prioritizing work items from repositories.
This is the main orchestrator that integrates Repository Scanner, File System Interface, and Priority Calculator.

Architecture:
- Follows Single Responsibility Principle with clear separation of concerns
- Integrates seamlessly with Data Access Layer and UI Layer
- Provides comprehensive error handling and logging
- Optimized for performance with lazy evaluation and efficient processing

Acceptance Criteria:
- BL-001: Discovers work items from all repository types
- BL-002: Correctly identifies due and overdue items
- BL-003: Determines project type (Application vs Standard Delivery)
- BL-004: Extracts hierarchical context information
- BL-005: Applies basic priority sorting (overdue first, then due today)
- BL-006: Handles parsing errors gracefully
"""

import logging
from datetime import date
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from src.business_logic.work_item_model import WorkItem, Priority, RequirementLevel, ProjectType, ItemStatus
from src.business_logic.priority_calculator import BasicPriorityCalculator
from src.data_access.repository_scanner import RepositoryScanner, RawRequirement


# Configure logging for better debugging and monitoring
logger = logging.getLogger(__name__)


class WorkItemDiscoveryEngine:
    """
    Core business logic engine for work item discovery and processing.
    
    Orchestrates the discovery workflow by coordinating Repository Scanner,
    Priority Calculator, and work item conversion logic to produce prioritized
    work items for the control tower system.
    
    Design Patterns:
    - Facade Pattern: Provides simplified interface to complex subsystem
    - Strategy Pattern: Uses Priority Calculator for flexible prioritization
    - Template Method: Standardized workflow with customizable steps
    """
    
    # Repository type classification for project type determination
    APPLICATION_REPOSITORIES = {
        'financial_security_dev',
        'opti_royale', 
        'home_improvements',
        'relationship_building'
    }
    
    STANDARD_DELIVERY_REPOSITORIES = {
        'lims_concept_actual',
        'contract_projects'
    }
    
    def __init__(self):
        """Initialize the discovery engine with required dependencies"""
        self.logger = logging.getLogger(__name__)
        self.repository_scanner = RepositoryScanner()
        self.priority_calculator = BasicPriorityCalculator()
        
        # Performance tracking
        self._stats = {
            'repositories_scanned': 0,
            'work_items_discovered': 0,
            'work_items_filtered': 0,
            'errors_encountered': 0
        }
    
    def discover_work_items(self, repositories: List[str]) -> List[WorkItem]:
        """
        Discover work items from the specified repositories.
        
        Args:
            repositories: List of repository paths to scan
            
        Returns:
            List of WorkItem objects discovered from all repositories
            
        Acceptance Criteria: BL-001, BL-006
        """
        try:
            if not repositories:
                self.logger.warning("No repositories provided for discovery")
                return []
            
            self._stats['repositories_scanned'] = len(repositories)
            
            # Scan repositories for raw requirements
            raw_requirements = self.repository_scanner.scan_repositories(repositories)
            
            # Convert raw requirements to work items with error handling
            work_items = self._convert_raw_requirements_to_work_items(raw_requirements)
            
            # Assign status to all items based on due dates
            self._assign_status_to_all_items(work_items)
            
            self._stats['work_items_discovered'] = len(work_items)
            self.logger.debug(f"Discovered {len(work_items)} work items from {len(repositories)} repositories")  # Changed to debug
            
            return work_items
            
        except Exception as e:
            self.logger.error(f"Error during work item discovery: {e}")
            self._stats['errors_encountered'] += 1
            return []  # Graceful handling - return empty list instead of crashing
    
    def _assign_status_to_all_items(self, items: List[WorkItem]) -> None:
        """
        Assign status to all work items based on their due dates.
        
        This ensures proper color coding in terminal output regardless of filtering.
        
        Args:
            items: List of work items to assign status to
        """
        try:
            today = date.today()
            
            for item in items:
                if not item.due_date:
                    item.status = ItemStatus.UPCOMING  # No due date = upcoming
                elif item.due_date < today:
                    item.status = ItemStatus.OVERDUE
                elif item.due_date == today:
                    item.status = ItemStatus.DUE_TODAY
                else:
                    item.status = ItemStatus.UPCOMING
                    
        except Exception as e:
            self.logger.error(f"Error assigning status to work items: {e}")
    
    def _convert_raw_requirements_to_work_items(self, raw_requirements: List[RawRequirement]) -> List[WorkItem]:
        """
        Convert raw requirements to work items with comprehensive error handling.
        
        Args:
            raw_requirements: List of raw requirements from repository scan
            
        Returns:
            List of successfully converted work items
        """
        work_items = []
        
        for raw_req in raw_requirements:
            try:
                work_item = self._convert_to_work_item(raw_req)
                if work_item:  # Only add valid work items
                    work_items.append(work_item)
            except Exception as e:
                self.logger.warning(f"Error converting requirement to work item: {raw_req.file_path}: {e}")
                self._stats['errors_encountered'] += 1
                continue  # Skip invalid items but continue processing
        
        return work_items
    
    def filter_due_and_overdue(self, items: List[WorkItem]) -> List[WorkItem]:
        """
        Filter work items to only include those that are due today or overdue.
        
        Args:
            items: List of work items to filter
            
        Returns:
            Filtered list containing only due and overdue items
            
        Acceptance Criteria: BL-002
        """
        try:
            today = date.today()
            filtered_items = []
            
            for item in items:
                if not item.due_date:
                    continue  # Skip items without due dates
                
                if item.due_date < today:
                    # Overdue item
                    item.status = ItemStatus.OVERDUE
                    filtered_items.append(item)
                elif item.due_date == today:
                    # Due today item
                    item.status = ItemStatus.DUE_TODAY
                    filtered_items.append(item)
                # Skip future items (item.due_date > today)
            
            self.logger.info(f"Filtered to {len(filtered_items)} due/overdue items from {len(items)} total")
            return filtered_items
            
        except Exception as e:
            self.logger.error(f"Error filtering due and overdue items: {e}")
            return []
    
    def apply_basic_prioritization(self, items: List[WorkItem]) -> List[WorkItem]:
        """
        Apply basic prioritization logic using the Priority Calculator.
        
        Args:
            items: List of work items to prioritize
            
        Returns:
            Prioritized list with overdue items first, then due today items
            
        Acceptance Criteria: BL-005
        """
        try:
            return self.priority_calculator.sort_by_priority(items)
        except Exception as e:
            self.logger.error(f"Error applying prioritization: {e}")
            return items  # Return original order if prioritization fails
    
    def determine_project_type(self, item: WorkItem) -> ProjectType:
        """
        Determine the project type based on repository and content characteristics.
        
        Args:
            item: Work item to analyze
            
        Returns:
            ProjectType (APPLICATION or STANDARD_DELIVERY)
            
        Acceptance Criteria: BL-003
        """
        try:
            repository_name = item.repository.lower()
            
            # Application project patterns
            application_indicators = [
                'financial_security_dev',
                'opti_royale', 
                'home_improvements',
                'relationship_building'
            ]
            
            # Standard delivery project patterns
            standard_delivery_indicators = [
                'lims_concept_actual',
                'contract_projects',
                'milestone',
                'documentation'
            ]
            
            # Check repository patterns
            for indicator in application_indicators:
                if indicator in repository_name:
                    return ProjectType.APPLICATION
            
            for indicator in standard_delivery_indicators:
                if indicator in repository_name:
                    return ProjectType.STANDARD_DELIVERY
            
            # Check requirement level patterns
            if item.requirement_level in [RequirementLevel.FR, RequirementLevel.PR]:
                return ProjectType.APPLICATION
            elif item.requirement_level in [RequirementLevel.MR, RequirementLevel.SR]:
                return ProjectType.STANDARD_DELIVERY
            
            # Default to APPLICATION if uncertain
            return ProjectType.APPLICATION
            
        except Exception as e:
            self.logger.warning(f"Error determining project type for {item.id}: {e}")
            return ProjectType.APPLICATION  # Safe default
    
    def _convert_to_work_item(self, raw_requirement: RawRequirement) -> Optional[WorkItem]:
        """
        Convert a raw requirement to a WorkItem object.
        
        Args:
            raw_requirement: Raw requirement data from repository scan
            
        Returns:
            WorkItem object or None if conversion fails
            
        Acceptance Criteria: BL-001, BL-004, BL-006
        """
        try:
            # Get title from metadata or extract from content
            title = raw_requirement.metadata.title if raw_requirement.metadata and raw_requirement.metadata.title else "Unknown Item"
            
            # Validate essential fields
            if not title or not raw_requirement.file_path:
                self.logger.warning(f"Skipping requirement with missing title or file path: {raw_requirement.file_path}")
                return None
            
            # Generate work item ID
            work_item_id = self._generate_work_item_id(raw_requirement)
            
            # Extract hierarchical context
            hierarchy_context = self._extract_hierarchical_context(raw_requirement)
            
            # Convert priority
            priority = raw_requirement.metadata.priority if raw_requirement.metadata else Priority.MEDIUM
            
            # Convert requirement level
            req_level = raw_requirement.metadata.requirement_level if raw_requirement.metadata else RequirementLevel.FR
            
            # Create work item
            work_item = WorkItem(
                id=work_item_id,
                title=title,
                description=raw_requirement.content[:200] + "..." if len(raw_requirement.content) > 200 else raw_requirement.content,
                due_date=raw_requirement.metadata.due_date if raw_requirement.metadata else None,
                priority=priority,
                effort_estimate=raw_requirement.metadata.effort_estimate if raw_requirement.metadata else "Unknown",
                requirement_level=req_level,
                project_type=ProjectType.APPLICATION,  # Will be determined later
                repository=hierarchy_context['repository'],
                system_name=hierarchy_context['system'],
                project_name=hierarchy_context['project'],
                layer_or_milestone=hierarchy_context['layer_or_milestone'],
                hierarchy_path=hierarchy_context['hierarchy_path'],
                status=ItemStatus.NOT_DUE  # Will be updated by filtering
            )
            
            # Determine project type
            work_item.project_type = self.determine_project_type(work_item)
            
            return work_item
            
        except Exception as e:
            self.logger.error(f"Error converting raw requirement to work item: {raw_requirement.file_path}: {e}")
            return None
    
    def _extract_hierarchical_context(self, raw_requirement: RawRequirement) -> dict:
        """
        Extract hierarchical context from raw requirement.
        
        Args:
            raw_requirement: Raw requirement to extract context from
            
        Returns:
            Dictionary with hierarchy components
            
        Acceptance Criteria: BL-004
        """
        try:
            file_path = raw_requirement.file_path
            content = raw_requirement.content
            title = raw_requirement.metadata.title if raw_requirement.metadata and raw_requirement.metadata.title else "Unknown"
            
            # Extract repository name from file path
            repository = "unknown"
            if "/cloned_repos/" in file_path:
                repo_part = file_path.split("/cloned_repos/")[1]
                repository = repo_part.split("/")[0] if "/" in repo_part else repo_part
            elif "/" in file_path:
                # Handle test paths like /test/financial_security_dev/
                path_parts = file_path.strip("/").split("/")
                if len(path_parts) >= 2:
                    repository = path_parts[1]  # Second part should be repo name
            
            # Extract system name from content or file path
            system_name = "Unknown System"
            if "**System**:" in content:
                system_lines = [line for line in content.split('\n') if "**System**:" in line]
                if system_lines:
                    system_name = system_lines[0].split("**System**:")[1].strip()
            elif repository:
                # Derive system name from repository
                system_name = repository.replace("_", " ").title()
            
            # Extract project name from content or derive from repository
            project_name = "Unknown Project"
            if "**Project**:" in content:
                project_lines = [line for line in content.split('\n') if "**Project**:" in line]
                if project_lines:
                    project_name = project_lines[0].split("**Project**:")[1].strip()
            elif repository:
                # Derive project name from repository
                project_name = repository.replace("_dev", "").replace("_", " ").title()
            
            # Determine layer or milestone
            layer_or_milestone = "Unknown Layer"
            if "/features/" in file_path:
                layer_or_milestone = "Business Logic Layer"
            elif "/milestones/" in file_path:
                layer_or_milestone = "Implementation Milestone"
            elif "data" in title.lower() or "database" in title.lower():
                layer_or_milestone = "Data Access Layer"
            elif "ui" in title.lower() or "interface" in title.lower():
                layer_or_milestone = "UI Layer"
            
            # Build hierarchy path
            hierarchy_path = f"{title} → {system_name} → {project_name} → {repository}"
            
            return {
                'repository': repository,
                'system': system_name,
                'project': project_name,
                'layer_or_milestone': layer_or_milestone,
                'hierarchy_path': hierarchy_path
            }
            
        except Exception as e:
            self.logger.warning(f"Error extracting hierarchical context: {e}")
            title = raw_requirement.metadata.title if raw_requirement.metadata and raw_requirement.metadata.title else "Unknown"
            return {
                'repository': 'unknown',
                'system': 'Unknown System',
                'project': 'Unknown Project',
                'layer_or_milestone': 'Unknown Layer',
                'hierarchy_path': f"{title} → Unknown → Unknown → unknown"
            }
    
    def _generate_work_item_id(self, raw_requirement: RawRequirement) -> str:
        """Generate a unique work item ID from the raw requirement."""
        try:
            # Extract repository name
            file_path = raw_requirement.file_path
            if "/cloned_repos/" in file_path:
                repo_part = file_path.split("/cloned_repos/")[1]
                repository = repo_part.split("/")[0] if "/" in repo_part else repo_part
            elif "/" in file_path:
                # Handle test paths like /test/financial_security_dev/
                path_parts = file_path.strip("/").split("/")
                if len(path_parts) >= 2:
                    repository = path_parts[1]  # Second part should be repo name
                else:
                    repository = "unknown"
            else:
                repository = "unknown"
            
            # Extract requirement type
            req_type = "FEATURE"
            if "/milestones/" in file_path:
                req_type = "MILESTONE"
            elif raw_requirement.metadata and raw_requirement.metadata.requirement_level:
                req_type = raw_requirement.metadata.requirement_level.value
            
            # Generate ID with repository prefix
            repo_prefix = repository.upper().replace("_", "-")[:8]
            title = raw_requirement.metadata.title if raw_requirement.metadata and raw_requirement.metadata.title else "UNKNOWN"
            title_part = title.replace(" ", "-").upper()[:15]
            
            return f"{repo_prefix}-{req_type}-{title_part}"
            
        except Exception as e:
            self.logger.warning(f"Error generating work item ID: {e}")
            return f"UNKNOWN-ITEM-{hash(raw_requirement.file_path) % 10000}"