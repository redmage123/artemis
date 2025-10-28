#!/usr/bin/env python3
"""
WHY: Validators package for continuous code validation.

RESPONSIBILITY: Provide modular validation system for code generation with
multi-stage validation, result aggregation, and pipeline execution.

PATTERNS:
- Chain of Responsibility for validation stages
- Registry pattern for validator management
- Dispatch table for stage routing

Package Structure:
    models.py - Data models and enums
    validator_base.py - Base validator interface
    stage_validators.py - Concrete stage validators
    validator_registry.py - Validator registry and factory
    pipeline_executor.py - Pipeline execution orchestration
    result_aggregator.py - Result analysis and reporting

Usage:
    from validators import ValidationPipeline, ValidationStage, validate_python_code

    # Quick validation
    result = validate_python_code(code, strict=True)

    # Pipeline validation
    pipeline = ValidationPipeline(llm_client=llm, logger=logger)
    result = pipeline.validate_stage(code, ValidationStage.IMPORTS)

    # Summary and analysis
    summary = pipeline.get_validation_summary()
"""

# Core models and enums
from .models import (
    ValidationStage,
    ValidationSeverity,
    StageValidationResult,
    ValidationContext,
    ValidationSummary
)

# Base validator
from .validator_base import (
    BaseValidator,
    ValidatorHelper
)

# Concrete validators
from .stage_validators import (
    ImportsValidator,
    SignatureValidator,
    DocstringValidator,
    BodyValidator,
    TestsValidator,
    FullCodeValidator
)

# Registry and factory
from .validator_registry import (
    ValidatorRegistry,
    ValidatorFactory,
    get_default_registry,
    reset_default_registry
)

# Pipeline execution
from .pipeline_executor import PipelineExecutor

# Result aggregation
from .result_aggregator import (
    ResultAggregator,
    ValidationMetrics
)

# Main pipeline interface (for backward compatibility and convenience)
from .validation_pipeline import (
    ValidationPipeline,
    validate_python_code,
    validate_incrementally
)


__all__ = [
    # Models
    'ValidationStage',
    'ValidationSeverity',
    'StageValidationResult',
    'ValidationContext',
    'ValidationSummary',

    # Base classes
    'BaseValidator',
    'ValidatorHelper',

    # Validators
    'ImportsValidator',
    'SignatureValidator',
    'DocstringValidator',
    'BodyValidator',
    'TestsValidator',
    'FullCodeValidator',

    # Registry
    'ValidatorRegistry',
    'ValidatorFactory',
    'get_default_registry',
    'reset_default_registry',

    # Pipeline
    'PipelineExecutor',
    'ValidationPipeline',

    # Aggregation
    'ResultAggregator',
    'ValidationMetrics',

    # Convenience functions
    'validate_python_code',
    'validate_incrementally',
]


__version__ = '1.0.0'
__author__ = 'Artemis Development Pipeline'
