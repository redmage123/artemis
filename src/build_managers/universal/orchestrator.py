#!/usr/bin/env python3
"""
Module: build_managers.universal.orchestrator

WHY: Universal build system orchestration that automatically detects and manages
     builds across all supported languages and ecosystems. Provides unified interface
     for Artemis development pipeline.

RESPONSIBILITY:
- Detect build system from project files
- Recommend build systems for new projects
- Factory for creating appropriate build manager instances
- Unified build/test interface across all build systems
- Support multi-language projects

PATTERNS:
- Facade Pattern: Simplified interface over build system complexity
- Factory Pattern: Dynamic build manager creation
- Strategy Pattern: Different strategies per build system
- Lazy Loading: Import managers only when needed

USAGE:
    from build_managers.universal import UniversalBuildSystem

    # Auto-detect and build
    ubs = UniversalBuildSystem(project_dir="/path/to/project")
    detection = ubs.detect_build_system()
    result = ubs.build()

    # Explicit build system
    result = ubs.build(build_system=BuildSystem.MAVEN)

    # Get specific manager
    maven = ubs.get_build_manager(BuildSystem.MAVEN)
"""

from pathlib import Path
from typing import Optional, Any, Callable, Dict
import logging

from build_managers.models import (
    BuildSystem,
    BuildSystemDetection,
    BuildSystemRecommendation,
    BuildResult
)
from build_managers.detector import BuildSystemDetector
from build_managers.recommender import BuildSystemRecommender
from build_system_exceptions import UnsupportedBuildSystemError


