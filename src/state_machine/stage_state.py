#!/usr/bin/env python3
"""
WHY: Define all possible states for individual pipeline stages
RESPONSIBILITY: Provide stage-level state tracking separate from pipeline-level
PATTERNS: State pattern, granular state management
"""

from enum import Enum


class StageState(Enum):
    """Individual stage states"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    SKIPPED = "skipped"
    CIRCUIT_OPEN = "circuit_open"
    TIMED_OUT = "timed_out"
    ROLLED_BACK = "rolled_back"
