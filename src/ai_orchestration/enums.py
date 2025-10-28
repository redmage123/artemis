#!/usr/bin/env python3
"""
Enumeration types for orchestration planning

WHY:
Enumerations provide type-safe, validated constants for complexity levels and execution strategies,
preventing invalid string values and improving code maintainability.

RESPONSIBILITY:
- Define Complexity levels (SIMPLE, MEDIUM, COMPLEX)
- Define ExecutionStrategy types (SEQUENTIAL, PARALLEL)
- Provide validation sets for O(1) membership checks

PATTERNS:
- Enum Pattern: Type-safe constants with validation
- Immutability: Enums are immutable by design
"""

from enum import Enum


class Complexity(Enum):
    """Task complexity levels"""
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"


class ExecutionStrategy(Enum):
    """Pipeline execution strategies"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"


# Performance: O(1) validation sets instead of O(n) list searches
VALID_COMPLEXITIES = {c.value for c in Complexity}
VALID_EXECUTION_STRATEGIES = {s.value for s in ExecutionStrategy}
