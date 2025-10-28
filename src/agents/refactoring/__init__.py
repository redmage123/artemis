#!/usr/bin/env python3
"""
Package: agents.refactoring - Modular Code Refactoring System

WHY: Provides automated code quality analysis and refactoring suggestions
     for Python codebases. Separates concerns into focused, testable modules.

RESPONSIBILITY:
    - Export public API for refactoring operations
    - Expose core agent and factory function
    - Expose model classes for type hints
    - Hide internal implementation details

PATTERNS:
    - Facade Pattern: Public API hides internal module structure
    - Module Pattern: Controlled exports prevent namespace pollution

ARCHITECTURE:
    - models.py: Data structures (RefactoringRule, CodeSmell, etc.)
    - analyzer.py: AST-based code smell detection
    - suggestion_generator.py: Markdown instruction generation
    - transformer.py: Code transformation framework (future)
    - agent_core.py: Main orchestration facade

PUBLIC API:
    - CodeRefactoringAgent: Main agent class
    - create_refactoring_agent(): Factory function
    - RefactoringRule: Rule metadata model
    - RefactoringAnalysis: Analysis result model
    - PatternType: Code smell category enum
    - RefactoringPriority: Priority level enum
"""

# Import public API from agent_core
from .agent_core import (
    CodeRefactoringAgent,
    create_refactoring_agent
)

# Import models for type hints and data structures
from .models import (
    RefactoringRule,
    RefactoringAnalysis,
    CodeSmell,
    LongMethodSmell,
    SimpleLoopSmell,
    IfElifChainSmell,
    PatternType,
    RefactoringPriority
)

# Define public API
__all__ = [
    # Main agent interface
    'CodeRefactoringAgent',
    'create_refactoring_agent',

    # Model classes
    'RefactoringRule',
    'RefactoringAnalysis',
    'CodeSmell',
    'LongMethodSmell',
    'SimpleLoopSmell',
    'IfElifChainSmell',

    # Enumerations
    'PatternType',
    'RefactoringPriority',
]

# Package metadata
__version__ = '2.0.0'
__author__ = 'Artemis Team'
__description__ = 'Modular code refactoring and quality analysis system'
