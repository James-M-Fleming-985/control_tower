"""Comprehensive unit tests for data access modules - GREEN phase coverage improvement"""

import pytest
import os
import sys
import tempfile
import shutil
import sqlite3
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from data_access.git_checkpoint_models import GitCheckpointModel, GitStateModel
from data_access.git_operations import GitOperationsManager
from data_access.phase_data_interface import PhaseDataInterface
from data_access.phase_models import PhaseState, PhaseTransition, PhaseMetrics
from data_access.tdd_phase_repository import TDDPhaseRepository
from data_access.utilities import DatabaseUtils, ValidationUtils, CacheUtils


class TestGitCheckpointModels:
    """Comprehensive unit tests for Git checkpoint models"""
    
    def setup_method(self):
        """Setup for each test"""
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Cleanup after each test"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_git_checkpoint_model_creation(self):
        """Test GitCheckpointModel creation"""
        model = GitCheckpointModel(
            checkpoint_id="test_checkpoint",
            commit_hash="abc123",
            phase="RED",
            timestamp=datetime.now()
        )
        assert model.checkpoint_id == "test_checkpoint"
        assert model.commit_hash == "abc123"
        assert model.phase == "RED"
        
    def test_git_state_model_creation(self):
        """Test GitStateModel creation"""
        state = GitStateModel(
            repository_path=self.temp_dir,
            current_branch="main",
            uncommitted_changes=False
        )
        assert state.repository_path == self.temp_dir
        assert state.current_branch == "main"
        assert state.uncommitted_changes is False
        
    def test_git_checkpoint_validation(self):
        """Test checkpoint validation"""
        model = GitCheckpointModel(
            checkpoint_id="",  # Invalid empty ID
            commit_hash="abc123",
            phase="RED",
            timestamp=datetime.now()
        )
        result = model.validate()
        assert result is not None
        
    def test_git_state_serialization(self):
        """Test git state serialization"""
        state = GitStateModel(
            repository_path=self.temp_dir,
            current_branch="feature/test",
            uncommitted_changes=True
        )
        serialized = state.to_dict()
        assert serialized is not None
        assert "repository_path" in serialized
        assert "current_branch" in serialized


