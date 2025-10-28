#!/usr/bin/env python3
"""
Module: observer/observable.py

WHY: Central event broadcasting hub that manages observer
     registration and notification. Decouples event producers (pipeline stages)
     from event consumers (observers).

RESPONSIBILITY:
    - Maintain list of registered observers
    - Broadcast events to all observers
    - Isolate observer errors from pipeline execution
    - Log observer attachment/detachment
    - Provide observer count for debugging

PATTERNS:
    - Observable/Subject (Gang of Four Observer pattern)
    - Error isolation pattern to prevent cascade failures
    - List-based observer registry for ordered notification

DESIGN DECISIONS:
    - Observer exceptions are caught and logged to prevent cascade failures
    - Not thread-safe (assumes single-threaded pipeline)
    - Verbose logging for debugging observer interactions
"""

from typing import List

from artemis_services import PipelineLogger

from .observer_interface import PipelineObserver
from .event_model import PipelineEvent


class PipelineObservable:
    """
    Observable pipeline subject (Subject in Observer pattern).

    Error handling: Observer exceptions are caught and logged to prevent
    one failing observer from breaking the entire notification chain.

    Thread-safety: Not thread-safe (assumes single-threaded pipeline)
    """

    def __init__(self, verbose: bool = True):
        self._observers: List[PipelineObserver] = []
        self.verbose = verbose
        self.logger = PipelineLogger(verbose=verbose)

    def attach(self, observer: PipelineObserver) -> None:
        """
        Attach observer to receive events

        Args:
            observer: Observer to attach
        """
        if observer not in self._observers:
            self._observers.append(observer)
            if self.verbose:
                self.logger.log(f"Attached observer: {observer.get_observer_name()}", "INFO")

    def detach(self, observer: PipelineObserver) -> None:
        """
        Detach observer from receiving events

        Args:
            observer: Observer to detach
        """
        if observer in self._observers:
            self._observers.remove(observer)
            if self.verbose:
                self.logger.log(f"Detached observer: {observer.get_observer_name()}", "INFO")

    def notify(self, event: PipelineEvent) -> None:
        """
        Notify all observers of event.

        Why needed: Core event broadcasting method. Ensures all registered
        observers receive events while isolating errors.

        Args:
            event: Event to broadcast (immutable)

        Error handling: Catches exceptions from observers to prevent cascade
        failures. Failed observers are logged but don't stop notification
        of other observers.

        Performance: O(n) where n is number of observers. Observers should
        return quickly to avoid blocking pipeline.
        """
        if self.verbose:
            self.logger.log(
                f"Broadcasting event: {event.event_type.value} "
                f"(card_id={event.card_id}, stage={event.stage_name})",
                "DEBUG"
            )

        for observer in self._observers:
            try:
                observer.on_event(event)
            except Exception as e:
                # Don't let observer errors break the pipeline
                self.logger.log(
                    f"Observer {observer.get_observer_name()} failed to handle event: {e}",
                    "ERROR"
                )

    def get_observer_count(self) -> int:
        """Get number of attached observers"""
        return len(self._observers)
