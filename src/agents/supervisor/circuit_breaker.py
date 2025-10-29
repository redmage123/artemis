"""
Module: agents/supervisor/circuit_breaker.py

WHY: Prevent cascading failures by temporarily disabling failing stages.
RESPONSIBILITY: Manage circuit breaker state for pipeline stages.
PATTERNS: Circuit Breaker Pattern, Guard Clauses (early returns).

This module handles:
- Stage registration with recovery strategies
- Circuit breaker state tracking (open/closed)
- Automatic circuit closing after timeout
- Alerting via AgentMessenger

Circuit Breaker Pattern:
- CLOSED (normal): Stage executes normally
- OPEN (failure): Stage temporarily disabled after repeated failures
- HALF-OPEN (recovery): Automatically closes after timeout expires

EXTRACTED FROM: supervisor_agent.py (lines 572-668)
"""

from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from agents.supervisor.models import RecoveryStrategy


@dataclass
class CircuitBreakerState:
    """
    Circuit breaker state for a stage (mutable)

    WHY: Track circuit breaker status separate from stage execution health
    PATTERNS: State Pattern - mutable state for circuit breaker transitions
    """
    stage_name: str
    failure_count: int = 0
    last_failure: Optional[datetime] = None
    total_duration: float = 0.0
    execution_count: int = 0
    circuit_open: bool = False
    circuit_open_until: Optional[datetime] = None


class CircuitBreakerManager:
    """
    Manages circuit breaker state for pipeline stages

    WHY: Prevent cascading failures from repeatedly failing stages
    PATTERNS: Circuit Breaker Pattern, Guard Clauses
    """

    def __init__(
        self,
        verbose: bool = False,
        messenger: Optional[Any] = None,
        state_machine: Optional[Any] = None,
        logger: Optional[Any] = None
    ):
        """
        Initialize circuit breaker manager

        Args:
            verbose: Enable verbose logging
            messenger: Optional messenger for alerts
            state_machine: Optional state machine for logging
            logger: Optional logger for recording events
        """
        self.verbose = verbose
        self.messenger = messenger
        self.state_machine = state_machine
        self.logger = logger
        self.stage_health: Dict[str, CircuitBreakerState] = {}
        self.recovery_strategies: Dict[str, RecoveryStrategy] = {}

    def register_stage(
        self,
        stage_name: str,
        recovery_strategy: Optional[RecoveryStrategy] = None
    ) -> None:
        """
        Register a stage for supervision with circuit breaker

        Args:
            stage_name: Name of the stage
            recovery_strategy: Recovery strategy (uses default if not provided)
        """
        # Guard: stage already registered
        if stage_name in self.stage_health:
            return

        # Create initial health status
        self.stage_health[stage_name] = CircuitBreakerState(
            stage_name=stage_name,
            failure_count=0,
            last_failure=None,
            total_duration=0.0,
            execution_count=0,
            circuit_open=False,
            circuit_open_until=None
        )

        # Set recovery strategy
        if recovery_strategy:
            self.recovery_strategies[stage_name] = recovery_strategy
        else:
            self.recovery_strategies[stage_name] = RecoveryStrategy()

        # Register with state machine
        if self.state_machine:
            from artemis_state_machine import StageState
            self.state_machine.update_stage_state(
                stage_name,
                StageState.PENDING
            )

        if self.verbose and self.logger:
            self.logger.log(f"[CircuitBreaker] Registered stage: {stage_name}", "INFO")

    def check_circuit_breaker(self, stage_name: str) -> bool:
        """
        Check if circuit breaker is open for a stage

        Args:
            stage_name: Stage name

        Returns:
            True if circuit is open (stage should not execute)
        """
        # Guard: stage not registered
        if stage_name not in self.stage_health:
            return False

        health = self.stage_health[stage_name]

        # Guard: circuit is closed
        if not health.circuit_open:
            return False

        # Check if circuit should automatically close
        should_close = self._should_auto_close_circuit(health)
        if should_close:
            self._close_circuit(stage_name, health)
            return False

        # Circuit is still open
        if self.verbose and self.logger:
            time_remaining = self._calculate_time_remaining(health)
            self.logger.log(f"[CircuitBreaker] ⚠️  Circuit OPEN for {stage_name} ({time_remaining}s remaining)", "WARNING")

        return True

    def open_circuit_breaker(self, stage_name: str) -> None:
        """
        Open circuit breaker for a stage (disable it temporarily)

        Args:
            stage_name: Stage name
        """
        # Guard: stage not registered
        if stage_name not in self.stage_health:
            return

        health = self.stage_health[stage_name]
        strategy = self.recovery_strategies.get(stage_name, RecoveryStrategy())

        # Open the circuit with timeout
        health.circuit_open = True
        health.circuit_open_until = datetime.now() + timedelta(
            seconds=strategy.timeout_seconds
        )

        # Send alert
        if self.messenger:
            self.messenger.send_message(
                f"🚨 CIRCUIT BREAKER OPEN: {stage_name}",
                f"Stage has failed {health.failure_count} times. Temporarily disabled for "
                f"{strategy.timeout_seconds}s"
            )

        if self.verbose and self.logger:
            self.logger.log(f"[CircuitBreaker] 🚨 Circuit OPEN for {stage_name} (timeout: {strategy.timeout_seconds}s)", "ERROR")

    def _should_auto_close_circuit(self, health: CircuitBreakerState) -> bool:
        """
        Check if circuit should automatically close (timeout expired)

        Args:
            health: Circuit breaker state

        Returns:
            True if circuit should close
        """
        # Guard: no timeout set
        if not health.circuit_open_until:
            return False

        return datetime.now() > health.circuit_open_until

    def _close_circuit(self, stage_name: str, health: CircuitBreakerState) -> None:
        """
        Close the circuit breaker (enable stage again)

        Args:
            stage_name: Stage name
            health: Stage health status
        """
        health.circuit_open = False
        health.circuit_open_until = None

        if self.verbose and self.logger:
            self.logger.log(f"[CircuitBreaker] Circuit closed for {stage_name}", "INFO")

    def _calculate_time_remaining(self, health: CircuitBreakerState) -> int:
        """
        Calculate time remaining until circuit auto-closes

        Args:
            health: Circuit breaker state

        Returns:
            Seconds remaining (0 if no timeout set)
        """
        # Guard: no timeout set
        if not health.circuit_open_until:
            return 0

        time_delta = health.circuit_open_until - datetime.now()
        return max(0, time_delta.seconds)

    def get_stage_health(self, stage_name: str) -> Optional[CircuitBreakerState]:
        """
        Get health status for a stage

        Args:
            stage_name: Stage name

        Returns:
            StageHealth or None if not registered
        """
        return self.stage_health.get(stage_name)

    def get_all_stage_health(self) -> Dict[str, CircuitBreakerState]:
        """
        Get health status for all registered stages

        Returns:
            Dict mapping stage_name to StageHealth
        """
        return self.stage_health.copy()


__all__ = [
    "CircuitBreakerManager"
]
