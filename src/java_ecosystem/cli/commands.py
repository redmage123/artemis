#!/usr/bin/env python3
"""
WHY: Handle CLI commands for Java ecosystem operations
RESPONSIBILITY: Execute analyze, build, and test commands
PATTERNS: Command (encapsulate operations), Strategy (command dispatch)

Commands delegate to JavaEcosystemManager and use formatters for output.
"""

from typing import Any
from java_ecosystem import JavaEcosystemManager
from java_ecosystem.cli.formatters import (
    print_analysis,
    print_build_result,
    print_test_result
)


def handle_analyze(manager: JavaEcosystemManager, args: Any) -> None:
    """
    Handle analyze command.

    WHY: Displays comprehensive Java project analysis.

    Args:
        manager: JavaEcosystemManager instance
        args: Command arguments with json flag
    """
    analysis = manager.analyze_project()
    print_analysis(analysis, as_json=args.json)


def handle_build(manager: JavaEcosystemManager, args: Any) -> None:
    """
    Handle build command.

    WHY: Executes project build with optional test skipping.

    Args:
        manager: JavaEcosystemManager instance
        args: Command arguments with no_clean and skip_tests flags
    """
    result = manager.build(
        clean=not args.no_clean,
        skip_tests=args.skip_tests
    )
    print_build_result(result, args.skip_tests)


def handle_test(manager: JavaEcosystemManager, args: Any) -> None:
    """
    Handle test command.

    WHY: Executes project tests with optional filtering.

    Args:
        manager: JavaEcosystemManager instance
        args: Command arguments with test_class and test_method
    """
    result = manager.run_tests(
        test_class=args.test_class,
        test_method=args.test_method
    )
    print_test_result(result)
