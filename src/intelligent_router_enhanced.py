#!/usr/bin/env python3
"""
Intelligent Router Enhanced - AI-Powered Stage Selection with Advanced Feature Integration

WHAT: Enhanced intelligent router that not only selects pipeline stages, but also
recommends which advanced features (Dynamic Pipelines, Two-Pass, Thermodynamic Computing)
to use for optimal execution.

WHY: The intelligent router analyzes task requirements and can identify which advanced
features would provide the most benefit. Simple tasks waste resources on advanced features,
while complex/risky tasks benefit enormously. The router is the perfect place to make
this decision since it already analyzes task complexity, risk, and requirements.

Integration Points:
    - Extends IntelligentRouter with advanced feature awareness
    - Integrates with AdvancedPipelineIntegration for mode selection
    - Provides context to ThermodynamicComputing for uncertainty quantification
    - Recommends Two-Pass for tasks needing fast feedback
    - Suggests Dynamic Pipeline for varying complexity

Design Patterns:
    - Strategy Pattern: Different routing strategies for different task types
    - Factory Pattern: Creates appropriate RoutingDecision with feature recommendations
    - Adapter Pattern: Adapts routing decision to advanced pipeline integration
    - Observer Pattern: Emits events for routing decisions
    - Decorator Pattern: @wrap_exception for error handling

Key Enhancements Over Base Router:
    1. Recommends PipelineMode (STANDARD, DYNAMIC, TWO_PASS, ADAPTIVE, FULL)
    2. Identifies risk factors that trigger Thermodynamic Computing
    3. Detects uncertainty patterns suggesting Two-Pass execution
    4. Calculates confidence scores for routing decisions
    5. Provides rich context for each advanced feature

Architecture:
    IntelligentRouterEnhanced
    ├── analyze_task_requirements() [inherited]
    ├── make_routing_decision() [inherited]
    ├── recommend_pipeline_mode() [NEW]
    ├── calculate_task_uncertainty() [NEW]
    ├── identify_risk_factors() [NEW]
    ├── should_use_two_pass() [NEW]
    └── create_advanced_pipeline_context() [NEW]
"""

from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import re

# Import base router
from intelligent_router import (
    IntelligentRouter,
    TaskRequirements,
    RoutingDecision,
    StageDecision
)

# Import advanced pipeline integration
from advanced_pipeline_integration import (
    PipelineMode,
    AdvancedPipelineConfig
)

# Import artemis core
from artemis_exceptions import (
    ArtemisException,
    wrap_exception,
    PipelineException
)
from debug_mixin import DebugMixin


# ============================================================================
# ENHANCED DATA STRUCTURES
# ============================================================================

@dataclass
class RiskFactor:
    """
    Identified risk factor in a task.

    WHY: Explicit risk identification enables Thermodynamic Computing to
    quantify uncertainty and Monte Carlo simulation to assess probability.
    """
    risk_type: str  # 'technical', 'complexity', 'dependency', 'security', 'performance'
    description: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    probability: float  # 0.0-1.0 estimated probability of risk occurring
    mitigation: str  # Suggested mitigation strategy


@dataclass
class UncertaintyAnalysis:
    """
    Analysis of task uncertainty.

    WHY: Provides structured input to Thermodynamic Computing for
    Bayesian learning and confidence estimation.
    """
    overall_uncertainty: float  # 0.0-1.0 (0=certain, 1=completely uncertain)
    uncertainty_sources: List[str]  # Sources of uncertainty
    known_unknowns: List[str]  # Things we know we don't know
    similar_task_history: int  # Number of similar past tasks
    confidence_level: str  # 'very_low', 'low', 'medium', 'high', 'very_high'


@dataclass
class AdvancedFeatureRecommendation:
    """
    Recommendation for intensity of ALL advanced features working in tandem.

    WHY: All three features work together simultaneously - this recommends
    HOW AGGRESSIVELY to use each feature, not WHETHER to enable them.

    Design Philosophy: Features are complementary layers, not alternatives
        - Thermodynamic: Always active, provides confidence scores throughout
        - Two-Pass: Optional layer, provides fast feedback + refinement
        - Dynamic: Always active within passes, optimization intensity varies

    Intensity Levels:
        0.0 = Minimal (feature present but not aggressive)
        0.5 = Moderate (balanced approach)
        1.0 = Maximum (full feature capability)
    """
    recommended_mode: PipelineMode

    # Intensity levels for each feature (0.0-1.0)
    thermodynamic_intensity: float  # How much uncertainty quantification
    two_pass_intensity: float       # 0.0=single pass, 1.0=full two-pass
    dynamic_intensity: float        # 0.0=sequential, 1.0=max parallelism

    # Legacy boolean flags (computed from intensity for backward compatibility)
    use_dynamic_pipeline: bool      # True if dynamic_intensity > 0.3
    use_two_pass: bool              # True if two_pass_intensity > 0.5
    use_thermodynamic: bool         # True if thermodynamic_intensity > 0.3

    rationale: str
    confidence_in_recommendation: float  # 0.0-1.0
    expected_benefits: List[str]  # Why these intensities will help


@dataclass
class EnhancedRoutingDecision(RoutingDecision):
    """
    Routing decision enhanced with advanced feature recommendations.

    WHY: Extends base RoutingDecision with information needed by
    advanced pipeline features. Maintains backward compatibility
    with existing orchestrator.
    """
    # Advanced feature recommendations
    feature_recommendation: AdvancedFeatureRecommendation = None

    # Uncertainty analysis for Thermodynamic Computing
    uncertainty_analysis: UncertaintyAnalysis = None

    # Risk factors for Monte Carlo simulation
    risk_factors: List[RiskFactor] = field(default_factory=list)

    # Context for advanced features
    thermodynamic_context: Dict[str, Any] = field(default_factory=dict)
    dynamic_pipeline_context: Dict[str, Any] = field(default_factory=dict)
    two_pass_context: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# ENHANCED INTELLIGENT ROUTER
# ============================================================================

