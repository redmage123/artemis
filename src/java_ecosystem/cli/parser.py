#!/usr/bin/env python3
"""
WHY: Configure argument parser for Java ecosystem CLI
RESPONSIBILITY: Setup command-line arguments and subcommands
PATTERNS: Builder (parser construction), Factory (subparser creation)

Parser provides clean separation of CLI configuration from logic.
"""

import argparse
from typing import Any


def create_parser() -> argparse.ArgumentParser:
    """
    Create argument parser with all subcommands.

    WHY: Builder pattern - construct complex parser step by step.

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description="Java Ecosystem Manager for Artemis"
    )

    parser.add_argument(
        "--project-dir",
        default=".",
        help="Java project directory"
    )

    # Create subcommands
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    _add_analyze_command(subparsers)
    _add_build_command(subparsers)
    _add_test_command(subparsers)

    return parser


def _add_analyze_command(subparsers: Any) -> None:
    """
    Add analyze subcommand.

    WHY: Factory method for analyze command parser.

    Args:
        subparsers: Subparser container
    """
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze Java project"
    )
    analyze_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )


def _add_build_command(subparsers: Any) -> None:
    """
    Add build subcommand.

    WHY: Factory method for build command parser.

    Args:
        subparsers: Subparser container
    """
    build_parser = subparsers.add_parser(
        "build",
        help="Build project"
    )
    build_parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip tests"
    )
    build_parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Don't clean before build"
    )


def _add_test_command(subparsers: Any) -> None:
    """
    Add test subcommand.

    WHY: Factory method for test command parser.

    Args:
        subparsers: Subparser container
    """
    test_parser = subparsers.add_parser(
        "test",
        help="Run tests"
    )
    test_parser.add_argument(
        "--class",
        dest="test_class",
        help="Test class to run"
    )
    test_parser.add_argument(
        "--method",
        dest="test_method",
        help="Test method to run"
    )
