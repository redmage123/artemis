#!/usr/bin/env python3
"""
WHY: Parse and Extract JSON from LLM Code Review Responses
RESPONSIBILITY: Handle various response formats (markdown, code blocks, raw JSON)
PATTERNS: Guard clauses, early returns, single responsibility
"""

import json
import re
import logging
from typing import Dict, Any, Optional

from artemis_exceptions import LLMResponseParsingError, wrap_exception
from code_review.schema_normalizer import normalize_review_schema


def parse_review_response(
    response_content: str,
    developer_name: str,
    logger: Optional[logging.Logger] = None
) -> Dict[str, Any]:
    """
    Parse the LLM's review response (JSON format).

    WHY: LLM responses can have markdown, code blocks, or raw JSON.
    RESPONSIBILITY: Extract and parse JSON, normalize schema.
    PATTERN: Guard clauses with early error handling.

    Args:
        response_content: Raw response content from LLM
        developer_name: Name of developer (for error context)
        logger: Optional logger for info messages

    Returns:
        Parsed and normalized review data dictionary

    Raises:
        LLMResponseParsingError: If parsing fails
    """
    try:
        # Extract JSON from response content
        content = extract_json_from_response(response_content)

        # Parse JSON
        review_data = json.loads(content)

        # Normalize the schema - convert category-based format to expected format
        # The LLM might return different schemas depending on the prompt version
        if 'review_summary' not in review_data:
            review_data = normalize_review_schema(review_data)

        if logger:
            logger.info("✅ Review response parsed successfully")
            log_review_summary(review_data, logger)

        return review_data

    except json.JSONDecodeError as e:
        raise wrap_exception(
            e,
            LLMResponseParsingError,
            "Failed to parse LLM review response as JSON",
            {
                "developer_name": developer_name,
                "response_preview": response_content[:200]
            }
        )
    except Exception as e:
        raise wrap_exception(
            e,
            LLMResponseParsingError,
            "Failed to process LLM review response",
            {"developer_name": developer_name}
        )


def extract_json_from_response(response_content: str) -> str:
    """
    Extract JSON from response content, handling markdown code blocks.

    WHY: Extracted to avoid nested if in parse_review_response.
    RESPONSIBILITY: Handle various JSON wrapping formats.
    PATTERN: Early returns on matches.

    Args:
        response_content: Raw response content from LLM

    Returns:
        Extracted JSON string
    """
    content = response_content.strip()

    # Try to extract JSON from ```json code block
    json_match = re.search(r'```json\s*\n(.*?)\n```', content, re.DOTALL)
    if json_match:
        return json_match.group(1).strip()

    # Try to extract from generic ``` code block
    code_match = re.search(r'```\s*\n(.*?)\n```', content, re.DOTALL)
    if code_match:
        return code_match.group(1).strip()

    # No code blocks found - remove markers if present
    return remove_code_block_markers(content)


def remove_code_block_markers(content: str) -> str:
    """
    Remove code block markers from content.

    WHY: Extracted to avoid nested if in extract_json_from_response.
    RESPONSIBILITY: Strip markdown code block delimiters.
    PATTERN: Simple string manipulation.

    Args:
        content: Content that may have code block markers

    Returns:
        Content with markers removed
    """
    if content.startswith('```json'):
        content = content[7:]
    elif content.startswith('```'):
        content = content[3:]

    if content.endswith('```'):
        content = content[:-3]

    return content.strip()


def log_review_summary(review_data: Dict[str, Any], logger: logging.Logger) -> None:
    """
    Log review summary information.

    WHY: Extracted to avoid nested if in parse_review_response.
    RESPONSIBILITY: Formatted logging of key metrics.
    PATTERN: Guard clause for type validation.

    Args:
        review_data: Parsed review data dictionary
        logger: Logger instance
    """
    summary = review_data.get('review_summary', {})
    if not isinstance(summary, dict):
        return

    logger.info(f"   Total issues: {summary.get('total_issues', 0)}")
    logger.info(f"   Critical: {summary.get('critical_issues', 0)}")
    logger.info(f"   Overall status: {summary.get('overall_status', 'UNKNOWN')}")
