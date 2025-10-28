#!/usr/bin/env python3
"""
Context Creator

WHAT: Creates rich context for each advanced feature.

WHY: Advanced features need structured context to make informed decisions
about execution strategies, parameters, and optimizations.

RESPONSIBILITY:
    - Create thermodynamic computing context
    - Create dynamic pipeline context
    - Create two-pass pipeline context
    - Suggest optimal parameters (samples, workers, temperature, etc.)

PATTERNS:
    - Builder Pattern: Constructs complex context objects
    - Strategy Pattern: Different context building strategies per feature
"""

from typing import Dict, List, Any
from advanced_pipeline_integration import AdvancedPipelineConfig
from intelligent_router import TaskRequirements
from intelligent_router_pkg.uncertainty_analysis import UncertaintyAnalysis
from intelligent_router_pkg.risk_factor import RiskFactor


class ContextCreator:
    """
    Creates rich context for each advanced feature.

    WHY: Provides structured information that advanced features need
    to make intelligent decisions about execution.
    """

    def __init__(
        self,
        advanced_config: AdvancedPipelineConfig,
        ai_query_service,
        prompt_generator
    ):
        """
        Initialize context creator.

        Args:
            advanced_config: Configuration for advanced features
            ai_query_service: AI service for LLM calls
            prompt_generator: Prompt generator instance
        """
        self.advanced_config = advanced_config
        self.ai_query_service = ai_query_service
        self.prompt_generator = prompt_generator

    def create_thermodynamic_context(
        self,
        card: Dict,
        requirements: TaskRequirements,
        uncertainty: UncertaintyAnalysis,
        risks: List[RiskFactor]
    ) -> Dict[str, Any]:
        """Create rich context for Thermodynamic Computing."""
        high_risk_count = len([r for r in risks if r.severity in ['high', 'critical']])
        total_risk_probability = sum(r.probability for r in risks)

        prompt = self.prompt_generator.generate_thermodynamic_prompt(
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

            # Configuration
            'confidence_threshold': self.advanced_config.confidence_threshold,
            'default_strategy': self.advanced_config.default_uncertainty_strategy,
            'enable_temperature_annealing': self.advanced_config.enable_temperature_annealing,
            'temperature_schedule': self.advanced_config.temperature_schedule,
            'initial_temperature': self.advanced_config.initial_temperature,
            'final_temperature': self.advanced_config.final_temperature,

            # AI service access
            'ai_service': self.ai_query_service,

            # Guidance prompt
            'prompt': prompt
        }

    def create_dynamic_pipeline_context(
        self,
        card: Dict,
        requirements: TaskRequirements,
        intensity: float
    ) -> Dict[str, Any]:
        """Create context for Dynamic Pipeline."""
        prompt = self.prompt_generator.generate_dynamic_pipeline_prompt(
            card, requirements, intensity
        )

        base_max_workers = self.advanced_config.max_parallel_workers
        max_workers = int(1 + intensity * (base_max_workers - 1))

        return {
            # Task characteristics
            'task_type': requirements.task_type,
            'complexity': requirements.complexity,
            'story_points': requirements.estimated_story_points,
            'task_title': card.get('title', ''),
            'task_description': card.get('description', ''),

            # Execution parameters
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

            # Configuration
            'parallel_execution_enabled': self.advanced_config.parallel_execution_enabled,
            'stage_caching_enabled': self.advanced_config.stage_result_caching_enabled,

            # AI service access
            'ai_service': self.ai_query_service,

            # Guidance prompt
            'prompt': prompt
        }

    def create_two_pass_context(
        self,
        card: Dict,
        requirements: TaskRequirements,
        uncertainty: UncertaintyAnalysis,
        intensity: float
    ) -> Dict[str, Any]:
        """Create context for Two-Pass Pipeline."""
        prompt = self.prompt_generator.generate_two_pass_prompt(
            card, requirements, uncertainty, intensity
        )

        base_first_pass_timeout = 30
        first_pass_timeout = int(base_first_pass_timeout * (1.0 + intensity * 0.5))

        estimated_total_minutes = requirements.estimated_story_points * 10
        second_pass_timeout = int(estimated_total_minutes * (1.0 - self.advanced_config.first_pass_timeout_multiplier))

        base_threshold = self.advanced_config.confidence_threshold
        quality_threshold = base_threshold + (intensity * 0.15)

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

            # Pass configuration
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

            # Rollback configuration
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

            # AI service access
            'ai_service': self.ai_query_service,

            # Guidance prompt
            'prompt': prompt
        }

    def _suggest_uncertainty_strategy(
        self,
        uncertainty: UncertaintyAnalysis,
        risks: List[RiskFactor]
    ) -> str:
        """Suggest which uncertainty strategy to use."""
        # Guard clauses
        if len(risks) >= 3:
            return 'monte_carlo'

        if uncertainty.similar_task_history >= 5:
            return 'bayesian'

        if uncertainty.overall_uncertainty > 0.7:
            return 'ensemble'

        return 'bayesian'

    def _suggest_monte_carlo_samples(self, risks: List[RiskFactor]) -> int:
        """Suggest number of Monte Carlo simulation samples."""
        if len(risks) >= 3:
            return 5000

        if len(risks) >= 1:
            return 1000

        return 500

    def _suggest_initial_temperature(self, uncertainty: UncertaintyAnalysis) -> float:
        """Suggest initial temperature for temperature sampling."""
        return 0.5 + (uncertainty.overall_uncertainty * 1.5)

    def _suggest_retry_attempts(self, requirements: TaskRequirements) -> int:
        """Suggest retry attempts for Dynamic Pipeline."""
        if requirements.complexity == 'complex' or requirements.has_external_dependencies:
            return 3

        if requirements.complexity == 'medium':
            return 2

        return 1

    def _identify_priority_stages(self, requirements: TaskRequirements) -> List[str]:
        """Identify which stages should be prioritized."""
        priority_stages = []

        if requirements.requires_frontend:
            priority_stages.append('ui_ux_stage')
        if requirements.requires_backend:
            priority_stages.append('implementation_stage')
        if requirements.requires_api:
            priority_stages.append('api_design_stage')
        if requirements.has_database:
            priority_stages.append('data_model_stage')

        if requirements.complexity in ['medium', 'complex']:
            priority_stages.extend(['architecture_stage', 'code_review_stage'])

        return priority_stages

    def _identify_optional_stages(self, requirements: TaskRequirements) -> List[str]:
        """Identify which stages are optional and can be skipped."""
        optional_stages = []

        if not requirements.requires_frontend:
            optional_stages.append('ui_ux_stage')
        if not requirements.has_database:
            optional_stages.append('data_model_stage')
        if not requirements.requires_api:
            optional_stages.append('api_design_stage')

        if requirements.complexity == 'simple':
            optional_stages.extend(['architecture_stage', 'performance_stage'])

        return optional_stages
