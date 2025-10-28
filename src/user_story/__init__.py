#!/usr/bin/env python3
"""
User Story Package - Modular user story generation system

WHY: Modular, testable user story generation from ADRs.
RESPONSIBILITY: Package-level exports and public API definition.
PATTERNS: Facade pattern for package API, clear separation of concerns.

Public API:
    - UserStoryGenerator: Main generator class (facade)
    - UserStory: Data model for stories
    - PromptContext: Context for prompt building
    - GenerationConfig: Configuration for generation
    - UserStoryValidator: Story validation
    - UserStoryParser: Response parsing
    - PromptBuilder: Prompt construction

Example:
    from user_story import UserStoryGenerator
    generator = UserStoryGenerator(llm_client, logger, prompt_manager)
    stories = generator.generate_user_stories(adr_content, "001", parent_card)
"""

# Import core generator (main facade)
from user_story.generator import (
    UserStoryGenerator,
    UserStoryGeneratorBuilder
)

# Import models
from user_story.models import (
    UserStory,
    PromptContext,
    GenerationConfig,
    VALID_PRIORITIES,
    REQUIRED_STORY_FIELDS
)

# Import validator
from user_story.validator import (
    UserStoryValidator,
    ValidationResult
)

# Import parser
from user_story.parser import (
    UserStoryParser,
    ParseResult,
    ParsingError
)

# Import prompt builder
from user_story.prompt_builder import (
    PromptBuilder,
    PromptBuilderFactory,
    build_prompts_for_adr
)

# Package metadata
__version__ = "1.0.0"
__author__ = "Artemis Team"

# Public API
__all__ = [
    # Main generator
    'UserStoryGenerator',
    'UserStoryGeneratorBuilder',

    # Models
    'UserStory',
    'PromptContext',
    'GenerationConfig',
    'VALID_PRIORITIES',
    'REQUIRED_STORY_FIELDS',

    # Validator
    'UserStoryValidator',
    'ValidationResult',

    # Parser
    'UserStoryParser',
    'ParseResult',
    'ParsingError',

    # Prompt builder
    'PromptBuilder',
    'PromptBuilderFactory',
    'build_prompts_for_adr',
]
