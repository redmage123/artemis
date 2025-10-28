#!/usr/bin/env python3
"""
Persistence Store Interface

WHY: Defines contract for all persistence backends, enabling multiple
     storage implementations (SQLite, PostgreSQL, JSON) without changing
     client code.

RESPONSIBILITY: Defines abstract interface for persistence operations.
                All concrete stores must implement these methods.

PATTERNS:
- Strategy Pattern: Interface for interchangeable storage backends
- Dependency Inversion Principle: Clients depend on abstraction not concretions
- Single Responsibility Principle: One clear interface for all persistence operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from .models import PipelineState, StageCheckpoint


class PersistenceStoreInterface(ABC):
    """
    Abstract interface for persistence stores.

    WHY: Defines contract for all persistence backends, enabling multiple
         storage implementations (SQLite, PostgreSQL, JSON) without changing
         client code.

    RESPONSIBILITY: Defines abstract interface for persistence operations.
                    All concrete stores must implement these methods.

    PATTERNS: Strategy Pattern - defines interface for interchangeable storage backends.
              Dependency Inversion Principle - clients depend on abstraction not concretions.
    """

    @abstractmethod
    def save_pipeline_state(self, state: PipelineState) -> None:
        """
        Save complete pipeline state.

        WHY: Persists pipeline state for recovery and audit trail.
        PERFORMANCE: Implementation-dependent (SQLite: O(1), file: O(n)).
        """
        pass

    @abstractmethod
    def load_pipeline_state(self, card_id: str) -> Optional[PipelineState]:
        """
        Load pipeline state by card ID.

        WHY: Retrieves saved pipeline state for resume/recovery.
        PERFORMANCE: Implementation-dependent (SQLite indexed: O(1), file scan: O(n)).
        """
        pass

    @abstractmethod
    def save_stage_checkpoint(self, checkpoint: StageCheckpoint) -> None:
        """
        Save stage checkpoint.

        WHY: Records stage execution for granular recovery and debugging.
        PERFORMANCE: Implementation-dependent (SQLite: O(1), file append: O(1)).
        """
        pass

    @abstractmethod
    def load_stage_checkpoints(self, card_id: str) -> List[StageCheckpoint]:
        """
        Load all stage checkpoints for a card.

        WHY: Retrieves stage execution history for recovery and analysis.
        PERFORMANCE: Implementation-dependent (SQLite indexed: O(n), file scan: O(n)).
        """
        pass

    @abstractmethod
    def get_resumable_pipelines(self) -> List[str]:
        """
        Get list of pipeline card IDs that can be resumed.

        WHY: Identifies incomplete pipelines for recovery.
        PERFORMANCE: Implementation-dependent (SQLite indexed: O(n), file scan: O(n)).
        """
        pass

    @abstractmethod
    def cleanup_old_states(self, days: int = 30) -> None:
        """
        Clean up states older than X days.

        WHY: Prevents unbounded storage growth by removing old completed pipelines.
        PERFORMANCE: Implementation-dependent (SQLite: O(n), file scan: O(n)).
        """
        pass
