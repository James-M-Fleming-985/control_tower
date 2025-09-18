"""
Phase Data Interface for RED-GREEN-REFACTOR Cycle Enforcer
=========================================================

Data access interface providing query operations, transaction management,
and database abstraction for TDD phase tracking.
"""

import sqlite3
from contextlib import contextmanager
from typing import Dict, List, Optional, Any
from datetime import datetime

from .phase_models import TDDPhase


class PhaseDataInterface:
    """Phase data access interface"""
    
    def __init__(self, db_connection_string: str, git_repo_path: str):
        self.db_connection_string = db_connection_string
        self.git_repo_path = git_repo_path
        
        # Extract database path from connection string
        if "sqlite:///" in db_connection_string:
            self.db_path = db_connection_string.replace("sqlite:///", "")
        else:
            self.db_path = db_connection_string
        
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database connection"""
        with sqlite3.connect(self.db_path) as conn:
            # Ensure tables exist
            conn.execute("""
                CREATE TABLE IF NOT EXISTS phases (
                    phase_id TEXT PRIMARY KEY,
                    phase_type TEXT NOT NULL,
                    feature_id TEXT NOT NULL,
                    layer_id TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    status TEXT NOT NULL,
                    metadata TEXT,
                    context TEXT
                )
            """)
    
    def is_connected(self) -> bool:
        """Check if interface is connected"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("SELECT 1")
            return True
        except:
            return False
    
    def supports_transactions(self) -> bool:
        """Check if transactions are supported"""
        return True
    
    def query_phases(self, **filters) -> List[TDDPhase]:
        """Query phases with filters"""
        query = "SELECT phase_id, phase_type, feature_id, layer_id, started_at, completed_at, status FROM phases WHERE 1=1"
        params = []
        
        if "status" in filters:
            query += " AND status = ?"
            params.append(filters["status"])
        
        if "phase_type" in filters:
            query += " AND phase_type = ?"
            params.append(filters["phase_type"])
        
        if "feature_id" in filters:
            query += " AND feature_id = ?"
            params.append(filters["feature_id"])
        
        if "phase_id" in filters:
            query += " AND phase_id = ?"
            params.append(filters["phase_id"])
        
        phases = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            
            for row in cursor.fetchall():
                completed_at = None
                if row[5]:
                    completed_at = datetime.fromisoformat(row[5])
                
                phase = TDDPhase(
                    phase_id=row[0],
                    phase_type=row[1],
                    feature_id=row[2],
                    layer_id=row[3],
                    started_at=datetime.fromisoformat(row[4]),
                    completed_at=completed_at,
                    status=row[6]
                )
                phases.append(phase)
        
        return phases
    
    @contextmanager
    def transaction(self):
        """Transaction context manager"""
        transaction = DatabaseTransaction(self.db_path)
        try:
            yield transaction
            transaction.commit()
        except Exception:
            transaction.rollback()
            raise


class DatabaseTransaction:
    """Database transaction manager"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("BEGIN")
        self._rolled_back = False
    
    def create_phase(self, phase: TDDPhase):
        """Create phase within transaction"""
        # Check for duplicate
        cursor = self.conn.execute("SELECT phase_id FROM phases WHERE phase_id = ?", (phase.phase_id,))
        if cursor.fetchone():
            raise ValueError(f"Phase {phase.phase_id} already exists")
        
        self.conn.execute("""
            INSERT INTO phases 
            (phase_id, phase_type, feature_id, layer_id, started_at, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            phase.phase_id,
            phase.phase_type,
            phase.feature_id,
            phase.layer_id,
            phase.started_at.isoformat(),
            phase.status
        ))
    
    def commit(self):
        """Commit transaction"""
        if not self._rolled_back:
            self.conn.execute("COMMIT")
        self.conn.close()
    
    def rollback(self):
        """Rollback transaction"""
        self.conn.execute("ROLLBACK")
        self._rolled_back = True
        self.conn.close()