#!/usr/bin/env python3
"""
WHY: Format code review requests into LLM messages with proper structure
RESPONSIBILITY: Generate system and user prompts with file content and focus areas
PATTERNS: Template Method (message formatting), Formatter Pattern

Message formatting provides:
- Consistent prompt structure
- File content with markdown formatting
- Numbered focus areas
- Context injection (task, developer, files)
"""

from typing import List
from llm_client import LLMMessage
from review_request.models import ImplementationFile


class ReviewMessageFormatter:
    """
    Formats review request data into LLM messages

    Generates structured prompts for code review.
    """

    def format_messages(
        self,
        developer_name: str,
        task_title: str,
        task_description: str,
        implementation_files: List[ImplementationFile],
        review_prompt: str,
        focus_areas: List[str]
    ) -> List[LLMMessage]:
        """
        Format review request into LLM messages

        Args:
            developer_name: Name of the developer
            task_title: Task title
            task_description: Task description
            implementation_files: List of implementation files
            review_prompt: System prompt for review
            focus_areas: List of focus area descriptions

        Returns:
            List of LLMMessage instances (system + user)
        """
        # Format files content
        files_content = self._format_files(implementation_files)

        # Format focus areas
        focus_areas_text = self._format_focus_areas(focus_areas)

        # Build user prompt
        user_prompt = self._build_user_prompt(
            task_title=task_title,
            task_description=task_description,
            developer_name=developer_name,
            files_content=files_content,
            focus_areas_text=focus_areas_text
        )

        # Build messages
        return [
            LLMMessage(role="system", content=review_prompt),
            LLMMessage(role="user", content=user_prompt)
        ]

    def _format_files(self, implementation_files: List[ImplementationFile]) -> str:
        """
        Format implementation files for display

        Args:
            implementation_files: List of implementation files

        Returns:
            Formatted files content
        """
        # Use list comprehension - Pythonic!
        formatted_files = [
            file.format_for_review()
            for file in implementation_files
        ]

        return '\n'.join(formatted_files)

    def _format_focus_areas(self, focus_areas: List[str]) -> str:
        """
        Format focus areas as numbered list

        Args:
            focus_areas: List of focus area descriptions

        Returns:
            Formatted focus areas text
        """
        # Use list comprehension with enumerate - Pythonic!
        formatted_areas = [
            f"{i+1}. **{area}**"
            for i, area in enumerate(focus_areas)
        ]

        return '\n'.join(formatted_areas)

    def _build_user_prompt(
        self,
        task_title: str,
        task_description: str,
        developer_name: str,
        files_content: str,
        focus_areas_text: str
    ) -> str:
        """
        Build user prompt with all components

        Args:
            task_title: Task title
            task_description: Task description
            developer_name: Name of the developer
            files_content: Formatted files content
            focus_areas_text: Formatted focus areas

        Returns:
            Complete user prompt
        """
        return f"""# Code Review Request

## Task Context

**Task Title:** {task_title}

**Task Description:** {task_description}

**Developer:** {developer_name}

## Implementation to Review

{files_content}

## Your Task

Perform a comprehensive code review following the guidelines in your system prompt. Analyze for:

{focus_areas_text}

Return your review as structured JSON exactly matching the format specified in your prompt.

Focus on being thorough, specific, and actionable. Include file paths, line numbers, code snippets, and clear recommendations.
"""