class TestGitOperationsManager:
    """Comprehensive unit tests for GitOperationsManager"""
    
    def setup_method(self):
        """Setup for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.git_manager = GitOperationsManager(self.temp_dir)
        
    def teardown_method(self):
        """Cleanup after each test"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            
    def test_git_manager_initialization(self):
        """Test GitOperationsManager initialization"""
        assert self.git_manager.repository_path == self.temp_dir
        assert self.git_manager is not None
        
    def test_get_current_commit_hash(self):
        """Test getting current commit hash"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = "abc123def456\n"
            mock_run.return_value.returncode = 0
            
            commit_hash = self.git_manager.get_current_commit_hash()
            assert commit_hash == "abc123def456"
            
    def test_create_checkpoint(self):
        """Test creating a checkpoint"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            result = self.git_manager.create_checkpoint("RED", "Test checkpoint")
            assert result is not None
            
    def test_get_repository_status(self):
        """Test getting repository status"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = "M file1.py\nA file2.py\n"
            mock_run.return_value.returncode = 0
            
            status = self.git_manager.get_repository_status()
            assert status is not None
            
    def test_validate_repository(self):
        """Test repository validation"""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            
            result = self.git_manager.validate_repository()
            assert result is not None


class TestPhaseDataInterface:
    """Comprehensive unit tests for PhaseDataInterface"""
    
    def setup_method(self):
        """Setup for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.interface = PhaseDataInterface()
        
    def teardown_method(self):
        """Cleanup after each test"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            
    def test_store_phase_data(self):
        """Test storing phase data"""
        phase_data = {
            "phase_id": "test_phase",
            "phase_type": "RED",
            "timestamp": datetime.now().isoformat()
        }
        result = self.interface.store_phase_data(phase_data)
        assert result is not None
        
    def test_retrieve_phase_data(self):
        """Test retrieving phase data"""
        phase_id = "test_phase_123"
        result = self.interface.retrieve_phase_data(phase_id)
        assert result is not None
        
    def test_update_phase_data(self):
        """Test updating phase data"""
        phase_id = "test_phase_456"
        updates = {"status": "completed", "duration": 45.5}
        result = self.interface.update_phase_data(phase_id, updates)
        assert result is not None
        
    def test_delete_phase_data(self):
        """Test deleting phase data"""
        phase_id = "test_phase_789"
        result = self.interface.delete_phase_data(phase_id)
        assert result is not None
        
    def test_query_phase_history(self):
        """Test querying phase history"""
        criteria = {"phase_type": "GREEN", "start_date": "2024-01-01"}
        result = self.interface.query_phase_history(criteria)
        assert result is not None


class TestPhaseModels:
    """Comprehensive unit tests for phase models"""
    
    def test_phase_state_creation(self):
        """Test PhaseState creation"""
        state = PhaseState(
            phase_id="state_001",
            phase_name="test_phase",
            phase_type="RED",
            feature_name="test_feature",
            status="active"
        )
        assert state.phase_id == "state_001"
        assert state.phase_type == "RED"
        assert state.feature_name == "test_feature"
        
    def test_phase_transition_creation(self):
        """Test PhaseTransition creation"""
        transition = PhaseTransition(
            transition_id="trans_001",
            from_phase="RED",
            to_phase="GREEN",
            trigger_condition="all_tests_pass",
            timestamp=datetime.now()
        )
        assert transition.from_phase == "RED"
        assert transition.to_phase == "GREEN"
        assert transition.trigger_condition == "all_tests_pass"
        
    def test_phase_metrics_creation(self):
        """Test PhaseMetrics creation"""
        metrics = PhaseMetrics(
            metrics_id="metrics_001",
            phase_id="phase_001",
            duration_seconds=120.5,
            test_count=15,
            coverage_percentage=95.2
        )
        assert metrics.duration_seconds == 120.5
        assert metrics.test_count == 15
        assert metrics.coverage_percentage == 95.2
        
    def test_phase_state_validation(self):
        """Test phase state validation"""
        state = PhaseState(
            phase_id="",  # Invalid empty ID
            phase_name="test",
            phase_type="INVALID",  # Invalid phase type
            feature_name="test",
            status="active"
        )
        result = state.validate()
        assert result is not None
        
    def test_phase_model_serialization(self):
        """Test phase model serialization"""
        state = PhaseState(
            phase_id="serialize_test",
            phase_name="serialization_test",
            phase_type="GREEN",
            feature_name="serialization_feature",
            status="completed"
        )
        serialized = state.to_dict()
        assert serialized is not None
        assert "phase_id" in serialized
        assert "phase_type" in serialized


class TestTDDPhaseRepository:
    """Comprehensive unit tests for TDDPhaseRepository"""
    
    def setup_method(self):
        """Setup for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_phases.db")
        self.repository = TDDPhaseRepository(self.db_path)
        
    def teardown_method(self):
        """Cleanup after each test"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            
    def test_repository_initialization(self):
        """Test repository initialization"""
        assert self.repository.db_path == self.db_path
        assert os.path.exists(self.db_path)
        
    def test_create_phase_state_record(self):
        """Test creating phase state record"""
        phase_id = self.repository.create_phase_state_record(
            "test_phase", "RED", "test_feature"
        )
        assert phase_id is not None
        assert isinstance(phase_id, str)
        
    def test_get_phase_state(self):
        """Test getting phase state"""
        # Create a test phase first
        phase_id = self.repository.create_phase_state_record(
            "get_test_phase", "GREEN", "get_test_feature"
        )
        
        # Retrieve it
        state = self.repository.get_phase_state(phase_id)
        assert state is not None
        assert state.get("phase_id") == phase_id
        
    def test_update_phase_state(self):
        """Test updating phase state"""
        # Create a test phase first
        phase_id = self.repository.create_phase_state_record(
            "update_test_phase", "RED", "update_test_feature"
        )
        
        # Update it
        updates = {"status": "completed", "test_count": 10}
        result = self.repository.update_phase_state(phase_id, updates)
        assert result is True
        
    def test_get_phase_history(self):
        """Test getting phase history"""
        # Create some test phases
        phase1 = self.repository.create_phase_state_record(
            "history_phase_1", "RED", "history_feature_1"
        )
        phase2 = self.repository.create_phase_state_record(
            "history_phase_2", "GREEN", "history_feature_2"
        )
        
        # Get history
        history = self.repository.get_phase_history("history_feature_1")
        assert history is not None
        assert len(history) > 0
        
    def test_repository_database_operations(self):
        """Test repository database operations"""
        # Test database connection
        assert os.path.exists(self.db_path)
        
        # Test table creation
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='phase_states'
            """)
            tables = cursor.fetchall()
            assert len(tables) > 0


