#!/usr/bin/env python3
"""
WHY: Validate code review request data before building messages
RESPONSIBILITY: Check required fields and accumulate validation errors
PATTERNS: Validator Pattern, Guard Clauses (early validation)

Validation ensures:
- All required fields are present
- Developer name is not empty
- Task title and description are provided
- At least one implementation file exists
- Review prompt is set
"""

from typing import List, Optional
from artemis_exceptions import CodeReviewExecutionError
from review_request.models import ImplementationFile


class ReviewRequestValidator:
    """
    Validates review request data

    Accumulates all validation errors before raising exception.
    """

    def validate_request(
        self,
        developer_name: Optional[str],
        task_title: Optional[str],
        task_description: Optional[str],
        implementation_files: List[ImplementationFile],
        review_prompt: Optional[str]
    ) -> bool:
        """
        Validate all required fields for review request

        Args:
            developer_name: Name of the developer
            task_title: Task title
            task_description: Task description
            implementation_files: List of implementation files
            review_prompt: System prompt for review

        Returns:
            True if valid

        Raises:
            CodeReviewExecutionError: If validation fails
        """
        errors = []

        # Validate developer name
        if not developer_name:
            errors.append("Developer name is required")

        # Validate task title
        if not task_title:
            errors.append("Task title is required")

        # Validate task description
        if not task_description:
            errors.append("Task description is required")

        # Validate implementation files
        if not implementation_files:
            errors.append("At least one implementation file is required")

        # Validate review prompt
        if not review_prompt:
            errors.append("Review prompt is required")

        # Guard clause - raise if errors found
        if errors:
            raise CodeReviewExecutionError(
                "Review request validation failed",
                context={
                    "errors": errors,
                    "developer_name": developer_name,
                    "files_count": len(implementation_files)
                }
            )

        return True

    def validate_developer_name(self, developer_name: str) -> None:
        """
        Validate developer name

        Args:
            developer_name: Name of the developer

        Raises:
            ValueError: If developer name is empty
        """
        # Guard clause - check if empty
        if not developer_name or not developer_name.strip():
            raise ValueError("Developer name cannot be empty")

    def validate_task(self, title: str, description: str) -> None:
        """
        Validate task details

        Args:
            title: Task title
            description: Task description

        Raises:
            ValueError: If title or description is empty
        """
        # Guard clause - validate title
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")

        # Guard clause - validate description
        if not description or not description.strip():
            raise ValueError("Task description cannot be empty")

    def validate_review_prompt(self, prompt: str) -> None:
        """
        Validate review prompt

        Args:
            prompt: System prompt text

        Raises:
            ValueError: If prompt is empty
        """
        # Guard clause - check if empty
        if not prompt or not prompt.strip():
            raise ValueError("Review prompt cannot be empty")

    def validate_focus_areas(self, focus_areas: List[str]) -> None:
        """
        Validate focus areas

        Args:
            focus_areas: List of focus area descriptions

        Raises:
            ValueError: If focus areas is empty
        """
        # Guard clause - check if empty
        if not focus_areas:
            raise ValueError("Focus areas cannot be empty")
