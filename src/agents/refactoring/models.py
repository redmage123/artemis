#!/usr/bin/env python3
"""
Module: Refactoring Models - Data Structures for Code Analysis

WHY: Encapsulates refactoring-related data structures to provide type safety,
     validation, and clear contracts for code analysis components.

RESPONSIBILITY:
    - Define refactoring rule metadata structure
    - Define code smell detection results
    - Define analysis report structures
    - Provide immutable value objects for refactoring data

PATTERNS:
    - Value Object Pattern: Immutable data containers with clear semantics
    - Data Transfer Object: Structures for passing analysis results between layers
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class RefactoringPriority(Enum):
    """
    Priority levels for refactoring suggestions.

    WHY: Explicit enumeration prevents magic numbers and provides
         type-safe priority comparisons.
    """
    CRITICAL = 1  # Security issues, broken code
    HIGH = 2      # Performance issues, maintainability
    MEDIUM = 3    # Code style, minor improvements
    LOW = 4       # Optional enhancements


class PatternType(Enum):
    """
    Categories of refactoring patterns detected by analysis.

    WHY: Enables dispatch table routing and categorical filtering.
    """
    LOOP = "loop"
    IF_ELIF = "if_elif"
    LONG_METHOD = "long_method"
    DUPLICATION = "duplication"
    COLLECTIONS = "collections"
    GENERATOR = "generator"


@dataclass
class RefactoringRule:
    """
    Represents a single refactoring pattern rule.

    WHY: Encapsulates refactoring metadata for prioritization and tracking.
         Provides single source of truth for rule configuration.

    RESPONSIBILITY:
        - Store rule identification and categorization
        - Maintain human-readable descriptions
        - Define rule priority for triage

    PATTERN: Value Object - immutable data container.

    Attributes:
        name: Unique identifier for the refactoring rule
        pattern_type: Category (PatternType enum)
        description: Human-readable explanation of the refactoring
        priority: Urgency level (RefactoringPriority enum)
    """
    name: str
    pattern_type: PatternType
    description: str
    priority: RefactoringPriority

    def __post_init__(self):
        """Validate rule data after initialization."""
        if not self.name:
            raise ValueError("Rule name cannot be empty")
        if not self.description:
            raise ValueError("Rule description cannot be empty")


@dataclass
class CodeSmell:
    """
    Represents a detected code smell (anti-pattern) in source code.

    WHY: Standardizes code smell reporting across different analyzers.
         Provides structured data for suggestion generation.

    RESPONSIBILITY:
        - Store location information (file, line)
        - Categorize smell by pattern type
        - Provide actionable suggestion text
        - Track severity/priority

    PATTERN: Data Transfer Object

    Attributes:
        file_path: Path to file containing the smell
        line_number: Starting line of the code smell
        pattern_type: Category of anti-pattern detected
        suggestion: Human-readable refactoring recommendation
        priority: Urgency level for fixing
        metadata: Additional context (e.g., method length, elif count)
    """
    file_path: str
    line_number: int
    pattern_type: PatternType
    suggestion: str
    priority: RefactoringPriority
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate code smell data."""
        if self.line_number < 1:
            raise ValueError("Line number must be positive")
        if not self.suggestion:
            raise ValueError("Suggestion cannot be empty")


@dataclass
class LongMethodSmell(CodeSmell):
    """
    Specialized code smell for long methods.

    WHY: Provides type-specific metadata (method name, length)
         for long method detection.
    """
    method_name: str = ""
    method_length: int = 0

    def __post_init__(self):
        """Initialize with long method specific data."""
        super().__post_init__()
        if not self.metadata.get('method_name'):
            self.metadata['method_name'] = self.method_name
        if not self.metadata.get('method_length'):
            self.metadata['method_length'] = self.method_length


@dataclass
class SimpleLoopSmell(CodeSmell):
    """
    Specialized code smell for simple loops convertible to comprehensions.

    WHY: Provides context about loop type and operation for better suggestions.
    """
    loop_operation: str = ""  # 'append', 'add', 'update'

    def __post_init__(self):
        """Initialize with loop-specific data."""
        super().__post_init__()
        if not self.metadata.get('loop_operation'):
            self.metadata['loop_operation'] = self.loop_operation


@dataclass
class IfElifChainSmell(CodeSmell):
    """
    Specialized code smell for if/elif chains.

    WHY: Tracks number of branches for prioritization.
    """
    elif_count: int = 0

    def __post_init__(self):
        """Initialize with if/elif chain specific data."""
        super().__post_init__()
        if not self.metadata.get('elif_count'):
            self.metadata['elif_count'] = self.elif_count


@dataclass
class RefactoringAnalysis:
    """
    Complete analysis report for a single file.

    WHY: Aggregates all detected code smells in a structured format.
         Provides summary statistics for quick assessment.

    RESPONSIBILITY:
        - Store file identification
        - Aggregate code smells by category
        - Compute summary statistics
        - Handle analysis errors gracefully

    PATTERN: Aggregate Root - manages collection of related entities

    Attributes:
        file_path: Path to analyzed file
        long_methods: List of long method smells
        simple_loops: List of simple loop smells
        if_elif_chains: List of if/elif chain smells
        total_issues: Computed count of all issues
        error: Optional error message if analysis failed
    """
    file_path: str
    long_methods: List[LongMethodSmell] = field(default_factory=list)
    simple_loops: List[SimpleLoopSmell] = field(default_factory=list)
    if_elif_chains: List[IfElifChainSmell] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def total_issues(self) -> int:
        """
        Compute total number of issues detected.

        WHY: Computed property ensures count is always accurate.
        """
        return (
            len(self.long_methods) +
            len(self.simple_loops) +
            len(self.if_elif_chains)
        )

    @property
    def has_errors(self) -> bool:
        """Check if analysis encountered errors."""
        return self.error is not None

    @property
    def all_smells(self) -> List[CodeSmell]:
        """
        Get all code smells as a flat list.

        WHY: Simplifies iteration when category doesn't matter.
        """
        return [
            *self.long_methods,
            *self.simple_loops,
            *self.if_elif_chains
        ]

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert analysis to dictionary format.

        WHY: Maintains backward compatibility with original API.
        """
        return {
            'file': self.file_path,
            'long_methods': [
                {
                    'name': smell.metadata.get('method_name', ''),
                    'line': smell.line_number,
                    'length': smell.metadata.get('method_length', 0),
                    'suggestion': smell.suggestion
                }
                for smell in self.long_methods
            ],
            'simple_loops': [
                {
                    'line': smell.line_number,
                    'suggestion': smell.suggestion
                }
                for smell in self.simple_loops
            ],
            'if_elif_chains': [
                {
                    'line': smell.line_number,
                    'elif_count': smell.metadata.get('elif_count', 0),
                    'suggestion': smell.suggestion
                }
                for smell in self.if_elif_chains
            ],
            'total_issues': self.total_issues,
            'error': self.error
        }
