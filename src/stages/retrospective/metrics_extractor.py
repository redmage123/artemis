#!/usr/bin/env python3
"""
Sprint Metrics Extractor

WHY: Extract quantitative metrics from sprint data
RESPONSIBILITY: Parse sprint data and calculate performance metrics
PATTERNS: Single Responsibility, Guard Clauses
"""

from typing import Dict, Any
from .retrospective_models import SprintMetrics


class MetricsExtractor:
    """
    Extract quantitative metrics from sprint execution data

    WHY: Separate metrics extraction from analysis logic
    RESPONSIBILITY: Convert raw sprint data into structured metrics
    PATTERNS: Single Responsibility Principle
    """

    def extract_metrics(self, sprint_data: Dict[str, Any]) -> SprintMetrics:
        """
        Extract quantitative metrics from sprint data

        Args:
            sprint_data: Raw sprint execution data

        Returns:
            SprintMetrics with calculated performance indicators

        WHY: Centralize metrics calculation logic
        RESPONSIBILITY: Transform raw data into metrics model
        PATTERNS: Guard clause for safe division
        """
        # Guard: Safe velocity calculation
        total_points = sprint_data.get('total_story_points', 1)
        completed_points = sprint_data.get('completed_story_points', 0)
        velocity = (completed_points / max(total_points, 1)) * 100

        return SprintMetrics(
            sprint_number=sprint_data.get('sprint_number', 0),
            planned_story_points=total_points,
            completed_story_points=completed_points,
            velocity=velocity,
            bugs_found=sprint_data.get('bugs_found', 0),
            bugs_fixed=sprint_data.get('bugs_fixed', 0),
            tests_passing=sprint_data.get('test_pass_rate', 100.0),
            code_review_iterations=sprint_data.get('code_review_iterations', 0),
            average_task_duration_hours=sprint_data.get('average_task_duration_hours', 0),
            blockers_encountered=sprint_data.get('blockers_encountered', 0)
        )
