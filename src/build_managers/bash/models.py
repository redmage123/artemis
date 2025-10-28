#!/usr/bin/env python3
"""
Bash Manager - Data Models

WHY: Centralize data structures and enums for type safety and clarity
RESPONSIBILITY: Define immutable data structures for bash operations
PATTERNS: Value Objects, Immutable Data Transfer Objects (DTOs)

This module provides type-safe data structures for shell script management,
ensuring consistent data handling across all bash components.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional
from enum import Enum


class ShellDialect(Enum):
    """
    Shell script dialects for shellcheck targeting.

    WHY: Different shells have different features and syntax
    RESPONSIBILITY: Provide type-safe shell dialect specification
    """
    BASH = "bash"
    SH = "sh"
    DASH = "dash"
    KSH = "ksh"
    ZSH = "zsh"


class CheckSeverity(Enum):
    """
    Shellcheck severity levels.

    WHY: Allow filtering by severity for different CI environments
    RESPONSIBILITY: Type-safe severity level specification
    """
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    STYLE = "style"


@dataclass(frozen=True)
class ShellScript:
    """
    Immutable representation of a shell script.

    WHY: Value object pattern ensures scripts can't be modified accidentally
    RESPONSIBILITY: Encapsulate shell script metadata
    PATTERNS: Value Object, Immutable DTO
    """
    path: Path
    relative_path: Path
    size_bytes: int

    def __str__(self) -> str:
        """Human-readable representation."""
        return str(self.relative_path)

    @property
    def name(self) -> str:
        """Get script filename."""
        return self.path.name


@dataclass(frozen=True)
class LintResult:
    """
    Shellcheck linting result.

    WHY: Immutable result object for pure functional processing
    RESPONSIBILITY: Encapsulate linting outcome for a single script
    PATTERNS: Value Object, Result Pattern
    """
    script: ShellScript
    passed: bool
    output: str
    exit_code: int
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        """Check if any issues were found."""
        return bool(self.errors or self.warnings)


@dataclass(frozen=True)
class FormatResult:
    """
    Shfmt formatting check result.

    WHY: Immutable result object for pure functional processing
    RESPONSIBILITY: Encapsulate format check outcome for a single script
    PATTERNS: Value Object, Result Pattern
    """
    script: ShellScript
    formatted: bool
    diff: str
    exit_code: int

    @property
    def needs_formatting(self) -> bool:
        """Check if script needs formatting."""
        return not self.formatted and bool(self.diff)


@dataclass(frozen=True)
class TestResult:
    """
    Bats test execution result.

    WHY: Immutable result object for pure functional processing
    RESPONSIBILITY: Encapsulate test execution outcome
    PATTERNS: Value Object, Result Pattern
    """
    passed: bool
    output: str
    exit_code: int
    tests_run: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    tests_skipped: int = 0
    duration: float = 0.0


@dataclass(frozen=True)
class BashProjectMetadata:
    """
    Bash project metadata snapshot.

    WHY: Immutable snapshot of project state for reporting
    RESPONSIBILITY: Encapsulate complete project metadata
    PATTERNS: Value Object, Snapshot Pattern
    """
    manager: str
    scripts: List[ShellScript]
    has_tests: bool
    test_directory: Optional[Path]
    total_size_bytes: int

    @property
    def script_count(self) -> int:
        """Get total script count."""
        return len(self.scripts)

    @property
    def script_names(self) -> List[str]:
        """Get list of script names."""
        return [script.name for script in self.scripts]

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.

        WHY: Backward compatibility with existing metadata format
        """
        return {
            "manager": self.manager,
            "shell_scripts": [str(s.relative_path) for s in self.scripts],
            "has_tests": self.has_tests,
            "script_count": self.script_count,
            "total_size_bytes": self.total_size_bytes,
            "test_directory": str(self.test_directory) if self.test_directory else None
        }


@dataclass
class QualityCheckConfig:
    """
    Configuration for quality checks.

    WHY: Centralize configuration for flexibility
    RESPONSIBILITY: Hold configuration options for linting and formatting
    PATTERNS: Configuration Object
    """
    shell_dialect: ShellDialect = ShellDialect.BASH
    min_severity: CheckSeverity = CheckSeverity.WARNING
    shfmt_indent: int = 2
    shfmt_case_indent: bool = True
    shfmt_binary_next_line: bool = False
    enable_shellcheck: bool = True
    enable_shfmt: bool = True

    def get_shfmt_args(self) -> List[str]:
        """
        Build shfmt command arguments.

        WHY: Centralize argument building logic
        RESPONSIBILITY: Translate config to CLI args
        PATTERNS: Builder pattern
        """
        args = ["-d"]  # Diff mode
        args.append(f"-i")
        args.append(str(self.shfmt_indent))

        if self.shfmt_case_indent:
            args.append("-ci")

        if self.shfmt_binary_next_line:
            args.append("-bn")

        return args

    def get_shellcheck_args(self, script_path: Path) -> List[str]:
        """
        Build shellcheck command arguments.

        WHY: Centralize argument building logic
        RESPONSIBILITY: Translate config to CLI args
        PATTERNS: Builder pattern
        """
        args = ["shellcheck"]
        args.extend(["-s", self.shell_dialect.value])
        args.extend(["-S", self.min_severity.value])
        args.append(str(script_path))

        return args


__all__ = [
    'ShellDialect',
    'CheckSeverity',
    'ShellScript',
    'LintResult',
    'FormatResult',
    'TestResult',
    'BashProjectMetadata',
    'QualityCheckConfig'
]
