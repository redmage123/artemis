"""
Module: two_pass/pipeline/executor.py

WHY: Orchestrates two-pass execution workflow and state management.
RESPONSIBILITY: Execute passes, manage mementos, coordinate comparison and rollback.
PATTERNS: Template Method, Memento, Observer, Guard Clauses.

This module handles:
- First pass execution with retry
- Memento creation and application
- Second pass execution with learnings
- Result comparison and rollback decision
- Execution history tracking
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import copy

from two_pass.models import PassResult, PassDelta, PassMemento
from two_pass.strategies import PassStrategy
from two_pass.comparator import PassComparator
from two_pass.rollback import RollbackManager
from two_pass.events import TwoPassEventType
from two_pass.exceptions import TwoPassPipelineException
from two_pass.pipeline.retry import RetryStrategy, RetryConfig
from artemis_exceptions import wrap_exception
from artemis_services import PipelineLogger
from pipeline_observer import PipelineObservable, PipelineEvent, EventType


class TwoPassExecutor:
    """
    Orchestrates two-pass pipeline execution workflow.

    Why it exists: Encapsulates the core two-pass execution logic.
    Separates execution orchestration from AI integration and factory concerns.

    Design pattern: Template Method + Memento + Observer
    Why this design:
    - Template Method: Defines overall workflow with customization points
    - Memento: Captures first pass state for second pass learning
    - Observer: Broadcasts events at every workflow stage

    Responsibilities:
    - Execute first pass and capture state
    - Transfer learnings to second pass
    - Execute second pass with refinements
    - Compare pass results
    - Decide on rollback if needed
    - Emit events for observability
    - Manage retry on transient failures

    Workflow:
    1. Execute first pass (fast analysis)
    2. Create memento of first pass state
    3. Apply memento to second pass context
    4. Execute second pass (refined implementation)
    5. Compare results and detect delta
    6. Rollback if quality degraded
    7. Return final result

    Thread-safety: Not thread-safe (assumes single-threaded execution)
    """

    def __init__(
        self,
        first_pass_strategy: PassStrategy,
        second_pass_strategy: PassStrategy,
        comparator: PassComparator,
        rollback_manager: RollbackManager,
        retry_strategy: RetryStrategy,
        observable: Optional[PipelineObservable] = None,
        auto_rollback: bool = True,
        rollback_threshold: float = -0.1,
        verbose: bool = True
    ):
        """
        Initialize two-pass executor.

        Why needed: Sets up all execution components (strategies, comparator,
        rollback manager) and configures behavior.

        Args:
            first_pass_strategy: Strategy for first pass execution
            second_pass_strategy: Strategy for second pass execution
            comparator: Pass result comparator
            rollback_manager: Rollback coordinator
            retry_strategy: Retry policy for transient failures
            observable: Event broadcaster for observer pattern
            auto_rollback: Automatically rollback if second pass degrades quality
            rollback_threshold: Quality degradation threshold for auto-rollback (-0.1 = 10% worse)
            verbose: Enable detailed logging
        """
        self.first_pass_strategy = first_pass_strategy
        self.second_pass_strategy = second_pass_strategy
        self.comparator = comparator
        self.rollback_manager = rollback_manager
        self.retry_strategy = retry_strategy
        self.observable = observable
        self.auto_rollback = auto_rollback
        self.rollback_threshold = rollback_threshold
        self.verbose = verbose
        self.logger = PipelineLogger(verbose=verbose)

        # State tracking
        self.first_pass_memento: Optional[PassMemento] = None
        self.execution_history: List[Dict[str, Any]] = []

    @wrap_exception(TwoPassPipelineException, "Two-pass pipeline execution failed")
    def execute(self, context: Dict[str, Any]) -> PassResult:
        """
        Execute complete two-pass pipeline workflow.

        What it does:
        1. Execute first pass with retry
        2. Create and store memento
        3. Apply memento to second pass context
        4. Execute second pass with retry
        5. Compare results
        6. Auto-rollback if configured and quality degraded
        7. Return final result (second pass or rolled back first pass)

        Args:
            context: Execution context with inputs, config, etc.

        Returns:
            Final PassResult (second pass if successful, first pass if rolled back)

        Raises:
            TwoPassPipelineException: On critical failure

        Design notes:
        - Uses retry strategy for resilience
        - Emits events at every major step
        - Auto-rollback is configurable
        - Preserves execution history for audit
        """
        execution_start = datetime.now()

        # Execute first pass with retry
        first_pass_result = self._execute_first_pass_with_retry(context)

        # Create memento from first pass
        self.first_pass_memento = self._create_memento(first_pass_result, context)

        # Apply memento to second pass context
        second_pass_context = self._prepare_second_pass_context(context)

        # Execute second pass with retry
        second_pass_result = self._execute_second_pass_with_retry(second_pass_context)

        # Compare results
        delta = self.comparator.compare(first_pass_result, second_pass_result)

        # Decide final result (may rollback)
        final_result = self._determine_final_result(
            first_pass_result,
            second_pass_result,
            delta
        )

        # Record execution in history
        self._record_execution(
            first_pass_result,
            second_pass_result,
            delta,
            final_result,
            execution_start
        )

        return final_result

    def _execute_first_pass_with_retry(self, context: Dict[str, Any]) -> PassResult:
        """
        Execute first pass with retry on transient failures.

        Why extracted: Encapsulates retry logic. Avoids nesting retry loop in execute().

        Args:
            context: Execution context

        Returns:
            First pass result

        Raises:
            FirstPassException: On persistent failure
        """
        def _execute() -> PassResult:
            return self.first_pass_strategy.execute(context)

        return self.retry_strategy.retry(_execute)

    def _create_memento(self, result: PassResult, context: Dict[str, Any]) -> PassMemento:
        """
        Create memento from first pass result.

        Why extracted: Separates memento creation from execution. Emits event for tracking.

        Args:
            result: First pass result
            context: Execution context

        Returns:
            PassMemento with state snapshot
        """
        memento = self.first_pass_strategy.create_memento(result, context)

        # Emit memento created event
        if self.observable:
            event = PipelineEvent(
                event_type=EventType.STAGE_PROGRESS,
                stage_name="TwoPassPipeline",
                data={
                    "two_pass_event": TwoPassEventType.MEMENTO_CREATED.value,
                    "pass_name": result.pass_name,
                    "quality_score": result.quality_score,
                    "learnings_count": len(result.learnings)
                }
            )
            self.observable.notify(event)

        return memento

    def _prepare_second_pass_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare second pass context with first pass learnings.

        Why extracted: Encapsulates context preparation logic. Creates new context
        dict to avoid mutating original.

        Args:
            context: Original context

        Returns:
            New context with memento applied
        """
        # Guard clause - need memento to prepare context
        if not self.first_pass_memento:
            raise TwoPassPipelineException("No first pass memento available")

        # Create new context (don't mutate original)
        second_pass_context = copy.deepcopy(context)

        # Apply memento to context
        self.second_pass_strategy.apply_memento(self.first_pass_memento, second_pass_context)

        # Emit memento applied event
        if self.observable:
            event = PipelineEvent(
                event_type=EventType.STAGE_PROGRESS,
                stage_name="TwoPassPipeline",
                data={
                    "two_pass_event": TwoPassEventType.MEMENTO_APPLIED.value,
                    "learnings_applied": len(second_pass_context.get("learnings", [])),
                    "insights_applied": len(second_pass_context.get("insights", {}))
                }
            )
            self.observable.notify(event)

        return second_pass_context

    def _execute_second_pass_with_retry(self, context: Dict[str, Any]) -> PassResult:
        """
        Execute second pass with retry on transient failures.

        Why extracted: Encapsulates retry logic. Avoids nesting retry loop in execute().

        Args:
            context: Second pass context with learnings

        Returns:
            Second pass result

        Raises:
            SecondPassException: On persistent failure
        """
        def _execute() -> PassResult:
            return self.second_pass_strategy.execute(context)

        return self.retry_strategy.retry(_execute)

    def _determine_final_result(
        self,
        first_pass: PassResult,
        second_pass: PassResult,
        delta: PassDelta
    ) -> PassResult:
        """
        Determine final result (may rollback to first pass).

        Why extracted: Encapsulates rollback decision logic. Uses guard clauses
        for clarity.

        Args:
            first_pass: First pass result
            second_pass: Second pass result
            delta: Comparison delta

        Returns:
            Final result (second pass or first pass if rolled back)
        """
        # Guard clause - if auto-rollback disabled, always use second pass
        if not self.auto_rollback:
            return second_pass

        # Determine if rollback needed
        should_rollback = self.rollback_manager.should_rollback(delta, self.rollback_threshold)

        # Guard clause - if rollback not needed, use second pass
        if not should_rollback:
            return second_pass

        # Rollback to first pass
        if self.verbose:
            self.logger.log(
                f"Rolling back to first pass (quality degraded by {abs(delta.quality_delta):.2%})",
                "WARNING"
            )

        # Perform rollback
        self.rollback_manager.rollback_to_memento(
            self.first_pass_memento,
            reason=f"Quality degraded by {abs(delta.quality_delta):.2%}"
        )

        return first_pass

    def _record_execution(
        self,
        first_pass: PassResult,
        second_pass: PassResult,
        delta: PassDelta,
        final_result: PassResult,
        start_time: datetime
    ) -> None:
        """
        Record execution in history for audit trail.

        Why extracted: Separates history tracking from execution logic.

        Args:
            first_pass: First pass result
            second_pass: Second pass result
            delta: Comparison delta
            final_result: Final result (may be first or second pass)
            start_time: Execution start timestamp
        """
        execution_time = (datetime.now() - start_time).total_seconds()

        self.execution_history.append({
            "timestamp": start_time.isoformat(),
            "execution_time": execution_time,
            "first_pass_quality": first_pass.quality_score,
            "second_pass_quality": second_pass.quality_score,
            "quality_delta": delta.quality_delta,
            "final_pass": final_result.pass_name,
            "rolled_back": final_result.pass_name == first_pass.pass_name
        })

    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get execution history for audit trail"""
        return self.execution_history.copy()

    def get_rollback_history(self) -> List[Dict[str, Any]]:
        """Get rollback history from rollback manager"""
        return self.rollback_manager.get_rollback_history()


__all__ = ['TwoPassExecutor']
