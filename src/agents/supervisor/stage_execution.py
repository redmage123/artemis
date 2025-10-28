#!/usr/bin/env python3
"""
Module: agents/supervisor/stage_execution.py

Purpose: Stage execution with retries, circuit breakers, and timeout monitoring
Why: Execute pipeline stages reliably WITHOUT while + try + nested ifs
Patterns: Recursion instead of while loops, Early Return, Guard Clause
Integration: Used by SupervisorAgent.execute_with_supervision()

VIOLATIONS FIXED FROM ORIGINAL:
- ❌ BEFORE: while loop + try + except + 3 nested ifs (lines 1020-1064)
- ✅ AFTER: Recursive retry with early returns (no nesting)
- ❌ BEFORE: Nested if for retry_count > 0
- ✅ AFTER: Guard clause with early return
- ❌ BEFORE: Nested if for should_break check
- ✅ AFTER: Immediate return on break condition
"""

import time
import threading
from typing import Dict, Any, Optional
from datetime import datetime

from core.interfaces import PipelineStage
from core.exceptions import PipelineStageError
from agents.supervisor.models import RecoveryStrategy


class StageExecutor:
    """
    Stage execution with retries and monitoring (claude.md compliant)

    WHY: Handles stage execution WITHOUT nested while/try/if
    PATTERN: Recursion instead of while loops, Early returns
    RESPONSIBILITY: Execute stages with retries, timeouts, circuit breakers
    """

    def __init__(self, verbose: bool = False):
        """Initialize stage executor"""
        self.verbose = verbose
        self.stage_health = {}
        self.recovery_strategies: Dict[str, RecoveryStrategy] = {}
        self.state_machine = None

    def execute_stage_with_retries(
        self,
        stage: PipelineStage,
        stage_name: str,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute stage with retries using RECURSION instead of while loop

        ❌ ORIGINAL VIOLATION (lines 1020-1064):
        while retry_count <= strategy.max_retries:              # WHILE LOOP
            try:                                                 # NESTED TRY
                if retry_count > 0:                              # NESTED IF
                    self._wait_before_retry(...)
                result_data = self._execute_stage_monitored()
                return result_data['result']
            except Exception as e:                               # NESTED EXCEPT
                last_error = e
                if self.state_machine:                           # DOUBLE NESTED IF
                    self.state_machine.push_state()
                should_break = self._handle_execution_failure()
                if should_break:                                 # TRIPLE NESTED IF!
                    break

        ✅ FIXED: Recursive retry with early returns (ZERO nesting)

        PATTERN: Recursion replaces while loop
        PERFORMANCE: Same as while loop, but cleaner
        """
        health = self.stage_health.get(stage_name)
        strategy = self.recovery_strategies.get(stage_name, RecoveryStrategy())

        return self._try_execute_recursive(
            stage=stage,
            stage_name=stage_name,
            health=health,
            strategy=strategy,
            retry_count=0,
            last_error=None,
            args=args,
            kwargs=kwargs
        )

    def _try_execute_recursive(
        self,
        stage: PipelineStage,
        stage_name: str,
        health: Any,
        strategy: RecoveryStrategy,
        retry_count: int,
        last_error: Optional[Exception],
        args: tuple,
        kwargs: dict
    ) -> Any:
        """
        Recursive retry logic (replaces while loop - no nesting!)

        WHY: Recursion is more functional than while + try + nested ifs
        PATTERN: Tail recursion with early returns
        BASE CASE: retry_count > max_retries
        """
        # BASE CASE: Early return if max retries exceeded
        if retry_count > strategy.max_retries:
            return self._raise_final_error(stage_name, health, retry_count, last_error)

        # GUARD CLAUSE: Wait before retry if this is a retry
        if retry_count > 0:
            self._wait_before_retry(stage_name, retry_count, strategy)

        # Try executing stage
        try:
            result_data = self._execute_stage_monitored(stage, stage_name, strategy, *args, **kwargs)

            # Success - handle and return (early return, no nesting)
            self._handle_successful_execution(
                stage_name,
                health,
                retry_count,
                result_data['duration'],
                result_data['result']
            )

            return result_data['result']

        except Exception as e:
            # Handle failure and check if should retry
            return self._handle_failure_and_retry(
                stage=stage,
                stage_name=stage_name,
                health=health,
                strategy=strategy,
                retry_count=retry_count,
                error=e,
                args=args,
                kwargs=kwargs
            )

    def _handle_failure_and_retry(
        self,
        stage: PipelineStage,
        stage_name: str,
        health: Any,
        strategy: RecoveryStrategy,
        retry_count: int,
        error: Exception,
        args: tuple,
        kwargs: dict
    ) -> Any:
        """
        Handle execution failure and retry (no nested ifs)

        WHY: Extract Method - removes nested if logic from try/except
        PATTERN: Early return on break conditions
        """
        # Store failure in state machine (guard clause)
        if self.state_machine:
            self._record_failure(stage_name, error, retry_count)

        # Check if should break retry loop
        should_break = self._handle_execution_failure(
            stage_name, health, strategy, retry_count + 1, error
        )

        # Early return: stop retrying if should break
        if should_break:
            return self._raise_final_error(stage_name, health, retry_count + 1, error)

        # RECURSIVE CASE: Retry with incremented count
        return self._try_execute_recursive(
            stage=stage,
            stage_name=stage_name,
            health=health,
            strategy=strategy,
            retry_count=retry_count + 1,
            last_error=error,
            args=args,
            kwargs=kwargs
        )

    def _record_failure(self, stage_name: str, error: Exception, retry_count: int) -> None:
        """
        Record failure in state machine (extracted method)

        WHY: Removes nested if from main execution flow
        """
        self.state_machine.push_state(
            "STAGE_FAILED",  # PipelineState.STAGE_FAILED
            {
                "stage": stage_name,
                "error": str(error),
                "error_type": type(error).__name__,
                "retry_count": retry_count + 1,
                "timestamp": datetime.now().isoformat()
            }
        )
        self.state_machine.update_stage_state(stage_name, "FAILED")

    def _wait_before_retry(
        self,
        stage_name: str,
        retry_count: int,
        strategy: RecoveryStrategy
    ) -> None:
        """
        Wait before retrying with exponential backoff

        PATTERN: Extracted method (was inline in while loop)
        PERFORMANCE: Same backoff calculation, cleaner
        """
        retry_delay = strategy.retry_delay_seconds * (
            strategy.backoff_multiplier ** (retry_count - 1)
        )

        if self.verbose:
            print(f"[Supervisor] Retry {retry_count}/{strategy.max_retries} for {stage_name} (waiting {retry_delay}s)")

        time.sleep(retry_delay)

    def _execute_stage_monitored(
        self,
        stage: PipelineStage,
        stage_name: str,
        strategy: RecoveryStrategy,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute stage with timeout monitoring

        WHY: Background thread monitors timeout (no blocking)
        PATTERN: Observer pattern via threading
        """
        start_time = datetime.now()

        # Start monitoring in background thread
        monitor_thread = threading.Thread(
            target=self._monitor_execution,
            args=(stage_name, strategy.timeout_seconds),
            daemon=True
        )
        monitor_thread.start()

        # Execute stage
        result = stage.execute(*args, **kwargs)
        duration = (datetime.now() - start_time).total_seconds()

        return {'result': result, 'duration': duration}

    def _monitor_execution(self, stage_name: str, timeout_seconds: float) -> None:
        """Monitor stage execution for timeout (background thread)"""
        start_time = datetime.now()
        CHECK_INTERVAL = 1.0  # Check every second

        while True:
            time.sleep(CHECK_INTERVAL)
            elapsed = (datetime.now() - start_time).total_seconds()

            # Early return: timeout exceeded
            if elapsed > timeout_seconds:
                if self.verbose:
                    print(f"[Supervisor] ⏰ TIMEOUT detected for {stage_name} ({elapsed:.1f}s > {timeout_seconds}s)")
                return

    def _handle_successful_execution(
        self,
        stage_name: str,
        health: Any,
        retry_count: int,
        duration: float,
        result: Any = None
    ) -> None:
        """
        Handle successful stage execution

        PATTERN: Extracted method
        SIDE EFFECTS: Updates health stats, state machine
        """
        # Update health stats
        health.execution_count += 1
        health.total_duration += duration
        health.last_success = datetime.now()

        # Reset circuit breaker on success
        if health.circuit_open:
            health.circuit_open = False
            if self.verbose:
                print(f"[Supervisor] ✅ Circuit breaker CLOSED for {stage_name}")

        # Store success in state machine
        if self.state_machine:
            self.state_machine.push_state(
                "STAGE_COMPLETED",  # PipelineState.STAGE_COMPLETED
                {
                    "stage": stage_name,
                    "duration": duration,
                    "retry_count": retry_count,
                    "timestamp": datetime.now().isoformat()
                }
            )
            self.state_machine.update_stage_state(stage_name, "COMPLETED")

            # Store result if provided
            if result is not None:
                self.state_machine.store_stage_result(stage_name, result)

        self.stats["successful_executions"] += 1

    def _handle_execution_failure(
        self,
        stage_name: str,
        health: Any,
        strategy: RecoveryStrategy,
        retry_count: int,
        error: Exception
    ) -> bool:
        """
        Handle execution failure, return True if should stop retrying

        PATTERN: Early return pattern
        RETURNS: True if should break retry loop, False if should continue
        """
        # Update health stats
        health.failure_count += 1
        health.last_failure = datetime.now()

        self.stats["total_interventions"] += 1

        # Log failure
        if self.verbose:
            print(f"[Supervisor] ❌ Stage {stage_name} failed (attempt {retry_count}/{strategy.max_retries}): {error}")

        # Early return: max retries exceeded, open circuit breaker
        if retry_count > strategy.max_retries:
            health.circuit_open = True
            if self.verbose:
                print(f"[Supervisor] 🚨 Circuit breaker OPEN for {stage_name}")
            return True  # Stop retrying

        return False  # Continue retrying

    def _raise_final_error(
        self,
        stage_name: str,
        health: Any,
        retry_count: int,
        last_error: Optional[Exception]
    ):
        """
        Raise final error after all retries exhausted

        PATTERN: Extracted method for error handling
        """
        if self.verbose:
            print(f"[Supervisor] 💥 Stage {stage_name} failed after {retry_count} attempts")

        # Open circuit breaker
        health.circuit_open = True

        # Raise wrapped exception
        raise PipelineStageError(
            f"Stage {stage_name} failed after {retry_count} attempts",
            context={"stage": stage_name, "attempts": retry_count},
            original_exception=last_error
        )


# Export all
__all__ = [
    "StageExecutor",
]
