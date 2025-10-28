"""
Module: thermodynamic/bayesian_strategy.py

WHY: Bayesian uncertainty estimation with learning from outcomes.
RESPONSIBILITY: Implement Bayesian inference for confidence quantification.
PATTERNS: Strategy Pattern, Observer Pattern, Guard Clauses.

This module handles:
- Bayesian prior/posterior calculations using Beta distribution
- Learning from outcomes (updating priors)
- Entropy calculation for uncertainty quantification
- Event emission for monitoring learning progress

EXTRACTED FROM: thermodynamic_computing.py (lines 364-841, 478 lines)
"""

from typing import Any, Dict, Optional, Tuple
from collections import defaultdict
import math

from thermodynamic.uncertainty_strategy import UncertaintyStrategy
from thermodynamic.models import ConfidenceScore
from thermodynamic.events import ThermodynamicEventType
from pipeline_observer import PipelineObservable, PipelineEvent, EventType
from artemis_exceptions import PipelineException, wrap_exception


class BayesianUncertaintyStrategy(UncertaintyStrategy):
    """
    Bayesian uncertainty estimation with prior updates from outcomes.

    Uses Beta distribution as conjugate prior for Bernoulli outcomes.
    Learns from historical outcomes to improve future predictions via Bayes' theorem.
    
    Mathematical foundation:
    - Prior: Beta(α, β)
    - Posterior mean: α / (α + β)
    - Posterior variance: αβ / [(α+β)²(α+β+1)]
    
    Learning: Success increments α, failure increments β
    """

    def __init__(self, observable: Optional[PipelineObservable] = None):
        """Initialize Bayesian strategy with uniform priors Beta(1,1)"""
        self._priors: Dict[Tuple[str, str], Dict[str, float]] = defaultdict(
            lambda: {"alpha": 1.0, "beta": 1.0}
        )
        self._evidence_counts: Dict[Tuple[str, str], int] = defaultdict(int)
        self.observable = observable

    @wrap_exception(PipelineException, "Bayesian confidence estimation failed")
    def estimate_confidence(
        self,
        prediction: Any,
        context: Dict[str, Any]
    ) -> ConfidenceScore:
        """Estimate confidence using Bayesian posterior"""
        # Extract context for prior lookup
        stage = context.get("stage", "unknown")
        pred_type = context.get("prediction_type", "default")
        key = (stage, pred_type)

        # Retrieve prior
        prior = self._priors[key]
        alpha = prior["alpha"]
        beta = prior["beta"]

        # Calculate Beta distribution statistics
        confidence = alpha / (alpha + beta)
        variance = (alpha * beta) / ((alpha + beta) ** 2 * (alpha + beta + 1))
        entropy = self._calculate_beta_entropy(alpha, beta)
        sample_size = self._evidence_counts[key]

        # Emit event
        self._emit_confidence_event(
            ThermodynamicEventType.CONFIDENCE_CALCULATED,
            confidence,
            context,
            {"alpha": alpha, "beta": beta, "method": "bayesian"}
        )

        return ConfidenceScore(
            confidence=confidence,
            variance=variance,
            entropy=entropy,
            evidence={
                "alpha": alpha,
                "beta": beta,
                "method": "bayesian_posterior",
                "prior_type": "beta_distribution"
            },
            sample_size=sample_size,
            context=context
        )

    @wrap_exception(PipelineException, "Bayesian prior update failed")
    def update_from_outcome(
        self,
        prediction: Any,
        actual: Any,
        context: Dict[str, Any]
    ) -> None:
        """Update Bayesian prior from observed outcome"""
        # Extract context
        stage = context.get("stage", "unknown")
        pred_type = context.get("prediction_type", "default")
        key = (stage, pred_type)

        # Evaluate outcome
        success = self._evaluate_outcome(prediction, actual, context)

        # Bayesian update
        prior = self._priors[key]
        if success:
            prior["alpha"] += 1.0
        else:
            prior["beta"] += 1.0

        # Increment evidence count
        self._evidence_counts[key] += 1

        # Emit event
        self._emit_bayesian_event(
            ThermodynamicEventType.BAYESIAN_PRIOR_UPDATED,
            key,
            prior,
            success,
            context
        )

    def _evaluate_outcome(
        self,
        prediction: Any,
        actual: Any,
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate if prediction matched actual outcome"""
        # Guard: handle None
        if prediction is None or actual is None:
            return False

        # Dispatch table for comparison types
        comparison_type = context.get("comparison_type", "equality")
        
        comparison_methods = {
            "equality": lambda p, a: p == a,
            "threshold": lambda p, a: self._within_threshold(p, a, context),
            "binary": lambda p, a: bool(p) == bool(a),
            "range": lambda p, a: self._in_range(p, a, context)
        }

        comparison_fn = comparison_methods.get(comparison_type, comparison_methods["equality"])
        return comparison_fn(prediction, actual)

    def _within_threshold(
        self,
        prediction: float,
        actual: float,
        context: Dict[str, Any]
    ) -> bool:
        """Check if prediction within threshold of actual"""
        # Guard: avoid division by zero
        if actual == 0:
            return prediction == 0

        threshold_pct = context.get("threshold_percent", 0.10)
        error_pct = abs(prediction - actual) / abs(actual)
        return error_pct <= threshold_pct

    def _in_range(
        self,
        prediction: Any,
        actual: float,
        context: Dict[str, Any]
    ) -> bool:
        """Check if actual value in predicted range"""
        # Guard: validate prediction format
        if not isinstance(prediction, (tuple, list)) or len(prediction) != 2:
            return False

        lower, upper = prediction
        return lower <= actual <= upper

    def _calculate_beta_entropy(self, alpha: float, beta: float) -> float:
        """Calculate entropy of Beta distribution (simplified variance-based approximation)"""
        total = alpha + beta
        variance = (alpha * beta) / ((total ** 2) * (total + 1))
        
        # Normalize to [0, 1] range
        max_variance = 0.25  # Maximum for Beta(1, 1)
        normalized_entropy = variance / max_variance
        return normalized_entropy

    def _emit_confidence_event(
        self,
        event_type: ThermodynamicEventType,
        confidence: float,
        context: Dict[str, Any],
        data: Dict[str, Any]
    ) -> None:
        """Emit confidence-related event"""
        # Guard: check if observable configured
        if not self.observable:
            return

        event_data = {
            "confidence": confidence,
            "strategy": "bayesian",
            **data
        }

        event = PipelineEvent(
            event_type=EventType.STAGE_PROGRESS,
            card_id=context.get("card_id"),
            stage_name=context.get("stage"),
            data={
                "thermodynamic_event": event_type.value,
                **event_data
            }
        )

        self.observable.notify(event)

    def _emit_bayesian_event(
        self,
        event_type: ThermodynamicEventType,
        key: Tuple[str, str],
        prior: Dict[str, float],
        success: bool,
        context: Dict[str, Any]
    ) -> None:
        """Emit Bayesian learning event"""
        # Guard: check if observable configured
        if not self.observable:
            return

        event_data = {
            "thermodynamic_event": event_type.value,
            "stage": key[0],
            "prediction_type": key[1],
            "alpha": prior["alpha"],
            "beta": prior["beta"],
            "success": success,
            "evidence_count": self._evidence_counts[key]
        }

        event = PipelineEvent(
            event_type=EventType.STAGE_PROGRESS,
            card_id=context.get("card_id"),
            stage_name=key[0],
            data=event_data
        )

        self.observable.notify(event)

    def get_priors(self) -> Dict[Tuple[str, str], Dict[str, float]]:
        """Get current Bayesian priors for all contexts"""
        return dict(self._priors)

    def set_prior(
        self,
        stage: str,
        prediction_type: str,
        alpha: float,
        beta: float
    ) -> None:
        """Manually set prior for a context"""
        # Guard: validate parameters
        if alpha <= 0 or beta <= 0:
            raise ValueError(f"Alpha and beta must be positive, got {alpha}, {beta}")

        key = (stage, prediction_type)
        self._priors[key] = {"alpha": alpha, "beta": beta}


__all__ = [
    "BayesianUncertaintyStrategy"
]
