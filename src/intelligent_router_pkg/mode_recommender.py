#!/usr/bin/env python3
"""
Mode Recommender

WHAT: Recommends pipeline mode and feature intensity levels.

WHY: Analyzes task characteristics to recommend how aggressively to use
each advanced feature (Dynamic, Two-Pass, Thermodynamic).

RESPONSIBILITY:
    - Recommend pipeline mode based on benefit scores
    - Determine intensity levels for each feature
    - Fine-tune intensities based on task characteristics
    - Calculate confidence in recommendation
    - Build expected benefits list

PATTERNS:
    - Strategy Pattern: Different mode selection strategies
    - Dictionary Dispatch: Maps modes to intensity levels
    - Guard Clause Pattern: Early returns for clarity
"""

from typing import Dict, List, Tuple
from advanced_pipeline_integration import PipelineMode, AdvancedPipelineConfig
from intelligent_router import TaskRequirements
from intelligent_router_pkg.advanced_feature_recommendation import AdvancedFeatureRecommendation
from intelligent_router_pkg.uncertainty_analysis import UncertaintyAnalysis
from intelligent_router_pkg.risk_factor import RiskFactor


class ModeRecommender:
    """
    Recommends pipeline mode and feature intensity levels.

    WHY: Analyzes task characteristics to recommend how aggressively
    to use each advanced feature working in tandem.
    """

    def __init__(self, advanced_config: AdvancedPipelineConfig, logger=None):
        """
        Initialize mode recommender.

        Args:
            advanced_config: Configuration for advanced pipeline features
            logger: Logger for output
        """
        self.advanced_config = advanced_config
        self.logger = logger

    def recommend_pipeline_mode(
        self,
        requirements: TaskRequirements,
        uncertainty: UncertaintyAnalysis,
        risks: List[RiskFactor],
        dynamic_benefit: float,
        two_pass_benefit: float,
        thermodynamic_benefit: float
    ) -> AdvancedFeatureRecommendation:
        """
        Recommend intensity levels for ALL THREE advanced features working in tandem.

        WHAT: Analyzes task characteristics and recommends:
            - Pipeline execution mode (STANDARD/DYNAMIC/TWO_PASS/ADAPTIVE/FULL)
            - Intensity levels (0.0-1.0) for each advanced feature
            - Rationale for recommendations

        Args:
            requirements: Analyzed task requirements
            uncertainty: Calculated uncertainty analysis
            risks: Identified risk factors
            dynamic_benefit: Benefit score for dynamic pipeline
            two_pass_benefit: Benefit score for two-pass
            thermodynamic_benefit: Benefit score for thermodynamic

        Returns:
            Recommendation with intensity levels for all three features
        """
        # Determine mode using dispatch table
        mode_selection_rules = [
            (
                lambda: two_pass_benefit > 0.7 and thermodynamic_benefit > 0.6,
                PipelineMode.FULL,
                "High benefit from both two-pass and uncertainty quantification"
            ),
            (
                lambda: thermodynamic_benefit > 0.7,
                PipelineMode.ADAPTIVE,
                "High uncertainty requires adaptive execution with confidence tracking"
            ),
            (
                lambda: two_pass_benefit > 0.6,
                PipelineMode.TWO_PASS,
                "Task benefits from fast feedback and iterative refinement"
            ),
            (
                lambda: dynamic_benefit > 0.5,
                PipelineMode.DYNAMIC,
                "Task complexity varies, dynamic stage selection beneficial"
            ),
            (
                lambda: True,  # Default
                PipelineMode.STANDARD,
                "Simple task, standard pipeline sufficient"
            )
        ]

        # Select first matching rule
        recommended_mode = None
        rationale = None
        for condition, mode, reason in mode_selection_rules:
            if condition():
                recommended_mode = mode
                rationale = reason
                break

        # Map mode to intensity levels
        MODE_INTENSITY_MAP = {
            PipelineMode.STANDARD: (0.2, 0.0, 0.2),
            PipelineMode.DYNAMIC: (0.5, 0.0, 0.8),
            PipelineMode.TWO_PASS: (0.6, 1.0, 0.6),
            PipelineMode.ADAPTIVE: (1.0, 0.0, 0.8),
            PipelineMode.FULL: (1.0, 1.0, 1.0)
        }

        # Get base intensity levels from mode
        therm_intensity, two_pass_intensity, dynamic_intensity = MODE_INTENSITY_MAP[recommended_mode]

        # Fine-tune intensities
        intensities = self._fine_tune_intensities(
            mode=recommended_mode,
            base_intensities=(therm_intensity, two_pass_intensity, dynamic_intensity),
            benefits=(thermodynamic_benefit, two_pass_benefit, dynamic_benefit)
        )
        therm_intensity, two_pass_intensity, dynamic_intensity = intensities

        # Determine legacy boolean flags
        use_dynamic = (
            dynamic_intensity > 0.3
            and self.advanced_config.enable_dynamic_pipeline
        )

        use_two_pass = (
            two_pass_intensity > 0.5
            and self.advanced_config.enable_two_pass
        )

        use_thermodynamic = (
            therm_intensity > 0.3
            and self.advanced_config.enable_thermodynamic
        )

        # Build expected benefits list
        expected_benefits = self._build_expected_benefits_list(
            use_dynamic=use_dynamic,
            use_two_pass=use_two_pass,
            use_thermodynamic=use_thermodynamic,
            dynamic_intensity=dynamic_intensity,
            two_pass_intensity=two_pass_intensity,
            therm_intensity=therm_intensity,
            dynamic_benefit=dynamic_benefit,
            requirements=requirements,
            uncertainty=uncertainty
        )

        # Calculate confidence in recommendation
        confidence = self._calculate_recommendation_confidence(
            requirements, uncertainty, risks
        )

        return AdvancedFeatureRecommendation(
            recommended_mode=recommended_mode,
            thermodynamic_intensity=therm_intensity,
            two_pass_intensity=two_pass_intensity,
            dynamic_intensity=dynamic_intensity,
            use_dynamic_pipeline=use_dynamic,
            use_two_pass=use_two_pass,
            use_thermodynamic=use_thermodynamic,
            rationale=rationale,
            confidence_in_recommendation=confidence,
            expected_benefits=expected_benefits
        )

    def _fine_tune_intensities(
        self,
        mode: PipelineMode,
        base_intensities: Tuple[float, float, float],
        benefits: Tuple[float, float, float]
    ) -> Tuple[float, float, float]:
        """
        Fine-tune intensity levels based on mode and benefits using Strategy pattern.

        WHY Strategy pattern: Declarative dispatch table, no sequential ifs.
        """
        therm_base, two_pass_base, dynamic_base = base_intensities
        therm_benefit, two_pass_benefit, dynamic_benefit = benefits

        # Intensity tuning strategies dispatch table
        INTENSITY_TUNING_STRATEGIES = {
            PipelineMode.STANDARD: lambda: (
                max(0.2, therm_base * (0.2 + therm_benefit * 0.8)),
                two_pass_base,
                max(0.2, dynamic_base * (0.5 + dynamic_benefit * 0.5))
            ),
            PipelineMode.DYNAMIC: lambda: (
                max(0.2, therm_base * (0.2 + therm_benefit * 0.8)),
                two_pass_base,
                max(0.5, dynamic_base * (0.5 + dynamic_benefit * 0.5))
            ),
            PipelineMode.TWO_PASS: lambda: (
                max(0.2, therm_base * (0.2 + therm_benefit * 0.8)),
                max(0.6, two_pass_base * (0.6 + two_pass_benefit * 0.4)),
                max(0.5, dynamic_base * (0.5 + dynamic_benefit * 0.5))
            ),
            PipelineMode.ADAPTIVE: lambda: (
                max(0.2, therm_base * (0.2 + therm_benefit * 0.8)),
                two_pass_base,
                max(0.5, dynamic_base * (0.5 + dynamic_benefit * 0.5))
            ),
            PipelineMode.FULL: lambda: (
                max(0.2, therm_base * (0.2 + therm_benefit * 0.8)),
                max(0.6, two_pass_base * (0.6 + two_pass_benefit * 0.4)),
                max(0.5, dynamic_base * (0.5 + dynamic_benefit * 0.5))
            )
        }

        # Dispatch to appropriate strategy
        tuning_strategy = INTENSITY_TUNING_STRATEGIES.get(mode)
        if not tuning_strategy:
            if self.logger:
                self.logger.warning(f"No tuning strategy for mode {mode}, using base intensities")
            return base_intensities

        return tuning_strategy()

    def _build_expected_benefits_list(
        self,
        use_dynamic: bool,
        use_two_pass: bool,
        use_thermodynamic: bool,
        dynamic_intensity: float,
        two_pass_intensity: float,
        therm_intensity: float,
        dynamic_benefit: float,
        requirements: TaskRequirements,
        uncertainty: UncertaintyAnalysis
    ) -> List[str]:
        """Build expected benefits list using guard clauses."""
        expected_benefits = []

        if use_dynamic:
            expected_benefits.append(
                f"Dynamic: Optimize stage selection at {dynamic_intensity:.0%} intensity "
                f"(estimated {int(dynamic_benefit * 30)}% time savings)"
            )

        if use_two_pass:
            expected_benefits.append(
                f"Two-Pass: Fast feedback in ~30s, refined in ~{requirements.estimated_story_points * 2}min "
                f"at {two_pass_intensity:.0%} intensity"
            )

        if use_thermodynamic:
            expected_benefits.append(
                f"Thermodynamic: Quantify uncertainty at {therm_intensity:.0%} intensity "
                f"(current: {uncertainty.overall_uncertainty:.0%}), learn from outcome"
            )

        return expected_benefits

    def _calculate_recommendation_confidence(
        self,
        requirements: TaskRequirements,
        uncertainty: UncertaintyAnalysis,
        risks: List[RiskFactor]
    ) -> float:
        """Calculate confidence in feature recommendation (0.0-1.0)."""
        confidence = 0.8  # Start with base confidence

        # Reduce confidence for high uncertainty tasks
        confidence -= uncertainty.overall_uncertainty * 0.2

        # Reduce confidence for unfamiliar task types
        if uncertainty.similar_task_history == 0:
            confidence -= 0.1

        # Increase confidence for clear patterns
        if requirements.task_type in ['bugfix', 'documentation']:
            confidence += 0.1

        return max(0.3, min(1.0, confidence))
