#!/usr/bin/env python3
"""
WHY: Isolate heartbeat thread management complexity
RESPONSIBILITY: Manage daemon heartbeat thread lifecycle and execution
PATTERNS: Guard Clauses, Thread Management, Defensive Programming

This module manages the heartbeat thread that sends periodic liveness signals
to the supervisor. It implements robust thread lifecycle management with
clean startup, execution, and shutdown.

Design Decisions:
- Daemon threads (die with main process, no blocking on exit)
- Event-based stop signaling (clean shutdown without force)
- Defensive error handling in heartbeat loop (don't crash on transient errors)
- Timeout-based join (prevent hanging on shutdown)
- Guard clauses for early exit when supervision disabled
"""

import logging
import threading
from typing import Optional, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from supervisor_agent import SupervisorAgent


class HeartbeatManager:
    """
    Manages daemon heartbeat thread for agent liveness signaling

    Implements the daemon thread pattern with clean lifecycle management
    and defensive error handling.
    """

    def __init__(
        self,
        supervisor: Optional['SupervisorAgent'],
        agent_name: str,
        heartbeat_interval: int,
        progress_callback: Callable[[], dict],
        enabled: bool = True
    ) -> None:
        """
        Initialize heartbeat manager

        Args:
            supervisor: SupervisorAgent instance or None
            agent_name: Agent identifier for heartbeat messages
            heartbeat_interval: Seconds between heartbeats
            progress_callback: Function returning current progress data
            enabled: Enable heartbeat thread
        """
        self.supervisor = supervisor
        self.agent_name = agent_name
        self.heartbeat_interval = heartbeat_interval
        self.progress_callback = progress_callback
        self.enabled = enabled and supervisor is not None

        self._thread: Optional[threading.Thread] = None
        self._stop_event: Optional[threading.Event] = None
        self._logger = logging.getLogger(f"heartbeat.{agent_name}")

    def start(self) -> None:
        """
        Start heartbeat thread

        Process:
            1. Guard: Skip if disabled or no supervisor
            2. Stop any existing heartbeat
            3. Create stop event
            4. Create and start daemon thread
        """
        # Guard clause: skip if disabled or no supervisor
        if not self.enabled or self.supervisor is None:
            return

        # Stop existing heartbeat if any (handles restart scenarios)
        self.stop()

        # Create stop event for clean shutdown
        self._stop_event = threading.Event()

        # Create and start daemon heartbeat thread
        self._thread = threading.Thread(
            target=self._heartbeat_loop,
            daemon=True,  # Dies with main process
            name=f"{self.agent_name}-heartbeat"
        )
        self._thread.start()
        self._logger.debug(f"Started heartbeat thread for {self.agent_name}")

    def stop(self) -> None:
        """
        Stop heartbeat thread gracefully

        Process:
            1. Signal thread to stop via event
            2. Wait for thread to finish (with timeout)
            3. Clean up thread resources
        """
        # Signal thread to stop
        if self._stop_event is not None:
            self._stop_event.set()

        # Wait for thread to finish (with timeout to prevent hanging)
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=1.0)
            if self._thread.is_alive():
                self._logger.warning(
                    f"Heartbeat thread for {self.agent_name} did not stop within timeout"
                )

        # Clean up resources
        self._thread = None
        self._stop_event = None
        self._logger.debug(f"Stopped heartbeat thread for {self.agent_name}")

    def _heartbeat_loop(self) -> None:
        """
        Heartbeat thread main loop

        Sends periodic heartbeats with progress data until stop event is set.
        Implements defensive error handling to prevent thread crashes.

        Error Handling:
            - Expected errors (AttributeError, KeyError, etc.): Log as debug
            - Unexpected errors: Log as warning with traceback, but continue
        """
        while not self._stop_event.is_set():
            try:
                # Get current progress data snapshot
                progress_data = self.progress_callback()

                # Send heartbeat to supervisor
                self.supervisor.agent_heartbeat(
                    agent_name=self.agent_name,
                    progress_data=progress_data
                )
                self._logger.debug(f"Heartbeat sent for {self.agent_name}")

            except (AttributeError, KeyError, ValueError, TypeError) as e:
                # Expected errors - supervisor might be None or method unavailable
                self._logger.debug(f"Heartbeat error (expected): {e}")

            except Exception as e:
                # Unexpected errors - log warning but don't crash heartbeat thread
                self._logger.warning(
                    f"Unexpected heartbeat error for {self.agent_name}: {e}",
                    exc_info=True
                )

            # Sleep with ability to wake up on stop event
            # This allows immediate shutdown when stop() is called
            self._stop_event.wait(timeout=self.heartbeat_interval)

    def is_running(self) -> bool:
        """Check if heartbeat thread is currently running"""
        return self._thread is not None and self._thread.is_alive()

    def __repr__(self) -> str:
        status = "running" if self.is_running() else "stopped"
        enabled_status = "enabled" if self.enabled else "disabled"
        return (
            f"HeartbeatManager("
            f"agent={self.agent_name}, "
            f"interval={self.heartbeat_interval}s, "
            f"status={status}, "
            f"{enabled_status})"
        )
