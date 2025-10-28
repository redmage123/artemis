"""
WHY: Define core data structures for prompt templates and context.
RESPONSIBILITY: Provide type-safe models for prompt management system.
PATTERNS: Dataclass pattern, Enum pattern for strategy types.

This module contains the fundamental data structures used throughout
the prompt management system, ensuring type safety and clear contracts.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum


class ReasoningStrategyType(Enum):
    """
    WHY: Enumerate available reasoning strategies for prompts.
    RESPONSIBILITY: Define valid reasoning strategy types.
    PATTERNS: Enum pattern for type safety.
    """
    NONE = "none"
    CHAIN_OF_THOUGHT = "chain_of_thought"
    TREE_OF_THOUGHTS = "tree_of_thoughts"
    LOGIC_OF_THOUGHTS = "logic_of_thoughts"
    SELF_CONSISTENCY = "self_consistency"


@dataclass
class PromptTemplate:
    """
    WHY: Represent a structured prompt template with DEPTH framework.
    RESPONSIBILITY: Hold all prompt data including DEPTH components.
    PATTERNS: Dataclass pattern for immutable data structures.

    DEPTH Framework:
    - D: Define Multiple Perspectives
    - E: Establish Clear Success Metrics
    - P: Provide Context Layers
    - T: Task Breakdown
    - H: Human Feedback Loop (Self-Critique)
    """
    prompt_id: str
    name: str
    category: str
    version: str

    # DEPTH Framework Components
    perspectives: List[str]
    success_metrics: List[str]
    context_layers: Dict[str, Any]
    task_breakdown: List[str]
    self_critique: str

    # Prompt Content
    system_message: str
    user_template: str

    # Metadata
    tags: List[str]
    created_at: str
    updated_at: str
    performance_score: float
    usage_count: int
    success_rate: float

    # Reasoning Strategy
    reasoning_strategy: ReasoningStrategyType = ReasoningStrategyType.NONE
    reasoning_config: Optional[Dict[str, Any]] = None


@dataclass
class PromptContext:
    """
    WHY: Encapsulate context information for prompt rendering.
    RESPONSIBILITY: Provide structured context data for template substitution.
    PATTERNS: Dataclass pattern, explicit over implicit.
    """
    variables: Dict[str, Any]
    additional_context: Optional[Dict[str, Any]] = None
    override_reasoning: Optional[ReasoningStrategyType] = None

    def get_all_variables(self) -> Dict[str, Any]:
        """
        WHY: Merge variables with additional context for complete substitution.
        RESPONSIBILITY: Combine all context sources into single dictionary.
        PATTERNS: Guard clause for None check.
        """
        # Guard clause: Early return if no additional context
        if not self.additional_context:
            return self.variables.copy()

        # Merge variables with additional context
        result = self.variables.copy()
        result.update(self.additional_context)
        return result


@dataclass
class RenderedPrompt:
    """
    WHY: Represent a fully rendered prompt ready for LLM consumption.
    RESPONSIBILITY: Hold final system and user messages.
    PATTERNS: Dataclass pattern for data transfer.
    """
    system: str
    user: str
    template_name: str
    template_version: str
    variables_used: Dict[str, Any]
    reasoning_strategy: ReasoningStrategyType
