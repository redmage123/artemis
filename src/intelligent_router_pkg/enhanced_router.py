#!/usr/bin/env python3
"""
Enhanced Intelligent Router

WHAT: Enhanced intelligent router with advanced feature integration.

WHY: Router already analyzes task requirements - perfect position to
recommend which advanced features would be most beneficial.

RESPONSIBILITY:
    - Extend base IntelligentRouter functionality
    - Make enhanced routing decisions with feature recommendations
    - Calculate task uncertainty
    - Identify risk factors
    - Recommend pipeline mode and intensity levels
    - Create context for advanced features

PATTERNS:
    - Template Method: Extends base router with enhanced decision making
    - Facade Pattern: Provides simple interface to complex analysis
    - Dependency Injection: Accepts configured dependencies
    - Liskov Substitution: Can be used anywhere IntelligentRouter is used
"""

import re
from typing import Dict, Optional
from intelligent_router import IntelligentRouter, TaskRequirements
from advanced_pipeline_integration import AdvancedPipelineConfig
from artemis_exceptions import wrap_exception, PipelineException

from intelligent_router_pkg.enhanced_routing_decision import EnhancedRoutingDecision
from intelligent_router_pkg.uncertainty_calculator import UncertaintyCalculator
from intelligent_router_pkg.risk_identifier import RiskIdentifier
from intelligent_router_pkg.benefit_calculator import BenefitCalculator
from intelligent_router_pkg.mode_recommender import ModeRecommender
from intelligent_router_pkg.context_creator import ContextCreator
from intelligent_router_pkg.prompt_generator import PromptGenerator
from intelligent_router_pkg.decision_logger import DecisionLogger


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

        # Compile risk detection patterns
        self.risk_patterns = self._compile_risk_patterns()

        # Keywords for feature detection
        self.two_pass_keywords = [
            'prototype', 'experiment', 'poc', 'proof of concept',
            'explore', 'investigate', 'research', 'try',
            'refactor', 'rewrite', 'redesign'
        ]

        self.uncertainty_keywords = [
            'unknown', 'uncertain', 'unclear', 'ambiguous',
            'research', 'investigate', 'explore', 'experimental',
            'new technology', 'never done', 'unfamiliar'
        ]

        # Initialize component modules
        self.uncertainty_calculator = UncertaintyCalculator(self.uncertainty_keywords)
        self.risk_identifier = RiskIdentifier(self.risk_patterns)
        self.benefit_calculator = BenefitCalculator(self.two_pass_keywords)
        self.prompt_generator = PromptGenerator()
        self.context_creator = ContextCreator(
            self.advanced_config,
            self.ai_query_service,
            self.prompt_generator
        )
        self.mode_recommender = ModeRecommender(self.advanced_config, self.logger)
        self.decision_logger = DecisionLogger(self.logger, self.log_routing_decision)

    def _compile_risk_patterns(self) -> Dict[str, re.Pattern]:
        """Compile risk detection patterns."""
        return {
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
        uncertainty_analysis = self.uncertainty_calculator.calculate_task_uncertainty(
            card, base_decision.requirements, self._estimate_similar_task_history
        )

        # Identify risk factors for Monte Carlo simulation
        risk_factors = self.risk_identifier.identify_risk_factors(
            card, base_decision.requirements
        )

        # Calculate benefit scores
        combined_text = f"{card.get('title', '')} {card.get('description', '')}".lower()
        dynamic_benefit = self.benefit_calculator.calculate_dynamic_pipeline_benefit(
            base_decision.requirements
        )
        two_pass_benefit = self.benefit_calculator.calculate_two_pass_benefit(
            base_decision.requirements, uncertainty_analysis, combined_text
        )
        thermodynamic_benefit = self.benefit_calculator.calculate_thermodynamic_benefit(
            uncertainty_analysis, risk_factors
        )

        # Recommend pipeline mode and features
        feature_recommendation = self.mode_recommender.recommend_pipeline_mode(
            base_decision.requirements,
            uncertainty_analysis,
            risk_factors,
            dynamic_benefit,
            two_pass_benefit,
            thermodynamic_benefit
        )

        # Create rich context for each advanced feature
        thermodynamic_context = self.context_creator.create_thermodynamic_context(
            card, base_decision.requirements, uncertainty_analysis, risk_factors
        )

        dynamic_pipeline_context = self.context_creator.create_dynamic_pipeline_context(
            card, base_decision.requirements,
            feature_recommendation.dynamic_intensity
        )

        two_pass_context = self.context_creator.create_two_pass_context(
            card, base_decision.requirements, uncertainty_analysis,
            feature_recommendation.two_pass_intensity
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
        self.decision_logger.log_enhanced_decision(enhanced_decision)

        return enhanced_decision

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
