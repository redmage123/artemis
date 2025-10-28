#!/usr/bin/env python3
"""
Action Item Generator

WHY: Generate actionable improvements for next sprint
RESPONSIBILITY: Convert retrospective findings into concrete action items
PATTERNS: Single Responsibility, List Comprehensions, Guard Clauses
"""

from typing import List

from .retrospective_models import RetrospectiveItem, SprintMetrics


class ActionItemGenerator:
    """
    Generate concrete action items from retrospective findings

    WHY: Transform insights into actionable improvements
    RESPONSIBILITY: Create prioritized action items for next sprint
    PATTERNS: Single Responsibility, List comprehensions
    """

    def generate_action_items(
        self,
        successes: List[RetrospectiveItem],
        failures: List[RetrospectiveItem],
        metrics: SprintMetrics
    ) -> List[RetrospectiveItem]:
        """
        Generate concrete action items for next sprint

        Args:
            successes: What went well items
            failures: What didn't go well items
            metrics: Sprint metrics (for context)

        Returns:
            List of action items prioritized by impact

        WHY: Consolidate actions from multiple sources
        RESPONSIBILITY: Aggregate and prioritize actions
        PATTERNS: List comprehensions for transformation
        """
        # Extract failure remediation actions (high/medium impact only)
        failure_actions = self._extract_failure_actions(failures)

        # Extract success reinforcement actions
        success_actions = self._extract_success_actions(successes)

        # Combine and return
        return failure_actions + success_actions

    def _extract_failure_actions(
        self,
        failures: List[RetrospectiveItem]
    ) -> List[RetrospectiveItem]:
        """
        Extract suggested actions from failures

        Args:
            failures: List of failure items

        Returns:
            List of action items from failures

        WHY: Focus on fixing problems
        RESPONSIBILITY: Convert failures to actions
        PATTERNS: List comprehension with guards
        """
        # Guard: Filter failures with suggestions and high/medium impact
        return [
            RetrospectiveItem(
                category="action_items",
                description=failure.suggested_action,
                impact=failure.impact,
                frequency="one-time"
            )
            for failure in failures
            if failure.suggested_action and failure.impact in ['high', 'medium']
        ]

    def _extract_success_actions(
        self,
        successes: List[RetrospectiveItem]
    ) -> List[RetrospectiveItem]:
        """
        Extract actions to maintain successes

        Args:
            successes: List of success items

        Returns:
            List of action items to maintain successes

        WHY: Preserve what works well
        RESPONSIBILITY: Convert successes to maintenance actions
        PATTERNS: List comprehension with guards
        """
        # Guard: Filter recurring high-impact successes with suggestions
        return [
            RetrospectiveItem(
                category="action_items",
                description=success.suggested_action,
                impact="medium",
                frequency="recurring"
            )
            for success in successes
            if (success.frequency == "recurring" and
                success.impact == "high" and
                success.suggested_action)
        ]
