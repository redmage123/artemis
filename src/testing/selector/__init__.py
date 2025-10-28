#!/usr/bin/env python3
"""
Testing Framework Selector Package

WHY: Automatic selection of appropriate test frameworks based on project
characteristics enables Artemis to generate tests without manual configuration.
Modular design separates detection, selection, and configuration concerns.

RESPONSIBILITY: Export public API for test framework selection. Single
responsibility - package interface definition.

PATTERNS: Facade pattern - expose simplified API hiding internal complexity.

Public API for test framework selection functionality.

Usage:
    from testing.selector import TestFrameworkSelector

    selector = TestFrameworkSelector(project_dir="/path/to/project")
    recommendation = selector.select_framework(requirements={"type": "unit"})
    print(f"Use {recommendation.framework}: {recommendation.rationale}")
"""

from testing.selector.models import (
    ProjectType,
    TestType,
    FrameworkRecommendation,
    SelectionRequirements,
    FrameworkCapabilities
)

from testing.selector.detector import (
    ProjectDetector,
    FrameworkDetector
)

from testing.selector.selector import (
    FrameworkSelector
)

from testing.selector.configurator import (
    FrameworkConfiguration,
    FrameworkConfigurator
)

from testing.selector.selector_core import (
    TestFrameworkSelector
)

__all__ = [
    # Core API
    "TestFrameworkSelector",

    # Models
    "ProjectType",
    "TestType",
    "FrameworkRecommendation",
    "SelectionRequirements",
    "FrameworkCapabilities",

    # Components (for advanced usage)
    "ProjectDetector",
    "FrameworkDetector",
    "FrameworkSelector",
    "FrameworkConfiguration",
    "FrameworkConfigurator"
]
