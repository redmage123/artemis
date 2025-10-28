#!/usr/bin/env python3
"""
Learning Extractor

WHY: Extract key learnings from sprint for organizational knowledge
RESPONSIBILITY: Identify patterns and generate actionable insights
PATTERNS: Single Responsibility, Guard Clauses, List Comprehensions
"""

from typing import Dict, List, Any

from .retrospective_models import RetrospectiveItem


class LearningExtractor:
    """
    Extract key learnings from sprint retrospective

    WHY: Capture organizational knowledge and patterns
    RESPONSIBILITY: Generate insights from sprint data and findings
    PATTERNS: Single Responsibility, Pattern detection
    """

    def extract_learnings(
        self,
        sprint_data: Dict[str, Any],
        successes: List[RetrospectiveItem],
        failures: List[RetrospectiveItem],
        historical_data: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Extract key learnings from sprint

        Args:
            sprint_data: Raw sprint data
            successes: Success items
            failures: Failure items
            historical_data: Historical sprint data

        Returns:
            List of learning statements

        WHY: Consolidate insights from multiple sources
        RESPONSIBILITY: Generate actionable learnings
        PATTERNS: Guard clauses, List comprehensions
        """
        learnings = []

        # Detect overload patterns
        learnings.extend(self._detect_overload_patterns(failures))

        # Extract historical insights
        learnings.extend(self._extract_historical_insights(historical_data))

        # Identify success patterns
        learnings.extend(self._identify_success_patterns(successes))

        # Identify recurring failure patterns
        learnings.extend(self._identify_failure_patterns(failures))

        return learnings

    def _detect_overload_patterns(
        self,
        failures: List[RetrospectiveItem]
    ) -> List[str]:
        """
        Detect sprint overload from failure count

        WHY: Too many challenges indicate scope/planning issues
        RESPONSIBILITY: Identify overload situations
        PATTERNS: Guard clause
        """
        # Guard: Only report if many failures
        if len(failures) <= 3:
            return []

        return [
            f"Sprint had {len(failures)} challenges - may need to reduce scope or improve planning"
        ]

    def _extract_historical_insights(
        self,
        historical_data: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Extract insights from historical comparison

        WHY: Historical context provides trends
        RESPONSIBILITY: Generate historical learnings
        PATTERNS: Guard clause
        """
        # Guard: Only if historical data exists
        if not historical_data:
            return []

        return ["Historical sprint data reviewed for velocity trends"]

    def _identify_success_patterns(
        self,
        successes: List[RetrospectiveItem]
    ) -> List[str]:
        """
        Identify patterns in successes

        WHY: Document what works well
        RESPONSIBILITY: Extract success learnings
        PATTERNS: List comprehension, Guard clause
        """
        # Filter high-impact successes
        high_impact_successes = [s for s in successes if s.impact == "high"]

        # Guard: Only if high-impact successes exist
        if not high_impact_successes:
            return []

        # Take first 2 successes for brevity
        success_descriptions = [s.description for s in high_impact_successes[:2]]

        return [
            f"Team excelled at: {', '.join(success_descriptions)}"
        ]

    def _identify_failure_patterns(
        self,
        failures: List[RetrospectiveItem]
    ) -> List[str]:
        """
        Identify recurring failure patterns

        WHY: Recurring issues need systemic solutions
        RESPONSIBILITY: Extract recurring failure learnings
        PATTERNS: List comprehension, Guard clause
        """
        # Filter recurring failures
        recurring_failures = [f for f in failures if f.frequency == "recurring"]

        # Guard: Only if recurring failures exist
        if not recurring_failures:
            return []

        # Take first 2 recurring failures for brevity
        failure_descriptions = [f.description for f in recurring_failures[:2]]

        return [
            f"Recurring issues identified: {', '.join(failure_descriptions)}"
        ]
