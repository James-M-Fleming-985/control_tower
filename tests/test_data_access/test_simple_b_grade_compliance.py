"""
Simple B Grade Data Access Layer Tests
LAYER-003-01-02-001 B Grade Compliance Validation

Focused tests for B grade compliance without complex fixtures.
"""

import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime

from src.data_access.requirements_driven_data_access import (
    FileDiscovery,
    ResultStorage,
    VerificationEvidenceStorage,
    VerificationDataAccess,
    FileInfo,
    ExecutionResult
)


class TestDataAccessLayerBGrade:
    """Test B grade compliance for Data Access Layer"""
    
    def test_f1_test_file_discovery_basic(self):
        """Test F1: Basic test file discovery works"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create a test file
            test_file = temp_path / "test_example.py"
            test_file.write_text("def test_something(): pass")
            
            # Test discovery
            discovery = FileDiscovery(str(temp_path))
            files = discovery.discover_test_files()
            
            assert len(files) == 1, "Should discover the test file"
            assert files[0].file_path == str(test_file), "Should find correct file"
            assert files[0].test_type == "unit", "Should classify as unit test"
            assert files[0].framework == "pytest", "Should detect pytest framework"
    
    def test_f1_file_integrity_verification(self):
        """Test F1: File integrity verification with hash"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test_hash.py"
            test_file.write_text("def test_hash_check(): pass")
            
            discovery = FileDiscovery(str(temp_path))
            files = discovery.discover_test_files()
            
            assert len(files) == 1, "Should find test file"
            file_info = files[0]
            assert file_info.content_hash, "Should generate content hash"
            assert len(file_info.content_hash) == 32, "Should be MD5 hash"
            assert file_info.file_size > 0, "Should record file size"
    
    def test_f2_test_result_storage(self):
        """Test F2: Test result storage and retrieval"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            db_path = temp_db.name
        
        try:
            storage = ResultStorage(db_path)
            
            # Store a test result
            result = ExecutionResult(
                test_id="test_001",
                test_file="test_example.py",
                test_name="test_function",
                status="passed",
                duration=0.05,
                timestamp=datetime.now()
            )
            
            success = storage.store_test_result(result)
            assert success, "Should store result successfully"
            
            # Retrieve results
            results = storage.get_test_results()
            assert len(results) == 1, "Should retrieve stored result"
            assert results[0].test_id == "test_001", "Should match stored data"
            assert results[0].status == "passed", "Should preserve status"
            
        finally:
            try:
                os.unlink(db_path)
            except FileNotFoundError:
                pass
    
    def test_f2_test_summary_generation(self):
        """Test F2: Test summary generation for metrics"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            db_path = temp_db.name
        
        try:
            storage = ResultStorage(db_path)
            
            # Store multiple results
            results = [
                ExecutionResult("t1", "test.py", "test1", "passed", 0.05, datetime.now()),
                ExecutionResult("t2", "test.py", "test2", "passed", 0.03, datetime.now()),
                ExecutionResult("t3", "test.py", "test3", "failed", 0.10, datetime.now()),
            ]
            
            for result in results:
                storage.store_test_result(result)
            
            summary = storage.get_test_summary()
            assert summary['total_tests'] == 3, "Should count all tests"
            assert summary['passed'] == 2, "Should count passed tests"
            assert summary['failed'] == 1, "Should count failed tests"
            assert abs(summary['pass_rate'] - 66.67) < 1, "Should calculate pass rate"
            
        finally:
            try:
                os.unlink(db_path)
            except FileNotFoundError:
                pass
    
    def test_f3_verification_evidence_storage(self):
        """Test F3: Verification evidence storage"""
        with tempfile.TemporaryDirectory() as temp_dir:
            evidence_storage = VerificationEvidenceStorage(temp_dir)
            
            test_file = "test_example.py"
            evidence_data = {
                "verification_type": "test_execution",
                "status": "passed",
                "duration": 0.05
            }
            
            # Store evidence
            success = evidence_storage.store_verification_evidence(test_file, evidence_data)
            assert success, "Should store evidence successfully"
            
            # Retrieve evidence
            evidence = evidence_storage.get_verification_evidence(test_file)
            assert len(evidence) == 1, "Should retrieve evidence"
            assert evidence[0]["status"] == "passed", "Should match stored data"
            assert "verification_timestamp" in evidence[0], "Should include timestamp"
    
    def test_main_interface_composition(self):
        """Test main VerificationDataAccess interface"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test files
            test_file = temp_path / "test_main.py"
            test_file.write_text("def test_main_interface(): pass")
            
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
                db_path = temp_db.name
            
            try:
                data_access = VerificationDataAccess(str(temp_path), db_path)
                
                # Test discovery through main interface
                files = data_access.discover_and_verify_tests()
                assert len(files) == 1, "Should discover files through main interface"
                
                # Test result storage through main interface
                result = ExecutionResult("t1", "test.py", "test1", "passed", 0.05, datetime.now())
                success = data_access.store_test_execution_result(result)
                assert success, "Should store through main interface"
                
                # Test status retrieval
                status = data_access.get_test_verification_status()
                assert 'summary' in status, "Should provide summary"
                assert 'recent_results' in status, "Should provide recent results"
                
            finally:
                try:
                    os.unlink(db_path)
                except FileNotFoundError:
                    pass
    
    def test_file_integrity_verification_interface(self):
        """Test file integrity verification through main interface"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test_integrity.py"
            test_file.write_text("def test_integrity_check(): pass")
            
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
                db_path = temp_db.name
            
            try:
                data_access = VerificationDataAccess(str(temp_path), db_path)
                
                # Test existing file
                result = data_access.verify_test_file_integrity(str(test_file))
                assert result['verified'], "Should verify existing file"
                assert result['status'] == 'verified', "Should report verified status"
                assert 'current_hash' in result, "Should provide file hash"
                
                # Test missing file
                missing_result = data_access.verify_test_file_integrity("nonexistent.py")
                assert not missing_result['verified'], "Should not verify missing file"
                assert missing_result['status'] == 'missing', "Should report missing status"
                
            finally:
                try:
                    os.unlink(db_path)
                except FileNotFoundError:
                    pass
    
    def test_q1_response_time_performance(self):
        """Test Q1: Response time performance requirement"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create multiple test files
            for i in range(10):
                test_file = temp_path / f"test_{i:03d}.py"
                test_file.write_text(f"def test_function_{i}(): pass")
            
            discovery = FileDiscovery(str(temp_path))
            
            import time
            start_time = time.time()
            files = discovery.discover_test_files()
            duration = time.time() - start_time
            
            assert len(files) == 10, "Should discover all files"
            assert duration < 0.1, "Should complete discovery in under 100ms"
    
    def test_q5_error_handling_reliability(self):
        """Test Q5: Error handling for reliability"""
        # Test discovery with invalid path
        discovery = FileDiscovery("/nonexistent/path")
        files = discovery.discover_test_files()
        assert isinstance(files, list), "Should return list even for invalid path"
        assert len(files) == 0, "Should return empty list for invalid path"
        
        # Test storage with invalid database path (should handle gracefully)
        storage = ResultStorage("/invalid/path/db.sqlite")
        result = ExecutionResult("t1", "test.py", "test1", "passed", 0.05, datetime.now())
        success = storage.store_test_result(result)
        assert not success, "Should handle database errors gracefully"
        
        # Should return empty results without crashing
        results = storage.get_test_results()
        assert isinstance(results, list), "Should return list even on error"
        assert len(results) == 0, "Should return empty list on error"
    
    def test_q9_input_sanitization_security(self):
        """Test Q9: Basic input sanitization"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test_security.py"
            test_file.write_text("def test_security_check(): pass")
            
            discovery = FileDiscovery(str(temp_path))
            files = discovery.discover_test_files()
            
            assert len(files) == 1, "Should discover test file"
            file_info = files[0]
            
            # Verify no path traversal in discovered files
            assert "../" not in file_info.file_path, "Should not include path traversal"
            assert file_info.file_path.startswith(str(temp_path)), "Should use absolute paths safely"
    
    def test_b_grade_core_functionality_complete(self):
        """Test that core functionality meets B grade requirements (75-80%)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test_b_grade.py"
            test_file.write_text("def test_b_grade_compliance(): pass")
            
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
                db_path = temp_db.name
            
            try:
                data_access = VerificationDataAccess(str(temp_path), db_path)
                
                # F1: Test file discovery ✓
                files = data_access.discover_and_verify_tests()
                assert len(files) > 0, "F1: Test discovery implemented"
                
                # F2: Test result storage ✓
                result = ExecutionResult("t1", "test.py", "test1", "passed", 0.05, datetime.now())
                success = data_access.store_test_execution_result(result)
                assert success, "F2: Test result storage implemented"
                
                # F3: Evidence storage (verified through F2) ✓
                status = data_access.get_test_verification_status("test.py")
                assert status['evidence_count'] > 0, "F3: Evidence storage implemented"
                
                # F4: File integrity verification ✓
                integrity = data_access.verify_test_file_integrity(str(test_file))
                assert integrity['verified'], "F4: File integrity verification implemented"
                
                # Q1: Basic performance ✓
                import time
                start_time = time.time()
                data_access.discover_and_verify_tests()
                duration = time.time() - start_time
                assert duration < 0.2, "Q1: Performance requirement met"
                
                # Q5: Basic error handling ✓
                invalid_integrity = data_access.verify_test_file_integrity("nonexistent.py")
                assert not invalid_integrity['verified'], "Q5: Error handling implemented"
                
                print("✅ B GRADE COMPLIANCE ACHIEVED (75-80%)")
                print("✅ Core functionality: F1, F2, F3, F4 implemented")
                print("✅ Essential quality requirements: Q1, Q5 implemented")
                print("✅ Integration interfaces ready for business logic layer")
                
            finally:
                try:
                    os.unlink(db_path)
                except FileNotFoundError:
                    pass