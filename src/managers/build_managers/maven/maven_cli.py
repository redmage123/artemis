#!/usr/bin/env python3
"""
Module: Maven CLI Handler

WHY: Command-line interface for Maven operations (standalone tool).
RESPONSIBILITY: Parse CLI arguments and execute Maven commands.
PATTERNS: Command pattern (dispatch table), Facade pattern.

Dependencies: maven_manager, maven_enums
"""

import argparse
import logging
from typing import Any, Callable, Dict

from .maven_manager import MavenManager
from .maven_enums import MavenPhase


def handle_info_command(maven: MavenManager) -> None:
    """
    Handle 'info' command to display project information.

    WHY: Display comprehensive project metadata.
    RESPONSIBILITY: Query project info and format output.

    Args:
        maven: MavenManager instance
    """
    info = maven.get_project_info()
    print(f"\n{'='*60}")
    print(f"Maven Project Information")
    print(f"{'='*60}")
    print(f"Project:      {info}")
    print(f"Name:         {info.name}")
    print(f"Packaging:    {info.packaging}")
    if info.description:
        print(f"Description:  {info.description}")
    print(f"Multi-module: {info.is_multi_module}")
    if info.modules:
        print(f"Modules:      {', '.join(info.modules)}")
    print(f"Dependencies: {len(info.dependencies)}")
    print(f"Plugins:      {len(info.plugins)}")
    print(f"{'='*60}\n")


def handle_build_command(maven: MavenManager, args: Any) -> None:
    """
    Handle 'build' command to build the project.

    WHY: Execute build with user-specified configuration.
    RESPONSIBILITY: Parse args, execute build, display results.

    Args:
        maven: MavenManager instance
        args: Parsed command-line arguments
    """
    phase = MavenPhase(args.phase)
    result = maven.build(
        phase=phase,
        skip_tests=args.skip_tests,
        clean=not args.no_clean
    )

    print(f"\n{'='*60}")
    print(f"Build Result: {'SUCCESS' if result.success else 'FAILURE'}")
    print(f"{'='*60}")
    print(f"Phase:     {result.phase}")
    print(f"Duration:  {result.duration:.2f}s")
    print(f"Exit Code: {result.exit_code}")

    if not args.skip_tests:
        print(f"Tests:     {result.tests_passed}/{result.tests_run} passed")

    if result.errors:
        print(f"\nErrors:")
        for error in result.errors[:5]:
            print(f"  - {error}")

    print(f"{'='*60}\n")


def handle_test_command(maven: MavenManager, args: Any) -> None:
    """
    Handle 'test' command to run tests.

    WHY: Execute tests with optional filtering.
    RESPONSIBILITY: Parse args, run tests, display results.

    Args:
        maven: MavenManager instance
        args: Parsed command-line arguments
    """
    result = maven.run_tests(
        test_class=args.test_class,
        test_method=args.test_method
    )

    print(f"\n{'='*60}")
    print(f"Test Result: {'SUCCESS' if result.success else 'FAILURE'}")
    print(f"{'='*60}")
    print(f"Tests Run:    {result.tests_run}")
    print(f"Passed:       {result.tests_passed}")
    print(f"Failed:       {result.tests_failed}")
    print(f"Skipped:      {result.tests_skipped}")
    print(f"Duration:     {result.duration:.2f}s")
    print(f"{'='*60}\n")


def handle_add_dep_command(maven: MavenManager, args: Any) -> None:
    """
    Handle 'add-dep' command to add a dependency.

    WHY: Programmatically add dependencies without manual XML editing.
    RESPONSIBILITY: Parse args, add dependency, display result.

    Args:
        maven: MavenManager instance
        args: Parsed command-line arguments
    """
    success = maven.add_dependency(
        args.group_id,
        args.artifact_id,
        args.version,
        args.scope
    )

    if success:
        print(f"Added dependency: {args.group_id}:{args.artifact_id}:{args.version}")
    else:
        print(f"Failed to add dependency")


def create_parser() -> argparse.ArgumentParser:
    """
    Create CLI argument parser.

    WHY: Centralized CLI definition.
    RESPONSIBILITY: Define all commands, subcommands, and arguments.

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description="Maven Build System Manager"
    )
    parser.add_argument(
        "--project-dir",
        default=".",
        help="Maven project directory"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Info command
    subparsers.add_parser("info", help="Show project information")

    # Build command
    build_parser = subparsers.add_parser("build", help="Build project")
    build_parser.add_argument("--phase", default="package", help="Maven phase")
    build_parser.add_argument("--skip-tests", action="store_true", help="Skip tests")
    build_parser.add_argument("--no-clean", action="store_true", help="Don't clean before build")

    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("--class", dest="test_class", help="Test class to run")
    test_parser.add_argument("--method", dest="test_method", help="Test method to run")

    # Dependency command
    dep_parser = subparsers.add_parser("add-dep", help="Add dependency")
    dep_parser.add_argument("group_id", help="Group ID")
    dep_parser.add_argument("artifact_id", help="Artifact ID")
    dep_parser.add_argument("version", help="Version")
    dep_parser.add_argument("--scope", default="compile", help="Dependency scope")

    return parser


def main() -> None:
    """
    Main CLI entry point.

    WHY: Execute CLI commands using dispatch table pattern.
    RESPONSIBILITY: Parse args, create manager, dispatch to handler.
    """
    parser = create_parser()
    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    # Create Maven manager
    maven = MavenManager(project_dir=args.project_dir)

    # Command dispatch table (avoid if/elif chain)
    command_handlers: Dict[str, Callable[[MavenManager, Any], None]] = {
        'info': lambda m, a: handle_info_command(m),
        'build': handle_build_command,
        'test': handle_test_command,
        'add-dep': handle_add_dep_command
    }

    # Execute command handler
    handler = command_handlers.get(args.command)
    if handler:
        # Handle both single-arg and dual-arg handlers
        if args.command == 'info':
            handler(maven, args)
        else:
            handler(maven, args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
