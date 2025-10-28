#!/usr/bin/env python3
"""
Checkpoint Data Models

WHY: Defines immutable data structures for checkpoint state representation,
     ensuring type safety and consistent serialization across the system.

RESPONSIBILITY:
    - Define checkpoint status enumeration
    - Model stage-level checkpoint data
    - Model pipeline-level checkpoint data
    - Provide serialization/deserialization methods

PATTERNS:
    - Data Transfer Object: Pure data structures without business logic
    - Dataclass Pattern: Leverages Python dataclasses for clean data modeling
    - Builder Pattern: from_dict classmethod for object construction
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


# ============================================================================
# ENUMERATIONS
# ============================================================================

class CheckpointStatus(Enum):
    """
    Pipeline checkpoint status enumeration

    Defines the lifecycle states a checkpoint can be in
    """
    ACTIVE = "active"           # Pipeline currently running
    PAUSED = "paused"           # Pipeline paused by user
    COMPLETED = "completed"     # Pipeline finished successfully
    FAILED = "failed"           # Pipeline failed with error
    RESUMED = "resumed"         # Resumed from previous checkpoint


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class StageCheckpoint:
    """
    Checkpoint data for a single pipeline stage

    Captures all execution details for one stage including timing,
    results, artifacts, and LLM interactions.
    """
    stage_name: str
    status: str  # completed, failed, skipped
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    result: Optional[Dict[str, Any]] = None
    artifacts: List[str] = field(default_factory=list)  # File paths
    llm_responses: List[Dict[str, Any]] = field(default_factory=list)
    error_message: Optional[str] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert stage checkpoint to dictionary for serialization

        Returns:
            Dictionary representation with ISO-formatted timestamps
        """
        return {
            "stage_name": self.stage_name,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "result": self.result,
            "artifacts": self.artifacts,
            "llm_responses": self.llm_responses,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StageCheckpoint':
        """
        Create StageCheckpoint from dictionary

        Args:
            data: Dictionary containing checkpoint data

        Returns:
            StageCheckpoint instance
        """
        return cls(
            stage_name=data["stage_name"],
            status=data["status"],
            start_time=datetime.fromisoformat(data["start_time"]) if data.get("start_time") else datetime.now(),
            end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None,
            duration_seconds=data.get("duration_seconds", 0.0),
            result=data.get("result"),
            artifacts=data.get("artifacts", []),
            llm_responses=data.get("llm_responses", []),
            error_message=data.get("error_message"),
            retry_count=data.get("retry_count", 0),
            metadata=data.get("metadata", {})
        )


@dataclass
class PipelineCheckpoint:
    """
    Complete pipeline checkpoint containing all execution state

    Root checkpoint object that aggregates stage checkpoints,
    execution context, statistics, and recovery metadata.
    """
    checkpoint_id: str
    card_id: str
    status: CheckpointStatus
    created_at: datetime
    updated_at: datetime

    # Stage tracking
    completed_stages: List[str] = field(default_factory=list)
    failed_stages: List[str] = field(default_factory=list)
    skipped_stages: List[str] = field(default_factory=list)
    current_stage: Optional[str] = None

    # Stage details
    stage_checkpoints: Dict[str, StageCheckpoint] = field(default_factory=dict)

    # Execution context
    execution_context: Dict[str, Any] = field(default_factory=dict)

    # Statistics
    total_stages: int = 0
    stages_completed: int = 0
    total_duration_seconds: float = 0.0
    estimated_remaining_seconds: float = 0.0

    # Recovery info
    resume_count: int = 0
    last_resume_time: Optional[datetime] = None

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert pipeline checkpoint to dictionary for serialization

        Returns:
            Complete dictionary representation with nested stage data
        """
        return {
            "checkpoint_id": self.checkpoint_id,
            "card_id": self.card_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_stages": self.completed_stages,
            "failed_stages": self.failed_stages,
            "skipped_stages": self.skipped_stages,
            "current_stage": self.current_stage,
            "stage_checkpoints": {
                name: cp.to_dict()
                for name, cp in self.stage_checkpoints.items()
            },
            "execution_context": self.execution_context,
            "total_stages": self.total_stages,
            "stages_completed": self.stages_completed,
            "total_duration_seconds": self.total_duration_seconds,
            "estimated_remaining_seconds": self.estimated_remaining_seconds,
            "resume_count": self.resume_count,
            "last_resume_time": self.last_resume_time.isoformat() if self.last_resume_time else None,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PipelineCheckpoint':
        """
        Create PipelineCheckpoint from dictionary

        Args:
            data: Dictionary containing checkpoint data

        Returns:
            PipelineCheckpoint instance with all nested stage checkpoints
        """
        # Parse stage checkpoints
        stage_checkpoints = {}
        for name, cp_data in data.get("stage_checkpoints", {}).items():
            stage_checkpoints[name] = StageCheckpoint.from_dict(cp_data)

        return cls(
            checkpoint_id=data["checkpoint_id"],
            card_id=data["card_id"],
            status=CheckpointStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            completed_stages=data.get("completed_stages", []),
            failed_stages=data.get("failed_stages", []),
            skipped_stages=data.get("skipped_stages", []),
            current_stage=data.get("current_stage"),
            stage_checkpoints=stage_checkpoints,
            execution_context=data.get("execution_context", {}),
            total_stages=data.get("total_stages", 0),
            stages_completed=data.get("stages_completed", 0),
            total_duration_seconds=data.get("total_duration_seconds", 0.0),
            estimated_remaining_seconds=data.get("estimated_remaining_seconds", 0.0),
            resume_count=data.get("resume_count", 0),
            last_resume_time=datetime.fromisoformat(data["last_resume_time"]) if data.get("last_resume_time") else None,
            metadata=data.get("metadata", {})
        )


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def calculate_progress_percent(stages_completed: int, total_stages: int) -> float:
    """
    Calculate pipeline progress percentage

    Args:
        stages_completed: Number of completed stages
        total_stages: Total number of stages

    Returns:
        Progress percentage (0-100)
    """
    if total_stages == 0:
        return 0.0

    return round((stages_completed / total_stages) * 100, 2)


def estimate_remaining_time(
    total_duration_seconds: float,
    stages_completed: int,
    total_stages: int
) -> float:
    """
    Estimate remaining execution time based on average stage duration

    Args:
        total_duration_seconds: Total time spent so far
        stages_completed: Number of completed stages
        total_stages: Total number of stages

    Returns:
        Estimated remaining seconds
    """
    if stages_completed == 0:
        return 0.0

    avg_stage_duration = total_duration_seconds / stages_completed
    remaining_stages = total_stages - stages_completed

    return round(avg_stage_duration * remaining_stages, 2)
