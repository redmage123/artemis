#!/usr/bin/env python3
"""
Module: observer/observer_interface.py

WHY: Defines the contract for all pipeline observers, ensuring
     consistent event handling interface across the system.

RESPONSIBILITY:
    - Define event handling contract via on_event()
    - Provide observer identification via get_observer_name()
    - Establish contract that observers must implement

PATTERNS:
    - Observer interface (Gang of Four Observer pattern)
    - Abstract base class for interface definition
    - Template method pattern for default get_observer_name()

DESIGN DECISIONS:
    - Observers must handle errors internally to prevent breaking pipeline
    - Observers should be fast (avoid blocking operations)
    - Observers should not modify pipeline state directly
    - Use commands/callbacks for pipeline interaction
"""

from abc import ABC, abstractmethod

from .event_model import PipelineEvent


class PipelineObserver(ABC):
    """
    Abstract base class for pipeline observers.

    Implementation notes:
    - Observers must handle errors internally to prevent breaking pipeline
    - Observers should be fast (avoid blocking operations)
    - Observers should not modify pipeline state directly
    - Use commands/callbacks for pipeline interaction

    Thread-safety: Implementations must be thread-safe if used in
    multi-threaded context
    """

    @abstractmethod
    def on_event(self, event: PipelineEvent) -> None:
        """
        Handle pipeline event.

        Why needed: Core event handling method called by PipelineObservable
        when events occur. Subclasses implement this to react to events.

        Args:
            event: Pipeline event to handle (immutable)

        Raises:
            Should not raise exceptions - errors should be logged internally
            to prevent breaking pipeline execution

        Performance: Should return quickly to avoid blocking other observers
        """
        pass

    def get_observer_name(self) -> str:
        """
        Get observer name for logging and identification.

        Why needed: Allows PipelineObservable to log which observers are
        attached and which observer failed if errors occur.

        Returns:
            Observer class name (default implementation)
        """
        return self.__class__.__name__
