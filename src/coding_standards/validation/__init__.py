#!/usr/bin/env python3
"""
WHY: Provide public API for code standards validation
RESPONSIBILITY: Export validation classes
PATTERNS: Facade (simplified package interface)

Validation package provides code quality checking for Artemis pipeline.
"""

from coding_standards.validation.models import ValidationResult
from coding_standards.validation.validator import CodeStandardsValidator

__all__ = [
    'ValidationResult',
    'CodeStandardsValidator',
]
