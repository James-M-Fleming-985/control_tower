#!/usr/bin/env python3
"""
Test Generation Verification System - Data Access Layer Implementation

Implementation for LAYER-003-01-02-001: Data Access Layer for Test Generation Verification
Provides REAL file verification, test discovery, and physical evidence storage.

Created: 2025-09-18
Phase: TDD GREEN phase - Minimal implementation to pass tests
"""

import os
import json
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, NamedTuple
from dataclasses import dataclass


@dataclass
class FileVerificationResult:
    """Result of physical file verification"""
    exists: bool
    is_test_file: bool
    file_size: int = 0
    last_modified: Optional[datetime] = None
    error_message: Optional[str] = None


class TestFileDiscovery:
    """REAL test file discovery and physical file verification"""
    
    def __init__(self, base_path: str):
        """Initialize test file discovery with base search path"""
        self.base_path = Path(base_path)
        self.discovered_files = []
    
    def discover_test_files(self) -> List[str]:
        """Discover REAL test files from physical file system"""
        test_files = []
        
        # Search for real test files
        for test_file in self.base_path.rglob("test_*.py"):
            if test_file.is_file():
                test_files.append(str(test_file))
        
        self.discovered_files = test_files
        return test_files
    
    def verify_file_exists(self, file_path: str) -> FileVerificationResult:
        """Verify REAL file existence and test file validity"""
        file_obj = Path(file_path)
        
        if not file_obj.exists():
            return FileVerificationResult(
                exists=False,
                is_test_file=False,
                error_message=f"File does not exist: {file_path}"
            )
        
        # Physical verification
        is_test_file = (
            file_obj.name.startswith("test_") and 
            file_obj.suffix == ".py"
        )
        
        return FileVerificationResult(
            exists=True,
            is_test_file=is_test_file,
            file_size=file_obj.stat().st_size,
            last_modified=datetime.fromtimestamp(file_obj.stat().st_mtime)
        )


