"""
WHY: Code Review Package - Modular Code Review Components
RESPONSIBILITY: Re-export all code review functionality
PATTERNS: Facade pattern for clean API

This package provides comprehensive code review capabilities including:
- Security analysis (OWASP Top 10)
- GDPR compliance checking
- Accessibility (WCAG 2.1) validation
- Code quality assessment
"""

from code_review.agent import CodeReviewAgent
from code_review.strategies import (
    build_base_review_prompt,
    build_review_request_legacy,
    extract_file_types,
    enhance_messages_with_kg_context,
    read_review_prompt,
    try_load_rag_prompt,
    load_prompt_from_file
)
from code_review.response_parser import (
    parse_review_response,
    extract_json_from_response,
    remove_code_block_markers,
    log_review_summary
)
from code_review.report_generator import (
    write_review_report,
    write_review_summary,
    build_header_section,
    build_issues_summary_section,
    build_critical_issues_section,
    build_high_issues_section,
    build_positive_findings_section,
    build_recommendations_section,
    format_critical_issue
)
from code_review.schema_normalizer import (
    normalize_review_schema,
    collect_issues_from_categories,
    process_category_issues,
    calculate_overall_score,
    determine_overall_status
)

__all__ = [
    # Main agent
    'CodeReviewAgent',

    # Strategy functions
    'build_base_review_prompt',
    'build_review_request_legacy',
    'extract_file_types',
    'enhance_messages_with_kg_context',
    'read_review_prompt',
    'try_load_rag_prompt',
    'load_prompt_from_file',

    # Response parsing
    'parse_review_response',
    'extract_json_from_response',
    'remove_code_block_markers',
    'log_review_summary',

    # Report generation
    'write_review_report',
    'write_review_summary',
    'build_header_section',
    'build_issues_summary_section',
    'build_critical_issues_section',
    'build_high_issues_section',
    'build_positive_findings_section',
    'build_recommendations_section',
    'format_critical_issue',

    # Schema normalization
    'normalize_review_schema',
    'collect_issues_from_categories',
    'process_category_issues',
    'calculate_overall_score',
    'determine_overall_status',
]
