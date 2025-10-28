#!/usr/bin/env python3
"""
Router-Validation Integration

WHY: Combine intelligent routing with intelligent validation for complete task orchestration
RESPONSIBILITY: Map routing decisions to validation strategies
PATTERNS: Adapter (routing → validation), Strategy (per-stage validation)

This module bridges the IntelligentRouter (which decides WHAT stages to execute)
with the AntiHallucinationOrchestrator (which decides HOW to validate each stage).

Integration Flow:
  1. Router analyzes task → RoutingDecision (complexity, stages)
  2. This module maps routing → ValidationStrategy (per stage)
  3. Each stage executes with appropriate validation

Example:
    from validation.router_validation_integration import RouterValidationIntegration

    # Initialize with router
    integration = RouterValidationIntegration(router, logger)

    # Get validation strategies for all stages
    strategies = integration.get_validation_strategies_for_routing(routing_decision)

    # Apply validation to specific stage
    strategy = strategies['development_stage']
    print(f"Development validation: {strategy.profile.value}")
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from artemis_logger import get_logger
from validation import (
    AntiHallucinationOrchestrator,
    ValidationProfile,
    TaskType,
    TaskContext,
    ValidationStrategy,
)


@dataclass
class StageValidationConfig:
    """
    Validation configuration for a single pipeline stage.

    WHY: Each stage has different validation needs
    RESPONSIBILITY: Store stage-specific validation settings
    """
    stage_name: str
    task_type: TaskType
    validation_strategy: ValidationStrategy
    rationale: str


class RouterValidationIntegration:
    """
    Integrate routing decisions with validation strategy selection.

    WHY: Router decides which stages, this decides how to validate each stage
    RESPONSIBILITY: Map routing complexity → validation strategies
    PATTERNS: Adapter, Strategy

    Key Integration Points:
    - Task complexity from router → Risk level for validation
    - Critical path stages → Higher validation profiles
    - Time budgets from router → Validation time constraints
    """

    def __init__(
        self,
        intelligent_router: Optional[Any] = None,
        logger: Optional[Any] = None
    ):
        """
        Initialize router-validation integration.

        Args:
            intelligent_router: The IntelligentRouter instance (optional)
            logger: Optional logger instance
        """
        self.router = intelligent_router
        self.logger = logger or get_logger("router_validation_integration")
        self.orchestrator = AntiHallucinationOrchestrator(logger=self.logger)

    def get_validation_strategies_for_routing(
        self,
        routing_decision: Any,
        card: Optional[Dict[str, Any]] = None
    ) -> Dict[str, StageValidationConfig]:
        """
        Get validation strategies for all stages in routing decision.

        WHY: Each stage needs appropriate validation based on task complexity
        RESPONSIBILITY: Map routing decision to per-stage validation strategies

        Args:
            routing_decision: RoutingDecision from IntelligentRouter
            card: Optional kanban card for additional context

        Returns:
            Dictionary mapping stage names to validation configs

        Example:
            strategies = integration.get_validation_strategies_for_routing(decision)
            dev_strategy = strategies['development_stage'].validation_strategy
        """
        strategies = {}

        # Extract task characteristics from routing decision
        complexity = getattr(routing_decision, 'complexity_score', 50)
        is_critical = self._is_critical_task(routing_decision, card)
        has_tests = self._requires_testing(routing_decision)

        # Get stage selections
        selected_stages = getattr(routing_decision, 'stages', [])
        required_stages = getattr(routing_decision, 'required_stages', [])

        # Map stage names to task types
        stage_to_task_type = {
            'requirements_parsing': TaskType.DOCUMENTATION,
            'architecture': TaskType.FEATURE_ADDITION,
            'development': TaskType.CODE_GENERATION,
            'code_review': TaskType.CODE_REVIEW,
            'refactoring': TaskType.REFACTORING,
            'testing': TaskType.TESTING,
            'bug_fix': TaskType.BUG_FIX,
        }

        # Create validation strategy for each stage
        for stage_name in selected_stages:
            # Determine if this is a required/critical stage
            is_required = stage_name in required_stages
            stage_critical = is_critical or is_required

            # Map stage name to task type
            task_type = self._infer_task_type_from_stage(stage_name, stage_to_task_type)

            # Create task context for validation
            context = TaskContext(
                task_type=task_type,
                code_complexity=complexity,
                is_critical=stage_critical,
                has_tests=has_tests,
                dependencies_count=self._estimate_dependencies(routing_decision),
                time_budget_ms=None  # Could be extracted from routing decision if available
            )

            # Get validation strategy
            validation_strategy = self.orchestrator.select_strategy(context)

            # Create stage validation config
            strategies[stage_name] = StageValidationConfig(
                stage_name=stage_name,
                task_type=task_type,
                validation_strategy=validation_strategy,
                rationale=f"{stage_name}: {validation_strategy.rationale}"
            )

            self.logger.info(f"Validation strategy for {stage_name}:")
            self.logger.info(f"  Profile: {validation_strategy.profile.value}")
            self.logger.info(f"  Techniques: {', '.join(validation_strategy.techniques)}")

        return strategies

    def get_validation_strategy_for_stage(
        self,
        stage_name: str,
        routing_decision: Any,
        card: Optional[Dict[str, Any]] = None
    ) -> ValidationStrategy:
        """
        Get validation strategy for a specific stage.

        WHY: Sometimes only need validation for one stage
        RESPONSIBILITY: Return validation strategy for single stage

        Args:
            stage_name: Name of the stage
            routing_decision: RoutingDecision from router
            card: Optional kanban card

        Returns:
            ValidationStrategy for the stage
        """
        all_strategies = self.get_validation_strategies_for_routing(routing_decision, card)

        # Guard: Stage not found
        if stage_name not in all_strategies:
            self.logger.warning(f"Stage {stage_name} not in routing decision, using default")
            # Return default strategy
            return self.orchestrator.select_strategy(
                TaskContext(
                    task_type=TaskType.CODE_GENERATION,
                    code_complexity=50,
                    is_critical=False,
                    has_tests=False,
                    dependencies_count=0
                )
            )

        return all_strategies[stage_name].validation_strategy

    def get_validation_profile_summary(
        self,
        routing_decision: Any,
        card: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get summary of validation profiles for all stages.

        WHY: Useful for logging and reporting
        RESPONSIBILITY: Summarize validation strategies

        Args:
            routing_decision: RoutingDecision from router
            card: Optional kanban card

        Returns:
            Summary dictionary with profile info
        """
        strategies = self.get_validation_strategies_for_routing(routing_decision, card)

        summary = {
            'total_stages': len(strategies),
            'profiles': {},
            'total_techniques': 0,
            'total_estimated_time_ms': 0,
            'average_reduction': 0.0,
        }

        technique_set = set()

        for stage_name, config in strategies.items():
            strategy = config.validation_strategy

            summary['profiles'][stage_name] = {
                'profile': strategy.profile.value,
                'risk': strategy.risk_level.value,
                'techniques': strategy.techniques,
                'time_ms': strategy.estimated_time_ms,
                'reduction': strategy.expected_reduction
            }

            technique_set.update(strategy.techniques)
            summary['total_estimated_time_ms'] += strategy.estimated_time_ms

        summary['total_techniques'] = len(technique_set)
        summary['unique_techniques'] = list(technique_set)

        if strategies:
            avg_reduction = sum(
                s.validation_strategy.expected_reduction
                for s in strategies.values()
            ) / len(strategies)
            summary['average_reduction'] = avg_reduction

        return summary

    def _infer_task_type_from_stage(
        self,
        stage_name: str,
        stage_map: Dict[str, TaskType]
    ) -> TaskType:
        """Infer TaskType from stage name."""
        # Try exact match
        if stage_name in stage_map:
            return stage_map[stage_name]

        # Try partial match
        for key, task_type in stage_map.items():
            if key in stage_name.lower():
                return task_type

        # Default to code generation
        return TaskType.CODE_GENERATION

    def _is_critical_task(
        self,
        routing_decision: Any,
        card: Optional[Dict[str, Any]]
    ) -> bool:
        """Determine if task is critical."""
        # Check routing decision
        if hasattr(routing_decision, 'is_critical'):
            return routing_decision.is_critical

        # Check card metadata
        if card:
            if card.get('priority') == 'critical':
                return True
            if 'critical' in card.get('tags', []):
                return True
            if card.get('severity') == 'critical':
                return True

        return False

    def _requires_testing(self, routing_decision: Any) -> bool:
        """Determine if testing stage is included."""
        selected_stages = getattr(routing_decision, 'stages', [])
        return any('test' in stage.lower() for stage in selected_stages)

    def _estimate_dependencies(self, routing_decision: Any) -> int:
        """Estimate dependency count from routing decision."""
        complexity = getattr(routing_decision, 'complexity_score', 50)

        # Heuristic: higher complexity = more dependencies
        if complexity > 200:
            return 15
        if complexity > 100:
            return 8
        if complexity > 50:
            return 5

        return 2


# Convenience singleton instance
_router_validation_instance: Optional[RouterValidationIntegration] = None


def get_router_validation_integration(
    router: Optional[Any] = None,
    logger: Optional[Any] = None
) -> RouterValidationIntegration:
    """
    Get singleton router-validation integration instance.

    Args:
        router: Optional IntelligentRouter instance
        logger: Optional logger

    Returns:
        Shared RouterValidationIntegration instance
    """
    global _router_validation_instance

    if _router_validation_instance is None:
        _router_validation_instance = RouterValidationIntegration(
            intelligent_router=router,
            logger=logger
        )

    return _router_validation_instance
