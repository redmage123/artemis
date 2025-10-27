#!/usr/bin/env python3
"""
Module: thermodynamic_computing.py

Purpose: Implements Thermodynamic Computing-inspired probabilistic reasoning for Artemis pipeline
Why: Applies statistical thermodynamics concepts (entropy, ensemble averaging, Bayesian updates,
     stochastic sampling) to software engineering. Quantifies uncertainty in LLM outputs, uses
     probabilistic planning for better estimates, learns from outcomes via Bayesian inference,
     and employs temperature-based exploration in code generation. This transforms deterministic
     "one solution" thinking into probabilistic "distribution of solutions" reasoning.

Thermodynamic Computing Analogy:
    Classical Computing    → Thermodynamic Computing
    Deterministic          → Probabilistic
    Single solution        → Ensemble of solutions
    Binary (works/fails)   → Confidence distribution
    Fixed strategy         → Temperature-based exploration
    No learning            → Bayesian prior updates
    Ignore uncertainty     → Quantify & propagate uncertainty

Why Thermodynamic Concepts in Software:
    1. Uncertainty Quantification: LLMs are probabilistic - we should measure confidence
    2. Ensemble Methods: Multiple solutions better than single solution (wisdom of crowds)
    3. Temperature Sampling: High temp = exploration, low temp = exploitation
    4. Bayesian Learning: Update priors based on outcomes (get smarter over time)
    5. Monte Carlo Planning: Simulate many paths to estimate effort/risk
    6. Entropy Minimization: Information gain guides next action
    7. Risk Assessment: Propagate uncertainty through decision pipeline

Design Patterns:
    - Strategy Pattern: Different uncertainty estimation strategies (Bayesian, ensemble, MC)
    - Observer Pattern: Emit confidence tracking events to pipeline observers
    - Visitor Pattern: Propagate uncertainty through pipeline stages
    - Decorator Pattern: Add uncertainty tracking to existing methods
    - Factory Pattern: Create uncertainty estimators for different contexts
    - Template Method: Common structure for all uncertainty strategies

Integration with Artemis:
    - Hooks into pipeline_observer.py for event emission
    - Uses artemis_exceptions.py @wrap_exception for error handling
    - Integrates with LLM calls to add confidence scores
    - Provides uncertainty-aware decision making for supervisor
    - Learns from retrospective data to improve estimates

Mathematical Foundations:
    - Bayesian Inference: P(θ|D) = P(D|θ)P(θ) / P(D) for prior updates
    - Monte Carlo: Estimate E[X] ≈ (1/N)Σx_i for effort/risk
    - Confidence Intervals: μ ± z*σ/√n for estimation bounds
    - Entropy: H(X) = -Σp(x)log(p(x)) for information gain
    - Temperature: P(x) ∝ exp(-E(x)/T) for exploration/exploitation
    - Ensemble: Majority vote or weighted average across models

Architecture:
    UncertaintyStrategy (abstract)
    ├── BayesianUncertaintyStrategy (learn from outcomes)
    ├── MonteCarloUncertaintyStrategy (simulation-based)
    ├── EnsembleUncertaintyStrategy (multiple models)
    └── ConfidenceIntervalStrategy (statistical bounds)

    ThermodynamicComputing (main facade)
    ├── Uses Strategy Pattern for uncertainty estimation
    ├── Implements Observer for confidence tracking
    ├── Provides Visitor for uncertainty propagation
    └── Emits events for all operations

    Components:
    - ConfidenceScore: Data class for uncertainty representation
    - UncertaintyPropagator: Visitor for propagating through stages
    - TemperatureScheduler: Annealing for exploration/exploitation
    - BayesianPriorManager: Learn from historical data
    - RiskAssessor: Quantify decision uncertainty
    - MonteCarloSimulator: Effort/timeline estimation
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable, Tuple
from datetime import datetime
from enum import Enum
import math
import random
from collections import defaultdict

# Artemis imports
from pipeline_observer import PipelineObserver, PipelineEvent, EventType, PipelineObservable
from artemis_exceptions import (
    ArtemisException,
    PipelineException,
    wrap_exception
)
from advanced_features_ai_mixin import AdvancedFeaturesAIMixin


# ============================================================================
# CONFIDENCE SCORE DATA MODEL
# ============================================================================

@dataclass
class ConfidenceScore:
    """
    Represents uncertainty quantification for a prediction/decision.

    Why it exists: Central data structure for representing probabilistic information.
    Instead of binary "works/fails", we track confidence, variance, entropy, and
    evidence strength to enable uncertainty-aware decision making.

    Design pattern: Value Object (immutable after creation)

    Responsibilities:
    - Store confidence as probability in [0, 1]
    - Track variance/uncertainty in estimate
    - Record entropy for information content
    - Maintain evidence supporting confidence
    - Preserve timestamp and context

    Thermodynamic interpretation:
    - confidence: Probability of state (like Boltzmann distribution)
    - variance: Spread of ensemble (uncertainty quantification)
    - entropy: Information content H(X) = -Σp(x)log(p(x))
    - sample_size: Ensemble size for averaging

    Usage:
        score = ConfidenceScore(
            confidence=0.85,
            variance=0.02,
            entropy=0.234,
            evidence={"test_results": "8/10 passed"},
            sample_size=10
        )
    """
    confidence: float  # Probability in [0, 1]
    variance: float = 0.0  # Uncertainty in estimate
    entropy: float = 0.0  # Information content
    evidence: Dict[str, Any] = field(default_factory=dict)  # Supporting data
    sample_size: int = 1  # Number of samples averaged
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)  # Where score came from

    def __post_init__(self):
        """
        Validate confidence score after initialization.

        Why needed: Ensure mathematical validity of probability values.
        Confidence must be valid probability [0, 1], variance non-negative.
        """
        # Guard clause: validate confidence bounds
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be in [0, 1], got {self.confidence}")

        # Guard clause: validate variance non-negative
        if self.variance < 0.0:
            raise ValueError(f"Variance must be non-negative, got {self.variance}")

        # Guard clause: validate sample size
        if self.sample_size < 1:
            raise ValueError(f"Sample size must be >= 1, got {self.sample_size}")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for serialization.

        Why needed: Enable storage in logs, databases, and event payloads.

        Returns:
            Dict with all fields as JSON-compatible types
        """
        return {
            "confidence": self.confidence,
            "variance": self.variance,
            "entropy": self.entropy,
            "evidence": self.evidence,
            "sample_size": self.sample_size,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context
        }

    def standard_error(self) -> float:
        """
        Calculate standard error (uncertainty in mean).

        Why needed: Standard error = σ/√n quantifies how precise our estimate is.
        As we gather more samples (n↑), standard error decreases (√n).

        Formula: SE = √(variance / sample_size)

        Returns:
            Standard error of confidence estimate
        """
        # Square root of variance normalized by sample size
        return math.sqrt(self.variance / self.sample_size)

    def confidence_interval(self, z_score: float = 1.96) -> Tuple[float, float]:
        """
        Calculate confidence interval for estimate.

        Why needed: Provides bounds on true value. 95% CI (z=1.96) means
        "we're 95% confident true value is in this range".

        Formula: (μ - z*SE, μ + z*SE)

        Args:
            z_score: Z-score for desired confidence level
                    1.96 = 95% CI, 2.58 = 99% CI, 1.0 = 68% CI

        Returns:
            Tuple of (lower_bound, upper_bound) clamped to [0, 1]

        Edge cases: Clamps bounds to valid probability range [0, 1]
        """
        se = self.standard_error()
        margin = z_score * se

        # Calculate bounds and clamp to [0, 1] probability range
        lower = max(0.0, self.confidence - margin)
        upper = min(1.0, self.confidence + margin)

        return (lower, upper)


# ============================================================================
# EVENT TYPES FOR THERMODYNAMIC COMPUTING
# ============================================================================

class ThermodynamicEventType(Enum):
    """
    Event types for thermodynamic computing operations.

    Why needed: Extends pipeline EventType with thermodynamic-specific events
    for tracking uncertainty, confidence, and probabilistic operations.

    Categories:
    - Confidence: Confidence calculated, updated, threshold events
    - Uncertainty: Uncertainty quantified, propagated
    - Bayesian: Prior updated, posterior calculated
    - Monte Carlo: Simulation started/completed
    - Ensemble: Multiple solutions generated/voted
    - Temperature: Temperature adjusted, annealing scheduled
    - Risk: Risk assessed, threshold exceeded
    """
    # Confidence tracking
    CONFIDENCE_CALCULATED = "thermodynamic_confidence_calculated"
    CONFIDENCE_UPDATED = "thermodynamic_confidence_updated"
    CONFIDENCE_THRESHOLD_EXCEEDED = "thermodynamic_confidence_threshold_exceeded"
    CONFIDENCE_THRESHOLD_FAILED = "thermodynamic_confidence_threshold_failed"

    # Uncertainty quantification
    UNCERTAINTY_QUANTIFIED = "thermodynamic_uncertainty_quantified"
    UNCERTAINTY_PROPAGATED = "thermodynamic_uncertainty_propagated"
    UNCERTAINTY_THRESHOLD_EXCEEDED = "thermodynamic_uncertainty_threshold_exceeded"

    # Bayesian learning
    BAYESIAN_PRIOR_UPDATED = "thermodynamic_bayesian_prior_updated"
    BAYESIAN_POSTERIOR_CALCULATED = "thermodynamic_bayesian_posterior_calculated"
    BAYESIAN_EVIDENCE_ADDED = "thermodynamic_bayesian_evidence_added"

    # Monte Carlo simulation
    MONTE_CARLO_STARTED = "thermodynamic_monte_carlo_started"
    MONTE_CARLO_COMPLETED = "thermodynamic_monte_carlo_completed"
    MONTE_CARLO_ITERATION = "thermodynamic_monte_carlo_iteration"

    # Ensemble methods
    ENSEMBLE_GENERATED = "thermodynamic_ensemble_generated"
    ENSEMBLE_VOTED = "thermodynamic_ensemble_voted"
    ENSEMBLE_CONSENSUS_REACHED = "thermodynamic_ensemble_consensus_reached"

    # Temperature/annealing
    TEMPERATURE_ADJUSTED = "thermodynamic_temperature_adjusted"
    TEMPERATURE_ANNEALING_STARTED = "thermodynamic_temperature_annealing_started"
    TEMPERATURE_ANNEALING_COMPLETED = "thermodynamic_temperature_annealing_completed"

    # Risk assessment
    RISK_ASSESSED = "thermodynamic_risk_assessed"
    RISK_THRESHOLD_EXCEEDED = "thermodynamic_risk_threshold_exceeded"
    RISK_MITIGATION_SUGGESTED = "thermodynamic_risk_mitigation_suggested"


