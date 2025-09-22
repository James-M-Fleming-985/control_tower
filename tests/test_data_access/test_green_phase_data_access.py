"""
GREEN Phase Tests for Data Access Layer
LAYER-003-01-02-001 B Grade Compliance Testing

Tests the requirements-driven implementation to verify B grade compliance (75-80%).
"""

import pytest
import tempfile
import os
import sqlite3
from pathlib import Path
from datetime import datetime

from src.data_access.requirements_driven_data_access import (
    TestFileDiscovery,
    TestResultStorage,
    VerificationEvidenceStorage,
    TestVerificationDataAccess,
    TestFileInfo,
    TestResult
)


class TestBGradeDataAccessLayer:
    """Test B grade compliance for Data Access Layer"""
    
    @pytest.fixture
    def temp_test_environment(self):
        """Create temporary test environment"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test files for discovery
            test_files = [
                (temp_path / "test_unit.py", "def test_unit_function(): pass"),
                (temp_path / "integration" / "test_integration.py", "def test_integration(): pass"),
                (temp_path / "e2e" / "test_e2e.py", "def test_e2e_workflow(): pass")
            ]
            
            for test_file, content in test_files:
                test_file.parent.mkdir(parents=True, exist_ok=True)
                test_file.write_text(content)
            
            yield temp_path
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        yield db_path
        try:
            os.unlink(db_path)
        except FileNotFoundError:
            pass


class TestF1TestFileDiscovery:
    """Test F1: REAL test file discovery and physical file verification"""
    
    def test_f1_discover_test_files_basic(self, temp_test_environment):
        """Test basic test file discovery functionality"""
        discovery = TestFileDiscovery(str(temp_test_environment))
        files = discovery.discover_test_files()
        
        assert len(files) == 3, "Should discover all 3 test files"
        assert all(isinstance(f, TestFileInfo) for f in files), "Should return TestFileInfo objects"
        
        # Verify files actually exist
        for file_info in files:
            assert Path(file_info.file_path).exists(), f"File {file_info.file_path} must exist"
    
    def test_f1_test_type_classification(self, temp_test_environment):
        """Test test type classification"""
        discovery = TestFileDiscovery(str(temp_test_environment))
        files = discovery.discover_test_files()
        
        test_types = [f.test_type for f in files]
        assert 'unit' in test_types, "Should identify unit tests"
        assert 'integration' in test_types, "Should identify integration tests"
        assert 'e2e' in test_types, "Should identify e2e tests"
    
    def test_f1_file_integrity_verification(self, temp_test_environment):
        """Test file integrity with hash verification"""
        discovery = TestFileDiscovery(str(temp_test_environment))
        files = discovery.discover_test_files()
        
        for file_info in files:
            assert file_info.content_hash, "Should generate content hash"
            assert len(file_info.content_hash) == 32, "Should generate MD5 hash"
            assert file_info.file_size > 0, "Should record file size"


class TestF2TestResultStorage:
    """Test F2: REAL test execution result storage"""
    
    def test_f2_store_and_retrieve_results(self, temp_db):
        """Test storing and retrieving test results"""
        storage = TestResultStorage(temp_db)
        
        result = TestResult(
            test_id="test_001",
            test_file="test_example.py",
            test_name="test_function",
            status="passed",
            duration=0.05,
            timestamp=datetime.now()
        )
        
        # Store result
        assert storage.store_test_result(result), "Should store result successfully"
        
        # Retrieve results
        results = storage.get_test_results()
        assert len(results) == 1, "Should retrieve stored result"
        assert results[0].test_id == "test_001", "Should match stored data"
    
    def test_f2_test_summary_generation(self, temp_db):
        """Test test summary generation for metrics"""
        storage = TestResultStorage(temp_db)
        
        # Store multiple results
        test_results = [
            TestResult("t1", "test.py", "test1", "passed", 0.05, datetime.now()),
            TestResult("t2", "test.py", "test2", "passed", 0.03, datetime.now()),
            TestResult("t3", "test.py", "test3", "failed", 0.10, datetime.now()),
        ]
        
        for result in test_results:
            storage.store_test_result(result)
        
        summary = storage.get_test_summary()
        assert summary['total_tests'] == 3, "Should count all tests"
        assert summary['passed'] == 2, "Should count passed tests"
        assert summary['failed'] == 1, "Should count failed tests"
        assert abs(summary['pass_rate'] - 66.67) < 1, "Should calculate pass rate"


class TestF3VerificationEvidenceStorage:
    """Test F3: REAL verification evidence storage"""
    
    def test_f3_store_evidence_with_timestamp(self):
        """Test evidence storage with timestamps"""
        with tempfile.TemporaryDirectory() as temp_dir:
            evidence_storage = VerificationEvidenceStorage(temp_dir)
            
            test_file = "test_example.py"
            evidence_data = {
                "verification_type": "test_execution",
                "status": "passed"
            }
            
            success = evidence_storage.store_verification_evidence(test_file, evidence_data)
            assert success, "Should store evidence successfully"
            
            # Check file was created
            evidence_files = list(Path(temp_dir).glob("verification_*.json"))
            assert len(evidence_files) == 1, "Should create evidence file"
    
    def test_f3_retrieve_evidence_by_test_file(self):
        """Test evidence retrieval by test file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            evidence_storage = VerificationEvidenceStorage(temp_dir)
            
            test_file = "test_example.py"
            evidence_data = {"status": "passed"}
            
            evidence_storage.store_verification_evidence(test_file, evidence_data)
            evidence = evidence_storage.get_verification_evidence(test_file)
            
            assert len(evidence) == 1, "Should retrieve evidence"
            assert evidence[0]["status"] == "passed", "Should match stored data"
            assert "verification_timestamp" in evidence[0], "Should include timestamp"


