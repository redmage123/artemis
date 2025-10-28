#!/usr/bin/env python3
"""
Reasoning Strategy Models and Data Classes

WHY: Centralized data models for reasoning strategies to maintain consistency
     and provide a single source of truth for reasoning components.

RESPONSIBILITY:
    - Define core data structures (ReasoningStep, ThoughtNode, LogicRule)
    - Define strategy enumeration (ReasoningStrategy)
    - Provide serialization methods for all models
    - Ensure type safety with dataclasses

PATTERNS:
    - Data Transfer Object (DTO): Structured data carriers
    - Enum Pattern: Type-safe strategy selection
    - Builder Pattern: Node construction with parent-child relationships
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import logging


class ReasoningStrategy(Enum):
    """
    Available reasoning strategies.

    WHY: Type-safe enumeration prevents invalid strategy selections
    RESPONSIBILITY: Define all supported reasoning strategy types
    """
    CHAIN_OF_THOUGHT = "chain_of_thought"
    TREE_OF_THOUGHTS = "tree_of_thoughts"
    LOGIC_OF_THOUGHTS = "logic_of_thoughts"
    SELF_CONSISTENCY = "self_consistency"
    LEAST_TO_MOST = "least_to_most"


@dataclass
class ReasoningStep:
    """
    Single step in reasoning chain.

    WHY: Structured representation of individual reasoning steps for CoT
    RESPONSIBILITY: Store and serialize a single reasoning step with metadata
    """
    step_number: int
    description: str
    reasoning: str
    output: Optional[str] = None
    confidence: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize step to dictionary.

        Returns:
            Dictionary representation of reasoning step
        """
        return {
            "step": self.step_number,
            "description": self.description,
            "reasoning": self.reasoning,
            "output": self.output,
            "confidence": self.confidence
        }


@dataclass
class ThoughtNode:
    """
    Node in tree of thoughts.

    WHY: Hierarchical structure for exploring multiple reasoning paths (ToT)
    RESPONSIBILITY: Manage parent-child relationships and path scoring
    PATTERNS: Composite Pattern for tree structure
    """
    thought: str
    depth: int
    score: float
    children: List['ThoughtNode'] = field(default_factory=list)
    parent: Optional['ThoughtNode'] = None
    path_score: float = 0.0

    def add_child(self, child: 'ThoughtNode') -> 'ThoughtNode':
        """
        Add child node to this node.

        WHY: Builder pattern for constructing tree structure

        Args:
            child: Child node to add

        Returns:
            The added child node for method chaining
        """
        child.parent = self
        self.children.append(child)
        return child

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize node and children to dictionary.

        Returns:
            Nested dictionary representation of thought tree
        """
        return {
            "thought": self.thought,
            "depth": self.depth,
            "score": self.score,
            "path_score": self.path_score,
            "children": [c.to_dict() for c in self.children]
        }


@dataclass
class LogicRule:
    """
    Logical rule for Logic of Thoughts (LoT).

    WHY: Formal representation of logical deductions and inferences
    RESPONSIBILITY: Store premise-conclusion pairs with rule types
    """
    premise: str
    conclusion: str
    rule_type: str  # deduction, induction, abduction
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize rule to dictionary.

        Returns:
            Dictionary representation of logic rule
        """
        return {
            "premise": self.premise,
            "conclusion": self.conclusion,
            "rule_type": self.rule_type,
            "confidence": self.confidence
        }


class ReasoningStrategyBase(ABC):
    """
    Base class for all reasoning strategies.

    WHY: Template Method pattern provides common interface and structure
    RESPONSIBILITY: Define abstract contract for all reasoning strategies
    PATTERNS: Template Method, Strategy Pattern (abstract base)
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize base reasoning strategy.

        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.steps: List[ReasoningStep] = []

    @abstractmethod
    def generate_prompt(self, task: str, context: Optional[str] = None) -> str:
        """
        Generate prompt with reasoning strategy.

        WHY: Template method forces consistent interface across strategies

        Args:
            task: The task to solve
            context: Optional additional context

        Returns:
            Formatted prompt string
        """
        pass

    @abstractmethod
    def parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM response into structured format.

        WHY: Standardized response parsing across all strategies

        Args:
            response: Raw LLM response text

        Returns:
            Structured dictionary with parsed reasoning
        """
        pass