# ============================================================================
# UNCERTAINTY ESTIMATION STRATEGIES
# ============================================================================

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
    - ConfidenceIntervalStrategy: Statistical bounds from samples

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


class BayesianUncertaintyStrategy(UncertaintyStrategy):
    """
    Bayesian uncertainty estimation with prior updates from outcomes.

    Why it exists: Implements Bayesian inference for uncertainty quantification.
    Learns from historical outcomes to improve future predictions. Uses Bayes'
    theorem: P(θ|D) = P(D|θ)P(θ) / P(D) to update beliefs based on evidence.

    Design pattern: Strategy (for UncertaintyStrategy) + Observer (for learning)

    Responsibilities:
    - Maintain Bayesian priors for different prediction types
    - Update priors based on observed outcomes
    - Calculate posterior probabilities for predictions
    - Track evidence strength (how many observations)

    Thermodynamic interpretation:
    - Prior: Initial belief distribution (ensemble state)
    - Likelihood: Evidence from observation (measurement)
    - Posterior: Updated belief (new ensemble state)
    - Evidence count: Sample size for averaging

    Mathematical foundation:
    Bayes' Theorem: P(success|evidence) = P(evidence|success)P(success) / P(evidence)

    For binary outcomes (success/failure):
    - Use Beta distribution for prior (conjugate prior for Bernoulli)
    - Prior: Beta(α, β) where α=successes+1, β=failures+1
    - Posterior mean: α / (α + β)
    - Posterior variance: αβ / [(α+β)²(α+β+1)]

    Why Beta distribution:
    - Conjugate prior for Bernoulli (posterior is also Beta)
    - Naturally bounded to [0, 1] (valid probabilities)
    - Flexible shape (uniform, peaked, skewed)
    - Simple updates: just increment α or β

    Learning example:
    1. Start with prior: Beta(1, 1) = Uniform[0, 1] (no knowledge)
    2. Observe 8 successes, 2 failures
    3. Posterior: Beta(9, 3)
    4. Posterior mean = 9/(9+3) = 0.75 confidence
    5. Next prediction uses Beta(9, 3) as prior
    """

    def __init__(self, observable: Optional[PipelineObservable] = None):
        """
        Initialize Bayesian strategy with default priors.

        Why needed: Sets up prior distributions for different contexts. Starts
        with uniform priors (Beta(1,1)) representing no knowledge. As outcomes
        are observed, priors are updated via update_from_outcome().

        Args:
            observable: Pipeline observable for emitting learning events

        Prior format: {context_key: {"alpha": successes+1, "beta": failures+1}}
        Why alpha/beta start at 1: Beta(1,1) = Uniform[0,1] prior (no assumptions)
        """
        # Dispatch table for priors by context type
        # Key: (stage_name, prediction_type), Value: {alpha, beta}
        self._priors: Dict[Tuple[str, str], Dict[str, float]] = defaultdict(
            lambda: {"alpha": 1.0, "beta": 1.0}  # Uniform prior
        )

        # Track number of observations for each prior
        self._evidence_counts: Dict[Tuple[str, str], int] = defaultdict(int)

        self.observable = observable

    @wrap_exception(PipelineException, "Bayesian confidence estimation failed")
    def estimate_confidence(
        self,
        prediction: Any,
        context: Dict[str, Any]
    ) -> ConfidenceScore:
        """
        Estimate confidence using Bayesian posterior.

        What it does:
        1. Extract context key (stage, prediction type)
        2. Retrieve prior distribution Beta(α, β)
        3. Calculate posterior mean: μ = α / (α + β)
        4. Calculate posterior variance: σ² = αβ / [(α+β)²(α+β+1)]
        5. Calculate entropy: measure of uncertainty
        6. Return ConfidenceScore with all statistics

        Args:
            prediction: Prediction to score
            context: Must contain "stage" and optionally "prediction_type"

        Returns:
            ConfidenceScore with Bayesian posterior statistics

        Raises:
            PipelineException: If context missing required keys

        Why posterior mean: Best single-point estimate from Beta distribution
        Why variance: Quantifies spread/uncertainty in estimate
        """
        # Extract context for prior lookup
        stage = context.get("stage", "unknown")
        pred_type = context.get("prediction_type", "default")
        key = (stage, pred_type)

        # Retrieve prior (defaults to Beta(1,1) if not seen before)
        prior = self._priors[key]
        alpha = prior["alpha"]
        beta = prior["beta"]

        # Calculate Beta distribution statistics
        # Posterior mean (expected value of Beta distribution)
        confidence = alpha / (alpha + beta)

        # Posterior variance (spread of Beta distribution)
        variance = (alpha * beta) / (
            (alpha + beta) ** 2 * (alpha + beta + 1)
        )

        # Entropy of Beta distribution (uncertainty measure)
        # High entropy = high uncertainty, low entropy = confident
        entropy = self._calculate_beta_entropy(alpha, beta)

        # Get evidence count
        sample_size = self._evidence_counts[key]

        # Emit confidence calculated event
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
        """
        Update Bayesian prior from observed outcome.

        What it does:
        1. Determine if prediction was correct (success=True/False)
        2. Retrieve current prior Beta(α, β)
        3. Update: α += 1 if success, β += 1 if failure
        4. Store updated prior for future predictions
        5. Increment evidence count
        6. Emit prior update event

        Why this works:
        Beta-Bernoulli conjugacy: If prior is Beta(α, β) and we observe
        success, posterior is Beta(α+1, β). For failure, Beta(α, β+1).
        This is mathematically exact Bayesian update.

        Args:
            prediction: What was predicted
            actual: What actually happened
            context: Context dict with stage/prediction_type

        Raises:
            PipelineException: If outcome comparison fails

        Learning example:
        - Current prior: Beta(5, 3) → confidence = 5/8 = 0.625
        - Observe success: Beta(6, 3) → confidence = 6/9 = 0.667
        - Observe failure: Beta(5, 4) → confidence = 5/9 = 0.556
        """
        # Extract context for prior lookup
        stage = context.get("stage", "unknown")
        pred_type = context.get("prediction_type", "default")
        key = (stage, pred_type)

        # Determine if prediction was correct
        success = self._evaluate_outcome(prediction, actual, context)

        # Retrieve current prior
        prior = self._priors[key]

        # Bayesian update: increment alpha for success, beta for failure
        if success:
            prior["alpha"] += 1.0
        else:
            prior["beta"] += 1.0

        # Increment evidence count
        self._evidence_counts[key] += 1

        # Emit prior update event
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
        """
        Evaluate if prediction matched actual outcome.

        Why needed: Different prediction types need different comparison logic.
        Binary predictions use ==, continuous predictions use threshold, etc.

        Args:
            prediction: Predicted value
            actual: Actual value
            context: May contain "comparison_type" for custom logic

        Returns:
            True if prediction was correct, False otherwise

        Edge cases:
        - For continuous values, checks if within threshold (default ±10%)
        - For None values, returns False
        - For unknown types, uses equality
        """
        # Guard clause: handle None values
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

        # Use dispatch table instead of elif chain
        comparison_fn = comparison_methods.get(
            comparison_type,
            comparison_methods["equality"]  # Default to equality
        )

        return comparison_fn(prediction, actual)

    def _within_threshold(
        self,
        prediction: float,
        actual: float,
        context: Dict[str, Any]
    ) -> bool:
        """
        Check if prediction within threshold of actual.

        Why needed: Continuous predictions shouldn't require exact match.
        For estimates (effort, time), being within 10% is often "correct".

        Args:
            prediction: Predicted value
            actual: Actual value
            context: May contain "threshold_percent" (default 10%)

        Returns:
            True if |prediction - actual| / actual < threshold
        """
        # Guard clause: avoid division by zero
        if actual == 0:
            return prediction == 0

        threshold_pct = context.get("threshold_percent", 0.10)  # 10% default
        error_pct = abs(prediction - actual) / abs(actual)

        return error_pct <= threshold_pct

    def _in_range(
        self,
        prediction: float,
        actual: float,
        context: Dict[str, Any]
    ) -> bool:
        """
        Check if actual value in predicted range.

        Why needed: For interval predictions like confidence intervals.

        Args:
            prediction: Tuple of (lower, upper) bounds
            actual: Actual value
            context: Context dict

        Returns:
            True if actual in [lower, upper]
        """
        # Guard clause: validate prediction is tuple/list
        if not isinstance(prediction, (tuple, list)) or len(prediction) != 2:
            return False

        lower, upper = prediction
        return lower <= actual <= upper

    def _calculate_beta_entropy(self, alpha: float, beta: float) -> float:
        """
        Calculate entropy of Beta distribution.

        Why needed: Entropy quantifies uncertainty. High entropy = uncertain,
        low entropy = confident. Used to guide exploration (high entropy =
        need more data) vs exploitation (low entropy = confident).

        Formula: H(Beta(α,β)) ≈ -log(max(p)) where max happens at (α-1)/(α+β-2)
        For uniform Beta(1,1): H ≈ 0 (maximum entropy)
        For peaked Beta(10,2): H ≈ -0.8 (low entropy, confident)

        Args:
            alpha: Beta distribution alpha parameter
            beta: Beta distribution beta parameter

        Returns:
            Entropy estimate (higher = more uncertain)

        Note: Simplified entropy calculation. Full Beta entropy requires
              polygamma functions which are expensive to compute.
        """
        # Simplified entropy: variance-based approximation
        # Higher variance = higher entropy
        total = alpha + beta
        variance = (alpha * beta) / ((total ** 2) * (total + 1))

        # Normalize to [0, 1] range for interpretability
        # Maximum variance is 0.25 (for Beta(1, 1))
        max_variance = 0.25
        normalized_entropy = variance / max_variance

        return normalized_entropy

    def _emit_confidence_event(
        self,
        event_type: ThermodynamicEventType,
        confidence: float,
        context: Dict[str, Any],
        data: Dict[str, Any]
    ) -> None:
        """
        Emit confidence-related event to pipeline observers.

        Why needed: Allows monitoring/logging of confidence calculations.
        Observers can track confidence over time, alert on low confidence, etc.

        Args:
            event_type: Type of confidence event
            confidence: Confidence value
            context: Context of confidence calculation
            data: Additional event data
        """
        # Guard clause: check if observable is configured
        if not self.observable:
            return

        # Create event data payload
        event_data = {
            "confidence": confidence,
            "strategy": "bayesian",
            **data
        }

        # Create and emit pipeline event
        # Note: Using custom event type, not standard EventType
        event = PipelineEvent(
            event_type=EventType.STAGE_PROGRESS,  # Map to existing type
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
        """
        Emit Bayesian learning event.

        Why needed: Tracks prior updates for monitoring learning progress.

        Args:
            event_type: Type of Bayesian event
            key: (stage, prediction_type) tuple
            prior: Updated prior dict
            success: Whether outcome was success
            context: Context dict
        """
        # Guard clause: check if observable is configured
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
        """
        Get current Bayesian priors for all contexts.

        Why needed: Allows inspection of learned priors for debugging,
        persistence, or transfer learning to new instances.

        Returns:
            Dict mapping (stage, pred_type) to Beta parameters
        """
        return dict(self._priors)

    def set_prior(
        self,
        stage: str,
        prediction_type: str,
        alpha: float,
        beta: float
    ) -> None:
        """
        Manually set prior for a context.

        Why needed: Enables loading learned priors from persistence,
        transfer learning, or expert initialization.

        Args:
            stage: Stage name
            prediction_type: Type of prediction
            alpha: Beta distribution alpha (successes + 1)
            beta: Beta distribution beta (failures + 1)

        Raises:
            ValueError: If alpha or beta invalid
        """
        # Guard clauses: validate parameters
        if alpha <= 0 or beta <= 0:
            raise ValueError(f"Alpha and beta must be positive, got {alpha}, {beta}")

        key = (stage, prediction_type)
        self._priors[key] = {"alpha": alpha, "beta": beta}


class MonteCarloUncertaintyStrategy(UncertaintyStrategy):
    """
    Monte Carlo simulation-based uncertainty estimation.

    Why it exists: Uses simulation to estimate distributions of outcomes.
    When analytic solutions are intractable, run many random simulations
    and aggregate results. Classic Monte Carlo: E[X] ≈ (1/N)Σx_i.

    Design pattern: Strategy + Template Method

    Responsibilities:
    - Run N simulations with random sampling
    - Aggregate results into confidence distribution
    - Calculate mean, variance, percentiles
    - Provide risk assessment from simulation results

    Thermodynamic interpretation:
    - Each simulation: Sample from ensemble
    - Aggregation: Ensemble averaging
    - Variance: Spread of ensemble states
    - Percentiles: Probability distribution of outcomes

    Use cases:
    - Effort estimation: Simulate many development paths
    - Timeline prediction: Sample from duration distributions
    - Risk assessment: Simulate failure modes
    - Feature complexity: Sample from complexity distributions

    Why Monte Carlo:
    - Works when analytic solutions impossible
    - Naturally handles complex dependencies
    - Provides full distribution, not just point estimate
    - Confidence improves with √N (more samples = better estimate)
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

        Why 1000 default: Standard error decreases as 1/√N.
        For N=1000, SE ≈ 0.03 (3% precision), good balance of speed/accuracy.
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

        What it does:
        1. Run N simulations with random sampling
        2. Count successes (simulations matching prediction)
        3. Calculate confidence = successes / N
        4. Calculate variance of Bernoulli: p(1-p)
        5. Calculate entropy: -p*log(p) - (1-p)*log(1-p)
        6. Return ConfidenceScore with simulation statistics

        Args:
            prediction: Prediction to test (passed to simulator)
            context: Must contain "simulator_fn" callable for running simulations

        Returns:
            ConfidenceScore with Monte Carlo statistics

        Raises:
            PipelineException: If simulator_fn missing or fails

        Context requirements:
        - simulator_fn: Callable that runs one simulation, returns success/failure
        - Optional: n_simulations to override default
        """
        # Guard clause: validate simulator function provided
        simulator_fn = context.get("simulator_fn")
        if not simulator_fn or not callable(simulator_fn):
            raise PipelineException(
                "Monte Carlo requires 'simulator_fn' in context",
                context=context
            )

        # Use context override or default n_simulations
        n_sims = context.get("n_simulations", self.n_simulations)

        # Emit Monte Carlo start event
        self._emit_mc_event(
            ThermodynamicEventType.MONTE_CARLO_STARTED,
            context,
            {"n_simulations": n_sims}
        )

        # Run simulations
        successes = 0
        simulation_results = []

        for i in range(n_sims):
            # Run one simulation
            result = simulator_fn(prediction, context)
            success = bool(result)

            if success:
                successes += 1

            simulation_results.append(success)

            # Emit periodic progress (every 10%)
            if (i + 1) % max(1, n_sims // 10) == 0:
                self._emit_mc_event(
                    ThermodynamicEventType.MONTE_CARLO_ITERATION,
                    context,
                    {"iteration": i + 1, "total": n_sims}
                )

        # Calculate statistics
        confidence = successes / n_sims  # Empirical probability

        # Variance of Bernoulli: p(1-p)/n
        variance = (confidence * (1 - confidence)) / n_sims

        # Binary entropy: H(p) = -p*log(p) - (1-p)*log(1-p)
        entropy = self._calculate_binary_entropy(confidence)

        # Emit completion event
        self._emit_mc_event(
            ThermodynamicEventType.MONTE_CARLO_COMPLETED,
            context,
            {
                "confidence": confidence,
                "successes": successes,
                "total": n_sims
            }
        )

        return ConfidenceScore(
            confidence=confidence,
            variance=variance,
            entropy=entropy,
            evidence={
                "successes": successes,
                "trials": n_sims,
                "method": "monte_carlo",
                "simulation_results": simulation_results[:100]  # Keep first 100
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
        Monte Carlo doesn't learn from outcomes (stateless).

        Why needed: Interface consistency. Monte Carlo recalculates fresh
        each time, doesn't maintain priors like Bayesian strategy.

        Args:
            prediction: Ignored
            actual: Ignored
            context: Ignored

        Note: This is a valid design choice. Monte Carlo strength is
              no-assumptions simulation, not learning from history.
        """
        # Monte Carlo is stateless - no learning from outcomes
        pass

    def _calculate_binary_entropy(self, p: float) -> float:
        """
        Calculate binary entropy H(p) = -p*log(p) - (1-p)*log(1-p).

        Why needed: Entropy quantifies uncertainty. For probability p:
        - p=0.5: Maximum entropy (1.0) - most uncertain
        - p=0 or p=1: Minimum entropy (0.0) - certain
        - p=0.1 or p=0.9: Medium entropy - fairly confident

        Args:
            p: Probability in [0, 1]

        Returns:
            Entropy in [0, 1] range

        Edge cases: Returns 0 for p=0 or p=1 (certain outcomes)
        """
        # Guard clauses: handle edge cases where log undefined
        if p <= 0 or p >= 1:
            return 0.0

        # Binary entropy formula
        entropy = -(p * math.log2(p) + (1 - p) * math.log2(1 - p))

        return entropy

    def _emit_mc_event(
        self,
        event_type: ThermodynamicEventType,
        context: Dict[str, Any],
        data: Dict[str, Any]
    ) -> None:
        """
        Emit Monte Carlo event to observers.

        Why needed: Allows monitoring simulation progress, especially for
        long-running simulations (N > 10000).

        Args:
            event_type: Type of Monte Carlo event
            context: Context dict
            data: Event data
        """
        # Guard clause: check if observable configured
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


class EnsembleUncertaintyStrategy(UncertaintyStrategy):
    """
    Ensemble-based uncertainty via multiple model voting.

    Why it exists: Wisdom of crowds - multiple independent models often
    outperform single model. Disagreement between models indicates uncertainty.
    Agreement indicates confidence.

    Design pattern: Strategy + Composite

    Responsibilities:
    - Generate predictions from multiple models
    - Aggregate via voting (classification) or averaging (regression)
    - Calculate confidence from agreement level
    - Track individual model performance for weighting

    Thermodynamic interpretation:
    - Each model: State in ensemble
    - Voting: Ensemble averaging
    - Disagreement: High entropy state (uncertainty)
    - Agreement: Low entropy state (confidence)

    Why ensemble works:
    - Reduces variance: Average of N models has variance σ²/N
    - Reduces bias: Different models have different biases
    - Robustness: No single point of failure
    - Uncertainty quantification: Disagreement = low confidence

    Ensemble types:
    - Bagging: Bootstrap samples, average results
    - Boosting: Sequential models correct previous errors
    - Stacking: Meta-model combines base models
    - Voting: Simple majority or weighted voting

    This implementation: Simple voting with optional weighting
    """

    def __init__(
        self,
        model_generators: List[Callable] = None,
        weights: Optional[List[float]] = None,
        observable: Optional[PipelineObservable] = None
    ):
        """
        Initialize ensemble strategy.

        Args:
            model_generators: List of callables that generate predictions
                             Each: fn(input, context) -> prediction
            weights: Optional weights for each model (default: equal weighting)
            observable: Pipeline observable for events

        Raises:
            ValueError: If weights length doesn't match generators length
        """
        self.model_generators = model_generators or []
        self.weights = weights

        # Guard clause: validate weights match generators
        if self.weights is not None:
            if len(self.weights) != len(self.model_generators):
                raise ValueError(
                    f"Weights length ({len(self.weights)}) must match "
                    f"generators length ({len(self.model_generators)})"
                )

        # If no weights, use equal weighting
        if self.weights is None and self.model_generators:
            self.weights = [1.0 / len(self.model_generators)] * len(self.model_generators)

        self.observable = observable

        # Track model performance for adaptive weighting
        self._model_performance: List[Dict[str, int]] = [
            {"correct": 0, "total": 0} for _ in self.model_generators
        ]

    @wrap_exception(PipelineException, "Ensemble confidence estimation failed")
    def estimate_confidence(
        self,
        prediction: Any,
        context: Dict[str, Any]
    ) -> ConfidenceScore:
        """
        Estimate confidence via ensemble voting.

        What it does:
        1. Generate predictions from all models
        2. Calculate agreement with main prediction
        3. Confidence = weighted agreement %
        4. Variance from disagreement spread
        5. Entropy from prediction distribution

        Args:
            prediction: Reference prediction to compare against
            context: Context for model generators

        Returns:
            ConfidenceScore with ensemble statistics

        Raises:
            PipelineException: If no model generators configured

        Algorithm:
        - For each model, generate prediction
        - Compare to reference prediction
        - Confidence = Σ(weight_i * agreement_i) / Σ(weight_i)
        """
        # Guard clause: require at least one model
        if not self.model_generators:
            raise PipelineException(
                "Ensemble requires at least one model generator",
                context=context
            )

        # Emit ensemble generation start
        self._emit_ensemble_event(
            ThermodynamicEventType.ENSEMBLE_GENERATED,
            context,
            {"n_models": len(self.model_generators)}
        )

        # Generate predictions from all models
        model_predictions = []
        agreements = []

        for i, generator in enumerate(self.model_generators):
            # Generate prediction from this model
            model_pred = generator(prediction, context)
            model_predictions.append(model_pred)

            # Check agreement with reference prediction
            agrees = self._check_agreement(model_pred, prediction, context)
            agreements.append(agrees)

        # Calculate weighted confidence
        weighted_agreement = sum(
            w * agrees for w, agrees in zip(self.weights, agreements)
        )
        total_weight = sum(self.weights)
        confidence = weighted_agreement / total_weight

        # Calculate variance from disagreement
        agreement_variance = self._calculate_agreement_variance(agreements, self.weights)

        # Calculate entropy from prediction distribution
        entropy = self._calculate_prediction_entropy(model_predictions)

        # Emit voting event
        self._emit_ensemble_event(
            ThermodynamicEventType.ENSEMBLE_VOTED,
            context,
            {
                "confidence": confidence,
                "agreements": agreements,
                "n_models": len(model_predictions)
            }
        )

        return ConfidenceScore(
            confidence=confidence,
            variance=agreement_variance,
            entropy=entropy,
            evidence={
                "n_models": len(model_predictions),
                "agreements": agreements,
                "method": "ensemble_voting",
                "model_predictions": model_predictions[:10]  # Keep first 10
            },
            sample_size=len(model_predictions),
            context=context
        )

    @wrap_exception(PipelineException, "Ensemble outcome update failed")
    def update_from_outcome(
        self,
        prediction: Any,
        actual: Any,
        context: Dict[str, Any]
    ) -> None:
        """
        Update model weights based on observed outcome.

        What it does:
        1. Regenerate predictions from all models
        2. Check which models were correct
        3. Update performance tracking
        4. Optionally adjust weights (adaptive weighting)

        Args:
            prediction: Original prediction (not used directly)
            actual: Actual outcome
            context: Context for model generators

        Why update weights: Models that are frequently correct should
        have higher weight in voting. This is adaptive ensemble learning.
        """
        # Guard clause: require model generators
        if not self.model_generators:
            return

        # Generate predictions from all models with original context
        for i, generator in enumerate(self.model_generators):
            # Generate this model's prediction
            model_pred = generator(prediction, context)

            # Check if model was correct
            correct = self._check_agreement(model_pred, actual, context)

            # Update performance tracking
            if correct:
                self._model_performance[i]["correct"] += 1
            self._model_performance[i]["total"] += 1

        # Optionally update weights based on performance
        if context.get("adaptive_weighting", False):
            self._update_weights_from_performance()

    def _check_agreement(
        self,
        pred1: Any,
        pred2: Any,
        context: Dict[str, Any]
    ) -> bool:
        """
        Check if two predictions agree.

        Why needed: Different prediction types need different comparison.
        Binary: exact match. Continuous: within threshold. Categorical: same class.

        Args:
            pred1: First prediction
            pred2: Second prediction
            context: May contain "comparison_type"

        Returns:
            True if predictions agree
        """
        # Dispatch table for comparison types
        comparison_type = context.get("comparison_type", "equality")

        comparison_methods = {
            "equality": lambda p1, p2: p1 == p2,
            "threshold": lambda p1, p2: self._within_threshold(p1, p2, context),
            "binary": lambda p1, p2: bool(p1) == bool(p2),
            "categorical": lambda p1, p2: str(p1) == str(p2)
        }

        comparison_fn = comparison_methods.get(
            comparison_type,
            comparison_methods["equality"]
        )

        return comparison_fn(pred1, pred2)

    def _within_threshold(
        self,
        val1: float,
        val2: float,
        context: Dict[str, Any]
    ) -> bool:
        """Check if values within threshold (for continuous predictions)."""
        threshold = context.get("threshold", 0.1)  # 10% default

        # Guard clause: handle zero values
        if val2 == 0:
            return val1 == 0

        error = abs(val1 - val2) / abs(val2)
        return error <= threshold

    def _calculate_agreement_variance(
        self,
        agreements: List[bool],
        weights: List[float]
    ) -> float:
        """
        Calculate variance of agreement distribution.

        Why needed: Quantifies spread in ensemble predictions.
        All agree = low variance. Half agree = high variance.

        Args:
            agreements: List of boolean agreement indicators
            weights: Model weights

        Returns:
            Weighted variance of agreements
        """
        # Convert agreements to 0/1
        agreement_values = [1.0 if a else 0.0 for a in agreements]

        # Calculate weighted mean
        weighted_mean = sum(
            w * v for w, v in zip(weights, agreement_values)
        ) / sum(weights)

        # Calculate weighted variance
        weighted_variance = sum(
            w * (v - weighted_mean) ** 2
            for w, v in zip(weights, agreement_values)
        ) / sum(weights)

        return weighted_variance

    def _calculate_prediction_entropy(self, predictions: List[Any]) -> float:
        """
        Calculate entropy of prediction distribution.

        Why needed: High entropy = models disagree (uncertain).
        Low entropy = models agree (confident).

        Args:
            predictions: List of predictions from models

        Returns:
            Entropy measure [0, 1]
        """
        # Count unique predictions
        prediction_counts = defaultdict(int)
        for pred in predictions:
            prediction_counts[str(pred)] += 1  # Use string for hashability

        # Calculate probabilities
        n_predictions = len(predictions)
        probabilities = [
            count / n_predictions for count in prediction_counts.values()
        ]

        # Calculate entropy: H = -Σp*log(p)
        entropy = 0.0
        for p in probabilities:
            if p > 0:
                entropy -= p * math.log2(p)

        # Normalize by maximum possible entropy (all different predictions)
        max_entropy = math.log2(n_predictions) if n_predictions > 1 else 1.0
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0

        return normalized_entropy

    def _update_weights_from_performance(self) -> None:
        """
        Update model weights based on historical performance.

        Why needed: Adaptive weighting - models that are frequently correct
        should have higher weight. This is online ensemble learning.

        Algorithm:
        - Weight_i = correct_i / total_i (accuracy)
        - Normalize weights to sum to 1.0
        """
        # Calculate accuracy for each model
        accuracies = []
        for perf in self._model_performance:
            # Guard clause: avoid division by zero
            if perf["total"] == 0:
                accuracies.append(0.0)
            else:
                accuracy = perf["correct"] / perf["total"]
                accuracies.append(accuracy)

        # Normalize to sum to 1.0
        total_accuracy = sum(accuracies)

        # Guard clause: handle case where all models have zero accuracy
        if total_accuracy == 0:
            # Revert to equal weighting
            self.weights = [1.0 / len(self.model_generators)] * len(self.model_generators)
        else:
            self.weights = [acc / total_accuracy for acc in accuracies]

    def _emit_ensemble_event(
        self,
        event_type: ThermodynamicEventType,
        context: Dict[str, Any],
        data: Dict[str, Any]
    ) -> None:
        """Emit ensemble event to observers."""
        # Guard clause: check if observable configured
        if not self.observable:
            return

        event_data = {
            "thermodynamic_event": event_type.value,
            "strategy": "ensemble",
            **data
        }

        event = PipelineEvent(
            event_type=EventType.STAGE_PROGRESS,
            card_id=context.get("card_id"),
            stage_name=context.get("stage"),
            data=event_data
        )

        self.observable.notify(event)

    def add_model(self, generator: Callable, weight: float = None) -> None:
        """
        Add new model to ensemble.

        Why needed: Allows dynamic ensemble construction.

        Args:
            generator: Callable that generates predictions
            weight: Optional weight (default: equal to existing)
        """
        self.model_generators.append(generator)
        self._model_performance.append({"correct": 0, "total": 0})

        # Add weight
        if weight is not None:
            self.weights.append(weight)
        else:
            # Recompute equal weighting
            n_models = len(self.model_generators)
            self.weights = [1.0 / n_models] * n_models


# ============================================================================
# TEMPERATURE SCHEDULER (for exploration/exploitation)
# ============================================================================

class TemperatureScheduler:
    """
    Temperature-based annealing for exploration/exploitation tradeoff.

    Why it exists: Simulated annealing concept from thermodynamics. Start with
    high temperature (explore broadly), gradually cool (exploit best found).
    Temperature controls randomness: high T = random, low T = deterministic.

    Design pattern: Strategy (for different schedules)

    Thermodynamic interpretation:
    - Temperature T: Controls thermal fluctuations
    - High T: System in high-energy state, lots of random motion (exploration)
    - Low T: System in low-energy state, settled to minimum (exploitation)
    - Annealing: Gradual cooling to find global minimum

    Applications in Artemis:
    - Code generation: High T = creative solutions, low T = conservative
    - Solution selection: High T = try new approaches, low T = stick with best
    - Parameter tuning: High T = broad search, low T = fine-tune
    - Developer selection: High T = try new developers, low T = use best

    Boltzmann distribution: P(state) ∝ exp(-E(state) / T)
    - High T: All states nearly equal probability (exploration)
    - Low T: Only low-energy states have significant probability (exploitation)

    Annealing schedules:
    - Linear: T(t) = T_max - (T_max - T_min) * t/t_max
    - Exponential: T(t) = T_max * exp(-α*t)
    - Inverse: T(t) = T_max / (1 + α*t)
    - Step: T decreases in discrete steps
    """

    def __init__(
        self,
        initial_temp: float = 1.0,
        final_temp: float = 0.1,
        schedule: str = "exponential",
        observable: Optional[PipelineObservable] = None
    ):
        """
        Initialize temperature scheduler.

        Args:
            initial_temp: Starting temperature (exploration)
            final_temp: Ending temperature (exploitation)
            schedule: Annealing schedule type
                     "linear", "exponential", "inverse", "step"
            observable: Pipeline observable for events

        Raises:
            ValueError: If temperatures invalid
        """
        # Guard clauses: validate temperature parameters
        if initial_temp <= 0:
            raise ValueError(f"Initial temp must be positive, got {initial_temp}")
        if final_temp <= 0:
            raise ValueError(f"Final temp must be positive, got {final_temp}")
        if final_temp >= initial_temp:
            raise ValueError("Final temp must be less than initial temp")

        self.initial_temp = initial_temp
        self.final_temp = final_temp
        self.schedule = schedule
        self.current_temp = initial_temp
        self.observable = observable

        # Dispatch table for schedule functions
        self._schedule_functions = {
            "linear": self._linear_schedule,
            "exponential": self._exponential_schedule,
            "inverse": self._inverse_schedule,
            "step": self._step_schedule
        }

    def get_temperature(self, step: int, max_steps: int) -> float:
        """
        Get temperature for current step.

        Why needed: Returns current temperature based on annealing schedule.
        Used by sampling functions to control randomness.

        Args:
            step: Current step (0 to max_steps)
            max_steps: Total number of steps

        Returns:
            Temperature at current step

        Raises:
            ValueError: If step or max_steps invalid
        """
        # Guard clauses: validate parameters
        if step < 0:
            raise ValueError(f"Step must be non-negative, got {step}")
        if max_steps <= 0:
            raise ValueError(f"Max steps must be positive, got {max_steps}")
        if step > max_steps:
            raise ValueError(f"Step {step} exceeds max_steps {max_steps}")

        # Get schedule function from dispatch table
        schedule_fn = self._schedule_functions.get(
            self.schedule,
            self._schedule_functions["exponential"]  # Default
        )

        # Calculate temperature
        temperature = schedule_fn(step, max_steps)

        # Update current temperature
        self.current_temp = temperature

        # Emit temperature update event
        self._emit_temperature_event(step, max_steps, temperature)

        return temperature

    def _linear_schedule(self, step: int, max_steps: int) -> float:
        """
        Linear annealing: T(t) = T_max - (T_max - T_min) * t/t_max

        Why: Simplest schedule, constant cooling rate.

        Args:
            step: Current step
            max_steps: Total steps

        Returns:
            Temperature at step
        """
        progress = step / max_steps
        temp = self.initial_temp - (self.initial_temp - self.final_temp) * progress
        return max(self.final_temp, temp)

    def _exponential_schedule(self, step: int, max_steps: int) -> float:
        """
        Exponential annealing: T(t) = T_max * (T_min/T_max)^(t/t_max)

        Why: Fast cooling early, slow cooling late. Mimics physical annealing.

        Args:
            step: Current step
            max_steps: Total steps

        Returns:
            Temperature at step
        """
        progress = step / max_steps
        ratio = self.final_temp / self.initial_temp
        temp = self.initial_temp * (ratio ** progress)
        return max(self.final_temp, temp)

    def _inverse_schedule(self, step: int, max_steps: int) -> float:
        """
        Inverse annealing: T(t) = T_max / (1 + α*t)

        Why: Slower cooling than exponential, maintains exploration longer.

        Args:
            step: Current step
            max_steps: Total steps

        Returns:
            Temperature at step
        """
        # Calculate α such that T(max_steps) = final_temp
        # T_max / (1 + α*max_steps) = T_min
        # α = (T_max - T_min) / (T_min * max_steps)
        alpha = (self.initial_temp - self.final_temp) / (self.final_temp * max_steps)

        temp = self.initial_temp / (1 + alpha * step)
        return max(self.final_temp, temp)

    def _step_schedule(self, step: int, max_steps: int) -> float:
        """
        Step annealing: Temperature drops in discrete steps.

        Why: Allows extended exploration at each temperature level.

        Args:
            step: Current step
            max_steps: Total steps

        Returns:
            Temperature at step
        """
        # Divide into 10 equal steps
        n_steps = 10
        step_size = max_steps / n_steps
        current_step = int(step / step_size)

        # Linear decrease across steps
        temp_range = self.initial_temp - self.final_temp
        temp_decrease = temp_range / n_steps
        temp = self.initial_temp - (current_step * temp_decrease)

        return max(self.final_temp, temp)

    def sample_with_temperature(
        self,
        options: List[Any],
        scores: List[float],
        temperature: Optional[float] = None
    ) -> Any:
        """
        Sample from options using Boltzmann distribution.

        Why needed: Temperature-controlled sampling. High T = random,
        low T = greedy. Implements: P(option_i) ∝ exp(score_i / T)

        Args:
            options: List of options to choose from
            scores: Score for each option (higher = better)
            temperature: Optional temperature (uses current if None)

        Returns:
            Sampled option

        Raises:
            ValueError: If options/scores length mismatch

        Algorithm:
        1. Calculate probabilities: p_i = exp(score_i / T)
        2. Normalize: p_i = p_i / Σp_i
        3. Sample from categorical distribution
        """
        # Guard clause: validate inputs
        if len(options) != len(scores):
            raise ValueError(
                f"Options ({len(options)}) and scores ({len(scores)}) length mismatch"
            )

        # Guard clause: require at least one option
        if not options:
            raise ValueError("Must provide at least one option")

        # Use provided temperature or current
        temp = temperature if temperature is not None else self.current_temp

        # Calculate Boltzmann probabilities: p_i ∝ exp(score_i / T)
        exp_scores = [math.exp(score / temp) for score in scores]
        total = sum(exp_scores)

        # Normalize to get probability distribution
        probabilities = [exp_score / total for exp_score in exp_scores]

        # Sample from categorical distribution
        selected = random.choices(options, weights=probabilities, k=1)[0]

        return selected

    def _emit_temperature_event(
        self,
        step: int,
        max_steps: int,
        temperature: float
    ) -> None:
        """
        Emit temperature update event.

        Why needed: Allows monitoring of annealing schedule.

        Args:
            step: Current step
            max_steps: Total steps
            temperature: Current temperature
        """
        # Guard clause: check if observable configured
        if not self.observable:
            return

        event_data = {
            "thermodynamic_event": ThermodynamicEventType.TEMPERATURE_ADJUSTED.value,
            "step": step,
            "max_steps": max_steps,
            "temperature": temperature,
            "schedule": self.schedule
        }

        event = PipelineEvent(
            event_type=EventType.STAGE_PROGRESS,
            data=event_data
        )

        self.observable.notify(event)


# ============================================================================
# THERMODYNAMIC COMPUTING FACADE
# ============================================================================

class ThermodynamicComputing(AdvancedFeaturesAIMixin):
    """
    Main facade for thermodynamic computing capabilities.

    Why it exists: Provides unified interface for all uncertainty quantification,
    probabilistic reasoning, and temperature-based features. Hides complexity
    of strategy selection, event emission, and coordination.

    Design pattern: Facade + Strategy + Observer + Mixin (for DRY AI calls)

    NEW: Hybrid AI Approach:
    - Receives initial uncertainty analysis from router (free!)
    - Uses AI service from context for adaptive calls (when needed)
    - Inherits DRY AI query methods from AdvancedFeaturesAIMixin

    Responsibilities:
    - Provide simple API for uncertainty quantification
    - Manage strategy selection and lifecycle
    - Coordinate temperature scheduling
    - Emit events for all operations
    - Integrate with pipeline observer system
    - Make adaptive AI calls for detailed analysis

    Usage:
        # New: Receives context from router
        tc = ThermodynamicComputing(
            context=router_context,
            observable=pipeline_observable
        )

        # Use pre-computed uncertainty (free!)
        initial_uncertainty = tc.initial_uncertainty  # 0.65 from router

        # Quantify uncertainty (uses initial + adaptive AI if needed)
        score = tc.quantify_uncertainty(
            prediction="feature will take 5 days",
            context={"stage": "estimation", "card_id": "TASK-001"},
            strategy="bayesian"
        )

        # Learn from outcome
        tc.learn_from_outcome(
            prediction="5 days",
            actual="7 days",
            context={"stage": "estimation"}
        )

        # Temperature-based sampling
        option = tc.sample_with_temperature(
            options=["conservative", "moderate", "aggressive"],
            scores=[0.8, 0.6, 0.4],
            temperature=0.5
        )

    Integration points:
    - pipeline_observer.py: Emits events for monitoring
    - artemis_exceptions.py: Uses @wrap_exception for errors
    - LLM calls: Via mixin methods + ai_service from context
    - Supervisor: Provides uncertainty-aware decisions
    - Retrospective: Learns from outcomes
    """

    def __init__(
        self,
        context: Optional[Dict[str, Any]] = None,
        observable: Optional[PipelineObservable] = None,
        default_strategy: Optional[str] = None
    ):
        """
        Initialize thermodynamic computing system.

        NEW: Hybrid approach - accepts context from router with initial analysis.

        Args:
            context: Rich context from router containing:
                - uncertainty_level: Pre-computed uncertainty (0.0-1.0)
                - risk_details: Identified risk factors
                - suggested_strategy: Recommended strategy
                - ai_service: AI service reference for adaptive calls
                - prompt: Guidance prompt from router
            observable: Pipeline observable for event emission
            default_strategy: Default uncertainty strategy override
                            "bayesian", "monte_carlo", "ensemble"
                            If None, uses strategy from context

        Raises:
            ValueError: If default_strategy invalid
        """
        self.observable = observable

        # NEW: Extract initial analysis from router context (hybrid approach)
        if context:
            self.context = context
            self.ai_service = context.get('ai_service')  # For adaptive AI calls
            self.initial_uncertainty = context.get('uncertainty_level', 0.5)
            self.router_guidance = context.get('prompt', '')
            self.risk_details = context.get('risk_details', [])
            self.known_unknowns = context.get('known_unknowns', [])

            # Use router's strategy suggestion if no override
            suggested_strategy = context.get('suggested_strategy', 'bayesian')
            self.default_strategy = default_strategy or suggested_strategy
        else:
            # Fallback: No context provided (legacy support)
            self.context = {}
            self.ai_service = None
            self.initial_uncertainty = 0.5
            self.router_guidance = ''
            self.risk_details = []
            self.known_unknowns = []
            self.default_strategy = default_strategy or "bayesian"

        # Initialize strategies (Factory Pattern)
        self._strategies: Dict[str, UncertaintyStrategy] = {
            "bayesian": BayesianUncertaintyStrategy(observable),
            "monte_carlo": MonteCarloUncertaintyStrategy(observable=observable),
            "ensemble": EnsembleUncertaintyStrategy(observable=observable)
        }

        # Validate default strategy
        if self.default_strategy not in self._strategies:
            raise ValueError(
                f"Invalid default strategy: {self.default_strategy}. "
                f"Must be one of {list(self._strategies.keys())}"
            )

        # Initialize temperature scheduler (use config values if available)
        initial_temp = context.get('initial_temperature', 1.0) if context else 1.0
        final_temp = context.get('final_temperature', 0.1) if context else 0.1
        schedule = context.get('temperature_schedule', 'exponential') if context else 'exponential'

        self.temperature_scheduler = TemperatureScheduler(
            initial_temp=initial_temp,
            final_temp=final_temp,
            schedule=schedule,
            observable=observable
        )

        # Track confidence history for analysis
        self._confidence_history: List[Dict[str, Any]] = []

        # Logger for mixin (required by AdvancedFeaturesAIMixin)
        self.logger = None  # Can be set later if logging needed

    @wrap_exception(PipelineException, "Uncertainty quantification failed")
    def quantify_uncertainty(
        self,
        prediction: Any,
        context: Dict[str, Any],
        strategy: Optional[str] = None
    ) -> ConfidenceScore:
        """
        Quantify uncertainty in a prediction.

        What it does:
        1. Select strategy (provided or default)
        2. Estimate confidence using strategy
        3. Record in confidence history
        4. Emit uncertainty quantified event
        5. Return ConfidenceScore

        Args:
            prediction: Prediction to quantify uncertainty for
            context: Context dict with metadata
            strategy: Strategy to use (optional, uses default if None)
                     "bayesian", "monte_carlo", "ensemble"

        Returns:
            ConfidenceScore with uncertainty quantification

        Raises:
            PipelineException: If strategy invalid or estimation fails

        Usage:
            score = tc.quantify_uncertainty(
                prediction=llm_output,
                context={
                    "stage": "architecture",
                    "card_id": "TASK-001",
                    "prediction_type": "code_quality"
                },
                strategy="bayesian"
            )
        """
        # Select strategy using dispatch table (no if/elif)
        strategy_name = strategy or self.default_strategy
        uncertainty_strategy = self._strategies.get(strategy_name)

        # Guard clause: validate strategy exists
        if not uncertainty_strategy:
            raise PipelineException(
                f"Unknown uncertainty strategy: {strategy_name}",
                context={"available_strategies": list(self._strategies.keys())}
            )

        # Estimate confidence using strategy
        confidence_score = uncertainty_strategy.estimate_confidence(
            prediction,
            context
        )

        # Record in history
        self._record_confidence(confidence_score, strategy_name, context)

        # Emit uncertainty quantified event
        self._emit_uncertainty_event(
            ThermodynamicEventType.UNCERTAINTY_QUANTIFIED,
            confidence_score,
            strategy_name,
            context
        )

        return confidence_score

    @wrap_exception(PipelineException, "Outcome learning failed")
    def learn_from_outcome(
        self,
        prediction: Any,
        actual: Any,
        context: Dict[str, Any],
        strategy: Optional[str] = None
    ) -> None:
        """
        Learn from observed outcome to improve future predictions.

        What it does:
        1. Select strategy
        2. Update strategy from outcome
        3. Emit learning event

        Args:
            prediction: What was predicted
            actual: What actually happened
            context: Context of prediction/outcome
            strategy: Strategy to update (optional, uses default if None)

        Raises:
            PipelineException: If update fails

        Usage:
            tc.learn_from_outcome(
                prediction="5 days",
                actual="7 days",
                context={
                    "stage": "estimation",
                    "prediction_type": "effort",
                    "comparison_type": "threshold"
                }
            )
        """
        # Select strategy
        strategy_name = strategy or self.default_strategy
        uncertainty_strategy = self._strategies.get(strategy_name)

        # Guard clause: validate strategy exists
        if not uncertainty_strategy:
            raise PipelineException(
                f"Unknown uncertainty strategy: {strategy_name}",
                context={"available_strategies": list(self._strategies.keys())}
            )

        # Update strategy from outcome
        uncertainty_strategy.update_from_outcome(prediction, actual, context)

        # Emit learning event
        self._emit_learning_event(strategy_name, prediction, actual, context)

    @wrap_exception(PipelineException, "Temperature sampling failed")
    def sample_with_temperature(
        self,
        options: List[Any],
        scores: List[float],
        temperature: Optional[float] = None,
        step: Optional[int] = None,
        max_steps: Optional[int] = None
    ) -> Any:
        """
        Sample from options using temperature-based Boltzmann distribution.

        What it does:
        1. Get temperature (provided, or from scheduler)
        2. Sample using Boltzmann: P(i) ∝ exp(score_i / T)
        3. Return sampled option

        Args:
            options: List of options to choose from
            scores: Score for each option (higher = better)
            temperature: Optional temperature override
            step: Current step for annealing (optional)
            max_steps: Total steps for annealing (optional)

        Returns:
            Sampled option

        Raises:
            PipelineException: If sampling fails

        Usage:
            # Explicit temperature
            option = tc.sample_with_temperature(
                options=["conservative", "moderate", "aggressive"],
                scores=[0.8, 0.6, 0.4],
                temperature=0.5
            )

            # Annealing schedule
            option = tc.sample_with_temperature(
                options=developers,
                scores=developer_scores,
                step=current_iteration,
                max_steps=total_iterations
            )
        """
        # Determine temperature
        if temperature is not None:
            # Use provided temperature
            temp = temperature
        elif step is not None and max_steps is not None:
            # Use annealing schedule
            temp = self.temperature_scheduler.get_temperature(step, max_steps)
        else:
            # Use current scheduler temperature
            temp = self.temperature_scheduler.current_temp

        # Sample using Boltzmann distribution
        selected = self.temperature_scheduler.sample_with_temperature(
            options,
            scores,
            temp
        )

        return selected

    def get_confidence_history(
        self,
        filter_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get confidence score history, optionally filtered.

        Why needed: Enables analysis of confidence trends over time,
        debugging of uncertainty estimation, and retrospective learning.

        Args:
            filter_context: Optional context to filter by
                           {"stage": "architecture"} returns only architecture scores

        Returns:
            List of confidence records with timestamps

        Usage:
            # Get all confidence scores
            all_scores = tc.get_confidence_history()

            # Get scores for specific stage
            arch_scores = tc.get_confidence_history(
                filter_context={"stage": "architecture"}
            )
        """
        # No filter: return all
        if not filter_context:
            return self._confidence_history.copy()

        # Filter by context
        filtered = []
        for record in self._confidence_history:
            # Check if all filter keys match
            matches = all(
                record["context"].get(key) == value
                for key, value in filter_context.items()
            )
            if matches:
                filtered.append(record)

        return filtered

    def get_strategy(self, strategy_name: str) -> UncertaintyStrategy:
        """
        Get uncertainty strategy by name.

        Why needed: Allows direct access to strategy for advanced use cases
        like custom configuration or inspection.

        Args:
            strategy_name: Name of strategy to retrieve

        Returns:
            UncertaintyStrategy instance

        Raises:
            ValueError: If strategy not found
        """
        strategy = self._strategies.get(strategy_name)

        if not strategy:
            raise ValueError(
                f"Unknown strategy: {strategy_name}. "
                f"Available: {list(self._strategies.keys())}"
            )

        return strategy

    # ========================================================================
    # HYBRID AI METHODS (Using Mixin)
    # ========================================================================

    @wrap_exception(PipelineException, "AI-enhanced confidence estimation failed")
    def quantify_code_confidence_with_ai(
        self,
        code: str,
        requirements: str = "",
        use_initial_analysis: bool = True
    ) -> ConfidenceScore:
        """
        Quantify confidence in code using hybrid AI approach.

        NEW: Demonstrates hybrid pattern:
        1. Start with router's pre-computed uncertainty (free!)
        2. Make adaptive AI call if more detail needed (via mixin)
        3. Convert AI response to internal ConfidenceScore format

        WHY: Shows integration of router context + adaptive AI calls.

        Args:
            code: Code to evaluate confidence for
            requirements: Requirements for context
            use_initial_analysis: If True, uses router's pre-computed uncertainty first

        Returns:
            ConfidenceScore with AI-enhanced confidence

        Usage:
            # Uses hybrid approach
            score = tc.quantify_code_confidence_with_ai(
                code=implementation_code,
                requirements=original_requirements
            )
        """
        # HYBRID STEP 1: Use router's pre-computed analysis (FREE!)
        if use_initial_analysis and self.initial_uncertainty is not None:
            initial_confidence = self.initial_uncertainty

            # If initial confidence is sufficient (>= threshold), use it
            threshold = self.context.get('confidence_threshold', 0.7)
            if initial_confidence >= threshold:
                # No need for additional AI call
                return ConfidenceScore(
                    mean=initial_confidence,
                    confidence_interval=(
                        max(0.0, initial_confidence - 0.1),
                        min(1.0, initial_uncertainty + 0.1)
                    ),
                    sources=["router_initial_analysis"],
                    metadata={
                        "source": "router_precomputed",
                        "cost": 0.0,  # Free!
                        "known_unknowns": self.known_unknowns
                    }
                )

        # HYBRID STEP 2: Initial insufficient or not available - make adaptive AI call
        if not self.ai_service:
            # Fallback: No AI service available, use initial or default
            fallback_confidence = self.initial_uncertainty if hasattr(self, 'initial_uncertainty') else 0.5
            return ConfidenceScore(
                mean=fallback_confidence,
                confidence_interval=(fallback_confidence - 0.15, fallback_confidence + 0.15),
                sources=["fallback_no_ai_service"],
                metadata={"warning": "No AI service available"}
            )

        # Make AI call via mixin method (DRY!)
        ai_estimate = self.query_for_confidence(
            code=code,
            context=f"Initial uncertainty: {self.initial_uncertainty:.0%}. Need detailed analysis.",
            requirements=requirements
        )

        # Convert mixin's ConfidenceEstimate to internal ConfidenceScore
        return ConfidenceScore(
            mean=ai_estimate.score,
            confidence_interval=(
                max(0.0, ai_estimate.score - 0.1),
                min(1.0, ai_estimate.score + 0.1)
            ),
            sources=ai_estimate.uncertainty_sources + ["ai_detailed_analysis"],
            metadata={
                "ai_model": ai_estimate.model_used,
                "ai_reasoning": ai_estimate.reasoning,
                "ai_suggestions": ai_estimate.suggestions,
                "initial_estimate": self.initial_uncertainty,
                "improvement": ai_estimate.score - self.initial_uncertainty
            }
        )

    @wrap_exception(PipelineException, "AI risk assessment failed")
    def assess_risks_with_ai(
        self,
        code: str,
        context_description: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Assess risks using AI (via mixin).

        NEW: Uses mixin's query_for_risk_assessment method (DRY!).

        Args:
            code: Code to assess
            context_description: Additional context

        Returns:
            List of risk assessments with AI-generated mitigations
        """
        if not self.ai_service:
            # Return router's pre-computed risks (free!)
            return self.risk_details

        # Make AI call via mixin method
        ai_risk = self.query_for_risk_assessment(
            code=code,
            context=context_description
        )

        # Combine with router's risks
        combined_risks = list(self.risk_details)  # Start with router's
        combined_risks.append({
            "type": ai_risk.risk_level,
            "severity": ai_risk.risk_level,
            "probability": ai_risk.probability,
            "description": ai_risk.impact,
            "mitigations": ai_risk.mitigations,
            "source": "ai_detailed_analysis"
        })

        return combined_risks

    # ========================================================================
    # HELPER METHODS (Internal)
    # ========================================================================

    def _record_confidence(
        self,
        score: ConfidenceScore,
        strategy: str,
        context: Dict[str, Any]
    ) -> None:
        """
        Record confidence score in history.

        Why needed: Maintains historical record for trend analysis,
        debugging, and retrospective learning.

        Args:
            score: ConfidenceScore to record
            strategy: Strategy used
            context: Context dict
        """
        record = {
            "timestamp": score.timestamp.isoformat(),
            "confidence": score.confidence,
            "variance": score.variance,
            "entropy": score.entropy,
            "strategy": strategy,
            "context": context,
            "sample_size": score.sample_size
        }

        self._confidence_history.append(record)

    def _emit_uncertainty_event(
        self,
        event_type: ThermodynamicEventType,
        score: ConfidenceScore,
        strategy: str,
        context: Dict[str, Any]
    ) -> None:
        """
        Emit uncertainty-related event.

        Why needed: Enables monitoring and logging of uncertainty operations.

        Args:
            event_type: Type of uncertainty event
            score: ConfidenceScore
            strategy: Strategy used
            context: Context dict
        """
        # Guard clause: check if observable configured
        if not self.observable:
            return

        event_data = {
            "thermodynamic_event": event_type.value,
            "confidence": score.confidence,
            "variance": score.variance,
            "entropy": score.entropy,
            "strategy": strategy,
            "sample_size": score.sample_size
        }

        event = PipelineEvent(
            event_type=EventType.STAGE_PROGRESS,
            card_id=context.get("card_id"),
            stage_name=context.get("stage"),
            data=event_data
        )

        self.observable.notify(event)

    def _emit_learning_event(
        self,
        strategy: str,
        prediction: Any,
        actual: Any,
        context: Dict[str, Any]
    ) -> None:
        """
        Emit learning event.

        Why needed: Tracks when system learns from outcomes.

        Args:
            strategy: Strategy that learned
            prediction: What was predicted
            actual: What happened
            context: Context dict
        """
        # Guard clause: check if observable configured
        if not self.observable:
            return

        event_data = {
            "thermodynamic_event": ThermodynamicEventType.BAYESIAN_EVIDENCE_ADDED.value,
            "strategy": strategy,
            "prediction": str(prediction),
            "actual": str(actual)
        }

        event = PipelineEvent(
            event_type=EventType.STAGE_PROGRESS,
            card_id=context.get("card_id"),
            stage_name=context.get("stage"),
            data=event_data
        )

        self.observable.notify(event)


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

@wrap_exception(PipelineException, "Confidence threshold check failed")
def check_confidence_threshold(
    score: ConfidenceScore,
    threshold: float,
    observable: Optional[PipelineObservable] = None,
    context: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Check if confidence score meets threshold.

    Why needed: Common operation for decision gates. "Proceed only if
    confidence > 0.7" is typical requirement.

    Args:
        score: ConfidenceScore to check
        threshold: Minimum confidence required
        observable: Optional observable for event emission
        context: Optional context for events

    Returns:
        True if confidence >= threshold, False otherwise

    Side effects:
        Emits CONFIDENCE_THRESHOLD_EXCEEDED or CONFIDENCE_THRESHOLD_FAILED event

    Usage:
        if check_confidence_threshold(score, 0.7):
            proceed_with_high_confidence()
        else:
            request_human_review()
    """
    # Check threshold
    meets_threshold = score.confidence >= threshold

    # Emit event
    if observable:
        event_type = (
            ThermodynamicEventType.CONFIDENCE_THRESHOLD_EXCEEDED
            if meets_threshold
            else ThermodynamicEventType.CONFIDENCE_THRESHOLD_FAILED
        )

        event_data = {
            "thermodynamic_event": event_type.value,
            "confidence": score.confidence,
            "threshold": threshold,
            "meets_threshold": meets_threshold
        }

        event = PipelineEvent(
            event_type=EventType.STAGE_PROGRESS,
            card_id=context.get("card_id") if context else None,
            stage_name=context.get("stage") if context else None,
            data=event_data
        )

        observable.notify(event)

    return meets_threshold


@wrap_exception(PipelineException, "Risk assessment failed")
def assess_risk(
    score: ConfidenceScore,
    risk_threshold: float = 0.3,
    observable: Optional[PipelineObservable] = None,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Assess risk level based on confidence score.

    Why needed: Translates confidence scores into actionable risk levels.
    Low confidence = high risk. High variance = high risk.

    Args:
        score: ConfidenceScore to assess
        risk_threshold: Variance threshold for high risk (default 0.3)
        observable: Optional observable for events
        context: Optional context for events

    Returns:
        Dict with:
        - "risk_level": "low", "medium", "high"
        - "confidence": Confidence value
        - "variance": Variance value
        - "recommendations": List of recommended actions

    Algorithm:
    - High risk: confidence < 0.5 or variance > threshold
    - Medium risk: 0.5 <= confidence < 0.7 or moderate variance
    - Low risk: confidence >= 0.7 and low variance

    Usage:
        risk = assess_risk(score)
        if risk["risk_level"] == "high":
            for action in risk["recommendations"]:
                take_action(action)
    """
    # Determine risk level using dispatch table (no elif)
    risk_levels = {
        "high": lambda c, v: c < 0.5 or v > risk_threshold,
        "medium": lambda c, v: (0.5 <= c < 0.7) or (risk_threshold / 2 < v <= risk_threshold),
        "low": lambda c, v: c >= 0.7 and v <= risk_threshold / 2
    }

    # Find matching risk level (iterate in order: high, medium, low)
    risk_level = "medium"  # Default
    for level in ["high", "medium", "low"]:
        if risk_levels[level](score.confidence, score.variance):
            risk_level = level
            break

    # Generate recommendations using dispatch table
    recommendation_dispatch = {
        "high": [
            "Request human review",
            "Gather more evidence",
            "Run additional validation",
            "Consider alternative approaches"
        ],
        "medium": [
            "Monitor closely",
            "Prepare contingency plans",
            "Document assumptions"
        ],
        "low": [
            "Proceed with confidence",
            "Document decision rationale"
        ]
    }

    recommendations = recommendation_dispatch[risk_level]

    # Build risk assessment
    risk_assessment = {
        "risk_level": risk_level,
        "confidence": score.confidence,
        "variance": score.variance,
        "entropy": score.entropy,
        "recommendations": recommendations
    }

    # Emit risk assessment event
    if observable:
        event_type = (
            ThermodynamicEventType.RISK_THRESHOLD_EXCEEDED
            if risk_level == "high"
            else ThermodynamicEventType.RISK_ASSESSED
        )

        event_data = {
            "thermodynamic_event": event_type.value,
            **risk_assessment
        }

        event = PipelineEvent(
            event_type=EventType.STAGE_PROGRESS,
            card_id=context.get("card_id") if context else None,
            stage_name=context.get("stage") if context else None,
            data=event_data
        )

        observable.notify(event)

    return risk_assessment


# ============================================================================
# EXAMPLE USAGE AND INTEGRATION GUIDE
# ============================================================================

"""
INTEGRATION EXAMPLES:

1. Add Uncertainty to LLM Calls:

   from thermodynamic_computing import ThermodynamicComputing

   tc = ThermodynamicComputing(observable=pipeline_observable)

   # Get LLM output
   llm_output = llm_client.call(prompt)

   # Quantify uncertainty
   score = tc.quantify_uncertainty(
       prediction=llm_output,
       context={
           "stage": "architecture",
           "card_id": card_id,
           "prediction_type": "architecture_design"
       },
       strategy="bayesian"
   )

   # Check confidence threshold
   if score.confidence < 0.7:
       logger.log("Low confidence - requesting review", "WARNING")
       request_human_review(llm_output, score)


2. Probabilistic Effort Estimation:

   def estimate_effort_monte_carlo(task_description):
       # Define simulator that samples from effort distribution
       def effort_simulator(prediction, context):
           # Sample duration from normal distribution
           # based on historical task durations
           mean_duration = 5  # days
           std_duration = 2
           sample = random.normalvariate(mean_duration, std_duration)
           # Return if sample close to prediction
           return abs(sample - prediction) < 1.0

       # Run Monte Carlo estimation
       score = tc.quantify_uncertainty(
           prediction=5,  # Predicted 5 days
           context={
               "simulator_fn": effort_simulator,
               "n_simulations": 1000,
               "stage": "estimation"
           },
           strategy="monte_carlo"
       )

       # Get confidence interval
       lower, upper = score.confidence_interval(z_score=1.96)  # 95% CI
       return f"Estimated effort: 5 days (95% CI: [{lower:.1f}, {upper:.1f}])"


3. Ensemble Code Generation:

   def generate_code_with_ensemble(requirement):
       # Define multiple code generators
       generators = [
           lambda req, ctx: generate_with_gpt4(req),
           lambda req, ctx: generate_with_claude(req),
           lambda req, ctx: generate_with_codex(req)
       ]

       # Create ensemble strategy
       ensemble = EnsembleUncertaintyStrategy(
           model_generators=generators,
           observable=pipeline_observable
       )

       # Add to thermodynamic computing
       tc._strategies["code_ensemble"] = ensemble

       # Generate code with ensemble
       code_options = [gen(requirement, {}) for gen in generators]

       # Get uncertainty score
       score = tc.quantify_uncertainty(
           prediction=code_options[0],  # Reference
           context={
               "stage": "development",
               "comparison_type": "code_similarity"
           },
           strategy="code_ensemble"
       )

       # If high agreement (high confidence), use any option
       # If low agreement (low confidence), request human selection
       if score.confidence > 0.7:
           return code_options[0]
       else:
           return request_human_code_selection(code_options, score)


4. Temperature-Based Developer Selection:

   def select_developer_with_annealing(iteration, total_iterations):
       developers = ["dev-a", "dev-b", "dev-c"]

       # Scores based on past performance
       scores = [0.85, 0.75, 0.65]

       # Early iterations (high temp): explore all developers
       # Late iterations (low temp): exploit best developer
       selected = tc.sample_with_temperature(
           options=developers,
           scores=scores,
           step=iteration,
           max_steps=total_iterations
       )

       return selected


5. Bayesian Learning from Retrospectives:

   def process_retrospective(task_id):
       # Get prediction from planning
       prediction = get_planning_estimate(task_id)

       # Get actual outcome
       actual = get_actual_duration(task_id)

       # Update Bayesian priors
       tc.learn_from_outcome(
           prediction=prediction,
           actual=actual,
           context={
               "stage": "estimation",
               "prediction_type": "effort",
               "comparison_type": "threshold",
               "threshold_percent": 0.2  # Within 20% is "correct"
           },
           strategy="bayesian"
       )

       # Future estimates will use updated priors


6. Risk-Aware Decision Making:

   def make_architecture_decision(options):
       scores = []

       for option in options:
           # Evaluate option
           score = tc.quantify_uncertainty(
               prediction=option,
               context={"stage": "architecture"},
               strategy="bayesian"
           )
           scores.append(score)

       # Assess risk for each option
       risks = [assess_risk(score) for score in scores]

       # Filter out high-risk options
       safe_options = [
           (opt, score) for opt, score, risk in zip(options, scores, risks)
           if risk["risk_level"] != "high"
       ]

       # Select best safe option
       if safe_options:
           best_option, best_score = max(safe_options, key=lambda x: x[1].confidence)
           return best_option
       else:
           # All options high-risk - escalate
           escalate_to_human(options, risks)
"""
