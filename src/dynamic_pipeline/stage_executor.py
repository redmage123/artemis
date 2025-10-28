#!/usr/bin/env python3
"""
Module: stage_executor.py

WHY: Stage execution requires consistent error handling, retry logic, conditional
     execution, and event emission. This executor centralizes all execution concerns.

RESPONSIBILITY: Execute individual pipeline stages with full retry, skip, and event logic.

PATTERNS:
    - Chain of Responsibility: Handles execution flow with skip/retry/failure paths
    - Decorator: Wraps stage execution with cross-cutting concerns
    - Template Method: Defines execution algorithm with extension points
    - Guard Clauses: Early returns for skip and retry conditions
"""

import time
from datetime import datetime
from typing import Dict, Any, Optional

from artemis_exceptions import PipelineException, wrap_exception
from artemis_services import PipelineLogger
from pipeline_observer import PipelineObservable, PipelineEvent, EventType
from dynamic_pipeline.pipeline_stage import PipelineStage
from dynamic_pipeline.stage_result import StageResult
from dynamic_pipeline.retry_policy import RetryPolicy


class StageExecutor:
    """
    Executes pipeline stages with retry, skip, and error handling.

    Why it exists: Centralizes stage execution logic including retry policies,
    conditional execution, error handling, and event emission.

    Design pattern: Chain of Responsibility + Decorator

    Responsibilities:
    - Execute individual stages
    - Handle retries according to policy
    - Skip stages based on conditions
    - Emit events for all operations
    - Catch and wrap exceptions
    - Track execution metrics (duration, retry count)

    Execution flow:
    1. Check if should execute (conditional)
    2. Execute stage
    3. On failure, check retry policy
    4. Retry with backoff if allowed
    5. Emit events for all outcomes
    """

    def __init__(
        self,
        observable: PipelineObservable,
        retry_policy: Optional[RetryPolicy] = None,
        logger: Optional[PipelineLogger] = None
    ):
        self.observable = observable
        self.retry_policy = retry_policy or RetryPolicy()
        self.logger = logger or PipelineLogger(verbose=True)

    @wrap_exception(PipelineException, "Failed to execute stage")
    def execute_stage(
        self,
        stage: PipelineStage,
        context: Dict[str, Any],
        card_id: str
    ) -> StageResult:
        """
        Execute single stage with retry and error handling.

        Why needed: Core stage execution with full error handling, retry
        logic, and event emission. Provides consistent execution behavior.

        Args:
            stage: Stage to execute
            context: Execution context from previous stages
            card_id: Card ID for event tracking

        Returns:
            StageResult with execution outcome

        Raises:
            PipelineException: If stage fails after all retries
        """
        # Guard clause: Check if stage should execute
        if not stage.should_execute(context):
            return self._handle_skip(stage, context, card_id)

        # Execute with retry loop
        # Why loop extraction: Separates retry logic into helper method
        return self._execute_with_retry(stage, context, card_id)

    def _handle_skip(
        self,
        stage: PipelineStage,
        context: Dict[str, Any],
        card_id: str
    ) -> StageResult:
        """
        Handle stage skip (conditional execution returned False).

        Why helper method: Extracts skip handling logic, avoids nested if.
        """
        self.logger.log(f"Skipping stage: {stage.name}", "INFO")

        # Emit skip event
        self.observable.notify(PipelineEvent(
            event_type=EventType.STAGE_SKIPPED,
            card_id=card_id,
            stage_name=stage.name,
            data={"reason": "conditional_execution"}
        ))

        return StageResult(
            stage_name=stage.name,
            success=True,
            skipped=True
        )

    def _execute_with_retry(
        self,
        stage: PipelineStage,
        context: Dict[str, Any],
        card_id: str
    ) -> StageResult:
        """
        Execute stage with retry logic.

        Why helper method: Extracts retry loop from main execute method,
        avoiding nested loops and improving testability.
        """
        attempt = 0
        last_exception = None

        # Retry loop - extracted to avoid nesting in main method
        while attempt <= self.retry_policy.max_retries:
            try:
                # Attempt execution
                result = self._attempt_execution(stage, context, card_id, attempt)

                # Success - return result
                return result

            except Exception as e:
                last_exception = e

                # Check if should retry
                if not self.retry_policy.should_retry(e, attempt):
                    break

                # Handle retry with backoff
                self._handle_retry(stage, card_id, attempt, e)
                attempt += 1

        # All retries exhausted - fail
        return self._handle_failure(stage, card_id, last_exception, attempt)

    def _attempt_execution(
        self,
        stage: PipelineStage,
        context: Dict[str, Any],
        card_id: str,
        attempt: int
    ) -> StageResult:
        """
        Attempt single stage execution.

        Why helper method: Separates single execution attempt from retry
        logic, enables clean event emission and timing.
        """
        # Emit start event
        self.observable.notify(PipelineEvent(
            event_type=EventType.STAGE_STARTED,
            card_id=card_id,
            stage_name=stage.name,
            data={"attempt": attempt}
        ))

        # Execute stage and time it
        start_time = datetime.now()
        result = stage.execute(context)
        duration = (datetime.now() - start_time).total_seconds()

        # Update result with metadata
        result.duration = duration
        result.retry_count = attempt

        # Emit completion event
        self.observable.notify(PipelineEvent(
            event_type=EventType.STAGE_COMPLETED,
            card_id=card_id,
            stage_name=stage.name,
            data={
                "duration": duration,
                "retry_count": attempt,
                "result": result.data
            }
        ))

        return result

    def _handle_retry(
        self,
        stage: PipelineStage,
        card_id: str,
        attempt: int,
        error: Exception
    ) -> None:
        """
        Handle retry preparation (logging, events, backoff).

        Why helper method: Extracts retry handling logic, avoids nesting.
        """
        delay = self.retry_policy.get_delay(attempt)

        self.logger.log(
            f"Stage {stage.name} failed (attempt {attempt + 1}), "
            f"retrying in {delay:.1f}s: {error}",
            "WARNING"
        )

        # Emit retry event
        self.observable.notify(PipelineEvent(
            event_type=EventType.STAGE_RETRYING,
            card_id=card_id,
            stage_name=stage.name,
            data={
                "attempt": attempt + 1,
                "delay": delay,
                "error": str(error)
            }
        ))

        # Backoff delay
        time.sleep(delay)

    def _handle_failure(
        self,
        stage: PipelineStage,
        card_id: str,
        error: Exception,
        attempts: int
    ) -> StageResult:
        """
        Handle final stage failure after all retries.

        Why helper method: Separates failure handling, enables clean
        event emission and error wrapping.
        """
        self.logger.log(
            f"Stage {stage.name} failed after {attempts} attempts: {error}",
            "ERROR"
        )

        # Emit failure event
        self.observable.notify(PipelineEvent(
            event_type=EventType.STAGE_FAILED,
            card_id=card_id,
            stage_name=stage.name,
            error=error,
            data={"attempts": attempts}
        ))

        return StageResult(
            stage_name=stage.name,
            success=False,
            error=error,
            retry_count=attempts
        )
