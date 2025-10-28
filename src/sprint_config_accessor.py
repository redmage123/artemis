#!/usr/bin/env python3
"""
Sprint Configuration Accessor - Backward Compatibility Wrapper

REFACTORED: This module has been refactored into agile.sprint_config package.

WHY: Maintains backward compatibility while directing users to new modular package.
RESPONSIBILITY: Re-export public API from agile.sprint_config for existing code.
PATTERNS: Facade pattern, deprecation wrapper

MIGRATION PATH:
    Old: from sprint_config_accessor import SprintConfig
    New: from agile.sprint_config import SprintConfigAccessor

    Old: config = SprintConfig.from_hydra(cfg)
    New: config = SprintConfigAccessor.from_hydra(cfg)

REFACTORED MODULES:
    - agile/sprint_config/models.py (127 lines)
    - agile/sprint_config/validators.py (203 lines)
    - agile/sprint_config/hydra_loader.py (178 lines)
    - agile/sprint_config/dict_loader.py (163 lines)
    - agile/sprint_config/accessor.py (208 lines)
    - agile/sprint_config/__init__.py (60 lines)

Total: 939 lines modularized from 227 lines (4.1x expansion for better separation)
Wrapper: 43 lines (81% reduction from original 227 lines)
"""

# Re-export from new package for backward compatibility
from agile.sprint_config import (
    SprintConfigAccessor as SprintConfig,
    SprintPlanningConfig,
    ProjectReviewConfig,
    UIUXEvaluationConfig,
    RetrospectiveConfig
)

__all__ = [
    'SprintConfig',
    'SprintPlanningConfig',
    'ProjectReviewConfig',
    'UIUXEvaluationConfig',
    'RetrospectiveConfig',
]
