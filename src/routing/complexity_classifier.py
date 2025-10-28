#!/usr/bin/env python3
"""
WHY: Classify task complexity from story points and requirements.

RESPONSIBILITY:
- Map story points to complexity levels (simple/medium/complex)
- Provide consistent complexity classification rules
- Support recalculation from sprint planning results

PATTERNS:
- Single Responsibility: Only handles complexity classification
- Strategy Pattern: Multiple classification strategies (story points, requirements)
- Guard Clauses: Early returns for edge cases
"""

from typing import Dict, List, Optional, Any


class ComplexityClassifier:
    """
    WHY: Centralized complexity classification logic.

    RESPONSIBILITY:
    - Convert story points to complexity levels
    - Apply consistent classification thresholds
    - Support both initial estimates and actual calculations
    """

    # Complexity thresholds (Fibonacci story points)
    SIMPLE_THRESHOLD = 3    # 1-3 points = simple
    MEDIUM_THRESHOLD = 8    # 5-8 points = medium
                           # 13+ points = complex

    def classify_from_story_points(self, story_points: int) -> str:
        """
        WHY: Convert numeric story points to semantic complexity level.

        RESPONSIBILITY:
        - Apply threshold-based classification
        - Return standardized complexity strings

        Args:
            story_points: Story point value (Fibonacci scale)

        Returns:
            Complexity level: 'simple', 'medium', or 'complex'

        PATTERNS: Guard Clauses - early return on threshold match
        """
        # Guard: Simple tasks
        if story_points <= self.SIMPLE_THRESHOLD:
            return 'simple'

        # Guard: Medium tasks
        if story_points <= self.MEDIUM_THRESHOLD:
            return 'medium'

        # Default: Complex tasks
        return 'complex'

    def recalculate_from_sprint_planning(
        self,
        sprint_planning_result: Dict[str, Any]
    ) -> Optional[str]:
        """
        WHY: Recalculate complexity from actual sprint planning breakdown.

        RESPONSIBILITY:
        - Extract total story points from sprint planning
        - Return corrected complexity classification
        - Return None if sprint planning data unavailable

        Args:
            sprint_planning_result: Sprint planning output with:
                - total_story_points: Actual calculated points
                - features: List of features with individual points

        Returns:
            Corrected complexity classification or None if data missing

        PATTERNS: Guard Clause - early None return if data invalid
        """
        # Guard: No sprint planning data
        total_story_points = sprint_planning_result.get('total_story_points', 0)
        if total_story_points == 0:
            return None

        # Classify from actual story points
        return self.classify_from_story_points(total_story_points)

    def calculate_review_requirements(
        self,
        complexity: str,
        has_database: bool = False,
        has_api: bool = False,
        story_points: int = 0
    ) -> Dict[str, bool]:
        """
        WHY: Determine which review stages are needed based on complexity and requirements.

        RESPONSIBILITY:
        - Calculate architecture review requirement
        - Calculate project review requirement
        - Apply consistent rules across routing decisions

        Args:
            complexity: Task complexity level
            has_database: Whether task involves database changes
            has_api: Whether task involves API changes
            story_points: Story point estimate

        Returns:
            Dictionary with 'architecture_review' and 'project_review' booleans

        PATTERNS: Single Responsibility - encapsulates review requirement logic
        """
        # Architecture review: medium/complex tasks or DB/API changes
        requires_architecture_review = (
            complexity in ['medium', 'complex'] or
            has_database or
            has_api
        )

        # Project review: complex tasks or high story points
        requires_project_review = (
            complexity == 'complex' or
            story_points >= 8
        )

        return {
            'architecture_review': requires_architecture_review,
            'project_review': requires_project_review
        }
