"""
Module: thermodynamic/monte_carlo_strategy.py

WHY: Monte Carlo simulation-based uncertainty estimation.
RESPONSIBILITY: Run simulations to estimate confidence distributions.
PATTERNS: Strategy Pattern, Template Method, Guard Clauses.

This module handles:
- N simulations with random sampling
- Aggregate results into confidence distribution
- Calculate mean, variance, percentiles from simulations
- Emit Monte Carlo events for monitoring

EXTRACTED FROM: thermodynamic_computing_original.py (lines 842-1085, 244 lines)
"""

from typing import Any, Dict, Optional
import math
import random

from thermodynamic.uncertainty_strategy import UncertaintyStrategy
from thermodynamic.models import ConfidenceScore
from thermodynamic.events import ThermodynamicEventType
from pipeline_observer import PipelineObservable, PipelineEvent, EventType
from artemis_exceptions import PipelineException, wrap_exception


class MonteCarloUncertaintyStrategy(UncertaintyStrategy):
    """
    Monte Carlo simulation-based uncertainty estimation.

    Uses simulation to estimate distributions when analytic solutions are intractable.
    Classic Monte Carlo: E[X] ≈ (1/N)Σx_i

    Confidence improves with √N (more samples = better estimate)
    """

    def __init__(
        self,
        n_simulations: int = 1000,
        observable: Optional[PipelineObservable] = None
    ):
        """
        Initialize Monte Carlo strategy.

        Args:
            n_simulations: Number of simulations to run (default 1000)
            observable: Pipeline observable for event emission
        """
        self.n_simulations = n_simulations
        self.observable = observable

    @wrap_exception(PipelineException, "Monte Carlo confidence estimation failed")
    def estimate_confidence(
        self,
        prediction: Any,
        context: Dict[str, Any]
    ) -> ConfidenceScore:
        """
        Estimate confidence via Monte Carlo simulation.

        Runs N simulations, counts successes, calculates statistics.

        Args:
            prediction: Prediction to test
            context: Must contain "simulator_fn" callable

        Returns:
            ConfidenceScore with Monte Carlo statistics
        """
        # Guard: validate simulator function
        simulator_fn = context.get("simulator_fn")
        if not simulator_fn or not callable(simulator_fn):
            raise PipelineException(
                "Monte Carlo requires 'simulator_fn' in context",
                context=context
            )

        # Use context override or default
        n_sims = context.get("n_simulations", self.n_simulations)

        # Emit start event
        self._emit_mc_event(
            ThermodynamicEventType.MONTE_CARLO_STARTED,
            context,
            {"n_simulations": n_sims}
        )

        # Run simulations
        successes = 0
        for i in range(n_sims):
            # Run one simulation
            result = simulator_fn(prediction, context)

            # Count success
            if result:
                successes += 1

            # Emit progress event every 100 iterations
            if (i + 1) % 100 == 0:
                self._emit_mc_event(
                    ThermodynamicEventType.MONTE_CARLO_ITERATION,
                    context,
                    {"iteration": i + 1, "successes_so_far": successes}
                )

        # Calculate statistics
        confidence = successes / n_sims
        variance = confidence * (1 - confidence)  # Bernoulli variance
        entropy = self._calculate_bernoulli_entropy(confidence)

        # Emit completion event
        self._emit_mc_event(
            ThermodynamicEventType.MONTE_CARLO_COMPLETED,
            context,
            {
                "confidence": confidence,
                "successes": successes,
                "n_simulations": n_sims
            }
        )

        return ConfidenceScore(
            confidence=confidence,
            variance=variance,
            entropy=entropy,
            evidence={
                "successes": successes,
                "n_simulations": n_sims,
                "method": "monte_carlo"
            },
            sample_size=n_sims,
            context=context
        )

    def update_from_outcome(
        self,
        prediction: Any,
        actual: Any,
        context: Dict[str, Any]
    ) -> None:
        """
        Update from outcome (no-op for Monte Carlo).

        Monte Carlo doesn't maintain state between calls,
        so no update needed. Each estimate is independent.
        """
        pass  # Monte Carlo is stateless

    def _calculate_bernoulli_entropy(self, p: float) -> float:
        """
        Calculate entropy of Bernoulli distribution.

        Formula: H(X) = -p*log(p) - (1-p)*log(1-p)

        Args:
            p: Probability of success

        Returns:
            Entropy (0 = certain, 1 = maximum uncertainty at p=0.5)
        """
        # Guard: handle edge cases
        if p <= 0 or p >= 1:
            return 0.0  # No uncertainty at extremes

        # Calculate Bernoulli entropy
        entropy = -(p * math.log2(p) + (1 - p) * math.log2(1 - p))

        return entropy

    def _emit_mc_event(
        self,
        event_type: ThermodynamicEventType,
        context: Dict[str, Any],
        data: Dict[str, Any]
    ) -> None:
        """Emit Monte Carlo event"""
        # Guard: check if observable configured
        if not self.observable:
            return

        event_data = {
            "thermodynamic_event": event_type.value,
            "strategy": "monte_carlo",
            **data
        }

        event = PipelineEvent(
            event_type=EventType.STAGE_PROGRESS,
            card_id=context.get("card_id"),
            stage_name=context.get("stage"),
            data=event_data
        )

        self.observable.notify(event)


__all__ = [
    "MonteCarloUncertaintyStrategy"
]
