#!/usr/bin/env python3
"""
WHY: Implement different git branching strategies using Strategy Pattern
RESPONSIBILITY: Provide pluggable branch management strategies
PATTERNS: Strategy Pattern, Factory Pattern
"""

from abc import ABC, abstractmethod
from typing import Dict, Type

from .models import BranchStrategy


# ============================================================================
# STRATEGY PATTERN - Branch Strategies
# ============================================================================

class BranchStrategyHandler(ABC):
    """
    WHY: Abstract interface for branch strategy implementations
    RESPONSIBILITY: Define contract for branch strategy operations
    PATTERNS: Strategy Pattern base class
    """

    @abstractmethod
    def get_base_branch(self, default_branch: str) -> str:
        """
        WHY: Determine correct base branch for feature branches
        RESPONSIBILITY: Return base branch based on strategy
        """
        pass

    @abstractmethod
    def get_branch_prefix(self) -> str:
        """
        WHY: Provide consistent branch naming conventions
        RESPONSIBILITY: Return prefix for feature branches
        """
        pass


class GitFlowStrategyHandler(BranchStrategyHandler):
    """
    WHY: Implement GitFlow branching strategy
    RESPONSIBILITY: Manage main/develop with feature/release/hotfix branches
    PATTERNS: Strategy Pattern implementation
    """

    def get_base_branch(self, default_branch: str) -> str:
        """Always use develop as base in GitFlow"""
        return "develop"

    def get_branch_prefix(self) -> str:
        """Use feature/ prefix for GitFlow"""
        return "feature/"


class GitHubFlowStrategyHandler(BranchStrategyHandler):
    """
    WHY: Implement GitHub Flow branching strategy
    RESPONSIBILITY: Manage main branch with feature branches
    PATTERNS: Strategy Pattern implementation
    """

    def get_base_branch(self, default_branch: str) -> str:
        """Use configured default branch (usually main)"""
        return default_branch

    def get_branch_prefix(self) -> str:
        """Use feature/ prefix for GitHub Flow"""
        return "feature/"


class TrunkBasedStrategyHandler(BranchStrategyHandler):
    """
    WHY: Implement trunk-based development strategy
    RESPONSIBILITY: Manage main branch with short-lived branches
    PATTERNS: Strategy Pattern implementation
    """

    def get_base_branch(self, default_branch: str) -> str:
        """Always use main/trunk"""
        return default_branch

    def get_branch_prefix(self) -> str:
        """No prefix for trunk-based (short-lived branches)"""
        return ""


# ============================================================================
# FACTORY PATTERN
# ============================================================================

class BranchStrategyFactory:
    """
    WHY: Create appropriate strategy handler based on strategy type
    RESPONSIBILITY: Instantiate correct strategy implementation
    PATTERNS: Factory Pattern with dispatch table
    """

    _strategies: Dict[BranchStrategy, Type[BranchStrategyHandler]] = {
        BranchStrategy.GITFLOW: GitFlowStrategyHandler,
        BranchStrategy.GITHUB_FLOW: GitHubFlowStrategyHandler,
        BranchStrategy.TRUNK_BASED: TrunkBasedStrategyHandler,
    }

    @classmethod
    def create(cls, strategy: BranchStrategy) -> BranchStrategyHandler:
        """
        WHY: Provide single point of strategy instantiation
        RESPONSIBILITY: Create and return strategy handler
        PATTERNS: Factory method with default fallback
        """
        handler_class = cls._strategies.get(strategy, GitHubFlowStrategyHandler)
        return handler_class()

    @classmethod
    def register_strategy(
        cls,
        strategy: BranchStrategy,
        handler_class: Type[BranchStrategyHandler]
    ) -> None:
        """
        WHY: Allow extension with custom strategies
        RESPONSIBILITY: Register new strategy handlers
        PATTERNS: Open/Closed Principle
        """
        cls._strategies[strategy] = handler_class
