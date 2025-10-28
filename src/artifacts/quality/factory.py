#!/usr/bin/env python3
"""
WHY: Create appropriate validator based on artifact type
RESPONSIBILITY: Factory for validator instantiation
PATTERNS: Factory (object creation), Dispatch table (validator mapping)

Factory enables dynamic validator creation based on type string.
"""

from typing import Dict
from artifacts.quality.base import ArtifactQualityValidator
from artifacts.quality.notebook_validator import NotebookQualityValidator
from artifacts.quality.code_validator import CodeQualityValidator
from artifacts.quality.ui_validator import UIQualityValidator


# Dispatch table: validator name -> validator class
VALIDATOR_REGISTRY: Dict[str, type] = {
    'NotebookQualityValidator': NotebookQualityValidator,
    'CodeQualityValidator': CodeQualityValidator,
    'UIQualityValidator': UIQualityValidator,
}


def create_validator(
    validator_class: str,
    quality_criteria: Dict,
    logger=None
) -> ArtifactQualityValidator:
    """
    Factory to create appropriate validator.

    WHY: Dynamic validator creation based on artifact type.
    PATTERNS: Factory pattern, Dispatch table (no if/elif chain).

    Args:
        validator_class: Validator class name (e.g., 'NotebookQualityValidator')
        quality_criteria: Quality criteria for validation
        logger: Optional logger instance

    Returns:
        Instantiated validator

    Raises:
        ValueError: If validator class is unknown

    Example:
        >>> validator = create_validator('NotebookQualityValidator', {...})
        >>> result = validator.validate(Path('notebook.ipynb'))
    """
    # Dispatch table lookup (no if/elif chain)
    validator_cls = VALIDATOR_REGISTRY.get(validator_class)

    # Guard clause - unknown validator
    if not validator_cls:
        raise ValueError(f"Unknown validator: {validator_class}")

    return validator_cls(quality_criteria, logger)
