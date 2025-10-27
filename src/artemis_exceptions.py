#!/usr/bin/env python3
"""
Module: artemis_exceptions.py

Purpose: Defines hierarchical exception types with context preservation for Artemis pipeline
Why: Enables granular error handling, preserves debugging context through exception chains,
     and standardizes error reporting across 50+ modules. Before this module, every
     component used ValueError or generic Exception, making debugging nearly impossible
     and preventing intelligent error recovery (retry transient vs fail permanent).

Patterns: Exception Hierarchy Pattern, Wrapper Pattern (original_exception preservation)
Integration: Foundation used by ALL Artemis modules. Orchestrator uses exception types
            to determine retry strategy. Logging uses types for categorization. Monitoring
            uses types for alerting rules.

Exception Hierarchy:
```
ArtemisException (base with context support)
├── RAGException (RAG database errors)
│   ├── RAGQueryError
│   ├── RAGStorageError
│   └── RAGConnectionError
├── RedisException (Redis cache errors)
│   ├── RedisConnectionError
│   └── RedisCacheError
├── LLMException (LLM service errors)
│   ├── LLMAPIError
│   ├── LLMResponseParsingError
│   ├── LLMRateLimitError (retryable)
│   └── LLMAuthenticationError (permanent)
├── DeveloperException (agent execution errors)
│   ├── DeveloperExecutionError
│   ├── DeveloperPromptError
│   └── DeveloperOutputError
├── CodeReviewException
│   ├── CodeReviewExecutionError
│   ├── CodeReviewScoringError
│   └── CodeReviewFeedbackError
├── RequirementsException (requirements parsing)
│   ├── RequirementsFileError
│   ├── RequirementsParsingError
│   ├── RequirementsValidationError
│   └── UnsupportedDocumentFormatError
├── PipelineException (orchestration errors)
│   ├── PipelineStageError
│   ├── PipelineValidationError
│   └── PipelineConfigurationError
├── KnowledgeGraphError
│   ├── KGQueryError
│   └── KGConnectionError
├── KanbanException (board operations)
│   ├── KanbanCardNotFoundError
│   ├── KanbanBoardError
│   └── KanbanWIPLimitError
├── ArtemisFileError (file I/O)
│   ├── FileNotFoundError
│   ├── FileWriteError
│   └── FileReadError
├── ProjectAnalysisException
│   ├── ADRGenerationError
│   └── DependencyAnalysisError
└── SprintException (workflow errors)
    ├── SprintPlanningError
    ├── FeatureExtractionError
    ├── PlanningPokerError
    └── UIUXEvaluationError
        ├── WCAGEvaluationError
        └── GDPREvaluationError
```

Key Features:
- Context preservation (card_id, stage, file paths in exception metadata)
- Original exception chaining (never lose root cause)
- Hierarchical catching (catch category or specific type)
- Human-readable __str__ with context formatting
- Decorator support (@wrap_exception) for automatic wrapping

Design Decision - Why so many exception types:
Specific exceptions enable:
1. Intelligent retry logic (retry LLMRateLimitError, fail on LLMAuthenticationError)
2. Alerting rules (page on PipelineConfigurationError, log LLMTimeoutError)
3. Error categorization in monitoring (transient vs permanent failures)
4. Granular exception handling (catch LLMException vs all errors)
5. Clear code intent (seeing WCAGEvaluationError immediately tells you what failed)
"""

from typing import Optional, Dict, Any


