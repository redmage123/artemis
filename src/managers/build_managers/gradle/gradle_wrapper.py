#!/usr/bin/env python3
"""
WHY: Detect and validate Gradle wrapper and system installations.

RESPONSIBILITY:
- Detect gradlew wrapper in project directory
- Fall back to system Gradle installation
- Validate Gradle is properly installed
- Parse and log Gradle version
- Provide single gradle_cmd for execution

PATTERNS:
- Guard clauses for existence checks
- Early return for wrapper preference
- Exception handling for subprocess failures
- Single Responsibility: installation detection only
"""

import re
import subprocess
from pathlib import Path
from typing import Optional
import logging


class GradleWrapper:
    """
    WHY: Centralized Gradle installation detection and validation.

    RESPONSIBILITY:
    - Prefer gradlew wrapper over system Gradle
    - Validate Gradle is accessible
    - Extract and log version information
    - Provide command path for execution

    PATTERNS:
    - Preference order: wrapper -> system
    - Guard clauses for file existence
    - Version extraction via regex
    - Logging integration
    """

    def __init__(
        self,
        project_dir: Path,
        logger: Optional[logging.Logger] = None
    ):
        """
        WHY: Initialize wrapper detector with project context.

        PATTERNS:
        - Optional logger with fallback
        - Automatic validation on init
        """
        self.project_dir = project_dir
        self.logger = logger or logging.getLogger(__name__)
        self.gradle_cmd: str = ""
        self.gradle_version: Optional[str] = None

        # Validate on initialization
        self._detect_and_validate()

    def _detect_and_validate(self) -> None:
        """
        WHY: Detect Gradle command and validate installation.

        RESPONSIBILITY:
        - Try gradlew wrapper first
        - Fall back to system gradle
        - Validate with version check
        - Extract version information

        PATTERNS:
        - Guard clause preference
        - Exception propagation for failures
        - Side effects: sets gradle_cmd and gradle_version
        """
        try:
            # Try wrapper first
            gradlew = self.project_dir / "gradlew"
            if gradlew.exists():
                self.gradle_cmd = str(gradlew)
                self._validate_gradle_command()
                return

            # Fall back to system gradle
            self.gradle_cmd = "gradle"
            self._validate_gradle_command()

        except FileNotFoundError:
            raise RuntimeError(
                "Gradle not found. Please install Gradle or use Gradle wrapper: "
                "https://gradle.org/install/"
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("Gradle version check timed out")

    def _validate_gradle_command(self) -> None:
        """
        WHY: Validate Gradle command is accessible and working.

        RESPONSIBILITY:
        - Execute gradle --version
        - Check return code
        - Extract version information
        - Log detected version

        PATTERNS:
        - Subprocess execution with timeout
        - Exception propagation
        - Side effect: sets gradle_version
        """
        result = subprocess.run(
            [self.gradle_cmd, "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            raise RuntimeError("Gradle is not properly installed")

        # Extract and log version
        self._parse_version(result.stdout)

    def _parse_version(self, stdout: str) -> None:
        """
        WHY: Extract Gradle version from --version output.

        RESPONSIBILITY:
        - Parse version using regex
        - Log detected version
        - Store for reference

        PATTERNS:
        - Guard clause for no match
        - Regex extraction
        - Side effect: sets gradle_version
        """
        version_match = re.search(r'Gradle (\d+\.\d+(?:\.\d+)?)', stdout)
        if not version_match:
            return

        self.gradle_version = version_match.group(1)
        self.logger.info(f"Detected Gradle version: {self.gradle_version}")

    def get_command(self) -> str:
        """
        WHY: Provide validated Gradle command for execution.

        PATTERNS:
        - Getter method
        - Already validated in __init__
        """
        return self.gradle_cmd

    def get_version(self) -> Optional[str]:
        """
        WHY: Provide detected Gradle version.

        PATTERNS:
        - Getter method
        - Optional return for robustness
        """
        return self.gradle_version

    def is_using_wrapper(self) -> bool:
        """
        WHY: Determine if using gradlew wrapper vs system Gradle.

        PATTERNS:
        - Simple string check
        - Boolean return for clarity
        """
        return "gradlew" in self.gradle_cmd
