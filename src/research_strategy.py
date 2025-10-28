#!/usr/bin/env python3
"""
Research Strategy Pattern Implementation - BACKWARD COMPATIBILITY WRAPPER

WHY: This module maintains backward compatibility with existing code that imports
from research_strategy.py. All implementation has been moved to the research/
package for better modularity and maintainability.

RESPONSIBILITY: Re-exports all public classes and functions from the research package
so that existing code continues to work without modification.

PATTERNS:
- Facade Pattern: Provides simplified interface to refactored subsystem
- Adapter Pattern: Maintains old API while delegating to new implementation

DEPRECATION NOTICE:
This module is deprecated. Please update imports to use the research package directly:

    OLD: from research_strategy import ResearchExample, ResearchStrategyFactory
    NEW: from research import ResearchExample, ResearchStrategyFactory

This wrapper will be removed in a future version.
"""

import warnings

# Show deprecation warning on import
warnings.warn(
    "research_strategy module is deprecated. "
    "Please use 'from research import ...' instead. "
    "This compatibility wrapper will be removed in a future version.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export all public classes from the research package
from research import (
    ResearchExample,
    ResearchStrategy,
    GitHubResearchStrategy,
    HuggingFaceResearchStrategy,
    LocalExamplesResearchStrategy,
    ResearchStrategyFactory,
)

# Maintain backward compatibility with module-level __all__
__all__ = [
    "ResearchExample",
    "ResearchStrategy",
    "GitHubResearchStrategy",
    "HuggingFaceResearchStrategy",
    "LocalExamplesResearchStrategy",
    "ResearchStrategyFactory",
]
