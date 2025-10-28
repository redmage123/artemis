#!/usr/bin/env python3
"""
WHY: Provide reusable supervised agent functionality via composition
RESPONSIBILITY: Coordinate registration, heartbeat, and progress tracking
PATTERNS: Mixin Pattern, Composition, Template Method, Context Manager

This module implements the core SupervisedAgentMixin using composition of
specialized managers. It provides the supervised_execution() context manager
that orchestrates the entire supervision lifecycle.

Design Decisions:
- Composition over inheritance for manager dependencies
- Context manager for automatic lifecycle management
- Guard clauses for validation (max 1 level nesting)
- Template method pattern in supervised_execution()
- Clean separation of concerns via delegation
"""

import logging
from typing import Optional, Dict, Any, TYPE_CHECKING
from contextlib import contextmanager

from .progress_tracker import ProgressTracker
from .registration_manager import RegistrationManager
from .heartbeat_manager import HeartbeatManager

if TYPE_CHECKING:
    from supervisor_agent import SupervisorAgent


class SupervisedAgentMixin:
    """
    Mixin class providing supervisor integration for agents

    Implements the Hybrid Strategy:
    - Daemon heartbeat thread (non-blocking background monitoring)
    - Automatic registration/unregistration
    - Context manager for clean execution

    Design Pattern: Mixin + Composition
    - Mixin: Can be added to any agent class
    - Composition: Uses manager objects for specific responsibilities
    """

    def __init__(
        self,
        supervisor: Optional['SupervisorAgent'],
        agent_name: str,
        agent_type: str = "agent",
        heartbeat_interval: int = 15,
        enable_heartbeat: bool = True
    ) -> None:
        """
        Initialize supervised agent

        Args:
            supervisor: SupervisorAgent instance (None = no supervision)
            agent_name: Unique name for this agent
            agent_type: Type of agent (e.g., "stage", "worker", "analyzer")
            heartbeat_interval: Seconds between heartbeats (default 15)
            enable_heartbeat: Enable heartbeat thread (default True)

        Raises:
            ValueError: If agent_name is empty or heartbeat_interval <= 0
        """
        # Validate inputs with guard clauses
        if not agent_name:
            raise ValueError("agent_name cannot be empty")
        if heartbeat_interval <= 0:
            raise ValueError(
                f"heartbeat_interval must be > 0, got {heartbeat_interval}"
            )

        # Store configuration
        self.supervisor = supervisor
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.heartbeat_interval = heartbeat_interval
        self.enable_heartbeat = enable_heartbeat and supervisor is not None

        # Initialize composed managers
        self._progress_tracker = ProgressTracker()

        self._registration_manager = RegistrationManager(
            supervisor=supervisor,
            agent_name=agent_name,
            agent_type=agent_type
        )

        self._heartbeat_manager = HeartbeatManager(
            supervisor=supervisor,
            agent_name=agent_name,
            heartbeat_interval=heartbeat_interval,
            progress_callback=self._progress_tracker.get_snapshot,
            enabled=self.enable_heartbeat
        )

        self._logger = logging.getLogger(f"supervised_agent.{agent_name}")

    def update_progress(self, progress_data: Dict[str, Any]) -> None:
        """
        Update progress data incrementally (sent with next heartbeat)

        Args:
            progress_data: Progress information
                          (e.g., {"step": "analyzing", "percent": 50})

        Example:
            self.update_progress({"step": "parsing"})
            self.update_progress({"percent": 25})
            # Result: {"step": "parsing", "percent": 25}
        """
        self._progress_tracker.update(progress_data)

    def set_progress(self, progress_data: Dict[str, Any]) -> None:
        """
        Replace all progress data

        Args:
            progress_data: Complete new progress state

        Example:
            self.set_progress({"step": "analyzing", "total": 100})
            # Previous progress data is completely replaced
        """
        self._progress_tracker.set(progress_data)

    @contextmanager
    def supervised_execution(self, metadata: Optional[Dict[str, Any]] = None):
        """
        Context manager for supervised execution (Template Method Pattern)

        Orchestrates the complete supervision lifecycle:
        1. Register with supervisor
        2. Start heartbeat thread
        3. Yield control to work block
        4. Cleanup (stop heartbeat, unregister)

        Args:
            metadata: Optional metadata for registration

        Usage:
            with self.supervised_execution(metadata={"task_id": "123"}):
                # Do work - registration and heartbeat are automatic
                result = expensive_operation()
                return result

        Guarantees:
            - Cleanup always runs (even on exception)
            - Heartbeat stops before unregistration
            - Resources are properly released
        """
        try:
            # Step 1: Register with supervisor
            self._registration_manager.register(metadata)

            # Step 2: Start heartbeat thread
            self._heartbeat_manager.start()

            # Step 3: Yield control to the work block
            yield

        finally:
            # Step 4: Always cleanup (even if exception occurs)
            # Order matters: stop heartbeat before unregistering
            self._heartbeat_manager.stop()
            self._registration_manager.unregister()

    def _register_with_supervisor(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Legacy method for backward compatibility - delegates to manager"""
        self._registration_manager.register(metadata)

    def _unregister_from_supervisor(self) -> None:
        """Legacy method for backward compatibility - delegates to manager"""
        self._registration_manager.unregister()

    def _start_heartbeat_thread(self) -> None:
        """Legacy method for backward compatibility - delegates to manager"""
        self._heartbeat_manager.start()

    def _stop_heartbeat_thread(self) -> None:
        """Legacy method for backward compatibility - delegates to manager"""
        self._heartbeat_manager.stop()

    def __repr__(self) -> str:
        supervisor_status = "supervised" if self.supervisor else "unsupervised"
        heartbeat_status = "enabled" if self.enable_heartbeat else "disabled"
        return (
            f"SupervisedAgentMixin("
            f"name={self.agent_name}, "
            f"type={self.agent_type}, "
            f"{supervisor_status}, "
            f"heartbeat={heartbeat_status})"
        )
