#!/usr/bin/env python3
"""
WHY: Immutable data structures for supervisor learning system
RESPONSIBILITY: Define data models for unexpected states, learned solutions, and learning strategies
PATTERNS: Data Transfer Object (DTO), Value Object, Strategy (via LearningStrategy enum)
"""

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, Any


class LearningStrategy(Enum):
    """
    WHY: Type-safe enumeration of learning approaches
    RESPONSIBILITY: Define available learning strategy types
    PATTERNS: Strategy pattern - defines different learning approaches
    """
    LLM_CONSULTATION = "llm_consultation"      # Ask LLM for solution
    SIMILAR_CASE_ADAPTATION = "similar_case"   # Adapt from similar past cases
    HUMAN_IN_LOOP = "human_in_loop"            # Ask human for guidance
    EXPERIMENTAL_TRIAL = "experimental"        # Try experimental solutions


@dataclass
class UnexpectedState:
    """
    WHY: Capture complete context of unexpected system states for analysis
    RESPONSIBILITY: Store all information needed to diagnose and recover from unexpected state
    PATTERNS: Value Object - immutable representation of unexpected state

    Design: Includes state transition info, error context, and severity assessment
    """
    state_id: str
    timestamp: str
    card_id: str
    stage_name: Optional[str]
    error_message: Optional[str]
    context: Dict[str, Any]
    stack_trace: Optional[str]
    previous_state: Optional[str]
    current_state: str
    expected_states: List[str]  # What states were expected
    severity: str  # low, medium, high, critical

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)


@dataclass
class LearnedSolution:
    """
    WHY: Encapsulate learned recovery solutions with success tracking
    RESPONSIBILITY: Store solution details, workflow steps, and performance metrics
    PATTERNS: Value Object with mutable success tracking

    Design: Tracks success rate to enable confidence-based solution selection
    """
    solution_id: str
    timestamp: str
    unexpected_state_id: str
    problem_description: str
    solution_description: str
    workflow_steps: List[Dict[str, Any]]
    success_rate: float
    times_applied: int
    times_successful: int
    learning_strategy: str
    llm_model_used: Optional[str]
    human_validated: bool
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)

    def update_success_metrics(self, succeeded: bool) -> None:
        """
        WHY: Track solution effectiveness over time
        RESPONSIBILITY: Update success rate based on application results
        """
        self.times_applied += 1
        if succeeded:
            self.times_successful += 1
        self.success_rate = self.times_successful / self.times_applied if self.times_applied > 0 else 0.0
