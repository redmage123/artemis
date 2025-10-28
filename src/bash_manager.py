#!/usr/bin/env python3
"""
Module: Bash Manager (Backward Compatibility Wrapper)

WHY: Maintain 100% backward compatibility during refactoring
RESPONSIBILITY: Re-export BashManager from new modular package
PATTERNS: Facade Pattern, Proxy Pattern

This module serves as a backward compatibility shim that redirects all
imports to the new modular build_managers/bash/ package structure.

MIGRATION PATH:
    Old import: from bash_manager import BashManager
    New import: from build_managers.bash import BashManager

Both imports work identically - this wrapper ensures zero breaking changes.

Purpose: Shell script quality management and testing for bash/sh projects
Why: Shell scripts need static analysis, formatting checks, and testing just like
     compiled code, but traditional build systems don't support them. This manager
     provides quality gates for shell script projects.
Patterns: Strategy Pattern (via BuildManagerBase), Decorator Pattern (wrap_exception)
Integration: Registered with BuildManagerFactory as BuildSystem.BASH, allowing Artemis
             to treat shell scripts as first-class projects with CI/CD pipelines.

Key Tools Used:
- shellcheck: Static analysis tool that catches common shell script bugs
  Why: Shell scripts are error-prone; shellcheck finds issues like unquoted variables,
       missing error handling, and portability problems before runtime
- shfmt: Shell script formatter (like prettier for JavaScript)
  Why: Consistent formatting improves readability and prevents formatting-related diffs
- bats: Bash Automated Testing System
  Why: Shell scripts need unit tests too; bats provides test framework for bash

REFACTORING NOTES:
    Original file: 290 lines (monolithic)
    New structure: 6 modules (models, detector, linter, formatter, test_runner, manager)
    Benefits:
        - Single Responsibility Principle: Each module has one clear purpose
        - Testability: Components can be tested in isolation
        - Maintainability: Changes localized to specific modules
        - Guard Clauses: Maximum 1-level nesting throughout
        - Immutable Data Models: Value objects prevent accidental mutations
        - Result Pattern: Structured outcomes for all operations
"""

from pathlib import Path
import sys

# Re-export everything from the new modular package
from build_managers.bash import (
    # Main manager (primary export)
    BashManager,

    # Data models (for advanced usage)
    ShellDialect,
    CheckSeverity,
    ShellScript,
    LintResult,
    FormatResult,
    TestResult,
    BashProjectMetadata,
    QualityCheckConfig,

    # Components (for direct access if needed)
    ScriptDetector,
    ShellcheckLinter,
    ShfmtFormatter,
    BatsTestRunner
)

# Maintain module-level __all__ for explicit exports
__all__ = [
    # Primary export
    'BashManager',

    # Data models
    'ShellDialect',
    'CheckSeverity',
    'ShellScript',
    'LintResult',
    'FormatResult',
    'TestResult',
    'BashProjectMetadata',
    'QualityCheckConfig',

    # Components
    'ScriptDetector',
    'ShellcheckLinter',
    'ShfmtFormatter',
    'BatsTestRunner'
]


# Preserve original CLI behavior
if __name__ == "__main__":
    """
    CLI entry point for bash manager.

    WHY: Support direct execution for testing
    RESPONSIBILITY: Detect if current directory is a bash project
    PATTERNS: CLI Pattern

    Usage:
        python bash_manager.py
        Exit code 0: Bash project detected
        Exit code 1: Not a bash project
    """
    manager = BashManager(Path.cwd())
    sys.exit(0 if manager.detect() else 1)
