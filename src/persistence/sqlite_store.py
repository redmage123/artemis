#!/usr/bin/env python3
"""
SQLite Persistence Store

WHY: Provides ACID-compliant persistence without external database server.
     Ideal for single-machine deployments and development environments.

RESPONSIBILITY: Manages pipeline state persistence using SQLite backend.
                Handles database connections, schema, and queries.

PATTERNS:
- Strategy Pattern: Implements PersistenceStoreInterface
- Early Return Pattern: Guard clauses for validation
- Single Responsibility: Focused on SQLite operations only
- Repository Pattern: Abstracts data access from business logic
"""

import os
import sqlite3
import json
from typing import List, Optional, Dict, Any

from .interface import PersistenceStoreInterface
from .models import PipelineState, StageCheckpoint


class SQLitePersistenceStore(PersistenceStoreInterface):
    """
    SQLite-based persistence store.

    WHY: Provides ACID-compliant persistence without external database server.
         Ideal for single-machine deployments and development environments.

    RESPONSIBILITY: Manages pipeline state persistence using SQLite backend.
                    Handles database connections, schema, and queries.

    PATTERNS: Strategy Pattern - implements PersistenceStoreInterface.
              Early Return Pattern - guard clauses for validation.

    Benefits:
    - File-based (no server needed)
    - ACID transactions
    - SQL queries for analysis
    - Good for single-machine deployment
    """

    def __init__(self, db_path: str = "../../.artemis_data/artemis_persistence.db"):
        """
        Initialize SQLite store.

        WHY: Creates database connection and ensures schema exists.
        PERFORMANCE: O(1) connection, schema creation only runs if tables missing.

        Args:
            db_path: Path to SQLite database file (relative to .agents/agile)
        """
        # Convert relative path to absolute
        if not os.path.isabs(db_path):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(script_dir, db_path)

        self.db_path = db_path

        # Ensure parent directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row  # Enable dict access
        self._create_tables()

    def _create_tables(self) -> None:
        """
        Create database tables if they don't exist.

        WHY: Ensures database schema exists before operations.
        PERFORMANCE: O(1) - only creates tables if missing, uses indexes for queries.
        """
        cursor = self.connection.cursor()

        # Pipeline states table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_states (
                card_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                current_stage TEXT,
                stages_completed TEXT,  -- JSON array
                stage_results TEXT,     -- JSON object
                developer_results TEXT, -- JSON array
                metrics TEXT,           -- JSON object
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                completed_at TEXT,
                error TEXT
            )
        """)

        # Stage checkpoints table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stage_checkpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id TEXT NOT NULL,
                stage_name TEXT NOT NULL,
                status TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                result TEXT,  -- JSON object
                error TEXT,
                UNIQUE(card_id, stage_name, started_at)
            )
        """)

        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_pipeline_status
            ON pipeline_states(status)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_stage_card_id
            ON stage_checkpoints(card_id)
        """)

        self.connection.commit()

    def save_pipeline_state(self, state: PipelineState) -> None:
        """
        Save complete pipeline state.

        WHY: Persists pipeline state for recovery and audit trail.
        PERFORMANCE: O(1) INSERT OR REPLACE with indexed primary key.
        """
        cursor = self.connection.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO pipeline_states (
                card_id, status, current_stage, stages_completed,
                stage_results, developer_results, metrics,
                created_at, updated_at, completed_at, error
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            state.card_id,
            state.status,
            state.current_stage,
            json.dumps(state.stages_completed),
            json.dumps(state.stage_results),
            json.dumps(state.developer_results),
            json.dumps(state.metrics),
            state.created_at,
            state.updated_at,
            state.completed_at,
            state.error
        ))

        self.connection.commit()

    def load_pipeline_state(self, card_id: str) -> Optional[PipelineState]:
        """
        Load pipeline state by card ID.

        WHY: Retrieves saved pipeline state for resume/recovery.
        PERFORMANCE: O(1) indexed lookup by primary key.
        """
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT * FROM pipeline_states WHERE card_id = ?
        """, (card_id,))

        row = cursor.fetchone()
        # Early return guard clause - no row found
        if not row:
            return None

        # Row found - reconstruct PipelineState
        return PipelineState(
            card_id=row['card_id'],
            status=row['status'],
            current_stage=row['current_stage'],
            stages_completed=json.loads(row['stages_completed']),
            stage_results=json.loads(row['stage_results']),
            developer_results=json.loads(row['developer_results']),
            metrics=json.loads(row['metrics']),
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            completed_at=row['completed_at'],
            error=row['error']
        )

    def save_stage_checkpoint(self, checkpoint: StageCheckpoint) -> None:
        """
        Save stage checkpoint.

        WHY: Records stage execution for granular recovery and debugging.
        PERFORMANCE: O(1) INSERT OR REPLACE with unique constraint.
        """
        cursor = self.connection.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO stage_checkpoints (
                card_id, stage_name, status, started_at,
                completed_at, result, error
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            checkpoint.card_id,
            checkpoint.stage_name,
            checkpoint.status,
            checkpoint.started_at,
            checkpoint.completed_at,
            json.dumps(checkpoint.result),
            checkpoint.error
        ))

        self.connection.commit()

    def load_stage_checkpoints(self, card_id: str) -> List[StageCheckpoint]:
        """
        Load all stage checkpoints for a card.

        WHY: Retrieves stage execution history for recovery and analysis.
        PERFORMANCE: O(n) where n is number of checkpoints, uses indexed card_id.
        """
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT * FROM stage_checkpoints
            WHERE card_id = ?
            ORDER BY started_at ASC
        """, (card_id,))

        checkpoints = []
        for row in cursor.fetchall():
            checkpoints.append(StageCheckpoint(
                card_id=row['card_id'],
                stage_name=row['stage_name'],
                status=row['status'],
                started_at=row['started_at'],
                completed_at=row['completed_at'],
                result=json.loads(row['result']),
                error=row['error']
            ))

        return checkpoints

    def get_resumable_pipelines(self) -> List[str]:
        """
        Get list of pipeline card IDs that can be resumed.

        WHY: Identifies incomplete pipelines for recovery.
        PERFORMANCE: O(n) indexed status scan, returns only matching pipelines.
        """
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT card_id FROM pipeline_states
            WHERE status IN ('running', 'failed', 'paused')
            ORDER BY updated_at DESC
        """)

        return [row['card_id'] for row in cursor.fetchall()]

    def cleanup_old_states(self, days: int = 30) -> None:
        """
        Clean up states older than X days.

        WHY: Prevents unbounded storage growth by removing old completed pipelines.
        PERFORMANCE: O(n) deletion, cascades to orphaned checkpoints.
        """
        from datetime import datetime, timedelta

        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat() + 'Z'

        cursor = self.connection.cursor()

        # Delete old completed/failed pipelines
        cursor.execute("""
            DELETE FROM pipeline_states
            WHERE status IN ('completed', 'failed')
            AND updated_at < ?
        """, (cutoff,))

        # Delete associated checkpoints
        cursor.execute("""
            DELETE FROM stage_checkpoints
            WHERE card_id NOT IN (SELECT card_id FROM pipeline_states)
        """)

        self.connection.commit()

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics.

        WHY: Provides visibility into persistence store usage and health.
        PERFORMANCE: O(n) aggregation queries across all pipelines.
        """
        cursor = self.connection.cursor()

        cursor.execute("SELECT COUNT(*) as total FROM pipeline_states")
        total = cursor.fetchone()['total']

        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM pipeline_states
            GROUP BY status
        """)
        by_status = {row['status']: row['count'] for row in cursor.fetchall()}

        cursor.execute("SELECT COUNT(*) as total FROM stage_checkpoints")
        total_checkpoints = cursor.fetchone()['total']

        return {
            "total_pipelines": total,
            "by_status": by_status,
            "total_checkpoints": total_checkpoints,
            "db_path": self.db_path
        }

    def close(self) -> None:
        """
        Close database connection.

        WHY: Releases database resources and ensures clean shutdown.
        PERFORMANCE: O(1) connection cleanup.
        """
        # Early return guard clause - no connection to close
        if not self.connection:
            return

        # Connection exists - close it
        self.connection.close()
