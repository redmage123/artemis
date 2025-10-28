#!/usr/bin/env python3
"""
Persistence Data Models

WHY: Defines immutable data structures for pipeline state and stage checkpoints.
     Ensures type safety and consistent state representation across persistence layer.

RESPONSIBILITY: Provides dataclass models for pipeline state and stage checkpoint data.
                These are value objects that represent snapshots of pipeline execution.

PATTERNS:
- Dataclass Pattern: Immutable state objects with automatic methods
- Value Object Pattern: State snapshots with no behavior
- Type Safety: Strong typing for all fields
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any


@dataclass
class PipelineState:
    """
    Complete pipeline state snapshot.

    WHY: Captures all pipeline state for persistence and recovery.
         Enables resuming pipelines from any point after crashes or pauses.

    RESPONSIBILITY: Holds immutable snapshot of pipeline state at a point in time.

    PATTERNS: Dataclass pattern for immutable state objects.
    """
    card_id: str
    status: str  # running, completed, failed, paused
    current_stage: Optional[str]
    stages_completed: List[str]
    stage_results: Dict[str, Any]
    developer_results: List[Dict]
    metrics: Dict[str, Any]
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.

        WHY: Enables serialization to JSON or database formats.
        PERFORMANCE: O(n) where n is size of state object.
        """
        return asdict(self)


@dataclass
class StageCheckpoint:
    """
    Checkpoint for a single stage.

    WHY: Tracks individual stage execution for granular recovery and debugging.
         Enables resuming from specific stage failures.

    RESPONSIBILITY: Holds immutable checkpoint data for a single pipeline stage.

    PATTERNS: Dataclass pattern for immutable state objects.
    """
    card_id: str
    stage_name: str
    status: str  # started, completed, failed
    started_at: str
    completed_at: Optional[str]
    result: Dict[str, Any]
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.

        WHY: Enables serialization to JSON or database formats.
        PERFORMANCE: O(n) where n is size of checkpoint object.
        """
        return asdict(self)
