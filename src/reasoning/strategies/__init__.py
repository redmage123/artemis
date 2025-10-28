#!/usr/bin/env python3
"""
Reasoning Strategies Package

WHY: Provides modular, extensible reasoning strategies for LLM prompting,
     enabling sophisticated problem-solving approaches beyond basic prompts.

RESPONSIBILITY:
    - Export all reasoning strategy components
    - Provide clean public API for strategy usage
    - Maintain backward compatibility with monolithic module
    - Enable easy strategy discovery and creation

PATTERNS:
    - Facade Pattern: Simplified interface to complex subsystem
    - Strategy Pattern: Interchangeable reasoning algorithms
    - Factory Pattern: Centralized strategy creation

USAGE:
    from reasoning.strategies import (
        ReasoningStrategy,
        ChainOfThoughtStrategy,
        TreeOfThoughtsStrategy,
        ReasoningStrategyFactory
    )

    # Create strategy using factory
    factory = ReasoningStrategyFactory()
    strategy = factory.create(ReasoningStrategy.CHAIN_OF_THOUGHT)

    # Or create directly
    cot = ChainOfThoughtStrategy()
    prompt = cot.generate_prompt("Solve this problem...")
"""

# Core models and enums
from .models import (
    ReasoningStrategy,
    ReasoningStep,
    ThoughtNode,
    LogicRule,
    ReasoningStrategyBase
)

# Strategy implementations
from .chain_of_thought import ChainOfThoughtStrategy
from .tree_of_thought import TreeOfThoughtsStrategy
from .logic_of_thought import LogicOfThoughtsStrategy
from .self_consistency import SelfConsistencyStrategy

# Factory and builder
from .strategy_factory import (
    ReasoningStrategyFactory,
    StrategyBuilder
)

# Public API - explicitly define what's exported
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

# Version information
__version__ = '2.0.0'
__author__ = 'Artemis Development Team'
