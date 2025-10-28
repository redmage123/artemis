#!/usr/bin/env python3
"""
Module: advanced_pipeline_integration.py (BACKWARD COMPATIBILITY WRAPPER)

Purpose: Integration facade connecting Dynamic Pipelines, Two-Pass Pipelines, and
         Thermodynamic Computing with artemis_orchestrator.py

MIGRATION NOTICE:
    This file is a backward compatibility wrapper. The actual implementation has been
    modularized into the advanced_pipeline/ package.

    OLD USAGE:
        from advanced_pipeline_integration import AdvancedPipelineIntegration

    NEW USAGE (preferred):
        from advanced_pipeline import AdvancedPipelineIntegration

WHY this wrapper exists:
    - Maintains backward compatibility with existing code
    - Allows gradual migration to modularized structure
    - Prevents breaking changes in existing imports

MIGRATION PATH:
    1. Update imports to use: from advanced_pipeline import ...
    2. Remove this wrapper file once all imports updated
    3. Update tests to import from advanced_pipeline package

For detailed documentation, see:
    - advanced_pipeline/__init__.py - Package overview
    - advanced_pipeline/advanced_pipeline_integration.py - Main facade
    - advanced_pipeline/advanced_pipeline_strategy.py - Strategy implementation
"""

# Re-export all public classes from modularized package
from advanced_pipeline import (
    # Main facade
    AdvancedPipelineIntegration,
    AdvancedPipelineStrategy,

    # Configuration
    AdvancedPipelineConfig,
    ConfigurationManager,

    # Mode selection
    PipelineMode,
    ModeSelectionStrategy,
    ManualModeSelector,
    AutomaticModeSelector,
    ModeSelector,
)

__all__ = [
    # Main facade
    'AdvancedPipelineIntegration',
    'AdvancedPipelineStrategy',

    # Configuration
    'AdvancedPipelineConfig',
    'ConfigurationManager',

    # Mode selection
    'PipelineMode',
    'ModeSelectionStrategy',
    'ManualModeSelector',
    'AutomaticModeSelector',
    'ModeSelector',
]
