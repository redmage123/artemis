#!/usr/bin/env python3
"""
Module: pipeline_observer.py

BACKWARD COMPATIBILITY WRAPPER

This module has been refactored into the observer/ package.
All classes have been extracted into focused, single-responsibility modules.

Original file: 1,140 lines
This wrapper: ~50 lines
Reduction: 95.6%

Purpose: Provides backward compatibility by re-exporting all classes from
the observer package. Existing imports will continue to work.

Migration: Update imports from:
    from pipeline_observer import EventType, PipelineEvent
To:
    from observer import EventType, PipelineEvent

Package structure:
    observer/
    ├── __init__.py                      # Package exports
    ├── event_types.py                   # EventType enum
    ├── event_model.py                   # PipelineEvent dataclass
    ├── observer_interface.py            # PipelineObserver ABC
    ├── observable.py                    # PipelineObservable (Subject)
    ├── logging_observer.py              # LoggingObserver
    ├── metrics_observer.py              # MetricsObserver
    ├── state_tracking_observer.py       # StateTrackingObserver
    ├── notification_observer.py         # NotificationObserver
    ├── supervisor_command_observer.py   # SupervisorCommandObserver
    ├── observer_factory.py              # ObserverFactory
    └── event_builder.py                 # EventBuilder

Why refactored: Original file was 1,140 lines with 11 classes.
Breaking it into focused modules improves:
    - Maintainability (single responsibility per module)
    - Testability (isolated testing per module)
    - Discoverability (clear module names)
    - Reusability (import only what you need)
"""

# Re-export everything from observer package for backward compatibility
from observer import (
    # Event types and models
    EventType,
    PipelineEvent,
    # Core observer pattern
    PipelineObserver,
    PipelineObservable,
    # Concrete observers
    LoggingObserver,
    MetricsObserver,
    StateTrackingObserver,
    NotificationObserver,
    SupervisorCommandObserver,
    # Factories and builders
    ObserverFactory,
    EventBuilder,
)

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
