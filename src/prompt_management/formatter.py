"""
WHY: Format prompts with DEPTH framework and reasoning strategies.
RESPONSIBILITY: Build complete prompts with all components.
PATTERNS: Builder pattern, dispatch table for reasoning strategies, guard clauses.

This module handles the complex logic of assembling prompts from
their constituent parts, applying DEPTH framework and reasoning strategies.
"""

from typing import Dict, List, Optional, Any
from .models import PromptTemplate, ReasoningStrategyType


class PromptFormatter:
    """
    WHY: Format prompts with DEPTH framework components.
    RESPONSIBILITY: Assemble complete prompts from templates.
    PATTERNS: Builder pattern, template method pattern.
    """

    def __init__(self, verbose: bool = False):
        """
        WHY: Initialize formatter with configuration.
        RESPONSIBILITY: Set up formatting behavior.
        PATTERNS: Configuration injection.

        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose

        # Dispatch table for reasoning instructions
        self._reasoning_instructions = {
            ReasoningStrategyType.CHAIN_OF_THOUGHT: self._get_cot_instructions,
            ReasoningStrategyType.TREE_OF_THOUGHTS: self._get_tot_instructions,
            ReasoningStrategyType.LOGIC_OF_THOUGHTS: self._get_lot_instructions,
            ReasoningStrategyType.SELF_CONSISTENCY: self._get_self_consistency_instructions,
        }

        # Dispatch table for reasoning templates
        self._reasoning_templates = {
            ReasoningStrategyType.CHAIN_OF_THOUGHT: self._get_cot_template,
            ReasoningStrategyType.TREE_OF_THOUGHTS: self._get_tot_template,
            ReasoningStrategyType.LOGIC_OF_THOUGHTS: self._get_lot_template,
            ReasoningStrategyType.SELF_CONSISTENCY: self._get_self_consistency_template,
        }

    def format_system_message(self, prompt: PromptTemplate) -> str:
        """
        WHY: Build complete system message with DEPTH components.
        RESPONSIBILITY: Assemble system message from template parts.
        PATTERNS: Builder pattern, guard clauses for optional components.

        Args:
            prompt: PromptTemplate to format

        Returns:
            Complete system message string
        """
        parts = [prompt.system_message]

        # Add perspectives if present
        if prompt.perspectives:
            parts.append(self._format_perspectives(prompt.perspectives))

        # Add success metrics if present
        if prompt.success_metrics:
            parts.append(self._format_success_metrics(prompt.success_metrics))

        # Add reasoning strategy instructions if not NONE
        if prompt.reasoning_strategy != ReasoningStrategyType.NONE:
            instructions = self._get_reasoning_instructions_dispatch(
                prompt.reasoning_strategy
            )
            if instructions:
                parts.append(f"\n**Reasoning Strategy:**\n{instructions}")

        # Add self-critique if present
        if prompt.self_critique:
            parts.append(f"\n**Self-Validation:**\n{prompt.self_critique}")

        return "\n".join(parts)

    def format_user_message(
        self,
        prompt: PromptTemplate,
        base_message: str
    ) -> str:
        """
        WHY: Build complete user message with context and tasks.
        RESPONSIBILITY: Assemble user message from template parts.
        PATTERNS: Builder pattern, guard clauses.

        Args:
            prompt: PromptTemplate for context
            base_message: Base message with variables already substituted

        Returns:
            Complete user message string
        """
        parts = [base_message]

        # Add context layers if present
        if prompt.context_layers:
            parts.append(self._format_context_layers(prompt.context_layers))

        # Add reasoning template if applicable
        reasoning_template = self._get_reasoning_template_dispatch(
            prompt.reasoning_strategy,
            prompt.reasoning_config or {}
        )
        if reasoning_template:
            parts.append(reasoning_template)

        # Add task breakdown if present
        if prompt.task_breakdown:
            parts.append(self._format_task_breakdown(prompt.task_breakdown))

        return "\n".join(parts)

    def _format_perspectives(self, perspectives: List[str]) -> str:
        """
        WHY: Format multiple expert perspectives section.
        RESPONSIBILITY: Create formatted perspectives list.
        PATTERNS: Guard clause for empty list.

        Args:
            perspectives: List of perspective descriptions

        Returns:
            Formatted perspectives string
        """
        # Guard clause: Early return for empty list
        if not perspectives:
            return ""

        formatted = "\n".join([f"- {p}" for p in perspectives])
        return f"\n**Multiple Expert Perspectives:**\n{formatted}"

    def _format_success_metrics(self, metrics: List[str]) -> str:
        """
        WHY: Format success metrics section.
        RESPONSIBILITY: Create formatted metrics list.
        PATTERNS: Guard clause for empty list.

        Args:
            metrics: List of success criteria

        Returns:
            Formatted metrics string
        """
        # Guard clause: Early return for empty list
        if not metrics:
            return ""

        formatted = "\n".join([f"- {m}" for m in metrics])
        return f"\n**Success Criteria:**\n{formatted}"

    def _format_context_layers(self, context: Dict[str, Any]) -> str:
        """
        WHY: Format context layers section.
        RESPONSIBILITY: Create formatted context information.
        PATTERNS: Guard clause for empty dict.

        Args:
            context: Context layers dictionary

        Returns:
            Formatted context string
        """
        # Guard clause: Early return for empty context
        if not context:
            return ""

        lines = ["\n**Context:**"]
        for key, value in context.items():
            lines.append(f"- {key}: {value}")

        return "\n".join(lines)

    def _format_task_breakdown(self, tasks: List[str]) -> str:
        """
        WHY: Format task breakdown section.
        RESPONSIBILITY: Create numbered task list.
        PATTERNS: Guard clause for empty list.

        Args:
            tasks: List of task descriptions

        Returns:
            Formatted task breakdown string
        """
        # Guard clause: Early return for empty list
        if not tasks:
            return ""

        lines = ["\n**Task Breakdown:**"]
        for i, task in enumerate(tasks, 1):
            lines.append(f"{i}. {task}")

        return "\n".join(lines)

    def _get_reasoning_instructions_dispatch(
        self,
        strategy: ReasoningStrategyType
    ) -> str:
        """
        WHY: Get reasoning instructions using dispatch table.
        RESPONSIBILITY: Route to appropriate instruction generator.
        PATTERNS: Dispatch table instead of if/elif chain.

        Args:
            strategy: Reasoning strategy type

        Returns:
            Instruction string or empty string
        """
        instruction_func = self._reasoning_instructions.get(strategy)

        # Guard clause: Return empty if no function found
        if not instruction_func:
            return ""

        return instruction_func()

    def _get_reasoning_template_dispatch(
        self,
        strategy: ReasoningStrategyType,
        config: Dict[str, Any]
    ) -> str:
        """
        WHY: Get reasoning template using dispatch table.
        RESPONSIBILITY: Route to appropriate template generator.
        PATTERNS: Dispatch table instead of if/elif chain.

        Args:
            strategy: Reasoning strategy type
            config: Strategy-specific configuration

        Returns:
            Template string or empty string
        """
        template_func = self._reasoning_templates.get(strategy)

        # Guard clause: Return empty if no function found
        if not template_func:
            return ""

        return template_func(config)

    # Reasoning instruction generators

    def _get_cot_instructions(self) -> str:
        """Chain of Thought instructions"""
        return """
