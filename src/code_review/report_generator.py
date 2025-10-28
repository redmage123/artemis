#!/usr/bin/env python3
"""
WHY: Generate Code Review Reports in Multiple Formats
RESPONSIBILITY: Create JSON and Markdown reports from review data
PATTERNS: Single responsibility, guard clauses, dispatch tables
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from collections import defaultdict

from artemis_exceptions import FileWriteError, wrap_exception


def write_review_report(
    review_data: Dict[str, Any],
    output_dir: str,
    developer_name: str,
    logger: Optional[logging.Logger] = None
) -> str:
    """
    Write the review report to JSON and Markdown files.

    WHY: Dual format output for machine and human consumption.
    RESPONSIBILITY: Orchestrate report generation.
    PATTERN: Guard clauses, single responsibility.

    Args:
        review_data: Complete review data dictionary
        output_dir: Directory to write reports
        developer_name: Developer identifier for filenames
        logger: Optional logger

    Returns:
        Path to JSON report file

    Raises:
        FileWriteError: If file writing fails
    """
    try:
        os.makedirs(output_dir, exist_ok=True)

        # Write JSON report
        report_file = os.path.join(output_dir, f"code_review_{developer_name}.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(review_data, f, indent=2)

        if logger:
            logger.info(f"📄 Review report written to: {report_file}")

        # Write Markdown summary
        summary_file = os.path.join(output_dir, f"code_review_{developer_name}_summary.md")
        write_review_summary(review_data, summary_file, developer_name, logger)

        return report_file

    except Exception as e:
        raise wrap_exception(
            e,
            FileWriteError,
            "Failed to write review report",
            {
                "output_dir": output_dir,
                "developer_name": developer_name
            }
        )


def write_review_summary(
    review_data: Dict[str, Any],
    summary_file: str,
    developer_name: str,
    logger: Optional[logging.Logger] = None
) -> None:
    """
    Write a human-readable markdown summary.

    WHY: Developers need readable summaries, not just JSON.
    RESPONSIBILITY: Generate formatted markdown report.
    PATTERN: Single responsibility, composition.

    Args:
        review_data: Complete review data dictionary
        summary_file: Path to markdown file
        developer_name: Developer identifier
        logger: Optional logger
    """
    summary = review_data['review_summary']
    issues = review_data['issues']

    # Build markdown content in sections
    md_content = build_header_section(developer_name, summary)
    md_content += build_issues_summary_section(summary)
    md_content += build_critical_issues_section(issues)
    md_content += build_high_issues_section(issues)
    md_content += build_positive_findings_section(review_data)
    md_content += build_recommendations_section(review_data)

    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(md_content)

    if logger:
        logger.info(f"📄 Review summary written to: {summary_file}")


def build_header_section(developer_name: str, summary: Dict[str, Any]) -> str:
    """
    Build markdown header section with overall assessment.

    WHY: Extracted for readability and testability.
    RESPONSIBILITY: Format header and scores.

    Args:
        developer_name: Developer identifier
        summary: Review summary dictionary

    Returns:
        Markdown string for header section
    """
    return f"""# Code Review Summary - {developer_name}

## Overall Assessment

**Status:** {summary['overall_status']}

**Overall Score:** {summary['score']['overall']}/100

### Category Scores

- **Code Quality:** {summary['score']['code_quality']}/100
- **Security:** {summary['score']['security']}/100
- **GDPR Compliance:** {summary['score']['gdpr_compliance']}/100
- **Accessibility:** {summary['score']['accessibility']}/100

"""


def build_issues_summary_section(summary: Dict[str, Any]) -> str:
    """
    Build issues summary section with counts.

    WHY: Extracted for clarity and single responsibility.
    RESPONSIBILITY: Format issue counts.

    Args:
        summary: Review summary dictionary

    Returns:
        Markdown string for issues summary
    """
    return f"""### Issues Summary

- **Critical:** {summary['critical_issues']}
- **High:** {summary['high_issues']}
- **Medium:** {summary['medium_issues']}
- **Low:** {summary['low_issues']}
- **Total:** {summary['total_issues']}

"""


def build_critical_issues_section(issues: List[Dict[str, Any]]) -> str:
    """
    Build critical issues section with detailed information.

    WHY: Critical issues need full visibility.
    RESPONSIBILITY: Format critical issues with code snippets.

    Args:
        issues: List of all issues

    Returns:
        Markdown string for critical issues
    """
    # Categorize issues by severity (Performance: Single-pass O(n))
    issues_by_severity = defaultdict(list)
    for issue in issues:
        issues_by_severity[issue['severity']].append(issue)

    critical = issues_by_severity['CRITICAL']

    md_content = "## Critical Issues\n\n"

    if critical:
        md_content += '\n'.join(
            format_critical_issue(issue)
            for issue in critical
        )
    else:
        md_content += "_No critical issues found._\n\n"

    return md_content


def format_critical_issue(issue: Dict[str, Any]) -> str:
    """
    Format a single critical issue with all details.

    WHY: Extracted to avoid nested string formatting.
    RESPONSIBILITY: Single issue formatting.

    Args:
        issue: Issue dictionary

    Returns:
        Formatted markdown string for issue
    """
    return f"""
### {issue['category']} - {issue['subcategory']}

**File:** `{issue['file']}:{issue['line']}`

**Description:** {issue['description']}

**Code:**
```
{issue['code_snippet']}
```

**Recommendation:** {issue['recommendation']}

---
"""


def build_high_issues_section(issues: List[Dict[str, Any]]) -> str:
    """
    Build high priority issues section with brief listings.

    WHY: High issues need visibility but less detail than critical.
    RESPONSIBILITY: Format high priority issues concisely.

    Args:
        issues: List of all issues

    Returns:
        Markdown string for high issues
    """
    # Categorize issues by severity
    issues_by_severity = defaultdict(list)
    for issue in issues:
        issues_by_severity[issue['severity']].append(issue)

    high = issues_by_severity['HIGH']

    md_content = "## High Priority Issues\n\n"

    if high:
        md_content += '\n'.join(
            f"- **{issue['category']}** ({issue['file']}:{issue['line']}): {issue['description']}"
            for issue in high[:5]  # Top 5 high issues
        ) + '\n'
    else:
        md_content += "_No high priority issues found._\n\n"

    return md_content


def build_positive_findings_section(review_data: Dict[str, Any]) -> str:
    """
    Build positive findings section.

    WHY: Recognize good practices, not just problems.
    RESPONSIBILITY: Format positive findings list.

    Args:
        review_data: Complete review data

    Returns:
        Markdown string for positive findings
    """
    if 'positive_findings' not in review_data or not review_data['positive_findings']:
        return ""

    md_content = "\n## Positive Findings\n\n"
    md_content += '\n'.join(
        f"- {finding}"
        for finding in review_data['positive_findings']
    ) + '\n'

    return md_content


def build_recommendations_section(review_data: Dict[str, Any]) -> str:
    """
    Build recommendations section.

    WHY: Provide actionable guidance for improvement.
    RESPONSIBILITY: Format recommendations list.

    Args:
        review_data: Complete review data

    Returns:
        Markdown string for recommendations
    """
    if 'recommendations' not in review_data or not review_data['recommendations']:
        return ""

    md_content = "\n## Recommendations\n\n"
    md_content += '\n'.join(
        f"- {rec}"
        for rec in review_data['recommendations']
    ) + '\n'

    return md_content
