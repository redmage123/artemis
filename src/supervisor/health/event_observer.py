#!/usr/bin/env python3
"""
WHY: Manage health event observers and notifications
RESPONSIBILITY: Register observers, notify them of health events
PATTERNS: Observer (event notification), Thread-safe (with locks)
"""

import threading
from typing import Any, Callable, Dict, List, Optional

from .event_types import AgentHealthEvent


class EventObserver:
    """
    WHY: Decouple health monitoring from event handling
    RESPONSIBILITY: Manage observer registration and event notification
    PATTERNS: Observer, Thread-safe
    """

    def __init__(self, logger: Optional[Callable[[str, str], None]] = None):
        """
        WHY: Initialize observer manager
        RESPONSIBILITY: Setup observer storage and synchronization
        PATTERNS: Dependency injection (logger)

        Args:
            logger: Optional logging function
        """
        self.health_observers: List[Any] = []
        self._observers_lock = threading.Lock()
        self._log = logger

    def register_observer(self, observer: Any) -> None:
        """
        WHY: Add observer to notification list
        RESPONSIBILITY: Register observer if not already registered
        PATTERNS: Guard clause (duplicate check), Thread-safe

        Args:
            observer: Observer object with on_agent_event() method
        """
        with self._observers_lock:
            if observer in self.health_observers:
                return

            self.health_observers.append(observer)

            if self._log:
                self._log(f"Registered health observer: {type(observer).__name__}", "INFO")

    def unregister_observer(self, observer: Any) -> None:
        """
        WHY: Remove observer from notification list
        RESPONSIBILITY: Unregister observer
        PATTERNS: Guard clause, Thread-safe

        Args:
            observer: Observer to remove
        """
        with self._observers_lock:
            if observer not in self.health_observers:
                return

            self.health_observers.remove(observer)

            if self._log:
                self._log(f"Unregistered health observer: {type(observer).__name__}", "INFO")

    def notify_event(
        self,
        agent_name: str,
        event: AgentHealthEvent,
        data: Dict[str, Any]
    ) -> None:
        """
        WHY: Broadcast health events to all observers
        RESPONSIBILITY: Call on_agent_event() on each observer
        PATTERNS: Observer (notification), Guard clause (exception handling)

        Args:
            agent_name: Name of the agent
            event: Health event type
            data: Event data
        """
        with self._observers_lock:
            for observer in self.health_observers:
                self._notify_single_observer(observer, agent_name, event, data)

    def _notify_single_observer(
        self,
        observer: Any,
        agent_name: str,
        event: AgentHealthEvent,
        data: Dict[str, Any]
    ) -> None:
        """
        WHY: Notify individual observer with error handling
        RESPONSIBILITY: Call observer method safely
        PATTERNS: Guard clause (exception handling)

        Args:
            observer: Observer to notify
            agent_name: Name of the agent
            event: Health event type
            data: Event data
        """
        try:
            if not hasattr(observer, 'on_agent_event'):
                return

            observer.on_agent_event(agent_name, event, data)

        except Exception as e:
            if self._log:
                self._log(f"Error notifying observer: {e}", "WARNING")

    def get_observer_count(self) -> int:
        """
        WHY: Report number of registered observers
        RESPONSIBILITY: Thread-safe count
        """
        with self._observers_lock:
            return len(self.health_observers)
