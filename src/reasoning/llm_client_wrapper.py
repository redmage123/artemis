#!/usr/bin/env python3
"""
WHY: Provide reasoning-enhanced LLM client wrapper.

RESPONSIBILITY: Integrate reasoning strategies into LLM client calls.

PATTERNS:
- Decorator Pattern: Enhance base LLM client with reasoning
- Facade Pattern: Simplify reasoning integration interface
- Guard Clauses: Early returns for disabled reasoning
"""

from typing import Dict, List, Optional, Any
import logging

from artemis_exceptions import wrap_exception, LLMClientError
from llm_client import LLMClientInterface, LLMMessage, LLMResponse
from reasoning.models import ReasoningConfig, ReasoningType
from reasoning.strategy_selector import StrategySelector
from reasoning.executors import ReasoningExecutor


class ReasoningEnhancedLLMClient:
    """
    Wrapper around LLMClientInterface that adds reasoning capabilities.

    WHY: Enhance any LLM client with reasoning strategies using Decorator pattern.

    Example:
        base_client = create_llm_client("openai")
        reasoning_client = ReasoningEnhancedLLMClient(base_client)

        response = reasoning_client.complete_with_reasoning(
            messages=[...],
            reasoning_config=ReasoningConfig(strategy=ReasoningType.CHAIN_OF_THOUGHT)
        )
    """

    def __init__(
        self,
        base_client: LLMClientInterface,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize reasoning-enhanced LLM client.

        Args:
            base_client: Base LLM client to enhance
            logger: Logger instance for diagnostics
        """
        self.base_client = base_client
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.strategy_selector = StrategySelector(logger=self.logger)
        self.executor = ReasoningExecutor(base_client, logger=self.logger)

    @wrap_exception(LLMClientError, "Failed to complete with reasoning")
    def complete_with_reasoning(
        self,
        messages: List[LLMMessage],
        reasoning_config: ReasoningConfig,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Complete LLM request with reasoning strategy applied.

        WHY: Main entry point for reasoning-enhanced completions.

        Args:
            messages: Conversation messages
            reasoning_config: Reasoning configuration
            model: Model to use
            temperature: Temperature override
            max_tokens: Max tokens override

        Returns:
            Dict with response and reasoning metadata

        Raises:
            LLMClientError: If completion fails

        Pattern: Template Method with guard clauses
        """
        # Guard clause: Check if reasoning is disabled
        if not reasoning_config.enabled:
            return self._execute_standard_completion(
                messages,
                model,
                temperature,
                max_tokens
            )

        # Create reasoning strategy
        strategy = self.strategy_selector.create_strategy(reasoning_config)

        # Extract task and context from messages
        task = self._extract_task_from_messages(messages)
        context = self._extract_context_from_messages(messages)

        # Generate reasoning-enhanced prompt
        reasoning_prompt = self._generate_reasoning_prompt(
            strategy,
            task,
            context,
            reasoning_config
        )

        # Build enhanced messages
        enhanced_messages = self._build_enhanced_messages(messages, reasoning_prompt)

        # Execute with reasoning strategy
        return self.executor.execute(
            enhanced_messages,
            strategy,
            reasoning_config,
            model,
            temperature,
            max_tokens
        )

    def _execute_standard_completion(
        self,
        messages: List[LLMMessage],
        model: Optional[str],
        temperature: Optional[float],
        max_tokens: Optional[int]
    ) -> Dict[str, Any]:
        """
        Execute standard completion without reasoning.

        WHY: Fallback for disabled reasoning.

        Args:
            messages: Messages to send
            model: Model override
            temperature: Temperature override
            max_tokens: Max tokens override

        Returns:
            Standard result dictionary

        Pattern: Guard clause handler
        """
        response = self.base_client.complete(
            messages=messages,
            model=model,
            temperature=temperature or 0.7,
            max_tokens=max_tokens or 4000
        )

        return {
            "response": response,
            "reasoning_applied": False,
            "reasoning_strategy": None
        }

    def _extract_task_from_messages(self, messages: List[LLMMessage]) -> str:
        """
        Extract main task from messages.

        WHY: Get the primary user request for reasoning.

        Args:
            messages: List of LLM messages

        Returns:
            Task string from last user message

        Pattern: Guard clause with iteration
        """
        # Guard clause: Check if messages exist
        if not messages:
            return ""

        # Get last user message as task
        for msg in reversed(messages):
            if msg.role == "user":
                return msg.content

        return ""

    def _extract_context_from_messages(self, messages: List[LLMMessage]) -> Optional[str]:
        """
        Extract context from system messages.

        WHY: Get system context for reasoning enhancement.

        Args:
            messages: List of LLM messages

        Returns:
            Context string from system messages or None

        Pattern: Early return on first match
        """
        # Guard clause: Check if messages exist
        if not messages:
            return None

        for msg in messages:
            if msg.role == "system":
                return msg.content

        return None

    def _generate_reasoning_prompt(
        self,
        strategy,
        task: str,
        context: Optional[str],
        config: ReasoningConfig
    ) -> str:
        """
        Generate reasoning-enhanced prompt.

        WHY: Create strategy-specific prompt with task and context.

        Args:
            strategy: Reasoning strategy instance
            task: Task string
            context: Optional context string
            config: Reasoning configuration

        Returns:
            Enhanced prompt string

        Pattern: Dispatch table for strategy-specific generation
        """
        # Dispatch table for prompt generation
        prompt_generators = {
            ReasoningType.CHAIN_OF_THOUGHT: lambda: strategy.generate_prompt(
                task=task,
                context=context,
                examples=config.cot_examples
            ),
            ReasoningType.TREE_OF_THOUGHTS: lambda: strategy.generate_prompt(
                task=task,
                context=context,
                depth=0
            ),
            ReasoningType.LOGIC_OF_THOUGHTS: lambda: strategy.generate_prompt(
                task=task,
                context=context,
                axioms=config.lot_axioms
            )
        }

        generator = prompt_generators.get(
            config.strategy,
            lambda: strategy.generate_prompt(task=task, context=context)
        )

        return generator()

    def _build_enhanced_messages(
        self,
        original_messages: List[LLMMessage],
        reasoning_prompt: str
    ) -> List[LLMMessage]:
        """
        Build enhanced messages with reasoning prompt.

        WHY: Construct message list with reasoning instructions.

        Args:
            original_messages: Original messages
            reasoning_prompt: Reasoning-enhanced prompt

        Returns:
            List of enhanced messages

        Pattern: Filter and append
        """
        enhanced = []

        # Keep system messages
        for msg in original_messages:
            if msg.role == "system":
                enhanced.append(msg)

        # Add reasoning-enhanced user message
        enhanced.append(LLMMessage(role="user", content=reasoning_prompt))

        return enhanced


def create_reasoning_client(
    provider: str = "openai",
    api_key: Optional[str] = None
) -> ReasoningEnhancedLLMClient:
    """
    Create reasoning-enhanced LLM client.

    WHY: Convenience factory for creating reasoning client.

    Args:
        provider: "openai" or "anthropic"
        api_key: API key (optional)

    Returns:
        ReasoningEnhancedLLMClient instance

    Example:
        client = create_reasoning_client("openai")
        response = client.complete_with_reasoning(
            messages=[...],
            reasoning_config=ReasoningConfig(strategy=ReasoningType.CHAIN_OF_THOUGHT)
        )
    """
    from llm_client import create_llm_client

    base_client = create_llm_client(provider, api_key)
    return ReasoningEnhancedLLMClient(base_client)