class TestResultStorage:
    """REAL test execution result storage with file system persistence"""
    
    def __init__(self, storage_path: str):
        """Initialize test result storage with physical database"""
        self.storage_path = Path(storage_path)
        self.db_path = self.storage_path / "test_results.db"
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for REAL storage"""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_name TEXT NOT NULL,
                status TEXT NOT NULL,
                duration REAL,
                timestamp TEXT,
                file_path TEXT,
                output TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def store_test_result(self, test_result: Dict[str, Any]) -> int:
        """Store REAL test result to physical database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO test_results (test_name, status, duration, timestamp, file_path, output)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            test_result["test_name"],
            test_result["status"],
            test_result.get("duration"),
            test_result.get("timestamp"),
            test_result.get("file_path"),
            test_result.get("output", "")
        ))
        
        result_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return result_id
    
    def get_test_result(self, result_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve REAL test result from physical storage"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT test_name, status, duration, timestamp, file_path, output, created_at
            FROM test_results WHERE id = ?
        """, (result_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "test_name": row[0],
                "status": row[1],
                "duration": row[2],
                "timestamp": row[3],
                "file_path": row[4],
                "output": row[5],
                "created_at": row[6]
            }
        return None
    
    def query_test_results(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query stored test results with optional filtering"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        if status:
            cursor.execute("""
                SELECT test_name, status, duration, timestamp, file_path, output, created_at
                FROM test_results WHERE status = ?
            """, (status,))
        else:
            cursor.execute("""
                SELECT test_name, status, duration, timestamp, file_path, output, created_at
                FROM test_results
            """)
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                "test_name": row[0],
                "status": row[1],
                "duration": row[2],
                "timestamp": row[3],
                "file_path": row[4],
                "output": row[5],
                "created_at": row[6]
            })
        
        return results


class TestMetadataPersistence:
    """REAL test metadata persistence with physical evidence collection"""
    
    def __init__(self, storage_path: str):
        """Initialize metadata persistence with physical file storage"""
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.metadata_counter = 0
    
    def store_metadata(self, metadata: Dict[str, Any]) -> str:
        """Store REAL test metadata to physical JSON files"""
        self.metadata_counter += 1
        metadata_id = f"meta_{self.metadata_counter}_{int(datetime.now().timestamp())}"
        
        # Add storage timestamp
        metadata["stored_at"] = datetime.now().isoformat()
        metadata["metadata_id"] = metadata_id
        
        # Store to physical JSON file
        metadata_file = self.storage_path / f"metadata_{metadata_id}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return metadata_id
    
    def get_metadata(self, metadata_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve REAL metadata from physical JSON files"""
        metadata_file = self.storage_path / f"metadata_{metadata_id}.json"
        
        if not metadata_file.exists():
            return None
        
        with open(metadata_file, 'r') as f:
            return json.load(f)
    
    def collect_file_evidence(self, file_path: str) -> Dict[str, Any]:
        """Collect REAL physical evidence about test files"""
        file_obj = Path(file_path)
        
        evidence = {
            "file_path": file_path,
            "file_exists": file_obj.exists(),
            "collected_at": datetime.now().isoformat()
        }
        
        if file_obj.exists():
            evidence.update({
                "file_size": file_obj.stat().st_size,
                "last_modified": datetime.fromtimestamp(file_obj.stat().st_mtime).isoformat(),
                "is_python_file": file_obj.suffix == ".py"
            })
            
            # Read file content for function analysis
            try:
                content = file_obj.read_text()
                evidence["line_count"] = len(content.splitlines())
                
                # Extract function names (simple pattern matching)
                import re
                function_pattern = r'def\s+(\w+)\s*\('
                functions = re.findall(function_pattern, content)
                evidence["function_names"] = functions
                
            except Exception as e:
                evidence["read_error"] = str(e)
        else:
            evidence.update({
                "file_size": 0,
                "line_count": 0,
                "function_names": []
            })
        
        return evidence


class VerificationEvidenceStorage:
    """REAL verification evidence storage for stage gate enforcement"""
    
    def __init__(self, storage_path: str):
        """Initialize evidence storage with physical file system"""
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.evidence_counter = 0
    
    def store_evidence(self, evidence: Dict[str, Any]) -> str:
        """Store REAL stage gate evidence to physical files"""
        self.evidence_counter += 1
        evidence_id = f"evidence_{self.evidence_counter}_{int(datetime.now().timestamp())}"
        
        # Add storage metadata
        evidence["evidence_id"] = evidence_id
        evidence["stored_at"] = datetime.now().isoformat()
        evidence["storage_path"] = str(self.storage_path)
        
        # Calculate evidence checksum for integrity
        evidence_str = json.dumps(evidence, sort_keys=True)
        evidence["checksum"] = hashlib.sha256(evidence_str.encode()).hexdigest()
        
        # Store to physical JSON file
        evidence_file = self.storage_path / f"evidence_{evidence_id}.json"
        with open(evidence_file, 'w') as f:
            json.dump(evidence, f, indent=2)
        
        return evidence_id
    
    def get_evidence(self, evidence_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve REAL evidence from physical storage"""
        evidence_file = self.storage_path / f"evidence_{evidence_id}.json"
        
        if not evidence_file.exists():
            return None
        
        with open(evidence_file, 'r') as f:
            return json.load(f)
    
    def query_evidence_by_stage(self, stage_gate: str) -> List[Dict[str, Any]]:
        """Query evidence by stage gate from physical files"""
        evidence_list = []
        
        # Scan all evidence files
        for evidence_file in self.storage_path.glob("evidence_*.json"):
            try:
                with open(evidence_file, 'r') as f:
                    evidence = json.load(f)
                    if evidence.get("stage_gate") == stage_gate:
                        evidence_list.append(evidence)
            except Exception:
                continue  # Skip corrupted files
        
        return evidence_list
    
    def validate_evidence_integrity(self, evidence_id: str) -> Dict[str, Any]:
        """Validate REAL evidence integrity from physical storage"""
        evidence_file = self.storage_path / f"evidence_{evidence_id}.json"
        
        integrity_result = {
            "evidence_id": evidence_id,
            "file_exists": evidence_file.exists(),
            "is_valid": False,
            "checksum": None,
            "validation_timestamp": datetime.now().isoformat()
        }
        
        if evidence_file.exists():
            try:
                with open(evidence_file, 'r') as f:
                    evidence = json.load(f)
                
                # Verify checksum
                stored_checksum = evidence.pop("checksum", None)
                evidence_str = json.dumps(evidence, sort_keys=True)
                calculated_checksum = hashlib.sha256(evidence_str.encode()).hexdigest()
                
                integrity_result.update({
                    "is_valid": stored_checksum == calculated_checksum,
                    "checksum": calculated_checksum,
                    "stored_checksum": stored_checksum
                })
                
            except Exception as e:
                integrity_result["error"] = str(e)
        
        return integrity_result


# Data Access Layer Factory for easy instantiation
class TestGenerationDataAccess:
    """Factory for Test Generation Verification data access components"""
    
    def __init__(self, base_path: str):
        """Initialize all data access components"""
        self.base_path = base_path
        self.file_discovery = TestFileDiscovery(base_path)
        self.result_storage = TestResultStorage(base_path)
        self.metadata_persistence = TestMetadataPersistence(base_path)
        self.evidence_storage = VerificationEvidenceStorage(base_path)
    
    def get_all_components(self):
        """Get all data access components"""
        return {
            "file_discovery": self.file_discovery,
            "result_storage": self.result_storage,
            "metadata_persistence": self.metadata_persistence,
            "evidence_storage": self.evidence_storage
        }


if __name__ == "__main__":
    # Demo of data access layer functionality
    import tempfile
    import shutil
    
    # Create temporary demo environment
    temp_dir = tempfile.mkdtemp()
    print(f"🧪 Demo: Test Generation Data Access Layer")
    print(f"📁 Demo directory: {temp_dir}")
    
    try:
        # Create demo test file
        demo_test = Path(temp_dir) / "test_demo.py"
        demo_test.write_text("""
def test_example():
    assert True

def test_another():
    pass
""")
        
        # Initialize data access layer
        data_access = TestGenerationDataAccess(temp_dir)
        
        # 1. Test file discovery
        print("\n🔍 REAL Test File Discovery:")
        discovered = data_access.file_discovery.discover_test_files()
        print(f"   Discovered files: {discovered}")
        
        # 2. File verification
        verification = data_access.file_discovery.verify_file_exists(str(demo_test))
        print(f"   File verified: {verification.exists}, Size: {verification.file_size}")
        
        # 3. Store test result
        print("\n💾 REAL Test Result Storage:")
        test_result = {
            "test_name": "test_example",
            "status": "passed",
            "duration": 0.001,
            "timestamp": datetime.now().isoformat(),
            "file_path": str(demo_test)
        }
        result_id = data_access.result_storage.store_test_result(test_result)
        print(f"   Stored result ID: {result_id}")
        
        # 4. Store metadata
        print("\n📊 REAL Metadata Persistence:")
        metadata = {
            "test_file": str(demo_test),
            "test_count": 2,
            "last_run": datetime.now().isoformat()
        }
        metadata_id = data_access.metadata_persistence.store_metadata(metadata)
        print(f"   Stored metadata ID: {metadata_id}")
        
        # 5. Store verification evidence
        print("\n🔒 REAL Evidence Storage:")
        evidence = {
            "stage_gate": "DEMO_VERIFICATION",
            "requirement_id": "LAY-003-01-02-001",
            "verification_timestamp": datetime.now().isoformat(),
            "evidence_type": "DEMO_TEST",
            "evidence_data": {
                "files_discovered": len(discovered),
                "verification_passed": True
            }
        }
        evidence_id = data_access.evidence_storage.store_evidence(evidence)
        print(f"   Stored evidence ID: {evidence_id}")
        
        print("\n✅ Data Access Layer Demo Complete!")
        print(f"📁 Physical files created in: {temp_dir}")
        
    finally:
        # Clean up demo
        print(f"\n🧹 Cleaning up demo directory...")
        shutil.rmtree(temp_dir)
        print("✅ Demo cleanup complete")