#!/usr/bin/env python3
"""
User Story Generator - Main generator orchestrating story creation

WHY: Orchestrate user story generation from ADRs using composition.
RESPONSIBILITY: Coordinate prompt building, LLM calls, parsing, validation.
PATTERNS: Facade pattern, composition over inheritance, dependency injection.

Example:
    generator = UserStoryGenerator(llm_client, logger, prompt_manager)
    stories = generator.generate_user_stories(adr_content, adr_number, parent_card)
"""

from typing import Dict, List, Optional, Any
from user_story.models import PromptContext, GenerationConfig
from user_story.prompt_builder import PromptBuilder
from user_story.parser import UserStoryParser
from user_story.validator import UserStoryValidator


try:
    from llm_client import LLMMessage
    LLM_CLIENT_AVAILABLE = True
except ImportError:
    LLM_CLIENT_AVAILABLE = False


class UserStoryGenerator:
    """
    Orchestrates user story generation from ADR content.

    WHY: Facade pattern - provide simple interface to complex subsystem.
    RESPONSIBILITY: Coordinate components, not implement all logic (SRP).
    PATTERNS: Facade, composition, dependency injection.

    Example:
        generator = UserStoryGenerator(llm_client, logger, prompt_manager)
        stories = generator.generate_user_stories(adr_content, "001", parent_card)

    Attributes:
        llm_client: LLM client for generation
        logger: Logger interface
        prompt_builder: Builds prompts for LLM
        parser: Parses LLM responses
        validator: Validates user stories
        config: Generation configuration
    """

    def __init__(
        self,
        llm_client: Optional[Any] = None,
        logger: Optional[Any] = None,
        prompt_manager: Optional[Any] = None,
        config: Optional[GenerationConfig] = None
    ):
        """
        Initialize user story generator with dependencies.

        WHY: Dependency injection for testability and flexibility.
        PATTERN: Dependency injection, composition over inheritance.

        Args:
            llm_client: LLM client for generation
            logger: Logger interface
            prompt_manager: Optional RAG-based prompt manager
            config: Optional generation configuration
        """
        self.llm_client = llm_client
        self.logger = logger

        # Compose with specialized components (composition over inheritance)
        self.prompt_builder = PromptBuilder(prompt_manager, logger)
        self.parser = UserStoryParser(logger)
        self.validator = UserStoryValidator(logger)

        # Configuration with defaults
        self.config = config or GenerationConfig()

        # Validate configuration
        if not self.config.validate():
            if self.logger:
                self.logger.log("⚠️  Invalid generation config, using defaults", "WARNING")
            self.config = GenerationConfig()

    def generate_user_stories(
        self,
        adr_content: str,
        adr_number: str,
        parent_card: Dict
    ) -> List[Dict]:
        """
        Generate user stories from ADR content using LLM.

        WHY: Main entry point for generation, orchestrates all steps.
        PATTERN: Guard clauses for dependencies, composition for logic.
        PERFORMANCE: Depends on LLM API latency and parsing complexity.

        Args:
            adr_content: Full ADR markdown content
            adr_number: ADR number (e.g., "001")
            parent_card: Parent task card (for context)

        Returns:
            List of user story dicts with title, description, acceptance_criteria, points
        """
        if self.logger:
            self.logger.log(
                f"🤖 Generating user stories from ADR-{adr_number}...",
                "INFO",
                context={'adr_number': adr_number}
            )

        # Guard clause: check LLM client availability
        if not self._check_llm_availability():
            return []

        try:
            # Build prompt context (immutable data structure)
            context = PromptContext(
                adr_content=adr_content,
                adr_number=adr_number
            )

            # Generate stories through pipeline
            user_stories = self._generate_stories_pipeline(context)

            if self.logger:
                self.logger.log(
                    f"✅ Generated {len(user_stories)} user stories from ADR-{adr_number}",
                    "INFO",
                    context={'adr_number': adr_number, 'story_count': len(user_stories)}
                )

            return user_stories

        except Exception as e:
            if self.logger:
                self.logger.log(
                    f"❌ Failed to generate user stories: {e}",
                    "ERROR",
                    context={'adr_number': adr_number, 'error': str(e)}
                )
            return []

    def _check_llm_availability(self) -> bool:
        """
        Check if LLM client is available.

        WHY: Guard clause extracted to method for clarity (DRY).
        PATTERN: Guard clause pattern.
        PERFORMANCE: O(1) - simple checks.

        Returns:
            True if LLM available, False otherwise
        """
        # Guard clause: no LLM client
        if not self.llm_client:
            if self.logger:
                self.logger.log(
                    "⚠️  No LLM client available - skipping user story generation",
                    "WARNING"
                )
            return False

        # Guard clause: LLM client module not available
        if not LLM_CLIENT_AVAILABLE:
            if self.logger:
                self.logger.log(
                    "⚠️  LLM client module unavailable",
                    "WARNING"
                )
            return False

        return True

    def _generate_stories_pipeline(self, context: PromptContext) -> List[Dict]:
        """
        Execute generation pipeline: prompt -> LLM -> parse -> validate.

        WHY: Separate pipeline logic from main method (SRP).
        PATTERN: Pipeline pattern, composition.
        PERFORMANCE: O(n) where n is number of stories generated.

        Args:
            context: Prompt context

        Returns:
            List of validated user stories
        """
        # Step 1: Build prompts (delegation to prompt_builder)
        system_message, user_message = self.prompt_builder.build_prompts(context)

        # Step 2: Call LLM (delegation to LLM client)
        response = self._call_llm(system_message, user_message)

        # Step 3: Parse response (delegation to parser)
        stories = self.parser.parse_response(response)

        # Step 4: Validate stories (delegation to validator)
        validated_stories = self.validator.validate_stories(stories)

        return validated_stories

    def _call_llm(self, system_message: str, user_message: str) -> str:
        """
        Call LLM with system and user messages.

        WHY: Encapsulate LLM API interaction (SRP).
        PATTERN: Guard clause for errors.
        PERFORMANCE: Depends on LLM API latency.

        Args:
            system_message: System prompt
            user_message: User prompt

        Returns:
            LLM response content

        Raises:
            Exception: If LLM call fails
        """
        # Build messages (using LLMMessage if available)
        messages = [
            LLMMessage(role="system", content=system_message),
            LLMMessage(role="user", content=user_message)
        ]

        # Call LLM with configuration
        llm_response = self.llm_client.complete(
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )

        return llm_response.content

    def generate_and_validate(
        self,
        adr_content: str,
        adr_number: str,
        parent_card: Dict
    ) -> tuple[List[Dict], List[str]]:
        """
        Generate stories and return validation details.

        WHY: Support use cases that need validation details.
        PATTERN: Tuple return for multiple values.

        Args:
            adr_content: ADR content
            adr_number: ADR number
            parent_card: Parent card

        Returns:
            Tuple of (validated_stories, validation_errors)
        """
        stories = self.generate_user_stories(adr_content, adr_number, parent_card)

        # Collect validation errors
        validation_errors = []
        for story in stories:
            errors = self.validator.get_validation_errors(story)
            validation_errors.extend(errors)

        return stories, validation_errors


