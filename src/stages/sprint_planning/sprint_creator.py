#!/usr/bin/env python3
"""
Module: sprint_creator.py

WHY: Allocate prioritized features to sprint backlogs
RESPONSIBILITY: Create sprint schedules respecting velocity constraints
PATTERNS: Strategy pattern with SprintAllocator
"""

from typing import List
from sprint_models import (
    PrioritizedFeature,
    Sprint,
    SprintAllocator,
    SprintScheduler,
    Clock,
    SystemClock
)
from artemis_exceptions import SprintAllocationError, wrap_exception


class SprintCreator:
    """
    WHY: Sprint allocation is complex with velocity and capacity constraints
    RESPONSIBILITY: Coordinate sprint scheduling and feature allocation
    PATTERNS: Strategy pattern delegates to SprintScheduler/SprintAllocator
    """

    def __init__(
        self,
        team_velocity: float,
        sprint_duration_days: int = 14,
        clock: Clock = None
    ):
        """
        WHY: Configure sprint parameters (velocity, duration, time source)

        Args:
            team_velocity: Team story points capacity per sprint
            sprint_duration_days: Sprint duration in days (default 2 weeks)
            clock: Clock abstraction for testable time (default SystemClock)
        """
        self.clock = clock or SystemClock()
        self.scheduler = SprintScheduler(
            sprint_duration_days=sprint_duration_days,
            clock=self.clock
        )
        self.allocator = SprintAllocator(
            team_velocity=team_velocity,
            scheduler=self.scheduler
        )

    def create_sprints(
        self,
        prioritized_features: List[PrioritizedFeature]
    ) -> List[Sprint]:
        """
        WHY: Convert prioritized feature list into sprint backlogs
        RESPONSIBILITY: Delegate to allocator and handle errors
        PATTERNS: Guard clause for empty input

        Args:
            prioritized_features: Features sorted by priority

        Returns:
            List of Sprint objects with allocated features

        Raises:
            SprintAllocationError: If allocation fails
        """
        # Guard: No features to allocate
        if not prioritized_features:
            return []

        try:
            return self.allocator.allocate_features_to_sprints(
                prioritized_features
            )
        except Exception as e:
            raise wrap_exception(
                e,
                SprintAllocationError,
                "Failed to allocate features to sprints",
                {"feature_count": len(prioritized_features)}
            )
