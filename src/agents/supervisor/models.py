#!/usr/bin/env python3
"""
Module: agents/supervisor/models.py

Purpose: Data models for supervisor health monitoring
Why: Encapsulates health status, events, and recovery strategies as immutable data
Patterns: Value Object Pattern, Enum Pattern, Data Class Pattern
Integration: Used by all supervisor modules for type-safe health tracking

WHAT: Defines enums and dataclasses for supervisor health monitoring
WHY: Type-safe, immutable data structures prevent state corruption
RESPONSIBILITY: Define health status, events, and recovery data structures
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


class AgentHealthEvent(Enum):
    """
    Agent health event types for observer notifications

    WHY: Type-safe event classification for observer pattern
    USAGE: Passed to AgentHealthObserver.on_agent_event()
    """
    STARTED = "started"
    CRASHED = "crashed"
    HUNG = "hung"
    STALLED = "stalled"
    RECOVERED = "recovered"
    TERMINATED = "terminated"


class HealthStatus(Enum):
    """
    Overall health status of supervised pipeline

    WHY: Single enum for system-wide health state
    USAGE: Returned by SupervisorAgent.get_health_status()
    """
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    FAILED = "failed"


class RecoveryAction(Enum):
    """
    Recovery actions for failed stages

    WHY: Type-safe recovery strategy selection
    USAGE: Determines retry vs restart vs skip
    """
    RETRY = "retry"
    RESTART = "restart"
    SKIP = "skip"
    ABORT = "abort"
    FALLBACK = "fallback"


@dataclass(frozen=True)
class ProcessHealth:
    """
    Process health snapshot (immutable)

    WHY: Immutable snapshot prevents race conditions in multi-threaded monitoring
    PATTERN: Value Object (frozen=True makes it immutable)
    USAGE: detect_hanging_processes() returns List[ProcessHealth]
    """
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    status: str
    create_time: float
    is_hanging: bool
    reason: Optional[str] = None


@dataclass(frozen=True)
class StageHealth:
    """
    Stage execution health snapshot (immutable)

    WHY: Captures complete stage execution state for recovery decisions
    PATTERN: Value Object
    USAGE: Passed to recovery engine for failure analysis
    """
    stage_name: str
    status: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: float
    retry_count: int
    error: Optional[Exception]
    success: bool


@dataclass
class RecoveryStrategy:
    """
    Recovery strategy configuration (mutable for dynamic adjustment)

    WHY: Mutable strategy allows learning engine to update recovery params
    PATTERN: Strategy Pattern
    USAGE: SupervisorAgent maintains per-stage recovery strategies
    """
    action: RecoveryAction
    max_retries: int
    retry_delay_seconds: float
    backoff_factor: float
    timeout_seconds: float
    fallback_value: Optional[Any] = None


# Export all models
__all__ = [
    "AgentHealthEvent",
    "HealthStatus",
    "RecoveryAction",
    "ProcessHealth",
    "StageHealth",
    "RecoveryStrategy",
]
