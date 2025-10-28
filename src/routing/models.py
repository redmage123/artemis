#!/usr/bin/env python3
"""
WHY: Data models for intelligent routing decisions and task requirements analysis.

RESPONSIBILITY:
- Define routing decision enumerations
- Define task requirements structure
- Define complete routing decision structure
- Provide type-safe data containers for routing logic

PATTERNS:
- Dataclass Pattern: Immutable data containers with type hints
- Enum Pattern: Type-safe decision states
- Value Object Pattern: Self-contained data structures
"""

from typing import Dict
from dataclasses import dataclass
from enum import Enum


class StageDecision(Enum):
    """
    WHY: Type-safe enumeration of routing decisions for pipeline stages.

    RESPONSIBILITY: Define all possible stage execution states.
    """
    REQUIRED = "required"       # Stage must run
    OPTIONAL = "optional"       # Stage can run but not critical
    SKIP = "skip"              # Stage should be skipped
    CONDITIONAL = "conditional" # Stage depends on previous results


@dataclass
class TaskRequirements:
    """
    WHY: Structured container for analyzed task requirements.

    RESPONSIBILITY:
    - Store detected technical requirements (frontend, backend, database, etc.)
    - Store task metadata (complexity, type, story points)
    - Store resource allocation recommendations
    - Provide confidence score for analysis quality

    PATTERNS: Value Object - immutable data structure with clear semantics
    """
    has_frontend: bool
    has_backend: bool
    has_api: bool
    has_database: bool
    has_external_dependencies: bool
    has_ui_components: bool
    has_accessibility_requirements: bool
    requires_notebook: bool  # True if task needs Jupyter notebook generation
    complexity: str  # 'simple', 'medium', 'complex'
    task_type: str   # 'feature', 'bugfix', 'refactor', 'documentation', 'test'
    estimated_story_points: int
    requires_architecture_review: bool
    requires_project_review: bool
    parallel_developers_recommended: int
    confidence_score: float


@dataclass
class RoutingDecision:
    """
    WHY: Complete routing decision package for a task.

    RESPONSIBILITY:
    - Bundle task metadata with routing analysis
    - Store per-stage decisions
    - Provide filtered stage lists (run vs skip)
    - Include reasoning and confidence metrics

    PATTERNS: Value Object + Aggregate Pattern - groups related decision data
    """
    task_id: str
    task_title: str
    requirements: TaskRequirements
    stage_decisions: Dict[str, StageDecision]
    stages_to_run: list[str]
    stages_to_skip: list[str]
    reasoning: str
    confidence_score: float
