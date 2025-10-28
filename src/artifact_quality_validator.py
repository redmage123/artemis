#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY WRAPPER

This module maintains backward compatibility while the codebase migrates
to the new modular structure in artifacts/quality/.

All functionality has been refactored into:
- artifacts/quality/models.py - ValidationResult value object
- artifacts/quality/base.py - ArtifactQualityValidator abstract base
- artifacts/quality/aggregator.py - Result aggregation logic
- artifacts/quality/notebook_validator.py - NotebookQualityValidator
- artifacts/quality/code_validator.py - CodeQualityValidator
- artifacts/quality/ui_validator.py - UIQualityValidator
- artifacts/quality/factory.py - create_validator factory

To migrate your code:
    OLD: from artifact_quality_validator import NotebookQualityValidator, ValidationResult
    NEW: from artifacts.quality import NotebookQualityValidator, ValidationResult

No breaking changes - all imports remain identical.
"""

# Re-export all public APIs from the modular package
from artifacts.quality import (
    ValidationResult,
    ArtifactQualityValidator,
    NotebookQualityValidator,
    CodeQualityValidator,
    UIQualityValidator,
    create_validator,
)

__all__ = [
    'ValidationResult',
    'ArtifactQualityValidator',
    'NotebookQualityValidator',
    'CodeQualityValidator',
    'UIQualityValidator',
    'create_validator',
]
