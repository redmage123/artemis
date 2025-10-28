#!/usr/bin/env python3
"""
Benefit Calculator

WHAT: Calculates benefit scores for each advanced feature.

WHY: Determines how much each feature (Dynamic, Two-Pass, Thermodynamic)
would help a specific task, used for intensity recommendations.

RESPONSIBILITY:
    - Calculate dynamic pipeline benefit score
    - Calculate two-pass pipeline benefit score
    - Calculate thermodynamic computing benefit score
    - Return normalized scores (0.0-1.0)

PATTERNS:
    - Strategy Pattern: Different calculation strategies per feature
    - Guard Clause Pattern: Early returns for clarity
"""

from typing import List
from intelligent_router import TaskRequirements
from intelligent_router_pkg.uncertainty_analysis import UncertaintyAnalysis
from intelligent_router_pkg.risk_factor import RiskFactor


class BenefitCalculator:
    """
    Calculates benefit scores for each advanced feature.

    WHY: Determines how much each feature would help a specific task,
    used to recommend appropriate intensity levels.
    """

    def __init__(self, two_pass_keywords: List[str]):
        """
        Initialize benefit calculator.

        Args:
            two_pass_keywords: Keywords suggesting two-pass would be valuable
        """
        self.two_pass_keywords = two_pass_keywords

    def calculate_dynamic_pipeline_benefit(
        self,
        requirements: TaskRequirements
    ) -> float:
        """
        Calculate benefit score for Dynamic Pipeline (0.0-1.0).

        WHY extracted: Separates benefit calculation logic for testing and tuning.

        High benefit when:
            - Varying complexity (some stages optional)
            - Multiple execution paths
            - Resource-constrained environment
        """
        benefit = 0.0

        # Moderate complexity benefits most (can skip some stages)
        if requirements.complexity == 'medium':
            benefit += 0.4
        elif requirements.complexity == 'simple':
            benefit += 0.2  # Less benefit (already few stages)

        # Multiple stage candidates → more optimization opportunity
        if requirements.complexity in ['medium', 'complex']:
            benefit += 0.3

        # External dependencies → benefit from conditional execution
        if requirements.has_external_dependencies:
            benefit += 0.2

        return min(1.0, benefit)

    def calculate_two_pass_benefit(
        self,
        requirements: TaskRequirements,
        uncertainty: UncertaintyAnalysis,
        text: str
    ) -> float:
        """
        Calculate benefit score for Two-Pass Pipeline (0.0-1.0).

        WHY extracted: Separates benefit calculation logic for testing and tuning.

        High benefit when:
            - Prototype/experimental work
            - Refactoring (needs rollback safety)
            - High uncertainty (learn from first pass)
            - Complex task (benefit from progressive refinement)
        """
        benefit = 0.0

        # Two-pass keywords indicate high benefit
        keyword_matches = sum(1 for kw in self.two_pass_keywords if kw in text)
        if keyword_matches > 0:
            benefit += min(0.5, keyword_matches * 0.2)

        # Refactoring benefits from rollback
        if requirements.task_type == 'refactor':
            benefit += 0.4

        # High uncertainty benefits from learning
        if uncertainty.overall_uncertainty > 0.6:
            benefit += 0.3

        # Complex tasks benefit from progressive refinement
        if requirements.complexity == 'complex':
            benefit += 0.2

        return min(1.0, benefit)

    def calculate_thermodynamic_benefit(
        self,
        uncertainty: UncertaintyAnalysis,
        risks: List[RiskFactor]
    ) -> float:
        """
        Calculate benefit score for Thermodynamic Computing (0.0-1.0).

        WHY extracted: Separates benefit calculation logic for testing and tuning.

        High benefit when:
            - High uncertainty (needs quantification)
            - Multiple risk factors (needs Monte Carlo)
            - Low confidence (needs Bayesian learning)
            - Estimation needed (needs confidence intervals)
        """
        benefit = 0.0

        # High uncertainty → high benefit
        benefit += uncertainty.overall_uncertainty * 0.5

        # Multiple risks → Monte Carlo valuable - guard clauses
        if len(risks) >= 3:
            benefit += 0.3
        elif len(risks) >= 1:
            benefit += 0.15

        # Low prior experience → Bayesian learning valuable
        if uncertainty.similar_task_history < 3:
            benefit += 0.2

        # Critical risks → risk quantification essential - guard clauses
        critical_risks = [r for r in risks if r.severity in ['critical', 'high']]
        critical_risk_count = len(critical_risks)

        if critical_risk_count >= 2:
            benefit += 0.2
        elif critical_risk_count == 1:
            benefit += 0.1

        return min(1.0, benefit)
