#!/usr/bin/env python3
"""
Module: models.py

WHY this module exists:
    Defines data structures for advanced pipeline strategy execution results,
    performance metrics, and execution metadata.

RESPONSIBILITY:
    - Define ExecutionResult data structure
    - Define PerformanceMetrics data structure
    - Provide type-safe data containers
    - Enable immutable result objects

PATTERNS:
    - Data Transfer Object (DTO) pattern for result passing
    - Type-safe data structures with validation
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class ExecutionResult:
    """
    Immutable execution result from pipeline execution.

    WHY: Provides type-safe container for execution results with all metadata.
    Immutable to prevent accidental modifications after execution completes.

    PATTERNS: Data Transfer Object (DTO), Immutability pattern
    """

    status: str  # "success" or "failed"
    results: Dict[str, Any]
    mode: str
    execution_time: float
    error: Optional[str] = None
    confidence_scores: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    dynamic_stats: Optional[Dict[str, Any]] = None
    two_pass_stats: Optional[Dict[str, Any]] = None
    mode_features: Optional[list] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary format.

        WHY: Enables serialization and backward compatibility with dict-based APIs.

        Returns:
            Dictionary representation of execution result
        """
        return {
            "status": self.status,
            "results": self.results,
            "mode": self.mode,
            "execution_time": self.execution_time,
            "error": self.error,
            "confidence_scores": self.confidence_scores,
            "performance_metrics": self.performance_metrics,
            "dynamic_stats": self.dynamic_stats,
            "two_pass_stats": self.two_pass_stats,
            "mode_features": self.mode_features
        }


@dataclass
class PerformanceMetrics:
    """
    Performance metrics for pipeline execution.

    WHY: Tracks performance data for optimization and monitoring.

    PATTERNS: Data Transfer Object (DTO)
    """

    timestamp: str
    mode: str
    status: str
    execution_time: float
    stages_executed: int
    success_rate: float
    dynamic_stats: Optional[Dict[str, Any]] = None
    two_pass_stats: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert metrics to dictionary format.

        Returns:
            Dictionary representation of performance metrics
        """
        result = {
            "timestamp": self.timestamp,
            "mode": self.mode,
            "status": self.status,
            "execution_time": self.execution_time,
            "stages_executed": self.stages_executed,
            "success_rate": self.success_rate
        }

        if self.dynamic_stats:
            result["dynamic_stats"] = self.dynamic_stats

        if self.two_pass_stats:
            result["two_pass_stats"] = self.two_pass_stats

        return result