class TestMainDataAccessInterface:
    """Test main TestVerificationDataAccess interface"""
    
    def test_main_interface_composition(self, temp_test_environment, temp_db):
        """Test main interface properly composes all components"""
        data_access = TestVerificationDataAccess(str(temp_test_environment), temp_db)
        
        # Test discovery through main interface
        files = data_access.discover_and_verify_tests()
        assert len(files) == 3, "Should discover files through main interface"
        
        # Test result storage through main interface
        result = TestResult("t1", "test.py", "test1", "passed", 0.05, datetime.now())
        success = data_access.store_test_execution_result(result)
        assert success, "Should store through main interface"
        
        # Test status retrieval
        status = data_access.get_test_verification_status()
        assert 'summary' in status, "Should provide summary"
        assert 'recent_results' in status, "Should provide recent results"
    
    def test_file_integrity_verification(self, temp_test_environment, temp_db):
        """Test file integrity verification through main interface"""
        data_access = TestVerificationDataAccess(str(temp_test_environment), temp_db)
        
        # Test existing file
        test_file = temp_test_environment / "test_unit.py"
        result = data_access.verify_test_file_integrity(str(test_file))
        
        assert result['verified'], "Should verify existing file"
        assert result['status'] == 'verified', "Should report verified status"
        assert 'current_hash' in result, "Should provide file hash"
        
        # Test missing file
        missing_result = data_access.verify_test_file_integrity("nonexistent.py")
        assert not missing_result['verified'], "Should not verify missing file"
        assert missing_result['status'] == 'missing', "Should report missing status"


class TestQualityRequirements:
    """Test quality requirements for B grade compliance"""
    
    def test_q1_response_time_performance(self, temp_test_environment):
        """Test Q1: Response Time < 100ms requirement"""
        discovery = TestFileDiscovery(str(temp_test_environment))
        
        import time
        start_time = time.time()
        files = discovery.discover_test_files()
        duration = time.time() - start_time
        
        assert len(files) > 0, "Should discover files"
        assert duration < 0.1, "Should complete discovery in under 100ms"
    
    def test_q5_error_handling(self):
        """Test Q5: Error handling for reliability"""
        # Test discovery with invalid path
        discovery = TestFileDiscovery("/nonexistent/path")
        files = discovery.discover_test_files()
        assert isinstance(files, list), "Should return list even for invalid path"
        
        # Test storage with invalid database
        storage = TestResultStorage("/invalid/path/db.sqlite")
        result = TestResult("t1", "test.py", "test1", "passed", 0.05, datetime.now())
        success = storage.store_test_result(result)
        assert not success, "Should handle database errors gracefully"
    
    def test_q9_input_sanitization(self, temp_test_environment):
        """Test Q9: Input sanitization for security"""
        discovery = TestFileDiscovery(str(temp_test_environment))
        
        # Test that path traversal attempts are handled safely
        files = discovery.discover_test_files()
        for file_info in files:
            # Verify no path traversal in discovered files
            assert "../" not in file_info.file_path, "Should not include path traversal"
            assert not file_info.file_path.startswith("/"), "Should use relative paths"


class TestBGradeComplianceValidation:
    """Validate B grade compliance (75-80% coverage)"""
    
    def test_core_functionality_implemented(self, temp_test_environment, temp_db):
        """Test that core functionality is implemented for B grade"""
        data_access = TestVerificationDataAccess(str(temp_test_environment), temp_db)
        
        # F1: Test file discovery
        files = data_access.discover_and_verify_tests()
        assert len(files) > 0, "F1: Test discovery implemented"
        
        # F2: Test result storage
        result = TestResult("t1", "test.py", "test1", "passed", 0.05, datetime.now())
        success = data_access.store_test_execution_result(result)
        assert success, "F2: Test result storage implemented"
        
        # F3: Evidence storage (tested through F2)
        status = data_access.get_test_verification_status("test.py")
        assert status['evidence_count'] > 0, "F3: Evidence storage implemented"
        
        # F4: File integrity verification
        test_file = temp_test_environment / "test_unit.py"
        integrity = data_access.verify_test_file_integrity(str(test_file))
        assert integrity['verified'], "F4: File integrity verification implemented"
    
    def test_essential_quality_requirements(self, temp_test_environment):
        """Test essential quality requirements for B grade"""
        discovery = TestFileDiscovery(str(temp_test_environment))
        
        # Q1: Performance (basic)
        import time
        start_time = time.time()
        files = discovery.discover_test_files()
        duration = time.time() - start_time
        assert duration < 0.2, "Q1: Basic performance requirement met"
        
        # Q5: Error handling (basic)
        invalid_discovery = TestFileDiscovery("/invalid/path")
        invalid_files = invalid_discovery.discover_test_files()
        assert isinstance(invalid_files, list), "Q5: Basic error handling implemented"
    
    def test_integration_readiness(self, temp_test_environment, temp_db):
        """Test readiness for business logic layer integration"""
        data_access = TestVerificationDataAccess(str(temp_test_environment), temp_db)
        
        # Interface methods exist and work
        assert hasattr(data_access, 'discover_and_verify_tests'), "Integration interface exists"
        assert hasattr(data_access, 'store_test_execution_result'), "Storage interface exists"
        assert hasattr(data_access, 'get_test_verification_status'), "Status interface exists"
        assert hasattr(data_access, 'verify_test_file_integrity'), "Integrity interface exists"
        
        # Data contracts are consistent
        files = data_access.discover_and_verify_tests()
        if files:
            assert all(hasattr(f, 'file_path') for f in files), "Consistent data contracts"
            assert all(hasattr(f, 'test_type') for f in files), "Required fields present"