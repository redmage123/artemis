#!/usr/bin/env python3
"""
JSON File Persistence Store

WHY: Provides simple file-based persistence for development and testing
     when database is not needed or available.

RESPONSIBILITY: Manages pipeline state persistence using JSON files.
                Handles file I/O and directory management.

PATTERNS:
- Strategy Pattern: Implements PersistenceStoreInterface
- Early Return Pattern: Guard clauses for validation
- Single Responsibility: Focused on JSON file operations only
- Repository Pattern: Abstracts file access from business logic
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional

from .interface import PersistenceStoreInterface
from .models import PipelineState, StageCheckpoint
from .serialization import (
    serialize_pipeline_state,
    deserialize_pipeline_state,
    serialize_stage_checkpoint,
    deserialize_stage_checkpoint
)


class JSONFilePersistenceStore(PersistenceStoreInterface):
    """
    JSON file-based persistence store (fallback).

    WHY: Provides simple file-based persistence for development and testing
         when database is not needed or available.

    RESPONSIBILITY: Manages pipeline state persistence using JSON files.
                    Handles file I/O and directory management.

    PATTERNS: Strategy Pattern - implements PersistenceStoreInterface.
              Early Return Pattern - guard clauses for validation.

    Simple file-based storage for when database is not available.
    Good for development/testing.
    """

    def __init__(self, storage_dir: str = "../../.artemis_data/persistence"):
        """
        Initialize JSON file store.

        WHY: Creates storage directory for JSON persistence files.
        PERFORMANCE: O(1) directory creation if not exists.

        Args:
            storage_dir: Directory to store JSON files (relative to .agents/agile)
        """
        # Convert relative path to absolute
        if not os.path.isabs(storage_dir):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            storage_dir = os.path.join(script_dir, storage_dir)

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True, parents=True)

    def save_pipeline_state(self, state: PipelineState) -> None:
        """
        Save pipeline state to JSON file.

        WHY: Persists pipeline state for recovery and audit trail.
        PERFORMANCE: O(n) where n is state size, file write operation.
        """
        file_path = self.storage_dir / f"{state.card_id}_state.json"
        with open(file_path, 'w') as f:
            json.dump(serialize_pipeline_state(state), f, indent=2)

    def load_pipeline_state(self, card_id: str) -> Optional[PipelineState]:
        """
        Load pipeline state from JSON file.

        WHY: Retrieves saved pipeline state for resume/recovery.
        PERFORMANCE: O(n) where n is file size, file read operation.
        """
        file_path = self.storage_dir / f"{card_id}_state.json"
        # Early return guard clause - file doesn't exist
        if not file_path.exists():
            return None

        # File exists - load and parse
        with open(file_path) as f:
            data = json.load(f)
            return deserialize_pipeline_state(data)

    def save_stage_checkpoint(self, checkpoint: StageCheckpoint) -> None:
        """
        Save stage checkpoint to JSON file.

        WHY: Records stage execution for granular recovery and debugging.
        PERFORMANCE: O(n) where n is checkpoint list size, file read+write operation.
        """
        file_path = self.storage_dir / f"{checkpoint.card_id}_checkpoints.json"

        # Load existing checkpoints
        checkpoints = []
        if file_path.exists():
            with open(file_path) as f:
                checkpoints = json.load(f)

        # Append new checkpoint
        checkpoints.append(serialize_stage_checkpoint(checkpoint))

        # Save
        with open(file_path, 'w') as f:
            json.dump(checkpoints, f, indent=2)

    def load_stage_checkpoints(self, card_id: str) -> List[StageCheckpoint]:
        """
        Load stage checkpoints from JSON file.

        WHY: Retrieves stage execution history for recovery and analysis.
        PERFORMANCE: O(n) where n is file size, file read operation.
        """
        file_path = self.storage_dir / f"{card_id}_checkpoints.json"
        # Early return guard clause - file doesn't exist
        if not file_path.exists():
            return []

        # File exists - load and parse checkpoints
        with open(file_path) as f:
            data = json.load(f)
            return [deserialize_stage_checkpoint(cp) for cp in data]

    def get_resumable_pipelines(self) -> List[str]:
        """
        Get list of resumable pipelines.

        WHY: Identifies incomplete pipelines for recovery.
        PERFORMANCE: O(n*m) where n is files, m is avg file size (file scan).
        """
        resumable = []
        for file_path in self.storage_dir.glob("*_state.json"):
            with open(file_path) as f:
                state = json.load(f)
                if state['status'] in ['running', 'failed', 'paused']:
                    resumable.append(state['card_id'])
        return resumable

    def cleanup_old_states(self, days: int = 30) -> None:
        """
        Clean up old state files.

        WHY: Prevents unbounded storage growth by removing old files.
        PERFORMANCE: O(n) where n is number of files, file system scan.
        """
        cutoff = datetime.utcnow() - timedelta(days=days)

        for file_path in self.storage_dir.glob("*.json"):
            mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            if mtime < cutoff:
                file_path.unlink()
