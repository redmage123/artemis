#!/usr/bin/env python3
"""
WHY: Specialized detector for Jakarta EE (formerly Java EE)
RESPONSIBILITY: Detects Jakarta EE applications and specifications
PATTERNS: Strategy Pattern, Guard Clauses
"""

from typing import Dict, Optional

from java_framework.detector_base import FrameworkDetector
from java_framework.models import DetectionResult, JavaWebFramework


class JakartaEEDetector(FrameworkDetector):
    """
    WHY: Detects Jakarta EE applications
    RESPONSIBILITY: Identifies Jakarta EE (and legacy Java EE) projects
    PATTERNS: Strategy Pattern implementation
    """

    def detect(self, dependencies: Dict[str, str]) -> Optional[DetectionResult]:
        """
        WHY: Identifies Jakarta EE framework in dependencies
        RESPONSIBILITY: Checks for Jakarta EE and Java EE API dependencies

        Args:
            dependencies: Project dependencies

        Returns:
            DetectionResult if Jakarta EE detected, None otherwise
        """
        # Check for Jakarta EE API
        has_jakarta = self._has_dependency(dependencies, "jakarta.jakartaee-api")

        # Check for legacy Java EE API
        has_javaee = self._has_dependency(dependencies, "javax.javaee-api")

        # Guard clause: early exit if no Jakarta/Java EE
        if not has_jakarta and not has_javaee:
            return None

        # Try to find version
        version = self._find_version(dependencies, "jakarta.jakartaee-api")
        if not version:
            version = self._find_version(dependencies, "javax.javaee-api")

        # Calculate confidence based on EE specifications
        indicators = [
            has_jakarta or has_javaee,
            self._has_dependency(dependencies, "jakarta.servlet-api"),
            self._has_dependency(dependencies, "jakarta.persistence-api"),
            self._has_dependency(dependencies, "jakarta.enterprise.cdi-api"),
        ]

        matches = sum(1 for indicator in indicators if indicator)
        confidence = self._calculate_confidence(matches, len(indicators))

        return DetectionResult(
            framework=JavaWebFramework.JAKARTA_EE,
            version=version,
            confidence=confidence,
            detected_by="JakartaEEDetector"
        )

    def get_priority(self) -> int:
        """
        WHY: Jakarta EE should be checked after modern frameworks
        RESPONSIBILITY: Returns medium priority value

        Returns:
            Priority value (30 = medium priority)
        """
        return 30
