#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY WRAPPER

This module maintains backward compatibility while the codebase migrates
to the new modular structure in coding_standards/scanner/.

All functionality has been refactored into:
- coding_standards/scanner/models.py - Violation value object
- coding_standards/scanner/checkers.py - NestedIfChecker, ElifChainChecker
- coding_standards/scanner/ast_visitor.py - CodeStandardsVisitor
- coding_standards/scanner/todo_scanner.py - TodoCommentScanner
- coding_standards/scanner/file_finder.py - PythonFileFinder
- coding_standards/scanner/scanner.py - CodeStandardsScanner orchestrator
- coding_standards/scanner/reporter.py - Reporting logic

To migrate your code:
    OLD: from code_standards_scanner import CodeStandardsScanner, Violation
    NEW: from coding_standards.scanner import CodeStandardsScanner, Violation

No breaking changes - all imports remain identical.
"""

# Re-export all public APIs from the modular package
from coding_standards.scanner import (
    Violation,
    CodeStandardsScanner,
)

__all__ = [
    'Violation',
    'CodeStandardsScanner',
]

# Main CLI entry point
if __name__ == '__main__':
    from coding_standards.scanner.scanner import main
    main()
