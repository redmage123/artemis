"""
WHY: Provide fluent builder pattern for constructing prompts.
RESPONSIBILITY: Enable step-by-step prompt construction with validation.
PATTERNS: Builder pattern, method chaining, guard clauses.

This module implements a fluent builder interface for creating
complex prompts with validation at each step.
"""

from typing import Dict, List, Optional, Any
from .models import PromptTemplate, PromptContext, RenderedPrompt, ReasoningStrategyType
from .variable_substitutor import VariableSubstitutor
from .formatter import PromptFormatter


class PromptBuilder:
    """
    WHY: Build prompts using fluent interface.
    RESPONSIBILITY: Coordinate prompt construction steps.
    PATTERNS: Builder pattern, method chaining, validation.
    """

    def __init__(
        self,
        template: PromptTemplate,
        verbose: bool = False
    ):
        """
        WHY: Initialize builder with template.
        RESPONSIBILITY: Set up builder state.
        PATTERNS: Builder initialization.

        Args:
            template: Base prompt template
            verbose: Enable verbose logging
        """
        self._template = template
        self._variables: Dict[str, Any] = {}
        self._override_reasoning: Optional[ReasoningStrategyType] = None
        self._override_config: Optional[Dict[str, Any]] = None
        self._verbose = verbose

        # Initialize helper components
        self._substitutor = VariableSubstitutor(strict=False, verbose=verbose)
        self._formatter = PromptFormatter(verbose=verbose)

    def with_variables(self, variables: Dict[str, Any]) -> 'PromptBuilder':
        """
        WHY: Set variables for template substitution.
        RESPONSIBILITY: Store variables for later use.
        PATTERNS: Method chaining, fluent interface.

        Args:
            variables: Template variables

        Returns:
            Self for method chaining
        """
        # Guard clause: Skip if empty
        if not variables:
            return self

        self._variables.update(variables)
        return self

    def with_variable(self, key: str, value: Any) -> 'PromptBuilder':
        """
        WHY: Set a single variable.
        RESPONSIBILITY: Add one variable to collection.
        PATTERNS: Method chaining, convenience method.

        Args:
            key: Variable name
            value: Variable value

        Returns:
            Self for method chaining
        """
        self._variables[key] = value
        return self

    def with_reasoning(
        self,
        strategy: ReasoningStrategyType,
        config: Optional[Dict[str, Any]] = None
    ) -> 'PromptBuilder':
        """
        WHY: Override reasoning strategy for this render.
        RESPONSIBILITY: Set reasoning strategy override.
        PATTERNS: Method chaining, optional override.

        Args:
            strategy: Reasoning strategy to use
            config: Strategy-specific configuration

        Returns:
            Self for method chaining
        """
        self._override_reasoning = strategy
        self._override_config = config or {}
        return self

    def build(self) -> RenderedPrompt:
        """
        WHY: Build final rendered prompt.
        RESPONSIBILITY: Coordinate substitution and formatting.
        PATTERNS: Template method pattern, validation.

        Returns:
            RenderedPrompt with system and user messages

        Raises:
            ValueError: If required variables missing
        """
        # Validate variables
        validation = self._substitutor.validate_variables(
            self._template.user_template,
            self._variables
        )

        # Guard clause: Raise if missing required variables
        if not validation["valid"]:
            missing = validation["missing"]
            raise ValueError(f"Missing required variables: {missing}")

        # Determine effective reasoning strategy
        effective_strategy = (
            self._override_reasoning
            if self._override_reasoning
            else self._template.reasoning_strategy
        )

        # Determine effective config
        effective_config = (
            self._override_config
            if self._override_config
            else (self._template.reasoning_config or {})
        )

        # Create temporary template with effective reasoning
        effective_template = self._create_effective_template(
            effective_strategy,
            effective_config
        )

        # Format system message
        system_message = self._formatter.format_system_message(effective_template)

        # Substitute variables in user template
        base_user_message = self._substitutor.substitute(
            self._template.user_template,
            self._variables
        )

        # Format complete user message
        user_message = self._formatter.format_user_message(
            effective_template,
            base_user_message
        )

        return RenderedPrompt(
            system=system_message,
            user=user_message,
            template_name=self._template.name,
            template_version=self._template.version,
            variables_used=self._variables.copy(),
            reasoning_strategy=effective_strategy
        )

    def validate(self) -> Dict[str, Any]:
        """
        WHY: Validate builder state without building.
        RESPONSIBILITY: Check if build will succeed.
        PATTERNS: Pre-validation, guard clause pattern.

        Returns:
            Validation result dictionary
        """
        return self._substitutor.validate_variables(
            self._template.user_template,
            self._variables
        )

    def _create_effective_template(
        self,
        strategy: ReasoningStrategyType,
        config: Dict[str, Any]
    ) -> PromptTemplate:
        """
        WHY: Create template with effective reasoning settings.
        RESPONSIBILITY: Merge override with base template.
        PATTERNS: Template copying with overrides.

        Args:
            strategy: Effective reasoning strategy
            config: Effective reasoning config

        Returns:
            Modified template copy
        """
        # Create shallow copy with reasoning overrides
        from dataclasses import replace

        return replace(
            self._template,
            reasoning_strategy=strategy,
            reasoning_config=config
        )


class PromptBuilderFactory:
    """
    WHY: Create PromptBuilder instances from templates.
    RESPONSIBILITY: Factory for builder creation.
    PATTERNS: Factory pattern, dependency injection.
    """

    def __init__(self, verbose: bool = False):
        """
        WHY: Initialize factory with configuration.
        RESPONSIBILITY: Set up factory state.
        PATTERNS: Configuration injection.

        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose

    def create_builder(self, template: PromptTemplate) -> PromptBuilder:
        """
        WHY: Create a new PromptBuilder for template.
        RESPONSIBILITY: Instantiate builder with dependencies.
        PATTERNS: Factory method.

        Args:
            template: Template to build from

        Returns:
            Configured PromptBuilder
        """
        return PromptBuilder(template, verbose=self.verbose)

    def create_with_context(
        self,
        template: PromptTemplate,
        context: PromptContext
    ) -> PromptBuilder:
        """
        WHY: Create builder pre-configured with context.
        RESPONSIBILITY: Instantiate builder with context applied.
        PATTERNS: Factory method with configuration.

        Args:
            template: Template to build from
            context: Context to apply

        Returns:
            Configured PromptBuilder
        """
        builder = self.create_builder(template)

        # Apply context variables
        builder.with_variables(context.get_all_variables())

        # Apply reasoning override if present
        if context.override_reasoning:
            builder.with_reasoning(context.override_reasoning)

        return builder
