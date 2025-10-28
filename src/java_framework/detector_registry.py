#!/usr/bin/env python3
"""
WHY: Central registry and factory for framework detectors
RESPONSIBILITY: Manages detector lifecycle and orchestrates detection process
PATTERNS: Factory Pattern, Registry Pattern, Strategy Pattern
"""

from typing import Dict, List, Optional

from java_framework.detector_base import FrameworkDetector
from java_framework.jakarta_detector import JakartaEEDetector
from java_framework.micronaut_detector import MicronautDetector
from java_framework.models import DetectionResult, JavaWebFramework
from java_framework.other_frameworks_detector import OtherFrameworksDetector
from java_framework.quarkus_detector import QuarkusDetector
from java_framework.spring_detector import SpringBootDetector, SpringMVCDetector


class DetectorRegistry:
    """
    WHY: Centralized registry for all framework detectors
    RESPONSIBILITY: Creates, registers, and manages framework detectors
    PATTERNS: Factory Pattern + Registry Pattern
    """

    def __init__(self) -> None:
        """Initialize registry with all available detectors"""
        self._detectors: List[FrameworkDetector] = []
        self._register_all_detectors()

    def _register_all_detectors(self) -> None:
        """
        WHY: Registers all available framework detectors
        RESPONSIBILITY: Creates and registers detector instances in priority order
        """
        # Register all detectors
        self._detectors = [
            SpringBootDetector(),
            MicronautDetector(),
            QuarkusDetector(),
            SpringMVCDetector(),
            JakartaEEDetector(),
            OtherFrameworksDetector(),
        ]

        # Sort by priority (lower number = higher priority)
        self._detectors.sort(key=lambda d: d.get_priority())

    def detect_framework(self, dependencies: Dict[str, str]) -> JavaWebFramework:
        """
        WHY: Orchestrates framework detection across all registered detectors
        RESPONSIBILITY: Runs detectors in priority order and returns first match

        Args:
            dependencies: Project dependencies

        Returns:
            Detected JavaWebFramework or UNKNOWN
        """
        # Guard clause: early exit if no dependencies
        if not dependencies:
            return JavaWebFramework.UNKNOWN

        # Run detectors in priority order
        for detector in self._detectors:
            result = detector.detect(dependencies)
            if result:
                return result.framework

        return JavaWebFramework.UNKNOWN

    def detect_with_details(self, dependencies: Dict[str, str]) -> Optional[DetectionResult]:
        """
        WHY: Provides detailed detection information
        RESPONSIBILITY: Returns full DetectionResult with confidence and metadata

        Args:
            dependencies: Project dependencies

        Returns:
            DetectionResult if framework detected, None otherwise
        """
        # Guard clause: early exit if no dependencies
        if not dependencies:
            return None

        # Run detectors in priority order
        for detector in self._detectors:
            result = detector.detect(dependencies)
            if result:
                return result

        return None

    def get_all_detectors(self) -> List[FrameworkDetector]:
        """
        WHY: Provides access to all registered detectors
        RESPONSIBILITY: Returns list of all detectors for testing/debugging

        Returns:
            List of all registered detectors
        """
        return self._detectors.copy()
