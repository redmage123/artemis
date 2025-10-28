#!/usr/bin/env python3
"""
Retrospective Data Models

WHY: Encapsulate retrospective data structures
RESPONSIBILITY: Define data models for retrospective items, metrics, and reports
PATTERNS: Dataclass, Immutable Parameter Object, Derived Properties
"""

from dataclasses import dataclass, asdict
from typing import List, Optional


@dataclass
class RetrospectiveItem:
    """
    Single retrospective observation

    WHY: Represent individual feedback items
    RESPONSIBILITY: Store categorized retrospective observations
    PATTERNS: Dataclass for immutability and clarity
    """
    category: str  # "what_went_well", "what_didnt", "action_items"
    description: str
    impact: str  # "high", "medium", "low"
    frequency: str  # "recurring", "one-time"
    suggested_action: Optional[str] = None


@dataclass
class SprintMetrics:
    """
    Sprint performance metrics

    WHY: Quantify sprint execution
    RESPONSIBILITY: Store measurable sprint performance data
    PATTERNS: Dataclass for structured metrics
    """
    sprint_number: int
    planned_story_points: int
    completed_story_points: int
    velocity: float  # Percentage of planned work completed
    bugs_found: int
    bugs_fixed: int
    tests_passing: float  # Percentage
    code_review_iterations: int
    average_task_duration_hours: float
    blockers_encountered: int


@dataclass
class RetrospectiveReport:
    """
    Complete sprint retrospective

    WHY: Aggregate all retrospective findings
    RESPONSIBILITY: Provide comprehensive sprint analysis report
    PATTERNS: Dataclass aggregate root
    """
    sprint_number: int
    sprint_start_date: str
    sprint_end_date: str
    metrics: SprintMetrics
    what_went_well: List[RetrospectiveItem]
    what_didnt_go_well: List[RetrospectiveItem]
    action_items: List[RetrospectiveItem]
    key_learnings: List[str]
    velocity_trend: str  # "improving", "declining", "stable"
    overall_health: str  # "healthy", "needs_attention", "critical"
    recommendations: List[str]


@dataclass(frozen=True)
class RetrospectiveContext:
    """
    Parameter Object: Encapsulates retrospective analysis context

    WHY: Reduce parameter count and improve encapsulation
    RESPONSIBILITY: Bundle related retrospective data
    PATTERNS: Parameter Object, Immutable (frozen), Derived Properties

    Benefits:
    - Reduces method parameter count (4+ → 1)
    - Makes dependencies explicit
    - Easy to extend with new data
    - Immutable (frozen)
    - Self-documenting
    """
    metrics: SprintMetrics
    action_items: List[RetrospectiveItem]
    velocity_trend: str
    overall_health: str
    what_went_well: List[RetrospectiveItem]
    what_didnt_go_well: List[RetrospectiveItem]

    @property
    def high_priority_actions(self) -> List[RetrospectiveItem]:
        """
        Derived property: Filter high priority action items

        WHY: Avoid duplicate filtering logic
        RESPONSIBILITY: Provide filtered view of high-priority actions
        """
        return [a for a in self.action_items if a.impact == "high"]

    @property
    def recurring_issues(self) -> List[RetrospectiveItem]:
        """
        Derived property: Filter recurring issues

        WHY: Identify systemic problems
        RESPONSIBILITY: Provide filtered view of recurring problems
        """
        return [a for a in self.what_didnt_go_well if a.frequency == "recurring"]

    @property
    def is_healthy(self) -> bool:
        """
        Derived property: Check if sprint is healthy

        WHY: Simplify health checks
        RESPONSIBILITY: Provide boolean health status
        """
        return self.overall_health == "healthy"

    @property
    def needs_immediate_attention(self) -> bool:
        """
        Derived property: Check if critical issues exist

        WHY: Identify urgent situations
        RESPONSIBILITY: Flag critical states requiring immediate action
        """
        return self.overall_health == "critical" or len(self.high_priority_actions) > 3
