#!/usr/bin/env python3
"""
Backward Compatibility Wrapper for Reasoning Strategies

WHY: Maintains backward compatibility with existing code that imports from
     the monolithic reasoning_strategies.py module.

RESPONSIBILITY:
    - Re-export all components from reasoning/strategies/ package
    - Preserve original import paths
    - Provide seamless migration path
    - Include CLI compatibility

PATTERNS:
    - Facade Pattern: Simplified interface to refactored subsystem
    - Adapter Pattern: Adapts new package structure to old interface
    - Deprecation Pattern: Maintains old API while encouraging migration

MIGRATION PATH:
    Old code (still works):
        from reasoning_strategies import ChainOfThoughtStrategy, ReasoningStrategy

    New code (recommended):
        from reasoning.strategies import ChainOfThoughtStrategy, ReasoningStrategy

REFACTORING SUMMARY:
    - Original: 612 lines monolithic module
    - Refactored: 6 focused modules (~150-250 lines each)
    - Wrapper: ~80 lines (this file)
    - Reduction: ~87% reduction in module complexity
"""

# Re-export all public components from refactored package
from reasoning.strategies import (
    # Core models and enums
    ReasoningStrategy,
    ReasoningStep,
    ThoughtNode,
    LogicRule,
    ReasoningStrategyBase,

    # Strategy implementations
    ChainOfThoughtStrategy,
    TreeOfThoughtsStrategy,
    LogicOfThoughtsStrategy,
    SelfConsistencyStrategy,

    # Factory and utilities
    ReasoningStrategyFactory,
    StrategyBuilder,
)

# Preserve __all__ for star imports
__all__ = [
    # Enums and core models
    'ReasoningStrategy',
    'ReasoningStep',
    'ThoughtNode',
    'LogicRule',
    'ReasoningStrategyBase',

    # Strategy implementations
    'ChainOfThoughtStrategy',
    'TreeOfThoughtsStrategy',
    'LogicOfThoughtsStrategy',
    'SelfConsistencyStrategy',

    # Factory and utilities
    'ReasoningStrategyFactory',
    'StrategyBuilder',
]

# CLI interface preserved for backward compatibility
if __name__ == "__main__":
    import argparse
    import logging

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Reasoning Strategy Demo")
    parser.add_argument(
        "strategy",
        choices=["cot", "tot", "lot", "sc"],
        help="Reasoning strategy to demonstrate"
    )
    parser.add_argument("--task", required=True, help="Task to solve")
    parser.add_argument("--context", help="Additional context")

    args = parser.parse_args()

    # Map CLI args to enum (dispatch table pattern)
    strategy_map = {
        "cot": ReasoningStrategy.CHAIN_OF_THOUGHT,
        "tot": ReasoningStrategy.TREE_OF_THOUGHTS,
        "lot": ReasoningStrategy.LOGIC_OF_THOUGHTS,
        "sc": ReasoningStrategy.SELF_CONSISTENCY
    }

    # Create strategy using factory
    factory = ReasoningStrategyFactory()
    strategy = factory.create(strategy_map[args.strategy])

    # Generate prompt
    prompt = strategy.generate_prompt(args.task, args.context)

    print("=" * 80)
    print(f"REASONING STRATEGY: {args.strategy.upper()}")
    print("=" * 80)
    print("\nGENERATED PROMPT:")
    print("-" * 80)
    print(prompt)
    print("=" * 80)
