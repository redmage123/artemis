#!/usr/bin/env python3
"""
WHY: Provide public API for building code review requests using Builder pattern
RESPONSIBILITY: Export main classes and convenience functions for external use
PATTERNS: Facade (simplified API), Builder (request construction)

This package provides a fluent interface for constructing complex code review
requests with validation, file handling, and message formatting.

Example:
    from review_request import ReviewRequestBuilder, create_review_request

    # Method 1: Using builder
    builder = ReviewRequestBuilder()
    messages = (builder
        .set_developer("developer-a")
        .set_task("Implement auth", "Add JWT authentication")
        .add_file("auth.py", "code here", 50)
        .set_review_prompt(prompt)
        .build())

    # Method 2: Convenience function
    messages = create_review_request(
        developer_name="developer-a",
        task_title="Implement auth",
        task_description="Add JWT authentication",
        implementation_dir="/tmp/developer-a",
        review_prompt=prompt_text
    )
"""

from review_request.models import ImplementationFile
from review_request.builder import ReviewRequestBuilder
from review_request.file_reader import read_implementation_files
from review_request.convenience import create_review_request

__all__ = [
    'ImplementationFile',
    'ReviewRequestBuilder',
    'read_implementation_files',
    'create_review_request'
]
