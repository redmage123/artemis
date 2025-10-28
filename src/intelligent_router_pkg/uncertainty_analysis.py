#!/usr/bin/env python3
"""
Uncertainty Analysis Model

WHAT: Data structure representing task uncertainty analysis.

WHY: Provides structured input to Thermodynamic Computing for Bayesian learning
and confidence estimation. Quantifies what we don't know about a task.

RESPONSIBILITY:
    - Quantify overall uncertainty level
    - Track sources of uncertainty
    - Identify known unknowns
    - Record similar task history
    - Assign confidence level

PATTERNS:
    - Value Object: Immutable data structure
    - Data Transfer Object: Carries uncertainty data between components
"""

from dataclasses import dataclass
from typing import List


@dataclass
class UncertaintyAnalysis:
    """
    Analysis of task uncertainty.

    WHY: Provides structured input to Thermodynamic Computing for
    Bayesian learning and confidence estimation.

    Attributes:
        overall_uncertainty: Uncertainty score (0.0=certain, 1.0=completely uncertain)
        uncertainty_sources: List of identified uncertainty sources
        known_unknowns: Things we know we don't know
        similar_task_history: Number of similar past tasks
        confidence_level: Text confidence level (very_low, low, medium, high, very_high)
    """
    overall_uncertainty: float  # 0.0-1.0 (0=certain, 1=completely uncertain)
    uncertainty_sources: List[str]  # Sources of uncertainty
    known_unknowns: List[str]  # Things we know we don't know
    similar_task_history: int  # Number of similar past tasks
    confidence_level: str  # 'very_low', 'low', 'medium', 'high', 'very_high'
