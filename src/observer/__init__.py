#!/usr/bin/env python3
"""
Package: observer

WHY: Implements Observer Pattern for decoupled event-driven pipeline monitoring.
     Allows multiple components to react to pipeline events without tight coupling,
     enabling extensible monitoring, metrics, logging, and notifications.

RESPONSIBILITY:
    - Provide Observer pattern implementation for pipeline events
    - Define event types and event data structures
    - Implement concrete observers (logging, metrics, state tracking, etc.)
    - Provide factory for creating standard observer configurations
    - Support bidirectional communication via supervisor commands

PATTERNS:
    - Observer (core pattern for event notification)
    - Strategy (configurable observers)
    - Factory (observer creation)
    - Command (supervisor command routing)
    - Builder (event creation)

ARCHITECTURE:
    - PipelineObservable: Event producer (Subject in Observer pattern)
    - PipelineObserver: Event consumer interface (Observer interface)
    - Concrete observers: LoggingObserver, MetricsObserver, StateTrackingObserver, etc.
    - PipelineEvent: Immutable event data structure
    - EventType: Enum of all event types in system
    - SupervisorCommandObserver: Bidirectional command routing

EVENT FLOW:
    Pipeline Stage -> notify(event) -> PipelineObservable -> all observers
    Supervisor -> SUPERVISOR_COMMAND_* event -> SupervisorCommandObserver -> stage handler

DESIGN DECISIONS:
    - Observer pattern decouples event producers from consumers (Open/Closed)
    - Immutable events prevent observer interference
    - Error isolation prevents observer failures from breaking pipeline
    - Command observer enables supervisor to send commands back to pipeline
    - Set-based active developers for O(1) add/remove operations
"""

# Event types and models
from .event_types import EventType
from .event_model import PipelineEvent

# Core observer pattern
from .observer_interface import PipelineObserver
from .observable import PipelineObservable

# Concrete observers
from .logging_observer import LoggingObserver
from .metrics_observer import MetricsObserver
from .state_tracking_observer import StateTrackingObserver
from .notification_observer import NotificationObserver
from .supervisor_command_observer import SupervisorCommandObserver

# Factories and builders
from .observer_factory import ObserverFactory
from .event_builder import EventBuilder

__all__ = [
    # Event types and models
    "EventType",
    "PipelineEvent",
    # Core observer pattern
    "PipelineObserver",
    "PipelineObservable",
    # Concrete observers
    "LoggingObserver",
    "MetricsObserver",
    "StateTrackingObserver",
    "NotificationObserver",
    "SupervisorCommandObserver",
    # Factories and builders
    "ObserverFactory",
    "EventBuilder",
]
