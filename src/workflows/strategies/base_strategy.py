#!/usr/bin/env python3
"""
Base Pipeline Strategy Interface.

WHY: Abstract strategy interface for pipeline execution patterns.
RESPONSIBILITY: Define contract for all pipeline execution strategies.
PATTERNS: Strategy Pattern, Template Method Pattern.

Dependencies: artemis_stage_interface, pipeline_observer
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime

from artemis_stage_interface import PipelineStage
from pipeline_observer import PipelineObservable, EventBuilder


class PipelineStrategy(ABC):
    """
    Abstract base class for pipeline execution strategies.

    All strategies must implement execute() which takes a list of stages
    and returns execution results.

    WHY: Provides common interface for interchangeable execution strategies.
    RESPONSIBILITY: Define strategy contract and shared utility methods.
    PATTERNS: Strategy Pattern - defines algorithm family interface.
    """

    def __init__(self, verbose: bool = True, observable: Optional[PipelineObservable] = None):
        """
        Initialize strategy.

        Args:
            verbose: Enable verbose logging
            observable: Optional PipelineObservable for event broadcasting
        """
        if not isinstance(verbose, bool):
            raise TypeError("verbose must be boolean")

        self.verbose = verbose
        self.observable = observable

    @abstractmethod
    def execute(self, stages: List[PipelineStage], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute pipeline stages using this strategy.

        Args:
            stages: List of pipeline stages to execute
            context: Execution context (card info, config, etc.)

        Returns:
            Dict with execution results:
            {
                "status": "success" | "failed",
                "stages_completed": int,
                "failed_stage": str (if failed),
                "results": Dict[str, Any],
                "duration_seconds": float,
                "strategy": str
            }
        """
        pass

    def _log(self, message: str, level: str = "INFO"):
        """
        Log message if verbose enabled.

        WHY: Centralized logging with consistent formatting.
        RESPONSIBILITY: Format and output log messages.
        """
        if not self.verbose:
            return

        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def _notify_stage_started(self, card_id: str, stage_name: str, **data):
        """
        Notify observers that stage started.

        WHY: Decouple stage execution from event notification.
        RESPONSIBILITY: Broadcast stage started events.
        """
        if not self.observable:
            return

        event = EventBuilder.stage_started(card_id, stage_name, **data)
        self.observable.notify(event)

    def _notify_stage_completed(self, card_id: str, stage_name: str, **data):
        """
        Notify observers that stage completed.

        WHY: Decouple stage execution from event notification.
        RESPONSIBILITY: Broadcast stage completed events.
        """
        if not self.observable:
            return

        event = EventBuilder.stage_completed(card_id, stage_name, **data)
        self.observable.notify(event)

    def _notify_stage_failed(self, card_id: str, stage_name: str, error: Exception, **data):
        """
        Notify observers that stage failed.

        WHY: Decouple stage execution from event notification.
        RESPONSIBILITY: Broadcast stage failed events.
        """
        if not self.observable:
            return

        event = EventBuilder.stage_failed(card_id, stage_name, error, **data)
        self.observable.notify(event)

    def _recalculate_complexity_after_sprint_planning(
        self,
        card: Dict,
        sprint_planning_result: Dict,
        context: Dict[str, Any]
    ):
        """
        POST-SPRINT-PLANNING HOOK: Recalculate complexity based on actual story points.

        WHY: Fix bug where AI guesses complexity without seeing actual sprint planning.
        RESPONSIBILITY: Update routing decision based on actual story points.
        PATTERNS: Hook Method Pattern - extension point for post-stage processing.

        Args:
            card: Kanban card
            sprint_planning_result: Result from SprintPlanningStage with total_story_points
            context: Pipeline execution context
        """
        # Guard: Check orchestrator exists
        orchestrator = context.get('orchestrator')
        if not orchestrator or not hasattr(orchestrator, 'intelligent_router'):
            return

        # Guard: Check router exists
        router = orchestrator.intelligent_router
        if not router:
            return

        # Recalculate complexity using intelligent router
        updated_decision = router.recalculate_complexity_from_sprint_planning(
            card,
            sprint_planning_result
        )

        # Update context with corrected routing decision
        context['routing_decision'] = updated_decision

        # Re-filter stages based on corrected complexity
        if not hasattr(orchestrator, 'stages'):
            return

        corrected_stages = router.filter_stages(orchestrator.stages, updated_decision)
        # Update orchestrator's active stages (note: won't affect current execution)
        self._log("🔧 Complexity recalculated after sprint planning", "INFO")
        self._log(f"   Updated stages to run: {len(corrected_stages)}", "INFO")
