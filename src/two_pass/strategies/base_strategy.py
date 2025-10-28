"""
Module: two_pass/strategies/base_strategy.py

WHY: Defines abstract base class for all pass execution strategies in two-pass pipeline.
RESPONSIBILITY: Provides contract and common functionality for pass strategies (first pass, second pass, custom passes).
PATTERNS: Strategy Pattern, Template Method Pattern, Observer Pattern, Guard Clauses.

This module handles:
- PassStrategy ABC: Abstract base class defining strategy contract
- Template methods for memento creation and application
- Event emission for observer pattern integration
- Common functionality shared across all pass strategies

EXTRACTED FROM: two_pass/strategies.py (lines 28-192, 165 lines)
REDUCES: Monolithic strategies.py by separating base abstraction from concrete implementations
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

from two_pass.models import PassResult, PassMemento
from two_pass.events import TwoPassEventType
from artemis_services import PipelineLogger
from pipeline_observer import PipelineObservable, PipelineEvent, EventType


class PassStrategy(ABC):
    """
    Abstract strategy for pipeline pass execution (Strategy Pattern).

    WHY: Defines contract for all pass strategies (first pass, second pass,
    custom passes). Enables swapping pass implementations without changing orchestrator.

    RESPONSIBILITY: Define pass execution contract and provide common template methods.

    PATTERNS: Strategy Pattern + Template Method Pattern
    - Strategy pattern: Allows different pass implementations (fast vs thorough)
    - Template Method: Provides common structure with customization points
    - Observer pattern: Event emission for monitoring and tracking

    Template Method structure:
    1. execute() - implemented by subclass (the strategy)
    2. create_memento() - default implementation with override option
    3. apply_memento() - default implementation with override option

    Thread-safety: Not thread-safe (assumes single-threaded execution)
    """

    def __init__(self, observable: Optional[PipelineObservable] = None, verbose: bool = True):
        """
        Initialize pass strategy.

        WHY: Sets up observer integration for event broadcasting and
        logging infrastructure.

        Args:
            observable: Event broadcaster for observer pattern integration
            verbose: Enable detailed logging
        """
        self.observable = observable
        self.verbose = verbose
        self.logger = PipelineLogger(verbose=verbose)

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> PassResult:
        """
        Execute pass with given context (abstract method - must override).

        WHY: Core strategy method that subclasses implement with
        pass-specific logic (fast analysis vs thorough execution).

        Args:
            context: Execution context with configuration, inputs, and prior state

        Returns:
            PassResult with artifacts, learnings, and quality metrics

        Raises:
            PassStrategy subclass exceptions on execution failure

        Design note: Takes Dict instead of typed config for flexibility across
        different pass types with different context requirements.
        """
        pass

    @abstractmethod
    def get_pass_name(self) -> str:
        """
        Get name of this pass strategy.

        WHY: Used for logging, events, and memento identification.
        Each strategy returns unique name (e.g., "FirstPass", "SecondPass").

        Returns:
            Human-readable pass name
        """
        pass

    def create_memento(self, result: PassResult, state: Dict[str, Any]) -> PassMemento:
        """
        Create memento from pass result and state (Template Method - can override).

        WHY: Captures pass state for rollback or transfer to next pass.
        Default implementation works for most cases, but can be overridden for
        custom state capture requirements.

        Args:
            result: PassResult from execute()
            state: Additional state to capture (configuration, intermediate results, etc.)

        Returns:
            PassMemento with complete state snapshot

        Design note: Separated from execute() to allow state capture at different
        points in pass lifecycle (not just at completion).
        """
        return PassMemento(
            pass_name=self.get_pass_name(),
            state=state,
            artifacts=result.artifacts,
            learnings=result.learnings,
            insights=result.insights,
            quality_score=result.quality_score,
            metadata=result.metadata
        )

    def apply_memento(self, memento: PassMemento, context: Dict[str, Any]) -> None:
        """
        Apply memento to context (Template Method - can override).

        WHY: Transfers learnings and insights from previous pass to current
        pass. Enables second pass to benefit from first pass discoveries.

        Args:
            memento: State snapshot from previous pass
            context: Current pass context to augment with memento data

        Side effects: Modifies context dict to include memento learnings and insights

        Design note: Modifies context in-place rather than returning new context
        because context may be large and copying is expensive.
        """
        # Merge learnings - use set to deduplicate
        existing_learnings = set(context.get("learnings", []))
        existing_learnings.update(memento.learnings)
        context["learnings"] = list(existing_learnings)

        # Merge insights - preserve both old and new
        if "insights" not in context:
            context["insights"] = {}
        context["insights"].update(memento.insights)

        # Store previous pass quality score for comparison
        context["previous_quality_score"] = memento.quality_score

    def emit_event(self, event_type: TwoPassEventType, data: Dict[str, Any]) -> None:
        """
        Emit event to observers (helper method).

        WHY: Centralizes event emission logic with consistent data structure.
        All events include standard fields (pass_name, timestamp) plus custom data.

        Args:
            event_type: Type of event to emit
            data: Event-specific data

        Design note: Converts TwoPassEventType to EventType.STAGE_PROGRESS for
        compatibility with existing observer infrastructure.
        """
        # Guard clause - early return if no observable
        if not self.observable:
            return

        # Create event with standard EventType that observers understand
        # Use STAGE_PROGRESS as catch-all for custom events
        event = PipelineEvent(
            event_type=EventType.STAGE_PROGRESS,
            stage_name=self.get_pass_name(),
            data={
                "two_pass_event": event_type.value,
                "pass_name": self.get_pass_name(),
                **data
            }
        )

        self.observable.notify(event)


__all__ = ["PassStrategy"]
