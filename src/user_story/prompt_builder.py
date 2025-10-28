#!/usr/bin/env python3
"""
User Story Prompt Builder - Generate prompts for user story creation

WHY: Separate prompt building logic from generation orchestration (SRP).
RESPONSIBILITY: Build prompts for LLM, handle RAG and defaults.
PATTERNS: Strategy pattern for prompt sources, template method.

Example:
    builder = PromptBuilder(prompt_manager, logger)
    system_msg, user_msg = builder.build_prompts(prompt_context)
"""

from typing import Tuple, Optional, Any
from user_story.models import PromptContext


# Default prompt templates (constants for DRY)
DEFAULT_SYSTEM_MESSAGE = """You are an expert at converting Architecture Decision Records (ADRs) into actionable user stories.
Generate user stories that implement the architectural decisions, following best practices:
- Use "As a [role], I want [feature], so that [benefit]" format
- Include specific acceptance criteria
- Estimate story points (1-8 scale)
- Break down complex decisions into multiple stories"""

DEFAULT_USER_MESSAGE_TEMPLATE = """Convert the following ADR into user stories:

{adr_content}

Generate 2-5 user stories in JSON format:
{{
  "user_stories": [
    {{
      "title": "As a developer, I want to implement X, so that Y",
      "description": "Detailed description of what needs to be built",
      "acceptance_criteria": [
        "Given X, when Y, then Z",
        "Criterion 2"
      ],
      "points": 5,
      "priority": "high"
    }}
  ]
}}

Focus on implementation tasks, not architectural discussions."""


class PromptBuilder:
    """
    Builds prompts for user story generation from ADRs.

    WHY: Separate prompt building from generation orchestration (SRP).
    RESPONSIBILITY: Construct system and user messages only.
    PATTERNS: Strategy pattern (RAG vs default), template method.

    Example:
        builder = PromptBuilder(prompt_manager, logger)
        system, user = builder.build_prompts(context)
    """

    def __init__(
        self,
        prompt_manager: Optional[Any] = None,
        logger: Optional[Any] = None
    ):
        """
        Initialize prompt builder.

        Args:
            prompt_manager: Optional RAG-based prompt manager
            logger: Optional logger interface
        """
        self.prompt_manager = prompt_manager
        self.logger = logger

    def build_prompts(self, context: PromptContext) -> Tuple[str, str]:
        """
        Build system and user messages for user story generation.

        WHY: Main entry point for prompt building, supports RAG and fallback.
        PATTERN: Guard clause for prompt manager, fallback strategy.
        PERFORMANCE: O(1) for default prompts, O(n) for RAG template rendering.

        Args:
            context: Prompt context with ADR content and variables

        Returns:
            Tuple of (system_message, user_message)
        """
        # Guard clause: no prompt manager, use default
        if not self.prompt_manager:
            return self._build_default_prompts(context)

        # Try RAG prompts first, fallback to default
        try:
            return self._build_rag_prompts(context)
        except Exception as e:
            if self.logger:
                self.logger.log(
                    f"⚠️  Error loading RAG prompt: {e} - using default",
                    "WARNING",
                    context={'adr_number': context.adr_number}
                )
            return self._build_default_prompts(context)

    def _build_rag_prompts(self, context: PromptContext) -> Tuple[str, str]:
        """
        Build prompts using RAG-based prompt manager.

        WHY: Support RAG-enhanced prompts for better generation quality.
        PATTERN: Guard clauses for error handling.
        PERFORMANCE: Depends on prompt manager implementation.

        Args:
            context: Prompt context

        Returns:
            Tuple of (system_message, user_message)

        Raises:
            Exception: If RAG prompt loading fails
        """
        if self.logger:
            self.logger.log(
                "📝 Loading architecture prompt from RAG",
                "INFO",
                context={'adr_number': context.adr_number}
            )

        # Get prompt template from RAG
        prompt_template = self.prompt_manager.get_prompt("architecture_design_adr")

        # Guard clause: no template found
        if not prompt_template:
            raise Exception("Prompt not found in RAG")

        # Render template with variables
        rendered = self.prompt_manager.render_prompt(
            prompt=prompt_template,
            variables=context.get_variables_dict()
        )

        if self.logger:
            perspectives_count = len(prompt_template.perspectives)
            self.logger.log(
                f"✅ Loaded RAG prompt with {perspectives_count} perspectives",
                "INFO",
                context={'adr_number': context.adr_number}
            )

        return rendered['system'], rendered['user']

    def _build_default_prompts(self, context: PromptContext) -> Tuple[str, str]:
        """
        Build default prompts without RAG.

        WHY: Fallback when RAG unavailable, ensure system always works.
        PATTERN: Template method pattern for prompt building.
        PERFORMANCE: O(1) - simple string formatting.

        Args:
            context: Prompt context

        Returns:
            Tuple of (system_message, user_message)
        """
        system_message = DEFAULT_SYSTEM_MESSAGE

        # Format user message with ADR content
        user_message = DEFAULT_USER_MESSAGE_TEMPLATE.format(
            adr_content=context.adr_content
        )

        return system_message, user_message


class PromptBuilderFactory:
    """
    Factory for creating prompt builders.

    WHY: Encapsulate prompt builder creation logic (Factory pattern).
    PATTERNS: Factory pattern, strategy pattern.

    Example:
        builder = PromptBuilderFactory.create(prompt_manager, logger)
    """

    @staticmethod
    def create(
        prompt_manager: Optional[Any] = None,
        logger: Optional[Any] = None,
        strategy: str = 'auto'
    ) -> PromptBuilder:
        """
        Create prompt builder with specified strategy.

        WHY: Factory pattern for flexible builder creation.
        PATTERN: Factory method with strategy selection.

        Args:
            prompt_manager: Optional RAG prompt manager
            logger: Optional logger
            strategy: Strategy type ('auto', 'rag', 'default')

        Returns:
            PromptBuilder instance
        """
        # Strategy pattern: determine builder configuration
        if strategy == 'default':
            # Force default prompts (no RAG)
            return PromptBuilder(prompt_manager=None, logger=logger)

        if strategy == 'rag':
            # Force RAG (will fail if unavailable)
            if not prompt_manager:
                raise ValueError("RAG strategy requires prompt_manager")
            return PromptBuilder(prompt_manager=prompt_manager, logger=logger)

        # Auto strategy: use RAG if available
        return PromptBuilder(prompt_manager=prompt_manager, logger=logger)


def build_prompts_for_adr(
    adr_content: str,
    adr_number: str,
    prompt_manager: Optional[Any] = None,
    logger: Optional[Any] = None
) -> Tuple[str, str]:
    """
    Convenience function to build prompts for an ADR.

    WHY: Simplified API for common use case.
    PATTERN: Facade pattern for simplified interface.

    Args:
        adr_content: ADR content to convert
        adr_number: ADR number
        prompt_manager: Optional RAG prompt manager
        logger: Optional logger

    Returns:
        Tuple of (system_message, user_message)
    """
    context = PromptContext(
        adr_content=adr_content,
        adr_number=adr_number
    )

    builder = PromptBuilder(prompt_manager=prompt_manager, logger=logger)
    return builder.build_prompts(context)
