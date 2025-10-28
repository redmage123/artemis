"""
Module: thermodynamic/events.py

WHY: Event types for thermodynamic computing operations.
RESPONSIBILITY: Define event enum for confidence tracking, uncertainty, Bayesian learning.
PATTERNS: Enum Pattern.

This module handles:
- Confidence tracking events
- Uncertainty quantification events
- Bayesian learning events
- Monte Carlo simulation events
- Ensemble method events
- Temperature/annealing events
- Risk assessment events

EXTRACTED FROM: thermodynamic_computing.py (lines 224-275)
"""

from enum import Enum


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


__all__ = [
    "ThermodynamicEventType"
]
