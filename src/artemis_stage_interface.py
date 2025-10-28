#!/usr/bin/env python3
"""
Module: artemis_stage_interface.py (DEPRECATED - Use core.interfaces instead)

BACKWARD COMPATIBILITY WRAPPER

Purpose: Maintains backward compatibility for existing imports.
Why: Allows gradual migration to new modular structure without breaking existing code.

DEPRECATION NOTICE:
This module is deprecated and will be removed in a future version.
Please update your imports to use:
    from core.interfaces import PipelineStage, TestRunnerInterface, ValidatorInterface, LoggerInterface

Migration Status: Phase 1 - Core interfaces moved to src/core/interfaces.py
Next Steps: Update all imports across codebase to use new location.

Patterns:
- Facade Pattern: Re-exports interfaces from new location
- Adapter Pattern: Provides compatibility shim during migration
"""

# Import from new location and re-export
from core.interfaces import (
    PipelineStage,
    TestRunnerInterface,
    ValidatorInterface,
    LoggerInterface
)

# Export for backward compatibility
__all__ = [
    "PipelineStage",
    "TestRunnerInterface",
    "ValidatorInterface",
    "LoggerInterface"
]
