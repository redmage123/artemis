#!/usr/bin/env python3
"""
Module: ai_optimizer.py

WHY: Provides hybrid AI optimization for pipeline execution - combines router's
     pre-computed analysis with adaptive AI calls when needed.

RESPONSIBILITY: Optimize stage execution order, assess parallelization safety,
                and leverage router context to minimize AI costs.

PATTERNS:
    - Strategy: Different optimization strategies based on intensity
    - Guard Clauses: Early returns for low-intensity/no-AI scenarios
    - Mixin Integration: Inherits DRY AI query methods
"""

from typing import Dict, Any, List
from artemis_exceptions import PipelineException, wrap_exception
from advanced_features_ai_mixin import AdvancedFeaturesAIMixin
from dynamic_pipeline.pipeline_stage import PipelineStage
from dynamic_pipeline.core.pipeline_context import PipelineContext


# Dispatch table for complexity to worker mapping
COMPLEXITY_TO_WORKERS = {
    'simple': 2,
    'moderate': 4,
    'complex': 6,
    'very_complex': 8
}

# Dispatch table for complexity to safety score
COMPLEXITY_TO_SAFETY = {
    'simple': 0.95,
    'moderate': 0.85,
    'complex': 0.70,
    'very_complex': 0.60
}


class AIOptimizer(AdvancedFeaturesAIMixin):
    """
    Hybrid AI optimizer for pipeline execution.

    WHY: Optimizes pipeline execution using router pre-computed analysis
         (free) when sufficient, and makes adaptive AI calls when needed
         for complex scenarios.

    RESPONSIBILITY: Provide execution plan optimization and parallelization
                    assessment while minimizing AI costs.

    PATTERNS: Strategy pattern for optimization mode selection, guard clauses
              for early returns, mixin for DRY AI queries.

    Attributes:
        context: Pipeline context with router metadata
        ai_service: Optional AI service for adaptive calls
    """

    def __init__(self, context: PipelineContext):
        """
        Initialize AI optimizer.

        Args:
            context: Pipeline context with router metadata
        """
        self.context = context
        self.ai_service = context.ai_service

    @wrap_exception(PipelineException, "AI-enhanced stage optimization failed")
    def optimize_stage_execution(
        self,
        stages: List[PipelineStage],
        use_initial_analysis: bool = True
    ) -> Dict[str, Any]:
        """
        Optimize stage execution using hybrid AI approach.

        WHY: Demonstrates hybrid pattern:
        1. Start with router's pre-computed intensity and priorities (free!)
        2. Make adaptive AI call if more optimization needed (via mixin)
        3. Return optimized execution plan

        Args:
            stages: Stages to optimize
            use_initial_analysis: If True, uses router's pre-computed analysis

        Returns:
            Dictionary with optimized execution plan:
                - execution_order: List[str] - Optimized stage order
                - parallel_groups: List[List[str]] - Stages that can run in parallel
                - max_workers: int - Suggested parallelization
                - skip_optional: List[str] - Optional stages to skip
                - intensity: float - Execution intensity
                - source: str - Where optimization came from
        """
        # Guard clause: Use router pre-computed analysis for low intensity
        if use_initial_analysis and self.context.is_low_intensity():
            return self._build_simple_plan(stages)

        # Guard clause: No AI service available
        if not self.context.has_ai_service():
            return self._build_fallback_plan(stages)

        # Make AI call for complex optimization
        return self._build_ai_optimized_plan(stages)

    def _build_simple_plan(self, stages: List[PipelineStage]) -> Dict[str, Any]:
        """
        Build simple execution plan from router data.

        WHY: Low intensity means simple execution plan sufficient.
             No AI call needed - uses free router data.

        Args:
            stages: Stages to plan

        Returns:
            Simple execution plan
        """
        return {
            'execution_order': [s.name for s in stages],
            'parallel_groups': [],  # Sequential execution
            'max_workers': self.context.suggested_workers,
            'skip_optional': self.context.optional_stages,
            'intensity': self.context.router_intensity,
            'source': 'router_precomputed',
            'cost': 0.0  # Free!
        }

    def _build_fallback_plan(self, stages: List[PipelineStage]) -> Dict[str, Any]:
        """
        Build fallback plan when no AI service available.

        WHY: Graceful degradation when AI unavailable.

        Args:
            stages: Stages to plan

        Returns:
            Fallback execution plan
        """
        return {
            'execution_order': [s.name for s in stages],
            'parallel_groups': [[s.name for s in stages[:self.context.suggested_workers]]],
            'max_workers': self.context.suggested_workers,
            'skip_optional': self.context.optional_stages,
            'intensity': self.context.router_intensity,
            'source': 'fallback_no_ai_service',
            'warning': 'No AI service available'
        }

    def _build_ai_optimized_plan(self, stages: List[PipelineStage]) -> Dict[str, Any]:
        """
        Build AI-optimized execution plan.

        WHY: High intensity or complex scenarios need AI analysis.

        Args:
            stages: Stages to optimize

        Returns:
            AI-optimized execution plan
        """
        # Make AI call via mixin (DRY!)
        stage_descriptions = "\n".join([
            f"- {s.name}: {s.get_description()}" for s in stages
        ])

        complexity_level, estimated_duration, analysis = self.query_for_complexity(
            requirements=stage_descriptions,
            context=f"Initial intensity: {self.context.router_intensity:.0%}. "
                   f"Priority stages: {', '.join(self.context.priority_stages)}. "
                   f"Router guidance: {self.context.router_guidance[:200]}..."
        )

        # Use dispatch table for worker count
        ai_suggested_workers = COMPLEXITY_TO_WORKERS.get(
            complexity_level,
            self.context.suggested_workers
        )

        # Build optimized order
        execution_order = self._compute_execution_order(stages)

        # Create parallel groups
        parallel_groups = self._create_parallel_groups(
            execution_order,
            ai_suggested_workers
        )

        return {
            'execution_order': execution_order,
            'parallel_groups': parallel_groups,
            'max_workers': ai_suggested_workers,
            'skip_optional': [
                s.name for s in stages
                if s.name in self.context.optional_stages
            ],
            'intensity': self.context.router_intensity,
            'source': 'ai_optimized',
            'complexity_level': complexity_level,
            'estimated_duration': estimated_duration,
            'ai_analysis': analysis,
            'initial_intensity': self.context.router_intensity,
            'improvement': 'adaptive_optimization_applied'
        }

    def _compute_execution_order(self, stages: List[PipelineStage]) -> List[str]:
        """
        Compute optimized execution order.

        WHY: Prioritizes stages based on router + AI analysis.

        Args:
            stages: Stages to order

        Returns:
            List of stage names in optimized order
        """
        priority_set = set(self.context.priority_stages)
        optional_set = set(self.context.optional_stages)

        # Separate stages by priority
        priority_stages = [s for s in stages if s.name in priority_set]
        normal_stages = [
            s for s in stages
            if s.name not in priority_set and s.name not in optional_set
        ]
        optional_stages = [s for s in stages if s.name in optional_set]

        # Return prioritized order
        return (
            [s.name for s in priority_stages] +
            [s.name for s in normal_stages] +
            [s.name for s in optional_stages]
        )

    def _create_parallel_groups(
        self,
        execution_order: List[str],
        max_workers: int
    ) -> List[List[str]]:
        """
        Create parallel execution groups.

        WHY: Groups stages that can run concurrently.

        Args:
            execution_order: Ordered stage names
            max_workers: Maximum parallel workers

        Returns:
            List of stage groups that can run in parallel
        """
        # Guard clause: No parallelization
        if max_workers <= 1:
            return []

        parallel_groups = []
        for i in range(0, len(execution_order), max_workers):
            group = execution_order[i:i + max_workers]
            if len(group) > 1:
                parallel_groups.append(group)

        return parallel_groups

    @wrap_exception(PipelineException, "AI-enhanced parallelization assessment failed")
    def assess_parallelization(
        self,
        stages: List[PipelineStage],
        use_initial_analysis: bool = True
    ) -> Dict[str, Any]:
        """
        Assess parallelization strategy using hybrid AI approach.

        WHY: Determines if stages can safely run in parallel based on
             dependencies and complexity.

        Args:
            stages: Stages to assess
            use_initial_analysis: If True, uses router's suggested workers

        Returns:
            Dictionary with parallelization assessment:
                - recommended_workers: int - Number of parallel workers
                - can_parallelize: List[str] - Stages safe to parallelize
                - must_serialize: List[str] - Stages requiring sequential execution
                - safety_score: float - Confidence in parallelization safety
                - source: str - Where assessment came from
        """
        # Guard clause: Low parallelization from router
        if use_initial_analysis and self.context.suggested_workers <= 2:
            return self._build_conservative_assessment(stages)

        # Guard clause: No AI service
        if not self.context.has_ai_service():
            return self._build_fallback_assessment(stages)

        # Make AI call for parallelization analysis
        return self._build_ai_assessment(stages)

    def _build_conservative_assessment(
        self,
        stages: List[PipelineStage]
    ) -> Dict[str, Any]:
        """
        Build conservative parallelization assessment.

        WHY: Low worker count from router means conservative approach.

        Args:
            stages: Stages to assess

        Returns:
            Conservative assessment
        """
        return {
            'recommended_workers': self.context.suggested_workers,
            'can_parallelize': [],
            'must_serialize': [s.name for s in stages],
            'safety_score': 1.0,  # Conservative = safe
            'source': 'router_precomputed',
            'cost': 0.0  # Free!
        }

    def _build_fallback_assessment(
        self,
        stages: List[PipelineStage]
    ) -> Dict[str, Any]:
        """
        Build fallback assessment without AI.

        Args:
            stages: Stages to assess

        Returns:
            Fallback assessment
        """
        return {
            'recommended_workers': self.context.suggested_workers or 2,
            'can_parallelize': [],
            'must_serialize': [s.name for s in stages],
            'safety_score': 0.8,
            'source': 'fallback_no_ai_service',
            'warning': 'No AI service available, conservative parallelization'
        }

    def _build_ai_assessment(
        self,
        stages: List[PipelineStage]
    ) -> Dict[str, Any]:
        """
        Build AI-based parallelization assessment.

        Args:
            stages: Stages to assess

        Returns:
            AI-based assessment
        """
        # Make AI call via mixin (DRY!)
        stage_info = "\n".join([
            f"- {s.name}: deps={s.get_dependencies()}" for s in stages
        ])

        complexity_level, estimated_duration, analysis = self.query_for_complexity(
            requirements=f"Parallelization assessment for stages:\n{stage_info}",
            context=f"Suggested workers: {self.context.suggested_workers}. "
                   f"Assess parallelization safety and dependencies."
        )

        # Build dependency analysis
        can_parallelize = [
            s.name for s in stages
            if not s.get_dependencies()
        ]

        must_serialize = [
            s.name for s in stages
            if s.get_dependencies()
        ]

        # Use dispatch table for safety score
        safety_score = COMPLEXITY_TO_SAFETY.get(complexity_level, 0.75)

        # Adjust workers based on complexity
        recommended_workers = self._compute_recommended_workers(complexity_level)

        return {
            'recommended_workers': recommended_workers,
            'can_parallelize': can_parallelize,
            'must_serialize': must_serialize,
            'safety_score': safety_score,
            'source': 'ai_assessed',
            'complexity_level': complexity_level,
            'estimated_duration': estimated_duration,
            'ai_analysis': analysis,
            'initial_suggested_workers': self.context.suggested_workers,
            'adjustment': recommended_workers - self.context.suggested_workers
        }

    def _compute_recommended_workers(self, complexity_level: str) -> int:
        """
        Compute recommended workers based on complexity.

        WHY: More complex pipelines need fewer parallel workers to
             avoid resource contention.

        Args:
            complexity_level: Complexity from AI analysis

        Returns:
            Recommended worker count
        """
        # Dispatch table for complexity adjustments
        adjustments = {
            'simple': 0,
            'moderate': -1,
            'complex': -2,
            'very_complex': -self.context.suggested_workers + 2
        }

        adjustment = adjustments.get(complexity_level, -1)
        return max(2, self.context.suggested_workers + adjustment)
