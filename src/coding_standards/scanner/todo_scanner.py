#!/usr/bin/env python3
"""
WHY: Scan for TODO/FIXME comments
RESPONSIBILITY: Detect unresolved TODO comments
PATTERNS: Scanner (text-based detection)

TODO scanner ensures code is production-ready.
"""

from typing import List
from coding_standards.scanner.models import Violation


class TodoCommentScanner:
    """
    Scans for TODO comments.

    WHY: TODO comments indicate unfinished work.
    RESPONSIBILITY: Detect and report TODO/FIXME/XXX comments.
    PATTERNS: Scanner pattern.
    """

    # TODO markers to detect
    TODO_MARKERS = ['# TODO', '# FIXME', '# XXX']

    @staticmethod
    def scan_file(file_path: str, source_lines: List[str]) -> List[Violation]:
        """
        Scan for TODO comments in source.

        WHY: Contextual check - TODOs in tests/examples are acceptable.

        Args:
            file_path: File path for violation reporting
            source_lines: Source code lines

        Returns:
            List of TODO violations
        """
        violations = []

        for i, line in enumerate(source_lines, 1):
            # Check if line contains any TODO marker
            if not any(marker in line for marker in TodoCommentScanner.TODO_MARKERS):
                continue

            # Guard clause - TODOs in tests or examples are OK
            if 'test_' in file_path or 'example' in file_path:
                continue

            violations.append(Violation(
                file_path=file_path,
                line_number=i,
                violation_type='todo_comment',
                severity='info',
                message='TODO comment found - resolve before production',
                context=line.strip()
            ))

        return violations
