#!/usr/bin/env python3
"""
WHY: Specialized detector for Quarkus framework
RESPONSIBILITY: Detects Quarkus applications
PATTERNS: Strategy Pattern, Guard Clauses
"""

from typing import Dict, Optional

from java_framework.detector_base import FrameworkDetector
from java_framework.models import DetectionResult, JavaWebFramework


class QuarkusDetector(FrameworkDetector):
    """
    WHY: Detects Quarkus applications
    RESPONSIBILITY: Identifies Quarkus projects by analyzing dependencies
    PATTERNS: Strategy Pattern implementation
    """

    def detect(self, dependencies: Dict[str, str]) -> Optional[DetectionResult]:
        """
        WHY: Identifies Quarkus framework in dependencies
        RESPONSIBILITY: Checks for quarkus-* dependencies

        Args:
            dependencies: Project dependencies

        Returns:
            DetectionResult if Quarkus detected, None otherwise
        """
        # Guard clause: early exit if no Quarkus dependencies
        if not self._has_dependency(dependencies, "quarkus"):
            return None

        version = self._find_version(dependencies, "quarkus-core")
        if not version:
            version = self._find_version(dependencies, "quarkus-arc")

        # Calculate confidence based on Quarkus components
        indicators = [
            self._has_dependency(dependencies, "quarkus-core"),
            self._has_dependency(dependencies, "quarkus-arc"),
            self._has_dependency(dependencies, "quarkus-resteasy"),
            self._has_dependency(dependencies, "io.quarkus"),
        ]

        matches = sum(1 for indicator in indicators if indicator)
        confidence = self._calculate_confidence(matches, len(indicators))

        return DetectionResult(
            framework=JavaWebFramework.QUARKUS,
            version=version,
            confidence=confidence,
            detected_by="QuarkusDetector"
        )

    def get_priority(self) -> int:
        """
        WHY: Quarkus is a modern framework that should be checked early
        RESPONSIBILITY: Returns high priority value

        Returns:
            Priority value (15 = high priority)
        """
        return 15
