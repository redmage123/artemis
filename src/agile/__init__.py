#!/usr/bin/env python3
"""
Agile Planning Poker Package

WHY: Provides Planning Poker estimation capabilities for AI agent teams.
Implements agile estimation techniques with voting, consensus building,
and risk assessment.

RESPONSIBILITY:
- Export Planning Poker classes and functions
- Provide backward-compatible API
- Define package public interface

PATTERNS:
- Facade Pattern: Simplified package interface
- Explicit Exports: Clear public API definition
"""

from .models import (
    EstimationConfig,
    FibonacciScale,
    EstimationVote,
    EstimationRound,
    FeatureEstimate
)

from .voting_session import VotingSession
from .consensus_builder import ConsensusBuilder
from .estimator import Estimator
from .poker_core import PlanningPoker, estimate_features_batch

__all__ = [
    # Configuration and models
    'EstimationConfig',
    'FibonacciScale',
    'EstimationVote',
    'EstimationRound',
    'FeatureEstimate',

    # Core components
    'VotingSession',
    'ConsensusBuilder',
    'Estimator',
    'PlanningPoker',

    # Utility functions
    'estimate_features_batch',
]

__version__ = '1.0.0'
