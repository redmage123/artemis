#!/usr/bin/env python3
"""
Planning Poker - Backward Compatibility Wrapper

WHY: Maintains backward compatibility with existing code while delegating
to modular agile package implementation.

RESPONSIBILITY:
- Re-export all Planning Poker classes and functions
- Preserve original API surface
- Delegate implementation to agile package

PATTERNS:
- Facade Pattern: Thin wrapper over modular implementation
- Proxy Pattern: Transparent delegation to new modules

MIGRATION PATH:
Old import: from planning_poker import PlanningPoker
New import: from agile import PlanningPoker

This wrapper allows gradual migration without breaking existing code.
"""

# Import everything from the modular agile package
from agile import (
    EstimationConfig,
    FibonacciScale,
    EstimationVote,
    EstimationRound,
    FeatureEstimate,
    VotingSession,
    ConsensusBuilder,
    Estimator,
    PlanningPoker,
    estimate_features_batch
)

# Re-export all symbols for backward compatibility
__all__ = [
    'EstimationConfig',
    'FibonacciScale',
    'EstimationVote',
    'EstimationRound',
    'FeatureEstimate',
    'VotingSession',
    'ConsensusBuilder',
    'Estimator',
    'PlanningPoker',
    'estimate_features_batch',
]
