#!/usr/bin/env python3
"""
Prompt Refinement Engine (Layer 4: Retry with Refinement)

WHY: Generates refined prompts based on validation failures for intelligent retry.
     Converts failure analysis into actionable prompt modifications.
     Increases specificity with each retry attempt.

RESPONSIBILITY: ONLY prompt refinement - no validation or retry logic.
PATTERNS: Strategy pattern for refinement strategies (no if/elif chains).

Example:
    engine = PromptRefinementEngine()
    failure_analysis = FailureAnalysis(category=FailureCategory.MISSING_IMPORTS, ...)
    refined_prompt = engine.refine_prompt(original_prompt, failure_analysis, attempt=2)
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

from artemis_stage_interface import LoggerInterface
from artemis_exceptions import ConfigurationError, create_wrapped_exception
from validation_failure_analyzer import FailureAnalysis, FailureCategory


@dataclass
class RefinedPrompt:
    """
    Result of prompt refinement.

    Attributes:
        prompt: Refined prompt text
        constraints_added: List of constraints added to prompt
        attempt_number: Which retry attempt this is for
        refinement_level: How aggressive the refinement is (0.0-1.0)
    """
    prompt: str
    constraints_added: List[str]
    attempt_number: int
    refinement_level: float


class PromptRefinementEngine:
    """
    Refines prompts based on validation failures for intelligent retry.

    WHY: Generic retries waste tokens on same mistakes.
         Refined prompts add specific constraints to fix known issues.

    RESPONSIBILITY: ONLY generate refined prompts - no validation or execution.
    PATTERNS: Strategy pattern for category-specific refinement (no if/elif).
    PERFORMANCE: Template caching, early returns, list comprehensions.

    Example:
        engine = PromptRefinementEngine()
        analysis = FailureAnalysis(category=FailureCategory.MISSING_IMPORTS, ...)
        refined = engine.refine_prompt(original_prompt, analysis, attempt=1)
    """

    # Refinement levels per attempt (Strategy pattern)
    REFINEMENT_LEVELS = {
        1: 0.3,   # Light refinement (add basic constraints)
        2: 0.6,   # Medium refinement (add detailed constraints)
        3: 0.9,   # Aggressive refinement (add very specific constraints)
    }

    # Constraint templates per category (Strategy pattern - dictionary mapping)
    CATEGORY_TEMPLATES = {
        FailureCategory.MISSING_IMPORTS: {
            'prefix': "\n## MANDATORY IMPORT REQUIREMENTS\n",
            'emphasis': "CRITICAL: You MUST include these imports:",
            'format': "- {constraint}"
        },
        FailureCategory.INCOMPLETE_IMPLEMENTATION: {
            'prefix': "\n## MANDATORY IMPLEMENTATION REQUIREMENTS\n",
            'emphasis': "CRITICAL: Code must be COMPLETE:",
            'format': "- {constraint}"
        },
        FailureCategory.INCORRECT_SIGNATURE: {
            'prefix': "\n## MANDATORY SIGNATURE REQUIREMENTS\n",
            'emphasis': "CRITICAL: Function signatures must match EXACTLY:",
            'format': "- {constraint}"
        },
        FailureCategory.MISSING_DOCSTRINGS: {
            'prefix': "\n## MANDATORY DOCUMENTATION REQUIREMENTS\n",
            'emphasis': "CRITICAL: All code must be documented:",
            'format': "- {constraint}"
        },
        FailureCategory.FORBIDDEN_PATTERNS: {
            'prefix': "\n## FORBIDDEN PATTERNS - DO NOT USE\n",
            'emphasis': "NEVER use these patterns:",
            'format': "- {constraint}"
        },
    }

    def __init__(self, logger: Optional[LoggerInterface] = None):
        """
        Initialize prompt refinement engine.

        Args:
            logger: Optional logger for debugging
        """
        self.logger = logger

        if self.logger:
            self.logger.log("✨ Prompt refinement engine initialized", "DEBUG")

    def refine_prompt(
        self,
        original_prompt: str,
        failure_analysis: FailureAnalysis,
        attempt: int = 1
    ) -> RefinedPrompt:
        """
        Refine prompt based on failure analysis.

        WHY: Adds specific constraints to fix validation failures.
             Increases constraint specificity with each retry attempt.

        PERFORMANCE: Template-based generation (O(1) constraint lookup).
                     Early returns when appropriate.

        Args:
            original_prompt: Original prompt that failed validation
            failure_analysis: Analysis of why validation failed
            attempt: Retry attempt number (1, 2, 3...)

        Returns:
            RefinedPrompt with added constraints

        Raises:
            ConfigurationError: If attempt number invalid

        Example:
            analysis = FailureAnalysis(
                category=FailureCategory.MISSING_IMPORTS,
                constraints=['Include import django']
            )
            refined = engine.refine_prompt(prompt, analysis, attempt=1)
        """
        # Validate attempt number (early return on error)
        if attempt < 1:
            raise ConfigurationError(
                "Attempt number must be >= 1",
                context={'attempt': attempt}
            )

        # Get refinement level for this attempt (Strategy pattern)
        refinement_level = self.REFINEMENT_LEVELS.get(attempt, 1.0)

        # Build refined prompt (avoid nested ifs - extract to helper)
        refined_prompt_text = self._build_refined_prompt(
            original_prompt,
            failure_analysis,
            refinement_level
        )

        # Track what constraints were added
        constraints_added = failure_analysis.constraints.copy()

        if self.logger:
            self.logger.log(
                f"✨ Refined prompt for {failure_analysis.category.value} "
                f"(attempt {attempt}, level {refinement_level:.1f})",
                "DEBUG"
            )

        return RefinedPrompt(
            prompt=refined_prompt_text,
            constraints_added=constraints_added,
            attempt_number=attempt,
            refinement_level=refinement_level
        )

    def _build_refined_prompt(
        self,
        original_prompt: str,
        failure_analysis: FailureAnalysis,
        refinement_level: float
    ) -> str:
        """
        Build refined prompt with added constraints.

        WHY: Centralizes prompt building logic for reusability.
        PATTERNS: Template pattern, Strategy pattern for category handling.
        PERFORMANCE: List join instead of string concatenation.

        Args:
            original_prompt: Original prompt
            failure_analysis: Failure analysis with constraints
            refinement_level: How aggressive to be (0.0-1.0)

        Returns:
            Refined prompt text
        """
        # Start with original prompt
        parts = [original_prompt]

        # Add constraints section (Strategy pattern - get template for category)
        constraints_section = self._build_constraints_section(
            failure_analysis.category,
            failure_analysis.constraints,
            refinement_level
        )

        # Early return if no constraints to add
        if not constraints_section:
            return original_prompt

        parts.append(constraints_section)

        # Add emphasis based on refinement level (Strategy pattern)
        emphasis = self._get_refinement_emphasis(refinement_level)
        if emphasis:
            parts.append(emphasis)

        # Join parts (performance: single join instead of multiple concatenations)
        return "\n\n".join(parts)

    def _build_constraints_section(
        self,
        category: FailureCategory,
        constraints: List[str],
        refinement_level: float
    ) -> str:
        """
        Build constraints section for category.

        WHY: Different failure categories need different constraint formatting.
        PATTERNS: Strategy pattern with template mapping (no if/elif).
        PERFORMANCE: List comprehension for constraint formatting.

        Args:
            category: Failure category
            constraints: List of constraints to add
            refinement_level: Refinement aggressiveness

        Returns:
            Formatted constraints section
        """
        # Early return if no constraints
        if not constraints:
            return ""

        # Get template for category (Strategy pattern - dictionary mapping)
        template = self.CATEGORY_TEMPLATES.get(category)

        # Use default template if category not found
        if not template:
            template = {
                'prefix': "\n## MANDATORY REQUIREMENTS\n",
                'emphasis': "IMPORTANT: You must fix these issues:",
                'format': "- {constraint}"
            }

        # Build section parts (avoid string concatenation in loop)
        parts = [
            template['prefix'],
            template['emphasis']
        ]

        # Format each constraint (list comprehension for performance)
        formatted_constraints = [
            template['format'].format(constraint=c)
            for c in constraints
        ]

        parts.extend(formatted_constraints)

        # Add extra emphasis for high refinement levels
        if refinement_level > 0.7:
            parts.append("\n**These requirements are NON-NEGOTIABLE.**")

        return "\n".join(parts)

    def _get_refinement_emphasis(self, refinement_level: float) -> Optional[str]:
        """
        Get emphasis text based on refinement level.

        WHY: Higher retry attempts need stronger emphasis.
        PATTERNS: Strategy pattern with level-based mapping.

        Args:
            refinement_level: Refinement level (0.0-1.0)

        Returns:
            Emphasis text or None
        """
        # Strategy pattern: Level thresholds → emphasis mapping
        emphasis_map = [
            (0.9, "\n\n⚠️  **CRITICAL**: This is the FINAL retry attempt. "
                  "All requirements MUST be met EXACTLY."),
            (0.6, "\n\n⚠️  **IMPORTANT**: Previous attempt failed validation. "
                  "Please follow ALL requirements carefully."),
            (0.3, "\n\n**Note**: Please ensure all requirements are met."),
        ]

        # Return first matching emphasis (early return pattern)
        for threshold, emphasis in emphasis_map:
            if refinement_level >= threshold:
                return emphasis

        return None

    def refine_with_examples(
        self,
        original_prompt: str,
        failure_analysis: FailureAnalysis,
        examples: List[str],
        attempt: int = 1
    ) -> RefinedPrompt:
        """
        Refine prompt with code examples from RAG.

        WHY: Examples show correct patterns, reducing hallucinations.
        PATTERNS: Template pattern with example injection.

        Args:
            original_prompt: Original prompt
            failure_analysis: Failure analysis
            examples: Code examples from RAG
            attempt: Retry attempt number

        Returns:
            RefinedPrompt with examples added
        """
        # Start with standard refinement
        refined = self.refine_prompt(original_prompt, failure_analysis, attempt)

        # Early return if no examples
        if not examples:
            return refined

        # Add examples section (avoid string concatenation in loop)
        examples_section = self._build_examples_section(examples)

        # Combine refined prompt with examples
        refined.prompt = f"{refined.prompt}\n\n{examples_section}"

        if self.logger:
            self.logger.log(
                f"✨ Added {len(examples)} examples to refined prompt",
                "DEBUG"
            )

        return refined

    def _build_examples_section(self, examples: List[str]) -> str:
        """
        Build examples section for prompt.

        WHY: Formatted examples help LLM understand correct patterns.
        PERFORMANCE: List join instead of string concatenation.

        Args:
            examples: List of code examples

        Returns:
            Formatted examples section
        """
        # Build header
        parts = [
            "## HIGH-QUALITY EXAMPLES",
            "Here are examples of correct implementations:"
        ]

        # Add each example with numbering (list comprehension)
        numbered_examples = [
            f"\n### Example {i+1}:\n```python\n{example}\n```"
            for i, example in enumerate(examples)
        ]

        parts.extend(numbered_examples)

        return "\n".join(parts)


class PromptRefinementFactory:
    """
    Factory for creating prompt refinement engines.

    WHY: Enables different engine configurations without code changes.
    PATTERNS: Factory pattern (Open/Closed principle).
    """

    @staticmethod
    def create_engine(logger: Optional[LoggerInterface] = None) -> PromptRefinementEngine:
        """
        Create prompt refinement engine.

        Args:
            logger: Optional logger

        Returns:
            PromptRefinementEngine instance
        """
        return PromptRefinementEngine(logger=logger)
