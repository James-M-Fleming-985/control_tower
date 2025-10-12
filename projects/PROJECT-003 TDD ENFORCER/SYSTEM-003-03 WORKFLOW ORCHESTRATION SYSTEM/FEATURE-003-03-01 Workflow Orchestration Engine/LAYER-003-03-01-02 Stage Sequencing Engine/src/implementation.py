```python
import asyncio
from typing import Dict, List, Set, Optional
from enum import Enum
from dataclasses import dataclass, field


class StageType(Enum):
    PREREQUISITE = "prerequisite"
    CORE = "core"
    EXTENDED = "extended"


class StageStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class Stage:
    """Represents a workflow stage."""
    id: str
    name: str
    stage_type: StageType
    dependencies: List[str] = field(default_factory=list)
    status: StageStatus = StageStatus.PENDING


class DependencyValidationError(Exception):
    """Raised when stage dependencies are invalid."""
    pass


class DependencyNotMetError(Exception):
    """Raised when stage dependencies are not met."""
    pass


class StageSequencingEngine:
    """
    Orchestrates workflow execution by managing stage dependencies and sequencing.
    
    Ensures stages are executed in the correct order:
    Prerequisites → Core → Extended
    """
    
    def __init__(self):
        self.stages: Dict[str, Stage] = {}
        self.completed_stages: Set[str] = set()
        self.failed_stages: Set[str] = set()
        
    def add_stage(self, stage: Stage) -> None:
        """
        Add a stage to the workflow.
        
        Args:
            stage: The stage to add
        """
        self.stages[stage.id] = stage
        
    def validate_dependencies(self, stage_id: str) -> bool:
        """
        Validate that all dependencies for a stage exist and are valid.
        
        Args:
            stage_id: The ID of the stage to validate
            
        Returns:
            True if dependencies are valid
            
        Raises:
            DependencyValidationError: If dependencies are invalid
        """
        if stage_id not in self.stages:
            raise DependencyValidationError(f"Stage {stage_id} not found")
            
        stage = self.stages[stage_id]
        
        for dep_id in stage.dependencies:
            if dep_id not in self.stages:
                raise DependencyValidationError(
                    f"Dependency {dep_id} for stage {stage_id} not found"
                )
                
            dep_stage = self.stages[dep_id]
            
            # Validate stage type ordering
            if stage.stage_type == StageType.PREREQUISITE:
                if dep_stage.stage_type in [StageType.CORE, StageType.EXTENDED]:
                    raise DependencyValidationError(
                        f"Prerequisite stage {stage_id} cannot depend on "
                        f"{dep_stage.stage_type.value} stage {dep_id}"
                    )
            elif stage.stage_type == StageType.CORE:
                if dep_stage.stage_type == StageType.EXTENDED:
                    raise DependencyValidationError(
                        f"Core stage {stage_id} cannot depend on "
                        f"extended stage {dep_id}"
                    )
                    
        # Check for circular dependencies
        if self._has_circular_dependency(stage_id):
            raise DependencyValidationError(
                f"Circular dependency detected for stage {stage_id}"
            )
            
        return True
        
    def _has_circular_dependency(self, stage_id: str, visited: Optional[Set[str]] = None) -> bool:
        """
        Check if a stage has circular dependencies.
        
        Args:
            stage_id: The stage to check
            visited: Set of already visited stages
            
        Returns:
            True if circular dependency exists
        """
        if visited is None:
            visited = set()
            
        if stage_id in visited:
            return True
            
        visited.add(stage_id)
        
        stage = self.stages.get(stage_id)
        if not stage:
            return False
            
        for dep_id in stage.dependencies:
            if self._has_circular_dependency(dep_id, visited.copy()):
                return True
                
        return False
        
    def can_execute(self, stage_id: str) -> bool:
        """
        Check if a stage can be executed based on its dependencies.
        
        Args:
            stage_id: The ID of the stage to check
            
        Returns:
            True if the stage can be executed
        """
        if stage_id not in self.stages:
            return False
            
        stage = self.stages[stage_id]
        
        # Check if all dependencies are completed
        for dep_id in stage.dependencies:
            if dep_id not in self.completed_stages:
                return False
                
        return True
        
    def execute_stage(self, stage_id: str) -> None:
        """
        Execute a stage if its dependencies are met.
        
        Args:
            stage_id: The ID of the stage to execute
            
        Raises:
            DependencyNotMetError: If dependencies are not met
        """
        if stage_id not in self.stages:
            raise ValueError(f"Stage {stage_id} not found")
            
        # Validate dependencies first
        self.validate_dependencies(stage_id)
        
        if not self.can_execute(stage_id):
            stage = self.stages[stage_id]
            unmet_deps = [dep for dep in stage.dependencies 
                         if dep not in self.completed_stages]
            raise DependencyNotMetError(
                f"Cannot execute stage {stage_id}: "
                f"dependencies not met: {unmet_deps}"
            )
            
        stage = self.stages[stage_id]
        stage.status = StageStatus.RUNNING
        
        # Simulate execution
        stage.status = StageStatus.COMPLETED
        self.completed_stages.add(stage_id)
        
    def get_execution_sequence(self) -> List[str]:
        """
        Get the correct execution sequence for all stages.
        
        Returns:
            List of stage IDs in execution order
        """
        sequence = []
        remaining = set(self.stages.keys())
        processed = set()
        
        while remaining:
            # Find stages that can be executed
            executable = []
            
            for stage_id in remaining:
                stage = self.stages[stage_id]
                deps_met = all(dep in processed for dep in stage.dependencies)
                
                if deps_met:
                    executable.append(stage_id)
                    
            if not executable:
                # No stages can be executed - circular dependency or invalid state
                break
                
            # Sort by stage type priority: prerequisite -> core -> extended
            type_priority = {
                StageType.PREREQUISITE: 0,
                StageType.CORE: 1,
                StageType.EXTENDED: 2
            }
            
            executable.sort(key=lambda sid: (
                type_priority[self.stages[sid].stage_type],
                sid
            ))
            
            for stage_id in executable:
                sequence.append(stage_id)
                processed.add(stage_id)
                remaining.remove(stage_id)
                
        return sequence
        
    async def execute_workflow(self) -> Dict[str, StageStatus]:
        """
        Execute the entire workflow in the correct sequence.
        
        Returns:
            Dictionary mapping stage IDs to their final status
        """
        sequence = self.get_execution_sequence()
        results = {}
        
        for stage_id in sequence:
            try:
                self.execute_stage(stage_id)
                results[stage_id] = StageStatus.COMPLETED
            except Exception as e:
                stage = self.stages[stage_id]
                stage.status = StageStatus.FAILED
                self.failed_stages.add(stage_id)
                results[stage_id] = StageStatus.FAILED
                # Stop execution on failure
                break
                
        # Mark remaining stages as blocked
        for stage_id in self.stages:
            if stage_id not in results:
                self.stages[stage_id].status = StageStatus.BLOCKED
                results[stage_id] = StageStatus.BLOCKED
                
        return results
        
    def get_stage_status(self, stage_id: str) -> StageStatus:
        """
        Get the current status of a stage.
        
        Args:
            stage_id: The ID of the stage
            
        Returns:
            The stage's current status
        """
        if stage_id not in self.stages:
            raise ValueError(f"Stage {stage_id} not found")
            
        return self.stages[stage_id].status
        
    def reset(self) -> None:
        """Reset the engine state."""
        self.completed_stages.clear()
        self.failed_stages.clear()
        
        for stage in self.stages.values():
            stage.status = StageStatus.PENDING
```