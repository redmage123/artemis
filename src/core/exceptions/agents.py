#!/usr/bin/env python3
"""
Module: core/exceptions/agents.py

WHY: Centralizes all agent-related exceptions (developer, code review).
     Agents are autonomous components that execute tasks, review code, and
     generate outputs. This module isolates agent execution concerns.

RESPONSIBILITY: Define agent-specific exception types for execution, prompts,
                outputs, and reviews. Single Responsibility - only agent errors.

PATTERNS: Exception Hierarchy Pattern, Agent Category Pattern
          - Hierarchy: Base classes (DeveloperException, CodeReviewException)
          - Category: Group by agent type (developer vs code review)

Integration: Used by standalone_developer_agent.py, code_review_agent.py,
             code_review_stage.py, and artemis_orchestrator.py for agent management.
"""

from core.exceptions.base import ArtemisException


# ============================================================================
# DEVELOPER AGENT EXCEPTIONS
# ============================================================================

class DeveloperException(ArtemisException):
    """
    Base exception for developer agent errors.

    WHY: Developer agents are autonomous coding agents that generate, test,
         and validate code. Enables catching all developer agent errors.

    RESPONSIBILITY: Base class for developer agent execution, prompts, and outputs.

    Use case:
        try:
            developer.execute(task)
        except DeveloperException as e:  # Catches all developer errors
            reassign_task()
    """
    pass


class DeveloperExecutionError(DeveloperException):
    """
    Error during developer agent execution.

    WHY: Execution errors indicate agent failed to complete task. May be
         code generation failure, test failure, or validation failure.

    Example context:
        {"agent": "developer-a", "task": "TASK-001", "stage": "implementation",
         "error_type": "test_failure", "attempt": 2}
    """
    pass


class DeveloperPromptError(DeveloperException):
    """
    Error building or loading developer prompt.

    WHY: Prompt errors indicate missing templates, invalid variables, or
         template syntax errors. Different from execution errors.

    Example context:
        {"template": "developer_prompt.txt", "missing_vars": ["framework", "requirements"],
         "template_path": "/path/to/templates"}
    """
    pass


class DeveloperOutputError(DeveloperException):
    """
    Error writing developer output files.

    WHY: Output errors indicate file system issues (permissions, disk space)
         or invalid output format. Different from execution or prompt errors.

    Example context:
        {"output_path": "/path/to/output", "file_count": 5, "error": "PermissionError",
         "required_space_mb": 100}
    """
    pass


# ============================================================================
# CODE REVIEW AGENT EXCEPTIONS
# ============================================================================

class CodeReviewException(ArtemisException):
    """
    Base exception for code review errors.

    WHY: Code review agents analyze code quality, provide feedback, and
         calculate scores. Enables catching all code review errors.

    RESPONSIBILITY: Base class for code review execution, scoring, and feedback.

    Use case:
        try:
            review_agent.review(code)
        except CodeReviewException as e:  # Catches all review errors
            skip_review()
    """
    pass


class CodeReviewExecutionError(CodeReviewException):
    """
    Error during code review execution.

    WHY: Execution errors indicate review agent failed to analyze code.
         May be LLM error, parsing error, or analysis timeout.

    Example context:
        {"code_path": "/path/to/code.py", "reviewer": "review-agent-1",
         "analysis_type": "structural", "timeout": 30}
    """
    pass


class CodeReviewScoringError(CodeReviewException):
    """
    Error calculating code review score.

    WHY: Scoring errors indicate metric calculation failed. May be missing
         data, invalid thresholds, or calculation logic error.

    Example context:
        {"metrics": ["complexity", "coverage", "style"], "missing": ["coverage"],
         "code_path": "/path/to/code.py"}
    """
    pass


class CodeReviewFeedbackError(CodeReviewException):
    """
    Error extracting or processing code review feedback.

    WHY: Feedback errors indicate parsing issue with review output. LLM may
         have returned unexpected format or missing required sections.

    Example context:
        {"expected_sections": ["strengths", "issues", "recommendations"],
         "received_sections": ["strengths"], "review_text": "partial..."}
    """
    pass
