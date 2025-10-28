#!/usr/bin/env python3
"""
WHY: Abstract base for all framework detectors
RESPONSIBILITY: Defines the contract for framework detection strategies
PATTERNS: Strategy Pattern, Template Method Pattern, Guard Clauses
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional

from java_framework.models import DetectionResult, JavaWebFramework


class FrameworkDetector(ABC):
    """
    WHY: Base interface for all framework detection strategies
    RESPONSIBILITY: Enforces consistent detection API across all framework detectors
    PATTERNS: Strategy Pattern - allows pluggable detection algorithms
    """

    @abstractmethod
    def detect(self, dependencies: Dict[str, str]) -> Optional[DetectionResult]:
        """
        WHY: Core detection method for framework identification
        RESPONSIBILITY: Analyzes dependencies and returns detection result if framework is found

        Args:
            dependencies: Dict mapping dependency keys (groupId:artifactId) to versions

        Returns:
            DetectionResult if framework detected, None otherwise
        """
        pass

    @abstractmethod
    def get_priority(self) -> int:
        """
        WHY: Determines the order of detector execution
        RESPONSIBILITY: Returns priority value (lower = higher priority)

        Returns:
            Priority value (0-100, where 0 is highest priority)
        """
        pass

    def _has_dependency(self, dependencies: Dict[str, str], keyword: str) -> bool:
        """
        WHY: Common utility for dependency checking
        RESPONSIBILITY: Checks if any dependency contains the given keyword

        Args:
            dependencies: Dependency dictionary
            keyword: Keyword to search for

        Returns:
            True if keyword found in any dependency
        """
        return any(keyword in dep for dep in dependencies)

    def _find_version(self, dependencies: Dict[str, str], keyword: str) -> Optional[str]:
        """
        WHY: Common utility for version extraction
        RESPONSIBILITY: Finds version of first dependency matching keyword

        Args:
            dependencies: Dependency dictionary
            keyword: Keyword to search for

        Returns:
            Version string if found, None otherwise
        """
        for dep, version in dependencies.items():
            if keyword in dep:
                return version
        return None

    def _calculate_confidence(self, matches: int, total_indicators: int) -> float:
        """
        WHY: Standardized confidence calculation
        RESPONSIBILITY: Calculates detection confidence based on matching indicators

        Args:
            matches: Number of matching indicators
            total_indicators: Total number of possible indicators

        Returns:
            Confidence score between 0.0 and 1.0
        """
        if total_indicators == 0:
            return 0.0
        return min(1.0, matches / total_indicators)
