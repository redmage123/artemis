#!/usr/bin/env python3
"""
Module: build_managers.models

WHY: Core data models and enumerations for build system management. These models
     are shared across all build system detection, recommendation, and execution logic.

RESPONSIBILITY:
- Define all supported build systems (Maven, Gradle, npm, Poetry, Cargo, etc.)
- Define programming languages and project types
- Provide structured results for detection and recommendation operations
- Ensure type safety with Enums and dataclasses

PATTERNS:
- Enum Pattern: Type-safe enumeration of build systems, languages, and project types
- Dataclass Pattern: Immutable data containers with automatic methods
- Value Object: BuildResult represents build outcome with all relevant data

USAGE:
    from build_managers.models import BuildSystem, Language, ProjectType
    from build_managers.models import BuildSystemDetection, BuildResult

    # Check build system
    if detection.build_system == BuildSystem.MAVEN:
        print(f"Maven project with {detection.confidence:.0%} confidence")

    # Create build result
    result = BuildResult(
        success=True,
        exit_code=0,
        duration=45.2,
        output="BUILD SUCCESS",
        build_system="maven"
    )
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List


class BuildSystem(Enum):
    """
    All supported build systems across all languages.

    WHY: Type-safe enumeration prevents typos and enables IDE autocomplete.
         Each build system has unique detection signatures and build commands.

    CATEGORIES:
    - Java: Maven (XML-based), Gradle (Groovy/Kotlin DSL), Ant (legacy XML)
    - JavaScript/Node.js: npm (default), yarn (fast), pnpm (disk-efficient)
    - Python: pip (basic), Poetry (modern), pipenv (virtual envs), conda (data science)
    - C/C++: CMake (cross-platform), Make (traditional)
    - Rust: Cargo (official package manager)
    - Go: go mod (official module system)
    - .NET: dotnet CLI (official), NuGet (package manager)
    - Ruby: Bundler (gem dependency manager)
    - PHP: Composer (dependency manager)
    """
    # Java ecosystem
    MAVEN = "maven"
    GRADLE = "gradle"
    ANT = "ant"

    # JavaScript/Node.js ecosystem
    NPM = "npm"
    YARN = "yarn"
    PNPM = "pnpm"

    # Python ecosystem
    PIP = "pip"
    POETRY = "poetry"
    PIPENV = "pipenv"
    CONDA = "conda"

    # C/C++ ecosystem
    CMAKE = "cmake"
    MAKE = "make"

    # Rust ecosystem
    CARGO = "cargo"

    # Go ecosystem
    GO_MOD = "go"

    # .NET ecosystem
    DOTNET = "dotnet"
    NUGET = "nuget"

    # Ruby ecosystem
    BUNDLER = "bundler"

    # PHP ecosystem
    COMPOSER = "composer"

    # Fallback
    UNKNOWN = "unknown"


class Language(Enum):
    """
    Programming languages supported by Artemis.

    WHY: Type-safe language identification for build system recommendations
         and project analysis. Each language has preferred build tools.

    ECOSYSTEM MAPPING:
    - JAVA -> Maven, Gradle, Ant
    - JAVASCRIPT/TYPESCRIPT -> npm, yarn, pnpm
    - PYTHON -> Poetry, pip, pipenv, conda
    - CPP/C -> CMake, Make
    - RUST -> Cargo
    - GO -> go mod
    - CSHARP -> dotnet, NuGet
    - RUBY -> Bundler
    - PHP -> Composer
    """
    JAVA = "java"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    PYTHON = "python"
    CPP = "cpp"
    C = "c"
    RUST = "rust"
    GO = "go"
    CSHARP = "csharp"
    RUBY = "ruby"
    PHP = "php"
    UNKNOWN = "unknown"


class ProjectType(Enum):
    """
    Project type classifications for build system recommendations.

    WHY: Different project types have different build requirements and
         recommended tools. Web APIs need different tooling than CLI tools.

    TYPES:
    - WEB_API: RESTful/GraphQL backend services
    - WEB_FRONTEND: React/Vue/Angular applications
    - WEB_FULLSTACK: Combined frontend + backend
    - CLI_TOOL: Command-line utilities
    - LIBRARY: Reusable packages/libraries
    - MICROSERVICE: Distributed service architectures
    - DESKTOP_APP: Native desktop applications
    - MOBILE_APP: iOS/Android applications
    - DATA_SCIENCE: Jupyter notebooks, ML models
    """
    WEB_API = "web_api"
    WEB_FRONTEND = "web_frontend"
    WEB_FULLSTACK = "web_fullstack"
    CLI_TOOL = "cli_tool"
    LIBRARY = "library"
    MICROSERVICE = "microservice"
    DESKTOP_APP = "desktop_app"
    MOBILE_APP = "mobile_app"
    DATA_SCIENCE = "data_science"
    UNKNOWN = "unknown"


@dataclass
class BuildSystemDetection:
    """
    Result of build system detection from project files.

    WHY: Structured result provides all information about detected build system
         including confidence level and supporting evidence.

    ATTRIBUTES:
    - build_system: Detected build system enum
    - confidence: Float 0.0-1.0 indicating detection certainty
    - evidence: List of files that support this detection (e.g., ["pom.xml"])
    - language: Detected primary programming language
    - project_type: Detected project type classification

    CONFIDENCE LEVELS:
    - 1.0: Strong match (multiple specific indicators)
    - 0.7-0.9: Good match (specific indicator found)
    - 0.4-0.6: Weak match (generic indicator)
    - 0.0: No match (no indicators found)

    EXAMPLE:
        BuildSystemDetection(
            build_system=BuildSystem.MAVEN,
            confidence=0.9,
            evidence=["pom.xml", "src/main/java/"],
            language=Language.JAVA,
            project_type=ProjectType.WEB_API
        )
    """
    build_system: BuildSystem
    confidence: float  # 0.0 to 1.0
    evidence: List[str] = field(default_factory=list)
    language: Language = Language.UNKNOWN
    project_type: ProjectType = ProjectType.UNKNOWN


@dataclass
class BuildSystemRecommendation:
    """
    Build system recommendation for new projects.

    WHY: Provides reasoned recommendation with alternatives and rationale
         to help developers make informed decisions.

    ATTRIBUTES:
    - build_system: Recommended build system
    - rationale: Human-readable explanation of why this was recommended
    - alternatives: List of alternative build systems to consider
    - confidence: How confident we are in this recommendation (0.0-1.0)

    EXAMPLE:
        BuildSystemRecommendation(
            build_system=BuildSystem.POETRY,
            rationale="Poetry provides modern dependency management for Python",
            alternatives=[BuildSystem.PIP, BuildSystem.PIPENV],
            confidence=0.9
        )
    """
    build_system: BuildSystem
    rationale: str
    alternatives: List[BuildSystem] = field(default_factory=list)
    confidence: float = 1.0


@dataclass
class BuildResult:
    """
    Universal build result structure for all build systems.

    WHY: Standardized result format enables consistent handling regardless of
         underlying build system (Maven, npm, Cargo, etc.). All build managers
         return this same structure.

    RESPONSIBILITY:
    - Report build success/failure with exit code
    - Capture build output and duration
    - Extract and categorize errors and warnings
    - Parse test results (if tests were run)
    - Store build-system-specific metadata

    ATTRIBUTES:
    - success: True if build succeeded (exit_code == 0)
    - exit_code: Process exit code (0 = success, non-zero = failure)
    - duration: Build duration in seconds
    - output: Full build output (stdout + stderr combined)
    - build_system: Name of build system used (e.g., "maven", "npm")
    - errors: List of parsed error messages (max 20)
    - warnings: List of parsed warning messages (max 20)
    - tests_run/passed/failed/skipped: Test statistics if applicable
    - metadata: Build-system-specific data (versions, artifacts, etc.)

    USAGE:
        result = maven_manager.build()
        if result.success:
            print(f"Build succeeded in {result.duration:.1f}s")
        else:
            print(f"Build failed: {result.errors[0]}")
    """
    success: bool
    exit_code: int
    duration: float
    output: str
    build_system: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    tests_run: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    tests_skipped: int = 0

    def __str__(self) -> str:
        """
        Human-readable summary of build result.

        WHY: Provides quick overview without requiring inspection of all fields.
        """
        status = "✓ SUCCESS" if self.success else "✗ FAILED"
        result = f"{status} [{self.build_system}] in {self.duration:.2f}s\n"

        # Guard clause: early return if no tests
        if self.tests_run == 0:
            result += self._format_errors_warnings()
            return result

        result += self._format_test_results()
        result += self._format_errors_warnings()
        return result

    def _format_test_results(self) -> str:
        """
        Format test results section.

        WHY: Separates test formatting logic for clarity.
        """
        parts = [f"Tests: {self.tests_passed}/{self.tests_run} passed"]

        if self.tests_failed > 0:
            parts.append(f"{self.tests_failed} failed")

        if self.tests_skipped > 0:
            parts.append(f"{self.tests_skipped} skipped")

        return ", ".join(parts) + "\n"

    def _format_errors_warnings(self) -> str:
        """
        Format errors and warnings section.

        WHY: Separates error/warning formatting logic for clarity.
        PATTERNS: Guard clause pattern (early returns).
        """
        result = ""

        if self.errors:
            result += f"Errors: {len(self.errors)}\n"

        if self.warnings:
            result += f"Warnings: {len(self.warnings)}\n"

        return result
