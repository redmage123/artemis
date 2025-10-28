#!/usr/bin/env python3
"""
Review Feedback - Code review feedback extraction and storage

WHAT:
Utilities for extracting, formatting, and storing code review feedback
in RAG for developer context during retry attempts.

WHY:
Separates review feedback handling from orchestrator core, enabling:
- Focused testing of feedback extraction
- Reusable feedback formatting logic
- Clean separation of concerns
- Easy modification of feedback structure

RESPONSIBILITY:
- Load detailed code review reports from files
- Extract structured feedback from review results
- Format issue lists for display and storage
- Store retry feedback in RAG for developer access
- Handle review report file errors gracefully

PATTERNS:
- Guard Clause: Early returns for missing/invalid data
- Exception Wrapper: Consistent error handling
- Template Method: Standardized feedback format
- Facade Pattern: Simplifies complex feedback operations

EXTRACTED FROM: artemis_orchestrator.py lines 1012-1213
"""

import json
from typing import List, Dict, Any
from pathlib import Path

from artemis_exceptions import FileReadError, RAGStorageError, create_wrapped_exception


def load_review_report(report_file: str, developer_name: str) -> List[Dict]:
    """
    Load detailed issues from a review report file.

    WHAT:
    Reads a code review report JSON file and extracts the list of
    detailed issues found during review.

    WHY:
    Review reports contain rich detail about code quality issues that
    developers need to fix during retry attempts. Loading from file
    separates storage from processing.

    Args:
        report_file: Path to the review report JSON file
        developer_name: Name of the developer for error context

    Returns:
        List of detailed issues, or empty list if file doesn't exist

    Raises:
        FileReadError: If file exists but cannot be read

    PATTERNS:
        - Guard Clause: Early returns for missing file
        - Exception Wrapper: Consistent error handling
    """
    # Guard: No report file specified
    if not report_file:
        return []

    # Guard: Report file doesn't exist
    if not Path(report_file).exists():
        return []

    # Load and parse report file
    try:
        with open(report_file, 'r') as f:
            full_review = json.load(f)
            return full_review.get('issues', [])
    except Exception as e:
        raise create_wrapped_exception(
            e,
            FileReadError,
            "Could not load detailed code review report",
            {
                "report_file": report_file,
                "developer": developer_name
            }
        )


def extract_code_review_feedback(code_review_result: Dict) -> Dict:
    """
    Extract detailed code review feedback for developers

    WHAT:
    Processes code review results and extracts structured feedback
    including issue counts, detailed issues per developer, and
    report file locations.

    WHY:
    Code review results contain nested data that needs to be flattened
    and enriched with detailed issue information from report files.
    This provides developers with actionable feedback during retries.

    Args:
        code_review_result: Result from code review stage

    Returns:
        Dict with structured feedback including specific issues and recommendations

    STRUCTURE:
        {
            'status': str,
            'total_critical_issues': int,
            'total_high_issues': int,
            'developer_reviews': [
                {
                    'developer': str,
                    'review_status': str,
                    'overall_score': int,
                    'critical_issues': int,
                    'high_issues': int,
                    'detailed_issues': List[Dict],
                    'report_file': str
                }
            ]
        }

    PATTERNS:
        - Builder Pattern: Incrementally builds feedback structure
        - Facade Pattern: Simplifies complex review data
    """
    feedback = {
        'status': code_review_result.get('status', 'UNKNOWN'),
        'total_critical_issues': code_review_result.get('total_critical_issues', 0),
        'total_high_issues': code_review_result.get('total_high_issues', 0),
        'developer_reviews': []
    }

    # Extract detailed feedback from each developer's review
    reviews = code_review_result.get('reviews', [])
    for review in reviews:
        developer_name = review.get('developer', 'unknown')
        report_file = review.get('report_file', '')

        # Try to load full review report with detailed issues
        detailed_issues = load_review_report(report_file, developer_name)

        feedback['developer_reviews'].append({
            'developer': developer_name,
            'review_status': review.get('review_status', 'UNKNOWN'),
            'overall_score': review.get('overall_score', 0),
            'critical_issues': review.get('critical_issues', 0),
            'high_issues': review.get('high_issues', 0),
            'detailed_issues': detailed_issues,
            'report_file': report_file
        })

    return feedback


