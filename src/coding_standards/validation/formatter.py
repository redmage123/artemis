#!/usr/bin/env python3
"""
WHY: Format violations for reports and display
RESPONSIBILITY: Convert violations to various output formats
PATTERNS: Formatter (presentation logic), Dispatch Table (icons)

Formatter transforms validation data into human-readable reports.
"""

from typing import List, Dict, Any


class ViolationFormatter:
    """
    Formats violations for reports.

    WHY: Different consumers need different formats (dict, markdown, CLI).
    PATTERNS: Formatter pattern, Dispatch table (severity icons).
    """

    # Dispatch table for severity icons
    SEVERITY_ICONS = {
        'critical': '🚨',
        'warning': '⚠️',
        'info': 'ℹ️'
    }

    def format_as_dicts(
        self,
        violations_by_type: Dict[str, List]
    ) -> List[Dict[str, Any]]:
        """
        Convert Violation objects to simple dicts.

        WHY: Dicts are easier to serialize and consume in pipeline.

        Args:
            violations_by_type: Violations grouped by type

        Returns:
            List of violation dicts
        """
        result = []

        for v_type, violations in violations_by_type.items():
            for v in violations:
                result.append({
                    'file': v.file_path,
                    'line': v.line_number,
                    'type': v.violation_type,
                    'severity': v.severity,
                    'message': v.message,
                    'context': v.context
                })

        return result

    def format_as_markdown_report(
        self,
        violations: List[Dict[str, Any]]
    ) -> str:
        """
        Format violations for inclusion in code review report.

        WHY: Code review stage needs markdown-formatted violations.

        Args:
            violations: List of violation dicts

        Returns:
            Formatted markdown string

        Example:
            ## Code Standards Violations
            ### 📄 src/file.py
            - **Line 42** 🚨 [CRITICAL]: Deep nesting detected
        """
        # Guard clause - early return for no violations
        if not violations:
            return "✅ **No code standards violations found**\n"

        # Group by file
        violations_by_file = self._group_by_file(violations)

        # Build markdown
        lines = ["## Code Standards Violations\n"]

        for file_path, file_violations in sorted(violations_by_file.items()):
            lines.append(f"### 📄 {file_path}\n")

            for v in sorted(file_violations, key=lambda x: x['line']):
                severity_icon = self.SEVERITY_ICONS.get(v['severity'], '•')
                lines.append(
                    f"- **Line {v['line']}** {severity_icon} [{v['severity'].upper()}]: "
                    f"{v['message']}\n"
                )

            lines.append("")  # Blank line between files

        # Add summary
        lines.append(self._format_summary_section(violations))

        return "".join(lines)

    def create_summary(
        self,
        files_scanned: int,
        violations: List[Dict[str, Any]],
        severity_threshold: str
    ) -> str:
        """
        Create human-readable summary.

        WHY: Provides quick status overview.

        Args:
            files_scanned: Number of files scanned
            violations: List of violations
            severity_threshold: Threshold used

        Returns:
            Summary string
        """
        # Guard clause - all valid
        if not violations:
            return (
                f"✅ All {files_scanned} files passed code standards check "
                f"(threshold: {severity_threshold})"
            )

        # Count by severity
        critical_count = sum(1 for v in violations if v['severity'] == 'critical')
        warning_count = sum(1 for v in violations if v['severity'] == 'warning')
        info_count = sum(1 for v in violations if v['severity'] == 'info')

        return (
            f"❌ Found {len(violations)} violations in {files_scanned} files "
            f"(Critical: {critical_count}, Warning: {warning_count}, Info: {info_count})"
        )

    def _group_by_file(self, violations: List[Dict[str, Any]]) -> Dict[str, List]:
        """Group violations by file"""
        violations_by_file = {}
        for v in violations:
            file_path = v['file']
            if file_path not in violations_by_file:
                violations_by_file[file_path] = []
            violations_by_file[file_path].append(v)

        return violations_by_file

    def _format_summary_section(self, violations: List[Dict[str, Any]]) -> str:
        """Format summary section for markdown"""
        critical_count = sum(1 for v in violations if v['severity'] == 'critical')
        warning_count = sum(1 for v in violations if v['severity'] == 'warning')
        info_count = sum(1 for v in violations if v['severity'] == 'info')

        return (
            "### Summary\n"
            f"- 🚨 Critical: {critical_count}\n"
            f"- ⚠️  Warning: {warning_count}\n"
            f"- ℹ️  Info: {info_count}\n"
            f"- **Total**: {len(violations)}\n"
        )
