#!/usr/bin/env python3
"""
Module: Code Refactoring Agent - Backward Compatibility Wrapper

WHY: Maintains backward compatibility with existing code that imports
     from code_refactoring_agent module. Delegates to refactored package.

RESPONSIBILITY:
    - Re-export public API from agents.refactoring package
    - Preserve original module interface
    - Support existing import statements
    - Provide migration path to new package

PATTERNS:
    - Facade Pattern: Wraps new implementation with old interface
    - Adapter Pattern: Adapts new API to old expectations

MIGRATION:
    Old: from code_refactoring_agent import CodeRefactoringAgent
    New: from agents.refactoring import CodeRefactoringAgent

    This wrapper allows both styles to work during transition period.

ARCHITECTURE:
    - Refactored implementation lives in agents/refactoring/
    - This file is a thin wrapper for backward compatibility
    - Will be deprecated in future version

DEPRECATION NOTICE:
    This module is maintained for backward compatibility only.
    New code should import from agents.refactoring package directly.
    See agents/refactoring/__init__.py for public API.
"""

# Import all public API from refactored package
from agents.refactoring import (
    CodeRefactoringAgent,
    create_refactoring_agent,
    RefactoringRule,
    RefactoringAnalysis,
    CodeSmell,
    LongMethodSmell,
    SimpleLoopSmell,
    IfElifChainSmell,
    PatternType,
    RefactoringPriority
)

# Re-export for backward compatibility
__all__ = [
    'CodeRefactoringAgent',
    'create_refactoring_agent',
    'RefactoringRule',
    'RefactoringAnalysis',
    'CodeSmell',
    'LongMethodSmell',
    'SimpleLoopSmell',
    'IfElifChainSmell',
    'PatternType',
    'RefactoringPriority',
]


# Preserve original main block for testing
if __name__ == "__main__":
    """
    Example usage demonstrating backward compatibility.

    WHY: Maintains original test behavior for regression testing.
    """
    import sys
    from pathlib import Path

    # Create agent using wrapper
    agent = create_refactoring_agent()

    # Analyze this file (now a wrapper)
    file_path = Path(__file__)
    analysis = agent.analyze_file_for_refactoring(file_path)

    print("\nRefactoring Analysis:")
    print(f"File: {analysis['file']}")
    print(f"Total Issues: {analysis['total_issues']}")

    if analysis.get('long_methods'):
        print(f"\nLong Methods: {len(analysis['long_methods'])}")
        for method in analysis['long_methods']:
            print(f"  - {method['name']} ({method['length']} lines)")

    # Generate instructions
    instructions = agent.generate_refactoring_instructions(analysis)
    print("\n" + instructions)

    print("\n" + "=" * 60)
    print("BACKWARD COMPATIBILITY WRAPPER ACTIVE")
    print("=" * 60)
    print("This module delegates to agents.refactoring package.")
    print("Consider migrating to: from agents.refactoring import ...")
    print("=" * 60)
