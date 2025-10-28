#!/usr/bin/env python3
"""
WHY: Specialized detector for Spring Framework ecosystem
RESPONSIBILITY: Detects Spring Boot and Spring MVC frameworks
PATTERNS: Strategy Pattern, Guard Clauses, Single Responsibility
"""

from typing import Dict, Optional

from java_framework.detector_base import FrameworkDetector
from java_framework.models import DetectionResult, JavaWebFramework


class SpringBootDetector(FrameworkDetector):
    """
    WHY: Detects Spring Boot applications
    RESPONSIBILITY: Identifies Spring Boot projects by analyzing dependencies
    PATTERNS: Strategy Pattern implementation
    """

    def detect(self, dependencies: Dict[str, str]) -> Optional[DetectionResult]:
        """
        WHY: Identifies Spring Boot framework in dependencies
        RESPONSIBILITY: Checks for spring-boot-* dependencies

        Args:
            dependencies: Project dependencies

        Returns:
            DetectionResult if Spring Boot detected, None otherwise
        """
        # Guard clause: early exit if no Spring Boot dependencies
        if not self._has_dependency(dependencies, "spring-boot"):
            return None

        version = self._find_version(dependencies, "spring-boot")

        # Calculate confidence based on multiple indicators
        indicators = [
            self._has_dependency(dependencies, "spring-boot-starter"),
            self._has_dependency(dependencies, "spring-boot-autoconfigure"),
            self._has_dependency(dependencies, "spring-boot-dependencies"),
        ]

        matches = sum(1 for indicator in indicators if indicator)
        confidence = self._calculate_confidence(matches, len(indicators))

        return DetectionResult(
            framework=JavaWebFramework.SPRING_BOOT,
            version=version,
            confidence=confidence,
            detected_by="SpringBootDetector"
        )

    def get_priority(self) -> int:
        """
        WHY: Spring Boot is very common and should be checked early
        RESPONSIBILITY: Returns high priority value

        Returns:
            Priority value (10 = high priority)
        """
        return 10


class SpringMVCDetector(FrameworkDetector):
    """
    WHY: Detects Spring MVC applications (without Spring Boot)
    RESPONSIBILITY: Identifies standalone Spring MVC projects
    PATTERNS: Strategy Pattern implementation
    """

    def detect(self, dependencies: Dict[str, str]) -> Optional[DetectionResult]:
        """
        WHY: Identifies Spring MVC framework in dependencies
        RESPONSIBILITY: Checks for spring-webmvc without spring-boot

        Args:
            dependencies: Project dependencies

        Returns:
            DetectionResult if Spring MVC detected, None otherwise
        """
        # Guard clause: skip if Spring Boot is present
        if self._has_dependency(dependencies, "spring-boot"):
            return None

        # Guard clause: early exit if no Spring Web MVC
        if not self._has_dependency(dependencies, "spring-webmvc"):
            return None

        version = self._find_version(dependencies, "spring-webmvc")

        # Calculate confidence based on Spring components
        indicators = [
            self._has_dependency(dependencies, "spring-web"),
            self._has_dependency(dependencies, "spring-core"),
            self._has_dependency(dependencies, "spring-context"),
        ]

        matches = sum(1 for indicator in indicators if indicator)
        confidence = self._calculate_confidence(matches, len(indicators))

        return DetectionResult(
            framework=JavaWebFramework.SPRING_MVC,
            version=version,
            confidence=confidence,
            detected_by="SpringMVCDetector"
        )

    def get_priority(self) -> int:
        """
        WHY: Spring MVC should be checked after Spring Boot
        RESPONSIBILITY: Returns medium priority value

        Returns:
            Priority value (20 = medium priority)
        """
        return 20
