#!/usr/bin/env python3
"""
Module: build_managers.detector

WHY: Automatically detect build systems from project files and directory structure.
     Enables Artemis to work with existing projects without manual configuration.

RESPONSIBILITY:
- Scan project directory for build system indicators (pom.xml, package.json, etc.)
- Calculate confidence scores based on evidence strength
- Detect primary programming language from source files
- Infer project type from directory structure and file patterns

PATTERNS:
- Strategy Pattern: Different detection strategies per build system
- Evidence-Based: Confidence calculated from multiple indicators
- Guard Clauses: Early returns for efficiency

USAGE:
    from build_managers.detector import BuildSystemDetector
    from pathlib import Path

    detector = BuildSystemDetector(project_dir=Path("/path/to/project"))
    detection = detector.detect()

    print(f"Build System: {detection.build_system.value}")
    print(f"Confidence: {detection.confidence:.0%}")
    print(f"Evidence: {detection.evidence}")
"""

from pathlib import Path
from typing import Dict, List, Optional
import logging

from build_managers.models import (
    BuildSystem,
    Language,
    ProjectType,
    BuildSystemDetection
)


class BuildSystemDetector:
    """
    Build system detection from project files.

    WHY: Automatically identifies build system to enable zero-configuration
         operation for existing projects.

    PATTERNS:
    - Strategy Pattern: Different detection strategies per build system
    - Evidence-Based Confidence: Multiple indicators increase confidence
    - Guard Clauses: Early returns for performance
    """

    # Build system file indicators (Strategy Pattern: dispatch table)
    BUILD_INDICATORS: Dict[BuildSystem, List[str]] = {
        BuildSystem.MAVEN: ["pom.xml"],
        BuildSystem.GRADLE: ["build.gradle", "build.gradle.kts", "settings.gradle"],
        BuildSystem.ANT: ["build.xml"],
        BuildSystem.NPM: ["package.json", "package-lock.json"],
        BuildSystem.YARN: ["yarn.lock"],
        BuildSystem.PNPM: ["pnpm-lock.yaml"],
        BuildSystem.PIP: ["requirements.txt", "setup.py"],
        BuildSystem.POETRY: ["pyproject.toml", "poetry.lock"],
        BuildSystem.PIPENV: ["Pipfile", "Pipfile.lock"],
        BuildSystem.CONDA: ["environment.yml", "conda.yml"],
        BuildSystem.CMAKE: ["CMakeLists.txt"],
        BuildSystem.MAKE: ["Makefile"],
        BuildSystem.CARGO: ["Cargo.toml", "Cargo.lock"],
        BuildSystem.GO_MOD: ["go.mod", "go.sum"],
        BuildSystem.DOTNET: ["*.csproj", "*.sln"],
        BuildSystem.BUNDLER: ["Gemfile", "Gemfile.lock"],
        BuildSystem.COMPOSER: ["composer.json", "composer.lock"],
    }

    # Language detection patterns (Strategy Pattern: dispatch table)
    LANGUAGE_PATTERNS: Dict[Language, List[str]] = {
        Language.JAVA: ["**/*.java"],
        Language.JAVASCRIPT: ["**/*.js", "**/*.jsx"],
        Language.TYPESCRIPT: ["**/*.ts", "**/*.tsx"],
        Language.PYTHON: ["**/*.py"],
        Language.CPP: ["**/*.cpp", "**/*.cc", "**/*.cxx", "**/*.hpp"],
        Language.C: ["**/*.c", "**/*.h"],
        Language.RUST: ["**/*.rs"],
        Language.GO: ["**/*.go"],
        Language.CSHARP: ["**/*.cs"],
        Language.RUBY: ["**/*.rb"],
        Language.PHP: ["**/*.php"],
    }

    def __init__(
        self,
        project_dir: Optional[Path] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize build system detector.

        Args:
            project_dir: Project root directory (defaults to current directory)
            logger: Optional logger instance
        """
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.logger = logger or logging.getLogger(__name__)

    def detect(self) -> BuildSystemDetection:
        """
        Automatically detect build system from project files.

        WHY: Main entry point for build system detection.
        PATTERNS: Evidence-based confidence scoring with fallback to UNKNOWN.

        Returns:
            BuildSystemDetection with detected build system, confidence, and evidence

        ALGORITHM:
        1. Scan for build system indicators (pom.xml, package.json, etc.)
        2. Calculate confidence based on evidence strength
        3. Select highest confidence detection
        4. Detect language and project type
        5. Return structured result
        """
        detections = self._detect_all_build_systems()

        # Guard clause: early return if no detections
        if not detections:
            return self._create_unknown_detection()

        # Select best detection (highest confidence)
        best_detection = max(detections, key=lambda d: d.confidence)

        # Enrich with language and project type
        best_detection.language = self._detect_language()
        best_detection.project_type = self._detect_project_type()

        return best_detection

    def _detect_all_build_systems(self) -> List[BuildSystemDetection]:
        """
        Detect all build systems present in project.

        WHY: Some projects may have multiple build systems (e.g., Java + npm for frontend).
             We detect all and return the strongest match.

        Returns:
            List of BuildSystemDetection results (may be empty)
        """
        detections = []

        for build_system, indicators in self.BUILD_INDICATORS.items():
            evidence = self._collect_evidence_for_indicators(indicators)

            # Guard clause: skip if no evidence
            if not evidence:
                continue

            # Calculate confidence based on evidence strength
            confidence = self._calculate_confidence(evidence, indicators)

            detections.append(BuildSystemDetection(
                build_system=build_system,
                confidence=confidence,
                evidence=evidence
            ))

        return detections

    def _collect_evidence_for_indicators(self, indicators: List[str]) -> List[str]:
        """
        Collect evidence for build system indicators.

        WHY: Validates that build system files exist in the project directory.
        PERFORMANCE: Uses generator expressions for memory efficiency.

        Args:
            indicators: List of file patterns to check (supports glob patterns)

        Returns:
            List of matching file paths as evidence
        """
        evidence = []

        for indicator in indicators:
            # Guard clause: handle glob patterns
            if "*" in indicator:
                matches = list(self.project_dir.glob(indicator))
                if matches:
                    evidence.extend([
                        str(m.relative_to(self.project_dir)) for m in matches
                    ])
                continue

            # Handle direct file paths
            file_path = self.project_dir / indicator
            if file_path.exists():
                evidence.append(indicator)

        return evidence

    def _calculate_confidence(
        self,
        evidence: List[str],
        indicators: List[str]
    ) -> float:
        """
        Calculate confidence score based on evidence strength.

        WHY: Multiple indicators increase confidence in detection.
        ALGORITHM: Base confidence 0.4, +0.3 per additional indicator, capped at 1.0

        Args:
            evidence: List of found indicators
            indicators: List of all possible indicators for this build system

        Returns:
            Confidence score between 0.0 and 1.0

        EXAMPLES:
        - 1 indicator found: 0.4 + 0.3 = 0.7
        - 2 indicators found: 0.4 + 0.6 = 1.0
        - 3+ indicators found: 1.0 (capped)
        """
        base_confidence = 0.4
        evidence_boost = len(evidence) * 0.3
        return min(1.0, base_confidence + evidence_boost)

    def _create_unknown_detection(self) -> BuildSystemDetection:
        """
        Create detection result for unknown build system.

        WHY: Provides consistent return type even when no build system detected.

        Returns:
            BuildSystemDetection with UNKNOWN values
        """
        return BuildSystemDetection(
            build_system=BuildSystem.UNKNOWN,
            confidence=0.0,
            evidence=[]
        )

    def _detect_language(self) -> Language:
        """
        Detect primary programming language.

        WHY: Identifies the main language to provide appropriate build system
             recommendations and configuration.

        PERFORMANCE: O(n) file counting with early continue for zero matches.

        Returns:
            Language enum for the predominant language, or Language.UNKNOWN
        """
        language_counts: Dict[Language, int] = {}

        for language, patterns in self.LANGUAGE_PATTERNS.items():
            count = self._count_files_for_patterns(patterns)

            # Guard clause: skip languages with no files
            if count == 0:
                continue

            language_counts[language] = count

        # Guard clause: early return if no languages detected
        if not language_counts:
            return Language.UNKNOWN

        # Return language with most files
        return max(language_counts.items(), key=lambda x: x[1])[0]

    def _count_files_for_patterns(self, patterns: List[str]) -> int:
        """
        Count files matching given patterns.

        WHY: Helper method to count language files for language detection.
        PERFORMANCE: Uses glob for efficient file system traversal.

        Args:
            patterns: List of glob patterns to match (e.g., ["**/*.py"])

        Returns:
            Total count of files matching any pattern
        """
        count = 0
        for pattern in patterns:
            count += len(list(self.project_dir.glob(pattern)))
        return count

    def _detect_project_type(self) -> ProjectType:
        """
        Detect project type from structure and files.

        WHY: Identifies project type to provide appropriate build recommendations.
        PERFORMANCE: Uses any() for short-circuit evaluation (stops at first match).

        Returns:
            ProjectType enum value
        """
        # Check for web indicators (any() short-circuits on first True)
        has_web = any([
            (self.project_dir / "public").exists(),
            (self.project_dir / "static").exists(),
            (self.project_dir / "templates").exists(),
            bool(list(self.project_dir.glob("**/*Controller.java"))),
            bool(list(self.project_dir.glob("**/routes.py"))),
        ])

        # Check for API indicators
        has_api = any([
            bool(list(self.project_dir.glob("**/api/**"))),
            bool(list(self.project_dir.glob("**/endpoints/**"))),
        ])

        # Check for CLI indicators
        has_cli = any([
            (self.project_dir / "bin").exists(),
            (self.project_dir / "cli.py").exists(),
            (self.project_dir / "main.rs").exists(),
        ])

        return self._determine_project_type(has_web, has_api, has_cli)

    def _determine_project_type(
        self,
        has_web: bool,
        has_api: bool,
        has_cli: bool
    ) -> ProjectType:
        """
        Determine project type based on indicators.

        WHY: Classifies project type to provide appropriate build system
             recommendations.

        PATTERNS: Guard clauses with early returns (no nested ifs).

        Args:
            has_web: True if web indicators found
            has_api: True if API indicators found
            has_cli: True if CLI indicators found

        Returns:
            ProjectType enum value
        """
        # Guard clauses with early returns (avoid nested ifs)
        if has_web and has_api:
            return ProjectType.WEB_FULLSTACK

        if has_api:
            return ProjectType.WEB_API

        if has_web:
            return ProjectType.WEB_FRONTEND

        if has_cli:
            return ProjectType.CLI_TOOL

        return ProjectType.LIBRARY
