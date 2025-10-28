#!/usr/bin/env python3
"""
WHY: Main IntelligentRouter class coordinating all routing components.

RESPONSIBILITY:
- Initialize all routing components
- Provide simplified interface for routing operations
- Delegate to specialized components
- Maintain backward compatibility interface

PATTERNS:
- Facade Pattern: Simplifies complex subsystem
- Dependency Injection: Components passed to constructor
- Composition over Inheritance: Delegates to components
- Single Responsibility: Only coordinates components
"""

from typing import Dict, List, Optional, Any

from routing.models import RoutingDecision, TaskRequirements
from routing.task_analyzer import TaskAnalyzer
from routing.stage_selector import StageSelector
from routing.policy_enforcer import PolicyEnforcer
from routing.complexity_classifier import ComplexityClassifier
from routing.decision_maker import DecisionMaker
from ai_query_service import AIQueryService
from debug_mixin import DebugMixin


class IntelligentRouter(DebugMixin):
    """
    WHY: Intelligent router that uses AI to determine which stages should execute.

    RESPONSIBILITY:
    - Coordinate all routing components
    - Provide simple interface for routing decisions
    - Support complexity recalculation from sprint planning
    - Log routing decisions for visibility

    PATTERNS: Facade - hides complexity of routing subsystem
    """

    def __init__(
        self,
        ai_service: Optional[AIQueryService] = None,
        logger: Optional[Any] = None,
        config: Optional[Any] = None
    ):
        """
        WHY: Initialize router with dependencies and build component graph.

        RESPONSIBILITY:
        - Initialize DebugMixin
        - Create all routing components
        - Wire components together
        - Load configuration

        Args:
            ai_service: AI Query Service for requirement analysis
            logger: Logger for output
            config: Configuration for routing rules

        PATTERNS: Constructor Injection - dependencies passed as parameters
        """
        # Initialize DebugMixin
        DebugMixin.__init__(self, component_name="routing")

        self.ai_service = ai_service
        self.logger = logger
        self.config = config

        # Load routing configuration
        self.enable_ai_routing = config.get('routing.enable_ai', True) if config else True
        self.skip_stages_threshold = config.get('routing.skip_threshold', 0.8) if config else 0.8
        self.require_stages_threshold = config.get('routing.require_threshold', 0.6) if config else 0.6

        # Build component graph
        self.complexity_classifier = ComplexityClassifier()

        self.task_analyzer = TaskAnalyzer(
            ai_service=ai_service,
            complexity_classifier=self.complexity_classifier,
            logger=logger,
            config=config
        )

        self.stage_selector = StageSelector()

        self.policy_enforcer = PolicyEnforcer(
            logger=logger,
            config=config
        )

        self.decision_maker = DecisionMaker(
            task_analyzer=self.task_analyzer,
            stage_selector=self.stage_selector,
            policy_enforcer=self.policy_enforcer,
            complexity_classifier=self.complexity_classifier,
            logger=logger
        )

    def analyze_task_requirements(self, card: Dict[str, Any]) -> TaskRequirements:
        """
        WHY: Analyze task to extract requirements.

        RESPONSIBILITY:
        - Delegate to TaskAnalyzer
        - Return structured TaskRequirements

        Args:
            card: Kanban card with task details

        Returns:
            TaskRequirements with analyzed needs

        PATTERNS: Delegation - forwards to TaskAnalyzer
        """
        return self.task_analyzer.analyze(card)

    def make_routing_decision(self, card: Dict[str, Any]) -> RoutingDecision:
        """
        WHY: Make complete routing decision for a task.

        RESPONSIBILITY:
        - Delegate to DecisionMaker
        - Return complete RoutingDecision

        Args:
            card: Kanban card with task details

        Returns:
            RoutingDecision with stage selections

        PATTERNS: Delegation - forwards to DecisionMaker
        """
        return self.decision_maker.make_decision(card)

    def recalculate_complexity_from_sprint_planning(
        self,
        card: Dict[str, Any],
        sprint_planning_result: Dict[str, Any]
    ) -> RoutingDecision:
        """
        WHY: Recalculate complexity based on actual sprint planning results.

        RESPONSIBILITY:
        - Delegate to DecisionMaker
        - Return updated RoutingDecision

        This method overrides the initial AI classification with actual story point totals
        calculated by sprint planning. This fixes the bug where AI guesses complexity
        without seeing actual breakdown.

        Args:
            card: Kanban card
            sprint_planning_result: Result from SprintPlanningStage with:
                - total_story_points: Actual calculated story points
                - features: List of features with individual story points

        Returns:
            Updated RoutingDecision with corrected complexity

        PATTERNS: Delegation - forwards to DecisionMaker
        """
        # DEBUG: Trace recalculation using mixin
        total_story_points = sprint_planning_result.get('total_story_points', 0)
        self.debug_trace(
            "recalculate_complexity_from_sprint_planning",
            total_story_points=total_story_points
        )

        return self.decision_maker.recalculate_from_sprint_planning(
            card=card,
            sprint_planning_result=sprint_planning_result
        )

    def filter_stages(
        self,
        all_stages: List[Any],
        routing_decision: RoutingDecision
    ) -> List[Any]:
        """
        WHY: Filter stage instances based on routing decision.

        RESPONSIBILITY:
        - Delegate to DecisionMaker
        - Return filtered stage list

        Args:
            all_stages: List of stage instances
            routing_decision: Routing decision with stages to run

        Returns:
            Filtered list of stage instances to execute

        PATTERNS: Delegation - forwards to DecisionMaker
        """
        return self.decision_maker.filter_stages(all_stages, routing_decision)

    def log_routing_decision(self, decision: RoutingDecision) -> None:
        """
        WHY: Log routing decision for visibility.

        RESPONSIBILITY:
        - Dump debug info if enabled
        - Delegate to DecisionMaker for logging

        Args:
            decision: Routing decision to log

        PATTERNS: Delegation - forwards to DecisionMaker
        """
        # DEBUG: Dump full routing decision using mixin
        self.debug_dump_if_enabled('log_decisions', "Routing Decision", {
            "task_title": decision.task_title,
            "complexity": decision.requirements.complexity,
            "task_type": decision.requirements.task_type,
            "story_points": decision.requirements.estimated_story_points,
            "parallel_developers": decision.requirements.parallel_developers_recommended,
            "stages": decision.stages_to_run,
            "skip_stages": decision.stages_to_skip
        })

        self.decision_maker.log_decision(decision)
