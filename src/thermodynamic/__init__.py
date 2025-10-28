"""
Thermodynamic Computing Package - Modularized probabilistic reasoning

WHY: Apply statistical thermodynamics to software engineering for uncertainty quantification.
RESPONSIBILITY: Provide probabilistic reasoning, Bayesian learning, ensemble methods.
PATTERNS: Strategy Pattern (uncertainty), Observer Pattern (events), Composition.

This package contains:
- models.py: ConfidenceScore data model
- events.py: ThermodynamicEventType enum
- uncertainty_strategy.py: Abstract strategy interface
- bayesian_strategy.py: Bayesian learning implementation
- monte_carlo_strategy.py: Monte Carlo simulation
- ensemble_strategy.py: Ensemble voting methods
- temperature_scheduler.py: Temperature-based exploration
- thermodynamic_computing.py: Main facade
- utils.py: Helper functions

EXTRACTED FROM: thermodynamic_computing.py (2,797 lines → 9 modules)
"""

# Export main classes
from thermodynamic.models import ConfidenceScore
from thermodynamic.events import ThermodynamicEventType
from thermodynamic.uncertainty_strategy import UncertaintyStrategy
from thermodynamic.bayesian_strategy import BayesianUncertaintyStrategy
from thermodynamic.monte_carlo_strategy import MonteCarloUncertaintyStrategy
from thermodynamic.ensemble_strategy import EnsembleUncertaintyStrategy
from thermodynamic.temperature_scheduler import TemperatureScheduler
from thermodynamic.utils import check_confidence_threshold, assess_risk

__all__ = [
    "ConfidenceScore",
    "ThermodynamicEventType",
    "UncertaintyStrategy",
    "BayesianUncertaintyStrategy",
    "MonteCarloUncertaintyStrategy",
    "EnsembleUncertaintyStrategy",
    "TemperatureScheduler",
    "check_confidence_threshold",
    "assess_risk",
]
