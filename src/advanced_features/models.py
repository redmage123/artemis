#!/usr/bin/env python3
"""
Advanced Features Models

WHY: Centralized data models for advanced AI features (Thermodynamic Computing,
Two-Pass Pipeline, Dynamic Pipeline). Provides type-safe containers for AI
responses and evaluation results.

RESPONSIBILITY:
- Define data structures for AI query responses
- Provide type hints for feature evaluation results
- Ensure consistent data representation across features

PATTERNS:
- Data Transfer Objects (DTOs): Simple data containers
- Immutable Design: Using @dataclass for value objects
- Type Safety: Full type hints for all attributes

USAGE:
    from advanced_features.models import ConfidenceEstimate

    estimate = ConfidenceEstimate(
        score=0.85,
        reasoning="Code meets requirements",
        uncertainty_sources=["Token refresh untested"],
        suggestions=["Add unit tests"],
        model_used="sonnet"
    )
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class RiskLevel(str, Enum):
    """Risk levels for risk assessment"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class ComplexityLevel(str, Enum):
    """Complexity levels for task estimation"""
    TRIVIAL = "trivial"
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


class IssueSeverity(str, Enum):
    """Issue severity for quality evaluation"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============================================================================
# DATA CLASSES FOR AI RESPONSES
# ============================================================================

@dataclass
class ConfidenceEstimate:
    """
    AI-generated confidence estimate for code/decision.

    WHY: Thermodynamic Computing needs confidence scores to quantify
    uncertainty in generated code.

    Attributes:
        score: Confidence score from 0.0 (no confidence) to 1.0 (full confidence)
        reasoning: Detailed explanation of confidence score
        uncertainty_sources: List of factors contributing to uncertainty
        suggestions: Recommended improvements to increase confidence
        model_used: Name of LLM model that generated this estimate
    """
    score: float  # 0.0-1.0
    reasoning: str
    uncertainty_sources: List[str]
    suggestions: List[str]
    model_used: str

    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """Check if confidence exceeds threshold"""
        return self.score >= threshold

    def is_low_confidence(self, threshold: float = 0.5) -> bool:
        """Check if confidence is below threshold"""
        return self.score < threshold


@dataclass
class RiskAssessment:
    """
    AI-generated risk assessment.

    WHY: All advanced features need risk assessment for decision-making:
    - Thermodynamic: Monte Carlo simulations
    - Two-Pass: Rollback decisions
    - Dynamic: Retry policies

    Attributes:
        risk_level: Categorical risk level
        probability: Numeric probability of risk (0.0-1.0)
        impact: Description of potential impact
        mitigations: Recommended risk mitigation strategies
        model_used: Name of LLM model that generated this assessment
    """
    risk_level: str  # Use RiskLevel enum values
    probability: float  # 0.0-1.0
    impact: str
    mitigations: List[str]
    model_used: str

    def is_critical_risk(self) -> bool:
        """Check if risk is critical"""
        return self.risk_level == RiskLevel.CRITICAL.value

    def is_acceptable_risk(self) -> bool:
        """Check if risk is low or medium"""
        return self.risk_level in [RiskLevel.LOW.value, RiskLevel.MEDIUM.value]


@dataclass
class QualityIssue:
    """
    Individual quality issue found in code.

    Attributes:
        severity: Issue severity level
        description: Detailed issue description
    """
    severity: str  # Use IssueSeverity enum values
    description: str


@dataclass
class QualityEvaluation:
    """
    AI-generated quality evaluation.

    WHY: Two-Pass Pipeline needs quality comparison between first and second
    pass to decide whether to accept improvements.

    Attributes:
        quality_score: Overall quality score (0.0-1.0)
        issues: List of quality issues identified
        strengths: List of code strengths
        improvement_suggestions: Recommended improvements
        model_used: Name of LLM model that generated this evaluation
    """
    quality_score: float  # 0.0-1.0
    issues: List[Dict[str, str]]
    strengths: List[str]
    improvement_suggestions: List[str]
    model_used: str

    def is_high_quality(self, threshold: float = 0.8) -> bool:
        """Check if quality exceeds threshold"""
        return self.quality_score >= threshold

    def has_critical_issues(self) -> bool:
        """Check if any critical issues exist"""
        return any(
            issue.get("severity") == IssueSeverity.CRITICAL.value
            for issue in self.issues
        )

    def get_issues_by_severity(self, severity: str) -> List[Dict[str, str]]:
        """Filter issues by severity level"""
        return [
            issue for issue in self.issues
            if issue.get("severity") == severity
        ]


@dataclass
class ComplexityEstimate:
    """
    AI-generated complexity estimation.

    WHY: Dynamic Pipeline needs complexity to configure parallelization
    and resource allocation.

    Attributes:
        complexity_level: Categorical complexity level
        story_points: Agile story point estimate
        reasoning: Detailed reasoning for estimate
        breakdown: Effort breakdown by phase
        parallelization_potential: Can work be parallelized (low/medium/high)
        suggested_workers: Recommended number of parallel workers
    """
    complexity_level: str  # Use ComplexityLevel enum values
    story_points: int
    reasoning: str
    breakdown: Dict[str, int]
    parallelization_potential: str
    suggested_workers: int

    def is_complex_task(self) -> bool:
        """Check if task is complex or very complex"""
        return self.complexity_level in [
            ComplexityLevel.COMPLEX.value,
            ComplexityLevel.VERY_COMPLEX.value
        ]

    def can_parallelize(self) -> bool:
        """Check if task has parallelization potential"""
        return self.parallelization_potential in ["medium", "high"]

    def get_total_effort(self) -> int:
        """Calculate total effort from breakdown"""
        return sum(self.breakdown.values()) if self.breakdown else self.story_points


@dataclass
class BatchConfidenceResult:
    """
    Result from batch confidence estimation.

    WHY: Thermodynamic Computing may need to evaluate multiple code paths
    simultaneously for Monte Carlo simulations.

    Attributes:
        estimates: List of confidence estimates
        average_confidence: Mean confidence across all samples
        min_confidence: Lowest confidence score
        max_confidence: Highest confidence score
    """
    estimates: List[ConfidenceEstimate]

    @property
    def average_confidence(self) -> float:
        """Calculate average confidence"""
        if not self.estimates:
            return 0.0
        return sum(e.score for e in self.estimates) / len(self.estimates)

    @property
    def min_confidence(self) -> float:
        """Get minimum confidence"""
        if not self.estimates:
            return 0.0
        return min(e.score for e in self.estimates)

    @property
    def max_confidence(self) -> float:
        """Get maximum confidence"""
        if not self.estimates:
            return 0.0
        return max(e.score for e in self.estimates)

    def get_low_confidence_samples(self, threshold: float = 0.5) -> List[ConfidenceEstimate]:
        """Get samples with confidence below threshold"""
        return [e for e in self.estimates if e.score < threshold]
