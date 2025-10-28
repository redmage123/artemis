#!/usr/bin/env python3
"""
Validated Developer Mixin - BACKWARD COMPATIBILITY WRAPPER

WHY: This file maintains backward compatibility while the codebase migrates
     to the new modularized structure in validated_developer/

MIGRATION PATH:
    OLD: from validated_developer_mixin import ValidatedDeveloperMixin
    NEW: from validated_developer import ValidatedDeveloperMixin

STATUS: All classes moved to validated_developer/ package
        This wrapper re-exports for backward compatibility

DEPRECATED: Use validated_developer package directly
"""

# Re-export all components from new package
from validated_developer.core_mixin import ValidatedDeveloperMixin
from validated_developer.tdd_mixin import ValidatedTDDMixin
from validated_developer.factory import create_validated_developer_agent
from validated_developer.validation_strategies import (
    RAGValidationStrategy,
    SelfCritiqueValidationStrategy
)
from validated_developer.event_notifier import ValidationEventNotifier
from validated_developer.code_extractor import CodeExtractor

__all__ = [
    # Core classes
    'ValidatedDeveloperMixin',
    'ValidatedTDDMixin',

    # Factory
    'create_validated_developer_agent',

    # Strategies
    'RAGValidationStrategy',
    'SelfCritiqueValidationStrategy',

    # Utilities
    'ValidationEventNotifier',
    'CodeExtractor'
]
