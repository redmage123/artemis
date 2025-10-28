#!/usr/bin/env python3
"""
WHY: Schema Normalization for Code Review Responses
RESPONSIBILITY: Convert different LLM response formats to standardized schema
PATTERNS: Guard clauses, early returns, single responsibility
"""

from typing import Dict, Any, List, Tuple


def normalize_review_schema(category_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize category-based schema to expected review_summary/issues format.

    WHY: LLM may return different schemas depending on prompt version.
    RESPONSIBILITY: Ensure consistent internal format for downstream processing.

    Args:
        category_data: Dict with category keys (security, solid_principles, etc.)

    Returns:
        Normalized dict with review_summary and issues keys
    """
    # Collect all issues from all categories
    all_issues, severity_counts = collect_issues_from_categories(category_data)

    # Calculate scores and status
    total_issues = len(all_issues)
    overall_score = calculate_overall_score(severity_counts)
    overall_status = determine_overall_status(severity_counts, total_issues)

    # Build normalized structure
    return {
        'review_summary': {
            'overall_status': overall_status,
            'total_issues': total_issues,
            'critical_issues': severity_counts['critical'],
            'high_issues': severity_counts['high'],
            'medium_issues': severity_counts['medium'],
            'low_issues': severity_counts['low'],
            'score': {
                'overall': overall_score,
                'code_quality': 100,  # Default scores
                'security': 100,
                'gdpr_compliance': 100,
                'accessibility': 100
            }
        },
        'issues': all_issues,
        'categories': category_data  # Preserve original category data
    }


def collect_issues_from_categories(category_data: Dict[str, Any]) -> Tuple[List[Dict], Dict[str, int]]:
    """
    Collect all issues from categories and count by severity.

    WHY: Extracted to avoid nested loops in normalize_review_schema.
    RESPONSIBILITY: Single-pass collection and counting.

    Args:
        category_data: Dictionary with category keys and issue data

    Returns:
        Tuple of (all_issues list, severity_counts dict)
    """
    all_issues = []
    severity_counts = {
        'critical': 0,
        'high': 0,
        'medium': 0,
        'low': 0
    }

    for category, data in category_data.items():
        if not isinstance(data, dict):
            continue

        category_issues = data.get('issues', [])
        if not isinstance(category_issues, list):
            continue

        # Process each issue in this category
        processed_issues = process_category_issues(category, category_issues, severity_counts)
        all_issues.extend(processed_issues)

    return all_issues, severity_counts


def process_category_issues(
    category: str,
    category_issues: List[Dict],
    severity_counts: Dict[str, int]
) -> List[Dict]:
    """
    Process issues from a single category.

    WHY: Extracted to avoid nested loop in collect_issues_from_categories.
    RESPONSIBILITY: Issue enrichment and severity counting.

    Args:
        category: Category name
        category_issues: List of issues for this category
        severity_counts: Dictionary to update with severity counts

    Returns:
        List of processed issues
    """
    processed_issues = []

    for issue in category_issues:
        if not isinstance(issue, dict):
            continue

        # Add category to issue if not present
        if 'category' not in issue:
            issue['category'] = category

        # Count by severity
        severity = issue.get('severity', 'low').lower()
        if severity in severity_counts:
            severity_counts[severity] += 1

        processed_issues.append(issue)

    return processed_issues


def calculate_overall_score(severity_counts: Dict[str, int]) -> int:
    """
    Calculate overall score based on severity counts.

    WHY: Extracted to avoid complex calculation in normalize_review_schema.
    RESPONSIBILITY: Score calculation logic.
    PATTERN: Single responsibility, pure function.

    Args:
        severity_counts: Dictionary with counts for each severity level

    Returns:
        Overall score (0-100)
    """
    score = 100
    score -= severity_counts['critical'] * 20
    score -= severity_counts['high'] * 10
    score -= severity_counts['medium'] * 5
    score -= severity_counts['low'] * 2
    return max(0, score)


def determine_overall_status(severity_counts: Dict[str, int], total_issues: int) -> str:
    """
    Determine overall status using early returns pattern.

    WHY: Extracted to avoid nested if in normalize_review_schema.
    RESPONSIBILITY: Status determination logic.
    PATTERN: Guard clauses with early returns.

    Args:
        severity_counts: Dictionary with counts for each severity level
        total_issues: Total number of issues

    Returns:
        Overall status string
    """
    if severity_counts['critical'] > 0:
        return "REJECTED"
    if severity_counts['high'] > 3:
        return "NEEDS_IMPROVEMENT"
    if total_issues == 0:
        return "APPROVED"
    return "CONDITIONAL_APPROVAL"
