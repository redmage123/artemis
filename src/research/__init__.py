#!/usr/bin/env python3
"""
Research Package

WHY: Provides a modular, extensible system for researching code examples from multiple
sources (GitHub, HuggingFace, local filesystem). Implements Strategy Pattern to enable
easy addition of new research sources.

RESPONSIBILITY: Exports public API for the research package:
- ResearchExample: Data model for research findings
- ResearchStrategy: Abstract base for all strategies
- Concrete strategy implementations (GitHub, HuggingFace, Local)
- ResearchStrategyFactory: Factory for creating strategies
- Exception types for error handling

PATTERNS:
- Facade Pattern: Simplifies access to research subsystem
- Strategy Pattern: Interchangeable research algorithms
- Factory Pattern: Centralized strategy creation

USAGE:
    from research import ResearchStrategyFactory, ResearchExample

    # Create a specific strategy
    github_strategy = ResearchStrategyFactory.create_strategy("github")
    results = github_strategy.search("authentication", ["python"], max_results=5)

    # Or create all strategies
    all_strategies = ResearchStrategyFactory.create_all_strategies()
    for strategy in all_strategies:
        results = strategy.search("REST API", ["javascript"], max_results=3)
"""

# Models
from research.models import ResearchExample

# Base strategy
from research.base_strategy import ResearchStrategy

# Concrete strategies
from research.github_strategy import GitHubResearchStrategy
from research.huggingface_strategy import HuggingFaceResearchStrategy
from research.local_strategy import LocalExamplesResearchStrategy

# Factory
from research.factory import ResearchStrategyFactory

# Version
__version__ = "1.0.0"

# Public API
__all__ = [
    # Models
    "ResearchExample",

    # Strategies
    "ResearchStrategy",
    "GitHubResearchStrategy",
    "HuggingFaceResearchStrategy",
    "LocalExamplesResearchStrategy",

    # Factory
    "ResearchStrategyFactory",
]
