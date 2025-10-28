#!/usr/bin/env python3
"""
WHY: Manage circuit breaker state for pipeline stages to prevent cascading failures
RESPONSIBILITY: Track stage health, open/close circuits, enforce failure thresholds
PATTERNS: Circuit Breaker (fault tolerance), State Machine (circuit states)

CircuitBreakerManager provides:
- Stage registration with recovery strategies
- Failure and success recording
- Automatic circuit opening on threshold breach
- Automatic circuit closing after timeout
- Health statistics and monitoring
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from artemis_stage_interface import LoggerInterface
from supervisor.circuit_breaker.models import StageHealth, RecoveryStrategy, CircuitState


class CircuitBreakerManager:
    """
    Manage circuit breaker state for pipeline stages

    Responsibilities:
    - Track stage health (failure counts, execution times)
    - Open/close circuit breakers based on failure thresholds
    - Store and retrieve recovery strategies per stage
    - Provide health status for stages

    Thread-Safety: Not thread-safe (assumes single-threaded pipeline execution)
    """

    def __init__(
        self,
        logger: Optional[LoggerInterface] = None,
        verbose: bool = True
    ):
        """
        Initialize Circuit Breaker Manager

        Args:
            logger: Logger for recording events
            verbose: Enable verbose logging
        """
        self.logger = logger
        self.verbose = verbose

        # Track stage health
        self.stage_health: Dict[str, StageHealth] = {}

        # Store recovery strategies per stage
        self.recovery_strategies: Dict[str, RecoveryStrategy] = {}

    def register_stage(
        self,
        stage_name: str,
        recovery_strategy: Optional[RecoveryStrategy] = None
    ) -> None:
        """
        Register a stage for circuit breaker management

        Args:
            stage_name: Name of the stage
            recovery_strategy: Recovery strategy (uses default if not provided)
        """
        # Guard clause - skip if already registered
        if stage_name in self.stage_health:
            return

        # Initialize health tracking
        self.stage_health[stage_name] = StageHealth(
            stage_name=stage_name,
            failure_count=0,
            last_failure=None,
            total_duration=0.0,
            execution_count=0,
            circuit_open=False,
            circuit_open_until=None
        )

        # Set recovery strategy (use default if not provided)
        self.recovery_strategies[stage_name] = (
            recovery_strategy if recovery_strategy else RecoveryStrategy()
        )

        self._log(f"Registered stage: {stage_name}")

    def check_circuit(self, stage_name: str) -> bool:
        """
        Check if circuit breaker is open for a stage

        Args:
            stage_name: Stage name

        Returns:
            True if circuit is open (stage should not execute)
        """
        # Guard clause - stage not registered
        if stage_name not in self.stage_health:
            return False

        health = self.stage_health[stage_name]

        # Guard clause - circuit not open
        if not health.circuit_open:
            return False

        # Check if circuit timeout has expired (auto-close)
        if health.circuit_open_until and datetime.now() > health.circuit_open_until:
            health.circuit_open = False
            health.circuit_open_until = None
            self._log(f"Circuit breaker auto-closed for {stage_name}")
            return False

        # Circuit still open - log remaining time
        if health.circuit_open_until:
            time_remaining = (health.circuit_open_until - datetime.now()).seconds
            self._log(f"⚠️  Circuit breaker OPEN for {stage_name} ({time_remaining}s remaining)")

        return True

    def open_circuit(self, stage_name: str) -> None:
        """
        Open circuit breaker for a stage (block future executions)

        Args:
            stage_name: Stage name
        """
        # Guard clause - stage not registered
        if stage_name not in self.stage_health:
            self._log(f"Cannot open circuit for unregistered stage: {stage_name}", level="WARNING")
            return

        health = self.stage_health[stage_name]
        strategy = self.recovery_strategies.get(stage_name, RecoveryStrategy())

        # Open circuit with timeout
        health.circuit_open = True
        health.circuit_open_until = datetime.now() + timedelta(
            seconds=strategy.circuit_breaker_timeout_seconds
        )

        self._log(
            f"🚨 Circuit breaker OPEN for {stage_name} "
            f"(timeout: {strategy.circuit_breaker_timeout_seconds}s, "
            f"failures: {health.failure_count})"
        )

    def close_circuit(self, stage_name: str) -> None:
        """
        Manually close circuit breaker for a stage

        Args:
            stage_name: Stage name
        """
        # Guard clause - stage not registered
        if stage_name not in self.stage_health:
            return

        health = self.stage_health[stage_name]
        health.circuit_open = False
        health.circuit_open_until = None

        self._log(f"Circuit breaker manually closed for {stage_name}")

    def record_failure(self, stage_name: str) -> None:
        """
        Record a stage failure and check circuit breaker threshold

        Args:
            stage_name: Stage name
        """
        # Auto-register stage if not registered
        if stage_name not in self.stage_health:
            self.register_stage(stage_name)

        health = self.stage_health[stage_name]
        strategy = self.recovery_strategies.get(stage_name, RecoveryStrategy())

        # Increment failure count and record timestamp
        health.failure_count += 1
        health.last_failure = datetime.now()

        self._log(
            f"Stage {stage_name} failed "
            f"({health.failure_count}/{strategy.circuit_breaker_threshold})"
        )

        # Open circuit if threshold exceeded
        if health.failure_count >= strategy.circuit_breaker_threshold:
            self.open_circuit(stage_name)

    def record_success(self, stage_name: str, duration: float = 0.0) -> None:
        """
        Record a successful stage execution

        Args:
            stage_name: Stage name
            duration: Execution duration in seconds
        """
        # Auto-register stage if not registered
        if stage_name not in self.stage_health:
            self.register_stage(stage_name)

        health = self.stage_health[stage_name]

        # Reset failure tracking on success
        health.failure_count = 0
        health.last_failure = None
        health.execution_count += 1
        health.total_duration += duration

        # Auto-close circuit on success (recovery)
        if health.circuit_open:
            self.close_circuit(stage_name)

    def get_stage_health(self, stage_name: str) -> Optional[StageHealth]:
        """
        Get health info for a stage

        Args:
            stage_name: Stage name

        Returns:
            StageHealth object or None if stage not registered
        """
        return self.stage_health.get(stage_name)

    def get_all_health(self) -> Dict[str, StageHealth]:
        """
        Get health info for all stages

        Returns:
            Dict mapping stage name to StageHealth
        """
        return self.stage_health.copy()

    def get_recovery_strategy(self, stage_name: str) -> Optional[RecoveryStrategy]:
        """
        Get recovery strategy for a stage

        Args:
            stage_name: Stage name

        Returns:
            RecoveryStrategy or None if not registered
        """
        return self.recovery_strategies.get(stage_name)

    def get_open_circuits(self) -> list[str]:
        """
        Get list of stages with open circuit breakers

        Returns:
            List of stage names with open circuits
        """
        return [
            name for name, health in self.stage_health.items()
            if health.circuit_open
        ]

    def reset_all(self) -> None:
        """
        Reset all circuit breakers (close all circuits)
        """
        for stage_name in self.stage_health:
            self.close_circuit(stage_name)
            self.stage_health[stage_name].failure_count = 0

        self._log("Reset all circuit breakers")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get circuit breaker statistics

        Returns:
            Dict with statistics including totals and per-stage metrics
        """
        total_stages = len(self.stage_health)
        open_circuits = len(self.get_open_circuits())
        total_failures = sum(h.failure_count for h in self.stage_health.values())
        total_executions = sum(h.execution_count for h in self.stage_health.values())

        return {
            "total_stages": total_stages,
            "open_circuits": open_circuits,
            "closed_circuits": total_stages - open_circuits,
            "total_failures": total_failures,
            "total_executions": total_executions,
            "stages": {
                name: {
                    "failure_count": health.failure_count,
                    "execution_count": health.execution_count,
                    "circuit_open": health.circuit_open,
                    "avg_duration": health.total_duration / max(health.execution_count, 1)
                }
                for name, health in self.stage_health.items()
            }
        }

    def _log(self, message: str, level: str = "INFO") -> None:
        """
        Log a message with fallback to console

        Args:
            message: Message to log
            level: Log level (INFO, WARNING, ERROR, DEBUG)
        """
        # Guard clause - use logger if available
        if self.logger:
            self.logger.log(message, level)
            return

        # Fallback to console if verbose
        if self.verbose:
            prefix = "[CircuitBreakerManager]"
            print(f"{prefix} {message}")
