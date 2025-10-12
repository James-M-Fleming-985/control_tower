```python
import json
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, asdict, field
from datetime import datetime
import os


class WorkflowStage(Enum):
    """Enumeration of workflow stages."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StateTransitionError(Exception):
    """Exception raised for invalid state transitions."""
    pass


@dataclass
class StageState:
    """Represents the state of a single workflow stage."""
    name: str
    status: str = WorkflowStage.PENDING.value
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowState:
    """Represents the complete state of a workflow."""
    workflow_id: str
    stages: List[StageState]
    current_stage_index: int = 0
    overall_status: str = WorkflowStage.PENDING.value
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow state to dictionary."""
        return {
            'workflow_id': self.workflow_id,
            'stages': [asdict(stage) for stage in self.stages],
            'current_stage_index': self.current_stage_index,
            'overall_status': self.overall_status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowState':
        """Create workflow state from dictionary."""
        stages = [StageState(**stage) for stage in data['stages']]
        return cls(
            workflow_id=data['workflow_id'],
            stages=stages,
            current_stage_index=data['current_stage_index'],
            overall_status=data['overall_status'],
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            metadata=data.get('metadata', {})
        )


class WorkflowStateManager:
    """Manages workflow state with persistence and validation."""
    
    # Valid state transitions
    VALID_TRANSITIONS = {
        WorkflowStage.PENDING.value: [WorkflowStage.RUNNING.value, WorkflowStage.CANCELLED.value],
        WorkflowStage.RUNNING.value: [WorkflowStage.COMPLETED.value, WorkflowStage.FAILED.value, WorkflowStage.CANCELLED.value],
        WorkflowStage.COMPLETED.value: [],
        WorkflowStage.FAILED.value: [WorkflowStage.RUNNING.value],
        WorkflowStage.CANCELLED.value: []
    }

    def __init__(self, persistence_path: Optional[str] = None):
        """
        Initialize workflow state manager.
        
        Args:
            persistence_path: Path to persist workflow states
        """
        self.persistence_path = persistence_path
        self.workflows: Dict[str, WorkflowState] = {}
        
        if persistence_path and os.path.exists(persistence_path):
            self._load_all_states()

    def initialize_workflow(self, workflow_id: str, stage_names: List[str], 
                          metadata: Optional[Dict[str, Any]] = None) -> WorkflowState:
        """
        Initialize a new workflow with all stages.
        
        Args:
            workflow_id: Unique identifier for the workflow
            stage_names: List of stage names
            metadata: Optional metadata for the workflow
            
        Returns:
            Initialized WorkflowState
        """
        stages = [StageState(name=name) for name in stage_names]
        workflow = WorkflowState(
            workflow_id=workflow_id,
            stages=stages,
            metadata=metadata or {}
        )
        self.workflows[workflow_id] = workflow
        self._persist_state(workflow)
        return workflow

    def get_workflow(self, workflow_id: str) -> Optional[WorkflowState]:
        """
        Get workflow state by ID.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            WorkflowState if found, None otherwise
        """
        return self.workflows.get(workflow_id)

    def update_stage_status(self, workflow_id: str, stage_index: int, 
                           new_status: str, error: Optional[str] = None) -> WorkflowState:
        """
        Update the status of a specific stage.
        
        Args:
            workflow_id: Workflow identifier
            stage_index: Index of the stage to update
            new_status: New status for the stage
            error: Optional error message if status is FAILED
            
        Returns:
            Updated WorkflowState
            
        Raises:
            ValueError: If workflow not found or stage index invalid
            StateTransitionError: If transition is invalid
        """
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        if stage_index < 0 or stage_index >= len(workflow.stages):
            raise ValueError(f"Invalid stage index: {stage_index}")
        
        stage = workflow.stages[stage_index]
        
        # Validate transition
        if not self._is_valid_transition(stage.status, new_status):
            raise StateTransitionError(
                f"Invalid transition from {stage.status} to {new_status}"
            )
        
        # Update stage
        old_status = stage.status
        stage.status = new_status
        
        if new_status == WorkflowStage.RUNNING.value and not stage.started_at:
            stage.started_at = datetime.utcnow().isoformat()
        elif new_status in [WorkflowStage.COMPLETED.value, WorkflowStage.FAILED.value]:
            stage.completed_at = datetime.utcnow().isoformat()
        
        if error:
            stage.error = error
        
        # Update workflow overall status
        self._update_overall_status(workflow)
        workflow.updated_at = datetime.utcnow().isoformat()
        
        self._persist_state(workflow)
        return workflow

    def advance_to_next_stage(self, workflow_id: str) -> WorkflowState:
        """
        Advance workflow to the next stage.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Updated WorkflowState
            
        Raises:
            ValueError: If workflow not found or already at last stage
        """
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        current_index = workflow.current_stage_index
        
        if current_index >= len(workflow.stages) - 1:
            raise ValueError("Already at last stage")
        
        # Mark current stage as completed if not already
        current_stage = workflow.stages[current_index]
        if current_stage.status != WorkflowStage.COMPLETED.value:
            self.update_stage_status(workflow_id, current_index, 
                                    WorkflowStage.COMPLETED.value)
        
        # Move to next stage
        workflow.current_stage_index += 1
        workflow.updated_at = datetime.utcnow().isoformat()
        
        self._persist_state(workflow)
        return workflow

    def get_current_stage(self, workflow_id: str) -> Optional[StageState]:
        """
        Get the current stage of a workflow.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Current StageState or None if workflow not found
        """
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return None
        
        if workflow.current_stage_index < len(workflow.stages):
            return workflow.stages[workflow.current_stage_index]
        return None

    def is_workflow_complete(self, workflow_id: str) -> bool:
        """
        Check if workflow is complete.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            True if workflow is complete, False otherwise
        """
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return False
        
        return workflow.overall_status == WorkflowStage.COMPLETED.value

    def _is_valid_transition(self, from_status: str, to_status: str) -> bool:
        """
        Validate if a state transition is allowed.
        
        Args:
            from_status: Current status
            to_status: Target status
            
        Returns:
            True if transition is valid, False otherwise
        """
        if from_status == to_status:
            return True
        
        valid_next_states = self.VALID_TRANSITIONS.get(from_status, [])
        return to_status in valid_next_states

    def _update_overall_status(self, workflow: WorkflowState) -> None:
        """
        Update the overall workflow status based on stage statuses.
        
        Args:
            workflow: WorkflowState to update
        """
        stages = workflow.stages
        
        # Check if any stage failed
        if any(stage.status == WorkflowStage.FAILED.value for stage in stages):
            workflow.overall_status = WorkflowStage.FAILED.value
        # Check if all stages completed
        elif all(stage.status == WorkflowStage.COMPLETED.value for stage in stages):
            workflow.overall_status = WorkflowStage.COMPLETED.value
        # Check if any stage is running
        elif any(stage.status == WorkflowStage.RUNNING.value for stage in stages):
            workflow.overall_status = WorkflowStage.RUNNING.value
        # Check if cancelled
        elif any(stage.status == WorkflowStage.CANCELLED.value for stage in stages):
            workflow.overall_status = WorkflowStage.CANCELLED.value
        else:
            workflow.overall_status = WorkflowStage.PENDING.value

    def _persist_state(self, workflow: WorkflowState) -> None:
        """
        Persist workflow state to storage.
        
        Args:
            workflow: WorkflowState to persist
        """
        if not self.persistence_path:
            return
        
        os.makedirs(os.path.dirname(self.persistence_path) if os.path.dirname(self.persistence_path) else '.', exist_ok=True)
        
        # Load existing states
        all_states = {}
        if os.path.exists(self.persistence_path):
            try:
                with open(self.persistence_path, 'r') as f:
                    all_states = json.load(f)
            except (json.JSONDecodeError, IOError):
                all_states = {}
        
        # Update with current workflow
        all_states[workflow.workflow_id] = workflow.to_dict()
        
        # Write back
        with open(self.persistence_path, 'w') as f:
            json.dump(all_states, f, indent=2)

    def _load_all_states(self) -> None:
        """Load all workflow states from persistence."""
        if not self.persistence_path or not os.path.exists(self.persistence_path):
            return
        
        try:
            with open(self.persistence_path, 'r') as f:
                all_states = json.load(f)
            
            for workflow_id, state_data in all_states.items():
                workflow = WorkflowState.from_dict(state_data)
                self.workflows[workflow_id] = workflow
        except (json.JSONDecodeError, IOError) as e:
            # Log error but don't fail initialization
            pass

    def recover_workflow(self, workflow_id: str) -> Optional[WorkflowState]:
        """
        Recover a workflow state from persistence.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Recovered WorkflowState or None if not found
        """
        if workflow_id in self.workflows:
            return self.workflows[workflow_id]
        
        if not self.persistence_path or not os.path.exists(self.persistence_path):
            return None
        
        try:
            with open(self.persistence_path, 'r') as f:
                all_states = json.load(f)
            
            if workflow_id in all_states:
                workflow = WorkflowState.from_dict(all_states[workflow_id])
                self.workflows[workflow_id] = workflow
                return workflow
        except (json.JSONDecodeError, IOError, KeyError):
            pass
        
        return None
```