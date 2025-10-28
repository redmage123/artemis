"""
Module: thermodynamic/uncertainty_strategy.py

WHY: Abstract base class for uncertainty estimation strategies.
RESPONSIBILITY: Define Strategy Pattern interface for different uncertainty quantification methods.
PATTERNS: Strategy Pattern, Abstract Base Class.

This module handles:
- UncertaintyStrategy: Abstract interface for all uncertainty estimators
- estimate_confidence(): Core method for confidence quantification
- update_from_outcome(): Learning from observed outcomes

EXTRACTED FROM: thermodynamic_computing.py (lines 281-362)
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
from thermodynamic.models import ConfidenceScore
from artemis_exceptions import ArtemisException


class UncertaintyStrategy(ABC):
    """
    Abstract base class for uncertainty estimation strategies.

    Why it exists: Defines interface for different uncertainty quantification methods.
    Strategy Pattern allows swapping estimation algorithms at runtime without changing
    client code. Different contexts need different strategies (Bayesian for learning,
    Monte Carlo for simulation, ensemble for voting).

    Design pattern: Strategy Pattern

    Responsibilities:
    - Define interface for uncertainty estimation
    - Provide contract for all concrete strategies
    - Enable runtime strategy swapping

    Implementations:
    - BayesianUncertaintyStrategy: Learn from outcomes, update priors
    - MonteCarloUncertaintyStrategy: Simulate many scenarios
    - EnsembleUncertaintyStrategy: Average multiple models

    Why Strategy Pattern:
    - Different stages need different uncertainty methods
    - Easy to add new strategies without modifying existing code
    - Strategies can be selected based on context/data availability
    - Enables A/B testing of uncertainty estimation methods
    """

    @abstractmethod
    def estimate_confidence(
        self,
        prediction: Any,
        context: Dict[str, Any]
    ) -> ConfidenceScore:
        """
        Estimate confidence for a prediction.

        Why needed: Core method that quantifies uncertainty in predictions/decisions.
        Returns ConfidenceScore with probability, variance, and supporting evidence.

        Args:
            prediction: The prediction/decision to score (LLM output, estimate, etc.)
            context: Context dict with metadata for estimation

        Returns:
            ConfidenceScore with uncertainty quantification

        Raises:
            ArtemisException: If estimation fails

        Edge cases: Must handle missing context gracefully with defaults
        """
        pass

    @abstractmethod
    def update_from_outcome(
        self,
        prediction: Any,
        actual: Any,
        context: Dict[str, Any]
    ) -> None:
        """
        Update strategy from observed outcome (learning).

        Why needed: Enables strategies to learn from experience. Bayesian strategies
        update priors, ensemble strategies adjust weights, etc. Core of "getting
        smarter over time" capability.

        Args:
            prediction: What was predicted
            actual: What actually happened
            context: Context of prediction/outcome

        Raises:
            ArtemisException: If update fails

        Note: Not all strategies learn (e.g., basic confidence intervals), but
              interface requires method for consistency.
        """
        pass


__all__ = [
    "UncertaintyStrategy"
]
