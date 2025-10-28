#!/usr/bin/env python3
"""
WHY: Enhance prompts with reasoning strategy instructions and templates.

RESPONSIBILITY: Add reasoning-specific instructions to system and user messages.

PATTERNS:
- Template Method: Consistent enhancement flow with strategy-specific customization
- Dispatch Table: Strategy-to-instruction mapping
- Guard Clauses: Early returns for disabled reasoning
"""

from typing import Dict, List, Optional
import logging

from artemis_exceptions import wrap_exception, LLMClientError
from reasoning.models import ReasoningConfig, ReasoningType


class PromptEnhancer:
    """
    Enhance prompts with reasoning strategy instructions.

    WHY: Integrate reasoning instructions into prompts systematically.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize prompt enhancer.

        Args:
            logger: Logger instance for diagnostics
        """
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self._instruction_map = self._build_instruction_map()
        self._template_builders = self._build_template_builders()

    @wrap_exception(LLMClientError, "Failed to enhance prompt with reasoning")
    def enhance_prompt(
        self,
        base_prompt: Dict[str, str],
        reasoning_config: ReasoningConfig
    ) -> Dict[str, str]:
        """
        Enhance a prompt with reasoning strategy instructions.

        WHY: Add reasoning instructions to base prompt.

        Args:
            base_prompt: Dict with 'system' and 'user' messages
            reasoning_config: Reasoning configuration

        Returns:
            Enhanced prompt dict with reasoning instructions

        Pattern: Template Method with guard clauses
        """
        # Guard clause: Check if reasoning is enabled
        if not reasoning_config.enabled:
            return base_prompt

        # Guard clause: Validate base prompt structure
        if not self._is_valid_prompt(base_prompt):
            self.logger.warning("Invalid base prompt structure, returning unchanged")
            return base_prompt

        enhanced = base_prompt.copy()

        # Add reasoning instructions to system message
        reasoning_instructions = self._get_reasoning_instructions(reasoning_config)
        enhanced["system"] = f"{base_prompt['system']}\n\n{reasoning_instructions}"

        # Add reasoning template to user message if applicable
        enhanced = self._add_user_message_template(
            enhanced,
            base_prompt,
            reasoning_config
        )

        self.logger.info(f"Enhanced prompt with {reasoning_config.strategy.value} reasoning")

        return enhanced

    def _is_valid_prompt(self, prompt: Dict[str, str]) -> bool:
        """
        Validate prompt structure.

        WHY: Ensure prompt has required fields before enhancement.

        Args:
            prompt: Prompt dictionary

        Returns:
            True if valid, False otherwise

        Pattern: Guard clause validation
        """
        if not prompt:
            return False

        if "system" not in prompt or "user" not in prompt:
            return False

        if not isinstance(prompt["system"], str) or not isinstance(prompt["user"], str):
            return False

        return True

    def _get_reasoning_instructions(self, config: ReasoningConfig) -> str:
        """
        Get reasoning strategy instructions for system message.

        WHY: Retrieve strategy-specific instructions.

        Args:
            config: Reasoning configuration

        Returns:
            Instructions string for the strategy

        Pattern: Dispatch table lookup
        """
        return self._instruction_map.get(config.strategy, "")

    def _add_user_message_template(
        self,
        enhanced: Dict[str, str],
        base_prompt: Dict[str, str],
        config: ReasoningConfig
    ) -> Dict[str, str]:
        """
        Add reasoning template to user message based on strategy.

        WHY: Some strategies need user message templates.

        Args:
            enhanced: Enhanced prompt being built
            base_prompt: Original prompt
            config: Reasoning configuration

        Returns:
            Enhanced prompt with user message template

        Pattern: Dispatch table for template builders
        """
        # Guard clause: Check if strategy needs template
        if config.strategy not in self._template_builders:
            return enhanced

        template_builder = self._template_builders[config.strategy]
        template = template_builder(config)

        # Guard clause: Skip if no template generated
        if not template:
            return enhanced

        enhanced["user"] = f"{base_prompt['user']}\n\n{template}"
        return enhanced

    def _build_instruction_map(self) -> Dict[ReasoningType, str]:
        """
        Build dispatch table for reasoning instructions.

        WHY: Centralize strategy-to-instruction mapping.

        Returns:
            Dictionary mapping strategy type to instructions

        Pattern: Dispatch table construction
        """
        return {
            ReasoningType.CHAIN_OF_THOUGHT: """
**Reasoning Strategy: Chain of Thought**

You must think through this problem step-by-step, showing all intermediate reasoning.
Break down complex problems into logical steps and explain each step clearly.
""",
            ReasoningType.TREE_OF_THOUGHTS: """
**Reasoning Strategy: Tree of Thoughts**

Explore multiple approaches in parallel. For each approach:
1. Describe the core idea
2. List advantages and challenges
3. Score from 0-10

Present alternatives as JSON array with thought, advantages, challenges, and score.
""",
            ReasoningType.LOGIC_OF_THOUGHTS: """
**Reasoning Strategy: Logic of Thoughts**

Use formal logical reasoning and deductions. Apply logical rules:
- Modus Ponens: If P then Q, P is true, therefore Q
- Modus Tollens: If P then Q, Q is false, therefore P is false
- Syllogism: If P then Q, Q then R, therefore P then R

Show each deduction explicitly and verify conclusions logically.
""",
            ReasoningType.SELF_CONSISTENCY: """
**Reasoning Strategy: Self-Consistency**

Solve this problem and show your complete reasoning.
Your answer will be compared with multiple samples to ensure consistency.
"""
        }

    def _build_template_builders(self) -> Dict[ReasoningType, callable]:
        """
        Build dispatch table for template builder functions.

        WHY: Map strategies to their template generation functions.

        Returns:
            Dictionary mapping strategy type to template builder function

        Pattern: Dispatch table with callables
        """
        return {
            ReasoningType.CHAIN_OF_THOUGHT: self._get_cot_template,
            ReasoningType.LOGIC_OF_THOUGHTS: self._get_lot_template
        }

    def _get_cot_template(self, config: ReasoningConfig) -> str:
        """
        Get Chain of Thought template.

        WHY: Provide step-by-step thinking template.

        Args:
            config: Reasoning configuration (unused but required for dispatch table)

        Returns:
            CoT template string
        """
        return """
Please think through this step by step:
1. First, identify what information we have
2. Then, determine what we need to find
3. Next, break down the solution into logical steps
4. Work through each step carefully
5. Finally, verify the answer makes sense
"""

    def _get_lot_template(self, config: ReasoningConfig) -> str:
        """
        Get Logic of Thoughts template.

        WHY: Provide formal logic template with optional axioms.

        Args:
            config: Reasoning configuration with potential axioms

        Returns:
            LoT template string with axioms if provided
        """
        template = "\n**Apply Formal Logic:**\n"
        template += "1. Identify all given premises\n"
        template += "2. State any assumptions clearly\n"
        template += "3. Apply logical rules step by step\n"
        template += "4. Show each deduction explicitly\n"
        template += "5. Verify conclusion follows logically\n"

        # Guard clause: Return basic template if no axioms
        if not config.lot_axioms:
            return template

        template += "\n**Known Facts (Axioms):**\n"
        for i, axiom in enumerate(config.lot_axioms, 1):
            template += f"{i}. {axiom}\n"

        return template


def enhance_prompt_with_reasoning(
    base_prompt: Dict[str, str],
    reasoning_config: ReasoningConfig
) -> Dict[str, str]:
    """
    Convenience function to enhance a prompt with reasoning.

    WHY: Simple function API for one-off prompt enhancement.

    Args:
        base_prompt: Base prompt dictionary
        reasoning_config: Reasoning configuration

    Returns:
        Enhanced prompt dictionary

    Example:
        enhanced = enhance_prompt_with_reasoning(
            base_prompt={"system": "...", "user": "..."},
            reasoning_config=ReasoningConfig(strategy=ReasoningType.CHAIN_OF_THOUGHT)
        )
    """
    enhancer = PromptEnhancer()
    return enhancer.enhance_prompt(base_prompt, reasoning_config)
