#!/usr/bin/env python3
"""
WHY: Format commit messages according to different conventions
RESPONSIBILITY: Provide pluggable commit message formatting strategies
PATTERNS: Strategy Pattern, Factory Pattern
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Type

from .models import CommitConvention, ARTEMIS_FOOTER


# ============================================================================
# STRATEGY PATTERN - Commit Message Formatters
# ============================================================================

class CommitMessageFormatter(ABC):
    """
    WHY: Abstract interface for commit message formatting
    RESPONSIBILITY: Define contract for commit formatting
    PATTERNS: Strategy Pattern base class
    """

    @abstractmethod
    def format(
        self,
        message: str,
        commit_type: Optional[str],
        scope: Optional[str]
    ) -> str:
        """
        WHY: Format commit message according to convention
        RESPONSIBILITY: Apply formatting rules to message
        """
        pass


class ConventionalCommitFormatter(CommitMessageFormatter):
    """
    WHY: Implement Conventional Commits specification
    RESPONSIBILITY: Format commits as type(scope): message
    PATTERNS: Strategy Pattern implementation
    """

    def format(
        self,
        message: str,
        commit_type: Optional[str],
        scope: Optional[str]
    ) -> str:
        """
        WHY: Apply conventional commit format
        RESPONSIBILITY: Build formatted message string
        PATTERNS: Guard clauses for early returns
        """
        if not commit_type:
            return message

        if scope:
            return f"{commit_type}({scope}): {message}"

        return f"{commit_type}: {message}"


class PlainCommitFormatter(CommitMessageFormatter):
    """
    WHY: Support plain commit messages without conventions
    RESPONSIBILITY: Pass through message without formatting
    PATTERNS: Strategy Pattern implementation (null object)
    """

    def format(
        self,
        message: str,
        commit_type: Optional[str],
        scope: Optional[str]
    ) -> str:
        """Return message unchanged"""
        return message


# ============================================================================
# FACTORY PATTERN
# ============================================================================

class CommitFormatterFactory:
    """
    WHY: Create appropriate formatter based on convention
    RESPONSIBILITY: Instantiate correct formatter implementation
    PATTERNS: Factory Pattern with dispatch table
    """

    _formatters: Dict[CommitConvention, Type[CommitMessageFormatter]] = {
        CommitConvention.CONVENTIONAL: ConventionalCommitFormatter,
        CommitConvention.SEMANTIC: ConventionalCommitFormatter,
        CommitConvention.CUSTOM: PlainCommitFormatter,
    }

    @classmethod
    def create(cls, convention: CommitConvention) -> CommitMessageFormatter:
        """
        WHY: Provide single point of formatter instantiation
        RESPONSIBILITY: Create and return formatter instance
        PATTERNS: Factory method with default fallback
        """
        formatter_class = cls._formatters.get(convention, PlainCommitFormatter)
        return formatter_class()

    @classmethod
    def register_formatter(
        cls,
        convention: CommitConvention,
        formatter_class: Type[CommitMessageFormatter]
    ) -> None:
        """
        WHY: Allow extension with custom formatters
        RESPONSIBILITY: Register new formatter implementations
        PATTERNS: Open/Closed Principle
        """
        cls._formatters[convention] = formatter_class


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def add_artemis_footer(message: str) -> str:
    """
    WHY: Add consistent Artemis signature to commits
    RESPONSIBILITY: Append Artemis footer to message
    PATTERNS: Single Responsibility Principle
    """
    return message + ARTEMIS_FOOTER
