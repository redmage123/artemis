#!/usr/bin/env python3
"""
Module: artemis_stage_interface.py

Purpose: Define abstract base classes and interfaces for the Artemis pipeline architecture.
Why: Establishes contracts that all pipeline stages must follow, enabling loose coupling
     and dependency injection throughout the system.

Patterns:
- Interface Segregation Principle (ISP): Each interface has a single focused responsibility
- Dependency Inversion Principle (DIP): High-level orchestration depends on these abstractions,
  not on concrete implementations
- Template Method Pattern: PipelineStage provides the execution contract

Integration: All pipeline stages (Architecture, Development, Validation, etc.) implement
             PipelineStage interface. Orchestrator depends on these abstractions for
             stage execution sequencing.

SOLID Principles Applied:
- S: Single Responsibility - Each interface defines one contract
- O: Open/Closed - New stages can be added without modifying these interfaces
- L: Liskov Substitution - All stage implementations are interchangeable
- I: Interface Segregation - Small, focused interfaces (LoggerInterface, TestRunnerInterface)
- D: Dependency Inversion - Orchestrator depends on abstractions, not concrete classes
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional


class PipelineStage(ABC):
    """
    Abstract base class for all pipeline stages in the Artemis workflow.

    Why it exists: Provides a common contract that enables the orchestrator to execute
                   stages polymorphically without knowing their specific implementation details.

    Design pattern: Template Method Pattern - defines the skeleton of stage execution
                    while allowing subclasses to implement specific behaviors.

    Responsibilities:
    - Define the execution contract (execute method)
    - Require stages to identify themselves (get_stage_name)
    - Enable Liskov Substitution - any stage can replace another in the pipeline

    SOLID Principles:
    - Single Responsibility: Only defines the stage contract
    - Open/Closed: New stages can be added without modifying this interface
    - Liskov Substitution: All stages can be used interchangeably by orchestrator
    - Dependency Inversion: Orchestrator depends on this abstraction, not concrete stages

    Usage:
        class MyStage(PipelineStage):
            def execute(self, card, context):
                # Implementation
                return {"stage": "my_stage", "result": "success"}

            def get_stage_name(self):
                return "my_stage"
    """

    @abstractmethod
    def execute(self, card: Dict, context: Dict) -> Dict:
        """
        Execute this pipeline stage with the given card and context.

        What it does: Processes a single work item (card) using shared pipeline state (context).

        Why needed: Each stage transforms data and passes results to subsequent stages.
                    This method is the single entry point for all stage execution.

        Args:
            card: Kanban card containing task details (title, description, card_id, etc.).
                  Why: Represents the work item being processed through the pipeline.
            context: Shared dictionary containing results from all previous stages.
                     Why: Stages need access to artifacts from earlier stages (requirements,
                          architecture diagrams, test results, etc.) to perform their work.

        Returns:
            Dict containing this stage's results, which will be merged into context for
            subsequent stages. Must include at minimum:
                - "stage": str - Name of this stage for tracking
                - "status": str - Execution status ("success", "failed", "skipped")

        Raises:
            PipelineStageError: If stage execution fails critically.
                                Why: Allows orchestrator to handle failures gracefully.

        Edge cases:
            - If card is missing required fields, raise PipelineStageError
            - If stage should be skipped based on context, return status="skipped"
            - If stage has warnings but succeeds, include "warnings" in result
        """
        pass

    @abstractmethod
    def get_stage_name(self) -> str:
        """
        Return the unique identifier for this pipeline stage.

        What it does: Provides a string name for logging, tracking, and debugging.

        Why needed: Allows orchestrator to identify which stage is executing and to
                    build context keys for storing stage-specific results.

        Returns:
            Lowercase string identifier (e.g., "requirements", "development", "validation")

        Edge cases:
            - Name must be unique within the pipeline to avoid context key collisions
            - Name should match the key used when storing results in context
        """
        pass


class TestRunnerInterface(ABC):
    """
    Interface for running test suites (pytest, unittest, etc.).

    Why it exists: Abstracts test execution to allow different test frameworks
                   to be used interchangeably (pytest, nose, unittest).

    Design pattern: Strategy Pattern - different test runners implement this interface.

    Responsibilities:
    - Execute test suites
    - Parse test results
    - Return standardized result format

    Interface Segregation: Focused only on test execution, not test generation or analysis.
    """

    @abstractmethod
    def run_tests(self, test_path: str) -> Dict:
        """
        Execute tests at the given path and return results.

        What it does: Runs a test suite (file or directory) and collects results.

        Why needed: Validation stages need to execute tests without knowing which
                    test framework is being used. This abstraction allows framework
                    switching without changing validation logic.

        Args:
            test_path: Absolute path to test file or directory to execute.
                       Why: Tests may be organized in various structures.

        Returns:
            Dict with standardized test results:
                - "passed": int - Number of passing tests
                - "failed": int - Number of failing tests
                - "errors": int - Number of tests with errors
                - "skipped": int - Number of skipped tests
                - "output": str - Raw test output for debugging
                - "duration": float - Execution time in seconds

        Edge cases:
            - If test_path doesn't exist, return all zeros with error in output
            - If no tests found, return skipped=0 and note in output
        """
        pass


class ValidatorInterface(ABC):
    """
    Interface for validation operations (code linting, type checking, security scans).

    Why it exists: Allows different validation tools (pylint, mypy, bandit) to be
                   used interchangeably through a common interface.

    Design pattern: Strategy Pattern - different validators implement this interface.

    Responsibilities:
    - Validate code, configurations, or artifacts
    - Return standardized validation results
    - Identify issues with severity levels

    Interface Segregation: Focused only on validation, not fixing or code generation.
    """

    @abstractmethod
    def validate(self, target) -> Dict:
        """
        Validate the given target and return results.

        What it does: Analyzes code/artifacts to identify issues, violations, or improvements.

        Why needed: Quality gates need to validate artifacts without knowing which
                    specific validation tool is being used (pylint vs mypy vs bandit).

        Args:
            target: Path to file/directory to validate, or artifact object.
                    Why: Different validators work on different target types.

        Returns:
            Dict with standardized validation results:
                - "valid": bool - Whether validation passed
                - "errors": List[str] - Critical issues found
                - "warnings": List[str] - Non-critical issues
                - "score": float - Quality score (0-100)
                - "details": str - Detailed validation output

        Edge cases:
            - If target is unreachable, return valid=False with error details
            - If validator tool is not installed, include in warnings
        """
        pass


class LoggerInterface(ABC):
    """
    Interface for logging throughout the Artemis pipeline.

    Why it exists: Abstracts logging implementation to allow switching between
                   different logging backends (file, database, cloud) without
                   changing stage code.

    Design pattern: Facade Pattern - provides simple interface to complex logging system.

    Responsibilities:
    - Accept log messages with severity levels
    - Format and output logs appropriately
    - Handle log rotation and persistence

    Interface Segregation: Focused only on logging, not metrics or monitoring.
    """

    @abstractmethod
    def log(self, message: str, level: str = "INFO"):
        """
        Log a message with the specified severity level.

        What it does: Records a timestamped message for debugging and monitoring.

        Why needed: All stages need to communicate status, errors, and progress.
                    This abstraction allows centralized log management without
                    coupling stages to specific logging libraries.

        Args:
            message: Text to log. Should be clear and actionable.
                     Why: Operators need to understand what's happening.
            level: Severity level - "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "SUCCESS", "STAGE".
                   Why: Allows filtering and routing based on importance.
                   Default "INFO" for standard operational messages.

        Returns:
            None - logging is a side effect

        Edge cases:
            - If invalid level provided, default to "INFO"
            - If message is None or empty, log with placeholder
            - If logging backend fails, print to stderr as fallback
        """
        pass
