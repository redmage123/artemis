"""
Module: two_pass/pipeline/ai_integration.py

WHY: Provides hybrid AI integration for quality assessment and strategy optimization.
RESPONSIBILITY: AI-enhanced quality evaluation, strategy optimization, hybrid approach.
PATTERNS: Mixin Pattern, Strategy Pattern, Guard Clauses, Dispatch Tables.

This module handles:
- AI-enhanced quality assessment using hybrid approach
- Strategy optimization based on complexity analysis
- Router context integration (pre-computed metrics)
- Adaptive AI calls for complex scenarios
- Cost-aware AI usage (router precomputed = free)
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass

from artemis_exceptions import wrap_exception
from two_pass.exceptions import TwoPassPipelineException
from advanced_features_ai_mixin import AdvancedFeaturesAIMixin


@dataclass
class AIConfig:
    """
    Configuration for AI integration behavior.

    Why: Centralizes AI-related configuration. Immutable by default.

    Attributes:
        ai_service: AI service instance for queries
        router_intensity: Pre-computed intensity from router (0.0-1.0)
        router_guidance: Pre-computed guidance prompt from router
        quality_threshold: Pre-computed quality threshold
        first_pass_timeout: Timeout for first pass (seconds)
        second_pass_timeout: Timeout for second pass (seconds)
        first_pass_guidance: Pre-computed first pass guidance
        second_pass_guidance: Pre-computed second pass guidance
    """
    ai_service: Optional[Any] = None
    router_intensity: float = 0.5
    router_guidance: str = ''
    quality_threshold: float = 0.7
    first_pass_timeout: int = 30
    second_pass_timeout: int = 120
    first_pass_guidance: list = None
    second_pass_guidance: list = None

    def __post_init__(self):
        """Initialize empty lists if None"""
        if self.first_pass_guidance is None:
            self.first_pass_guidance = []
        if self.second_pass_guidance is None:
            self.second_pass_guidance = []


class AIIntegrationMixin(AdvancedFeaturesAIMixin):
    """
    Provides AI-enhanced capabilities for two-pass pipeline.

    Why it exists: Encapsulates hybrid AI approach - starts with router's
    pre-computed analysis (free), makes adaptive AI calls only when needed.

    Design pattern: Mixin + Strategy + Dispatch Table
    Why this design:
    - Mixin: Adds AI capabilities without inheritance complexity
    - Strategy: Different AI strategies for different complexity levels
    - Dispatch Table: Maps complexity to strategy configuration

    Responsibilities:
    - Assess pass quality with hybrid approach
    - Optimize pass strategy based on complexity
    - Integrate router context for cost efficiency
    - Make adaptive AI calls for complex scenarios

    Hybrid Approach:
    1. Start with router's pre-computed metrics (FREE!)
    2. Use simple heuristics for low-intensity tasks
    3. Make adaptive AI calls only for complex scenarios
    4. Return comprehensive evaluation

    Thread-safety: Not thread-safe (assumes single-threaded execution)
    """

    def __init__(self, ai_config: AIConfig):
        """
        Initialize AI integration with configuration.

        Args:
            ai_config: AI behavior configuration
        """
        super().__init__()
        self.ai_config = ai_config

    @wrap_exception(TwoPassPipelineException, "AI-enhanced quality assessment failed")
    def assess_pass_quality_with_ai(
        self,
        code: str,
        requirements: str = "",
        previous_version: Optional[str] = None,
        use_initial_analysis: bool = True
    ) -> Dict[str, Any]:
        """
        Assess pass quality using hybrid AI approach.

        NEW: Demonstrates hybrid pattern for TwoPassPipeline:
        1. Start with router's pre-computed quality threshold (free!)
        2. Make adaptive AI call if detailed assessment needed (via mixin)
        3. Return comprehensive quality evaluation

        WHY: Shows integration of router context + adaptive AI calls for quality assessment.

        Args:
            code: Code to evaluate
            requirements: Requirements for context
            previous_version: Previous pass version for comparison
            use_initial_analysis: If True, uses router's pre-computed threshold first

        Returns:
            Dict with quality assessment including:
                - overall_score: float - Overall quality score (0.0-1.0)
                - criteria_scores: Dict[str, float] - Individual quality criteria
                - improvement: float - Improvement over previous version (if provided)
                - meets_threshold: bool - Whether quality meets router's threshold
                - source: str - Where assessment came from
                - suggestions: List[str] - Improvement suggestions

        Usage:
            # Uses hybrid approach
            assessment = ai_integration.assess_pass_quality_with_ai(
                code=implementation_code,
                requirements=task_requirements,
                previous_version=first_pass_code
            )
        """
        # HYBRID STEP 1: Use router's pre-computed threshold (FREE!)
        if use_initial_analysis and self.ai_config.quality_threshold is not None:
            # Router already provided quality threshold based on task analysis
            # For simple tasks, basic heuristics sufficient
            if self.ai_config.router_intensity < 0.4:
                # Simple task - basic quality check
                basic_score = min(1.0, 0.5 + (self.ai_config.router_intensity * 0.5))
                return {
                    'overall_score': basic_score,
                    'criteria_scores': {
                        'correctness': basic_score,
                        'completeness': basic_score,
                        'maintainability': basic_score
                    },
                    'improvement': 0.0,
                    'meets_threshold': basic_score >= self.ai_config.quality_threshold,
                    'source': 'router_precomputed',
                    'suggestions': [],
                    'cost': 0.0  # Free!
                }

        # HYBRID STEP 2: Complex task or threshold not met - make adaptive AI call
        if not self.ai_config.ai_service:
            # Fallback: No AI service available, use conservative estimate
            fallback_score = self.ai_config.quality_threshold if self.ai_config.quality_threshold else 0.7
            return {
                'overall_score': fallback_score,
                'criteria_scores': {
                    'correctness': fallback_score,
                    'completeness': fallback_score,
                    'maintainability': fallback_score
                },
                'improvement': 0.0,
                'meets_threshold': True,
                'source': 'fallback_no_ai_service',
                'suggestions': [],
                'warning': 'No AI service available, conservative estimate'
            }

        # Make AI call via mixin method for quality evaluation (DRY!)
        ai_quality = self.query_for_quality(
            code=code,
            requirements=requirements,
            previous_version=previous_version
        )

        # Calculate improvement if previous version provided
        improvement = 0.0
        if previous_version and ai_quality.comparison:
            improvement = ai_quality.comparison.get('improvement', 0.0)

        return {
            'overall_score': ai_quality.overall_score,
            'criteria_scores': ai_quality.criteria_scores,
            'improvement': improvement,
            'meets_threshold': ai_quality.overall_score >= self.ai_config.quality_threshold,
            'source': 'ai_assessed',
            'suggestions': ai_quality.suggestions,
            'ai_reasoning': ai_quality.reasoning,
            'model_used': ai_quality.model_used,
            'detailed_comparison': ai_quality.comparison,
            'initial_threshold': self.ai_config.quality_threshold,
            'quality_delta': ai_quality.overall_score - self.ai_config.quality_threshold
        }

    @wrap_exception(TwoPassPipelineException, "AI-enhanced strategy optimization failed")
    def optimize_pass_strategy_with_ai(
        self,
        task_requirements: str,
        context_info: Dict[str, Any],
        use_initial_analysis: bool = True
    ) -> Dict[str, Any]:
        """
        Optimize pass execution strategy using hybrid AI approach.

        NEW: Uses router's intensity and guidance to optimize first/second pass strategy.

        Args:
            task_requirements: Task requirements description
            context_info: Additional context information
            use_initial_analysis: If True, uses router's pre-computed strategy first

        Returns:
            Dict with optimized strategy including:
                - first_pass_focus: List[str] - What first pass should focus on
                - second_pass_focus: List[str] - What second pass should focus on
                - recommended_timeouts: Dict[str, int] - Timeout recommendations
                - parallelization: bool - Whether passes can be partially parallelized
                - rollback_likelihood: float - Probability of needing rollback
                - source: str - Where optimization came from

        Usage:
            strategy = ai_integration.optimize_pass_strategy_with_ai(
                task_requirements=requirements_text,
                context_info=execution_context
            )
        """
        # HYBRID STEP 1: Use router's pre-computed strategy (FREE!)
        if use_initial_analysis and self.ai_config.router_intensity is not None:
            # Router already provided intensity and guidance
            # For low intensity, simple strategy sufficient
            if self.ai_config.router_intensity < 0.5:
                return {
                    'first_pass_focus': self.ai_config.first_pass_guidance if self.ai_config.first_pass_guidance else [
                        'Validate requirements',
                        'Check for obvious issues',
                        'Quick feasibility check'
                    ],
                    'second_pass_focus': self.ai_config.second_pass_guidance if self.ai_config.second_pass_guidance else [
                        'Implement core functionality',
                        'Apply first pass learnings'
                    ],
                    'recommended_timeouts': {
                        'first_pass': self.ai_config.first_pass_timeout,
                        'second_pass': self.ai_config.second_pass_timeout
                    },
                    'parallelization': False,  # Conservative for simple tasks
                    'rollback_likelihood': 0.1,  # Low for simple tasks
                    'source': 'router_precomputed',
                    'intensity': self.ai_config.router_intensity,
                    'cost': 0.0  # Free!
                }

        # HYBRID STEP 2: Higher intensity - make adaptive AI call
        if not self.ai_config.ai_service:
            # Fallback: Use router's guidance with defaults
            return {
                'first_pass_focus': self.ai_config.first_pass_guidance if self.ai_config.first_pass_guidance else [
                    'Analyze requirements',
                    'Identify risks',
                    'Create execution plan'
                ],
                'second_pass_focus': self.ai_config.second_pass_guidance if self.ai_config.second_pass_guidance else [
                    'Full implementation',
                    'Apply optimizations',
                    'Integrate learnings'
                ],
                'recommended_timeouts': {
                    'first_pass': self.ai_config.first_pass_timeout,
                    'second_pass': self.ai_config.second_pass_timeout
                },
                'parallelization': self.ai_config.router_intensity > 0.7,
                'rollback_likelihood': 0.3,
                'source': 'fallback_no_ai_service',
                'intensity': self.ai_config.router_intensity,
                'warning': 'No AI service available, using defaults'
            }

        # Make AI call via mixin for complexity analysis (DRY!)
        complexity_level, estimated_duration, analysis = self.query_for_complexity(
            requirements=task_requirements,
            context=f"Two-pass pipeline optimization. "
                   f"Initial intensity: {self.ai_config.router_intensity:.0%}. "
                   f"Router guidance: {self.ai_config.router_guidance[:200]}..."
        )

        # Dispatch table for complexity-based strategy configuration
        complexity_to_strategy = self._get_complexity_strategy_dispatch()

        strategy_config = complexity_to_strategy.get(
            complexity_level,
            complexity_to_strategy['moderate']
        )

        # Merge with router's guidance if available
        first_focus = strategy_config['first_focus']
        if self.ai_config.first_pass_guidance:
            first_focus = list(set(first_focus + self.ai_config.first_pass_guidance))

        second_focus = strategy_config['second_focus']
        if self.ai_config.second_pass_guidance:
            second_focus = list(set(second_focus + self.ai_config.second_pass_guidance))

        return {
            'first_pass_focus': first_focus,
            'second_pass_focus': second_focus,
            'recommended_timeouts': {
                'first_pass': strategy_config['timeouts'][0],
                'second_pass': strategy_config['timeouts'][1]
            },
            'parallelization': strategy_config['parallel'],
            'rollback_likelihood': strategy_config['rollback'],
            'source': 'ai_optimized',
            'complexity_level': complexity_level,
            'estimated_duration': estimated_duration,
            'ai_analysis': analysis,
            'initial_intensity': self.ai_config.router_intensity,
            'initial_timeouts': {
                'first_pass': self.ai_config.first_pass_timeout,
                'second_pass': self.ai_config.second_pass_timeout
            },
            'timeout_adjustment': {
                'first_pass': strategy_config['timeouts'][0] - self.ai_config.first_pass_timeout,
                'second_pass': strategy_config['timeouts'][1] - self.ai_config.second_pass_timeout
            }
        }

    def _get_complexity_strategy_dispatch(self) -> Dict[str, Dict[str, Any]]:
        """
        Get dispatch table for complexity-based strategy configuration.

        Why extracted: Separates configuration data from logic. Makes it easy
        to modify strategy configurations without changing algorithm.

        Returns:
            Dispatch table mapping complexity level to strategy config
        """
        return {
            'simple': {
                'first_focus': ['Quick validation', 'Schema check', 'Dependency scan'],
                'second_focus': ['Direct implementation', 'Simple testing'],
                'timeouts': (
                    int(self.ai_config.first_pass_timeout * 0.8),
                    int(self.ai_config.second_pass_timeout * 0.8)
                ),
                'parallel': False,
                'rollback': 0.05
            },
            'moderate': {
                'first_focus': ['Thorough analysis', 'Risk assessment', 'Architecture planning'],
                'second_focus': ['Structured implementation', 'Integration', 'Comprehensive testing'],
                'timeouts': (
                    self.ai_config.first_pass_timeout,
                    self.ai_config.second_pass_timeout
                ),
                'parallel': False,
                'rollback': 0.15
            },
            'complex': {
                'first_focus': [
                    'Deep analysis',
                    'Multiple risk scenarios',
                    'Detailed architecture',
                    'Prototyping'
                ],
                'second_focus': [
                    'Incremental implementation',
                    'Continuous validation',
                    'Extensive testing',
                    'Performance optimization'
                ],
                'timeouts': (
                    int(self.ai_config.first_pass_timeout * 1.2),
                    int(self.ai_config.second_pass_timeout * 1.3)
                ),
                'parallel': True,
                'rollback': 0.30
            },
            'very_complex': {
                'first_focus': [
                    'Comprehensive analysis',
                    'Multiple prototypes',
                    'Risk mitigation plans',
                    'Architecture validation'
                ],
                'second_focus': [
                    'Phased implementation',
                    'Continuous feedback',
                    'Iterative refinement',
                    'Full test coverage'
                ],
                'timeouts': (
                    int(self.ai_config.first_pass_timeout * 1.5),
                    int(self.ai_config.second_pass_timeout * 1.5)
                ),
                'parallel': True,
                'rollback': 0.45
            }
        }


__all__ = ['AIIntegrationMixin', 'AIConfig']