class IntelligentRouterEnhanced(IntelligentRouter):
    """
    Enhanced intelligent router with advanced feature integration.

    WHY: Router already analyzes task requirements - perfect position to
    recommend which advanced features would be most beneficial. Extends
    base router without breaking existing functionality.

    New Capabilities:
        1. Pipeline Mode Recommendation: Suggest STANDARD/DYNAMIC/TWO_PASS/ADAPTIVE/FULL
        2. Uncertainty Quantification: Calculate task uncertainty for Thermodynamic Computing
        3. Risk Identification: Identify risk factors for Monte Carlo simulation
        4. Two-Pass Detection: Recognize when two-pass would provide value
        5. Context Creation: Build rich context for each advanced feature

    Design Principle: Liskov Substitution
        - Can be used anywhere IntelligentRouter is used
        - Adds new methods without breaking existing interface
        - Enhanced routing decision is superset of base decision
    """

    def __init__(
        self,
        ai_service=None,
        logger=None,
        config=None,
        advanced_config: Optional[AdvancedPipelineConfig] = None
    ):
        """
        Initialize enhanced router.

        Args:
            ai_service: AI Query Service for requirement analysis
            logger: Logger for output
            config: Base configuration for routing rules
            advanced_config: Configuration for advanced pipeline features
        """
        # Initialize base router
        super().__init__(ai_service, logger, config)

        # Advanced feature configuration
        self.advanced_config = advanced_config or AdvancedPipelineConfig()

        # Patterns for risk detection (pre-compiled for performance)
        self.RISK_PATTERNS = {
            'security': re.compile(
                r'\b(auth|security|encrypt|password|token|session|csrf|xss|sql\s*injection|vulnerability)\b',
                re.IGNORECASE
            ),
            'performance': re.compile(
                r'\b(performance|scalability|optimization|latency|throughput|load|stress)\b',
                re.IGNORECASE
            ),
            'database': re.compile(
                r'\b(migration|schema\s*change|data\s*loss|rollback|transaction|consistency)\b',
                re.IGNORECASE
            ),
            'integration': re.compile(
                r'\b(integration|external\s*api|third[\s-]party|dependency|breaking\s*change)\b',
                re.IGNORECASE
            ),
            'complexity': re.compile(
                r'\b(complex|complicated|difficult|challenging|unknown|uncertain|unclear)\b',
                re.IGNORECASE
            )
        }

        # Keywords suggesting two-pass would be valuable
        self.TWO_PASS_KEYWORDS = [
            'prototype', 'experiment', 'poc', 'proof of concept',
            'explore', 'investigate', 'research', 'try',
            'refactor', 'rewrite', 'redesign'
        ]

        # Keywords suggesting high uncertainty (thermodynamic computing valuable)
        self.UNCERTAINTY_KEYWORDS = [
            'unknown', 'uncertain', 'unclear', 'ambiguous',
            'research', 'investigate', 'explore', 'experimental',
            'new technology', 'never done', 'unfamiliar'
        ]

    @wrap_exception(PipelineException, "Enhanced routing decision failed")
    def make_enhanced_routing_decision(self, card: Dict) -> EnhancedRoutingDecision:
        """
        Make complete routing decision with advanced feature recommendations.

        WHAT: Extends base routing decision with:
            - Advanced pipeline mode recommendation
            - Uncertainty analysis for Thermodynamic Computing
            - Risk factors for Monte Carlo simulation
            - Rich context for each advanced feature

        WHY: Single point of analysis that feeds all advanced features.
        Router already analyzes task - logical place to make feature recommendations.

        Args:
            card: Kanban card with task details

        Returns:
            EnhancedRoutingDecision with stage selection AND feature recommendations
        """
        # Get base routing decision (stage selection)
        base_decision = self.make_routing_decision(card)

        # Calculate uncertainty for Thermodynamic Computing
        uncertainty_analysis = self.calculate_task_uncertainty(
            card, base_decision.requirements
        )

        # Identify risk factors for Monte Carlo simulation
        risk_factors = self.identify_risk_factors(
            card, base_decision.requirements
        )

        # Recommend pipeline mode and features
        feature_recommendation = self.recommend_pipeline_mode(
            card,
            base_decision.requirements,
            uncertainty_analysis,
            risk_factors
        )

        # Create rich context for each advanced feature with intensity levels
        thermodynamic_context = self._create_thermodynamic_context(
            card, base_decision.requirements, uncertainty_analysis, risk_factors
        )

        dynamic_pipeline_context = self._create_dynamic_pipeline_context(
            card, base_decision.requirements,
            intensity=feature_recommendation.dynamic_intensity
        )

        two_pass_context = self._create_two_pass_context(
            card, base_decision.requirements, uncertainty_analysis,
            intensity=feature_recommendation.two_pass_intensity
        )

        # Create enhanced decision
        enhanced_decision = EnhancedRoutingDecision(
            task_id=base_decision.task_id,
            task_title=base_decision.task_title,
            requirements=base_decision.requirements,
            stage_decisions=base_decision.stage_decisions,
            stages_to_run=base_decision.stages_to_run,
            stages_to_skip=base_decision.stages_to_skip,
            reasoning=base_decision.reasoning,
            confidence_score=base_decision.confidence_score,
            feature_recommendation=feature_recommendation,
            uncertainty_analysis=uncertainty_analysis,
            risk_factors=risk_factors,
            thermodynamic_context=thermodynamic_context,
            dynamic_pipeline_context=dynamic_pipeline_context,
            two_pass_context=two_pass_context
        )

        # Log enhanced decision
        self._log_enhanced_decision(enhanced_decision)

        return enhanced_decision

    @wrap_exception(PipelineException, "Uncertainty calculation failed")
    def calculate_task_uncertainty(
        self,
        card: Dict,
        requirements: TaskRequirements
    ) -> UncertaintyAnalysis:
        """
        Calculate task uncertainty for Thermodynamic Computing.

        WHAT: Quantifies uncertainty based on:
            - Presence of uncertainty keywords
            - Lack of similar past tasks
            - Task complexity
            - Requirement clarity
            - External dependencies

        WHY: Thermodynamic Computing needs uncertainty input to:
            - Set appropriate confidence thresholds
            - Configure Monte Carlo simulation samples
            - Determine initial Bayesian priors
            - Decide temperature schedule for sampling

        Args:
            card: Kanban card with task details
            requirements: Analyzed task requirements

        Returns:
            UncertaintyAnalysis with quantified uncertainty
        """
        combined_text = f"{card.get('title', '')} {card.get('description', '')}".lower()

        # Calculate uncertainty components
        uncertainty_score = 0.0
        uncertainty_sources = []
        known_unknowns = []

        # Complexity contribution (complex = more uncertain)
        complexity_uncertainty = {
            'simple': 0.1,
            'medium': 0.3,
            'complex': 0.6
        }
        uncertainty_score += complexity_uncertainty.get(requirements.complexity, 0.3)
        uncertainty_sources.append(f"Task complexity: {requirements.complexity}")

        # Uncertainty keyword detection
        uncertainty_keyword_count = sum(
            1 for keyword in self.UNCERTAINTY_KEYWORDS
            if keyword in combined_text
        )
        if uncertainty_keyword_count > 0:
            uncertainty_score += min(0.3, uncertainty_keyword_count * 0.1)
            uncertainty_sources.append(
                f"Uncertainty keywords found: {uncertainty_keyword_count}"
            )
            known_unknowns.append("Task contains explicit uncertainty language")

        # External dependency uncertainty
        if requirements.has_external_dependencies:
            uncertainty_score += 0.15
            uncertainty_sources.append("External dependencies add uncertainty")
            known_unknowns.append("External API/library behavior")

        # Database migration uncertainty
        if requirements.has_database and 'migrat' in combined_text:
            uncertainty_score += 0.2
            uncertainty_sources.append("Database migration adds significant uncertainty")
            known_unknowns.append("Data migration edge cases and rollback scenarios")

        # New technology uncertainty
        new_tech_keywords = ['new technology', 'unfamiliar', 'never used', 'first time']
        if any(keyword in combined_text for keyword in new_tech_keywords):
            uncertainty_score += 0.25
            uncertainty_sources.append("New/unfamiliar technology")
            known_unknowns.append("Learning curve and unexpected behaviors")

        # Estimate similar task history (in real implementation, query from Thermodynamic Computing)
        # For now, use heuristics
        similar_task_history = self._estimate_similar_task_history(
            requirements.task_type,
            requirements.complexity
        )

        # Adjust uncertainty based on experience
        if similar_task_history == 0:
            uncertainty_score += 0.2
            uncertainty_sources.append("No prior experience with similar tasks")
        elif similar_task_history < 3:
            uncertainty_score += 0.1
            uncertainty_sources.append("Limited prior experience")
        elif similar_task_history >= 10:
            uncertainty_score -= 0.1  # Experience reduces uncertainty
            uncertainty_sources.append("Extensive prior experience")

        # Cap uncertainty at 1.0
        uncertainty_score = min(1.0, max(0.0, uncertainty_score))

        # Determine confidence level
        if uncertainty_score < 0.2:
            confidence_level = 'very_high'
        elif uncertainty_score < 0.4:
            confidence_level = 'high'
        elif uncertainty_score < 0.6:
            confidence_level = 'medium'
        elif uncertainty_score < 0.8:
            confidence_level = 'low'
        else:
            confidence_level = 'very_low'

        return UncertaintyAnalysis(
            overall_uncertainty=uncertainty_score,
            uncertainty_sources=uncertainty_sources,
            known_unknowns=known_unknowns if known_unknowns else ["None identified"],
            similar_task_history=similar_task_history,
            confidence_level=confidence_level
        )

    @wrap_exception(PipelineException, "Risk factor identification failed")
    def identify_risk_factors(
        self,
        card: Dict,
        requirements: TaskRequirements
    ) -> List[RiskFactor]:
        """
        Identify risk factors for Monte Carlo simulation.

        WHAT: Scans task description for risk patterns and creates structured
        risk factors with severity and probability estimates.

        WHY: Monte Carlo simulation needs risk factors to:
            - Simulate probability of failures
            - Calculate confidence intervals
            - Identify critical paths
            - Recommend mitigations

        Args:
            card: Kanban card with task details
            requirements: Analyzed task requirements

        Returns:
            List of identified risk factors
        """
        combined_text = f"{card.get('title', '')} {card.get('description', '')}".lower()
        risk_factors = []

        # Security risks
        if self.RISK_PATTERNS['security'].search(combined_text):
            risk_factors.append(RiskFactor(
                risk_type='security',
                description='Security-sensitive task requiring careful implementation',
                severity='high' if 'critical' in combined_text or 'auth' in combined_text else 'medium',
                probability=0.3,  # 30% chance of security issue if not careful
                mitigation='Add security review stage, penetration testing, OWASP guidelines'
            ))

        # Performance risks
        if self.RISK_PATTERNS['performance'].search(combined_text):
            risk_factors.append(RiskFactor(
                risk_type='performance',
                description='Performance-critical task with scalability concerns',
                severity='medium',
                probability=0.25,  # 25% chance of performance issues
                mitigation='Add performance testing, load testing, profiling'
            ))

        # Database risks
        if self.RISK_PATTERNS['database'].search(combined_text):
            severity = 'critical' if 'migration' in combined_text else 'high'
            probability = 0.4 if 'migration' in combined_text else 0.2

            risk_factors.append(RiskFactor(
                risk_type='database',
                description='Database changes with potential data loss or corruption',
                severity=severity,
                probability=probability,
                mitigation='Dry-run migration, rollback script, backup verification, staging test'
            ))

        # Integration risks
        if self.RISK_PATTERNS['integration'].search(combined_text) or requirements.has_external_dependencies:
            risk_factors.append(RiskFactor(
                risk_type='dependency',
                description='External dependencies with potential breaking changes',
                severity='medium',
                probability=0.20,  # 20% chance of integration issues
                mitigation='API contract testing, mock servers, version pinning, fallback strategies'
            ))

        # Complexity risks
        if self.RISK_PATTERNS['complexity'].search(combined_text) or requirements.complexity == 'complex':
            risk_factors.append(RiskFactor(
                risk_type='complexity',
                description='High complexity with potential for underestimation',
                severity='high' if requirements.estimated_story_points >= 13 else 'medium',
                probability=0.35,  # 35% chance of complexity-related issues
                mitigation='Break into smaller tasks, architecture review, incremental delivery'
            ))

        return risk_factors

    @wrap_exception(PipelineException, "Pipeline mode recommendation failed")
    def recommend_pipeline_mode(
        self,
        card: Dict,
        requirements: TaskRequirements,
        uncertainty: UncertaintyAnalysis,
        risks: List[RiskFactor]
    ) -> AdvancedFeatureRecommendation:
        """
        Recommend intensity levels for ALL THREE advanced features working in tandem.

        WHAT: Analyzes task characteristics and recommends:
            - Pipeline execution mode (STANDARD/DYNAMIC/TWO_PASS/ADAPTIVE/FULL)
            - Intensity levels (0.0-1.0) for each advanced feature
            - Rationale for recommendations

        WHY: All three features work as complementary layers:
            - Thermodynamic: Provides intelligence throughout (always active)
            - Two-Pass: Execution strategy (intensity varies by task)
            - Dynamic: Optimization within passes (always active, intensity varies)

        Changed from: Recommending which features to enable (binary choice)
        Changed to: Recommending how aggressively to use each feature (intensity)

        Decision Algorithm:
            1. Calculate benefit scores for each feature (0.0-1.0)
            2. Consider task characteristics, uncertainty, risks
            3. Select mode based on scores (mode = intensity configuration)
            4. Map mode to intensity levels for all three features

        Args:
            card: Kanban card with task details
            requirements: Analyzed task requirements
            uncertainty: Calculated uncertainty analysis
            risks: Identified risk factors

        Returns:
            Recommendation with intensity levels for all three features
        """
        combined_text = f"{card.get('title', '')} {card.get('description', '')}".lower()

        # Calculate benefit scores for each feature (0.0-1.0)
        # These represent how much each feature would help this task
        dynamic_benefit = self._calculate_dynamic_pipeline_benefit(requirements)
        two_pass_benefit = self._calculate_two_pass_benefit(
            requirements, uncertainty, combined_text
        )
        thermodynamic_benefit = self._calculate_thermodynamic_benefit(
            uncertainty, risks
        )

        # Determine mode using dispatch table
        # WHY dispatch table: Declarative, no elif chains, easy to tune
        # Mode represents an intensity configuration for all three features
        mode_selection_rules = [
            # (condition, mode, rationale)
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

        # Map mode to intensity levels for ALL THREE features
        # All features always have some intensity (they work in tandem)
        # Mode determines the intensity configuration, not which features to enable
        MODE_INTENSITY_MAP = {
            # Mode: (thermodynamic_intensity, two_pass_intensity, dynamic_intensity)
            PipelineMode.STANDARD: (0.2, 0.0, 0.2),  # Minimal - simple tasks
            PipelineMode.DYNAMIC: (0.5, 0.0, 0.8),   # Moderate therm, no two-pass, high dynamic
            PipelineMode.TWO_PASS: (0.6, 1.0, 0.6),  # High therm, full two-pass, moderate dynamic
            PipelineMode.ADAPTIVE: (1.0, 0.0, 0.8),  # Max therm, no two-pass, high dynamic
            PipelineMode.FULL: (1.0, 1.0, 1.0)       # Maximum intensity for all
        }

        # Get base intensity levels from mode
        therm_intensity, two_pass_intensity, dynamic_intensity = MODE_INTENSITY_MAP[recommended_mode]

        # Fine-tune intensities using Strategy pattern
        # WHY Strategy pattern: Declarative, no sequential ifs, easy to extend
        intensities = self._fine_tune_intensities(
            mode=recommended_mode,
            base_intensities=(therm_intensity, two_pass_intensity, dynamic_intensity),
            benefits=(thermodynamic_benefit, two_pass_benefit, dynamic_benefit)
        )
        therm_intensity, two_pass_intensity, dynamic_intensity = intensities

        # Determine legacy boolean flags for backward compatibility
        # Computed from intensities using thresholds
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

    # ========================================================================
    # HELPER METHODS (EXTRACTED FOR CLARITY)
    # ========================================================================

    def _calculate_dynamic_pipeline_benefit(
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
        # (In full implementation, query stage count from routing decision)
        if requirements.complexity in ['medium', 'complex']:
            benefit += 0.3

        # External dependencies → benefit from conditional execution
        if requirements.has_external_dependencies:
            benefit += 0.2

        return min(1.0, benefit)

    def _calculate_two_pass_benefit(
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
        keyword_matches = sum(1 for kw in self.TWO_PASS_KEYWORDS if kw in text)
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

    def _calculate_thermodynamic_benefit(
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

        # Multiple risks → Monte Carlo valuable
        if len(risks) >= 3:
            benefit += 0.3
        elif len(risks) >= 1:
            benefit += 0.15

        # Low prior experience → Bayesian learning valuable
        if uncertainty.similar_task_history < 3:
            benefit += 0.2

        # Critical risks → risk quantification essential
        critical_risks = [r for r in risks if r.severity in ['critical', 'high']]
        if len(critical_risks) >= 2:
            benefit += 0.2
        elif len(critical_risks) == 1:
            benefit += 0.1

        return min(1.0, benefit)

    def _fine_tune_intensities(
        self,
        mode: PipelineMode,
        base_intensities: Tuple[float, float, float],
        benefits: Tuple[float, float, float]
    ) -> Tuple[float, float, float]:
        """
        Fine-tune intensity levels based on mode and benefits using Strategy pattern.

        WHAT: Adjusts base intensities from mode using task-specific benefit scores.
        WHY Strategy pattern: Declarative dispatch table, no sequential ifs, easy to extend.

        Each mode has a tuning strategy that determines:
        - Which intensities to adjust
        - Scaling factors for adjustment
        - Min/max bounds

        Args:
            mode: Selected pipeline mode
            base_intensities: (therm, two_pass, dynamic) from MODE_INTENSITY_MAP
            benefits: (therm_benefit, two_pass_benefit, dynamic_benefit)

        Returns:
            Tuple of (therm_intensity, two_pass_intensity, dynamic_intensity)
        """
        therm_base, two_pass_base, dynamic_base = base_intensities
        therm_benefit, two_pass_benefit, dynamic_benefit = benefits

        # Intensity tuning strategies dispatch table
        # WHY dispatch table: Maps mode → tuning function, no if/elif chain
        INTENSITY_TUNING_STRATEGIES = {
            PipelineMode.STANDARD: lambda: (
                # Thermodynamic: Always tune (always active)
                max(0.2, therm_base * (0.2 + therm_benefit * 0.8)),
                # Two-Pass: Off, no tuning
                two_pass_base,
                # Dynamic: Minimal, light tuning
                max(0.2, dynamic_base * (0.5 + dynamic_benefit * 0.5))
            ),
            PipelineMode.DYNAMIC: lambda: (
                # Thermodynamic: Always tune
                max(0.2, therm_base * (0.2 + therm_benefit * 0.8)),
                # Two-Pass: Off, no tuning
                two_pass_base,
                # Dynamic: High intensity, significant tuning
                max(0.5, dynamic_base * (0.5 + dynamic_benefit * 0.5))
            ),
            PipelineMode.TWO_PASS: lambda: (
                # Thermodynamic: Always tune
                max(0.2, therm_base * (0.2 + therm_benefit * 0.8)),
                # Two-Pass: Full tuning (on with varying intensity)
                max(0.6, two_pass_base * (0.6 + two_pass_benefit * 0.4)),
                # Dynamic: Moderate tuning
                max(0.5, dynamic_base * (0.5 + dynamic_benefit * 0.5))
            ),
            PipelineMode.ADAPTIVE: lambda: (
                # Thermodynamic: Maximum tuning
                max(0.2, therm_base * (0.2 + therm_benefit * 0.8)),
                # Two-Pass: Off, no tuning
                two_pass_base,
                # Dynamic: High tuning
                max(0.5, dynamic_base * (0.5 + dynamic_benefit * 0.5))
            ),
            PipelineMode.FULL: lambda: (
                # Thermodynamic: Maximum tuning
                max(0.2, therm_base * (0.2 + therm_benefit * 0.8)),
                # Two-Pass: Maximum tuning
                max(0.6, two_pass_base * (0.6 + two_pass_benefit * 0.4)),
                # Dynamic: Maximum tuning
                max(0.5, dynamic_base * (0.5 + dynamic_benefit * 0.5))
            )
        }

        # Dispatch to appropriate strategy
        tuning_strategy = INTENSITY_TUNING_STRATEGIES.get(mode)
        if not tuning_strategy:
            # Fallback: Return base intensities unmodified
            self.logger.warning(f"No tuning strategy for mode {mode}, using base intensities")
            return base_intensities

        return tuning_strategy()

    def _calculate_recommendation_confidence(
        self,
        requirements: TaskRequirements,
        uncertainty: UncertaintyAnalysis,
        risks: List[RiskFactor]
    ) -> float:
        """
        Calculate confidence in feature recommendation (0.0-1.0).

        WHY: Provides meta-uncertainty - how confident are we in our recommendation?
        Useful for deciding whether to override automatic selection.
        """
        confidence = 0.8  # Start with base confidence

        # Reduce confidence for high uncertainty tasks
        confidence -= uncertainty.overall_uncertainty * 0.2

        # Reduce confidence for unfamiliar task types
        if uncertainty.similar_task_history == 0:
            confidence -= 0.1

        # Increase confidence for clear patterns
        if requirements.task_type in ['bugfix', 'documentation']:
            confidence += 0.1  # Well-understood task types

        return max(0.3, min(1.0, confidence))

    def _estimate_similar_task_history(
        self,
        task_type: str,
        complexity: str
    ) -> int:
        """
        Estimate number of similar past tasks.

        WHY: In full implementation, would query Thermodynamic Computing's
        Bayesian priors. For now, use heuristics based on common task types.

        This is a placeholder - real implementation would query historical data.
        """
        # Heuristic estimates (replace with actual historical query)
        common_tasks = {
            ('bugfix', 'simple'): 20,
            ('bugfix', 'medium'): 10,
            ('feature', 'simple'): 15,
            ('feature', 'medium'): 8,
            ('feature', 'complex'): 3,
            ('refactor', 'medium'): 5,
            ('refactor', 'complex'): 2,
            ('documentation', 'simple'): 25,
        }

        return common_tasks.get((task_type, complexity), 0)

    # ========================================================================
    # CONTEXT CREATION FOR ADVANCED FEATURES
    # ========================================================================

    def _create_thermodynamic_context(
        self,
        card: Dict,
        requirements: TaskRequirements,
        uncertainty: UncertaintyAnalysis,
        risks: List[RiskFactor]
    ) -> Dict[str, Any]:
        """
        Create rich context for Thermodynamic Computing.

        WHY: Thermodynamic Computing needs context to:
            - Select appropriate uncertainty strategy (Bayesian, Monte Carlo, Ensemble)
            - Set confidence thresholds
            - Initialize priors
            - Configure temperature schedule
        """
        # Calculate risk statistics
        high_risk_count = len([r for r in risks if r.severity in ['high', 'critical']])
        total_risk_probability = sum(r.probability for r in risks)

        # Generate comprehensive prompt
        prompt = self._generate_thermodynamic_prompt(
            card, requirements, uncertainty, risks
        )

        return {
            # Task characteristics
            'task_type': requirements.task_type,
            'complexity': requirements.complexity,
            'story_points': requirements.estimated_story_points,
            'task_title': card.get('title', ''),
            'task_description': card.get('description', ''),

            # Uncertainty analysis
            'uncertainty_level': uncertainty.overall_uncertainty,
            'confidence_level': uncertainty.confidence_level,
            'similar_task_count': uncertainty.similar_task_history,
            'uncertainty_sources': uncertainty.uncertainty_sources,
            'known_unknowns': uncertainty.known_unknowns,

            # Risk information
            'risk_count': len(risks),
            'high_risk_count': high_risk_count,
            'total_risk_probability': total_risk_probability,
            'risk_details': [
                {
                    'type': r.risk_type,
                    'severity': r.severity,
                    'probability': r.probability,
                    'description': r.description,
                    'mitigation': r.mitigation
                }
                for r in risks
            ],

            # Strategy recommendations
            'suggested_strategy': self._suggest_uncertainty_strategy(uncertainty, risks),
            'suggested_samples': self._suggest_monte_carlo_samples(risks),
            'suggested_temperature': self._suggest_initial_temperature(uncertainty),

            # Configuration from config (not hardcoded)
            'confidence_threshold': self.advanced_config.confidence_threshold,
            'default_strategy': self.advanced_config.default_uncertainty_strategy,
            'enable_temperature_annealing': self.advanced_config.enable_temperature_annealing,
            'temperature_schedule': self.advanced_config.temperature_schedule,
            'initial_temperature': self.advanced_config.initial_temperature,
            'final_temperature': self.advanced_config.final_temperature,

            # AI service access for LLM calls
            'ai_service': self.ai_query_service,

            # Guidance prompt
            'prompt': prompt
        }

    def _create_dynamic_pipeline_context(
        self,
        card: Dict,
        requirements: TaskRequirements,
        intensity: float
    ) -> Dict[str, Any]:
        """
        Create context for Dynamic Pipeline.

        WHY: Dynamic Pipeline needs context to:
            - Select stage selection strategy
            - Configure parallel execution
            - Set retry policies
            - Allocate resources
        """
        # Generate comprehensive prompt
        prompt = self._generate_dynamic_pipeline_prompt(
            card, requirements, intensity
        )

        # Get config values with intensity scaling
        base_max_workers = self.advanced_config.max_parallel_workers
        max_workers = int(1 + intensity * (base_max_workers - 1))

        return {
            # Task characteristics
            'task_type': requirements.task_type,
            'complexity': requirements.complexity,
            'story_points': requirements.estimated_story_points,
            'task_title': card.get('title', ''),
            'task_description': card.get('description', ''),

            # Execution parameters (intensity-scaled)
            'intensity': intensity,
            'estimated_duration_hours': requirements.estimated_story_points * 2,
            'parallel_developers': requirements.parallel_developers_recommended,
            'suggested_max_workers': max_workers,
            'suggested_retry_attempts': self._suggest_retry_attempts(requirements),
            'suggested_timeout_minutes': requirements.estimated_story_points * 10,

            # Task requirements
            'has_database': requirements.has_database,
            'has_external_deps': requirements.has_external_dependencies,
            'requires_frontend': requirements.requires_frontend,
            'requires_backend': requirements.requires_backend,
            'requires_api': requirements.requires_api,

            # Stage selection hints
            'stages_to_prioritize': self._identify_priority_stages(requirements),
            'stages_optional': self._identify_optional_stages(requirements),

            # Configuration from config (not hardcoded)
            'parallel_execution_enabled': self.advanced_config.parallel_execution_enabled,
            'stage_caching_enabled': self.advanced_config.stage_result_caching_enabled,

            # AI service access for LLM calls
            'ai_service': self.ai_query_service,

            # Guidance prompt
            'prompt': prompt
        }

    def _create_two_pass_context(
        self,
        card: Dict,
        requirements: TaskRequirements,
        uncertainty: UncertaintyAnalysis,
        intensity: float
    ) -> Dict[str, Any]:
        """
        Create context for Two-Pass Pipeline.

        WHY: Two-Pass Pipeline needs context to:
            - Configure first pass timeout
            - Set quality thresholds for rollback
            - Decide if second pass needed
            - Configure learning transfer
        """
        # Generate comprehensive prompt
        prompt = self._generate_two_pass_prompt(
            card, requirements, uncertainty, intensity
        )

        # Calculate timeouts from config with intensity scaling
        base_first_pass_timeout = 30  # seconds - quick analysis
        first_pass_timeout = int(base_first_pass_timeout * (1.0 + intensity * 0.5))

        # Second pass timeout from config multiplier
        estimated_total_minutes = requirements.estimated_story_points * 10
        second_pass_timeout = int(estimated_total_minutes * (1.0 - self.advanced_config.first_pass_timeout_multiplier))

        # Quality threshold based on uncertainty and intensity
        base_threshold = self.advanced_config.confidence_threshold
        quality_threshold = base_threshold + (intensity * 0.15)  # Higher intensity = higher threshold

        return {
            # Task characteristics
            'task_type': requirements.task_type,
            'complexity': requirements.complexity,
            'story_points': requirements.estimated_story_points,
            'task_title': card.get('title', ''),
            'task_description': card.get('description', ''),

            # Uncertainty information
            'uncertainty_level': uncertainty.overall_uncertainty,
            'confidence_level': uncertainty.confidence_level,
            'uncertainty_sources': uncertainty.uncertainty_sources,
            'known_unknowns': uncertainty.known_unknowns,

            # Pass configuration (intensity-scaled)
            'intensity': intensity,
            'suggested_first_pass_timeout_seconds': first_pass_timeout,
            'suggested_second_pass_timeout_minutes': second_pass_timeout,
            'suggested_quality_threshold': quality_threshold,

            # Learning configuration
            'learning_transfer_enabled': True,
            'capture_learnings_from_first_pass': [
                'Architectural decisions and trade-offs',
                'Risk mitigation strategies',
                'Known unknowns that became known',
                'Performance bottlenecks identified',
                'Integration challenges discovered'
            ],

            # Rollback configuration from config (not hardcoded)
            'enable_rollback': self.advanced_config.two_pass_auto_rollback,
            'rollback_degradation_threshold': self.advanced_config.rollback_degradation_threshold,
            'quality_improvement_threshold': self.advanced_config.quality_improvement_threshold,

            # First pass guidance
            'first_pass_focus': [
                'Quick architecture validation',
                'Risk identification',
                'Feasibility assessment',
                'Dependencies discovery',
                'Complexity estimation refinement'
            ],

            # Second pass guidance
            'second_pass_focus': [
                'Full implementation with learnings applied',
                'Risk mitigations from first pass',
                'Comprehensive testing',
                'Performance optimization',
                'Code quality and maintainability'
            ],

            # AI service access for LLM calls
            'ai_service': self.ai_query_service,

            # Guidance prompt
            'prompt': prompt
        }

    def _suggest_uncertainty_strategy(
        self,
        uncertainty: UncertaintyAnalysis,
        risks: List[RiskFactor]
    ) -> str:
        """
        Suggest which uncertainty strategy to use.

        WHY: Different strategies optimal for different scenarios:
            - Bayesian: Tasks with prior experience
            - Monte Carlo: Tasks with multiple risk factors
            - Ensemble: High-stakes tasks needing multiple perspectives
        """
        if len(risks) >= 3:
            return 'monte_carlo'  # Multiple risks → simulate outcomes
        elif uncertainty.similar_task_history >= 5:
            return 'bayesian'  # Prior experience → learn from outcomes
        elif uncertainty.overall_uncertainty > 0.7:
            return 'ensemble'  # High uncertainty → multiple models
        else:
            return 'bayesian'  # Default

    def _suggest_monte_carlo_samples(self, risks: List[RiskFactor]) -> int:
        """
        Suggest number of Monte Carlo simulation samples.

        WHY: More risks → need more samples for accurate risk quantification.
        """
        if len(risks) >= 3:
            return 5000  # Many risks → high sample count
        elif len(risks) >= 1:
            return 1000  # Some risks → moderate sample count
        else:
            return 500   # Few risks → low sample count

    def _suggest_initial_temperature(self, uncertainty: UncertaintyAnalysis) -> float:
        """
        Suggest initial temperature for temperature sampling.

        WHY: High uncertainty → high temperature (explore diverse solutions).
        Low uncertainty → low temperature (exploit known best).
        """
        # Map uncertainty to temperature (0.5 - 2.0 range)
        return 0.5 + (uncertainty.overall_uncertainty * 1.5)

    def _suggest_max_workers(self, requirements: TaskRequirements) -> int:
        """
        Suggest max parallel workers for Dynamic Pipeline.

        WHY: Complex tasks benefit from parallelism, simple tasks don't.
        """
        if requirements.complexity == 'complex':
            return 8
        elif requirements.complexity == 'medium':
            return 4
        else:
            return 2

    def _suggest_retry_attempts(self, requirements: TaskRequirements) -> int:
        """
        Suggest retry attempts for Dynamic Pipeline.

        WHY: Complex/risky tasks need more retries for transient failures.
        """
        if requirements.complexity == 'complex' or requirements.has_external_dependencies:
            return 3
        elif requirements.complexity == 'medium':
            return 2
        else:
            return 1

    # ========================================================================
    # PROMPT GENERATION FOR ADVANCED FEATURES
    # ========================================================================

    def _generate_thermodynamic_prompt(
        self,
        card: Dict,
        requirements: TaskRequirements,
        uncertainty: UncertaintyAnalysis,
        risks: List[RiskFactor]
    ) -> str:
        """
        Generate comprehensive prompt for Thermodynamic Computing.

        WHY: Provides rich context explaining WHAT to do and WHY, helping
        the feature make informed decisions about uncertainty quantification.
        """
        risk_summary = "\n".join([
            f"  - {r.risk_type.upper()} ({r.severity}): {r.description}"
            for r in risks
        ])

        return f"""## Thermodynamic Computing Guidance

### Task Overview
**Title**: {card.get('title', 'Unknown')}
**Complexity**: {requirements.complexity}
**Story Points**: {requirements.estimated_story_points}
**Type**: {requirements.task_type}

### Uncertainty Analysis
**Overall Uncertainty**: {uncertainty.overall_uncertainty:.0%}
**Confidence Level**: {uncertainty.confidence_level}
**Similar Tasks in History**: {uncertainty.similar_task_history}

**Uncertainty Sources**:
{chr(10).join(f"  - {source}" for source in uncertainty.uncertainty_sources)}

**Known Unknowns**:
{chr(10).join(f"  - {unknown}" for unknown in uncertainty.known_unknowns)}

### Risk Factors ({len(risks)} identified)
{risk_summary if risks else "  No significant risks identified"}

### Your Mission
Use Thermodynamic Computing to:

1. **Quantify Uncertainty** ({uncertainty.overall_uncertainty:.0%} current)
   - Track confidence scores throughout execution
   - Update as unknowns become known
   - Provide probabilistic estimates for outcomes

2. **Risk Quantification**
   - Run Monte Carlo simulations for {len(risks)} risk factors
   - Calculate probability distributions for outcomes
   - Identify high-impact, high-probability risks

3. **Bayesian Learning**
   - Update priors based on similar tasks ({uncertainty.similar_task_history} in history)
   - Learn from this execution for future tasks
   - Improve confidence estimates over time

4. **Decision Support**
   - Provide confidence intervals for estimates
   - Recommend when to seek human input
   - Suggest risk mitigations based on simulations

### Expected Outcomes
- Confidence trajectory: {uncertainty.overall_uncertainty:.0%} → 85%+
- Risk assessment: Quantified probabilities for all {len(risks)} risks
- Learning: Updated Bayesian priors for future similar tasks
"""

    def _generate_dynamic_pipeline_prompt(
        self,
        card: Dict,
        requirements: TaskRequirements,
        intensity: float
    ) -> str:
        """
        Generate comprehensive prompt for Dynamic Pipeline.

        WHY: Provides guidance on HOW to optimize execution based on
        task characteristics and intensity level.
        """
        return f"""## Dynamic Pipeline Guidance

### Task Overview
**Title**: {card.get('title', 'Unknown')}
**Complexity**: {requirements.complexity}
**Story Points**: {requirements.estimated_story_points}
**Type**: {requirements.task_type}

### Execution Intensity: {intensity:.0%}
**Meaning**: {"Maximum parallelization and optimization" if intensity > 0.8 else
              "High parallelization" if intensity > 0.6 else
              "Moderate optimization" if intensity > 0.3 else
              "Sequential execution with minimal overhead"}

### Your Mission
Optimize pipeline execution using Dynamic Pipeline at {intensity:.0%} intensity:

1. **Stage Selection** (Intensity: {intensity:.0%})
   {"- Aggressively parallelize all independent stages" if intensity > 0.7 else
    "- Parallelize some independent stages" if intensity > 0.4 else
    "- Mostly sequential execution"}
   - Skip unnecessary stages based on requirements
   - Prioritize critical path stages
   - Cache results for reuse

2. **Resource Allocation**
   - Workers: Scale up to {int(1 + intensity * 7)} parallel workers
   - Retries: {self._suggest_retry_attempts(requirements)} attempts per stage
   - Timeout: {requirements.estimated_story_points * 10} minutes per stage

3. **Optimization Strategies**
   {"- Maximum: Aggressive parallelization, extensive caching, fast failure detection" if intensity > 0.8 else
    "- High: Significant parallelization, selective caching" if intensity > 0.6 else
    "- Moderate: Some parallelization, minimal caching" if intensity > 0.3 else
    "- Minimal: Sequential execution, basic error handling"}

4. **Monitoring & Adaptation**
   - Track stage execution times
   - Detect bottlenecks early
   - Adjust parallelization if needed
   - Learn optimal configurations

### Task-Specific Guidance
**Requirements**: {', '.join([
    'Frontend' if requirements.requires_frontend else '',
    'Backend' if requirements.requires_backend else '',
    'API' if requirements.requires_api else '',
    'Database' if requirements.has_database else '',
    'External Dependencies' if requirements.has_external_dependencies else ''
]).strip(', ')}

**Priority Stages**: Focus optimization efforts on stages that handle above requirements.

### Expected Outcomes
- Execution time: ~{requirements.estimated_story_points * 2} hours
- Time savings: {int(intensity * 30)}% vs sequential
- Resource utilization: {intensity:.0%} of maximum capacity
"""

    def _generate_two_pass_prompt(
        self,
        card: Dict,
        requirements: TaskRequirements,
        uncertainty: UncertaintyAnalysis,
        intensity: float
    ) -> str:
        """
        Generate comprehensive prompt for Two-Pass Pipeline.

        WHY: Provides clear guidance on WHAT to focus on in each pass
        and HOW to transfer learnings between passes.
        """
        return f"""## Two-Pass Pipeline Guidance

### Task Overview
**Title**: {card.get('title', 'Unknown')}
**Complexity**: {requirements.complexity}
**Story Points**: {requirements.estimated_story_points}
**Uncertainty**: {uncertainty.overall_uncertainty:.0%}

### Two-Pass Intensity: {intensity:.0%}
**Meaning**: {"Aggressive two-pass with high quality threshold" if intensity > 0.8 else
              "Full two-pass with rollback enabled" if intensity > 0.6 else
              "Moderate two-pass approach" if intensity > 0.3 else
              "Single pass (two-pass disabled)"}

### Your Mission
Execute using two-pass strategy at {intensity:.0%} intensity:

## FIRST PASS (~30 seconds)

### Focus Areas:
1. **Quick Architecture Validation**
   - Verify approach is feasible
   - Identify architectural risks
   - Validate key assumptions

2. **Risk Discovery**
   - Scan for security concerns
   - Identify performance bottlenecks
   - Find integration challenges

3. **Uncertainty Reduction**
   Current unknowns:
{chr(10).join(f"   - {unknown}" for unknown in uncertainty.known_unknowns)}

   Goal: Convert as many unknowns to knowns as possible

4. **Complexity Refinement**
   - Initial estimate: {requirements.estimated_story_points} points
   - Refine based on discoveries
   - Adjust second pass plan

### First Pass Outputs:
- **Architecture Decision**: Chosen approach and trade-offs
- **Risk List**: All identified risks with severity
- **Learnings**: Key insights about the task
- **Refined Estimate**: Updated story points if needed
- **Go/No-Go Decision**: Continue to second pass?

---

## SECOND PASS (~{requirements.estimated_story_points * 5} minutes)

### Focus Areas:
1. **Full Implementation**
   - Apply architecture from first pass
   - Implement with learnings applied
   - Address all identified risks

2. **Risk Mitigation**
   - Apply mitigations for each discovered risk
   - Add safeguards and error handling
   - Implement security measures

3. **Quality Optimization**
   - Target quality: {0.70 + intensity * 0.15:.0%}
   - Comprehensive testing
   - Code review and refinement

4. **Learning Capture**
   - Document what worked/didn't work
   - Update Bayesian priors
   - Share insights for future tasks

### Success Criteria:
- Quality threshold: {0.70 + intensity * 0.15:.0%}
- All risks mitigated
- All tests passing
- Code meets standards

### Rollback Conditions:
- Quality drops below {0.70 + intensity * 0.15 - 0.1:.0%}
- Critical functionality broken
- Significant regressions detected

If rollback triggered: Revert to first pass state and report findings.

### Expected Outcomes
- First pass: Architecture validated, risks identified
- Second pass: High-quality implementation with risk mitigations
- Learning: Updated priors for future similar tasks
"""

    def _identify_priority_stages(self, requirements: TaskRequirements) -> List[str]:
        """
        Identify which stages should be prioritized based on requirements.

        WHY: Dynamic Pipeline can optimize by focusing resources on
        high-priority stages and de-prioritizing or skipping others.
        """
        priority_stages = []

        if requirements.requires_frontend:
            priority_stages.append('ui_ux_stage')
        if requirements.requires_backend:
            priority_stages.append('implementation_stage')
        if requirements.requires_api:
            priority_stages.append('api_design_stage')
        if requirements.has_database:
            priority_stages.append('data_model_stage')

        # Always prioritize these for complex tasks
        if requirements.complexity in ['medium', 'complex']:
            priority_stages.extend(['architecture_stage', 'code_review_stage'])

        return priority_stages

    def _identify_optional_stages(self, requirements: TaskRequirements) -> List[str]:
        """
        Identify which stages are optional and can be skipped.

        WHY: Dynamic Pipeline can save time by skipping stages that
        don't add value for this specific task.
        """
        optional_stages = []

        if not requirements.requires_frontend:
            optional_stages.append('ui_ux_stage')
        if not requirements.has_database:
            optional_stages.append('data_model_stage')
        if not requirements.requires_api:
            optional_stages.append('api_design_stage')

        # Simple tasks can skip some quality stages
        if requirements.complexity == 'simple':
            optional_stages.extend(['architecture_stage', 'performance_stage'])

        return optional_stages

    # ========================================================================
    # LOGGING
    # ========================================================================

    def _log_enhanced_decision(self, decision: EnhancedRoutingDecision) -> None:
        """
        Log enhanced routing decision with advanced feature recommendations.

        WHY: Transparency into why advanced features were recommended.
        Helps with debugging, tuning, and user trust.
        """
        if not self.logger:
            return

        # Log base routing decision (inherited)
        self.log_routing_decision(decision)

        # Log advanced feature recommendations
        self.logger.log("=" * 60, "INFO")
        self.logger.log("🚀 ADVANCED FEATURE RECOMMENDATIONS", "INFO")
        self.logger.log("=" * 60, "INFO")

        rec = decision.feature_recommendation
        self.logger.log(f"Recommended Mode: {rec.recommended_mode.value.upper()}", "INFO")
        self.logger.log(f"Confidence: {rec.confidence_in_recommendation:.0%}", "INFO")
        self.logger.log(f"Rationale: {rec.rationale}", "INFO")
        self.logger.log("", "INFO")

        self.logger.log("Features to Enable:", "INFO")
        self.logger.log(f"  Dynamic Pipeline: {'✓' if rec.use_dynamic_pipeline else '✗'}", "INFO")
        self.logger.log(f"  Two-Pass: {'✓' if rec.use_two_pass else '✗'}", "INFO")
        self.logger.log(f"  Thermodynamic: {'✓' if rec.use_thermodynamic else '✗'}", "INFO")
        self.logger.log("", "INFO")

        if rec.expected_benefits:
            self.logger.log("Expected Benefits:", "INFO")
            for benefit in rec.expected_benefits:
                self.logger.log(f"  • {benefit}", "INFO")
            self.logger.log("", "INFO")

        # Log uncertainty analysis
        unc = decision.uncertainty_analysis
        self.logger.log("Uncertainty Analysis:", "INFO")
        self.logger.log(f"  Overall: {unc.overall_uncertainty:.0%} ({unc.confidence_level})", "INFO")
        self.logger.log(f"  Similar Tasks: {unc.similar_task_history}", "INFO")
        if unc.known_unknowns:
            self.logger.log(f"  Known Unknowns:", "INFO")
            for unknown in unc.known_unknowns[:3]:  # Limit to 3
                self.logger.log(f"    - {unknown}", "INFO")
        self.logger.log("", "INFO")

        # Log risk factors
        if decision.risk_factors:
            self.logger.log(f"Risk Factors Identified: {len(decision.risk_factors)}", "INFO")
            for risk in decision.risk_factors:
                self.logger.log(
                    f"  ⚠️  {risk.risk_type.upper()}: {risk.description} "
                    f"(severity: {risk.severity}, probability: {risk.probability:.0%})",
                    "WARNING" if risk.severity in ['high', 'critical'] else "INFO"
                )
            self.logger.log("", "INFO")

        self.logger.log("=" * 60, "INFO")
