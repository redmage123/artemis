#!/usr/bin/env python3
"""
Testing Framework Selector - Core Orchestration

WHY: Orchestrates detection, selection, and configuration components to
provide unified framework selection API. Separating orchestration from
individual components enables flexible composition and testing.

RESPONSIBILITY: Coordinate detector, selector, and configurator components.
Single responsibility - orchestration only, delegates to specialized components.

PATTERNS: Facade pattern for unified API. Dependency Injection for testability.

Main entry point for test framework selection functionality.
"""

from pathlib import Path
from typing import Optional, Dict, Any
from testing.selector.models import (
    FrameworkRecommendation,
    SelectionRequirements,
    ProjectType
)
from testing.selector.detector import ProjectDetector, FrameworkDetector
from testing.selector.selector import FrameworkSelector
from testing.selector.configurator import FrameworkConfigurator, FrameworkConfiguration


class TestFrameworkSelector:
    """
    Intelligent test framework selector for Artemis.

    WHY: Different projects require different testing frameworks based on
    language, technology stack, and testing requirements. This class
    orchestrates detection, selection, and configuration components.

    RESPONSIBILITY: Coordinate framework selection workflow. Single
    responsibility - orchestration only, delegates to specialized components.

    PATTERNS: Facade pattern for unified API. Dependency Injection for
    component composition. Strategy pattern delegated to selector component.

    Analyzes project structure, language, and requirements to recommend
    the most appropriate testing framework.
    """

    def __init__(
        self,
        project_dir: Optional[Path] = None,
        project_detector: Optional[ProjectDetector] = None,
        framework_detector: Optional[FrameworkDetector] = None,
        framework_selector: Optional[FrameworkSelector] = None,
        framework_configurator: Optional[FrameworkConfigurator] = None
    ):
        """
        Initialize selector with optional project directory and components.

        WHY: Project directory allows automatic detection of project type
        and existing frameworks. Component injection enables testing with
        mocks and flexible composition.

        Args:
            project_dir: Project root directory for analysis
            project_detector: Component for project type detection (injectable)
            framework_detector: Component for framework detection (injectable)
            framework_selector: Component for framework selection (injectable)
            framework_configurator: Component for framework configuration (injectable)
        """
        self.project_dir = Path(project_dir) if project_dir else None

        # Dependency Injection: Allow component override for testing
        # WHY: Enables unit testing with mocks, flexible composition
        self.project_detector = project_detector or ProjectDetector(self.project_dir)
        self.framework_detector = framework_detector or FrameworkDetector(self.project_dir)
        self.framework_selector = framework_selector or FrameworkSelector()
        self.framework_configurator = framework_configurator or FrameworkConfigurator()

        # Cache project type to avoid repeated file system scans
        self.project_type = (
            self.project_detector.detect_project_type()
            if project_dir
            else ProjectType.UNKNOWN
        )

    def select_framework(
        self,
        requirements: Optional[Dict[str, Any]] = None,
        test_type: str = "unit"
    ) -> FrameworkRecommendation:
        """
        Select the best test framework based on requirements.

        WHY: Artemis needs to choose the right testing framework automatically
        based on project context and requirements. This enables automated test
        generation without manual framework configuration.

        PERFORMANCE: O(1) dictionary lookups for framework selection. File system
        operations cached in project_type attribute to avoid repeated scans.

        Args:
            requirements: Dict with keys like:
                - type: Test type (unit, e2e, performance, etc.)
                - language: Programming language
                - browser: Whether browser automation needed
                - mobile: Whether mobile testing needed
                - existing_tests: Whether tests already exist
            test_type: Type of testing (unit, integration, e2e, etc.)

        Returns:
            FrameworkRecommendation with selected framework and rationale
        """
        # Convert dict requirements to typed object
        requirements = requirements or {}
        requirements["type"] = requirements.get("type", test_type)
        selection_reqs = SelectionRequirements.from_dict(requirements)

        # Infer language if not specified
        if not selection_reqs.language:
            selection_reqs.language = self._infer_language()

        # Detect existing framework if tests exist
        existing_framework = None
        if selection_reqs.existing_tests and self.project_dir:
            existing_framework = self.framework_detector.detect_existing_framework()

        # Delegate to selector component
        return self.framework_selector.select_framework(
            requirements=selection_reqs,
            existing_framework=existing_framework
        )

    def get_framework_configuration(
        self,
        framework_name: str
    ) -> Optional[FrameworkConfiguration]:
        """
        Get configuration details for a framework.

        WHY: After selecting a framework, configuration details (dependencies,
        commands) are needed for setup. Delegates to configurator component.

        Args:
            framework_name: Name of framework to configure

        Returns:
            FrameworkConfiguration if framework known, None otherwise
        """
        return self.framework_configurator.get_configuration(framework_name)

    def _infer_language(self) -> str:
        """
        Infer programming language from project type.

        WHY: Language inference enables framework selection when language
        not explicitly specified in requirements.

        Returns:
            String representation of programming language (default: "python")
        """
        return self.project_detector.infer_language(self.project_type)

    def analyze_project(self) -> Dict[str, Any]:
        """
        Analyze project and return comprehensive information.

        WHY: Provides complete project analysis including type, language,
        and existing frameworks. Useful for debugging and understanding
        project context.

        Returns:
            Dictionary with project analysis results
        """
        # Guard clause: Early return if no project directory
        if not self.project_dir:
            return {
                "project_type": "unknown",
                "language": "python",
                "existing_framework": None,
                "project_dir": None
            }

        existing_framework = self.framework_detector.detect_existing_framework()

        return {
            "project_type": self.project_type.value,
            "language": self._infer_language(),
            "existing_framework": existing_framework,
            "project_dir": str(self.project_dir)
        }
