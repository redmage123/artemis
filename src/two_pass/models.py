"""
Module: two_pass/models.py

WHY: Data models for two-pass pipeline execution results and state.
RESPONSIBILITY: PassResult, PassDelta, PassMemento data structures.
PATTERNS: Value Object, Memento Pattern, Guard Clauses.

This module handles:
- PassResult: Standardized pass execution results
- PassDelta: Difference detection between passes
- PassMemento: State capture for rollback

EXTRACTED FROM: two_pass_pipeline.py (lines 105-303, 198 lines)
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List
from datetime import datetime
import copy


@dataclass
class PassResult:
    """
    Result of a pipeline pass execution.

    Why needed: Standardized structure for pass outputs, enabling comparison,
    validation, and learning extraction across passes.

    Responsibilities:
    - Store pass execution artifacts and metadata
    - Track quality metrics for comparison
    - Capture learnings and insights
    - Provide serialization for storage
    """
    pass_name: str
    success: bool
    artifacts: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0
    execution_time: float = 0.0
    learnings: List[str] = field(default_factory=list)
    insights: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary for serialization.

        Why needed: Enables storage, logging, and transmission of pass results.
        Used by observers for metrics collection and by memento for state capture.

        Returns:
            Dictionary representation of pass result
        """
        return {
            "pass_name": self.pass_name,
            "success": self.success,
            "artifacts": self.artifacts,
            "quality_score": self.quality_score,
            "execution_time": self.execution_time,
            "learnings": self.learnings,
            "insights": self.insights,
            "errors": self.errors,
            "warnings": self.warnings,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class PassDelta:
    """
    Difference between two pass executions.

    Why needed: Captures what changed between first and second pass, enabling
    learning extraction, quality tracking, and incremental improvement analysis.

    Design pattern: Value Object (immutable after creation)

    Responsibilities:
    - Compare pass results and extract differences
    - Calculate quality improvements/degradations
    - Identify new learnings and insights
    - Track artifact changes
    """
    first_pass: PassResult
    second_pass: PassResult
    quality_delta: float = 0.0
    new_artifacts: List[str] = field(default_factory=list)
    modified_artifacts: List[str] = field(default_factory=list)
    removed_artifacts: List[str] = field(default_factory=list)
    new_learnings: List[str] = field(default_factory=list)
    quality_improved: bool = False
    execution_time_delta: float = 0.0

    def __post_init__(self):
        """
        Calculate delta metrics after initialization.

        Why needed: Automatically computes deltas when PassDelta is created,
        ensuring metrics are always consistent and up-to-date.
        """
        # Calculate quality delta - positive means improvement
        self.quality_delta = self.second_pass.quality_score - self.first_pass.quality_score
        self.quality_improved = self.quality_delta > 0

        # Calculate execution time delta
        self.execution_time_delta = self.second_pass.execution_time - self.first_pass.execution_time

        # Detect artifact changes using sets for O(1) lookups instead of nested loops
        first_artifacts = set(self.first_pass.artifacts.keys())
        second_artifacts = set(self.second_pass.artifacts.keys())

        self.new_artifacts = list(second_artifacts - first_artifacts)
        self.removed_artifacts = list(first_artifacts - second_artifacts)

        # Modified artifacts: present in both but with different values
        common_artifacts = first_artifacts & second_artifacts
        self.modified_artifacts = [
            key for key in common_artifacts
            if self.first_pass.artifacts[key] != self.second_pass.artifacts[key]
        ]

        # Extract new learnings using set difference
        first_learnings = set(self.first_pass.learnings)
        second_learnings = set(self.second_pass.learnings)
        self.new_learnings = list(second_learnings - first_learnings)

    def to_dict(self) -> Dict[str, Any]:
        """Convert delta to dictionary for serialization"""
        return {
            "first_pass": self.first_pass.to_dict(),
            "second_pass": self.second_pass.to_dict(),
            "quality_delta": self.quality_delta,
            "new_artifacts": self.new_artifacts,
            "modified_artifacts": self.modified_artifacts,
            "removed_artifacts": self.removed_artifacts,
            "new_learnings": self.new_learnings,
            "quality_improved": self.quality_improved,
            "execution_time_delta": self.execution_time_delta
        }


@dataclass
class PassMemento:
    """
    Memento for capturing pass state (Memento Pattern).

    Why it exists: Captures complete state of a pipeline pass for restoration
    or analysis. Enables rollback when second pass fails and learning transfer
    from first to second pass.

    Design pattern: Memento Pattern
    Why this design: Provides snapshot of pass state without exposing internal
    structure. Allows state capture/restore without tight coupling between passes.

    Responsibilities:
    - Capture pass state at point in time
    - Store artifacts, learnings, and insights
    - Enable state restoration for rollback
    - Preserve quality metrics for comparison
    - Support deep copy to prevent mutation

    Use cases:
    - Rollback to first pass if second pass fails
    - Transfer learnings from first to second pass
    - Compare states across passes
    - Audit trail of pass evolution
    """
    pass_name: str
    state: Dict[str, Any]
    artifacts: Dict[str, Any]
    learnings: List[str]
    insights: Dict[str, Any]
    quality_score: float
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def create_copy(self) -> 'PassMemento':
        """
        Create deep copy of memento.

        Why needed: Prevents mutation of stored state. When applying memento to
        second pass, we don't want changes to second pass to affect stored state.

        Returns:
            Deep copy of memento

        Design note: Uses copy.deepcopy to recursively copy all nested structures
        """
        return PassMemento(
            pass_name=self.pass_name,
            state=copy.deepcopy(self.state),
            artifacts=copy.deepcopy(self.artifacts),
            learnings=copy.deepcopy(self.learnings),
            insights=copy.deepcopy(self.insights),
            quality_score=self.quality_score,
            timestamp=self.timestamp,
            metadata=copy.deepcopy(self.metadata)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert memento to dictionary for serialization"""
        return {
            "pass_name": self.pass_name,
            "state": self.state,
            "artifacts": self.artifacts,
            "learnings": self.learnings,
            "insights": self.insights,
            "quality_score": self.quality_score,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


__all__ = [
    "PassResult",
    "PassDelta",
    "PassMemento"
]
