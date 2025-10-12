```python
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any


class TestAC001InitializeWorkflowState:
    """Test initialization of workflow state with all stages."""
    
    def test_initialize_workflow_state_with_empty_stages(self):
        """Test that workflow state initialization fails with empty stages list."""
        from workflow_state import WorkflowState
        
        with pytest.raises(ValueError, match="Stages cannot be empty"):
            WorkflowState(stages=[])
    
    def test_initialize_workflow_state_with_valid_stages(self):
        """Test that workflow state initializes with all provided stages."""
        from workflow_state import WorkflowState
        
        stages = ["stage1", "stage2", "stage3"]
        workflow = WorkflowState(stages=stages)
        
        assert workflow.get_all_stages() == stages
        assert len(workflow.get_all_stages()) == 3
    
    def test_initialize_workflow_state_with_duplicate_stages(self):
        """Test that workflow state initialization fails with duplicate stages."""
        from workflow_state import WorkflowState
        
        stages = ["stage1", "stage2", "stage1"]
        with pytest.raises(ValueError, match="Duplicate stages not allowed"):
            WorkflowState(stages=stages)
    
    def test_initialize_workflow_state_preserves_stage_order(self):
        """Test that workflow state preserves the order of stages."""
        from workflow_state import WorkflowState
        
        stages = ["checkout", "build", "test", "deploy"]
        workflow = WorkflowState(stages=stages)
        
        assert workflow.get_all_stages() == stages


class TestAC002TrackCurrentStageAndCompletion:
    """Test tracking of current stage and completion status."""
    
    def test_track_current_stage_initial_state(self):
        """Test that initial current stage is set to first stage."""
        from workflow_state import WorkflowState
        
        stages = ["stage1", "stage2", "stage3"]
        workflow = WorkflowState(stages=stages)
        
        assert workflow.get_current_stage() == "stage1"
        assert workflow.is_completed() is False
    
    def test_track_current_stage_progression(self):
        """Test that current stage progresses correctly."""
        from workflow_state import WorkflowState
        
        stages = ["stage1", "stage2", "stage3"]
        workflow = WorkflowState(stages=stages)
        
        workflow.advance_stage()
        assert workflow.get_current_stage() == "stage2"
        
        workflow.advance_stage()
        assert workflow.get_current_stage() == "stage3"
    
    def test_completion_status_when_all_stages_complete(self):
        """Test that completion status is True when all stages are complete."""
        from workflow_state import WorkflowState
        
        stages = ["stage1", "stage2"]
        workflow = WorkflowState(stages=stages)
        
        workflow.advance_stage()
        workflow.advance_stage()
        
        assert workflow.is_completed() is True
    
    def test_get_completion_percentage(self):
        """Test that completion percentage is calculated correctly."""
        from workflow_state import WorkflowState
        
        stages = ["stage1", "stage2", "stage3", "stage4"]
        workflow = WorkflowState(stages=stages)
        
        assert workflow.get_completion_percentage() == 0
        
        workflow.advance_stage()
        assert workflow.get_completion_percentage() == 25


class TestAC003PersistStateForRecovery:
    """Test state persistence for recovery capability."""
    
    def test_persist_state_to_storage(self):
        """Test that workflow state can be persisted to storage."""
        from workflow_state import WorkflowState
        
        stages = ["stage1", "stage2", "stage3"]
        workflow = WorkflowState(stages=stages)
        workflow.advance_stage()
        
        state_dict = workflow.serialize()
        
        assert "stages" in state_dict
        assert "current_stage" in state_dict
        assert state_dict["current_stage"] == "stage2"
    
    def test_restore_state_from_storage(self):
        """Test that workflow state can be restored from persisted data."""
        from workflow_state import WorkflowState
        
        state_dict = {
            "stages": ["stage1", "stage2", "stage3"],
            "current_stage": "stage2",
            "completed": False
        }
        
        workflow = WorkflowState.deserialize(state_dict)
        
        assert workflow.get_current_stage() == "stage2"
        assert workflow.get_all_stages() == ["stage1", "stage2", "stage3"]
    
    def test_persist_state_with_invalid_data(self):
        """Test that deserializing invalid state data raises error."""
        from workflow_state import WorkflowState
        
        invalid_state = {"invalid": "data"}
        
        with pytest.raises(KeyError, match="stages"):
            WorkflowState.deserialize(invalid_state)
    
    def test_persist_state_maintains_completion_status(self):
        """Test that completion status is maintained after persistence."""
        from workflow_state import WorkflowState
        
        stages = ["stage1", "stage2"]
        workflow = WorkflowState(stages=stages)
        workflow.advance_stage()
        workflow.advance_stage()
        
        state_dict = workflow.serialize()
        restored_workflow = WorkflowState.deserialize(state_dict)
        
        assert restored_workflow.is_completed() is True


class TestAC004ValidateStateTransitions:
    """Test validation of state transitions."""
    
    def test_validate_transition_to_next_stage(self):
        """Test that transition to next stage is valid."""
        from workflow_state import WorkflowState
        
        stages = ["stage1", "stage2", "stage3"]
        workflow = WorkflowState(stages=stages)
        
        assert workflow.can_transition_to("stage2") is True
        assert workflow.can_transition_to("stage3") is False
    
    def test_validate_invalid_stage_transition(self):
        """Test that transition to invalid stage raises error."""
        from workflow_state import WorkflowState
        
        stages = ["stage1", "stage2", "stage3"]
        workflow = WorkflowState(stages=stages)
        
        with pytest.raises(ValueError, match="Invalid stage transition"):
            workflow.transition_to("stage3")
    
    def test_validate_transition_from_completed_state(self):
        """Test that no transitions allowed from completed state."""
        from workflow_state import WorkflowState
        
        stages = ["stage1", "stage2"]
        workflow = WorkflowState(stages=stages)
        workflow.advance_stage()
        workflow.advance_stage()
        
        with pytest.raises(ValueError, match="Workflow already completed"):
            workflow.advance_stage()
    
    def test_validate_transition_to_non_existent_stage(self):
        """Test that transition to non-existent stage raises error."""
        from workflow_state import WorkflowState
        
        stages = ["stage1", "stage2", "stage3"]
        workflow = WorkflowState(stages=stages)
        
        with pytest.raises(ValueError, match="Stage .* does not exist"):
            workflow.transition_to("non_existent_stage")
    
    def test_validate_backward_transition_not_allowed(self):
        """Test that backward transitions are not allowed by default."""
        from workflow_state import WorkflowState
        
        stages = ["stage1", "stage2", "stage3"]
        workflow = WorkflowState(stages=stages)
        workflow.advance_stage()
        
        assert workflow.can_transition_to("stage1") is False
        
        with pytest.raises(ValueError, match="Backward transitions not allowed"):
            workflow.transition_to("stage1")
```