#!/usr/bin/env python3
"""
WHY: Provide public API for code standards scanning
RESPONSIBILITY: Export scanner classes and models
PATTERNS: Facade (simplified package interface)

Scanner package provides AST-based code standards checking.
"""

from coding_standards.scanner.models import Violation
from coding_standards.scanner.scanner import CodeStandardsScanner

__all__ = [
    'Violation',
    'CodeStandardsScanner',
]
