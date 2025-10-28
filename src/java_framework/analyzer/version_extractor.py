#!/usr/bin/env python3
"""
WHY: Extracts version information from dependencies
RESPONSIBILITY: Finds and extracts version numbers for frameworks and web servers
PATTERNS: Strategy Pattern (dispatch tables), Guard Clauses, DRY Principle
"""

from typing import Dict, Optional

from java_framework.models import JavaWebFramework, WebServer


class VersionExtractor:
    """
    WHY: Extracts version information for detected technologies
    RESPONSIBILITY: Maps frameworks/servers to version keywords and extracts versions
    PATTERNS: Strategy Pattern with dispatch tables for extensible version extraction
    """

    def __init__(self):
        """Initialize version extractor with dispatch tables"""
        # Dispatch table for framework version keywords
        self._framework_keywords: Dict[JavaWebFramework, str] = {
            JavaWebFramework.SPRING_BOOT: "spring-boot",
            JavaWebFramework.MICRONAUT: "micronaut-core",
            JavaWebFramework.QUARKUS: "quarkus-core",
        }

        # Dispatch table for server version keywords
        self._server_keywords: Dict[WebServer, str] = {
            WebServer.TOMCAT: "tomcat",
            WebServer.JETTY: "jetty",
            WebServer.UNDERTOW: "undertow",
            WebServer.NETTY: "netty",
        }

    def get_framework_version(
        self,
        framework: JavaWebFramework,
        dependencies: Dict[str, str]
    ) -> Optional[str]:
        """
        WHY: Extracts version for detected framework using dispatch table
        RESPONSIBILITY: Maps framework to version extraction strategy

        Args:
            framework: Detected framework
            dependencies: Project dependencies

        Returns:
            Version string if found, None otherwise
        """
        keyword = self._framework_keywords.get(framework)
        if not keyword:
            return None

        return self._find_version_by_keyword(dependencies, keyword)

    def get_web_server_version(
        self,
        web_server: WebServer,
        dependencies: Dict[str, str]
    ) -> Optional[str]:
        """
        WHY: Extracts web server version
        RESPONSIBILITY: Maps server to version keyword and extracts version

        Args:
            web_server: Detected web server
            dependencies: Project dependencies

        Returns:
            Version string if found, None otherwise
        """
        keyword = self._server_keywords.get(web_server)
        if not keyword:
            return None

        return self._find_version_by_keyword(dependencies, keyword)

    def _find_version_by_keyword(
        self,
        dependencies: Dict[str, str],
        keyword: str
    ) -> Optional[str]:
        """
        WHY: Common utility for version lookup (DRY principle)
        RESPONSIBILITY: Finds version of first dependency containing keyword

        Args:
            dependencies: Dependencies dictionary
            keyword: Keyword to search for

        Returns:
            Version string if found, None otherwise
        """
        for dep, ver in dependencies.items():
            if keyword in dep:
                return ver
        return None
