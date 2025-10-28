#!/usr/bin/env python3
"""
Package: advanced_pipeline

WHY this package exists:
    Modularized advanced pipeline integration system providing unified facade
    for Dynamic Pipelines, Two-Pass Pipelines, and Thermodynamic Computing.

RESPONSIBILITY:
    - Export all public classes for advanced pipeline integration
    - Provide clean package interface
    - Enable backward compatibility through wrapper

USAGE:
    from advanced_pipeline import (
        AdvancedPipelineIntegration,
        AdvancedPipelineStrategy,
        AdvancedPipelineConfig,
        PipelineMode
    )

    # Create integration
    integration = AdvancedPipelineIntegration.create_default()

    # Use in orchestrator
    strategy = integration.get_strategy()
"""

# Core integration classes
from advanced_pipeline.advanced_pipeline_integration import AdvancedPipelineIntegration
from advanced_pipeline.advanced_pipeline_strategy import AdvancedPipelineStrategy

# Configuration
from advanced_pipeline.pipeline_config import AdvancedPipelineConfig
from advanced_pipeline.configuration_manager import ConfigurationManager

# Mode selection
from advanced_pipeline.pipeline_mode import PipelineMode
from advanced_pipeline.mode_selection_strategy import ModeSelectionStrategy
from advanced_pipeline.manual_mode_selector import ManualModeSelector
from advanced_pipeline.automatic_mode_selector import AutomaticModeSelector
from advanced_pipeline.mode_selector import ModeSelector

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
