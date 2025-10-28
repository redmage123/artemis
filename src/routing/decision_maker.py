#!/usr/bin/env python3
"""
WHY: Orchestrate routing decision process and build complete RoutingDecision objects.

RESPONSIBILITY:
- Coordinate task analysis, stage selection, and policy enforcement
- Build complete RoutingDecision from components
- Handle complexity recalculation from sprint planning
- Log routing decisions for visibility

PATTERNS:
- Facade Pattern: Simplifies complex routing workflow
- Composition: Delegates to specialized components
- Guard Clauses: Early returns for edge cases
- Single Responsibility: Only orchestrates decision-making
"""

from typing import Dict, List, Any, Optional

from routing.models import RoutingDecision, TaskRequirements
from routing.task_analyzer import TaskAnalyzer
from routing.stage_selector import StageSelector
from routing.policy_enforcer import PolicyEnforcer
from routing.complexity_classifier import ComplexityClassifier


class DecisionMaker:
    """
    WHY: Orchestrate the complete routing decision workflow.

    RESPONSIBILITY:
    - Coordinate task analysis
    - Select appropriate stages
    - Enforce policies
    - Build RoutingDecision objects
    - Handle complexity recalculation
    - Log decisions
    """

    def __init__(
        self,
        task_analyzer: TaskAnalyzer,
        stage_selector: StageSelector,
        policy_enforcer: PolicyEnforcer,
        complexity_classifier: ComplexityClassifier,
        logger: Optional[Any] = None
    ):
        """
        WHY: Initialize with all required components.

        Args:
            task_analyzer: Analyzes task requirements
            stage_selector: Selects stages to run
            policy_enforcer: Enforces routing policies
            complexity_classifier: Classifies task complexity
            logger: Logger for output
        """
        self.task_analyzer = task_analyzer
        self.stage_selector = stage_selector
        self.policy_enforcer = policy_enforcer
        self.complexity_classifier = complexity_classifier
        self.logger = logger

    def make_decision(self, card: Dict[str, Any]) -> RoutingDecision:
        """
        WHY: Create complete routing decision for a task.

        RESPONSIBILITY:
        - Analyze task requirements
        - Enforce policies on requirements
        - Select stages based on requirements
        - Build reasoning
        - Return complete RoutingDecision

        Args:
            card: Kanban card with task details

        Returns:
            Complete RoutingDecision with stage selections

        PATTERNS: Template Method - defines decision workflow
        """
        # Step 1: Analyze task requirements
        requirements = self.task_analyzer.analyze(card)

        # Step 2: Enforce policies
        requirements = self.policy_enforcer.enforce_dev_group_policy(requirements)

        # Step 3: Select stages
        selection_result = self.stage_selector.select_stages(requirements)
        stage_decisions = selection_result['stage_decisions']
        reasoning_parts = selection_result['reasoning_parts']

        # Step 4: Build stage lists
        stage_lists = self.stage_selector.build_stage_lists(stage_decisions)

        # Step 5: Build reasoning
        reasoning = "; ".join(reasoning_parts) if reasoning_parts else "Running all standard stages"

        # Step 6: Create RoutingDecision
        return RoutingDecision(
            task_id=card.get('card_id', card.get('task_id', 'unknown')),
            task_title=card.get('title', 'Unknown'),
            requirements=requirements,
            stage_decisions=stage_decisions,
            stages_to_run=stage_lists['stages_to_run'],
            stages_to_skip=stage_lists['stages_to_skip'],
            reasoning=reasoning,
            confidence_score=requirements.confidence_score
        )

    def recalculate_from_sprint_planning(
        self,
        card: Dict[str, Any],
        sprint_planning_result: Dict[str, Any]
    ) -> RoutingDecision:
        """
        WHY: Recalculate routing decision with actual story points from sprint planning.

        RESPONSIBILITY:
        - Extract actual story points from sprint planning
        - Recalculate complexity from actual points
        - Update routing decision if complexity changed
        - Log recalculation details

        This fixes the bug where AI guesses complexity without seeing actual breakdown.

        Args:
            card: Kanban card
            sprint_planning_result: Result from SprintPlanningStage with:
                - total_story_points: Actual calculated story points
                - features: List of features with individual story points

        Returns:
            Updated RoutingDecision with corrected complexity

        PATTERNS: Guard Clauses - early return if no data or no change
        """
        # Extract actual story points
        total_story_points = sprint_planning_result.get('total_story_points', 0)
        features = sprint_planning_result.get('features', [])

        # Guard: No sprint planning data - keep original decision
        if total_story_points == 0:
            if self.logger:
                self.logger.log(
                    "No sprint planning data available, keeping original complexity",
                    "WARNING"
                )
            return self.make_decision(card)

        # Calculate corrected complexity
        corrected_complexity = self.complexity_classifier.classify_from_story_points(
            total_story_points
        )

        # Get original decision
        original_decision = self.make_decision(card)
        original_complexity = original_decision.requirements.complexity

        # Guard: No change needed
        if original_complexity == corrected_complexity:
            return original_decision

        # Log recalculation
        self._log_complexity_recalculation(
            original=original_complexity,
            corrected=corrected_complexity,
            total_points=total_story_points,
            features=features
        )

        # Update requirements with corrected complexity
        return self._update_decision_with_corrected_complexity(
            original_decision=original_decision,
            corrected_complexity=corrected_complexity,
            total_story_points=total_story_points,
            card=card
        )

    def _log_complexity_recalculation(
        self,
        original: str,
        corrected: str,
        total_points: int,
        features: List[Dict[str, Any]]
    ) -> None:
        """
        WHY: Log complexity recalculation for visibility.

        RESPONSIBILITY:
        - Log original vs corrected complexity
        - Show actual story points
        - Display feature breakdown

        Args:
            original: Original complexity classification
            corrected: Corrected complexity classification
            total_points: Total story points
            features: List of features with story points

        PATTERNS: Guard Clause - skip if no logger
        """
        # Guard: No logger
        if not self.logger:
            return

        self.logger.log("=" * 60, "INFO")
        self.logger.log("COMPLEXITY RECALCULATION", "INFO")
        self.logger.log("=" * 60, "INFO")
        self.logger.log(f"Original AI Classification: {original}", "INFO")
        self.logger.log(f"Actual Story Points from Sprint Planning: {total_points}", "INFO")
        self.logger.log(f"Corrected Complexity: {corrected}", "INFO")
        self.logger.log(f"Features Breakdown:", "INFO")
        for feature in features:
            self.logger.log(
                f"  - {feature.get('title', 'Unknown')}: {feature.get('story_points', 0)} points",
                "INFO"
            )
        self.logger.log("=" * 60, "INFO")

    def _update_decision_with_corrected_complexity(
        self,
        original_decision: RoutingDecision,
        corrected_complexity: str,
        total_story_points: int,
        card: Dict[str, Any]
    ) -> RoutingDecision:
        """
        WHY: Rebuild routing decision with corrected complexity.

        RESPONSIBILITY:
        - Update card with actual story points
        - Recalculate review requirements
        - Rebuild routing decision

        Args:
            original_decision: Original routing decision
            corrected_complexity: Corrected complexity classification
            total_story_points: Total story points
            card: Kanban card

        Returns:
            Updated routing decision

        PATTERNS: Immutability - creates new decision instead of modifying
        """
        # Update card with actual story points
        card_copy = card.copy()
        card_copy['story_points'] = total_story_points

        # Rebuild decision with corrected data
        return self.make_decision(card_copy)

    def filter_stages(
        self,
        all_stages: List[Any],
        routing_decision: RoutingDecision
    ) -> List[Any]:
        """
        WHY: Filter stage instances based on routing decision.

        RESPONSIBILITY:
        - Extract stage names to run
        - Filter stage instances by name
        - Maintain execution order

        Args:
            all_stages: List of stage instances
            routing_decision: Routing decision with stages to run

        Returns:
            Filtered list of stage instances to execute

        PATTERNS: Filter Pattern - selects matching elements
        """
        stages_to_run_names = set(routing_decision.stages_to_run)

        filtered_stages = [
            stage for stage in all_stages
            if stage.get_stage_name() in stages_to_run_names
        ]

        return filtered_stages

    def log_decision(self, decision: RoutingDecision) -> None:
        """
        WHY: Log routing decision for visibility and debugging.

        RESPONSIBILITY:
        - Format decision as readable output
        - Show all requirements
        - List stages to run/skip
        - Display reasoning and confidence

        Args:
            decision: Routing decision to log

        PATTERNS: Guard Clause - skip if no logger
        """
        # Guard: No logger
        if not self.logger:
            return

        self.logger.log("=" * 60, "INFO")
        self.logger.log("INTELLIGENT ROUTING DECISION", "INFO")
        self.logger.log("=" * 60, "INFO")
        self.logger.log(f"Task: {decision.task_title}", "INFO")
        self.logger.log(f"Complexity: {decision.requirements.complexity}", "INFO")
        self.logger.log(f"Type: {decision.requirements.task_type}", "INFO")
        self.logger.log(f"Story Points: {decision.requirements.estimated_story_points}", "INFO")
        self.logger.log(
            f"Parallel Developers: {decision.requirements.parallel_developers_recommended}",
            "INFO"
        )
        self.logger.log("", "INFO")
        self.logger.log("Requirements Detected:", "INFO")
        self.logger.log(f"  Frontend: {decision.requirements.has_frontend}", "INFO")
        self.logger.log(f"  Backend: {decision.requirements.has_backend}", "INFO")
        self.logger.log(f"  API: {decision.requirements.has_api}", "INFO")
        self.logger.log(f"  Database: {decision.requirements.has_database}", "INFO")
        self.logger.log(f"  UI Components: {decision.requirements.has_ui_components}", "INFO")
        self.logger.log(
            f"  Accessibility: {decision.requirements.has_accessibility_requirements}",
            "INFO"
        )
        self.logger.log(
            f"  External Deps: {decision.requirements.has_external_dependencies}",
            "INFO"
        )
        self.logger.log("", "INFO")
        self.logger.log(f"Stages to Run ({len(decision.stages_to_run)}):", "INFO")
        for stage in decision.stages_to_run:
            self.logger.log(f"  ✓ {stage}", "INFO")
        self.logger.log("", "INFO")
        if decision.stages_to_skip:
            self.logger.log(f"Stages to Skip ({len(decision.stages_to_skip)}):", "INFO")
            for stage in decision.stages_to_skip:
                self.logger.log(f"  ✗ {stage}", "INFO")
            self.logger.log("", "INFO")
        self.logger.log(f"Reasoning: {decision.reasoning}", "INFO")
        self.logger.log(f"Confidence: {decision.confidence_score:.1%}", "INFO")
        self.logger.log("=" * 60, "INFO")