class UniversalBuildSystem:
    """
    Universal build system orchestrator.

    WHY: Provides unified interface for all build operations across different
         languages and build systems. Enables Artemis to work with any project
         without manual configuration.

    RESPONSIBILITY:
    - Auto-detect build systems from project files
    - Recommend build systems for new projects
    - Factory for creating build manager instances
    - Unified build/test interface

    PATTERNS:
    - Facade: Simplified interface
    - Factory: Dynamic manager creation
    - Lazy Loading: Import only when needed
    """

    def __init__(
        self,
        project_dir: Optional[Path] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize universal build system.

        Args:
            project_dir: Project root directory (defaults to current directory)
            logger: Optional logger instance
        """
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.logger = logger or logging.getLogger(__name__)

        # Lazy initialization
        self._detector: Optional[BuildSystemDetector] = None
        self._recommender: Optional[BuildSystemRecommender] = None

    @property
    def detector(self) -> BuildSystemDetector:
        """
        Lazy-initialized build system detector.

        WHY: Defer creation until needed to reduce initialization overhead.
        """
        if self._detector is None:
            self._detector = BuildSystemDetector(
                project_dir=self.project_dir,
                logger=self.logger
            )
        return self._detector

    @property
    def recommender(self) -> BuildSystemRecommender:
        """
        Lazy-initialized build system recommender.

        WHY: Defer creation until needed to reduce initialization overhead.
        """
        if self._recommender is None:
            self._recommender = BuildSystemRecommender(logger=self.logger)
        return self._recommender

    def detect_build_system(self) -> BuildSystemDetection:
        """
        Automatically detect build system from project files.

        WHY: Enables zero-configuration operation for existing projects.

        Returns:
            BuildSystemDetection with detected build system, confidence, and evidence

        EXAMPLE:
            detection = ubs.detect_build_system()
            if detection.build_system == BuildSystem.MAVEN:
                print(f"Maven project detected with {detection.confidence:.0%} confidence")
        """
        return self.detector.detect()

    def recommend_build_system(
        self,
        language: str,
        project_type: str = "unknown"
    ) -> BuildSystemRecommendation:
        """
        Recommend build system for new project.

        WHY: Helps developers choose appropriate build tools based on best practices.

        Args:
            language: Programming language (e.g., "python", "java")
            project_type: Type of project (e.g., "web_api", "cli_tool")

        Returns:
            BuildSystemRecommendation with recommended system, rationale, and alternatives

        EXAMPLE:
            recommendation = ubs.recommend_build_system(
                language="python",
                project_type="web_api"
            )
            print(f"Recommended: {recommendation.build_system.value}")
            print(f"Rationale: {recommendation.rationale}")
        """
        return self.recommender.recommend(language=language, project_type=project_type)

    def get_build_manager(
        self,
        build_system: Optional[BuildSystem] = None
    ) -> Any:
        """
        Get appropriate build manager instance.

        WHY: Factory method for creating build-system-specific managers.
        PATTERNS: Factory pattern with auto-detection fallback.

        Args:
            build_system: Specific build system (auto-detected if None)

        Returns:
            Build manager instance (MavenManager, GradleManager, etc.)

        EXAMPLE:
            # Auto-detect
            manager = ubs.get_build_manager()

            # Explicit
            maven = ubs.get_build_manager(BuildSystem.MAVEN)
            result = maven.build()
        """
        # Guard clause: auto-detect if not specified
        if build_system is None:
            detection = self.detect_build_system()
            build_system = detection.build_system

        return self._create_build_manager(build_system)

    def _create_build_manager(self, build_system: BuildSystem) -> Any:
        """
        Create and return the appropriate build manager.

        WHY: Factory method that instantiates framework-specific build managers.
        PATTERNS: Factory pattern with strategy pattern (dictionary mapping).
        PERFORMANCE: Lazy imports reduce startup time.

        Args:
            build_system: BuildSystem enum value

        Returns:
            Build manager instance for the specified build system

        Raises:
            UnsupportedBuildSystemError: If build system not yet implemented
        """
        # Strategy pattern: Dictionary mapping (avoid if/elif chain)
        build_manager_factories: Dict[BuildSystem, Callable] = {
            BuildSystem.MAVEN: self._create_maven_manager,
            BuildSystem.GRADLE: self._create_gradle_manager,
            BuildSystem.NPM: self._create_npm_manager,
            BuildSystem.POETRY: self._create_poetry_manager,
            BuildSystem.CARGO: self._create_cargo_manager,
            BuildSystem.GO_MOD: self._create_go_mod_manager,
            BuildSystem.CMAKE: self._create_cmake_manager,
            BuildSystem.DOTNET: self._create_dotnet_manager,
            BuildSystem.BUNDLER: self._create_bundler_manager,
            BuildSystem.COMPOSER: self._create_composer_manager,
        }

        factory = build_manager_factories.get(build_system)

        # Guard clause: raise if not implemented
        if not factory:
            raise UnsupportedBuildSystemError(
                f"Build system {build_system.value} not yet implemented",
                {
                    "requested_system": build_system.value,
                    "supported_systems": list(build_manager_factories.keys())
                }
            )

        return factory()

    # ========================================================================
    # Build Manager Factory Methods (Lazy Imports)
    # ========================================================================

    def _create_maven_manager(self) -> Any:
        """
        Create Maven manager instance.

        WHY: Lazy import reduces startup time, separate method for testability.
        """
        from maven_manager import MavenManager
        return MavenManager(self.project_dir, self.logger)

    def _create_gradle_manager(self) -> Any:
        """
        Create Gradle manager instance.

        WHY: Lazy import reduces startup time, separate method for testability.
        """
        from gradle_manager import GradleManager
        return GradleManager(self.project_dir, self.logger)

    def _create_npm_manager(self) -> Any:
        """
        Create npm manager instance.

        WHY: Lazy import reduces startup time, separate method for testability.
        """
        from npm_manager import NPMManager
        return NPMManager(self.project_dir, self.logger)

    def _create_poetry_manager(self) -> Any:
        """
        Create Poetry manager instance.

        WHY: Lazy import reduces startup time, separate method for testability.
        """
        from poetry_manager import PoetryManager
        return PoetryManager(self.project_dir, self.logger)

    def _create_cargo_manager(self) -> Any:
        """
        Create Cargo manager instance.

        WHY: Lazy import reduces startup time, separate method for testability.
        """
        from cargo_manager import CargoManager
        return CargoManager(self.project_dir, self.logger)

    def _create_go_mod_manager(self) -> Any:
        """
        Create Go modules manager instance.

        WHY: Lazy import reduces startup time, separate method for testability.
        """
        from go_mod_manager import GoModManager
        return GoModManager(self.project_dir, self.logger)

    def _create_cmake_manager(self) -> Any:
        """
        Create CMake manager instance.

        WHY: Lazy import reduces startup time, separate method for testability.
        """
        from cmake_manager import CMakeManager
        return CMakeManager(self.project_dir, self.logger)

    def _create_dotnet_manager(self) -> Any:
        """
        Create .NET manager instance.

        WHY: Lazy import reduces startup time, separate method for testability.
        """
        from dotnet_manager import DotNetManager
        return DotNetManager(self.project_dir, self.logger)

    def _create_bundler_manager(self) -> Any:
        """
        Create Bundler manager instance.

        WHY: Lazy import reduces startup time, separate method for testability.
        """
        from bundler_manager import BundlerManager
        return BundlerManager(self.project_dir, self.logger)

    def _create_composer_manager(self) -> Any:
        """
        Create Composer manager instance.

        WHY: Lazy import reduces startup time, separate method for testability.
        """
        from composer_manager import ComposerManager
        return ComposerManager(self.project_dir, self.logger)
