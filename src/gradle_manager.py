#!/usr/bin/env python3
"""
WHY: Backward compatibility wrapper for modularized Gradle manager.

RESPONSIBILITY:
- Re-export all components from managers.build_managers.gradle
- Maintain existing import paths for legacy code
- Provide CLI interface for standalone usage
- Ensure zero breaking changes

PATTERNS:
- Transparent re-export pattern
- Backward compatibility layer
- CLI delegation
- Import forwarding

MIGRATION:
Old imports (still supported):
    from gradle_manager import GradleManager

New imports (preferred):
    from managers.build_managers.gradle import GradleManager

Both work identically - this file ensures backward compatibility.
"""

# Re-export all components from modularized package
from managers.build_managers.gradle import (
    # Main facade
    GradleManager,

    # Models
    GradleDSL,
    GradleDependency,
    GradlePlugin,
    GradleProjectInfo,
    GradleBuildResult,

    # Components (for advanced usage)
    GradleWrapper,
    BuildFileParser,
    DependencyManager,
    ProjectAnalyzer,
    TaskExecutor,
)

__all__ = [
    # Main facade
    "GradleManager",

    # Models
    "GradleDSL",
    "GradleDependency",
    "GradlePlugin",
    "GradleProjectInfo",
    "GradleBuildResult",

    # Components
    "GradleWrapper",
    "BuildFileParser",
    "DependencyManager",
    "ProjectAnalyzer",
    "TaskExecutor",
]


# ============================================================================
# COMMAND-LINE INTERFACE
# ============================================================================

if __name__ == "__main__":
    import argparse
    import logging
    from typing import Optional, Any

    def handle_info_command(gradle: GradleManager) -> None:
        """
        WHY: Display comprehensive project information.

        PATTERNS:
        - Guard clauses for optional fields
        - Formatted output with separators
        """
        info = gradle.get_project_info()
        print(f"\n{'='*60}")
        print(f"Gradle Project Information")
        print(f"{'='*60}")
        print(f"Name:         {info.name}")
        print(f"Group:        {info.group}")
        print(f"Version:      {info.version}")
        print(f"DSL:          {info.dsl.value}")
        print(f"Multi-project: {info.is_multi_project}")
        print(f"Android:      {info.is_android}")

        if info.source_compatibility:
            print(f"Java Source:  {info.source_compatibility}")
        if info.target_compatibility:
            print(f"Java Target:  {info.target_compatibility}")

        if info.subprojects:
            print(f"Subprojects:  {', '.join(info.subprojects)}")

        print(f"Plugins:      {len(info.plugins)}")
        print(f"Dependencies: {len(info.dependencies)}")
        print(f"Tasks:        {len(info.tasks)}")
        print(f"{'='*60}\n")

    def handle_build_command(gradle: GradleManager, args: Any) -> None:
        """
        WHY: Execute build and display results.

        PATTERNS:
        - Guard clause for test results
        - Error limiting
        """
        result = gradle.build(
            task=args.task,
            clean=not args.no_clean
        )
        print(f"\n{'='*60}")
        print(f"Build Result: {'SUCCESS' if result.success else 'FAILURE'}")
        print(f"{'='*60}")
        print(f"Task:      {result.task}")
        print(f"Duration:  {result.duration:.2f}s")
        print(f"Exit Code: {result.exit_code}")

        if result.tests_run > 0:
            print(f"Tests:     {result.tests_passed}/{result.tests_run} passed")

        if result.errors:
            print(f"\nErrors:")
            for error in result.errors[:5]:
                print(f"  - {error}")

        print(f"{'='*60}\n")

    def handle_test_command(gradle: GradleManager, args: Any) -> None:
        """
        WHY: Execute tests and display results.

        PATTERNS:
        - Structured output format
        """
        result = gradle.run_tests(
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

    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Gradle Build System Manager"
    )
    parser.add_argument(
        "--project-dir",
        default=".",
        help="Gradle project directory"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Info command
    subparsers.add_parser("info", help="Show project information")

    # Build command
    build_parser = subparsers.add_parser("build", help="Build project")
    build_parser.add_argument("--task", default="build", help="Gradle task")
    build_parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Don't clean before build"
    )

    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("--class", dest="test_class", help="Test class to run")
    test_parser.add_argument("--method", dest="test_method", help="Test method to run")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    # Create Gradle manager
    gradle = GradleManager(project_dir=args.project_dir)

    # Dispatch table for commands
    command_handlers = {
        "info": lambda: handle_info_command(gradle),
        "build": lambda: handle_build_command(gradle, args),
        "test": lambda: handle_test_command(gradle, args)
    }

    handler = command_handlers.get(args.command)
    if handler:
        handler()
    else:
        parser.print_help()
