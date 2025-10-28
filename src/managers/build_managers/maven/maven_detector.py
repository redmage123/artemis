#!/usr/bin/env python3
"""
Module: Maven Detector and Validator

WHY: Detect Maven installation, Maven Wrapper, and validate Maven project structure.
RESPONSIBILITY: Verify Maven availability and project validity before operations.
PATTERNS: Validator pattern, Guard clause pattern.

Dependencies: subprocess for Maven version check
"""

import subprocess
import re
from pathlib import Path
from typing import Optional, Tuple
import logging


class MavenDetector:
    """
    Maven installation and project detector.

    WHY: Need to verify Maven is available before attempting builds.
    RESPONSIBILITY:
    - Detect Maven installation and version
    - Check for Maven Wrapper (mvnw)
    - Validate Maven project structure (pom.xml exists)

    PATTERNS:
    - Validator pattern: Pre-execution validation
    - Guard clause: Fail fast if requirements not met

    Maven vs Maven Wrapper:
    - Maven: Requires system-wide installation (mvn command)
    - Maven Wrapper: Project-specific Maven version (mvnw script)
    - Wrapper ensures consistent Maven version across team
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize Maven detector.

        Args:
            logger: Optional logger for output
        """
        self.logger = logger or logging.getLogger(__name__)
        self.maven_version: Optional[str] = None

    def validate_maven_installation(self) -> None:
        """
        Validate that Maven is installed and accessible.

        WHY: Guard clause - fail fast if Maven not available.
        RESPONSIBILITY: Check Maven installation and extract version.

        Raises:
            RuntimeError: If Maven is not installed or not accessible
        """
        try:
            result = subprocess.run(
                ["mvn", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                raise RuntimeError("Maven is not properly installed")

            # Parse Maven version
            self.maven_version = self._extract_maven_version(result.stdout)
            if self.maven_version:
                self.logger.info(f"Detected Maven version: {self.maven_version}")

        except FileNotFoundError:
            raise RuntimeError(
                "Maven (mvn) not found in PATH. Please install Maven: "
                "https://maven.apache.org/install.html"
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("Maven version check timed out")

    def _extract_maven_version(self, version_output: str) -> Optional[str]:
        """
        Extract Maven version from --version output.

        WHY: Version information useful for diagnostics and feature detection.
        RESPONSIBILITY: Parse version string from Maven output.

        Args:
            version_output: Output from 'mvn --version'

        Returns:
            Version string (e.g., "3.9.5") or None
        """
        version_match = re.search(r'Apache Maven (\d+\.\d+\.\d+)', version_output)
        return version_match.group(1) if version_match else None

    def is_maven_project(self, project_dir: Path) -> bool:
        """
        Check if directory is a Maven project.

        WHY: Guard clause - verify project structure before operations.
        RESPONSIBILITY: Check for pom.xml existence.

        Args:
            project_dir: Directory to check

        Returns:
            True if pom.xml exists
        """
        return (project_dir / "pom.xml").exists()

    def detect_maven_wrapper(self, project_dir: Path) -> Tuple[bool, Optional[Path]]:
        """
        Detect Maven Wrapper in project.

        WHY: Maven Wrapper ensures consistent Maven version across team.
             Should prefer mvnw over mvn if available.
        RESPONSIBILITY: Check for mvnw/mvnw.cmd scripts.

        Maven Wrapper Files:
        - mvnw: Unix/Linux/Mac wrapper script
        - mvnw.cmd: Windows wrapper script
        - .mvn/wrapper/maven-wrapper.jar: Wrapper implementation
        - .mvn/wrapper/maven-wrapper.properties: Wrapper configuration

        Args:
            project_dir: Project directory to check

        Returns:
            Tuple of (wrapper_exists, wrapper_path)
        """
        # Check for Unix wrapper
        unix_wrapper = project_dir / "mvnw"
        if unix_wrapper.exists():
            return (True, unix_wrapper)

        # Check for Windows wrapper
        windows_wrapper = project_dir / "mvnw.cmd"
        if windows_wrapper.exists():
            return (True, windows_wrapper)

        return (False, None)

    def get_maven_command(self, project_dir: Path) -> str:
        """
        Get appropriate Maven command for project.

        WHY: Prefer Maven Wrapper if available, fallback to system Maven.
        RESPONSIBILITY: Return correct command to use for Maven operations.

        Args:
            project_dir: Project directory

        Returns:
            Maven command to use ("mvn", "./mvnw", or "mvnw.cmd")
        """
        has_wrapper, wrapper_path = self.detect_maven_wrapper(project_dir)

        if not has_wrapper:
            return "mvn"

        # Return wrapper script name (will need proper path in execution)
        return wrapper_path.name if wrapper_path else "mvn"

    def get_maven_info(self) -> dict:
        """
        Get comprehensive Maven installation information.

        WHY: Useful for diagnostics and feature detection.
        RESPONSIBILITY: Collect all Maven environment information.

        Returns:
            Dictionary with Maven version, home, Java version, etc.
        """
        if not self.maven_version:
            try:
                self.validate_maven_installation()
            except RuntimeError:
                return {"error": "Maven not installed"}

        return {
            "maven_version": self.maven_version,
            "command": "mvn",
            "installed": True
        }
