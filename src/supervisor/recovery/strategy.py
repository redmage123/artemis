#!/usr/bin/env python3
"""
Module: supervisor/recovery/strategy.py

WHY: Base class for recovery strategies following Strategy pattern
RESPONSIBILITY: Define interface for pluggable recovery strategies
PATTERNS: Strategy (polymorphic recovery strategies), Template Method (common recovery workflow)

Design Philosophy:
- Each strategy knows if it can handle a given error
- Strategies are tried in sequence (Chain of Responsibility)
- New strategies can be added without modifying existing code (Open/Closed Principle)
"""

from typing import Dict, Any, Optional


class RecoveryStrategy:
    """
    Base class for recovery strategies.

    WHY: Provides polymorphic interface for different recovery approaches
    RESPONSIBILITY: Define contract for all recovery strategies

    Design Pattern: Strategy + Template Method
    - can_handle(): Hook method to check if strategy applies
    - recover(): Template method for recovery execution

    Subclasses implement:
    - can_handle(): Check if this strategy can handle the error
    - recover(): Attempt recovery and return result
    """

    def __init__(self, name: str):
        """
        Initialize recovery strategy.

        Args:
            name: Human-readable strategy name for logging
        """
        self.name = name

    def can_handle(self, error: Exception, context: Dict[str, Any]) -> bool:
        """
        Check if this strategy can handle the error.

        WHY: Pre-condition check avoids wasted recovery attempts
        PERFORMANCE: O(1) pattern matching on error type/message

        Args:
            error: The exception that occurred
            context: Execution context with error details

        Returns:
            True if this strategy can handle the error
        """
        return False

    def recover(self, error: Exception, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Attempt recovery using this strategy.

        WHY: Execute strategy-specific recovery logic
        PERFORMANCE: Varies by strategy (O(1) to O(n))

        Args:
            error: The exception that occurred
            context: Execution context with error details

        Returns:
            Recovery result dict if successful, None if failed
            Result dict contains:
            - success: bool - Whether recovery succeeded
            - strategy: str - Name of this strategy
            - message: str - Human-readable result message
            - Additional strategy-specific fields
        """
        return None
