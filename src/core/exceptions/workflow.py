#!/usr/bin/env python3
"""
Module: core/exceptions/workflow.py

WHY: Centralizes all workflow-related exceptions (Kanban, Sprint, Project Management).
     Workflows manage tasks, sprints, and project progression. This module
     isolates workflow concerns from pipeline execution.

RESPONSIBILITY: Define workflow-specific exception types for Kanban, sprints,
                planning, and project management. Single Responsibility - workflow only.

PATTERNS: Exception Hierarchy Pattern, Workflow Category Pattern
          - Hierarchy: Base classes (KanbanException, SprintException)
          - Category: Group by workflow type (task management, sprint planning)

Integration: Used by kanban_manager.py, artemis_workflows.py, sprint planning stages,
             retrospective agents, and UI/UX evaluation components.

Design Decision: Why separate workflow from pipeline exceptions?
    Workflow errors (card not found, WIP limit) are management concerns,
    not execution failures. Different recovery strategies needed.
"""

from core.exceptions.base import ArtemisException


# ============================================================================
# KANBAN / TASK MANAGEMENT EXCEPTIONS
# ============================================================================

class KanbanException(ArtemisException):
    """
    Base exception for Kanban board errors.

    WHY: Kanban boards track task status, WIP limits, and card lifecycle.
         Enables catching all Kanban errors for workflow recovery.

    RESPONSIBILITY: Base class for Kanban card, board, and WIP limit errors.

    Use case:
        try:
            board.move_card(card_id, "done")
        except KanbanException as e:  # Catches all Kanban errors
            log_workflow_issue(e)
    """
    pass


class KanbanCardNotFoundError(KanbanException):
    """
    Kanban card not found.

    WHY: Card not found indicates invalid card_id or deleted card. Must fail
         fast with clear message. Different from board errors.

    Example context:
        {"card_id": "TASK-999", "board": "main_board",
         "available_cards": ["TASK-001", "TASK-002"]}
    """
    pass


class KanbanBoardError(KanbanException):
    """
    Error loading or saving Kanban board.

    WHY: Board errors indicate file system issues, corruption, or serialization
         problems. Different from card-specific errors.

    Example context:
        {"board_path": "/path/to/board.json", "operation": "save",
         "error": "PermissionError", "card_count": 25}
    """
    pass


class KanbanWIPLimitError(KanbanException):
    """
    WIP (Work In Progress) limit exceeded.

    WHY: WIP limit errors enforce workflow discipline. Must prevent card
         movement, not fail silently. Different from other board errors.

    PATTERNS: Validation Pattern - enforce constraints before state change

    Example context:
        {"column": "in_progress", "current_wip": 5, "wip_limit": 5,
         "attempted_card": "TASK-010"}
    """
    pass


# ============================================================================
# SPRINT WORKFLOW EXCEPTIONS
# ============================================================================

class SprintException(ArtemisException):
    """
    Base exception for sprint workflow errors.

    WHY: Sprints manage feature planning, estimation, and allocation.
         Enables catching all sprint errors for workflow recovery.

    RESPONSIBILITY: Base class for sprint planning, estimation, and allocation errors.

    Use case:
        try:
            sprint.plan_features()
        except SprintException as e:  # Catches all sprint errors
            reschedule_planning()
    """
    pass


class SprintPlanningError(SprintException):
    """
    Error during sprint planning.

    WHY: Planning errors indicate issues extracting or organizing features.
         Different from estimation or allocation errors.

    Example context:
        {"sprint_number": 1, "feature_count": 10, "planning_stage": "feature_extraction",
         "error_type": "RequirementsParsingError"}
    """
    pass


class FeatureExtractionError(SprintException):
    """
    Error extracting or parsing features.

    WHY: Feature extraction errors indicate parsing issues with requirements
         or LLM response. Different from planning or estimation errors.

    Example context:
        {"requirements_file": "/path/to/requirements.pdf", "extracted_count": 5,
         "expected_format": "json", "parser_error": "JSONDecodeError"}
    """
    pass


class PlanningPokerError(SprintException):
    """
    Error during Planning Poker estimation.

    WHY: Estimation errors indicate issues with multi-agent consensus or
         LLM failures. Different from feature extraction or allocation.

    Example context:
        {"feature": "User authentication", "agents": ["dev-a", "dev-b", "dev-c"],
         "estimates": [5, 8], "consensus": False}
    """
    pass


class SprintAllocationError(SprintException):
    """
    Error allocating features to sprints.

    WHY: Allocation errors indicate capacity issues or invalid allocations.
         Different from planning or estimation errors.

    Example context:
        {"sprint_capacity": 40, "total_story_points": 65, "feature_count": 15,
         "allocation_strategy": "priority_based"}
    """
    pass


class ProjectReviewError(SprintException):
    """
    Error during project review.

    WHY: Project review errors indicate issues analyzing completed work or
         generating review reports. Different from sprint planning errors.

    Example context:
        {"project": "artemis", "review_stage": "retrospective",
         "completed_features": 8, "error_type": "AnalysisTimeout"}
    """
    pass


class RetrospectiveError(SprintException):
    """
    Error during sprint retrospective.

    WHY: Retrospective errors indicate issues analyzing sprint performance or
         generating improvement recommendations. Different from planning.

    Example context:
        {"sprint_number": 1, "retrospective_type": "automated",
         "analysis_dimensions": ["velocity", "quality"], "error": "DataMissing"}
    """
    pass


class UIUXEvaluationError(SprintException):
    """
    Error during UI/UX evaluation.

    WHY: UI/UX evaluation errors indicate issues with accessibility or
         compliance checks. Different from code review or testing errors.

    RESPONSIBILITY: Base class for WCAG and GDPR evaluation errors.

    Use case:
        try:
            evaluate_uiux()
        except UIUXEvaluationError as e:  # Catches all UI/UX errors
            skip_uiux_evaluation()
    """
    pass


class WCAGEvaluationError(UIUXEvaluationError):
    """
    Error during WCAG accessibility evaluation.

    WHY: WCAG errors indicate accessibility check failures. Must be specific
         for compliance reporting and remediation tracking.

    Example context:
        {"wcag_level": "AA", "page_url": "/dashboard", "violations": 5,
         "checker": "axe-core", "error": "CheckerTimeout"}
    """
    pass


class GDPREvaluationError(UIUXEvaluationError):
    """
    Error during GDPR compliance evaluation.

    WHY: GDPR errors indicate privacy/compliance check failures. Must be
         specific for legal compliance tracking and audit trail.

    Example context:
        {"evaluation_type": "data_processing", "violations": ["missing_consent"],
         "pages_checked": 10, "error": "AnalysisFailed"}
    """
    pass
