#!/usr/bin/env python3
"""
WHY: Persist state machine state to disk for recovery and debugging
RESPONSIBILITY: Save and load pipeline state snapshots to/from filesystem
PATTERNS: Repository pattern for persistence, serialization strategy
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from state_machine.pipeline_snapshot import PipelineSnapshot
from state_machine.pipeline_state import PipelineState
from state_machine.stage_state_info import StageStateInfo


class StatePersistence:
    """
    Handles state persistence to filesystem

    Features:
    - JSON-based state serialization
    - Automatic directory creation
    - State snapshot saving
    - Conversion to JSON-serializable format
    """

    def __init__(self, state_dir: Path, card_id: str, verbose: bool = True) -> None:
        """
        Initialize state persistence

        Args:
            state_dir: Directory for state files
            card_id: Kanban card ID
            verbose: Enable verbose logging
        """
        self.state_dir = state_dir
        self.card_id = card_id
        self.verbose = verbose
        self._ensure_state_directory()

    def _ensure_state_directory(self) -> None:
        """Ensure state directory exists"""
        self.state_dir.mkdir(exist_ok=True, parents=True)

    def save_snapshot(self, snapshot: PipelineSnapshot) -> None:
        """
        Save pipeline snapshot to disk

        Args:
            snapshot: Snapshot to save
        """
        state_file = self._get_state_file_path()
        state_data = self._convert_snapshot_to_json(snapshot)

        with open(state_file, 'w') as f:
            json.dump(state_data, f, indent=2)

    def _get_state_file_path(self) -> Path:
        """Get state file path"""
        return self.state_dir / f"{self.card_id}_state.json"

    def _convert_snapshot_to_json(self, snapshot: PipelineSnapshot) -> Dict[str, Any]:
        """
        Convert snapshot to JSON-serializable format

        Args:
            snapshot: Snapshot to convert

        Returns:
            JSON-serializable dictionary
        """
        return {
            "state": snapshot.state.value,
            "timestamp": snapshot.timestamp.isoformat(),
            "card_id": snapshot.card_id,
            "active_stage": snapshot.active_stage,
            "health_status": snapshot.health_status,
            "circuit_breakers_open": snapshot.circuit_breakers_open,
            "active_issues": [issue.value for issue in snapshot.active_issues],
            "stages": self._convert_stages_to_json(snapshot.stages)
        }

    def _convert_stages_to_json(
        self,
        stages: Dict[str, StageStateInfo]
    ) -> Dict[str, Dict[str, Any]]:
        """Convert stage states to JSON-serializable format"""
        return {
            name: {
                "stage_name": info.stage_name,
                "state": info.state.value,
                "start_time": info.start_time.isoformat() if info.start_time else None,
                "end_time": info.end_time.isoformat() if info.end_time else None,
                "duration_seconds": info.duration_seconds,
                "retry_count": info.retry_count,
                "error_message": info.error_message,
                "metadata": info.metadata
            }
            for name, info in stages.items()
        }

    def load_snapshot(self) -> Dict[str, Any]:
        """
        Load pipeline snapshot from disk

        Returns:
            Snapshot data dictionary, or empty dict if not found
        """
        state_file = self._get_state_file_path()

        # Guard: Check file exists
        if not state_file.exists():
            if self.verbose:
                print(f"[StatePersistence] No state file found: {state_file}")
            return {}

        try:
            with open(state_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            if self.verbose:
                print(f"[StatePersistence] ⚠️  Failed to load state: {e}")
            return {}

    def delete_snapshot(self) -> None:
        """Delete state snapshot from disk"""
        state_file = self._get_state_file_path()

        # Guard: Check file exists
        if not state_file.exists():
            return

        try:
            state_file.unlink()
            if self.verbose:
                print(f"[StatePersistence] Deleted state file: {state_file}")
        except Exception as e:
            if self.verbose:
                print(f"[StatePersistence] ⚠️  Failed to delete state: {e}")
