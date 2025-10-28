#!/usr/bin/env python3
"""
WHY: Define data models and configurations for reasoning strategies.

RESPONSIBILITY: Provide data structures for reasoning configuration and types.

PATTERNS:
- Dataclass Pattern: Type-safe configuration with defaults
- Value Object: Immutable configuration objects
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ReasoningType(str, Enum):
    """Enumeration of supported reasoning strategies"""
    CHAIN_OF_THOUGHT = "chain_of_thought"
    TREE_OF_THOUGHTS = "tree_of_thoughts"
    LOGIC_OF_THOUGHTS = "logic_of_thoughts"
    SELF_CONSISTENCY = "self_consistency"


@dataclass
class ReasoningConfig:
    """
    Configuration for reasoning strategy.

    WHY: Centralize all reasoning parameters in one immutable structure.

    Attributes:
        strategy: The reasoning strategy to use
        enabled: Whether reasoning is enabled
        cot_examples: Optional examples for Chain of Thought
        tot_branching_factor: Branching factor for Tree of Thoughts
        tot_max_depth: Maximum depth for Tree of Thoughts
        lot_axioms: Axioms for Logic of Thoughts
        sc_num_samples: Number of samples for Self-Consistency
        temperature: LLM temperature parameter
        max_tokens: Maximum tokens for LLM response
    """
    strategy: ReasoningType
    enabled: bool = True

    # CoT specific
    cot_examples: Optional[List[Dict[str, str]]] = None

    # ToT specific
    tot_branching_factor: int = 3
    tot_max_depth: int = 4

    # LoT specific
    lot_axioms: Optional[List[str]] = None

    # Self-Consistency specific
    sc_num_samples: int = 5

    # General
    temperature: float = 0.7
    max_tokens: int = 4000


@dataclass
class ReasoningResult:
    """
    Result of reasoning-enhanced LLM completion.

    WHY: Standardize the output format for all reasoning strategies.

    Attributes:
        response: The LLM response object
        reasoning_applied: Whether reasoning was applied
        reasoning_strategy: Name of the strategy used
        reasoning_output: Parsed reasoning output
        metadata: Additional strategy-specific metadata
    """
    response: Any  # LLMResponse type
    reasoning_applied: bool
    reasoning_strategy: Optional[str] = None
    reasoning_output: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


# Type alias for enhanced messages
EnhancedMessage = Dict[str, str]


def get_default_config_for_task(task_type: str) -> ReasoningConfig:
    """
    Get default reasoning configuration for task type.

    WHY: Provide sensible defaults based on task characteristics.

    Args:
        task_type: Type of task (coding, architecture, analysis, testing)

    Returns:
        ReasoningConfig with appropriate defaults

    Pattern: Strategy Selection based on task type
    """
    # Guard clause: Check task type is valid
    if not task_type:
        return ReasoningConfig(
            strategy=ReasoningType.CHAIN_OF_THOUGHT,
            enabled=True
        )

    # Dispatch table for task-to-config mapping
    config_map: Dict[str, ReasoningConfig] = {
        "coding": ReasoningConfig(
            strategy=ReasoningType.CHAIN_OF_THOUGHT,
            enabled=True
        ),
        "architecture": ReasoningConfig(
            strategy=ReasoningType.TREE_OF_THOUGHTS,
            enabled=True,
            tot_branching_factor=3,
            tot_max_depth=4
        ),
        "analysis": ReasoningConfig(
            strategy=ReasoningType.LOGIC_OF_THOUGHTS,
            enabled=True
        ),
        "testing": ReasoningConfig(
            strategy=ReasoningType.SELF_CONSISTENCY,
            enabled=True,
            sc_num_samples=3
        )
    }

    return config_map.get(
        task_type.lower(),
        ReasoningConfig(
            strategy=ReasoningType.CHAIN_OF_THOUGHT,
            enabled=True
        )
    )
