#!/usr/bin/env python3
"""
Package: build_managers

WHY: Central package for all build system management functionality across multiple languages
     and ecosystems. Provides unified interface for detecting, configuring, and executing
     builds for Java, Python, JavaScript, C++, Rust, Go, .NET, Ruby, PHP, and more.

RESPONSIBILITY:
- Detect build systems from project files (pom.xml, package.json, Cargo.toml, etc.)
- Recommend appropriate build systems for new projects based on language and type
- Provide unified interface for building, testing, and managing dependencies
- Support multi-language projects with multiple build systems

PATTERNS:
- Factory Pattern: BuildManager creation based on detected/selected build system
- Strategy Pattern: Different build strategies for different systems
- Template Method: Common build flow with system-specific implementations
- Facade: Simplified interface over complex build tool ecosystems

MODULES:
- models: Core enums and data classes (BuildSystem, Language, ProjectType, BuildResult)
- detector: Build system detection from project files
- recommender: Build system recommendations for new projects
- universal/: Universal build system orchestration for multi-language projects
- base: Abstract base class for all build managers (BuildManagerBase)

INTEGRATION:
- Used by stages/development_stage.py for building projects
- Used by test_runner.py for executing tests
- Used by standalone_developer_agent.py for dependency management
- Integrates with existing *_manager.py modules (maven_manager, npm_manager, etc.)

USAGE:
    from build_managers import UniversalBuildSystem, BuildSystem
    from build_managers.detector import BuildSystemDetector
    from build_managers.recommender import BuildSystemRecommender

    # Detect build system
    detector = BuildSystemDetector(project_dir="/path/to/project")
    detection = detector.detect()

    # Or recommend for new project
    recommender = BuildSystemRecommender()
    recommendation = recommender.recommend(language="python", project_type="web_api")

    # Universal orchestration
    ubs = UniversalBuildSystem(project_dir="/path/to/project")
    build_result = ubs.build()
    test_result = ubs.test()
"""

from pathlib import Path
from typing import Optional
import logging

# Core models (enums and data classes)
from build_managers.models import (
    BuildSystem,
    Language,
    ProjectType,
    BuildSystemDetection,
    BuildSystemRecommendation,
    BuildResult
)

# Detection and recommendation
from build_managers.detector import BuildSystemDetector
from build_managers.recommender import BuildSystemRecommender

# Universal orchestration
from build_managers.universal.orchestrator import UniversalBuildSystem

__all__ = [
    # Core models
    'BuildSystem',
    'Language',
    'ProjectType',
    'BuildSystemDetection',
    'BuildSystemRecommendation',
    'BuildResult',

    # Detection and recommendation
    'BuildSystemDetector',
    'BuildSystemRecommender',

    # Universal orchestration
    'UniversalBuildSystem',
]

__version__ = '1.0.0'


def get_universal_build_system(
    project_dir: Optional[Path] = None,
    logger: Optional[logging.Logger] = None
) -> UniversalBuildSystem:
    """
    Convenience factory function for creating UniversalBuildSystem instance.

    WHY: Provides simple entry point for common use case.

    Args:
        project_dir: Project root directory
        logger: Optional logger instance

    Returns:
        Configured UniversalBuildSystem instance

    Example:
        from build_managers import get_universal_build_system

        ubs = get_universal_build_system(project_dir="/path/to/project")
        detection = ubs.detect_build_system()
        build_result = ubs.build()
    """
    return UniversalBuildSystem(project_dir=project_dir, logger=logger)
