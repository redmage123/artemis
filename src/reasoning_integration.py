#!/usr/bin/env python3
"""
WHY: Backward compatibility wrapper for reasoning_integration module.

RESPONSIBILITY: Maintain existing API while delegating to modular reasoning/ package.

PATTERNS:
- Facade Pattern: Simple interface over complex subsystem
- Adapter Pattern: Bridge old and new implementations
- Deprecation Warning: Guide users to new API

MIGRATION GUIDE:
    Old:
        from reasoning_integration import ReasoningEnhancedLLMClient, ReasoningConfig
        from reasoning_strategies import ReasoningStrategy

        config = ReasoningConfig(strategy=ReasoningStrategy.CHAIN_OF_THOUGHT)
        client = ReasoningEnhancedLLMClient(base_client)

    New:
        from reasoning import ReasoningEnhancedLLMClient, ReasoningConfig, ReasoningType

        config = ReasoningConfig(strategy=ReasoningType.CHAIN_OF_THOUGHT)
        client = ReasoningEnhancedLLMClient(base_client)

REFACTORED: This module has been refactored into the reasoning/ package.
    - reasoning/models.py - Data models and configuration
    - reasoning/strategy_selector.py - Strategy selection logic
    - reasoning/prompt_enhancer.py - Prompt enhancement
    - reasoning/executors.py - Execution strategies
    - reasoning/llm_client_wrapper.py - LLM client wrapper
    - reasoning/__init__.py - Package exports

Original file: reasoning_integration_original.py (647 lines)
New structure: 6 focused modules (~150-250 lines each)
"""

import warnings
from typing import Dict, List, Optional, Any

# Import from modular package
from reasoning import (
    ReasoningConfig,
    ReasoningType,
    ReasoningResult,
    ReasoningEnhancedLLMClient,
    PromptEnhancer as ReasoningPromptEnhancer,
    create_reasoning_client as create_reasoning_enhanced_client,
    get_default_config_for_task as get_default_reasoning_config
)

# Import for backward compatibility with old enum
from reasoning_strategies import ReasoningStrategy


# Emit deprecation warning when module is imported
warnings.warn(
    "reasoning_integration module is deprecated. "
    "Use 'from reasoning import ReasoningEnhancedLLMClient, ReasoningConfig, ReasoningType' instead. "
    "See module docstring for migration guide.",
    DeprecationWarning,
    stacklevel=2
)


# Re-export all public APIs for backward compatibility
__all__ = [
    # Main classes
    "ReasoningConfig",
    "ReasoningEnhancedLLMClient",
    "ReasoningPromptEnhancer",

    # Types and enums
    "ReasoningType",
    "ReasoningResult",
    "ReasoningStrategy",  # Legacy enum

    # Factory functions
    "create_reasoning_enhanced_client",
    "get_default_reasoning_config",
]


# ============================================================================
# CLI INTERFACE - Maintained for backward compatibility
# ============================================================================

if __name__ == "__main__":
    import argparse
    import sys
    import logging
    from llm_client import LLMMessage

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    parser = argparse.ArgumentParser(description="Reasoning Integration Demo")
    parser.add_argument("--provider", default="openai", choices=["openai", "anthropic"],
                       help="LLM provider")
    parser.add_argument("--strategy", required=True,
                       choices=["cot", "tot", "lot", "sc"],
                       help="Reasoning strategy")
    parser.add_argument("--task", required=True, help="Task to solve")
    parser.add_argument("--context", help="Additional context")

    args = parser.parse_args()

    # Map CLI args to enum
    strategy_map = {
        "cot": ReasoningType.CHAIN_OF_THOUGHT,
        "tot": ReasoningType.TREE_OF_THOUGHTS,
        "lot": ReasoningType.LOGIC_OF_THOUGHTS,
        "sc": ReasoningType.SELF_CONSISTENCY
    }

    try:
        # Create reasoning-enhanced client
        client = create_reasoning_enhanced_client(args.provider)

        # Build messages
        messages = [
            LLMMessage(role="system", content="You are a helpful assistant."),
            LLMMessage(role="user", content=args.task)
        ]

        if args.context:
            messages.insert(1, LLMMessage(role="system", content=args.context))

        # Create reasoning config
        config = ReasoningConfig(
            strategy=strategy_map[args.strategy],
            enabled=True,
            sc_num_samples=3 if args.strategy == "sc" else 5
        )

        print("=" * 80)
        print(f"REASONING STRATEGY: {args.strategy.upper()}")
        print("=" * 80)
        print(f"\nTask: {args.task}")
        if args.context:
            print(f"Context: {args.context}")
        print("\nExecuting with reasoning enhancement...")
        print("-" * 80)

        # Execute with reasoning
        result = client.complete_with_reasoning(
            messages=messages,
            reasoning_config=config
        )

        print("\nRESPONSE:")
        print("-" * 80)
        print(result["response"].content)
        print("-" * 80)

        print("\nREASONING METADATA:")
        print(f"Strategy Applied: {result['reasoning_strategy']}")
        print(f"Total Tokens: {result['response'].usage['total_tokens']}")

        if "reasoning_output" in result:
            print("\nREASONING OUTPUT:")
            import json
            print(json.dumps(result["reasoning_output"], indent=2))

        if "consistent_answer" in result:
            print("\nCONSISTENT ANSWER:")
            import json
            print(json.dumps(result["consistent_answer"], indent=2))

        print("=" * 80)

    except Exception as e:
        logging.error(f"Error: {e}")
        sys.exit(1)
