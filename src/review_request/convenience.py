#!/usr/bin/env python3
"""
WHY: Provide convenience functions for common review request operations
RESPONSIBILITY: One-call functions for creating review requests without builder setup
PATTERNS: Facade (simplified interface), Convenience Factory

Convenience functions simplify:
- Single-call review request creation
- Default configuration application
- Common use case patterns
"""

from typing import List
from llm_client import LLMMessage
from review_request.builder import ReviewRequestBuilder
from review_request.file_reader import read_implementation_files


def create_review_request(
    developer_name: str,
    task_title: str,
    task_description: str,
    implementation_dir: str,
    review_prompt: str
) -> List[LLMMessage]:
    """
    Convenience function to create a review request in one call

    Args:
        developer_name: Name of the developer
        task_title: Task title
        task_description: Task description
        implementation_dir: Directory with implementation files
        review_prompt: System prompt for review

    Returns:
        List of LLMMessage instances

    Example:
        messages = create_review_request(
            developer_name="developer-a",
            task_title="Implement authentication",
            task_description="Add JWT-based authentication",
            implementation_dir="/tmp/developer-a",
            review_prompt=prompt_text
        )
    """
    # Read files from directory
    files = read_implementation_files(implementation_dir)

    # Build request using fluent interface
    builder = ReviewRequestBuilder()
    messages = (builder
        .set_developer(developer_name)
        .set_task(task_title, task_description)
        .add_files(files)
        .set_review_prompt(review_prompt)
        .build())

    return messages
