#!/usr/bin/env python3
"""
WHY: Calculate overall health status from metrics
RESPONSIBILITY: Determine health status based on stalled agent ratios
PATTERNS: Strategy (health calculation), Dispatch table (ratio thresholds)
"""

from typing import Callable, Dict

from .event_types import HealthStatus


class HealthCalculator:
    """
    WHY: Separate health calculation logic from monitoring
    RESPONSIBILITY: Calculate health status from stalled agent ratios
    PATTERNS: Strategy, Dispatch table
    """

    def __init__(self):
        """
        WHY: Initialize health calculator with threshold strategy
        RESPONSIBILITY: Setup threshold dispatch table
        PATTERNS: Dispatch table (threshold -> status mapping)
        """
        # Dispatch table: threshold -> status
        # Ordered from highest to lowest threshold
        self.threshold_dispatch: list[tuple[float, HealthStatus]] = [
            (0.75, HealthStatus.CRITICAL),
            (0.5, HealthStatus.FAILING),
            (0.0, HealthStatus.DEGRADED)
        ]

    def calculate_status(
        self,
        stalled_count: int,
        total_count: int
    ) -> HealthStatus:
        """
        WHY: Determine overall health status
        RESPONSIBILITY: Calculate stalled ratio and map to health level
        PATTERNS: Guard clause, Dispatch table

        Args:
            stalled_count: Number of stalled agents
            total_count: Total number of registered agents

        Returns:
            HealthStatus enum value
        """
        # No agents = healthy by default
        if total_count == 0:
            return HealthStatus.HEALTHY

        stalled_ratio = stalled_count / total_count
        return self._determine_health_from_ratio(stalled_ratio)

    def _determine_health_from_ratio(self, stalled_ratio: float) -> HealthStatus:
        """
        WHY: Map stalled ratio to health status
        RESPONSIBILITY: Use threshold dispatch table to determine status
        PATTERNS: Dispatch table (replaces elif chain)

        Args:
            stalled_ratio: Ratio of stalled agents (0.0 to 1.0)

        Returns:
            HealthStatus enum value
        """
        # Iterate through thresholds (highest to lowest)
        for threshold, status in self.threshold_dispatch:
            if stalled_ratio >= threshold:
                return status

        # All agents healthy
        return HealthStatus.HEALTHY

    def set_threshold(self, status: HealthStatus, threshold: float) -> None:
        """
        WHY: Allow custom threshold configuration
        RESPONSIBILITY: Update threshold for specific health status
        PATTERNS: Builder (configuration)

        Args:
            status: Health status to configure
            threshold: Stalled ratio threshold (0.0 to 1.0)
        """
        # Remove existing entry for this status
        self.threshold_dispatch = [
            (t, s) for t, s in self.threshold_dispatch if s != status
        ]

        # Add new threshold
        self.threshold_dispatch.append((threshold, status))

        # Re-sort by threshold (highest to lowest)
        self.threshold_dispatch.sort(key=lambda x: x[0], reverse=True)
