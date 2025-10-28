#!/usr/bin/env python3
"""
Agile Planning Poker Models

WHY: Defines data structures for Planning Poker estimation process.
Provides type-safe representations of votes, estimation rounds, and feature estimates.

RESPONSIBILITY:
- Define estimation vote structure with agent metadata
- Model estimation rounds and consensus tracking
- Represent complete feature estimates with risk assessment
- Provide Fibonacci scale enumeration for story points

PATTERNS:
- Data Classes: Immutable value objects with automatic methods
- Enums: Type-safe Fibonacci scale values
- Value Objects: Rich domain models with validation
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class EstimationConfig:
    """
    Configuration constants for Planning Poker estimation

    WHY: Centralize magic numbers into named constants for maintainability
    """
    HOURS_PER_SPRINT = 40  # Standard 40-hour work week
    HEARTBEAT_INTERVAL_MS = 10  # Observer update interval
    ROUND_PENALTY_FACTOR = 0.1  # Confidence penalty per additional round
    FORCED_CONSENSUS_PENALTY = 0.2  # Confidence penalty for forced consensus
    HIGH_RISK_POINTS_THRESHOLD = 13  # Story points triggering high risk
    MEDIUM_RISK_POINTS_THRESHOLD = 8  # Story points triggering medium risk
    HIGH_RISK_CONFIDENCE_THRESHOLD = 0.6  # Confidence below this = high risk
    MEDIUM_RISK_CONFIDENCE_THRESHOLD = 0.7  # Confidence below this = medium risk
    DEFAULT_CONFIDENCE = 0.5  # Default confidence on error
    ERROR_VOTE_POINTS = 5  # Default story points when estimation fails


class FibonacciScale(Enum):
    """
    Fibonacci scale for story points estimation

    WHY: Standard agile estimation scale prevents false precision
    """
    TINY = 1
    SMALL = 2
    MEDIUM = 3
    LARGE = 5
    HUGE = 8
    ENORMOUS = 13
    EPIC = 21
    UNKNOWN = 100  # Too complex to estimate


@dataclass
class EstimationVote:
    """
    Single agent's estimation vote

    WHY: Encapsulates agent's assessment including confidence and concerns
    """
    agent_name: str
    story_points: int
    reasoning: str
    confidence: float  # 0.0 to 1.0
    concerns: List[str]


@dataclass
class EstimationRound:
    """
    Single round of Planning Poker

    WHY: Tracks voting iteration with consensus status and discussion
    """
    round_number: int
    votes: List[EstimationVote]
    consensus_reached: bool
    final_estimate: Optional[int]
    discussion_summary: str


@dataclass
class FeatureEstimate:
    """
    Complete estimation for a feature

    WHY: Final estimation result with confidence and risk metrics
    """
    feature_title: str
    feature_description: str
    rounds: List[EstimationRound]
    final_estimate: int
    confidence: float
    risk_level: str  # "low", "medium", "high"
    estimated_hours: float  # Based on team velocity
