#!/usr/bin/env python3
"""
WHY: Define data models for circuit breaker state and configuration
RESPONSIBILITY: Provide immutable data structures for health tracking and recovery strategy
PATTERNS: Value Object (immutable data), Strategy (recovery configuration)

Models:
- StageHealth: Track stage execution metrics and circuit state
- RecoveryStrategy: Configure retry and circuit breaker behavior
- CircuitState: Enum for circuit breaker states (CLOSED/OPEN/HALF_OPEN)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any
from enum import Enum
from artemis_constants import (
    MAX_RETRY_ATTEMPTS,
    DEFAULT_RETRY_INTERVAL_SECONDS,
    RETRY_BACKOFF_FACTOR
)


class CircuitState(Enum):
    """
    Circuit breaker states

    - CLOSED: Normal operation (requests pass through)
    - OPEN: Failures detected (blocking requests)
    - HALF_OPEN: Testing if recovery succeeded (allow one request)
    """
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class StageHealth:
    """
    Stage health tracking data

    Tracks execution metrics and circuit breaker state for a single stage.
    """
    stage_name: str
    failure_count: int
    last_failure: Optional[datetime]
    total_duration: float
    execution_count: int
    circuit_open: bool
    circuit_open_until: Optional[datetime]


@dataclass
class RecoveryStrategy:
    """
    Recovery strategy for a stage

    Defines retry behavior, backoff, timeouts, and circuit breaker thresholds.
    """
    max_retries: int = MAX_RETRY_ATTEMPTS
    retry_delay_seconds: float = DEFAULT_RETRY_INTERVAL_SECONDS
    backoff_multiplier: float = RETRY_BACKOFF_FACTOR
    timeout_seconds: float = 300.0  # 5 minutes (stage-specific)
    circuit_breaker_threshold: int = MAX_RETRY_ATTEMPTS + 2  # 5
    circuit_breaker_timeout_seconds: float = 300.0  # 5 minutes
    fallback_action: Optional[Any] = None
