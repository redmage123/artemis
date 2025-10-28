#!/usr/bin/env python3
"""
Module: notebook_generation_stage.py (BACKWARD COMPATIBILITY WRAPPER)

WHY: Maintains backward compatibility with existing imports while providing
     access to refactored modular implementation.

RESPONSIBILITY:
- Re-export NotebookGenerationStage from modular package
- Re-export generate_notebook convenience function
- Preserve existing public API
- Redirect to new implementation

MIGRATION NOTICE:
This is a compatibility wrapper. New code should import from:
    from stages.notebook_generation import NotebookGenerationStage

Pattern: Facade/Adapter for backward compatibility
"""

# Import from new modular package
from stages.notebook_generation import (
    NotebookGenerationStage,
    generate_notebook
)

# Re-export for backward compatibility
__all__ = [
    'NotebookGenerationStage',
    'generate_notebook',
]

# Version tracking
__version__ = '2.0.0'
__legacy__ = True
__refactored__ = 'stages.notebook_generation'
