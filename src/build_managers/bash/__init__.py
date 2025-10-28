"""
Bash Build Manager - Modularized Components

WHY: Backward compatibility wrapper for refactored Bash manager
RESPONSIBILITY: Re-export all components for seamless migration
PATTERNS: Facade pattern - single import point for all functionality

This module provides a unified interface to the modularized Bash manager
components, allowing existing code to continue working without modification.

Package Structure:
    models.py         - Data structures and enums
    script_detector.py - Shell script discovery
    linter.py         - Shellcheck integration
    formatter.py      - Shfmt integration
    test_runner.py    - Bats test execution
    manager.py        - Main orchestration layer

Design Patterns Applied:
    - Template Method: BashManager extends BuildManagerBase
    - Strategy Pattern: Configurable quality checks
    - Composition over Inheritance: Component delegation
    - Value Objects: Immutable data models
    - Result Pattern: Structured operation outcomes
    - Guard Clauses: Maximum 1-level nesting
    - Facade: Unified interface for complex subsystems
"""

# Data models and enums
from .models import (
    ShellDialect,
    CheckSeverity,
    ShellScript,
    LintResult,
    FormatResult,
    TestResult,
    BashProjectMetadata,
    QualityCheckConfig
)

# Specialized components
from .script_detector import ScriptDetector
from .linter import ShellcheckLinter
from .formatter import ShfmtFormatter
from .test_runner import BatsTestRunner

# Main manager
from .manager import BashManager

__all__ = [
    # Models
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
    'BatsTestRunner',

    # Main manager
    'BashManager'
]
