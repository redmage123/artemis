#!/usr/bin/env python3
"""
WHY: Factory for creating framework-specific test runners
RESPONSIBILITY: Instantiate appropriate runner based on framework
PATTERNS: Factory Pattern, Registry Pattern

This module implements the Factory pattern to create framework-specific
test runners. It maintains a registry of runners and provides methods
to register new runners dynamically.
"""

import logging
from typing import Dict, Optional, Type

from artemis_exceptions import wrap_exception
from stages.testing.models import TestFramework
from stages.testing.base import BaseFrameworkRunner
from stages.testing.exceptions import TestRunnerError
from stages.testing.runners import (
    PytestRunner,
    UnittestRunner,
    GtestRunner,
    JunitRunner,
    JestRunner,
    PlaywrightRunner,
    SeleniumRunner,
    AppiumRunner,
    RobotRunner,
    HypothesisRunner,
    JmeterRunner
)


class FrameworkRunnerFactory:
    """
    WHY: Centralized runner creation
    RESPONSIBILITY: Create and manage framework runners
    PATTERNS: Factory Pattern, Registry Pattern

    This factory maintains a registry of all available test runners
    and creates instances on demand. New runners can be registered
    dynamically to extend functionality.

    Guard Clauses: Max 1 level nesting throughout
    """

    _runners: Dict[TestFramework, Type[BaseFrameworkRunner]] = {
        TestFramework.PYTEST: PytestRunner,
        TestFramework.UNITTEST: UnittestRunner,
        TestFramework.GTEST: GtestRunner,
        TestFramework.JUNIT: JunitRunner,
        TestFramework.JEST: JestRunner,
        TestFramework.PLAYWRIGHT: PlaywrightRunner,
        TestFramework.SELENIUM: SeleniumRunner,
        TestFramework.APPIUM: AppiumRunner,
        TestFramework.ROBOT: RobotRunner,
        TestFramework.HYPOTHESIS: HypothesisRunner,
        TestFramework.JMETER: JmeterRunner,
    }

    @classmethod
    def register_runner(
        cls,
        framework: TestFramework,
        runner_class: Type[BaseFrameworkRunner]
    ) -> None:
        """
        WHY: Allow dynamic runner registration
        RESPONSIBILITY: Add new runner to registry

        This enables plugin-style extensions where new framework
        runners can be registered at runtime.

        Args:
            framework: Framework enum
            runner_class: Runner class to register
        """
        cls._runners[framework] = runner_class

    @classmethod
    @wrap_exception(TestRunnerError, "Failed to create framework runner")
    def create_runner(
        cls,
        framework: TestFramework,
        logger: Optional[logging.Logger] = None
    ) -> BaseFrameworkRunner:
        """
        WHY: Create framework-specific runner instance
        RESPONSIBILITY: Instantiate runner with dependency injection

        Args:
            framework: Framework enum
            logger: Optional logger for dependency injection

        Returns:
            Framework runner instance

        Raises:
            TestRunnerError: If framework not registered
        """
        runner_class = cls._runners.get(framework)

        if not runner_class:
            raise TestRunnerError(
                f"No runner registered for framework: {framework.value}",
                {
                    "framework": framework.value,
                    "available": [f.value for f in cls._runners.keys()]
                }
            )

        return runner_class(logger=logger)

    @classmethod
    def get_available_frameworks(cls) -> list[str]:
        """
        WHY: List supported frameworks
        RESPONSIBILITY: Provide framework discovery

        Returns:
            List of framework names
        """
        return [framework.value for framework in cls._runners.keys()]

    @classmethod
    def is_framework_supported(cls, framework: TestFramework) -> bool:
        """
        WHY: Check framework support
        RESPONSIBILITY: Validate framework availability

        Args:
            framework: Framework to check

        Returns:
            True if framework is supported
        """
        return framework in cls._runners
