"""
Module: agents/developer/models.py

WHY: Data models and enums for developer agent workflows.
RESPONSIBILITY: Define workflow types, task types, and execution strategies.
PATTERNS: Value Object Pattern, Enum Pattern.

This module contains:
- Workflow type enums (TDD, Quality-Driven)
- Task type enums (Notebook, Code, HTML)
- Execution strategy enums
- Data structures for workflow results

EXTRACTED FROM: standalone_developer_agent.py (implicit data structures)
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional


class WorkflowType(Enum):
    """Developer workflow types"""
    TDD = "tdd"
    QUALITY_DRIVEN = "quality_driven"


class TaskType(Enum):
    """Task types for detection"""
    NOTEBOOK = "notebook"
    CODE = "code"
    HTML = "html"
    PRESENTATION = "presentation"
    UNKNOWN = "unknown"


class ExecutionStrategy(Enum):
    """Execution strategies for developer agent"""
    RED_GREEN_REFACTOR = "red_green_refactor"
    QUALITY_FIRST = "quality_first"
    FAST_ITERATION = "fast_iteration"


@dataclass
class WorkflowContext:
    """Context for workflow execution"""
    task_title: str
    task_description: str
    adr_content: str
    output_dir: str
    developer_prompt: str
    rag_examples: Optional[str] = None
    kg_context: Optional[Dict] = None
    code_review_feedback: Optional[str] = None
    refactoring_instructions: Optional[str] = None


@dataclass
class PhaseResult:
    """Result from a TDD phase (Red/Green/Refactor)"""
    files: List[Dict]
    test_results: Dict
    status: str
    phase_name: str


__all__ = [
    "WorkflowType",
    "TaskType",
    "ExecutionStrategy",
    "WorkflowContext",
    "PhaseResult",
]
