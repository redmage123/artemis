#!/usr/bin/env python3
"""
Module: performance_tracker.py

WHY this module exists:
    Tracks pipeline performance metrics across executions for optimization
    and monitoring.

RESPONSIBILITY:
    - Track execution performance metrics
    - Calculate success rates and statistics
    - Maintain rolling window of metrics history
    - Generate performance summaries

PATTERNS:
    - Single Responsibility Principle (only performance tracking)
    - Guard clauses for feature flags
"""

from typing import Dict, Any, List
from datetime import datetime
from advanced_pipeline.pipeline_mode import PipelineMode
from advanced_pipeline.strategy.models import PerformanceMetrics


class PerformanceTracker:
    """
    Tracks pipeline performance metrics.

    WHY: Performance tracking enables comparing modes, identifying regressions,
    optimizing thresholds, and reporting on advanced features impact.

    RESPONSIBILITY: Track and aggregate performance metrics

    PATTERNS: Data aggregation, Rolling window pattern
    """

    def __init__(self, window_size: int = 100, enabled: bool = True):
        """
        Initialize performance tracker.

        Args:
            window_size: Maximum number of metrics to keep in history
            enabled: Enable/disable tracking
        """
        self.window_size = window_size
        self.enabled = enabled
        self.history: List[PerformanceMetrics] = []

    def track(self, result: Dict[str, Any], mode: PipelineMode) -> None:
        """
        Track pipeline performance metrics.

        WHY: Performance tracking enables comparing modes, identifying
        regressions, and optimizing configuration.

        Args:
            result: Execution result
            mode: Execution mode used
        """
        # Guard clause: check if tracking enabled
        if not self.enabled:
            return

        # Extract metrics
        metrics = PerformanceMetrics(
            timestamp=datetime.now().isoformat(),
            mode=mode.value,
            status=result.get("status", "unknown"),
            execution_time=result.get("execution_time", 0),
            stages_executed=len(result.get("results", {})),
            success_rate=self._calculate_success_rate(result),
            dynamic_stats=result.get("dynamic_stats"),
            two_pass_stats=result.get("two_pass_stats")
        )

        # Store metrics (keep last N)
        self.history.append(metrics)

        # Trim history to window size
        if len(self.history) > self.window_size:
            self.history = self.history[-self.window_size:]

    def get_summary(self) -> Dict[str, Any]:
        """
        Get performance summary across recent executions.

        WHY: Provides aggregate metrics for evaluating advanced features impact.

        Returns:
            Dict with performance summary:
                - total_executions: Total pipeline runs
                - success_rate: Overall success rate
                - avg_execution_time: Average execution time
                - mode_distribution: Count of each mode used
        """
        # Guard clause: no performance history
        if not self.history:
            return {
                "total_executions": 0,
                "message": "No performance data available"
            }

        total = len(self.history)
        successful = sum(1 for m in self.history if m.status == "success")

        # Calculate average execution time
        avg_time = sum(m.execution_time for m in self.history) / total

        # Count mode distribution
        mode_counts = {}
        for metrics in self.history:
            mode = metrics.mode
            mode_counts[mode] = mode_counts.get(mode, 0) + 1

        return {
            "total_executions": total,
            "success_rate": successful / total,
            "avg_execution_time": avg_time,
            "mode_distribution": mode_counts,
            "window_size": self.window_size
        }

    def _calculate_success_rate(self, result: Dict[str, Any]) -> float:
        """
        Calculate success rate from execution result.

        Args:
            result: Execution result

        Returns:
            Success rate (0.0 to 1.0)
        """
        results = result.get("results", {})

        # Guard clause: no results
        if not results:
            return 0.0

        successful = sum(
            1 for r in results.values()
            if isinstance(r, dict) and r.get("status") == "success"
        )

        return successful / len(results)
