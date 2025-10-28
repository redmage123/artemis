#!/usr/bin/env python3
"""
WHY: Define base validator interface
RESPONSIBILITY: Provide abstract base for artifact validators
PATTERNS: Template Method (abstract validation interface)

Base validator ensures consistent validation API across artifact types.
"""

from abc import ABC, abstractmethod
from typing import Dict
from pathlib import Path
from artifacts.quality.models import ValidationResult


class ArtifactQualityValidator(ABC):
    """
    Base class for artifact quality validators.

    WHY: Different artifact types need type-specific validation.
    RESPONSIBILITY: Define validation interface, store quality criteria.
    PATTERNS: Template Method (abstract methods), Strategy (pluggable validators).
    """

    def __init__(self, quality_criteria: Dict, logger=None):
        """
        Initialize validator.

        Args:
            quality_criteria: Quality criteria for validation
            logger: Optional logger instance
        """
        self.quality_criteria = quality_criteria
        self.logger = logger

    @abstractmethod
    def validate(self, artifact_path: Path) -> ValidationResult:
        """
        Validate artifact against quality criteria.

        WHY: Each artifact type requires specialized validation logic.

        Args:
            artifact_path: Path to artifact to validate

        Returns:
            ValidationResult with pass/fail, score, and feedback
        """
        pass

    @abstractmethod
    def generate_validation_prompt(self, requirements: str) -> str:
        """
        Generate LLM prompt for creating the artifact.

        WHY: Prompt quality directly affects artifact quality.

        Args:
            requirements: User requirements for artifact

        Returns:
            Comprehensive prompt including quality criteria
        """
        pass
