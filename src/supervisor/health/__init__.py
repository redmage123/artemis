#!/usr/bin/env python3
"""
WHY: Health monitoring package for supervisor
RESPONSIBILITY: Provide unified health monitoring interface
PATTERNS: Facade (package-level exports)

Package Structure:
- event_types: Health event types and data structures
- agent_registry: Agent registration and heartbeat tracking
- process_monitor: Process resource monitoring
- crash_detector: Crash detection via state machine
- progress_tracker: State transition tracking
- health_calculator: Overall health status calculation
- event_observer: Observer pattern implementation
- watchdog: Autonomous background monitoring
- health_monitor: Main facade orchestrator
"""

from .agent_registry import AgentRegistry
from .crash_detector import CrashDetector
from .event_observer import EventObserver
from .event_types import (
    AgentHealthEvent,
    CrashInfo,
    HealthEventData,
    HealthStatus,
    ProcessHealth,
)
from .health_calculator import HealthCalculator
from .health_monitor import HealthMonitor
from .process_monitor import ProcessMonitor
from .progress_tracker import ProgressTracker
from .watchdog import Watchdog

__all__ = [
    # Main interface
    "HealthMonitor",
    # Event types
    "AgentHealthEvent",
    "HealthStatus",
    "ProcessHealth",
    "CrashInfo",
    "HealthEventData",
    # Components
    "AgentRegistry",
    "ProcessMonitor",
    "CrashDetector",
    "ProgressTracker",
    "HealthCalculator",
    "EventObserver",
    "Watchdog",
]
