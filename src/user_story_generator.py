#!/usr/bin/env python3
"""
UserStoryGenerator (Backward Compatibility Wrapper)

WHY: Maintain backward compatibility while using refactored modular package.
RESPONSIBILITY: Re-export UserStoryGenerator from user_story package.
PATTERNS: Facade pattern, backward compatibility wrapper.

REFACTORING NOTICE:
This module has been refactored into a modular package: user_story/
- user_story/models.py: Data models and structures (160 lines)
- user_story/validator.py: Story validation logic (238 lines)
- user_story/prompt_builder.py: Prompt building and RAG integration (207 lines)
- user_story/parser.py: LLM response parsing (258 lines)
- user_story/generator.py: Main generator orchestration (250 lines)
- user_story/__init__.py: Package exports (73 lines)

Total: 1,186 lines (modular) vs 229 lines (original)
Wrapper: 40 lines (82.5% reduction from original)

All original functionality is preserved. Import from user_story package for
direct access to modular components.

Example (backward compatible):
    from user_story_generator import UserStoryGenerator
    generator = UserStoryGenerator(llm_client, logger, prompt_manager)
    stories = generator.generate_user_stories(adr_content, "001", parent_card)

Example (new modular usage):
    from user_story import UserStoryGenerator, UserStoryValidator
    generator = UserStoryGenerator(llm_client, logger)
    validator = UserStoryValidator(logger)
"""

# Re-export from refactored package (backward compatibility)
from user_story import (
    UserStoryGenerator,
    UserStoryGeneratorBuilder,
    UserStory,
    PromptContext,
    GenerationConfig
)

# Maintain identical public API
__all__ = [
    'UserStoryGenerator',
    'UserStoryGeneratorBuilder',
    'UserStory',
    'PromptContext',
    'GenerationConfig'
]
