#!/usr/bin/env python3
"""
Module: core/exceptions/analysis.py

WHY: Centralizes all project analysis related exceptions (ADR generation,
     dependency analysis). Analysis components examine project structure and
     generate architectural documentation. This module isolates analysis concerns.

RESPONSIBILITY: Define analysis-specific exception types for ADR generation
                and dependency analysis. Single Responsibility - project analysis.

PATTERNS: Exception Hierarchy Pattern, Analysis Type Pattern
          - Hierarchy: Base ProjectAnalysisException with specific subtypes
          - Type: By analysis operation (ADR, dependencies)

Integration: Used by project_analysis_agent.py, adr_generator.py, dependency
             analyzers, and any component that performs project structure analysis.

Design Decision: Why separate analysis from other exceptions?
    Analysis errors are architectural concerns (ADRs, dependencies), not
    execution failures. Different recovery strategies (regenerate vs skip).
"""

from core.exceptions.base import ArtemisException


class ProjectAnalysisException(ArtemisException):
    """
    Base exception for project analysis errors.

    WHY: Project analysis examines code structure, dependencies, and architecture.
         Enables catching all analysis errors for centralized recovery.

    RESPONSIBILITY: Base class for ADR generation and dependency analysis errors.

    PATTERNS: Exception Hierarchy - specific analysis types inherit from this

    Use case:
        try:
            analyze_project()
        except ProjectAnalysisException as e:  # Catches all analysis errors
            use_default_architecture()
    """
    pass


class ADRGenerationError(ProjectAnalysisException):
    """
    Error generating ADR (Architectural Decision Record).

    WHY: ADR generation errors indicate issues creating architectural
         documentation. May be LLM error, template issue, or data missing.

    Example context:
        {"adr_id": "ADR-001", "decision": "Use microservices architecture",
         "template": "adr-template.md", "error_type": "TemplateMissing"}
    """
    pass


class DependencyAnalysisError(ProjectAnalysisException):
    """
    Error analyzing project dependencies.

    WHY: Dependency analysis errors indicate issues parsing package files,
         resolving versions, or detecting conflicts. Different from ADR errors.

    Example context:
        {"package_file": "requirements.txt", "total_dependencies": 50,
         "unresolved": ["package-xyz==1.2.3"], "conflict_count": 2}
    """
    pass
