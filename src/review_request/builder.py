#!/usr/bin/env python3
"""
WHY: Provide fluent Builder pattern interface for constructing code review requests
RESPONSIBILITY: Step-by-step construction of review requests with validation
PATTERNS: Builder (fluent interface), Method Chaining, Facade (simplified API)

The ReviewRequestBuilder provides:
- Fluent method chaining (builder.set_x().set_y().build())
- Validation before building
- Default focus areas (security, GDPR, accessibility)
- Immutable result (LLMMessage list)
- Easy reset for reuse
"""

from dataclasses import dataclass, field
from typing import List, Optional
from llm_client import LLMMessage
from review_request.models import ImplementationFile
from review_request.validator import ReviewRequestValidator
from review_request.message_formatter import ReviewMessageFormatter


@dataclass
class ReviewRequestBuilder:
    """
    Builder for constructing code review requests

    Uses Builder pattern for step-by-step construction of complex review requests.

    Example:
        builder = ReviewRequestBuilder()
        messages = (builder
            .set_developer("developer-a")
            .set_task("Implement auth", "Add JWT authentication")
            .add_file("auth.py", "code here", 50)
            .set_review_prompt(prompt)
            .build())
    """

    # Mutable state during building (reset after build)
    _developer_name: Optional[str] = None
    _task_title: Optional[str] = None
    _task_description: Optional[str] = None
    _implementation_files: List[ImplementationFile] = field(default_factory=list)
    _review_prompt: Optional[str] = None
    _review_focus_areas: List[str] = field(default_factory=lambda: [
        "Code Quality - Anti-patterns, optimization opportunities",
        "Security - OWASP Top 10 vulnerabilities, secure coding practices",
        "GDPR Compliance - Data privacy, consent, user rights",
        "Accessibility - WCAG 2.1 AA standards"
    ])

    def __post_init__(self):
        """Initialize validator and formatter"""
        self._validator = ReviewRequestValidator()
        self._formatter = ReviewMessageFormatter()

    def set_developer(self, developer_name: str) -> 'ReviewRequestBuilder':
        """
        Set the developer name

        Args:
            developer_name: Name of the developer (e.g., "developer-a")

        Returns:
            Self for method chaining

        Raises:
            ValueError: If developer name is empty
        """
        self._validator.validate_developer_name(developer_name)
        self._developer_name = developer_name
        return self

    def set_task(self, title: str, description: str) -> 'ReviewRequestBuilder':
        """
        Set the task details

        Args:
            title: Task title
            description: Task description

        Returns:
            Self for method chaining

        Raises:
            ValueError: If title or description is empty
        """
        self._validator.validate_task(title, description)
        self._task_title = title
        self._task_description = description
        return self

    def add_file(self, path: str, content: str, lines: Optional[int] = None) -> 'ReviewRequestBuilder':
        """
        Add an implementation file

        Args:
            path: File path (relative)
            content: File content
            lines: Number of lines (auto-calculated if None)

        Returns:
            Self for method chaining
        """
        # Guard clause - auto-calculate lines if not provided
        if lines is None:
            lines = len(content.split('\n'))

        impl_file = ImplementationFile(path=path, content=content, lines=lines)
        self._implementation_files.append(impl_file)
        return self

    def add_file_object(self, impl_file: ImplementationFile) -> 'ReviewRequestBuilder':
        """
        Add an ImplementationFile object

        Args:
            impl_file: ImplementationFile instance

        Returns:
            Self for method chaining
        """
        self._implementation_files.append(impl_file)
        return self

    def add_files(self, files: List[ImplementationFile]) -> 'ReviewRequestBuilder':
        """
        Add multiple implementation files

        Args:
            files: List of ImplementationFile instances

        Returns:
            Self for method chaining
        """
        self._implementation_files.extend(files)
        return self

    def set_review_prompt(self, prompt: str) -> 'ReviewRequestBuilder':
        """
        Set the system prompt for code review

        Args:
            prompt: System prompt text

        Returns:
            Self for method chaining

        Raises:
            ValueError: If prompt is empty
        """
        self._validator.validate_review_prompt(prompt)
        self._review_prompt = prompt
        return self

    def set_focus_areas(self, focus_areas: List[str]) -> 'ReviewRequestBuilder':
        """
        Set custom review focus areas

        Args:
            focus_areas: List of focus area descriptions

        Returns:
            Self for method chaining

        Raises:
            ValueError: If focus areas is empty
        """
        self._validator.validate_focus_areas(focus_areas)
        self._review_focus_areas = focus_areas
        return self

    def add_focus_area(self, focus_area: str) -> 'ReviewRequestBuilder':
        """
        Add a single focus area

        Args:
            focus_area: Focus area description

        Returns:
            Self for method chaining
        """
        self._review_focus_areas.append(focus_area)
        return self

    def validate(self) -> bool:
        """
        Validate that all required fields are set

        Returns:
            True if valid

        Raises:
            CodeReviewExecutionError: If validation fails
        """
        return self._validator.validate_request(
            developer_name=self._developer_name,
            task_title=self._task_title,
            task_description=self._task_description,
            implementation_files=self._implementation_files,
            review_prompt=self._review_prompt
        )

    def build(self) -> List[LLMMessage]:
        """
        Build the review request messages

        Returns:
            List of LLMMessage instances (system + user prompts)

        Raises:
            CodeReviewExecutionError: If validation fails
        """
        # Validate before building
        self.validate()

        # Format messages
        return self._formatter.format_messages(
            developer_name=self._developer_name,
            task_title=self._task_title,
            task_description=self._task_description,
            implementation_files=self._implementation_files,
            review_prompt=self._review_prompt,
            focus_areas=self._review_focus_areas
        )

    def get_file_count(self) -> int:
        """Get the number of files added"""
        return len(self._implementation_files)

    def get_total_lines(self) -> int:
        """Get total lines across all files"""
        return sum(file.lines for file in self._implementation_files)

    def get_files(self) -> List[ImplementationFile]:
        """Get the list of implementation files (copy to prevent mutation)"""
        return self._implementation_files.copy()

    def reset(self) -> 'ReviewRequestBuilder':
        """
        Reset the builder to initial state

        Returns:
            Self for method chaining
        """
        self._developer_name = None
        self._task_title = None
        self._task_description = None
        self._implementation_files = []
        self._review_prompt = None
        self._review_focus_areas = [
            "Code Quality - Anti-patterns, optimization opportunities",
            "Security - OWASP Top 10 vulnerabilities, secure coding practices",
            "GDPR Compliance - Data privacy, consent, user rights",
            "Accessibility - WCAG 2.1 AA standards"
        ]
        return self
