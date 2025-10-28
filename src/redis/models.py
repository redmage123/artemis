#!/usr/bin/env python3
"""
WHY: Define status enums for pipeline and stage tracking
RESPONSIBILITY: Provide type-safe status values for pipeline state management
PATTERNS: Value Object (immutable enums)

Status enums:
- StageStatus: Status for individual pipeline stages (PENDING/RUNNING/COMPLETED/FAILED/SKIPPED)
- PipelineStatus: Status for overall pipeline (QUEUED/RUNNING/COMPLETED/FAILED/CANCELLED)
"""

from enum import Enum


class StageStatus(Enum):
    """
    Pipeline stage status

    - PENDING: Stage not yet started
    - RUNNING: Stage currently executing
    - COMPLETED: Stage finished successfully
    - FAILED: Stage failed with error
    - SKIPPED: Stage skipped (conditional execution)
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class PipelineStatus(Enum):
    """
    Overall pipeline status

    - QUEUED: Pipeline waiting to start
    - RUNNING: Pipeline currently executing
    - COMPLETED: Pipeline finished successfully
    - FAILED: Pipeline failed
    - CANCELLED: Pipeline manually cancelled
    """
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
