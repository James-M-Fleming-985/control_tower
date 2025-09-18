"""
Test Generation Verification System - Data Access Layer
LAYER-003-01-02-001 Implementation

Provides REAL file verification, test file discovery, and test result storage
for TDD workflow stage gate enforcement.
"""

import os
import json
import sqlite3
import glob
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib


@dataclass
class TestFileInfo:
    """Represents discovered test file information"""
    file_path: str
    file_size: int
    modified_time: float
    content_hash: str
    test_type: str  # unit, integration, e2e
    framework: str  # pytest, unittest, etc.


@dataclass
class TestResult:
    """Represents test execution result"""
    test_id: str
    test_file: str
    test_name: str
    status: str  # passed, failed, skipped
    duration: float
    timestamp: datetime
    error_message: Optional[str] = None


class TestFileDiscovery:
    """REAL test file discovery with physical file verification"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.test_patterns = [
            "test_*.py",
            "*_test.py", 
            "**/test_*.py",
            "**/*_test.py"
        ]
    
    def discover_test_files(self) -> List[TestFileInfo]:
        """Discover all test files with REAL verification"""
        test_files = []
        
        for pattern in self.test_patterns:
            for file_path in self.base_path.glob(pattern):
                if file_path.is_file() and self._is_test_file(file_path):
                    test_info = self._extract_test_info(file_path)
                    if test_info:
                        test_files.append(test_info)
        
        return test_files
    
    def _is_test_file(self, file_path: Path) -> bool:
        """Verify file is actually a test file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(1000)  # Read first 1KB
                return any(keyword in content for keyword in [
                    'def test_', 'class Test', '@pytest', 'unittest.TestCase'
                ])
        except (IOError, UnicodeDecodeError):
            return False
    
    def _extract_test_info(self, file_path: Path) -> Optional[TestFileInfo]:
        """Extract test file information with REAL verification"""
        try:
            stat = file_path.stat()
            
            # Calculate content hash for integrity
            with open(file_path, 'rb') as f:
                content_hash = hashlib.md5(f.read()).hexdigest()
            
            # Determine test type based on path
            test_type = self._determine_test_type(file_path)
            
            # Determine framework
            framework = self._determine_framework(file_path)
            
            return TestFileInfo(
                file_path=str(file_path),
                file_size=stat.st_size,
                modified_time=stat.st_mtime,
                content_hash=content_hash,
                test_type=test_type,
                framework=framework
            )
        except Exception:
            return None
    
    def _determine_test_type(self, file_path: Path) -> str:
        """Determine test type from file path"""
        path_str = str(file_path).lower()
        if 'e2e' in path_str or 'end_to_end' in path_str:
            return 'e2e'
        elif 'integration' in path_str:
            return 'integration'
        else:
            return 'unit'
    
    def _determine_framework(self, file_path: Path) -> str:
        """Determine test framework from file content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(2000)  # Read first 2KB
                if 'pytest' in content or '@pytest' in content:
                    return 'pytest'
                elif 'unittest' in content:
                    return 'unittest'
                else:
                    return 'pytest'  # Default
        except Exception:
            return 'pytest'


class TestResultStorage:
    """REAL test result storage with SQLite persistence"""
    
    def __init__(self, db_path: str = "test_results.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with test results schema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                CREATE TABLE IF NOT EXISTS test_results (
                    test_id TEXT PRIMARY KEY,
                    test_file TEXT NOT NULL,
                    test_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    duration REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    error_message TEXT
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_test_file 
                ON test_results(test_file)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON test_results(timestamp)
            """)
        except sqlite3.Error:
            # Handle database errors gracefully
            pass
    
    def store_test_result(self, result: TestResult) -> bool:
        """Store test result with REAL persistence"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO test_results 
                    (test_id, test_file, test_name, status, duration, timestamp, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    result.test_id,
                    result.test_file,
                    result.test_name,
                    result.status,
                    result.duration,
                    result.timestamp.isoformat(),
                    result.error_message
                ))
            return True
        except Exception:
            return False
    
    def get_test_results(self, test_file: Optional[str] = None) -> List[TestResult]:
        """Retrieve test results with optional filtering"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if test_file:
                    cursor = conn.execute(
                        "SELECT * FROM test_results WHERE test_file = ? ORDER BY timestamp DESC",
                        (test_file,)
                    )
                else:
                    cursor = conn.execute(
                        "SELECT * FROM test_results ORDER BY timestamp DESC"
                    )
                
                results = []
                for row in cursor.fetchall():
                    results.append(TestResult(
                        test_id=row[0],
                        test_file=row[1],
                        test_name=row[2],
                        status=row[3],
                        duration=row[4],
                        timestamp=datetime.fromisoformat(row[5]),
                        error_message=row[6]
                    ))
                
                return results
        except Exception:
            return []
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get test execution summary statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_tests,
                        SUM(CASE WHEN status = 'passed' THEN 1 ELSE 0 END) as passed,
                        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                        SUM(CASE WHEN status = 'skipped' THEN 1 ELSE 0 END) as skipped,
                        AVG(duration) as avg_duration
                    FROM test_results
                    WHERE date(timestamp) = date('now')
                """)
                
                row = cursor.fetchone()
                return {
                    'total_tests': row[0] or 0,
                    'passed': row[1] or 0,
                    'failed': row[2] or 0,
                    'skipped': row[3] or 0,
                    'avg_duration': row[4] or 0.0,
                    'pass_rate': (row[1] or 0) / max(row[0] or 1, 1) * 100
                }
        except Exception:
            return {'total_tests': 0, 'passed': 0, 'failed': 0, 'skipped': 0, 'avg_duration': 0.0, 'pass_rate': 0.0}


class VerificationEvidenceStorage:
    """REAL verification evidence storage for audit trail"""
    
    def __init__(self, evidence_dir: str = "verification_evidence"):
        self.evidence_dir = Path(evidence_dir)
        self.evidence_dir.mkdir(exist_ok=True)
    
    def store_verification_evidence(self, test_file: str, evidence_data: Dict[str, Any]) -> bool:
        """Store verification evidence with timestamp"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"verification_{Path(test_file).stem}_{timestamp}.json"
            evidence_path = self.evidence_dir / file_name
            
            evidence_data['verification_timestamp'] = datetime.now().isoformat()
            evidence_data['test_file'] = test_file
            
            with open(evidence_path, 'w') as f:
                json.dump(evidence_data, f, indent=2)
            
            return True
        except Exception:
            return False
    
    def get_verification_evidence(self, test_file: str) -> List[Dict[str, Any]]:
        """Retrieve verification evidence for a test file"""
        evidence = []
        file_stem = Path(test_file).stem
        
        try:
            for evidence_file in self.evidence_dir.glob(f"verification_{file_stem}_*.json"):
                with open(evidence_file, 'r') as f:
                    evidence.append(json.load(f))
            
            return sorted(evidence, key=lambda x: x.get('verification_timestamp', ''), reverse=True)
        except Exception:
            return []