class UserStoryGeneratorBuilder:
    """
    Builder for UserStoryGenerator.

    WHY: Provide fluent API for generator construction.
    PATTERNS: Builder pattern for complex object construction.

    Example:
        generator = (UserStoryGeneratorBuilder()
            .with_llm_client(llm_client)
            .with_logger(logger)
            .with_prompt_manager(prompt_manager)
            .with_temperature(0.5)
            .build())
    """

    def __init__(self):
        """Initialize builder with defaults."""
        self._llm_client = None
        self._logger = None
        self._prompt_manager = None
        self._temperature = 0.4
        self._max_tokens = 2000

    def with_llm_client(self, llm_client: Any) -> 'UserStoryGeneratorBuilder':
        """Set LLM client."""
        self._llm_client = llm_client
        return self

    def with_logger(self, logger: Any) -> 'UserStoryGeneratorBuilder':
        """Set logger."""
        self._logger = logger
        return self

    def with_prompt_manager(self, prompt_manager: Any) -> 'UserStoryGeneratorBuilder':
        """Set prompt manager."""
        self._prompt_manager = prompt_manager
        return self

    def with_temperature(self, temperature: float) -> 'UserStoryGeneratorBuilder':
        """Set LLM temperature."""
        self._temperature = temperature
        return self

    def with_max_tokens(self, max_tokens: int) -> 'UserStoryGeneratorBuilder':
        """Set max tokens."""
        self._max_tokens = max_tokens
        return self

    def build(self) -> UserStoryGenerator:
        """
        Build UserStoryGenerator instance.

        WHY: Construct generator with all configured options.
        PATTERN: Builder pattern final method.

        Returns:
            Configured UserStoryGenerator
        """
        config = GenerationConfig(
            temperature=self._temperature,
            max_tokens=self._max_tokens
        )

        return UserStoryGenerator(
            llm_client=self._llm_client,
            logger=self._logger,
            prompt_manager=self._prompt_manager,
            config=config
        )