def format_issue_list(issues: List[Dict]) -> str:
    """
    Format a list of code review issues for display.

    WHAT:
    Converts a list of issue dictionaries into a human-readable
    formatted string with severity, category, location, and
    recommended fixes.

    WHY:
    Provides consistent, readable formatting of code review issues
    for storage in RAG and display to developers. Makes issues
    actionable with clear location and fix information.

    Args:
        issues: List of issue dictionaries to format

    Returns:
        Formatted string with issue details

    FORMAT:
        1. [SEVERITY] Category
           File: path/to/file.py:123
           Problem: Description of the issue
           Fix: Recommended solution
           ADR Reference: path/to/adr.md

    PATTERNS:
        - Template Method: Standardized issue format
        - Guard Clause: Handles missing optional fields
    """
    result = ""
    for i, issue in enumerate(issues, 1):
        result += f"{i}. [{issue.get('severity', 'UNKNOWN')}] {issue.get('category', 'Unknown Category')}\n"
        result += f"   File: {issue.get('file', 'Unknown')}"

        # Add line number if present
        if issue.get('line'):
            result += f":{issue.get('line')}"
        result += "\n"

        result += f"   Problem: {issue.get('description', 'No description')}\n"
        result += f"   Fix: {issue.get('recommendation', 'No recommendation')}\n"

        # Add ADR reference if present
        if issue.get('adr_reference'):
            result += f"   ADR Reference: {issue.get('adr_reference')}\n"
        result += "\n"

    return result


def store_retry_feedback_in_rag(
    card: Dict,
    code_review_result: Dict,
    retry_attempt: int,
    rag: Any,
    logger: Any
) -> None:
    """
    Store code review failure feedback in RAG for developer context

    WHAT:
    Creates a comprehensive feedback document from code review results
    and stores it in RAG so developers can query for context during
    retry attempts.

    WHY:
    When code review fails, developers need detailed feedback about
    what went wrong and how to fix it. Storing in RAG enables:
    - Developers can query for relevant fixes
    - Historical context persists across retries
    - Refactoring suggestions are preserved
    - Top issues are prioritized

    STRUCTURE:
        - Task and review metadata
        - Issue counts by severity
        - Top issues per developer (sorted by severity)
        - Refactoring instructions if available

    Args:
        card: Kanban card with task details
        code_review_result: Result from failed code review
        retry_attempt: Current retry attempt number
        rag: RAG agent for storage
        logger: Logger for status messages

    Raises:
        RAGStorageError: If feedback cannot be stored in RAG

    PATTERNS:
        - Builder Pattern: Incrementally builds feedback document
        - Exception Wrapper: Consistent error handling
        - Guard Clause: Handles missing data gracefully
    """
    try:
        card_id = card['card_id']
        task_title = card.get('title', 'Unknown Task')

        # Extract detailed feedback
        feedback = extract_code_review_feedback(code_review_result)

        # Create comprehensive failure report
        content = f"""Code Review Retry Feedback - Attempt {retry_attempt}

Task: {task_title}
Card ID: {card_id}
Review Status: {feedback['status']}
Critical Issues: {feedback['total_critical_issues']}
High Issues: {feedback['total_high_issues']}

DETAILED ISSUES BY DEVELOPER:

"""

        # Add detailed issues for each developer
        for dev_review in feedback['developer_reviews']:
            developer_name = dev_review['developer']
            content += f"\n{'='*60}\n"
            content += f"Developer: {developer_name}\n"
            content += f"Review Status: {dev_review['review_status']}\n"
            content += f"Score: {dev_review['overall_score']}/100\n"
            content += f"Critical Issues: {dev_review['critical_issues']}\n"
            content += f"High Issues: {dev_review['high_issues']}\n"
            content += f"{'='*60}\n\n"

            # Add top 10 most critical issues
            detailed_issues = dev_review.get('detailed_issues', [])

            # Guard: No issues to display
            if not detailed_issues:
                continue

            # Sort by severity (CRITICAL > HIGH > MEDIUM > LOW)
            severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
            sorted_issues = sorted(
                detailed_issues,
                key=lambda x: severity_order.get(x.get('severity', 'LOW'), 4)
            )

            content += "TOP ISSUES TO FIX:\n\n"
            content += format_issue_list(sorted_issues[:10])
            content += "\n"

        # Add refactoring suggestions if available
        refactoring_suggestions = code_review_result.get('refactoring_suggestions')
        if refactoring_suggestions:
            content += f"\n{'='*60}\n"
            content += "REFACTORING INSTRUCTIONS\n"
            content += f"{'='*60}\n\n"
            content += refactoring_suggestions
            content += "\n"

        # Store in RAG
        artifact_id = rag.store_artifact(
            artifact_type="code_review_retry_feedback",
            card_id=card_id,
            task_title=task_title,
            content=content,
            metadata={
                'retry_attempt': retry_attempt,
                'review_status': feedback['status'],
                'total_critical_issues': feedback['total_critical_issues'],
                'total_high_issues': feedback['total_high_issues'],
                'developers': [r['developer'] for r in feedback['developer_reviews']],
                'has_refactoring_suggestions': refactoring_suggestions is not None
            }
        )

        logger.log(f"Stored retry feedback in RAG: {artifact_id}", "DEBUG")

    except Exception as e:
        raise create_wrapped_exception(
            e,
            RAGStorageError,
            "Failed to store retry feedback in RAG",
            {
                "card_id": card_id,
                "task_title": task_title,
                "retry_attempt": retry_attempt,
                "critical_issues": feedback['total_critical_issues'],
                "high_issues": feedback['total_high_issues']
            }
        )
