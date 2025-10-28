#!/usr/bin/env python3
"""
WHY: Define health event types and data structures
RESPONSIBILITY: Central definitions for health events, status levels, and process health
PATTERNS: Value Object (immutable event types), Data Transfer Object (ProcessHealth)
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class AgentHealthEvent(Enum):
    """
    WHY: Type-safe health event categories
    RESPONSIBILITY: Define all possible agent health state transitions
    """
    STARTED = "started"
    PROGRESS = "progress"
    STALLED = "stalled"
    CRASHED = "crashed"
    HUNG = "hung"
    COMPLETED = "completed"


class HealthStatus(Enum):
    """
    WHY: Type-safe overall system health levels
    RESPONSIBILITY: Define health severity levels for monitoring thresholds
    PATTERNS: State (health levels represent system states)
    """
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"
    CRITICAL = "critical"


@dataclass
class ProcessHealth:
    """
    WHY: Encapsulate process health metrics
    RESPONSIBILITY: Store and transfer process health information
    PATTERNS: Data Transfer Object, Value Object
    """
    pid: int
    stage_name: str
    start_time: datetime
    cpu_percent: float
    memory_mb: float
    status: str
    is_hanging: bool
    is_timeout: bool


@dataclass
class CrashInfo:
    """
    WHY: Structured crash information
    RESPONSIBILITY: Store crash details for recovery and logging
    """
    agent_name: str
    error: str
    error_type: str
    traceback: str
    state: str


@dataclass
class HealthEventData:
    """
    WHY: Structured health event data
    RESPONSIBILITY: Type-safe event data transfer
    """
    agent_name: str
    event: AgentHealthEvent
    data: Dict[str, Any]
    timestamp: datetime
