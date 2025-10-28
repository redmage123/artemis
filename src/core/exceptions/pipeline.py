#!/usr/bin/env python3
"""
Module: core/exceptions/pipeline.py

WHY: Centralizes all pipeline orchestration and configuration exceptions.
     Pipeline errors are critical system failures that affect entire workflow.
     This module isolates orchestration concerns for better error recovery.

RESPONSIBILITY: Define pipeline-specific exception types for stages, validation,
                and configuration. Single Responsibility - pipeline orchestration.

PATTERNS: Exception Hierarchy Pattern, Configuration Validation Pattern
          - Hierarchy: Base PipelineException with specific subtypes
          - Configuration: Separate config errors for fail-fast validation

Integration: Used by artemis_orchestrator.py, dynamic_pipeline.py, stage implementations,
             and any component that manages pipeline execution and configuration.

Design Decision: Why separate pipeline from stage exceptions?
    Pipeline errors (orchestration, config) need different handling than
    stage errors (execution). Separate module enables pipeline-specific recovery.
"""

from core.exceptions.base import ArtemisException


class PipelineException(ArtemisException):
    """
    Base exception for pipeline orchestration errors.

    WHY: Pipelines orchestrate multiple stages (analysis, development, testing).
         Enables catching all pipeline errors for centralized error recovery.

    RESPONSIBILITY: Base class for pipeline stage, validation, and config errors.

    PATTERNS: Exception Hierarchy - specific subtypes inherit from this

    Use case:
        try:
            pipeline.execute()
        except PipelineException as e:  # Catches all pipeline errors
            log_pipeline_failure(e)
            rollback()
    """
    pass


class PipelineStageError(PipelineException):
    """
    Error during pipeline stage execution.

    WHY: Stage errors indicate specific stage failed (architecture, development).
         Enables stage-specific error recovery (retry stage, skip stage, fail).

    Example context:
        {"stage": "architecture", "card_id": "TASK-001", "duration_sec": 45,
         "error_type": "LLMTimeout", "retry_count": 2}
    """
    pass


class PipelineValidationError(PipelineException):
    """
    Pipeline validation failed (missing dependencies, etc.).

    WHY: Validation errors indicate pipeline prerequisites not met. Must fail
         fast before execution starts. Different from runtime stage errors.

    PATTERNS: Fail Fast Pattern - validate before execution, not during

    Example context:
        {"missing_dependencies": ["kanban_board", "requirements"],
         "required_stages": ["project_analysis", "architecture"],
         "available_stages": ["project_analysis"]}
    """
    pass


class PipelineConfigurationError(PipelineException):
    """
    Pipeline configuration error (missing env vars, invalid config, etc.).

    WHY: Configuration errors indicate setup issue. Must fail fast with clear
         message about missing config. Different from runtime errors.

    PATTERNS: Fail Fast Pattern - validate config at startup, not during execution

    Example context:
        {"missing_env_vars": ["OPENAI_API_KEY", "REDIS_HOST"],
         "invalid_config": ["max_workers=-1"], "config_file": "/path/to/config.yaml"}
    """
    pass


class ConfigurationError(ArtemisException):
    """
    Base exception for general configuration errors (API keys, env vars, etc.).

    WHY: Generic configuration errors not specific to pipeline. Enables
         catching all config errors across system (LLM keys, database URLs).

    RESPONSIBILITY: Base class for all configuration validation errors.

    Use case:
        try:
            validate_config()
        except ConfigurationError as e:  # Catches all config errors
            display_setup_instructions()
    """
    pass
