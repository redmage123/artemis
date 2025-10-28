#!/usr/bin/env python3
"""
Module: complexity_based_selector.py

WHY: Simple projects waste resources on extensive validation. Complex projects risk
     quality issues without thorough gates. This selector adapts pipeline to project size.

RESPONSIBILITY: Select pipeline stages based on project complexity analysis.

PATTERNS:
    - Strategy: Implements stage selection based on complexity
    - Dispatch Table: Maps complexity levels to filter functions
    - Guard Clauses: Early validation and error handling
"""

from typing import Dict, Any, List, Optional

from artemis_exceptions import PipelineException, wrap_exception
from artemis_services import PipelineLogger
from dynamic_pipeline.project_complexity import ProjectComplexity
from dynamic_pipeline.pipeline_stage import PipelineStage
from dynamic_pipeline.stage_selection_strategy import StageSelectionStrategy


class ComplexityBasedSelector(StageSelectionStrategy):
    """
    Selects stages based on project complexity analysis.

    Why it exists: Simple projects don't need extensive validation,
    complex projects need all quality gates. Adapts pipeline to project.

    Design pattern: Strategy implementation

    Selection rules:
        SIMPLE: Basic stages only (requirements, development, basic tests)
        MODERATE: + code review, integration tests
        COMPLEX: + architecture review, performance tests, security scan
        ENTERPRISE: + compliance, multi-environment deployment
    """

    def __init__(self, logger: Optional[PipelineLogger] = None):
        self.logger = logger or PipelineLogger(verbose=True)
        # Dispatch table maps complexity to stage filter predicate
        # Why dispatch table: Eliminates elif chain, declarative configuration
        self._stage_filters = {
            ProjectComplexity.SIMPLE: self._simple_stages,
            ProjectComplexity.MODERATE: self._moderate_stages,
            ProjectComplexity.COMPLEX: self._complex_stages,
            ProjectComplexity.ENTERPRISE: self._enterprise_stages
        }

    @wrap_exception(PipelineException, "Failed to select stages")
    def select_stages(
        self,
        available_stages: List[PipelineStage],
        context: Dict[str, Any]
    ) -> List[PipelineStage]:
        """Select stages based on project complexity"""

        complexity = context.get("complexity", ProjectComplexity.MODERATE)

        # Guard clause: Validate complexity type
        if not isinstance(complexity, ProjectComplexity):
            self.logger.log(
                f"Invalid complexity type: {type(complexity)}, defaulting to MODERATE",
                "WARNING"
            )
            complexity = ProjectComplexity.MODERATE

        # Dispatch to appropriate filter using strategy map
        # Why dispatch table: No elif chain, O(1) lookup, easy to extend
        filter_func = self._stage_filters.get(complexity)

        # Guard clause: Handle unknown complexity
        if not filter_func:
            self.logger.log(
                f"No filter for complexity {complexity}, using all stages",
                "WARNING"
            )
            return available_stages

        # Apply filter strategy
        selected = [stage for stage in available_stages if filter_func(stage)]

        self.logger.log(
            f"Selected {len(selected)}/{len(available_stages)} stages for {complexity.value}",
            "INFO"
        )

        return selected

    def _simple_stages(self, stage: PipelineStage) -> bool:
        """Filter for simple projects - basic stages only"""
        basic_stages = {
            "requirements", "development", "unit_tests", "integration"
        }
        return any(name in stage.name.lower() for name in basic_stages)

    def _moderate_stages(self, stage: PipelineStage) -> bool:
        """Filter for moderate projects - includes code review"""
        # Moderate includes all simple stages plus code review
        moderate_stages = {
            "requirements", "development", "unit_tests",
            "integration", "code_review", "validation"
        }
        return any(name in stage.name.lower() for name in moderate_stages)

    def _complex_stages(self, stage: PipelineStage) -> bool:
        """Filter for complex projects - includes architecture and security"""
        complex_stages = {
            "requirements", "architecture", "development", "code_review",
            "unit_tests", "integration", "security", "performance", "validation"
        }
        return any(name in stage.name.lower() for name in complex_stages)

    def _enterprise_stages(self, stage: PipelineStage) -> bool:
        """Filter for enterprise projects - all stages"""
        # Enterprise projects use all available stages
        return True
