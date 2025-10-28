#!/usr/bin/env python3
"""
Module: observer/observer_factory.py

WHY: Factory for creating standard observer configurations.
     Makes it easy to set up common observer patterns without
     manually instantiating each observer.

RESPONSIBILITY:
    - Create common observer configurations
    - Provide default, minimal, and full observer sets
    - Simplify observer setup for different use cases

PATTERNS:
    - Factory pattern for object creation
    - Static methods for stateless factory
    - Configuration pattern for different setups

DESIGN DECISIONS:
    - Static methods (no state needed)
    - Three standard configurations: default, minimal, full
    - Default includes logging, metrics, and state tracking
    - Minimal includes only logging
    - Full includes all observers including notifications
"""

from typing import List

from .observer_interface import PipelineObserver
from .logging_observer import LoggingObserver
from .metrics_observer import MetricsObserver
from .state_tracking_observer import StateTrackingObserver
from .notification_observer import NotificationObserver


class ObserverFactory:
    """
    Factory for creating standard observers.

    Makes it easy to set up common observer configurations.
    """

    @staticmethod
    def create_default_observers(verbose: bool = True) -> List[PipelineObserver]:
        """
        Create default set of observers

        Returns:
            List of: LoggingObserver, MetricsObserver, StateTrackingObserver
        """
        return [
            LoggingObserver(verbose=verbose),
            MetricsObserver(),
            StateTrackingObserver()
        ]

    @staticmethod
    def create_minimal_observers() -> List[PipelineObserver]:
        """
        Create minimal set of observers (just logging)

        Returns:
            List with only LoggingObserver
        """
        return [LoggingObserver(verbose=True)]

    @staticmethod
    def create_full_observers(verbose: bool = True) -> List[PipelineObserver]:
        """
        Create full set of observers including notifications

        Returns:
            List of all observer types
        """
        return [
            LoggingObserver(verbose=verbose),
            MetricsObserver(),
            StateTrackingObserver(),
            NotificationObserver(verbose=verbose)
        ]
