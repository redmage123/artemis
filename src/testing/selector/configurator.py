#!/usr/bin/env python3
"""
Testing Framework Selector - Framework Configuration

WHY: After selecting a framework, configuration details (dependencies,
commands, setup instructions) are needed. Separating configuration from
selection keeps concerns focused and enables independent evolution.

RESPONSIBILITY: Provide configuration details for selected test frameworks.
Single responsibility - configuration data only, no selection logic.

PATTERNS: Strategy pattern with dispatch tables for framework configs.
Factory pattern for creating configuration objects.

Used by selector_core and external tools to configure test frameworks.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class FrameworkConfiguration:
    """
    Configuration details for a test framework.

    WHY: Frameworks need specific dependencies, commands, and setup.
    Encapsulating configuration enables automation of framework setup.

    RESPONSIBILITY: Value object containing framework configuration data.

    PATTERNS: Dataclass for structured configuration.

    Attributes:
        framework_name: Name of the framework
        install_commands: Commands to install the framework
        dependencies: Required dependencies/packages
        config_files: Configuration files needed
        run_command: Command to run tests
        setup_instructions: Human-readable setup instructions
    """
    framework_name: str
    install_commands: List[str]
    dependencies: List[str]
    config_files: Dict[str, str]  # filename -> content
    run_command: str
    setup_instructions: str


class FrameworkConfigurator:
    """
    Provides configuration details for test frameworks.

    WHY: After framework selection, Artemis needs to know how to install
    and configure the framework. Centralizing configuration logic enables
    consistent setup across projects.

    RESPONSIBILITY: Generate configuration details for selected frameworks.
    Single responsibility - configuration only.

    PATTERNS: Strategy pattern with dispatch tables for framework configs.
    """

    def __init__(self):
        """Initialize configurator with framework configs."""
        # Strategy pattern: Dispatch table for framework configurations
        # WHY: Easily extensible, testable independently
        self._config_strategies: Dict[str, Any] = {
            "pytest": self._configure_pytest,
            "unittest": self._configure_unittest,
            "jest": self._configure_jest,
            "junit": self._configure_junit,
            "gtest": self._configure_gtest,
            "playwright": self._configure_playwright,
            "selenium": self._configure_selenium,
            "appium": self._configure_appium,
            "jmeter": self._configure_jmeter,
            "robot": self._configure_robot,
            "hypothesis": self._configure_hypothesis
        }

    def get_configuration(self, framework_name: str) -> Optional[FrameworkConfiguration]:
        """
        Get configuration for specified framework.

        WHY: Provides all details needed to set up and use a framework.

        Args:
            framework_name: Name of framework to configure

        Returns:
            FrameworkConfiguration if framework known, None otherwise
        """
        # Guard clause: Check if framework configuration exists
        if framework_name not in self._config_strategies:
            return None

        # Execute configuration strategy
        return self._config_strategies[framework_name]()

    def _configure_pytest(self) -> FrameworkConfiguration:
        """Configure pytest framework."""
        return FrameworkConfiguration(
            framework_name="pytest",
            install_commands=["pip install pytest pytest-cov"],
            dependencies=["pytest", "pytest-cov"],
            config_files={
                "pytest.ini": "[pytest]\ntestpaths = tests\npython_files = test_*.py\npython_classes = Test*\npython_functions = test_*\n"
            },
            run_command="pytest",
            setup_instructions="Install pytest and create tests/ directory with test_*.py files"
        )

    def _configure_unittest(self) -> FrameworkConfiguration:
        """Configure unittest framework."""
        return FrameworkConfiguration(
            framework_name="unittest",
            install_commands=[],  # Built into Python
            dependencies=[],
            config_files={},
            run_command="python -m unittest discover",
            setup_instructions="unittest is built into Python. Create test files with test_*.py naming"
        )

    def _configure_jest(self) -> FrameworkConfiguration:
        """Configure Jest framework."""
        return FrameworkConfiguration(
            framework_name="jest",
            install_commands=["npm install --save-dev jest @types/jest"],
            dependencies=["jest", "@types/jest"],
            config_files={
                "jest.config.js": "module.exports = {\n  testEnvironment: 'node',\n  coverageDirectory: 'coverage',\n  testMatch: ['**/*.test.js', '**/*.spec.js']\n};\n"
            },
            run_command="npm test",
            setup_instructions="Install Jest via npm and create *.test.js or *.spec.js test files"
        )

    def _configure_junit(self) -> FrameworkConfiguration:
        """Configure JUnit framework."""
        return FrameworkConfiguration(
            framework_name="junit",
            install_commands=["# Add to pom.xml or build.gradle"],
            dependencies=["junit:junit:4.13.2"],
            config_files={},
            run_command="mvn test",
            setup_instructions="Add JUnit dependency to Maven/Gradle and create test classes with @Test annotations"
        )

    def _configure_gtest(self) -> FrameworkConfiguration:
        """Configure Google Test framework."""
        return FrameworkConfiguration(
            framework_name="gtest",
            install_commands=["# Add to CMakeLists.txt"],
            dependencies=["gtest", "gtest_main"],
            config_files={},
            run_command="./test_executable",
            setup_instructions="Add Google Test to CMake and create test files with TEST() macros"
        )

    def _configure_playwright(self) -> FrameworkConfiguration:
        """Configure Playwright framework."""
        return FrameworkConfiguration(
            framework_name="playwright",
            install_commands=["pip install playwright", "playwright install"],
            dependencies=["playwright"],
            config_files={},
            run_command="pytest",
            setup_instructions="Install Playwright and browser binaries, create tests using playwright fixtures"
        )

    def _configure_selenium(self) -> FrameworkConfiguration:
        """Configure Selenium framework."""
        return FrameworkConfiguration(
            framework_name="selenium",
            install_commands=["pip install selenium webdriver-manager"],
            dependencies=["selenium", "webdriver-manager"],
            config_files={},
            run_command="pytest",
            setup_instructions="Install Selenium and WebDriver, create tests using WebDriver API"
        )

    def _configure_appium(self) -> FrameworkConfiguration:
        """Configure Appium framework."""
        return FrameworkConfiguration(
            framework_name="appium",
            install_commands=["npm install -g appium", "pip install Appium-Python-Client"],
            dependencies=["appium", "Appium-Python-Client"],
            config_files={},
            run_command="pytest",
            setup_instructions="Install Appium server and client, configure device capabilities"
        )

    def _configure_jmeter(self) -> FrameworkConfiguration:
        """Configure JMeter framework."""
        return FrameworkConfiguration(
            framework_name="jmeter",
            install_commands=["# Download from jmeter.apache.org"],
            dependencies=[],
            config_files={},
            run_command="jmeter -n -t test_plan.jmx -l results.jtl",
            setup_instructions="Download JMeter and create test plans with .jmx files"
        )

    def _configure_robot(self) -> FrameworkConfiguration:
        """Configure Robot Framework."""
        return FrameworkConfiguration(
            framework_name="robot",
            install_commands=["pip install robotframework"],
            dependencies=["robotframework"],
            config_files={},
            run_command="robot tests/",
            setup_instructions="Install Robot Framework and create .robot test files with keywords"
        )

    def _configure_hypothesis(self) -> FrameworkConfiguration:
        """Configure Hypothesis framework."""
        return FrameworkConfiguration(
            framework_name="hypothesis",
            install_commands=["pip install hypothesis"],
            dependencies=["hypothesis"],
            config_files={},
            run_command="pytest",
            setup_instructions="Install Hypothesis and use @given decorator for property-based tests"
        )
