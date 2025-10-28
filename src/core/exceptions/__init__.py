#!/usr/bin/env python3
"""
Module: core/exceptions/__init__.py

WHY: Provides clean public API facade for exception package. Enables backward
     compatibility by re-exporting all exceptions from modular structure.
     Single import point hides internal organization from consumers.

RESPONSIBILITY: Re-export all exception types and utilities from submodules.
                Maintain 100% backward compatibility with original exceptions.py.

PATTERNS: Facade Pattern, Namespace Management Pattern
          - Facade: Simple interface hiding complex module structure
          - Namespace: Single import point (from core.exceptions import X)

Integration: ALL Artemis modules import exceptions from this facade. Changes to
             internal structure are transparent to consumers. Backward compatible.

Design Decision: Why facade pattern?
    1. Backward compatibility - existing imports continue working
    2. Clean API - users don't need to know internal structure
    3. Flexibility - can reorganize modules without breaking imports
    4. Single source of truth - all exports in one place

Usage:
    # Old style (still works):
    from core.exceptions import RAGException, LLMAPIError, wrap_exception

    # New style (also works):
    from core.exceptions.database import RAGException
    from core.exceptions.llm import LLMAPIError
    from core.exceptions.utilities import wrap_exception
"""

# Base exception - foundation for all Artemis exceptions
from core.exceptions.base import ArtemisException

# Database exceptions (RAG, Redis, Knowledge Graph)
from core.exceptions.database import (
    RAGException,
    RAGError,  # Alias for compatibility
    RAGQueryError,
    RAGStorageError,
    RAGConnectionError,
    RedisException,
    RedisConnectionError,
    RedisCacheError,
    KnowledgeGraphError,
    KGQueryError,
    KGConnectionError,
)

# LLM/API exceptions
from core.exceptions.llm import (
    LLMException,
    LLMError,  # Alias for compatibility
    LLMClientError,
    LLMAPIError,
    LLMResponseParsingError,
    LLMRateLimitError,
    LLMAuthenticationError,
)

# Agent exceptions (Developer, Code Review)
from core.exceptions.agents import (
    DeveloperException,
    DeveloperExecutionError,
    DeveloperPromptError,
    DeveloperOutputError,
    CodeReviewException,
    CodeReviewExecutionError,
    CodeReviewScoringError,
    CodeReviewFeedbackError,
)

# Parsing exceptions (Requirements, Documents)
from core.exceptions.parsing import (
    RequirementsException,
    RequirementsFileError,
    RequirementsParsingError,
    RequirementsValidationError,
    RequirementsExportError,
    UnsupportedDocumentFormatError,
    DocumentReadError,
)

# Pipeline exceptions (Orchestration, Configuration)
from core.exceptions.pipeline import (
    PipelineException,
    PipelineStageError,
    PipelineValidationError,
    PipelineConfigurationError,
    ConfigurationError,
)

# Workflow exceptions (Kanban, Sprint, Project Management)
from core.exceptions.workflow import (
    KanbanException,
    KanbanCardNotFoundError,
    KanbanBoardError,
    KanbanWIPLimitError,
    SprintException,
    SprintPlanningError,
    FeatureExtractionError,
    PlanningPokerError,
    SprintAllocationError,
    ProjectReviewError,
    RetrospectiveError,
    UIUXEvaluationError,
    WCAGEvaluationError,
    GDPREvaluationError,
)

# File system exceptions
from core.exceptions.filesystem import (
    ArtemisFileError,
    FileNotFoundError,
    FileWriteError,
    FileReadError,
)

# Analysis exceptions (ADR, Dependencies)
from core.exceptions.analysis import (
    ProjectAnalysisException,
    ADRGenerationError,
    DependencyAnalysisError,
)

# Utility functions and decorators
from core.exceptions.utilities import (
    create_wrapped_exception,
    wrap_exception,
)

# Define __all__ for explicit public API
__all__ = [
    # Base
    "ArtemisException",

    # Database
    "RAGException",
    "RAGError",
    "RAGQueryError",
    "RAGStorageError",
    "RAGConnectionError",
    "RedisException",
    "RedisConnectionError",
    "RedisCacheError",
    "KnowledgeGraphError",
    "KGQueryError",
    "KGConnectionError",

    # LLM
    "LLMException",
    "LLMError",
    "LLMClientError",
    "LLMAPIError",
    "LLMResponseParsingError",
    "LLMRateLimitError",
    "LLMAuthenticationError",

    # Agents
    "DeveloperException",
    "DeveloperExecutionError",
    "DeveloperPromptError",
    "DeveloperOutputError",
    "CodeReviewException",
    "CodeReviewExecutionError",
    "CodeReviewScoringError",
    "CodeReviewFeedbackError",

    # Parsing
    "RequirementsException",
    "RequirementsFileError",
    "RequirementsParsingError",
    "RequirementsValidationError",
    "RequirementsExportError",
    "UnsupportedDocumentFormatError",
    "DocumentReadError",

    # Pipeline
    "PipelineException",
    "PipelineStageError",
    "PipelineValidationError",
    "PipelineConfigurationError",
    "ConfigurationError",

    # Workflow
    "KanbanException",
    "KanbanCardNotFoundError",
    "KanbanBoardError",
    "KanbanWIPLimitError",
    "SprintException",
    "SprintPlanningError",
    "FeatureExtractionError",
    "PlanningPokerError",
    "SprintAllocationError",
    "ProjectReviewError",
    "RetrospectiveError",
    "UIUXEvaluationError",
    "WCAGEvaluationError",
    "GDPREvaluationError",

    # Filesystem
    "ArtemisFileError",
    "FileNotFoundError",
    "FileWriteError",
    "FileReadError",

    # Analysis
    "ProjectAnalysisException",
    "ADRGenerationError",
    "DependencyAnalysisError",

    # Utilities
    "create_wrapped_exception",
    "wrap_exception",
]
