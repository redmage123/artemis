#!/usr/bin/env python3
"""
User Story Parser - Parse LLM responses into user stories

WHY: Separate parsing logic from generation orchestration (SRP).
RESPONSIBILITY: Parse and extract user stories from LLM responses only.
PATTERNS: Strategy pattern for parsing methods, guard clauses.

Example:
    parser = UserStoryParser(logger)
    stories = parser.parse_response(llm_response)
"""

import json
import re
from typing import List, Dict, Any, Optional


# Regex patterns (compiled once for performance)
JSON_PATTERN = re.compile(r'\{.*\}', re.DOTALL)
CODE_BLOCK_PATTERN = re.compile(r'```(?:json)?\s*(\{.*?\})\s*```', re.DOTALL)


class ParsingError(Exception):
    """
    Exception raised when parsing fails.

    WHY: Specific exception for parsing errors.
    PATTERNS: Custom exception with context.
    """

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        """
        Initialize parsing error.

        Args:
            message: Error message
            context: Optional context dictionary
        """
        super().__init__(message)
        self.context = context or {}


class UserStoryParser:
    """
    Parses LLM responses to extract user stories.

    WHY: Separate parsing concerns from generation logic (SRP).
    RESPONSIBILITY: Parse LLM responses only, no generation or validation.
    PATTERNS: Strategy pattern (multiple parsing strategies), guard clauses.

    Example:
        parser = UserStoryParser(logger)
        stories = parser.parse_response(llm_response_text)
    """

    def __init__(self, logger: Optional[Any] = None):
        """
        Initialize parser.

        Args:
            logger: Optional logger interface
        """
        self.logger = logger

    def parse_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse LLM response to extract user stories.

        WHY: Main entry point for parsing, tries multiple strategies.
        PATTERN: Guard clauses, strategy pattern for parsing methods.
        PERFORMANCE: O(n) where n is response length for regex matching.

        Args:
            response: LLM response text

        Returns:
            List of user story dictionaries
        """
        # Guard clause: empty response
        if not response or not response.strip():
            if self.logger:
                self.logger.log("⚠️  Empty LLM response", "WARNING")
            return []

        # Try multiple parsing strategies (Strategy pattern)
        parsing_strategies = [
            ('code_block', self._parse_code_block),
            ('json_direct', self._parse_json_direct),
            ('json_search', self._parse_json_search)
        ]

        for strategy_name, strategy_func in parsing_strategies:
            try:
                stories = strategy_func(response)
                if stories:
                    if self.logger:
                        self.logger.log(
                            f"✅ Parsed {len(stories)} stories using {strategy_name}",
                            "DEBUG"
                        )
                    return stories
            except Exception as e:
                if self.logger:
                    self.logger.log(
                        f"⚠️  Strategy {strategy_name} failed: {e}",
                        "DEBUG"
                    )
                continue

        # All strategies failed
        if self.logger:
            self.logger.log("⚠️  LLM response did not contain valid JSON", "WARNING")
        return []

    def _parse_code_block(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse JSON from markdown code block.

        WHY: LLMs often wrap JSON in ```json code blocks.
        PATTERN: Guard clause for regex match.
        PERFORMANCE: O(n) regex search with compiled pattern.

        Args:
            response: LLM response text

        Returns:
            List of user stories

        Raises:
            ParsingError: If no code block found or invalid JSON
        """
        # Guard clause: find code block
        match = CODE_BLOCK_PATTERN.search(response)
        if not match:
            raise ParsingError("No code block found")

        json_text = match.group(1)
        return self._extract_stories_from_json(json_text)

    def _parse_json_direct(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse JSON directly from response.

        WHY: Handle responses that are pure JSON.
        PATTERN: Guard clause for parsing errors.
        PERFORMANCE: O(n) JSON parsing.

        Args:
            response: LLM response text

        Returns:
            List of user stories

        Raises:
            ParsingError: If response is not valid JSON
        """
        try:
            # Try to parse entire response as JSON
            data = json.loads(response.strip())
            return self._extract_stories_from_data(data)
        except json.JSONDecodeError as e:
            raise ParsingError(f"Direct JSON parsing failed: {e}")

    def _parse_json_search(self, response: str) -> List[Dict[str, Any]]:
        """
        Search for JSON in response text.

        WHY: Handle responses with JSON embedded in text.
        PATTERN: Guard clause for regex match.
        PERFORMANCE: O(n) regex search with compiled pattern.

        Args:
            response: LLM response text

        Returns:
            List of user stories

        Raises:
            ParsingError: If no JSON found
        """
        # Guard clause: find JSON pattern
        match = JSON_PATTERN.search(response)
        if not match:
            raise ParsingError("No JSON pattern found")

        json_text = match.group(0)
        return self._extract_stories_from_json(json_text)

    def _extract_stories_from_json(self, json_text: str) -> List[Dict[str, Any]]:
        """
        Extract stories from JSON text.

        WHY: DRY - centralize JSON parsing logic.
        PATTERN: Guard clause for parsing errors.
        PERFORMANCE: O(n) JSON parsing.

        Args:
            json_text: JSON string

        Returns:
            List of user stories

        Raises:
            ParsingError: If JSON is invalid
        """
        try:
            data = json.loads(json_text)
            return self._extract_stories_from_data(data)
        except json.JSONDecodeError as e:
            raise ParsingError(f"Invalid JSON: {e}")

    def _extract_stories_from_data(self, data: Any) -> List[Dict[str, Any]]:
        """
        Extract stories from parsed JSON data.

        WHY: Handle different JSON structures (array vs object).
        PATTERN: Guard clauses for structure validation.
        PERFORMANCE: O(1) for structure checks.

        Args:
            data: Parsed JSON data

        Returns:
            List of user stories

        Raises:
            ParsingError: If data structure is invalid
        """
        # Guard clause: data must be dict or list
        if not isinstance(data, (dict, list)):
            raise ParsingError(f"Expected dict or list, got {type(data)}")

        # Handle direct list of stories
        if isinstance(data, list):
            return data

        # Handle dict with 'user_stories' key
        if 'user_stories' in data:
            stories = data['user_stories']
            if not isinstance(stories, list):
                raise ParsingError("'user_stories' must be a list")
            return stories

        # Handle dict with 'stories' key
        if 'stories' in data:
            stories = data['stories']
            if not isinstance(stories, list):
                raise ParsingError("'stories' must be a list")
            return stories

        # Single story as dict
        if self._looks_like_story(data):
            return [data]

        raise ParsingError("Could not find stories in data structure")

    def _looks_like_story(self, data: Dict[str, Any]) -> bool:
        """
        Check if dictionary looks like a user story.

        WHY: Detect single story objects vs wrapper objects.
        PATTERN: Simple heuristic check.
        PERFORMANCE: O(1) - key existence checks.

        Args:
            data: Dictionary to check

        Returns:
            True if looks like a story, False otherwise
        """
        # Must be a dict
        if not isinstance(data, dict):
            return False

        # Check for common story fields
        story_indicators = ['title', 'description', 'acceptance_criteria']
        return any(key in data for key in story_indicators)


class ParseResult:
    """
    Result of parsing operation.

    WHY: Encapsulate parsing result with metadata.
    PATTERNS: Result object pattern.

    Attributes:
        stories: List of parsed user stories
        success: Whether parsing succeeded
        strategy_used: Which parsing strategy succeeded
        error: Error message if parsing failed
    """

    def __init__(
        self,
        stories: List[Dict[str, Any]],
        success: bool = True,
        strategy_used: Optional[str] = None,
        error: Optional[str] = None
    ):
        """
        Initialize parse result.

        Args:
            stories: Parsed user stories
            success: Whether parsing succeeded
            strategy_used: Which strategy succeeded
            error: Error message if failed
        """
        self.stories = stories
        self.success = success
        self.strategy_used = strategy_used
        self.error = error

    def __bool__(self) -> bool:
        """
        Allow boolean checks on parse result.

        WHY: Enable idiomatic usage like 'if result:'.
        """
        return self.success

    def __len__(self) -> int:
        """
        Return number of stories parsed.

        WHY: Enable len() checks on result.
        """
        return len(self.stories)
