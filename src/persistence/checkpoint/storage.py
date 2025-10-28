#!/usr/bin/env python3
"""
Checkpoint Storage Backend

WHY: Abstracts checkpoint persistence operations behind a repository interface,
     enabling different storage backends (filesystem, database, cloud) while
     maintaining consistent access patterns.

RESPONSIBILITY:
    - Define storage repository interface
    - Implement filesystem-based storage
    - Handle checkpoint serialization/deserialization
    - Manage checkpoint file operations

PATTERNS:
    - Repository Pattern: Abstract data access behind interface
    - Strategy Pattern: Pluggable storage backends
    - Single Responsibility: Each storage implementation handles one backend type
"""

import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from .models import PipelineCheckpoint, CheckpointStatus


# ============================================================================
# REPOSITORY INTERFACE
# ============================================================================

class CheckpointRepository(ABC):
    """
    Abstract repository interface for checkpoint storage

    Defines contract that all storage backends must implement,
    enabling transparent backend switching.
    """

    @abstractmethod
    def save(self, checkpoint: PipelineCheckpoint) -> None:
        """
        Save checkpoint to storage

        Args:
            checkpoint: PipelineCheckpoint to save
        """
        pass

    @abstractmethod
    def load(self, card_id: str) -> Optional[PipelineCheckpoint]:
        """
        Load checkpoint from storage

        Args:
            card_id: Card ID to load checkpoint for

        Returns:
            PipelineCheckpoint if exists, None otherwise
        """
        pass

    @abstractmethod
    def exists(self, card_id: str) -> bool:
        """
        Check if checkpoint exists

        Args:
            card_id: Card ID to check

        Returns:
            True if checkpoint exists
        """
        pass

    @abstractmethod
    def delete(self, card_id: str) -> bool:
        """
        Delete checkpoint from storage

        Args:
            card_id: Card ID to delete

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def list_all(self) -> List[str]:
        """
        List all checkpoint card IDs

        Returns:
            List of card IDs with checkpoints
        """
        pass


# ============================================================================
# FILESYSTEM STORAGE IMPLEMENTATION
# ============================================================================

class FilesystemCheckpointRepository(CheckpointRepository):
    """
    Filesystem-based checkpoint storage implementation

    Stores checkpoints as JSON files in a configured directory,
    using card ID as the filename.
    """

    def __init__(self, checkpoint_dir: Optional[str] = None):
        """
        Initialize filesystem repository

        Args:
            checkpoint_dir: Directory for checkpoint storage
                          (defaults to env var or repo path)
        """
        if checkpoint_dir is None:
            checkpoint_dir = os.getenv(
                "ARTEMIS_CHECKPOINT_DIR",
                "../../.artemis_data/checkpoints"
            )

        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True, parents=True)

    def save(self, checkpoint: PipelineCheckpoint) -> None:
        """
        Save checkpoint to filesystem as JSON

        Args:
            checkpoint: PipelineCheckpoint to save

        Raises:
            IOError: If file write fails
        """
        checkpoint_file = self._get_checkpoint_path(checkpoint.card_id)

        try:
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint.to_dict(), f, indent=2)
        except IOError as e:
            raise IOError(f"Failed to save checkpoint: {e}") from e

    def load(self, card_id: str) -> Optional[PipelineCheckpoint]:
        """
        Load checkpoint from filesystem

        Args:
            card_id: Card ID to load checkpoint for

        Returns:
            PipelineCheckpoint if exists, None otherwise
        """
        if not self.exists(card_id):
            return None

        checkpoint_file = self._get_checkpoint_path(card_id)

        try:
            with open(checkpoint_file, 'r') as f:
                data = json.load(f)
            return PipelineCheckpoint.from_dict(data)
        except (IOError, json.JSONDecodeError, KeyError) as e:
            # Log error but return None to indicate load failure
            print(f"Warning: Failed to load checkpoint for {card_id}: {e}")
            return None

    def exists(self, card_id: str) -> bool:
        """
        Check if checkpoint file exists

        Args:
            card_id: Card ID to check

        Returns:
            True if checkpoint file exists
        """
        checkpoint_file = self._get_checkpoint_path(card_id)
        return checkpoint_file.exists()

    def delete(self, card_id: str) -> bool:
        """
        Delete checkpoint file

        Args:
            card_id: Card ID to delete

        Returns:
            True if deleted, False if not found
        """
        if not self.exists(card_id):
            return False

        checkpoint_file = self._get_checkpoint_path(card_id)

        try:
            checkpoint_file.unlink()
            return True
        except OSError:
            return False

    def list_all(self) -> List[str]:
        """
        List all checkpoint card IDs in directory

        Returns:
            List of card IDs with checkpoints
        """
        checkpoint_files = self.checkpoint_dir.glob("*.json")
        return [f.stem for f in checkpoint_files]

    def _get_checkpoint_path(self, card_id: str) -> Path:
        """
        Get checkpoint file path for card ID

        Args:
            card_id: Card ID

        Returns:
            Path to checkpoint file
        """
        return self.checkpoint_dir / f"{card_id}.json"


# ============================================================================
# STORAGE VALIDATION
# ============================================================================

class CheckpointValidator:
    """
    Validates checkpoint data integrity and resumability

    Ensures checkpoints meet requirements for successful restoration.
    """

    @staticmethod
    def can_resume_checkpoint(checkpoint: PipelineCheckpoint) -> bool:
        """
        Check if checkpoint can be resumed

        Guard clause approach - fail fast on invalid conditions

        Args:
            checkpoint: Checkpoint to validate

        Returns:
            True if checkpoint can be resumed
        """
        # Guard: Checkpoint must not be completed
        if checkpoint.status == CheckpointStatus.COMPLETED:
            return False

        # Guard: Checkpoint must be in resumable state
        resumable_states = [CheckpointStatus.ACTIVE, CheckpointStatus.PAUSED]
        if checkpoint.status not in resumable_states:
            return False

        # Guard: Must have valid card ID
        if not checkpoint.card_id:
            return False

        return True

    @staticmethod
    def validate_checkpoint_data(data: Dict[str, Any]) -> bool:
        """
        Validate checkpoint dictionary has required fields

        Args:
            data: Checkpoint data dictionary

        Returns:
            True if valid
        """
        required_fields = [
            "checkpoint_id",
            "card_id",
            "status",
            "created_at",
            "updated_at"
        ]

        for field in required_fields:
            if field not in data:
                return False

        return True


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_checkpoint_repository(
    storage_type: str = "filesystem",
    **kwargs
) -> CheckpointRepository:
    """
    Factory function to create checkpoint repository

    Args:
        storage_type: Type of storage backend (filesystem, database, etc.)
        **kwargs: Backend-specific configuration

    Returns:
        CheckpointRepository instance

    Raises:
        ValueError: If storage type is unknown
    """
    storage_types = {
        "filesystem": lambda: FilesystemCheckpointRepository(
            checkpoint_dir=kwargs.get("checkpoint_dir")
        ),
    }

    factory = storage_types.get(storage_type)

    if not factory:
        raise ValueError(f"Unknown storage type: {storage_type}")

    return factory()
