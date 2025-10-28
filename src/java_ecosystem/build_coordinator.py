#!/usr/bin/env python3
"""
Build Coordination for Java Projects

WHY: Provides unified build and test execution interface across Maven and Gradle,
     abstracting away build-system-specific command differences.

RESPONSIBILITY:
    - Coordinate build operations across Maven and Gradle
    - Provide consistent build() and run_tests() interface
    - Route build requests to appropriate build system
    - Handle build system detection and validation
    - Return normalized build results

PATTERNS:
    - Strategy pattern - selects appropriate build system strategy
    - Guard clauses - validate build system availability
    - Dispatch table - routes operations via dictionary lookup
"""

from typing import Optional, Any, Callable, Dict
import logging


class BuildCoordinator:
    """
    Coordinates build operations across Maven and Gradle.

    WHY: Provides single entry point for build/test operations,
         hiding Maven vs Gradle differences from callers.
    """

    def __init__(
        self,
        maven_build: Optional[Callable] = None,
        maven_test: Optional[Callable] = None,
        gradle_build: Optional[Callable] = None,
        gradle_test: Optional[Callable] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize build coordinator.

        Args:
            maven_build: Maven build function
            maven_test: Maven test function
            gradle_build: Gradle build function
            gradle_test: Gradle test function
            logger: Optional logger instance

        WHY: Dependency injection enables testing and flexibility
        """
        self.maven_build = maven_build
        self.maven_test = maven_test
        self.gradle_build = gradle_build
        self.gradle_test = gradle_test
        self.logger = logger or logging.getLogger(__name__)

        # Build dispatch table for strategy pattern
        self._build_strategies = self._create_build_dispatch_table()
        self._test_strategies = self._create_test_dispatch_table()

    def _create_build_dispatch_table(self) -> Dict[str, Callable]:
        """
        Create build dispatch table.

        Returns:
            Dictionary mapping build system to build function

        WHY: Dispatch table pattern - eliminates if/elif chains
        """
        strategies = {}

        if self.maven_build:
            strategies['maven'] = self.maven_build

        if self.gradle_build:
            strategies['gradle'] = self.gradle_build

        return strategies

    def _create_test_dispatch_table(self) -> Dict[str, Callable]:
        """
        Create test dispatch table.

        Returns:
            Dictionary mapping build system to test function

        WHY: Dispatch table pattern - eliminates if/elif chains
        """
        strategies = {}

        if self.maven_test:
            strategies['maven'] = self.maven_test

        if self.gradle_test:
            strategies['gradle'] = self.gradle_test

        return strategies

    def get_build_system_name(self) -> str:
        """
        Get detected build system name.

        Returns:
            Build system name (Maven, Gradle, or Unknown)

        WHY: Guard clause pattern - check Maven first, then Gradle
        """
        if self.maven_build:
            return "Maven"

        if self.gradle_build:
            return "Gradle"

        return "Unknown"

    def is_build_system_available(self) -> bool:
        """
        Check if build system is available.

        Returns:
            True if at least one build system available
        """
        return len(self._build_strategies) > 0

    def build(
        self,
        clean: bool = True,
        skip_tests: bool = False,
        timeout: int = 600
    ) -> Any:
        """
        Execute project build.

        Args:
            clean: Run clean before build
            skip_tests: Skip test execution
            timeout: Build timeout in seconds

        Returns:
            Build result from Maven or Gradle

        Raises:
            RuntimeError: If no build system available

        WHY: Strategy pattern - delegates to appropriate build handler
        """
        # Guard clause: ensure build system available
        if not self.is_build_system_available():
            raise RuntimeError("No build system detected")

        # Try Maven first
        if self.maven_build:
            return self.maven_build(
                clean=clean,
                skip_tests=skip_tests,
                timeout=timeout
            )

        # Fall back to Gradle
        if self.gradle_build:
            return self.gradle_build(
                clean=clean,
                timeout=timeout
            )

        # Should never reach here due to guard clause
        raise RuntimeError("No build system detected")

    def run_tests(
        self,
        test_class: Optional[str] = None,
        test_method: Optional[str] = None,
        timeout: int = 300
    ) -> Any:
        """
        Run project tests.

        Args:
            test_class: Specific test class to run
            test_method: Specific test method to run
            timeout: Test timeout in seconds

        Returns:
            Test result from Maven or Gradle

        Raises:
            RuntimeError: If no build system available

        WHY: Strategy pattern - delegates to appropriate test handler
        """
        # Guard clause: ensure build system available
        if not self.is_build_system_available():
            raise RuntimeError("No build system detected")

        # Try Maven first
        if self.maven_test:
            return self.maven_test(
                test_class=test_class,
                test_method=test_method,
                timeout=timeout
            )

        # Fall back to Gradle
        if self.gradle_test:
            return self.gradle_test(
                test_class=test_class,
                test_method=test_method,
                timeout=timeout
            )

        # Should never reach here due to guard clause
        raise RuntimeError("No build system detected")


__all__ = ['BuildCoordinator']