You MUST think through this problem step-by-step, showing all intermediate reasoning.
Break down complex problems into logical steps and explain each step clearly.
"""

    def _get_tot_instructions(self) -> str:
        """Tree of Thoughts instructions"""
        return """
Explore multiple approaches in parallel. For each approach:
1. Describe the core idea
2. List advantages and challenges
3. Score from 0-10
Present alternatives as JSON array.
"""

    def _get_lot_instructions(self) -> str:
        """Logic of Thoughts instructions"""
        return """
Use formal logical reasoning and deductions. Apply logical rules:
- Modus Ponens: If P then Q, P is true, therefore Q
- Modus Tollens: If P then Q, Q is false, therefore P is false
- Syllogism: If P then Q, Q then R, therefore P then R
Show each deduction explicitly.
"""

    def _get_self_consistency_instructions(self) -> str:
        """Self-consistency instructions"""
        return """
Solve this problem and show your complete reasoning.
Your answer will be sampled multiple times to ensure consistency.
"""

    # Reasoning template generators

    def _get_cot_template(self, config: Dict[str, Any]) -> str:
        """
        WHY: Generate Chain of Thought template.
        RESPONSIBILITY: Build CoT template with optional examples.
        PATTERNS: Guard clause for examples.

        Args:
            config: Configuration with optional examples

        Returns:
            CoT template string
        """
        template = "\n\n**Think Step by Step:**\n"
        template += "1. First, identify what information we have\n"
        template += "2. Then, determine what we need to find\n"
        template += "3. Next, break down the solution into logical steps\n"
        template += "4. Work through each step carefully\n"
        template += "5. Finally, verify the answer makes sense\n"

        # Guard clause: Return early if no examples
        examples = config.get("examples", [])
        if not examples:
            return template

        # Add examples section
        template += "\n**Example Reasoning:**\n"
        for i, ex in enumerate(examples, 1):
            template += f"\nExample {i}:\n"
            template += f"Q: {ex.get('question', '')}\n"
            template += f"Reasoning: {ex.get('reasoning', '')}\n"
            template += f"A: {ex.get('answer', '')}\n"

        return template

    def _get_tot_template(self, config: Dict[str, Any]) -> str:
        """
        WHY: Generate Tree of Thoughts template.
        RESPONSIBILITY: Build ToT template with branching factor.
        PATTERNS: Configuration-based generation.

        Args:
            config: Configuration with branching_factor

        Returns:
            ToT template string
        """
        branching = config.get("branching_factor", 3)
        template = f"\n\n**Explore {branching} Different Approaches:**\n"
        template += "For each approach provide:\n"
        template += "- Core idea\n"
        template += "- Advantages\n"
        template += "- Challenges\n"
        template += "- Score (0-10)\n"
        return template

    def _get_lot_template(self, config: Dict[str, Any]) -> str:
        """
        WHY: Generate Logic of Thoughts template.
        RESPONSIBILITY: Build LoT template with optional axioms.
        PATTERNS: Guard clause for axioms.

        Args:
            config: Configuration with optional axioms

        Returns:
            LoT template string
        """
        template = "\n\n**Apply Formal Logic:**\n"
        template += "1. Identify all given premises\n"
        template += "2. State any assumptions clearly\n"
        template += "3. Apply logical rules step by step\n"
        template += "4. Show each deduction explicitly\n"
        template += "5. Verify conclusion follows logically\n"

        # Guard clause: Return early if no axioms
        axioms = config.get("axioms", [])
        if not axioms:
            return template

        # Add axioms section
        template += "\n**Known Facts (Axioms):**\n"
        for i, axiom in enumerate(axioms, 1):
            template += f"{i}. {axiom}\n"

        return template

    def _get_self_consistency_template(self, config: Dict[str, Any]) -> str:
        """
        WHY: Generate Self-consistency template.
        RESPONSIBILITY: Build simple self-consistency template.
        PATTERNS: Minimal template generation.

        Args:
            config: Configuration (unused for this strategy)

        Returns:
            Self-consistency template string
        """
        return "\n\n**Provide your complete reasoning and solution.**\n"