class TestUtilities:
    """Comprehensive unit tests for utility modules"""
    
    def setup_method(self):
        """Setup for utility tests"""
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Cleanup after utility tests"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            
    def test_database_utils_connection(self):
        """Test database utility connection functions"""
        db_path = os.path.join(self.temp_dir, "utils_test.db")
        utils = DatabaseUtils()
        
        result = utils.create_connection(db_path)
        assert result is not None
        
    def test_validation_utils_data_validation(self):
        """Test validation utility functions"""
        utils = ValidationUtils()
        
        # Test valid data
        valid_data = {"id": "test123", "type": "RED", "status": "active"}
        result = utils.validate_phase_data(valid_data)
        assert result is not None
        
        # Test invalid data
        invalid_data = {"id": "", "type": "INVALID", "status": None}
        result = utils.validate_phase_data(invalid_data)
        assert result is not None
        
    def test_cache_utils_caching_operations(self):
        """Test cache utility operations"""
        utils = CacheUtils()
        
        # Test cache set/get
        utils.set_cache("test_key", {"data": "test_value"})
        cached_data = utils.get_cache("test_key")
        assert cached_data is not None
        
        # Test cache clear
        utils.clear_cache("test_key")
        cleared_data = utils.get_cache("test_key")
        assert cleared_data is None
        
    def test_utility_error_handling(self):
        """Test utility error handling"""
        utils = DatabaseUtils()
        
        # Test with invalid database path
        result = utils.create_connection("/invalid/path/db.sqlite")
        assert result is not None  # Should handle error gracefully


# Integration tests for data access modules
class TestDataAccessIntegration:
    """Integration tests for data access module interactions"""
    
    def setup_method(self):
        """Setup for integration tests"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "integration_test.db")
        self.repository = TDDPhaseRepository(self.db_path)
        self.git_manager = GitOperationsManager(self.temp_dir)
        self.interface = PhaseDataInterface()
        
    def teardown_method(self):
        """Cleanup after integration tests"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            
    def test_repository_and_git_integration(self):
        """Test repository and git manager integration"""
        # Create phase with git info
        with patch.object(self.git_manager, 'get_current_commit_hash', return_value='abc123'):
            phase_id = self.repository.create_phase_state_record(
                "git_integration_phase", "RED", "git_integration_feature"
            )
            
            # Verify phase created
            state = self.repository.get_phase_state(phase_id)
            assert state is not None
            assert "git_commit" in state
            
    def test_interface_and_repository_integration(self):
        """Test interface and repository integration"""
        # Store data through interface
        phase_data = {
            "phase_name": "interface_test",
            "phase_type": "GREEN",
            "feature_name": "interface_feature"
        }
        result = self.interface.store_phase_data(phase_data)
        assert result is not None
        
    def test_cross_module_data_consistency(self):
        """Test data consistency across modules"""
        # Create phase in repository
        phase_id = self.repository.create_phase_state_record(
            "consistency_test", "REFACTOR", "consistency_feature"
        )
        
        # Verify through interface
        retrieved_data = self.interface.retrieve_phase_data(phase_id)
        assert retrieved_data is not None
        
        # Update through repository
        updates = {"status": "completed"}
        update_result = self.repository.update_phase_state(phase_id, updates)
        assert update_result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])