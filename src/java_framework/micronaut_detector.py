#!/usr/bin/env python3
"""
WHY: Specialized detector for Micronaut framework
RESPONSIBILITY: Detects Micronaut applications
PATTERNS: Strategy Pattern, Guard Clauses
"""

from typing import Dict, Optional

from java_framework.detector_base import FrameworkDetector
from java_framework.models import DetectionResult, JavaWebFramework


class MicronautDetector(FrameworkDetector):
    """
    WHY: Detects Micronaut applications
    RESPONSIBILITY: Identifies Micronaut projects by analyzing dependencies
    PATTERNS: Strategy Pattern implementation
    """

    def detect(self, dependencies: Dict[str, str]) -> Optional[DetectionResult]:
        """
        WHY: Identifies Micronaut framework in dependencies
        RESPONSIBILITY: Checks for micronaut-* dependencies

        Args:
            dependencies: Project dependencies

        Returns:
            DetectionResult if Micronaut detected, None otherwise
        """
        # Guard clause: early exit if no Micronaut dependencies
        if not self._has_dependency(dependencies, "micronaut"):
            return None

        version = self._find_version(dependencies, "micronaut-core")
        if not version:
            version = self._find_version(dependencies, "micronaut-runtime")

        # Calculate confidence based on Micronaut components
        indicators = [
            self._has_dependency(dependencies, "micronaut-core"),
            self._has_dependency(dependencies, "micronaut-runtime"),
            self._has_dependency(dependencies, "micronaut-http"),
            self._has_dependency(dependencies, "micronaut-inject"),
        ]

        matches = sum(1 for indicator in indicators if indicator)
        confidence = self._calculate_confidence(matches, len(indicators))

        return DetectionResult(
            framework=JavaWebFramework.MICRONAUT,
            version=version,
            confidence=confidence,
            detected_by="MicronautDetector"
        )

    def get_priority(self) -> int:
        """
        WHY: Micronaut is a modern framework that should be checked early
        RESPONSIBILITY: Returns high priority value

        Returns:
            Priority value (15 = high priority)
        """
        return 15
