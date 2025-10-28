#!/usr/bin/env python3
"""
WHY: Framework-specific test runners
RESPONSIBILITY: Organize framework runner implementations
PATTERNS: Strategy Pattern

This package contains concrete implementations of test runners for
different testing frameworks, organized by category.
"""

from stages.testing.runners.python import PytestRunner, UnittestRunner
from stages.testing.runners.compiled import GtestRunner, JunitRunner
from stages.testing.runners.javascript import JestRunner
from stages.testing.runners.web import PlaywrightRunner, SeleniumRunner, AppiumRunner
from stages.testing.runners.specialized import RobotRunner, HypothesisRunner, JmeterRunner

__all__ = [
    # Python runners
    'PytestRunner',
    'UnittestRunner',

    # Compiled language runners
    'GtestRunner',
    'JunitRunner',

    # JavaScript runners
    'JestRunner',

    # Web automation runners
    'PlaywrightRunner',
    'SeleniumRunner',
    'AppiumRunner',

    # Specialized runners
    'RobotRunner',
    'HypothesisRunner',
    'JmeterRunner',
]
