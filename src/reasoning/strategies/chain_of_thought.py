#!/usr/bin/env python3
"""
Chain of Thought (CoT) Reasoning Strategy

WHY: Implements step-by-step reasoning that encourages LLMs to show their work,
     improving accuracy on complex reasoning tasks by making intermediate steps explicit.

RESPONSIBILITY:
    - Generate CoT prompts with optional few-shot examples
    - Parse step-by-step reasoning from LLM responses
    - Extract structured reasoning steps from natural language
    - Maintain chain of reasoning steps

PATTERNS:
    - Strategy Pattern: Concrete implementation of reasoning strategy
    - Template Method: Uses base class contract
    - Guard Clauses: Early returns for edge cases
"""

from typing import Dict, List, Optional, Any
import logging

from .models import ReasoningStrategyBase, ReasoningStep


class ChainOfThoughtStrategy(ReasoningStrategyBase):
    """
    Chain of Thought (CoT) prompting strategy.

    Encourages step-by-step reasoning with explicit intermediate steps.

    WHY: Breaking complex problems into steps improves LLM reasoning accuracy
    RESPONSIBILITY: Generate CoT prompts and parse step-by-step responses

    Example:
        cot = ChainOfThoughtStrategy()
        prompt = cot.generate_prompt("Solve: If a train travels 120 miles in 2 hours...")
        result = cot.parse_response(llm_response)
    """

    def generate_prompt(
        self,
        task: str,
        context: Optional[str] = None,
        examples: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate CoT prompt with step-by-step instructions.

        WHY: Structured prompts guide LLM to show reasoning steps
        PATTERNS: Guard clauses for optional parameters

        Args:
            task: The task to solve
            context: Additional context information
            examples: Few-shot examples with reasoning demonstrations

        Returns:
            Formatted prompt with CoT instructions
        """
        prompt = "Let's solve this step by step.\n\n"

        # Guard clause: Add context if provided
        if context:
            prompt += f"Context:\n{context}\n\n"

        # Guard clause: Add few-shot examples if provided
        if examples:
            prompt += self._format_examples(examples)

        prompt += f"Task: {task}\n\n"
        prompt += self._get_step_instructions()

        return prompt

    def _format_examples(self, examples: List[Dict[str, str]]) -> str:
        """
        Format few-shot examples for CoT prompt.

        WHY: Separate formatting logic for better testability and maintainability
        RESPONSIBILITY: Convert examples list to formatted string

        Args:
            examples: List of example dictionaries

        Returns:
            Formatted examples string
        """
        result = "Here are some examples of step-by-step reasoning:\n\n"

        for i, example in enumerate(examples, 1):
            result += f"Example {i}:\n"
            result += f"Question: {example['question']}\n"
            result += f"Reasoning: {example['reasoning']}\n"
            result += f"Answer: {example['answer']}\n\n"

        return result

    def _get_step_instructions(self) -> str:
        """
        Get standard CoT step instructions.

        WHY: Centralized instructions for consistency
        RESPONSIBILITY: Provide template step-by-step instructions

        Returns:
            Step-by-step instruction text
        """
        return (
            "Please think through this step by step:\n"
            "1. First, identify what information we have\n"
            "2. Then, determine what we need to find\n"
            "3. Next, break down the solution into logical steps\n"
            "4. Work through each step carefully\n"
            "5. Finally, verify the answer makes sense\n\n"
            "Your step-by-step reasoning:"
        )

    def parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse CoT response into structured reasoning steps.

        WHY: Structured parsing enables analysis and verification
        PATTERNS: Guard clauses for empty input

        Args:
            response: LLM response with step-by-step reasoning

        Returns:
            Structured dictionary with reasoning steps
        """
        # Guard clause: Handle empty response
        if not response or not response.strip():
            return {
                "strategy": "chain_of_thought",
                "steps": [],
                "total_steps": 0,
                "error": "empty_response"
            }

        steps = self._extract_steps(response)
        self.steps = steps

        return {
            "strategy": "chain_of_thought",
            "steps": [s.to_dict() for s in steps],
            "total_steps": len(steps)
        }

    def _extract_steps(self, response: str) -> List[ReasoningStep]:
        """
        Extract reasoning steps from response text.

        WHY: Separate extraction logic for better testability
        RESPONSIBILITY: Parse text into ReasoningStep objects
        PATTERNS: Guard clauses for line processing

        Args:
            response: Response text to parse

        Returns:
            List of extracted reasoning steps
        """
        lines = response.strip().split('\n')
        steps = []
        current_step = None
        step_num = 0

        for line in lines:
            # Guard clause: Skip empty lines
            if not line.strip():
                continue

            # Check if line starts a new step
            if self._is_step_marker(line):
                # Save previous step if exists
                if current_step:
                    steps.append(current_step)

                # Start new step
                step_num += 1
                current_step = ReasoningStep(
                    step_number=step_num,
                    description=line.strip(),
                    reasoning=""
                )
            elif current_step:
                # Add to current step's reasoning
                current_step.reasoning += line + "\n"

        # Don't forget the last step
        if current_step:
            steps.append(current_step)

        return steps

    def _is_step_marker(self, line: str) -> bool:
        """
        Check if line marks the start of a reasoning step.

        WHY: Centralized step detection logic
        RESPONSIBILITY: Identify step markers (numbered or labeled)

        Args:
            line: Text line to check

        Returns:
            True if line starts a step, False otherwise
        """
        # Guard clause: Empty line cannot be step marker
        if not line.strip():
            return False

        # Check for common step patterns
        first_char = line.strip()[0]
        lower_line = line.lower()

        return first_char.isdigit() or lower_line.startswith('step')