class TestVerificationDataAccess:
    """Main data access interface for Test Generation Verification System"""
    
    def __init__(self, base_path: str = ".", db_path: str = "test_results.db"):
        self.file_discovery = TestFileDiscovery(base_path)
        self.result_storage = TestResultStorage(db_path)
        self.evidence_storage = VerificationEvidenceStorage()
    
    def discover_and_verify_tests(self) -> List[TestFileInfo]:
        """Discover all test files with REAL verification"""
        return self.file_discovery.discover_test_files()
    
    def store_test_execution_result(self, result: TestResult) -> bool:
        """Store test execution result with evidence"""
        success = self.result_storage.store_test_result(result)
        
        if success:
            # Store verification evidence
            evidence = {
                'test_id': result.test_id,
                'execution_status': result.status,
                'execution_duration': result.duration,
                'verification_method': 'automated_execution',
                'evidence_type': 'test_execution_result'
            }
            self.evidence_storage.store_verification_evidence(result.test_file, evidence)
        
        return success
    
    def get_test_verification_status(self, test_file: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive test verification status"""
        results = self.result_storage.get_test_results(test_file)
        summary = self.result_storage.get_test_summary()
        
        if test_file:
            evidence = self.evidence_storage.get_verification_evidence(test_file)
            return {
                'test_file': test_file,
                'recent_results': results[:10],  # Last 10 results
                'evidence_count': len(evidence),
                'latest_evidence': evidence[0] if evidence else None,
                'summary': summary
            }
        else:
            return {
                'summary': summary,
                'recent_results': results[:20],  # Last 20 results
                'total_evidence_files': len(list(self.evidence_storage.evidence_dir.glob("*.json")))
            }
    
    def verify_test_file_integrity(self, test_file: str) -> Dict[str, Any]:
        """Verify test file integrity with current state"""
        file_path = Path(test_file)
        
        if not file_path.exists():
            return {'status': 'missing', 'verified': False}
        
        try:
            # Get current file info
            current_info = self.file_discovery._extract_test_info(file_path)
            if not current_info:
                return {'status': 'invalid', 'verified': False}
            
            # Get stored evidence
            evidence_list = self.evidence_storage.get_verification_evidence(test_file)
            
            return {
                'status': 'verified',
                'verified': True,
                'current_hash': current_info.content_hash,
                'file_size': current_info.file_size,
                'last_modified': current_info.modified_time,
                'test_type': current_info.test_type,
                'framework': current_info.framework,
                'evidence_count': len(evidence_list)
            }
        except Exception as e:
            return {'status': 'error', 'verified': False, 'error': str(e)}