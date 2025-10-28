#!/usr/bin/env python3
"""
WHY: Detectors for less common Java web frameworks
RESPONSIBILITY: Detects Play, Dropwizard, Vert.x, Spark, Struts, JSF, Vaadin, and Grails
PATTERNS: Strategy Pattern, Guard Clauses, Dispatch Tables
"""

from typing import Callable, Dict, List, Optional

from java_framework.detector_base import FrameworkDetector
from java_framework.models import DetectionResult, JavaWebFramework


class OtherFrameworksDetector(FrameworkDetector):
    """
    WHY: Multi-framework detector for less common frameworks
    RESPONSIBILITY: Handles detection of multiple frameworks using dispatch table
    PATTERNS: Strategy Pattern + Dispatch Table Pattern
    """

    def __init__(self) -> None:
        """Initialize detector with framework detection dispatch table"""
        self._detection_table: Dict[JavaWebFramework, Callable[[Dict[str, str]], Optional[DetectionResult]]] = {
            JavaWebFramework.PLAY: self._detect_play,
            JavaWebFramework.DROPWIZARD: self._detect_dropwizard,
            JavaWebFramework.VERTX: self._detect_vertx,
            JavaWebFramework.SPARK: self._detect_spark,
            JavaWebFramework.STRUTS: self._detect_struts,
            JavaWebFramework.JSF: self._detect_jsf,
            JavaWebFramework.VAADIN: self._detect_vaadin,
            JavaWebFramework.GRAILS: self._detect_grails,
        }

    def detect(self, dependencies: Dict[str, str]) -> Optional[DetectionResult]:
        """
        WHY: Orchestrates detection across multiple frameworks
        RESPONSIBILITY: Iterates through detection table to find matching framework

        Args:
            dependencies: Project dependencies

        Returns:
            First DetectionResult found, or None
        """
        for framework, detector_func in self._detection_table.items():
            result = detector_func(dependencies)
            if result:
                return result

        return None

    def get_priority(self) -> int:
        """
        WHY: Less common frameworks should be checked after major ones
        RESPONSIBILITY: Returns low priority value

        Returns:
            Priority value (40 = low priority)
        """
        return 40

    def _detect_play(self, dependencies: Dict[str, str]) -> Optional[DetectionResult]:
        """
        WHY: Detects Play Framework
        RESPONSIBILITY: Checks for Play-specific dependencies

        Args:
            dependencies: Project dependencies

        Returns:
            DetectionResult if Play detected, None otherwise
        """
        # Guard clause: check for Play indicators
        if not (self._has_dependency(dependencies, "play") and self._has_dependency(dependencies, "typesafe")):
            return None

        version = self._find_version(dependencies, "play")

        return DetectionResult(
            framework=JavaWebFramework.PLAY,
            version=version,
            confidence=0.9,
            detected_by="OtherFrameworksDetector:Play"
        )

    def _detect_dropwizard(self, dependencies: Dict[str, str]) -> Optional[DetectionResult]:
        """
        WHY: Detects Dropwizard framework
        RESPONSIBILITY: Checks for Dropwizard dependencies

        Args:
            dependencies: Project dependencies

        Returns:
            DetectionResult if Dropwizard detected, None otherwise
        """
        # Guard clause
        if not self._has_dependency(dependencies, "dropwizard"):
            return None

        version = self._find_version(dependencies, "dropwizard-core")

        return DetectionResult(
            framework=JavaWebFramework.DROPWIZARD,
            version=version,
            confidence=0.95,
            detected_by="OtherFrameworksDetector:Dropwizard"
        )

    def _detect_vertx(self, dependencies: Dict[str, str]) -> Optional[DetectionResult]:
        """
        WHY: Detects Vert.x framework
        RESPONSIBILITY: Checks for Vert.x dependencies

        Args:
            dependencies: Project dependencies

        Returns:
            DetectionResult if Vert.x detected, None otherwise
        """
        # Guard clause
        if not self._has_dependency(dependencies, "vertx"):
            return None

        version = self._find_version(dependencies, "vertx-core")

        return DetectionResult(
            framework=JavaWebFramework.VERTX,
            version=version,
            confidence=0.9,
            detected_by="OtherFrameworksDetector:Vertx"
        )

    def _detect_spark(self, dependencies: Dict[str, str]) -> Optional[DetectionResult]:
        """
        WHY: Detects Spark Framework (not Apache Spark)
        RESPONSIBILITY: Checks for Spark Framework dependencies

        Args:
            dependencies: Project dependencies

        Returns:
            DetectionResult if Spark Framework detected, None otherwise
        """
        # Guard clause: check for Spark Framework specific indicators
        if not (self._has_dependency(dependencies, "spark-core") and self._has_dependency(dependencies, "sparkjava")):
            return None

        version = self._find_version(dependencies, "spark-core")

        return DetectionResult(
            framework=JavaWebFramework.SPARK,
            version=version,
            confidence=0.85,
            detected_by="OtherFrameworksDetector:Spark"
        )

    def _detect_struts(self, dependencies: Dict[str, str]) -> Optional[DetectionResult]:
        """
        WHY: Detects Apache Struts framework
        RESPONSIBILITY: Checks for Struts dependencies

        Args:
            dependencies: Project dependencies

        Returns:
            DetectionResult if Struts detected, None otherwise
        """
        # Guard clause
        if not self._has_dependency(dependencies, "struts"):
            return None

        version = self._find_version(dependencies, "struts-core")
        if not version:
            version = self._find_version(dependencies, "struts2-core")

        return DetectionResult(
            framework=JavaWebFramework.STRUTS,
            version=version,
            confidence=0.9,
            detected_by="OtherFrameworksDetector:Struts"
        )

    def _detect_jsf(self, dependencies: Dict[str, str]) -> Optional[DetectionResult]:
        """
        WHY: Detects JavaServer Faces framework
        RESPONSIBILITY: Checks for JSF dependencies

        Args:
            dependencies: Project dependencies

        Returns:
            DetectionResult if JSF detected, None otherwise
        """
        # Guard clause: check for JSF indicators
        has_jsf = self._has_dependency(dependencies, "jsf")
        has_mojarra = self._has_dependency(dependencies, "mojarra")
        has_myfaces = self._has_dependency(dependencies, "myfaces")

        if not (has_jsf or has_mojarra or has_myfaces):
            return None

        version = self._find_version(dependencies, "jakarta.faces-api")
        if not version:
            version = self._find_version(dependencies, "javax.faces-api")

        return DetectionResult(
            framework=JavaWebFramework.JSF,
            version=version,
            confidence=0.85,
            detected_by="OtherFrameworksDetector:JSF"
        )

    def _detect_vaadin(self, dependencies: Dict[str, str]) -> Optional[DetectionResult]:
        """
        WHY: Detects Vaadin framework
        RESPONSIBILITY: Checks for Vaadin dependencies

        Args:
            dependencies: Project dependencies

        Returns:
            DetectionResult if Vaadin detected, None otherwise
        """
        # Guard clause
        if not self._has_dependency(dependencies, "vaadin"):
            return None

        version = self._find_version(dependencies, "vaadin-core")

        return DetectionResult(
            framework=JavaWebFramework.VAADIN,
            version=version,
            confidence=0.95,
            detected_by="OtherFrameworksDetector:Vaadin"
        )

    def _detect_grails(self, dependencies: Dict[str, str]) -> Optional[DetectionResult]:
        """
        WHY: Detects Grails framework
        RESPONSIBILITY: Checks for Grails dependencies

        Args:
            dependencies: Project dependencies

        Returns:
            DetectionResult if Grails detected, None otherwise
        """
        # Guard clause
        if not self._has_dependency(dependencies, "grails"):
            return None

        version = self._find_version(dependencies, "grails-core")

        return DetectionResult(
            framework=JavaWebFramework.GRAILS,
            version=version,
            confidence=0.9,
            detected_by="OtherFrameworksDetector:Grails"
        )
