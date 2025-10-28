#!/usr/bin/env python3
"""
Testing Framework Selector - Selection Logic

WHY: Framework selection requires sophisticated logic based on test type,
language, and special requirements. Separating selection logic from detection
and configuration enables focused testing and evolution.

RESPONSIBILITY: Apply selection rules to choose appropriate testing framework.
Single responsibility - selection logic only, no detection or configuration.

PATTERNS: Strategy pattern with dispatch tables for selection rules.
Guard clauses for early returns based on priority.

Used by selector_core to choose frameworks based on requirements.
"""

from typing import Optional, Dict, Callable
from testing.selector.models import (
    FrameworkRecommendation,
    TestType,
    SelectionRequirements
)


class FrameworkSelector:
    """
    Applies selection rules to choose testing framework.

    WHY: Different test types and requirements demand different frameworks.
    Encapsulating selection logic enables testability and evolution of rules.

    RESPONSIBILITY: Execute framework selection algorithm based on requirements.
    Single responsibility - selection rules only.

    PATTERNS: Strategy pattern with dispatch tables for selection rules.
    Chain of Responsibility for priority-based selection.
    """

    def __init__(self):
        """Initialize selector with selection strategies."""
        # Strategy pattern: Dispatch table for test type strategies
        # WHY: Easily extensible, testable independently, avoids elif chains
        self._test_type_strategies: Dict[TestType, Callable[[SelectionRequirements], Optional[FrameworkRecommendation]]] = {
            TestType.MOBILE: self._select_mobile_framework,
            TestType.PERFORMANCE: self._select_performance_framework,
            TestType.BROWSER: self._select_browser_framework,
            TestType.ACCEPTANCE: self._select_acceptance_framework,
            TestType.PROPERTY_BASED: self._select_property_framework
        }

        # Strategy pattern: Dispatch table for language-based selection
        self._language_strategies: Dict[str, Callable[[SelectionRequirements], FrameworkRecommendation]] = {
            "python": self._select_python_framework,
            "javascript": self._select_javascript_framework,
            "typescript": self._select_typescript_framework,
            "java": self._select_java_framework,
            "cpp": self._select_cpp_framework,
            "c++": self._select_cpp_framework
        }

    def select_framework(
        self,
        requirements: SelectionRequirements,
        existing_framework: Optional[str] = None
    ) -> FrameworkRecommendation:
        """
        Select best test framework based on requirements.

        WHY: Artemis needs to choose the right testing framework automatically
        based on project context and requirements. This enables automated test
        generation without manual framework configuration.

        PERFORMANCE: O(1) dictionary lookups for framework selection.
        Early returns avoid unnecessary rule evaluation.

        Args:
            requirements: Selection requirements (test type, language, etc.)
            existing_framework: Framework already in use (if any)

        Returns:
            FrameworkRecommendation with selected framework and rationale
        """
        # Guard clause: Early return for existing frameworks
        # WHY: Prefer consistency - use existing framework if tests already exist
        if existing_framework:
            return FrameworkRecommendation(
                framework=existing_framework,
                confidence=0.9,
                rationale=f"Project already uses {existing_framework} framework",
                alternatives=[]
            )

        # Convert test type string to enum
        try:
            test_type_enum = TestType(requirements.test_type)
        except ValueError:
            test_type_enum = TestType.UNIT

        # Guard clause: Check specialized test type strategies
        # WHY: Specialized test types (mobile, performance) have specific needs
        if test_type_enum in self._test_type_strategies:
            result = self._test_type_strategies[test_type_enum](requirements)
            if result:
                return result

        # Guard clause: Check language-based strategies
        # WHY: Language determines available framework options
        if requirements.language and requirements.language in self._language_strategies:
            return self._language_strategies[requirements.language](requirements)

        # Default fallback: pytest for unknown languages
        # WHY: pytest is versatile and widely supported
        return FrameworkRecommendation(
            framework="pytest",
            confidence=0.5,
            rationale="pytest is a versatile default choice for most projects",
            alternatives=["unittest"]
        )

    def _select_mobile_framework(
        self,
        requirements: SelectionRequirements
    ) -> FrameworkRecommendation:
        """
        Select framework for mobile testing.

        WHY: Mobile testing requires specialized frameworks with device automation.

        Args:
            requirements: Selection requirements

        Returns:
            Framework recommendation for mobile testing
        """
        return FrameworkRecommendation(
            framework="appium",
            confidence=0.95,
            rationale="Mobile app testing requires Appium for cross-platform support",
            alternatives=[]
        )

    def _select_performance_framework(
        self,
        requirements: SelectionRequirements
    ) -> FrameworkRecommendation:
        """
        Select framework for performance testing.

        WHY: Performance testing requires specialized load testing tools.

        Args:
            requirements: Selection requirements

        Returns:
            Framework recommendation for performance testing
        """
        return FrameworkRecommendation(
            framework="jmeter",
            confidence=0.9,
            rationale="JMeter is the industry standard for performance and load testing",
            alternatives=["locust"]
        )

    def _select_browser_framework(
        self,
        requirements: SelectionRequirements
    ) -> FrameworkRecommendation:
        """
        Select framework for browser automation.

        WHY: Browser testing requires specialized automation frameworks.

        Args:
            requirements: Selection requirements

        Returns:
            Framework recommendation for browser testing
        """
        # Prefer modern Playwright over Selenium
        return FrameworkRecommendation(
            framework="playwright",
            confidence=0.85,
            rationale="Playwright provides modern browser automation with better reliability",
            alternatives=["selenium"]
        )

    def _select_acceptance_framework(
        self,
        requirements: SelectionRequirements
    ) -> FrameworkRecommendation:
        """
        Select framework for acceptance testing (BDD).

        WHY: BDD requires human-readable test frameworks.

        Args:
            requirements: Selection requirements

        Returns:
            Framework recommendation for acceptance testing
        """
        return FrameworkRecommendation(
            framework="robot",
            confidence=0.8,
            rationale="Robot Framework provides human-readable acceptance tests",
            alternatives=["pytest"]  # with pytest-bdd
        )

    def _select_property_framework(
        self,
        requirements: SelectionRequirements
    ) -> FrameworkRecommendation:
        """
        Select framework for property-based testing.

        WHY: Property-based testing requires specialized frameworks.

        Args:
            requirements: Selection requirements

        Returns:
            Framework recommendation for property-based testing
        """
        return FrameworkRecommendation(
            framework="hypothesis",
            confidence=0.95,
            rationale="Hypothesis specializes in property-based testing for Python",
            alternatives=["pytest"]
        )

    def _select_python_framework(
        self,
        requirements: SelectionRequirements
    ) -> FrameworkRecommendation:
        """
        Select framework for Python projects.

        WHY: Python has well-established testing frameworks.

        Args:
            requirements: Selection requirements

        Returns:
            Framework recommendation for Python
        """
        return FrameworkRecommendation(
            framework="pytest",
            confidence=0.9,
            rationale="pytest is the modern standard for Python testing",
            alternatives=["unittest"]
        )

    def _select_javascript_framework(
        self,
        requirements: SelectionRequirements
    ) -> FrameworkRecommendation:
        """
        Select framework for JavaScript projects.

        WHY: JavaScript ecosystem standardized on Jest.

        Args:
            requirements: Selection requirements

        Returns:
            Framework recommendation for JavaScript
        """
        return FrameworkRecommendation(
            framework="jest",
            confidence=0.9,
            rationale="Jest is the de facto standard for JavaScript testing",
            alternatives=["mocha"]
        )

    def _select_typescript_framework(
        self,
        requirements: SelectionRequirements
    ) -> FrameworkRecommendation:
        """
        Select framework for TypeScript projects.

        WHY: TypeScript uses same ecosystem as JavaScript.

        Args:
            requirements: Selection requirements

        Returns:
            Framework recommendation for TypeScript
        """
        return FrameworkRecommendation(
            framework="jest",
            confidence=0.9,
            rationale="Jest is the de facto standard for TypeScript testing",
            alternatives=["mocha"]
        )

    def _select_java_framework(
        self,
        requirements: SelectionRequirements
    ) -> FrameworkRecommendation:
        """
        Select framework for Java projects.

        WHY: Java has JUnit as the standard framework.

        Args:
            requirements: Selection requirements

        Returns:
            Framework recommendation for Java
        """
        return FrameworkRecommendation(
            framework="junit",
            confidence=0.9,
            rationale="JUnit is the standard testing framework for Java",
            alternatives=["testng"]
        )

    def _select_cpp_framework(
        self,
        requirements: SelectionRequirements
    ) -> FrameworkRecommendation:
        """
        Select framework for C++ projects.

        WHY: C++ has Google Test as the industry standard.

        Args:
            requirements: Selection requirements

        Returns:
            Framework recommendation for C++
        """
        return FrameworkRecommendation(
            framework="gtest",
            confidence=0.9,
            rationale="Google Test is the industry standard for C++ testing",
            alternatives=["catch2"]
        )
