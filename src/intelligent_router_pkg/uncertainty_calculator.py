#!/usr/bin/env python3
"""
Uncertainty Calculator

WHAT: Calculates task uncertainty for Thermodynamic Computing.

WHY: Quantifies uncertainty based on task complexity, keywords, dependencies,
and prior experience. Provides structured input for confidence estimation.

RESPONSIBILITY:
    - Calculate overall uncertainty score
    - Identify uncertainty sources
    - Extract known unknowns
    - Adjust uncertainty based on experience
    - Determine confidence level

PATTERNS:
    - Strategy Pattern: Different calculation strategies for different factors
    - Guard Clause Pattern: Early returns for clarity
    - Dictionary Dispatch: For confidence level mapping
"""

from typing import Dict, List
from intelligent_router import TaskRequirements
from intelligent_router_pkg.uncertainty_analysis import UncertaintyAnalysis


class UncertaintyCalculator:
    """
    Calculates task uncertainty for Thermodynamic Computing.

    WHY: Quantifies uncertainty based on multiple factors to provide
    structured input for confidence estimation and Bayesian learning.
    """

    def __init__(self, uncertainty_keywords: List[str]):
        """
        Initialize uncertainty calculator.

        Args:
            uncertainty_keywords: Keywords indicating uncertainty
        """
        self.uncertainty_keywords = uncertainty_keywords

    def calculate_task_uncertainty(
        self,
        card: Dict,
        requirements: TaskRequirements,
        estimate_similar_task_history_func
    ) -> UncertaintyAnalysis:
        """
        Calculate task uncertainty for Thermodynamic Computing.

        WHAT: Quantifies uncertainty based on:
            - Presence of uncertainty keywords
            - Lack of similar past tasks
            - Task complexity
            - Requirement clarity
            - External dependencies

        Args:
            card: Kanban card with task details
            requirements: Analyzed task requirements
            estimate_similar_task_history_func: Function to estimate task history

        Returns:
            UncertaintyAnalysis with quantified uncertainty
        """
        combined_text = f"{card.get('title', '')} {card.get('description', '')}".lower()

        # Calculate uncertainty components
        uncertainty_score = 0.0
        uncertainty_sources = []
        known_unknowns = []

        # Complexity contribution
        uncertainty_score, uncertainty_sources = self._add_complexity_uncertainty(
            uncertainty_score, uncertainty_sources, requirements
        )

        # Uncertainty keyword detection
        uncertainty_score, uncertainty_sources, known_unknowns = self._add_keyword_uncertainty(
            uncertainty_score, uncertainty_sources, known_unknowns, combined_text
        )

        # External dependency uncertainty
        uncertainty_score, uncertainty_sources, known_unknowns = self._add_dependency_uncertainty(
            uncertainty_score, uncertainty_sources, known_unknowns, requirements
        )

        # Database migration uncertainty
        uncertainty_score, uncertainty_sources, known_unknowns = self._add_database_uncertainty(
            uncertainty_score, uncertainty_sources, known_unknowns, requirements, combined_text
        )

        # New technology uncertainty
        uncertainty_score, uncertainty_sources, known_unknowns = self._add_new_tech_uncertainty(
            uncertainty_score, uncertainty_sources, known_unknowns, combined_text
        )

        # Estimate similar task history
        similar_task_history = estimate_similar_task_history_func(
            requirements.task_type,
            requirements.complexity
        )

        # Adjust uncertainty based on experience
        uncertainty_score = self._adjust_uncertainty_by_experience(
            uncertainty_score, similar_task_history, uncertainty_sources
        )

        # Cap uncertainty at 1.0
        uncertainty_score = min(1.0, max(0.0, uncertainty_score))

        # Determine confidence level
        confidence_level = self._determine_confidence_level(uncertainty_score)

        return UncertaintyAnalysis(
            overall_uncertainty=uncertainty_score,
            uncertainty_sources=uncertainty_sources,
            known_unknowns=known_unknowns if known_unknowns else ["None identified"],
            similar_task_history=similar_task_history,
            confidence_level=confidence_level
        )

    def _add_complexity_uncertainty(
        self,
        uncertainty_score: float,
        uncertainty_sources: List[str],
        requirements: TaskRequirements
    ) -> tuple:
        """Add complexity contribution to uncertainty."""
        complexity_uncertainty = {
            'simple': 0.1,
            'medium': 0.3,
            'complex': 0.6
        }
        uncertainty_score += complexity_uncertainty.get(requirements.complexity, 0.3)
        uncertainty_sources.append(f"Task complexity: {requirements.complexity}")
        return uncertainty_score, uncertainty_sources

    def _add_keyword_uncertainty(
        self,
        uncertainty_score: float,
        uncertainty_sources: List[str],
        known_unknowns: List[str],
        combined_text: str
    ) -> tuple:
        """Add uncertainty keyword contribution."""
        uncertainty_keyword_count = sum(
            1 for keyword in self.uncertainty_keywords
            if keyword in combined_text
        )

        # Guard clause: skip if no keywords found
        if uncertainty_keyword_count == 0:
            return uncertainty_score, uncertainty_sources, known_unknowns

        uncertainty_score += min(0.3, uncertainty_keyword_count * 0.1)
        uncertainty_sources.append(
            f"Uncertainty keywords found: {uncertainty_keyword_count}"
        )
        known_unknowns.append("Task contains explicit uncertainty language")
        return uncertainty_score, uncertainty_sources, known_unknowns

    def _add_dependency_uncertainty(
        self,
        uncertainty_score: float,
        uncertainty_sources: List[str],
        known_unknowns: List[str],
        requirements: TaskRequirements
    ) -> tuple:
        """Add external dependency uncertainty."""
        if not requirements.has_external_dependencies:
            return uncertainty_score, uncertainty_sources, known_unknowns

        uncertainty_score += 0.15
        uncertainty_sources.append("External dependencies add uncertainty")
        known_unknowns.append("External API/library behavior")
        return uncertainty_score, uncertainty_sources, known_unknowns

    def _add_database_uncertainty(
        self,
        uncertainty_score: float,
        uncertainty_sources: List[str],
        known_unknowns: List[str],
        requirements: TaskRequirements,
        combined_text: str
    ) -> tuple:
        """Add database migration uncertainty."""
        if not (requirements.has_database and 'migrat' in combined_text):
            return uncertainty_score, uncertainty_sources, known_unknowns

        uncertainty_score += 0.2
        uncertainty_sources.append("Database migration adds significant uncertainty")
        known_unknowns.append("Data migration edge cases and rollback scenarios")
        return uncertainty_score, uncertainty_sources, known_unknowns

    def _add_new_tech_uncertainty(
        self,
        uncertainty_score: float,
        uncertainty_sources: List[str],
        known_unknowns: List[str],
        combined_text: str
    ) -> tuple:
        """Add new technology uncertainty."""
        new_tech_keywords = ['new technology', 'unfamiliar', 'never used', 'first time']
        if not any(keyword in combined_text for keyword in new_tech_keywords):
            return uncertainty_score, uncertainty_sources, known_unknowns

        uncertainty_score += 0.25
        uncertainty_sources.append("New/unfamiliar technology")
        known_unknowns.append("Learning curve and unexpected behaviors")
        return uncertainty_score, uncertainty_sources, known_unknowns

    def _adjust_uncertainty_by_experience(
        self,
        uncertainty_score: float,
        similar_task_history: int,
        uncertainty_sources: List[str]
    ) -> float:
        """
        Adjust uncertainty score based on experience using guard clauses.

        WHY: Extracted to eliminate if/elif chain and reduce nesting.
        Uses early returns for clear control flow.
        """
        # Guard clause: extensive experience reduces uncertainty
        if similar_task_history >= 10:
            uncertainty_sources.append("Extensive prior experience")
            return uncertainty_score - 0.1

        # Guard clause: no experience adds significant uncertainty
        if similar_task_history == 0:
            uncertainty_sources.append("No prior experience with similar tasks")
            return uncertainty_score + 0.2

        # Guard clause: limited experience adds moderate uncertainty
        if similar_task_history < 3:
            uncertainty_sources.append("Limited prior experience")
            return uncertainty_score + 0.1

        # Default: moderate experience, no adjustment
        return uncertainty_score

    def _determine_confidence_level(self, uncertainty_score: float) -> str:
        """
        Determine confidence level from uncertainty score using dictionary dispatch.

        WHY: Eliminates if/elif chain using declarative threshold mapping.
        """
        # Dictionary dispatch: threshold -> confidence level
        confidence_thresholds = [
            (0.8, 'very_low'),
            (0.6, 'low'),
            (0.4, 'medium'),
            (0.2, 'high'),
            (0.0, 'very_high'),
        ]

        # Find first threshold where score >= threshold
        for threshold, level in confidence_thresholds:
            if uncertainty_score >= threshold:
                return level

        # Fallback
        return 'very_high'
