#!/usr/bin/env python3
"""
WHY: Execute reasoning strategies with LLM client integration.

RESPONSIBILITY: Implement execution logic for different reasoning strategy types.

PATTERNS:
- Strategy Pattern: Different execution approaches for reasoning types
- Template Method: Common execution flow with strategy-specific steps
- Guard Clauses: Early validation and returns
"""

from typing import Dict, List, Optional, Any
import logging

from reasoning_strategies import (
    ReasoningStrategyBase,
    TreeOfThoughtsStrategy,
    SelfConsistencyStrategy
)
from llm_client import LLMClientInterface, LLMMessage, LLMResponse
from reasoning.models import ReasoningConfig, ReasoningType


class ReasoningExecutor:
    """
    Execute reasoning strategies with LLM client.

    WHY: Centralize LLM execution logic for all reasoning types.
    """

    def __init__(
        self,
        llm_client: LLMClientInterface,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize reasoning executor.

        Args:
            llm_client: LLM client for completions
            logger: Logger instance for diagnostics
        """
        self.llm_client = llm_client
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self._executor_map = self._build_executor_map()

    def execute(
        self,
        messages: List[LLMMessage],
        strategy: ReasoningStrategyBase,
        config: ReasoningConfig,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute reasoning strategy with LLM client.

        WHY: Route to appropriate executor based on strategy type.

        Args:
            messages: Enhanced messages to send
            strategy: Reasoning strategy instance
            config: Reasoning configuration
            model: Optional model override
            temperature: Optional temperature override
            max_tokens: Optional max_tokens override

        Returns:
            Dictionary with response and reasoning metadata

        Pattern: Dispatch table with guard clauses
        """
        # Guard clause: Validate messages
        if not messages:
            self.logger.warning("No messages provided for execution")
            return self._empty_result()

        # Get executor function for strategy type
        executor_func = self._executor_map.get(
            config.strategy,
            self._execute_single_shot
        )

        # Execute with appropriate strategy
        return executor_func(
            messages,
            strategy,
            config,
            model,
            temperature,
            max_tokens
        )

    def _execute_single_shot(
        self,
        messages: List[LLMMessage],
        strategy: ReasoningStrategyBase,
        config: ReasoningConfig,
        model: Optional[str],
        temperature: Optional[float],
        max_tokens: Optional[int]
    ) -> Dict[str, Any]:
        """
        Execute single-shot reasoning (CoT, LoT).

        WHY: Simple one-call execution for linear reasoning.

        Args:
            messages: Messages to send
            strategy: Reasoning strategy
            config: Configuration
            model: Model override
            temperature: Temperature override
            max_tokens: Max tokens override

        Returns:
            Result dictionary with response and reasoning output

        Pattern: Single LLM call with response parsing
        """
        response = self.llm_client.complete(
            messages=messages,
            model=model,
            temperature=temperature or config.temperature,
            max_tokens=max_tokens or config.max_tokens
        )

        # Parse response with strategy
        reasoning_output = strategy.parse_response(response.content)

        self.logger.info(
            f"Applied {config.strategy.value} reasoning "
            f"(tokens: {response.usage['total_tokens']})"
        )

        return {
            "response": response,
            "reasoning_applied": True,
            "reasoning_strategy": config.strategy.value,
            "reasoning_output": reasoning_output
        }

    def _execute_tree_of_thoughts(
        self,
        messages: List[LLMMessage],
        strategy: TreeOfThoughtsStrategy,
        config: ReasoningConfig,
        model: Optional[str],
        temperature: Optional[float],
        max_tokens: Optional[int]
    ) -> Dict[str, Any]:
        """
        Execute Tree of Thoughts exploration.

        WHY: Multi-branch exploration with path selection.

        Args:
            messages: Messages to send
            strategy: ToT strategy instance
            config: Configuration
            model: Model override
            temperature: Temperature override
            max_tokens: Max tokens override

        Returns:
            Result dictionary with branches and best path

        Pattern: Branching exploration with best path selection
        """
        # Initial exploration
        response = self.llm_client.complete(
            messages=messages,
            model=model,
            temperature=temperature or config.temperature,
            max_tokens=max_tokens or config.max_tokens
        )

        # Parse initial branches
        reasoning_output = strategy.parse_response(response.content)

        # Select best path (simplified - would normally iterate deeper)
        best_path = strategy.select_best_path() if strategy.root else []

        self.logger.info(
            f"Applied Tree of Thoughts reasoning with "
            f"{reasoning_output.get('branches', 0)} branches explored"
        )

        return {
            "response": response,
            "reasoning_applied": True,
            "reasoning_strategy": "tree_of_thoughts",
            "reasoning_output": reasoning_output,
            "best_path": [node.thought for node in best_path]
        }

    def _execute_self_consistency(
        self,
        messages: List[LLMMessage],
        strategy: SelfConsistencyStrategy,
        config: ReasoningConfig,
        model: Optional[str],
        temperature: Optional[float],
        max_tokens: Optional[int]
    ) -> Dict[str, Any]:
        """
        Execute Self-Consistency with multiple samples.

        WHY: Multiple sampling for answer consistency verification.

        Args:
            messages: Messages to send
            strategy: Self-consistency strategy instance
            config: Configuration
            model: Model override
            temperature: Temperature override
            max_tokens: Max tokens override

        Returns:
            Result dictionary with samples and consistent answer

        Pattern: Multiple sampling with consistency aggregation
        """
        samples = []
        total_tokens = 0
        last_response = None

        # Generate multiple samples
        for i in range(config.sc_num_samples):
            response = self.llm_client.complete(
                messages=messages,
                model=model,
                temperature=temperature or config.temperature,
                max_tokens=max_tokens or config.max_tokens
            )

            samples.append(response.content)
            total_tokens += response.usage['total_tokens']
            last_response = response

            # Parse each sample
            strategy.parse_response(response.content)

        # Get consistent answer
        consistent_answer = strategy.get_consistent_answer()

        self.logger.info(
            f"Applied Self-Consistency reasoning with {config.sc_num_samples} samples "
            f"(total tokens: {total_tokens})"
        )

        return {
            "response": last_response,
            "reasoning_applied": True,
            "reasoning_strategy": "self_consistency",
            "samples": samples,
            "consistent_answer": consistent_answer,
            "total_tokens": total_tokens
        }

    def _build_executor_map(self) -> Dict[ReasoningType, callable]:
        """
        Build dispatch table for executor functions.

        WHY: Map strategy types to their execution functions.

        Returns:
            Dictionary mapping strategy type to executor function

        Pattern: Dispatch table construction
        """
        return {
            ReasoningType.CHAIN_OF_THOUGHT: self._execute_single_shot,
            ReasoningType.LOGIC_OF_THOUGHTS: self._execute_single_shot,
            ReasoningType.TREE_OF_THOUGHTS: self._execute_tree_of_thoughts,
            ReasoningType.SELF_CONSISTENCY: self._execute_self_consistency
        }

    def _empty_result(self) -> Dict[str, Any]:
        """
        Create empty result for error cases.

        WHY: Consistent error result structure.

        Returns:
            Empty result dictionary
        """
        return {
            "response": None,
            "reasoning_applied": False,
            "reasoning_strategy": None,
            "error": "No messages provided"
        }
