```python
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any
from enum import Enum


class TestAC001InitializeWorkflowStateWithAllStages:
    """Test class for AC-001: Initialize workflow state with all stages"""

    def test_workflow_initialization_includes_all_required_stages(self):
        """
        Test that workflow state initialization includes all required stages.
        Expected to FAIL in RED phase.
        """
        from workflow_state import WorkflowState
        
        expected_stages = ["pending", "in_progress", "review", "completed"]
        workflow = WorkflowState()
        
        assert hasattr(workflow, 'stages')
        assert workflow.stages == expected_stages

    def test_workflow_initialization_sets_initial_stage(self):
        """
        Test that workflow initialization sets the first stage as initial.
        Expected to FAIL in RED phase.
        """
        from workflow_state import WorkflowState
        
        workflow = WorkflowState()
        
        assert hasattr(workflow, 'current_stage')
        assert workflow.current_stage == "pending"

    def test_workflow_initialization_with_custom_stages(self):
        """
        Test that workflow can be initialized with custom stages.
        Expected to FAIL in RED phase.
        """
        from workflow_state import WorkflowState
        
        custom_stages = ["draft", "approval", "published"]
        workflow = WorkflowState(stages=custom_stages)
        
        assert workflow.stages == custom_stages
        assert workflow.current_stage == "draft"

    def test_workflow_initialization_raises_error_for_empty_stages(self):
        """
        Test that workflow initialization raises error for empty stages list.
        Expected to FAIL in RED phase.
        """
        from workflow_state import WorkflowState
        
        with pytest.raises(ValueError):
            workflow = WorkflowState(stages=[])


class TestAC002TrackCurrentStageAndCompletionStatus:
    """Test class for AC-002: Track current stage and completion status"""

    def test_workflow_tracks_current_stage_changes(self):
        """
        Test that workflow correctly tracks current stage changes.
        Expected to FAIL in RED phase.
        """
        from workflow_state import WorkflowState
        
        workflow = WorkflowState()
        workflow.advance_stage()
        
        assert workflow.current_stage == "in_progress"
        assert workflow.get_stage_index() == 1

    def test_workflow_tracks_completion_status(self):
        """
        Test that workflow tracks completion status correctly.
        Expected to FAIL in RED phase.
        """
        from workflow_state import WorkflowState
        
        workflow = WorkflowState()
        
        assert workflow.is_completed() is False
        
        while not workflow.is_completed():
            workflow.advance_stage()
        
        assert workflow.is_completed() is True
        assert workflow.current_stage == "completed"

    def test_workflow_provides_progress_percentage(self):
        """
        Test that workflow provides progress percentage.
        Expected to FAIL in RED phase.
        """
        from workflow_state import WorkflowState
        
        workflow = WorkflowState()
        
        assert workflow.get_progress_percentage() == 0.0
        
        workflow.advance_stage()
        assert workflow.get_progress_percentage() > 0.0

    def test_workflow_tracks_stage_history(self):
        """
        Test that workflow maintains history of stage transitions.
        Expected to FAIL in RED phase.
        """
        from workflow_state import WorkflowState
        
        workflow = WorkflowState()
        workflow.advance_stage()
        workflow.advance_stage()
        
        history = workflow.get_stage_history()
        assert len(history) == 3
        assert history[0] == "pending"
        assert history[1] == "in_progress"
        assert history[2] == "review"


class TestAC003PersistStateForRecoveryCapability:
    """Test class for AC-003: Persist state for recovery capability"""

    def test_workflow_state_can_be_serialized(self):
        """
        Test that workflow state can be serialized to dict.
        Expected to FAIL in RED phase.
        """
        from workflow_state import WorkflowState
        
        workflow = WorkflowState()
        workflow.advance_stage()
        
        state_dict = workflow.to_dict()
        
        assert isinstance(state_dict, dict)
        assert 'current_stage' in state_dict
        assert 'stages' in state_dict
        assert state_dict['current_stage'] == "in_progress"

    def test_workflow_state_can_be_deserialized(self):
        """
        Test that workflow state can be restored from dict.
        Expected to FAIL in RED phase.
        """
        from workflow_state import WorkflowState
        
        state_dict = {
            'current_stage': 'review',
            'stages': ['pending', 'in_progress', 'review', 'completed'],
            'stage_history': ['pending', 'in_progress', 'review']
        }
        
        workflow = WorkflowState.from_dict(state_dict)
        
        assert workflow.current_stage == "review"
        assert workflow.stages == state_dict['stages']

    def test_workflow_state_persists_to_storage(self):
        """
        Test that workflow state can be persisted to storage.
        Expected to FAIL in RED phase.
        """
        from workflow_state import WorkflowState
        
        workflow = WorkflowState()
        workflow.advance_stage()
        
        mock_storage = Mock()
        workflow.save(mock_storage)
        
        mock_storage.save.assert_called_once()

    def test_workflow_state_recovers_from_storage(self):
        """
        Test that workflow state can be recovered from storage.
        Expected to FAIL in RED phase.
        """
        from workflow_state import WorkflowState
        
        mock_storage = Mock()
        mock_storage.load.return_value = {
            'current_stage': 'review',
            'stages': ['pending', 'in_progress', 'review', 'completed']
        }
        
        workflow = WorkflowState.load(mock_storage)
        
        assert workflow.current_stage == "review"
        mock_storage.load.assert_called_once()


class TestAC004ValidateStateTransitions:
    """Test class for AC-004: Validate state transitions"""

    def test_workflow_validates_forward_transitions(self):
        """
        Test that workflow validates forward stage transitions.
        Expected to FAIL in RED phase.
        """
        from workflow_state import WorkflowState
        
        workflow = WorkflowState()
        
        assert workflow.can_transition_to("in_progress") is True
        assert workflow.can_transition_to("review") is False

    def test_workflow_prevents_invalid_transitions(self):
        """
        Test that workflow prevents invalid stage transitions.
        Expected to FAIL in RED phase.
        """
        from workflow_state import WorkflowState
        
        workflow = WorkflowState()
        
        with pytest.raises(ValueError):
            workflow.transition_to("completed")

    def test_workflow_validates_backward_transitions(self):
        """
        Test that workflow validates or prevents backward transitions.
        Expected to FAIL in RED phase.
        """
        from workflow_state import WorkflowState
        
        workflow = WorkflowState()
        workflow.advance_stage()
        workflow.advance_stage()
        
        with pytest.raises(ValueError):
            workflow.transition_to("pending")

    def test_workflow_validates_transition_to_same_stage(self):
        """
        Test that workflow handles transition to same stage.
        Expected to FAIL in RED phase.
        """
        from workflow_state import WorkflowState
        
        workflow = WorkflowState()
        current_stage = workflow.current_stage
        
        result = workflow.transition_to(current_stage)
        
        assert result is False
        assert workflow.current_stage == current_stage

    def test_workflow_validates_transition_to_nonexistent_stage(self):
        """
        Test that workflow raises error for transition to nonexistent stage.
        Expected to FAIL in RED phase.
        """
        from workflow_state import WorkflowState
        
        workflow = WorkflowState()
        
        with pytest.raises(ValueError):
            workflow.transition_to("nonexistent_stage")

    def test_workflow_prevents_transition_after_completion(self):
        """
        Test that workflow prevents transitions after completion.
        Expected to FAIL in RED phase.
        """
        from workflow_state import WorkflowState
        
        workflow = WorkflowState()
        
        while not workflow.is_completed():
            workflow.advance_stage()
        
        with pytest.raises(ValueError):
            workflow.advance_stage()
```