class ArtemisException(Exception):
    """
    Base exception for all Artemis errors with context preservation

    Why it exists: Provides foundation for entire exception hierarchy. Every Artemis
                   exception inherits from this to enable:
                   1. Catch-all error handling (catch ArtemisException vs Exception)
                   2. Context preservation (metadata attached to every exception)
                   3. Exception chaining (original_exception never lost)
                   4. Consistent error formatting across system

    Design pattern: Base Exception with Context
    Why this design: Adding context and original_exception fields to base class means
                     ALL derived exceptions automatically get these capabilities without
                     reimplementing logic.

    Responsibilities:
    - Store human-readable error message
    - Preserve contextual metadata (card_id, stage, file paths, etc.)
    - Chain original exception (root cause never lost)
    - Format error string with context for logging
    - Provide type-based exception catching

    Use cases:
    - Catch all Artemis errors: except ArtemisException
    - Add context to errors: raise LLMError("API failed", context={"card_id": "001"})
    - Wrap exceptions: raise FileReadError("Read failed", original_exception=e)
    - Debug errors: exception.context shows all metadata, original_exception shows root cause

    Context examples:
    - {"card_id": "TASK-001", "stage": "architecture"}
    - {"file_path": "/path/to/file.py", "operation": "read"}
    - {"llm_model": "gpt-4", "prompt_length": 5000}
    - {"developer": "developer-a", "test_status": "failed"}
    """

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """
        Initialize Artemis exception with message, context, and original exception

        Why needed: Captures all information needed for debugging - the WHAT (message),
                    the WHERE/WHEN (context), and the WHY (original exception).

        Args:
            message: Human-readable error message describing what went wrong
            context: Dictionary with debugging metadata (card_id, stage, file paths, etc.)
                    Automatically included in error string and logging
            original_exception: Original exception if this is wrapping another exception
                               Preserves root cause for debugging stack traces

        Example:
            raise LLMAPIError(
                "Failed to call OpenAI API",
                context={"model": "gpt-4", "timeout": 30, "attempt": 3},
                original_exception=original_api_exception
            )
            # Output: "Failed to call OpenAI API (Context: model=gpt-4, timeout=30, attempt=3)
            #         | Caused by: requests.exceptions.Timeout: Connection timeout"
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}
        self.original_exception = original_exception

    def __str__(self) -> str:
        """
        Format exception as human-readable string with full context

        Why needed: Default Exception.__str__ only shows message. This adds context
                    and original exception for complete debugging picture.

        What it does:
        - Starts with error message
        - Appends context dict as "key=value" pairs if present
        - Appends original exception type and message if present
        - Creates single-line string suitable for logging

        Returns:
            Formatted string: "Message (Context: key1=val1, key2=val2) | Caused by: Type: message"

        Example output:
            "Failed to read file (Context: file_path=/tmp/test.py, operation=read) |
             Caused by: FileNotFoundError: [Errno 2] No such file or directory"
        """
        msg = self.message
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            msg = f"{msg} (Context: {context_str})"
        if self.original_exception:
            msg = f"{msg} | Caused by: {type(self.original_exception).__name__}: {self.original_exception}"
        return msg


# ============================================================================
# DATABASE / RAG EXCEPTIONS
# ============================================================================

class RAGException(ArtemisException):
    """Base exception for RAG-related errors"""
    pass


# Alias for compatibility with AIQueryService
RAGError = RAGException


class RAGQueryError(RAGException):
    """Error querying RAG database"""
    pass


class RAGStorageError(RAGException):
    """Error storing data in RAG database"""
    pass


class RAGConnectionError(RAGException):
    """Error connecting to RAG database (ChromaDB)"""
    pass


# ============================================================================
# REDIS EXCEPTIONS
# ============================================================================

class RedisException(ArtemisException):
    """Base exception for Redis-related errors"""
    pass


class RedisConnectionError(RedisException):
    """Error connecting to Redis"""
    pass


class RedisCacheError(RedisException):
    """Error performing Redis cache operation"""
    pass


# ============================================================================
# LLM / API EXCEPTIONS
# ============================================================================

class LLMException(ArtemisException):
    """Base exception for LLM-related errors"""
    pass


# Alias for compatibility with AIQueryService
LLMError = LLMException


class LLMClientError(LLMException):
    """Error initializing or using LLM client"""
    pass


class LLMAPIError(LLMException):
    """Error calling LLM API (OpenAI, Anthropic, etc.)"""
    pass


class LLMResponseParsingError(LLMException):
    """Error parsing LLM response (invalid JSON, etc.)"""
    pass


class LLMRateLimitError(LLMException):
    """LLM API rate limit exceeded"""
    pass


class LLMAuthenticationError(LLMException):
    """LLM API authentication failed (invalid API key, etc.)"""
    pass


# ============================================================================
# DEVELOPER / EXECUTION EXCEPTIONS
# ============================================================================

class DeveloperException(ArtemisException):
    """Base exception for developer agent errors"""
    pass


class DeveloperExecutionError(DeveloperException):
    """Error during developer agent execution"""
    pass


class DeveloperPromptError(DeveloperException):
    """Error building or loading developer prompt"""
    pass


class DeveloperOutputError(DeveloperException):
    """Error writing developer output files"""
    pass


#============================================================================
# CODE REVIEW EXCEPTIONS
# ============================================================================

class CodeReviewException(ArtemisException):
    """Base exception for code review errors"""
    pass


class CodeReviewExecutionError(CodeReviewException):
    """Error during code review execution"""
    pass


class CodeReviewScoringError(CodeReviewException):
    """Error calculating code review score"""
    pass


class CodeReviewFeedbackError(CodeReviewException):
    """Error extracting or processing code review feedback"""
    pass


# ============================================================================
# REQUIREMENTS PARSING EXCEPTIONS
# ============================================================================

class RequirementsException(ArtemisException):
    """Base exception for requirements parsing errors"""
    pass


class RequirementsFileError(RequirementsException):
    """Error reading requirements file"""
    pass


class RequirementsParsingError(RequirementsException):
    """Error parsing requirements content"""
    pass


class RequirementsValidationError(RequirementsException):
    """Requirements validation failed"""
    pass


class RequirementsExportError(RequirementsException):
    """Error exporting requirements to YAML/JSON"""
    pass


class UnsupportedDocumentFormatError(RequirementsException):
    """Document format not supported"""
    pass


class DocumentReadError(RequirementsException):
    """Error reading document content"""
    pass


# ============================================================================
# PIPELINE / ORCHESTRATION EXCEPTIONS
# ============================================================================

class PipelineException(ArtemisException):
    """Base exception for pipeline orchestration errors"""
    pass


class PipelineStageError(PipelineException):
    """Error during pipeline stage execution"""
    pass


class PipelineValidationError(PipelineException):
    """Pipeline validation failed (missing dependencies, etc.)"""
    pass


class PipelineConfigurationError(PipelineException):
    """Pipeline configuration error (missing env vars, etc.)"""
    pass


class ConfigurationError(ArtemisException):
    """Base exception for configuration errors (API keys, env vars, etc.)"""
    pass


# ============================================================================
# KNOWLEDGE GRAPH EXCEPTIONS
# ============================================================================

class KnowledgeGraphError(ArtemisException):
    """Base class for Knowledge Graph errors"""
    pass


class KGQueryError(KnowledgeGraphError):
    """Error executing Knowledge Graph query"""
    pass


class KGConnectionError(KnowledgeGraphError):
    """Error connecting to Knowledge Graph database"""
    pass


# ============================================================================
# KANBAN / TASK MANAGEMENT EXCEPTIONS
# ============================================================================

class KanbanException(ArtemisException):
    """Base exception for Kanban board errors"""
    pass


class KanbanCardNotFoundError(KanbanException):
    """Kanban card not found"""
    pass


class KanbanBoardError(KanbanException):
    """Error loading or saving Kanban board"""
    pass


class KanbanWIPLimitError(KanbanException):
    """WIP limit exceeded"""
    pass


# ============================================================================
# FILE / IO EXCEPTIONS
# ============================================================================

class ArtemisFileError(ArtemisException):
    """Base exception for file operations"""
    pass


class FileNotFoundError(ArtemisFileError):
    """Required file not found"""
    pass


class FileWriteError(ArtemisFileError):
    """Error writing file"""
    pass


class FileReadError(ArtemisFileError):
    """Error reading file"""
    pass


# ============================================================================
# PROJECT ANALYSIS EXCEPTIONS
# ============================================================================

class ProjectAnalysisException(ArtemisException):
    """Base exception for project analysis errors"""
    pass


class ADRGenerationError(ProjectAnalysisException):
    """Error generating ADR (Architectural Decision Record)"""
    pass


class DependencyAnalysisError(ProjectAnalysisException):
    """Error analyzing project dependencies"""
    pass


# ============================================================================
# SPRINT WORKFLOW EXCEPTIONS
# ============================================================================

class SprintException(ArtemisException):
    """Base exception for sprint workflow errors"""
    pass


class SprintPlanningError(SprintException):
    """Error during sprint planning"""
    pass


class FeatureExtractionError(SprintException):
    """Error extracting or parsing features"""
    pass


class PlanningPokerError(SprintException):
    """Error during Planning Poker estimation"""
    pass


class SprintAllocationError(SprintException):
    """Error allocating features to sprints"""
    pass


class ProjectReviewError(SprintException):
    """Error during project review"""
    pass


class RetrospectiveError(SprintException):
    """Error during sprint retrospective"""
    pass


class UIUXEvaluationError(SprintException):
    """Error during UI/UX evaluation"""
    pass


class WCAGEvaluationError(UIUXEvaluationError):
    """Error during WCAG accessibility evaluation"""
    pass


class GDPREvaluationError(UIUXEvaluationError):
    """Error during GDPR compliance evaluation"""
    pass


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_wrapped_exception(
    exception: Exception,
    artemis_exception_class: type[ArtemisException],
    message: str,
    context: Optional[Dict[str, Any]] = None
) -> ArtemisException:
    """
    Wrap a generic exception in an Artemis-specific exception (utility function)

    Args:
        exception: Original exception
        artemis_exception_class: Artemis exception class to wrap with
        message: Human-readable error message
        context: Additional context

    Returns:
        Wrapped Artemis exception

    Example:
        try:
            some_operation()
        except Exception as e:
            raise create_wrapped_exception(
                e,
                RAGQueryError,
                "Failed to query RAG database",
                {"card_id": "123", "query": "test"}
            )
    """
    return artemis_exception_class(
        message=message,
        context=context,
        original_exception=exception
    )


# Decorator factory version for use with @wrap_exception syntax
def wrap_exception(artemis_exception_class: type[ArtemisException], message: str):
    """
    Decorator to automatically wrap exceptions in Artemis exception types

    Why needed: Eliminates repetitive try-except-wrap boilerplate in every method.
                Instead of 10 lines of exception handling, just add one @decorator.

    Design pattern: Decorator Pattern
    Why this design: Allows adding exception wrapping behavior to functions without
                     modifying their code. Follows DRY principle - write once, apply
                     to many functions.

    What it does:
    - Wraps decorated function in try-except block
    - On exception, wraps in specified Artemis exception type
    - Preserves original exception in original_exception field
    - Adds message prefix to exception
    - Re-raises ArtemisExceptions without wrapping (prevents double-wrapping)

    Args:
        artemis_exception_class: Artemis exception type to wrap with (e.g., PipelineStageError)
        message: Human-readable message prefix (e.g., "Stage execution failed")

    Returns:
        Decorator function that wraps exceptions

    Usage:
        @wrap_exception(PipelineStageError, "Stage execution failed")
        def execute(self, card, context):
            # Any exception here becomes PipelineStageError
            llm_call()  # LLM exception wrapped
            file.read() # IO exception wrapped
            return result

    Without decorator (11 lines):
        def execute(self, card, context):
            try:
                llm_call()
                file.read()
                return result
            except ArtemisException:
                raise  # Don't double-wrap
            except Exception as e:
                raise PipelineStageError(
                    f"Stage execution failed: {e}",
                    original_exception=e
                )

    With decorator (4 lines):
        @wrap_exception(PipelineStageError, "Stage execution failed")
        def execute(self, card, context):
            llm_call()
            file.read()
            return result

    Design note: Doesn't wrap ArtemisExceptions to prevent double-wrapping. If function
                 raises LLMError, that exception passes through unchanged.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ArtemisException:
                # Pattern #10: Early return - don't wrap Artemis exceptions
                raise
            except Exception as e:
                # Wrap non-Artemis exceptions
                raise artemis_exception_class(
                    message=f"{message}: {str(e)}",
                    original_exception=e
                )
        return wrapper
    return decorator
