#!/usr/bin/env python3
"""
User Story Validator - Story structure validation

WHY: Separate validation logic from generation logic (SRP).
RESPONSIBILITY: Validate user story structure and fields only.
PATTERNS: Strategy pattern for validation rules, guard clauses.

Example:
    validator = UserStoryValidator()
    is_valid = validator.validate_story(story_dict)
"""

from typing import Dict, List, Any, Optional, Callable
from user_story.models import VALID_PRIORITIES, REQUIRED_STORY_FIELDS


# Validation strategies (Strategy pattern: dictionary mapping)
FIELD_TYPE_VALIDATORS = {
    'title': lambda v: isinstance(v, str) and len(v) > 0,
    'description': lambda v: isinstance(v, str) and len(v) > 0,
    'acceptance_criteria': lambda v: isinstance(v, list) and len(v) > 0,
    'points': lambda v: isinstance(v, (int, float)) and 1 <= v <= 8,
    'priority': lambda v: v in VALID_PRIORITIES
}


class UserStoryValidator:
    """
    Validates user story structure and fields.

    WHY: Separate validation concerns from generation logic (SRP).
    RESPONSIBILITY: Story validation only, no generation.
    PATTERNS: Strategy pattern (validation rules), guard clauses.

    Example:
        validator = UserStoryValidator()
        if validator.validate_story(story):
            process(story)
    """

    def __init__(self, logger: Optional[Any] = None):
        """
        Initialize validator.

        Args:
            logger: Optional logger for validation warnings
        """
        self.logger = logger

    def validate_story(self, story: Dict[str, Any]) -> bool:
        """
        Validate user story has required fields and correct types.

        WHY: Ensure story structure matches expected format before processing.
        PERFORMANCE: O(n) where n is number of required fields.
        PATTERN: Guard clauses for early exit on validation failure.

        Args:
            story: User story dictionary

        Returns:
            True if valid, False otherwise
        """
        # Guard clause: check required fields exist
        if not self._validate_required_fields(story):
            return False

        # Guard clause: check field types
        if not self._validate_field_types(story):
            return False

        return True

    def validate_stories(self, stories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate list of stories, filtering out invalid ones.

        WHY: Batch validation with filtering instead of failing entire batch.
        PERFORMANCE: O(n*m) where n=stories, m=fields. Uses comprehension.
        PATTERN: Declarative filtering over imperative loop.

        Args:
            stories: List of user story dictionaries

        Returns:
            List of valid stories only
        """
        # Guard clause: empty list
        if not stories:
            return []

        # Declarative filtering (functional programming)
        validated_stories = [
            story for story in stories
            if self.validate_story(story)
        ]

        # Log filtered stories
        skipped_count = len(stories) - len(validated_stories)
        if skipped_count > 0 and self.logger:
            self.logger.log(
                f"⚠️  Skipped {skipped_count} malformed user stories",
                "WARNING"
            )

        return validated_stories

    def _validate_required_fields(self, story: Dict[str, Any]) -> bool:
        """
        Validate all required fields are present.

        WHY: Ensure story has minimum required data.
        PERFORMANCE: O(n) where n is number of required fields.
        PATTERN: List comprehension for finding missing fields.

        Args:
            story: User story dictionary

        Returns:
            True if all required fields present, False otherwise
        """
        # Declarative: find missing fields using comprehension
        missing_fields = [
            field for field in REQUIRED_STORY_FIELDS
            if field not in story
        ]

        # Guard clause: log missing fields
        if missing_fields:
            if self.logger:
                self.logger.log(
                    f"⚠️  Story missing required fields: {missing_fields}",
                    "WARNING",
                    context={'story_title': story.get('title', 'Unknown')}
                )
            return False

        return True

    def _validate_field_types(self, story: Dict[str, Any]) -> bool:
        """
        Validate field types using strategy pattern.

        WHY: Ensure each field has correct type and format.
        PERFORMANCE: O(n) where n is number of fields to validate.
        PATTERN: Strategy pattern with validator dictionary.

        Args:
            story: User story dictionary

        Returns:
            True if all fields have correct types, False otherwise
        """
        # Strategy pattern: iterate through validators
        for field, validator_func in FIELD_TYPE_VALIDATORS.items():
            # Guard clause: field exists (already checked by _validate_required_fields)
            if field not in story:
                continue

            # Apply validator strategy
            if not validator_func(story[field]):
                if self.logger:
                    self.logger.log(
                        f"⚠️  Invalid type for field '{field}' in story",
                        "WARNING",
                        context={
                            'story_title': story.get('title', 'Unknown'),
                            'field': field,
                            'value': str(story[field])[:50]
                        }
                    )
                return False

        return True

    def get_validation_errors(self, story: Dict[str, Any]) -> List[str]:
        """
        Get detailed validation errors for a story.

        WHY: Provide detailed feedback about validation failures.
        PERFORMANCE: O(n) where n is number of fields.
        PATTERN: Declarative list building with comprehensions.

        Args:
            story: User story dictionary

        Returns:
            List of validation error messages
        """
        errors = []

        # Check missing fields
        missing_fields = [
            field for field in REQUIRED_STORY_FIELDS
            if field not in story
        ]
        if missing_fields:
            errors.append(f"Missing required fields: {', '.join(missing_fields)}")

        # Check field types
        type_errors = [
            f"Invalid {field}: {story.get(field)}"
            for field, validator in FIELD_TYPE_VALIDATORS.items()
            if field in story and not validator(story[field])
        ]
        errors.extend(type_errors)

        return errors


class ValidationResult:
    """
    Result of validation operation.

    WHY: Encapsulate validation result with details.
    PATTERNS: Result object pattern.

    Attributes:
        is_valid: Whether validation passed
        errors: List of validation errors
        warnings: List of validation warnings
    """

    def __init__(
        self,
        is_valid: bool,
        errors: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None
    ):
        """
        Initialize validation result.

        Args:
            is_valid: Whether validation passed
            errors: List of validation errors
            warnings: List of validation warnings
        """
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []

    def __bool__(self) -> bool:
        """
        Allow boolean checks on validation result.

        WHY: Enable idiomatic usage like 'if result:'.
        """
        return self.is_valid

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.

        WHY: Support serialization and logging.

        Returns:
            Dictionary representation
        """
        return {
            'is_valid': self.is_valid,
            'errors': self.errors,
            'warnings': self.warnings
        }
