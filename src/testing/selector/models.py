#!/usr/bin/env python3
"""
Testing Framework Selector - Data Models

WHY: Centralized data models for test framework selection provide type safety
and clear contracts between modules. Separating models from business logic
enables easier testing and evolution of the selection algorithm.

RESPONSIBILITY: Define data structures for project types, test types, and
framework recommendations. Single source of truth for framework selection
domain models.

PATTERNS: Dataclass pattern for immutable value objects. Enum pattern for
type-safe categorization of projects and tests.

Used by all testing selector modules to communicate framework data.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any


class ProjectType(Enum):
    """
    Project types that influence framework selection.

    WHY: Different project types (languages, platforms) require different
    testing frameworks. Enums provide type safety and exhaustive matching.

    PATTERNS: Enum pattern for type-safe categorization.
    """
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    WEB_FRONTEND = "web_frontend"
    WEB_BACKEND = "web_backend"
    MOBILE_IOS = "mobile_ios"
    MOBILE_ANDROID = "mobile_android"
    API = "api"
    UNKNOWN = "unknown"


class TestType(Enum):
    """
    Test types that require specific frameworks.

    WHY: Different test types (unit, E2E, performance) have specialized
    framework requirements. Enums enable exhaustive matching in selection logic.

    PATTERNS: Enum pattern for type-safe test categorization.
    """
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    BROWSER = "browser"
    MOBILE = "mobile"
    PERFORMANCE = "performance"
    API_TEST = "api"
    ACCEPTANCE = "acceptance"
    PROPERTY_BASED = "property_based"


@dataclass
class FrameworkRecommendation:
    """
    Framework recommendation with confidence and rationale.

    WHY: Recommendations include not just the framework name but also
    confidence score and explanation. This enables Artemis to make
    informed decisions and provide transparency to users.

    RESPONSIBILITY: Immutable value object representing a framework
    selection decision with supporting information.

    PATTERNS: Dataclass for immutable value objects.

    Attributes:
        framework: Name of recommended testing framework
        confidence: Confidence score 0.0-1.0 (0.0=uncertain, 1.0=certain)
        rationale: Human-readable explanation of why this framework was chosen
        alternatives: List of alternative frameworks that could also work
    """
    framework: str
    confidence: float  # 0.0 to 1.0
    rationale: str
    alternatives: List[str]


@dataclass
class SelectionRequirements:
    """
    Requirements for test framework selection.

    WHY: Encapsulating selection criteria in a typed object provides
    clarity and enables validation. Better than passing raw dictionaries.

    RESPONSIBILITY: Value object containing all inputs needed for
    framework selection decisions.

    PATTERNS: Dataclass for structured data with defaults.

    Attributes:
        test_type: Type of testing needed (unit, e2e, etc.)
        language: Programming language (python, java, etc.)
        browser: Whether browser automation is needed
        mobile: Whether mobile testing is needed
        performance: Whether performance/load testing is needed
        existing_tests: Whether tests already exist in project
        custom_requirements: Dictionary for additional requirements
    """
    test_type: str = "unit"
    language: Optional[str] = None
    browser: bool = False
    mobile: bool = False
    performance: bool = False
    existing_tests: bool = False
    custom_requirements: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert requirements to dictionary format.

        WHY: Enables backward compatibility with code expecting
        dictionary-based requirements.

        Returns:
            Dictionary representation of requirements
        """
        result = {
            "type": self.test_type,
            "browser": self.browser,
            "mobile": self.mobile,
            "performance": self.performance,
            "existing_tests": self.existing_tests
        }

        # Guard clause: Add language if specified
        if self.language:
            result["language"] = self.language

        # Guard clause: Merge custom requirements if present
        if self.custom_requirements:
            result.update(self.custom_requirements)

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SelectionRequirements":
        """
        Create requirements from dictionary.

        WHY: Enables backward compatibility with code passing
        dictionary-based requirements.

        Args:
            data: Dictionary containing requirement fields

        Returns:
            SelectionRequirements instance
        """
        return cls(
            test_type=data.get("type", data.get("test_type", "unit")),
            language=data.get("language"),
            browser=data.get("browser", False),
            mobile=data.get("mobile", False),
            performance=data.get("performance", False),
            existing_tests=data.get("existing_tests", False),
            custom_requirements=data.get("custom_requirements")
        )


@dataclass
class FrameworkCapabilities:
    """
    Capabilities supported by a testing framework.

    WHY: Different frameworks support different test types and features.
    Modeling capabilities explicitly enables data-driven framework selection.

    RESPONSIBILITY: Value object describing what a framework can do.

    PATTERNS: Dataclass for structured capability description.

    Attributes:
        framework_name: Name of the framework
        supported_languages: Languages the framework supports
        supported_test_types: Types of tests the framework handles
        browser_automation: Whether framework supports browser testing
        mobile_testing: Whether framework supports mobile testing
        performance_testing: Whether framework supports performance testing
        parallel_execution: Whether framework supports parallel test execution
        property_based: Whether framework supports property-based testing
    """
    framework_name: str
    supported_languages: List[str]
    supported_test_types: List[str]
    browser_automation: bool = False
    mobile_testing: bool = False
    performance_testing: bool = False
    parallel_execution: bool = False
    property_based: bool = False
