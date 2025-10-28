#!/usr/bin/env python3
"""
WHY: Provide clean API for reasoning package.

RESPONSIBILITY: Export public interfaces and maintain backward compatibility.

PATTERNS:
- Facade Pattern: Simple unified interface
- Explicit Exports: Control public API surface
"""

# Core models and types
from reasoning.models import (
    ReasoningConfig,
    ReasoningType,
    ReasoningResult,
    EnhancedMessage,
    get_default_config_for_task
)

# Strategy selection
from reasoning.strategy_selector import (
    StrategySelector,
    select_strategy
)

# Prompt enhancement
from reasoning.prompt_enhancer import (
    PromptEnhancer,
    enhance_prompt_with_reasoning
)

# Execution
from reasoning.executors import ReasoningExecutor

# LLM client wrapper
from reasoning.llm_client_wrapper import (
    ReasoningEnhancedLLMClient,
    create_reasoning_client
)

# Backward compatibility - map old enum to new
from reasoning_strategies import ReasoningStrategy

# Version info
__version__ = "2.0.0"
__all__ = [
    # Models
    "ReasoningConfig",
    "ReasoningType",
    "ReasoningResult",
    "EnhancedMessage",
    "get_default_config_for_task",

    # Strategy selection
    "StrategySelector",
    "select_strategy",

    # Prompt enhancement
    "PromptEnhancer",
    "enhance_prompt_with_reasoning",

    # Execution
    "ReasoningExecutor",

    # Client wrapper
    "ReasoningEnhancedLLMClient",
    "create_reasoning_client",

    # Backward compatibility
    "ReasoningStrategy",
]
