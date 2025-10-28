#!/usr/bin/env python3
"""
Module: build_managers.recommender

WHY: Recommend appropriate build systems for new projects based on language,
     project type, and best practices. Helps developers choose the right tools.

RESPONSIBILITY:
- Recommend build systems based on language and project type
- Provide rationale for recommendations
- Suggest alternative options
- Apply industry best practices and conventions

PATTERNS:
- Strategy Pattern: Lookup tables for recommendations
- Factory Pattern: Create recommendations with defaults
- Expert System: Codified build system selection knowledge

USAGE:
    from build_managers.recommender import BuildSystemRecommender

    recommender = BuildSystemRecommender()
    recommendation = recommender.recommend(
        language="python",
        project_type="web_api"
    )

    print(f"Recommended: {recommendation.build_system.value}")
    print(f"Rationale: {recommendation.rationale}")
    print(f"Alternatives: {recommendation.alternatives}")
"""

from typing import Dict, List, Tuple
import logging

from build_managers.models import (
    BuildSystem,
    Language,
    ProjectType,
    BuildSystemRecommendation
)


class BuildSystemRecommender:
    """
    Build system recommendation engine.

    WHY: Provides expert guidance on build system selection based on
         industry best practices and project characteristics.

    PATTERNS:
    - Strategy Pattern: Lookup tables instead of if/elif chains
    - Expert System: Codified domain knowledge
    """

    # Recommended build systems by language and project type
    # Strategy Pattern: Dictionary mapping (avoid if/elif chains)
    RECOMMENDATIONS: Dict[Tuple[Language, ProjectType], BuildSystem] = {
        # Java ecosystem
        (Language.JAVA, ProjectType.WEB_API): BuildSystem.MAVEN,
        (Language.JAVA, ProjectType.MICROSERVICE): BuildSystem.GRADLE,
        (Language.JAVA, ProjectType.LIBRARY): BuildSystem.GRADLE,
        (Language.JAVA, ProjectType.CLI_TOOL): BuildSystem.MAVEN,

        # JavaScript/TypeScript ecosystem
        (Language.JAVASCRIPT, ProjectType.WEB_FRONTEND): BuildSystem.NPM,
        (Language.JAVASCRIPT, ProjectType.WEB_API): BuildSystem.NPM,
        (Language.JAVASCRIPT, ProjectType.CLI_TOOL): BuildSystem.NPM,
        (Language.TYPESCRIPT, ProjectType.WEB_FRONTEND): BuildSystem.NPM,
        (Language.TYPESCRIPT, ProjectType.WEB_API): BuildSystem.NPM,
        (Language.TYPESCRIPT, ProjectType.CLI_TOOL): BuildSystem.NPM,

        # Python ecosystem
        (Language.PYTHON, ProjectType.WEB_API): BuildSystem.POETRY,
        (Language.PYTHON, ProjectType.CLI_TOOL): BuildSystem.POETRY,
        (Language.PYTHON, ProjectType.LIBRARY): BuildSystem.POETRY,
        (Language.PYTHON, ProjectType.DATA_SCIENCE): BuildSystem.CONDA,

        # C/C++ ecosystem
        (Language.CPP, ProjectType.LIBRARY): BuildSystem.CMAKE,
        (Language.CPP, ProjectType.CLI_TOOL): BuildSystem.CMAKE,
        (Language.C, ProjectType.LIBRARY): BuildSystem.CMAKE,
        (Language.C, ProjectType.CLI_TOOL): BuildSystem.CMAKE,

        # Rust ecosystem
        (Language.RUST, ProjectType.CLI_TOOL): BuildSystem.CARGO,
        (Language.RUST, ProjectType.LIBRARY): BuildSystem.CARGO,
        (Language.RUST, ProjectType.WEB_API): BuildSystem.CARGO,

        # Go ecosystem
        (Language.GO, ProjectType.WEB_API): BuildSystem.GO_MOD,
        (Language.GO, ProjectType.MICROSERVICE): BuildSystem.GO_MOD,
        (Language.GO, ProjectType.CLI_TOOL): BuildSystem.GO_MOD,

        # .NET ecosystem
        (Language.CSHARP, ProjectType.WEB_API): BuildSystem.DOTNET,
        (Language.CSHARP, ProjectType.LIBRARY): BuildSystem.DOTNET,
        (Language.CSHARP, ProjectType.CLI_TOOL): BuildSystem.DOTNET,

        # Ruby ecosystem
        (Language.RUBY, ProjectType.WEB_API): BuildSystem.BUNDLER,
        (Language.RUBY, ProjectType.CLI_TOOL): BuildSystem.BUNDLER,

        # PHP ecosystem
        (Language.PHP, ProjectType.WEB_API): BuildSystem.COMPOSER,
        (Language.PHP, ProjectType.CLI_TOOL): BuildSystem.COMPOSER,
    }

    # Default build systems by language (fallback when project type unknown)
    # Strategy Pattern: Dictionary mapping
    LANGUAGE_DEFAULTS: Dict[Language, BuildSystem] = {
        Language.JAVA: BuildSystem.MAVEN,
        Language.JAVASCRIPT: BuildSystem.NPM,
        Language.TYPESCRIPT: BuildSystem.NPM,
        Language.PYTHON: BuildSystem.POETRY,
        Language.CPP: BuildSystem.CMAKE,
        Language.C: BuildSystem.CMAKE,
        Language.RUST: BuildSystem.CARGO,
        Language.GO: BuildSystem.GO_MOD,
        Language.CSHARP: BuildSystem.DOTNET,
        Language.RUBY: BuildSystem.BUNDLER,
        Language.PHP: BuildSystem.COMPOSER,
    }

    def __init__(self, logger: logging.Logger = None):
        """
        Initialize build system recommender.

        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)

    def recommend(
        self,
        language: str,
        project_type: str = "unknown"
    ) -> BuildSystemRecommendation:
        """
        Recommend build system for new project.

        WHY: Main entry point for build system recommendations.
        PATTERNS: Strategy pattern with fallback defaults.

        Args:
            language: Programming language (e.g., "python", "java")
            project_type: Type of project (e.g., "web_api", "cli_tool")

        Returns:
            BuildSystemRecommendation with recommended system, rationale, and alternatives

        EXAMPLES:
            recommend("python", "web_api") -> Poetry
            recommend("java", "microservice") -> Gradle
            recommend("rust", "cli_tool") -> Cargo
        """
        # Convert string inputs to enums
        lang_enum = self._parse_language(language)
        type_enum = self._parse_project_type(project_type)

        # Get recommendation from lookup table
        build_system = self._get_recommendation(lang_enum, type_enum)

        # Build recommendation with rationale and alternatives
        rationale = self._get_rationale(build_system, lang_enum, type_enum)
        alternatives = self._get_alternatives(build_system, lang_enum)

        return BuildSystemRecommendation(
            build_system=build_system,
            rationale=rationale,
            alternatives=alternatives,
            confidence=0.9
        )

    def _parse_language(self, language: str) -> Language:
        """
        Parse language string to enum.

        WHY: Converts user input to type-safe enum.
        PATTERNS: Guard clause for error handling.

        Args:
            language: Language string (e.g., "python", "java")

        Returns:
            Language enum value, or Language.UNKNOWN if invalid
        """
        # Guard clause: handle None/empty
        if not language:
            return Language.UNKNOWN

        try:
            return Language(language.lower())
        except ValueError:
            self.logger.warning(f"Unknown language: {language}")
            return Language.UNKNOWN

    def _parse_project_type(self, project_type: str) -> ProjectType:
        """
        Parse project type string to enum.

        WHY: Converts user input to type-safe enum.
        PATTERNS: Guard clause for error handling.

        Args:
            project_type: Project type string (e.g., "web_api", "cli_tool")

        Returns:
            ProjectType enum value, or ProjectType.UNKNOWN if invalid
        """
        # Guard clause: handle None/empty
        if not project_type:
            return ProjectType.UNKNOWN

        try:
            return ProjectType(project_type.lower())
        except ValueError:
            self.logger.warning(f"Unknown project type: {project_type}")
            return ProjectType.UNKNOWN

    def _get_recommendation(
        self,
        language: Language,
        project_type: ProjectType
    ) -> BuildSystem:
        """
        Get build system recommendation from lookup table.

        WHY: Strategy pattern with fallback for unknown combinations.

        Args:
            language: Language enum
            project_type: Project type enum

        Returns:
            Recommended BuildSystem
        """
        # Try specific recommendation first
        recommendation = self.RECOMMENDATIONS.get((language, project_type))

        # Guard clause: return if found
        if recommendation:
            return recommendation

        # Fallback to language default
        return self._get_default_for_language(language)

    def _get_default_for_language(self, language: Language) -> BuildSystem:
        """
        Get default build system for language.

        WHY: Provides fallback recommendation when no specific project type match.
        PATTERNS: Strategy pattern (dictionary mapping instead of if/elif chain).

        Args:
            language: Language enum value

        Returns:
            Default BuildSystem for the language, or BuildSystem.UNKNOWN
        """
        return self.LANGUAGE_DEFAULTS.get(language, BuildSystem.UNKNOWN)

    def _get_rationale(
        self,
        build_system: BuildSystem,
        language: Language,
        project_type: ProjectType
    ) -> str:
        """
        Get rationale for build system choice.

        WHY: Explains reasoning to help users understand recommendations.
        PATTERNS: Strategy pattern (dictionary mapping).

        Args:
            build_system: Recommended build system
            language: Target programming language
            project_type: Type of project

        Returns:
            Human-readable rationale string
        """
        # Strategy pattern: Dictionary mapping (avoid if/elif chain)
        rationales: Dict[BuildSystem, str] = {
            BuildSystem.MAVEN: "Maven is the industry standard for Java projects with convention-over-configuration",
            BuildSystem.GRADLE: "Gradle provides flexible build scripting for complex Java projects",
            BuildSystem.NPM: "npm is the default package manager for Node.js/JavaScript ecosystem",
            BuildSystem.POETRY: "Poetry provides modern dependency management and packaging for Python",
            BuildSystem.CMAKE: "CMake is the cross-platform build system standard for C/C++",
            BuildSystem.CARGO: "Cargo is the official Rust package manager and build tool",
            BuildSystem.GO_MOD: "Go modules is the standard dependency management for Go",
            BuildSystem.DOTNET: "dotnet CLI is the official build tool for .NET projects",
            BuildSystem.BUNDLER: "Bundler is the standard gem dependency manager for Ruby",
            BuildSystem.COMPOSER: "Composer is the standard dependency manager for PHP",
        }

        return rationales.get(
            build_system,
            f"{build_system.value} is recommended for {language.value} {project_type.value} projects"
        )

    def _get_alternatives(
        self,
        build_system: BuildSystem,
        language: Language
    ) -> List[BuildSystem]:
        """
        Get alternative build systems.

        WHY: Provides users with alternative options for their use case.
        PATTERNS: Strategy pattern (dictionary mapping with tuple keys).

        Args:
            build_system: Primary recommended build system
            language: Target programming language

        Returns:
            List of alternative BuildSystem options (empty if none)
        """
        # Strategy pattern: Dictionary mapping with tuple keys
        alternatives_map: Dict[Tuple[BuildSystem, Language], List[BuildSystem]] = {
            (BuildSystem.MAVEN, Language.JAVA): [BuildSystem.GRADLE],
            (BuildSystem.GRADLE, Language.JAVA): [BuildSystem.MAVEN],
            (BuildSystem.NPM, Language.JAVASCRIPT): [BuildSystem.YARN, BuildSystem.PNPM],
            (BuildSystem.NPM, Language.TYPESCRIPT): [BuildSystem.YARN, BuildSystem.PNPM],
            (BuildSystem.POETRY, Language.PYTHON): [BuildSystem.PIP, BuildSystem.PIPENV],
            (BuildSystem.PIP, Language.PYTHON): [BuildSystem.POETRY, BuildSystem.PIPENV],
        }

        return alternatives_map.get((build_system, language), [])
