#!/usr/bin/env python3
"""
WHY: Autonomous background monitoring via watchdog thread
RESPONSIBILITY: Run continuous health checks in daemon thread
PATTERNS: Watchdog (background monitoring), Strategy (check strategies)
"""

import threading
import time
from typing import Any, Callable, Optional

from .crash_detector import CrashDetector
from .event_observer import EventObserver
from .event_types import AgentHealthEvent
from .progress_tracker import ProgressTracker


class Watchdog:
    """
    WHY: Provide continuous background monitoring without manual checks
    RESPONSIBILITY: Run daemon thread, perform periodic health checks, notify observers
    PATTERNS: Watchdog, Strategy (check strategies), Observer (notifications)
    """

    def __init__(
        self,
        crash_detector: CrashDetector,
        progress_tracker: ProgressTracker,
        event_observer: EventObserver,
        logger: Optional[Callable[[str, str], None]] = None
    ):
        """
        WHY: Initialize watchdog with monitoring strategies
        RESPONSIBILITY: Setup monitoring components and thread state
        PATTERNS: Dependency injection (strategies)

        Args:
            crash_detector: Crash detection strategy
            progress_tracker: Progress tracking strategy
            event_observer: Observer notification strategy
            logger: Optional logging function
        """
        self.crash_detector = crash_detector
        self.progress_tracker = progress_tracker
        self.event_observer = event_observer
        self._log = logger

        self.watchdog_thread: Optional[threading.Thread] = None
        self._watchdog_running = False

    def start(
        self,
        check_interval: int = 5,
        timeout_seconds: int = 300
    ) -> threading.Thread:
        """
        WHY: Start autonomous monitoring
        RESPONSIBILITY: Launch daemon thread for continuous health checks
        PATTERNS: Guard clause (already running check)

        Args:
            check_interval: Seconds between checks (lower = more responsive)
            timeout_seconds: Max time before considering hung

        Returns:
            Watchdog thread (already started as daemon)
        """
        if self._watchdog_running:
            if self._log:
                self._log("Watchdog already running", "WARNING")
            return self.watchdog_thread

        def watchdog_loop():
            """Watchdog monitoring loop"""
            if self._log:
                self._log(
                    f"🐕 Watchdog started (check_interval={check_interval}s, timeout={timeout_seconds}s)",
                    "INFO"
                )

            self._watchdog_running = True

            while self._watchdog_running:
                try:
                    time.sleep(check_interval)
                    self._perform_health_checks(timeout_seconds)

                except Exception as e:
                    if self._log:
                        self._log(f"⚠️  Watchdog error: {e}", "WARNING")

            if self._log:
                self._log("🐕 Watchdog stopped", "INFO")

        # Start watchdog in daemon thread
        self.watchdog_thread = threading.Thread(target=watchdog_loop, daemon=True)
        self.watchdog_thread.start()

        return self.watchdog_thread

    def stop(self) -> None:
        """
        WHY: Gracefully stop watchdog
        RESPONSIBILITY: Set stop flag and wait for thread to exit
        PATTERNS: Guard clause
        """
        self._watchdog_running = False

        if self.watchdog_thread:
            self.watchdog_thread.join(timeout=5.0)

        if self._log:
            self._log("Watchdog stopped", "INFO")

    def is_running(self) -> bool:
        """
        WHY: Check watchdog status
        RESPONSIBILITY: Return running state
        """
        return self._watchdog_running

    def _perform_health_checks(self, timeout_seconds: int) -> None:
        """
        WHY: Execute all health check strategies
        RESPONSIBILITY: Check for crashes, hangs, and stalls
        PATTERNS: Guard clause (state machine check)

        Args:
            timeout_seconds: Timeout threshold for hung detection
        """
        if not self.crash_detector.state_machine:
            return

        self._check_for_crash()
        self._check_for_hang_or_stall(timeout_seconds)

    def _check_for_crash(self) -> None:
        """
        WHY: Detect crashed agents
        RESPONSIBILITY: Query crash detector and notify observers
        PATTERNS: Guard clause
        """
        crash_info = self.crash_detector.check_for_crash_event()

        if not crash_info:
            return

        # Notify observers
        self.event_observer.notify_event(
            crash_info["agent_name"],
            AgentHealthEvent.CRASHED,
            {"crash_info": crash_info, "context": crash_info.get("context", {})}
        )

    def _check_for_hang_or_stall(self, timeout_seconds: int) -> None:
        """
        WHY: Detect hung or stalled agents
        RESPONSIBILITY: Query progress tracker and notify observers
        PATTERNS: Guard clause, Dispatch table (event type mapping)

        Args:
            timeout_seconds: Timeout threshold for hung detection
        """
        result = self.progress_tracker.check_hang_or_stall(timeout_seconds)

        if not result:
            return

        # Dispatch table: event type -> AgentHealthEvent
        event_dispatch = {
            "hung": AgentHealthEvent.HUNG,
            "stalled": AgentHealthEvent.STALLED
        }

        event_type = event_dispatch.get(result["event"])

        if not event_type:
            return

        # Notify observers
        self.event_observer.notify_event(
            result["stage_name"],
            event_type,
            result["data"]
        )
