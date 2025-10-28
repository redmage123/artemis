#!/usr/bin/env python3
"""
Package: stages.notebook_generation

WHY: Modularized notebook generation stage for Artemis pipeline.
     Separates concerns for maintainability and testability.

RESPONSIBILITY:
- Export main stage class and convenience functions
- Provide unified interface for notebook generation
- Hide internal implementation details

PATTERNS:
- Facade: Simple public API hiding complex subsystem
- Dependency Injection: Components can be injected or defaulted
"""

from .notebook_generation_stage_core import (
    NotebookGenerationStage,
    generate_notebook
)
from .template_selector import TemplateSelector
from .cell_generator import CellGeneratorStrategy
from .notebook_validator import NotebookValidator
from .output_formatter import OutputFormatter
from .execution_handler import ExecutionHandler

__all__ = [
    # Main stage class
    'NotebookGenerationStage',

    # Convenience function
    'generate_notebook',

    # Components (for testing/customization)
    'TemplateSelector',
    'CellGeneratorStrategy',
    'NotebookValidator',
    'OutputFormatter',
    'ExecutionHandler',
]

__version__ = '2.0.0'
__author__ = 'Artemis Development Team'
