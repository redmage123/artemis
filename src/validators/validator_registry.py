#!/usr/bin/env python3
"""
WHY: Centralize validator registration and dispatching.

RESPONSIBILITY: Maintain registry of validators and provide dispatch mechanism
using lookup table instead of if/elif chains.

PATTERNS:
- Registry pattern for validator management
- Dispatch table pattern for stage routing
- Factory pattern for validator creation
"""

from typing import Dict, Optional, Callable
from .models import ValidationStage
from .stage_validators import (
    ImportsValidator,
    SignatureValidator,
    DocstringValidator,
    BodyValidator,
    TestsValidator,
    FullCodeValidator
)
from .validator_base import BaseValidator


class ValidatorRegistry:
    """
    WHY: Central registry for all validators using dispatch table pattern.

    RESPONSIBILITY: Map validation stages to their validators and provide
    clean dispatch mechanism without if/elif chains.

    Usage:
        registry = ValidatorRegistry()
        validator = registry.get_validator(ValidationStage.IMPORTS)
        checks, feedback, severity = validator.validate(code, context)
    """

    def __init__(self):
        """Initialize registry with default validators."""
        self._validators: Dict[ValidationStage, BaseValidator] = {}
        self._initialize_default_validators()

    def _initialize_default_validators(self) -> None:
        """
        WHY: Set up default validator mappings.

        Uses dispatch table pattern for O(1) lookup instead of if/elif chains.
        """
        self._validators = {
            ValidationStage.IMPORTS: ImportsValidator(),
            ValidationStage.SIGNATURE: SignatureValidator(),
            ValidationStage.DOCSTRING: DocstringValidator(),
            ValidationStage.BODY: BodyValidator(),
            ValidationStage.TESTS: TestsValidator(),
            ValidationStage.FULL_CODE: FullCodeValidator()
        }

    def register_validator(self, stage: ValidationStage, validator: BaseValidator) -> None:
        """
        WHY: Allow custom validators to override default implementations.

        Args:
            stage: Validation stage to register for
            validator: Validator instance to use
        """
        if not isinstance(validator, BaseValidator):
            raise TypeError(f"Validator must inherit from BaseValidator, got {type(validator)}")

        self._validators[stage] = validator

    def get_validator(self, stage: ValidationStage) -> Optional[BaseValidator]:
        """
        WHY: Retrieve validator for a stage using dispatch table lookup.

        Args:
            stage: Validation stage

        Returns:
            Validator instance or None if not found
        """
        return self._validators.get(stage)

    def has_validator(self, stage: ValidationStage) -> bool:
        """
        WHY: Check if validator exists for a stage.

        Args:
            stage: Validation stage to check

        Returns:
            True if validator is registered
        """
        return stage in self._validators

    def get_all_stages(self) -> list:
        """
        WHY: Get list of all registered validation stages.

        Returns:
            List of ValidationStage enums
        """
        return list(self._validators.keys())

    def unregister_validator(self, stage: ValidationStage) -> bool:
        """
        WHY: Remove a validator from the registry.

        Args:
            stage: Validation stage to unregister

        Returns:
            True if validator was removed, False if not found
        """
        if stage not in self._validators:
            return False

        del self._validators[stage]
        return True

    def clear_registry(self) -> None:
        """
        WHY: Clear all validators from registry.

        Useful for testing or complete re-initialization.
        """
        self._validators.clear()

    def reset_to_defaults(self) -> None:
        """
        WHY: Reset registry to default validators.

        Useful for testing or recovering from custom configurations.
        """
        self.clear_registry()
        self._initialize_default_validators()


class ValidatorFactory:
    """
    WHY: Factory for creating validator instances.

    RESPONSIBILITY: Provide centralized creation logic for validators
    with optional configuration.
    """

    @staticmethod
    def create_validator(stage: ValidationStage, **kwargs) -> BaseValidator:
        """
        WHY: Create validator instance for a stage with optional configuration.

        Args:
            stage: Validation stage
            **kwargs: Optional configuration for validator

        Returns:
            Configured validator instance

        Raises:
            ValueError: If stage is not recognized
        """
        # Dispatch table for validator creation
        validator_classes: Dict[ValidationStage, Callable[[], BaseValidator]] = {
            ValidationStage.IMPORTS: ImportsValidator,
            ValidationStage.SIGNATURE: SignatureValidator,
            ValidationStage.DOCSTRING: DocstringValidator,
            ValidationStage.BODY: BodyValidator,
            ValidationStage.TESTS: TestsValidator,
            ValidationStage.FULL_CODE: FullCodeValidator
        }

        validator_class = validator_classes.get(stage)

        # Guard: Unknown stage
        if not validator_class:
            raise ValueError(f"Unknown validation stage: {stage}")

        return validator_class()

    @staticmethod
    def create_registry() -> ValidatorRegistry:
        """
        WHY: Factory method for creating configured registry.

        Returns:
            Initialized ValidatorRegistry
        """
        return ValidatorRegistry()


# Singleton registry instance for convenience
_default_registry: Optional[ValidatorRegistry] = None


def get_default_registry() -> ValidatorRegistry:
    """
    WHY: Provide singleton access to default validator registry.

    Returns:
        Default ValidatorRegistry instance
    """
    global _default_registry

    if _default_registry is None:
        _default_registry = ValidatorRegistry()

    return _default_registry


def reset_default_registry() -> None:
    """
    WHY: Reset the default registry (useful for testing).

    Forces creation of new registry on next get_default_registry() call.
    """
    global _default_registry
    _default_registry = None
