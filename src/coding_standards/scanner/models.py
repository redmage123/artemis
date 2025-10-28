#!/usr/bin/env python3
"""
WHY: Define violation model
RESPONSIBILITY: Represent code standards violations
PATTERNS: Value Object (immutable violation)

Violation provides structured representation of code issues.
"""

from dataclasses import dataclass


@dataclass
class Violation:
    """
    Represents a coding standards violation.

    WHY: Structured violation data enables consistent reporting.
    RESPONSIBILITY: Carry violation details (location, type, severity, context).
    PATTERNS: Value Object (immutable data).
    """
    file_path: str
    line_number: int
    violation_type: str
    severity: str  # 'critical', 'warning', 'info'
    message: str
    context: str = ""
