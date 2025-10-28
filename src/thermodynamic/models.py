"""
Module: thermodynamic/models.py

WHY: Data models for thermodynamic computing (confidence, uncertainty quantification).
RESPONSIBILITY: Define ConfidenceScore value object for probabilistic reasoning.
PATTERNS: Value Object Pattern, Guard Clauses.

This module handles:
- ConfidenceScore: Represents probabilistic confidence with variance, entropy
- Validation of probability values [0, 1]
- Statistical calculations (standard error, confidence intervals)
- Serialization for storage/logging

EXTRACTED FROM: thermodynamic_computing.py (lines 99-218)
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Tuple
from datetime import datetime
import math


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


__all__ = [
    "ConfidenceScore"
]
