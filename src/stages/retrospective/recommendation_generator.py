#!/usr/bin/env python3
"""
Recommendation Generator

WHY: Generate actionable recommendations for next sprint
RESPONSIBILITY: Analyze context and produce prioritized recommendations
PATTERNS: Single Responsibility, Parameter Object, Guard Clauses
"""

from typing import List

from .retrospective_models import RetrospectiveContext


class RecommendationGenerator:
    """
    Generate recommendations for next sprint

    WHY: Provide actionable guidance based on retrospective
    RESPONSIBILITY: Create prioritized recommendations
    PATTERNS: Single Responsibility, Parameter Object pattern
    """

    def generate_recommendations(
        self,
        context: RetrospectiveContext
    ) -> List[str]:
        """
        Generate recommendations for next sprint using Parameter Object

        Args:
            context: RetrospectiveContext with all analysis data

        Returns:
            List of actionable recommendations

        WHY: Parameter Object reduces parameter count and improves clarity
        RESPONSIBILITY: Aggregate recommendations from multiple sources
        PATTERNS: Parameter Object, Guard clauses
        """
        recommendations = []

        # Velocity-based recommendations
        recommendations.extend(self._generate_velocity_recommendations(context))

        # Health-based recommendations
        recommendations.extend(self._generate_health_recommendations(context))

        # Action item recommendations
        recommendations.extend(self._generate_action_recommendations(context))

        # Recurring issue recommendations
        recommendations.extend(self._generate_recurring_issue_recommendations(context))

        # Test quality recommendations
        recommendations.extend(self._generate_test_quality_recommendations(context))

        return recommendations

    def _generate_velocity_recommendations(
        self,
        context: RetrospectiveContext
    ) -> List[str]:
        """
        Generate velocity-based recommendations

        WHY: Velocity trend indicates process health
        RESPONSIBILITY: Recommend velocity improvements
        PATTERNS: Guard clauses, Dispatch table approach
        """
        recommendations = []

        # Guard: Declining trend
        if context.velocity_trend == "declining":
            recommendations.append(
                "Consider reducing sprint scope or investigating capacity constraints"
            )
            return recommendations

        # Guard: Improving trend
        if context.velocity_trend == "improving":
            recommendations.append(
                "Maintain current practices that are improving velocity"
            )

        return recommendations

    def _generate_health_recommendations(
        self,
        context: RetrospectiveContext
    ) -> List[str]:
        """
        Generate health-based recommendations

        WHY: Critical health needs immediate attention
        RESPONSIBILITY: Recommend health improvements
        PATTERNS: Guard clause, Derived property usage
        """
        # Guard: Check if immediate attention needed (using derived property)
        if not context.needs_immediate_attention:
            return []

        return [
            "Focus on addressing critical issues before planning next sprint",
            "Consider a technical debt sprint to stabilize the codebase"
        ]

    def _generate_action_recommendations(
        self,
        context: RetrospectiveContext
    ) -> List[str]:
        """
        Generate action item recommendations

        WHY: High-priority actions need visibility
        RESPONSIBILITY: Recommend action prioritization
        PATTERNS: Guard clause, Derived property usage
        """
        # Use derived property for high-priority actions
        high_priority_actions = context.high_priority_actions

        # Guard: Only if high-priority actions exist
        if not high_priority_actions:
            return []

        return [
            f"Prioritize {len(high_priority_actions)} high-impact action items in next sprint planning"
        ]

    def _generate_recurring_issue_recommendations(
        self,
        context: RetrospectiveContext
    ) -> List[str]:
        """
        Generate recurring issue recommendations

        WHY: Recurring issues need systemic solutions
        RESPONSIBILITY: Recommend recurring issue remediation
        PATTERNS: Guard clause, Derived property usage
        """
        # Use derived property for recurring issues
        recurring_issues = context.recurring_issues

        # Guard: Only if recurring issues exist
        if not recurring_issues:
            return []

        return [
            f"Address {len(recurring_issues)} recurring issues to prevent future sprints from similar problems"
        ]

    def _generate_test_quality_recommendations(
        self,
        context: RetrospectiveContext
    ) -> List[str]:
        """
        Generate test quality recommendations

        WHY: Test quality is critical for code health
        RESPONSIBILITY: Recommend test improvements
        PATTERNS: Guard clause
        """
        # Guard: Only if test quality is below threshold
        if context.metrics.tests_passing >= 90:
            return []

        return [
            "Improve test coverage and quality - current pass rate below threshold"
        ]
