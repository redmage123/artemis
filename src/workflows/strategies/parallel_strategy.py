#!/usr/bin/env python3
"""
Parallel Pipeline Execution Strategy.

WHY: Optimize execution time through concurrent stage execution.
RESPONSIBILITY: Execute independent stages in parallel.
PATTERNS: Strategy Pattern, Parallel Processing Pattern.

Dependencies: base_strategy, execution_context, concurrent.futures, artemis_constants
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import concurrent.futures

from artemis_stage_interface import PipelineStage
from artemis_constants import (
    STAGE_PROJECT_ANALYSIS,
    STAGE_ARCHITECTURE,
    STAGE_DEPENDENCIES,
    STAGE_DEVELOPMENT,
    STAGE_CODE_REVIEW,
    STAGE_VALIDATION,
    STAGE_INTEGRATION,
    STAGE_TESTING
)
from pipeline_observer import PipelineObservable

from .base_strategy import PipelineStrategy
from .execution_context import ExecutionContextManager


class ParallelPipelineStrategy(PipelineStrategy):
    """
    Parallel execution strategy - run independent stages concurrently.

    WHY: Reduce total execution time through parallelization.
    RESPONSIBILITY: Group stages by dependencies and execute groups in parallel.
    PATTERNS: Strategy Pattern - parallel execution variant.

    Parallelization Groups:
    - Group 1 (parallel): Project Analysis, Dependencies
    - Group 2 (sequential): Architecture (needs Group 1)
    - Group 3 (sequential): Development (needs Group 2)
    - Group 4 (sequential): Code Review (needs Group 3)
    - Group 5 (parallel): Validation, Integration
    - Group 6 (sequential): Testing (needs Group 5)

    Potential Speedup: 20-30% reduction in execution time
    """

    def __init__(
        self,
        max_workers: int = 4,
        verbose: bool = True,
        observable: Optional[PipelineObservable] = None
    ):
        """
        Initialize parallel strategy.

        Args:
            max_workers: Maximum number of parallel workers
            verbose: Enable verbose logging
            observable: Optional PipelineObservable for event broadcasting
        """
        super().__init__(verbose, observable)

        if max_workers < 1:
            raise ValueError("max_workers must be at least 1")

        self.max_workers = max_workers
        self.context_manager = ExecutionContextManager()

    def execute(self, stages: List[PipelineStage], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute pipeline with parallel execution where possible.

        WHY: Optimize execution time by running independent stages concurrently.
        RESPONSIBILITY: Group stages and execute groups with appropriate parallelization.

        Args:
            stages: List of pipeline stages to execute
            context: Execution context (card info, config, etc.)

        Returns:
            Execution result dict with status, results, duration
        """
        start_time = datetime.now()

        # Group stages by dependencies
        stage_groups = self._group_stages_by_dependencies(stages)

        self._log(f"⚡ Starting PARALLEL pipeline execution (max workers: {self.max_workers})")
        self._log(f"   Grouped into {len(stage_groups)} execution groups")

        results = {}
        total_stages_completed = 0

        for group_idx, stage_group in enumerate(stage_groups, 1):
            self._log(f"📦 Executing Group {group_idx}: {len(stage_group)} stage(s)", "STAGE")

            if len(stage_group) == 1:
                # Single stage - execute directly
                group_result = self._execute_single_stage_group(
                    stage_group[0],
                    context,
                    results,
                    total_stages_completed,
                    start_time
                )
            else:
                # Multiple stages - execute in parallel
                group_result = self._execute_parallel_stage_group(
                    stage_group,
                    context,
                    results,
                    total_stages_completed,
                    start_time
                )

            # Guard: Check for group failure
            if group_result["status"] == "failed":
                return group_result

            # Update counters
            total_stages_completed += group_result["stages_completed"]
            results.update(group_result["results"])

        # All stages completed successfully
        return self._build_success_result(total_stages_completed, len(stage_groups), results, start_time)

    def _execute_single_stage_group(
        self,
        stage: PipelineStage,
        context: Dict[str, Any],
        results: Dict[str, Any],
        total_completed: int,
        start_time: datetime
    ) -> Dict[str, Any]:
        """
        Execute single-stage group.

        WHY: Handle sequential stages efficiently.
        RESPONSIBILITY: Execute one stage and return result.

        Args:
            stage: Pipeline stage to execute
            context: Execution context
            results: Accumulated results
            total_completed: Total stages completed so far
            start_time: Execution start time

        Returns:
            Group execution result
        """
        stage_name = stage.__class__.__name__
        card_id = self.context_manager.get_card_id(context)

        self._log(f"   ▶️  {stage_name}")

        # Notify stage started
        self._notify_stage_started(card_id, stage_name)

        # Execute stage
        try:
            card = self.context_manager.get_card(context)
            stage_result = stage.execute(card, context)

            # Check if stage succeeded
            if not self.context_manager.is_stage_successful(stage_result):
                return self._build_failure_result(
                    total_completed,
                    stage_name,
                    stage_result.get("error", "Unknown error"),
                    results,
                    start_time
                )

            self._log(f"   ✅ {stage_name}")

            # Notify stage completed
            self._notify_stage_completed(card_id, stage_name, stage_result=stage_result)

            return {
                "status": "success",
                "stages_completed": 1,
                "results": {stage_name: stage_result}
            }

        except Exception as e:
            self._log(f"   ❌ {stage_name} - {e}", "ERROR")

            # Notify stage failed
            self._notify_stage_failed(card_id, stage_name, e)

            return self._build_failure_result(
                total_completed,
                stage_name,
                str(e),
                results,
                start_time
            )

    def _execute_parallel_stage_group(
        self,
        stage_group: List[PipelineStage],
        context: Dict[str, Any],
        results: Dict[str, Any],
        total_completed: int,
        start_time: datetime
    ) -> Dict[str, Any]:
        """
        Execute multi-stage group in parallel.

        WHY: Maximize throughput for independent stages.
        RESPONSIBILITY: Execute stages concurrently and collect results.

        Args:
            stage_group: List of stages to execute in parallel
            context: Execution context
            results: Accumulated results
            total_completed: Total stages completed so far
            start_time: Execution start time

        Returns:
            Group execution result
        """
        card = self.context_manager.get_card(context)
        group_results = {}
        completed_count = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all stages in this group
            future_to_stage = {
                executor.submit(stage.execute, card, context): stage
                for stage in stage_group
            }

            # Wait for all to complete
            for future in concurrent.futures.as_completed(future_to_stage):
                stage = future_to_stage[future]
                stage_name = stage.__class__.__name__
                card_id = self.context_manager.get_card_id(context)

                try:
                    stage_result = future.result()

                    # Check if stage succeeded
                    if not self.context_manager.is_stage_successful(stage_result):
                        # Cancel remaining futures
                        for f in future_to_stage:
                            f.cancel()

                        return self._build_failure_result(
                            total_completed + completed_count,
                            stage_name,
                            stage_result.get("error", "Unknown error"),
                            results,
                            start_time
                        )

                    self._log(f"   ✅ {stage_name}")

                    # Notify stage completed
                    self._notify_stage_completed(card_id, stage_name, stage_result=stage_result)

                    group_results[stage_name] = stage_result
                    completed_count += 1

                except Exception as e:
                    self._log(f"   ❌ {stage_name} - {e}", "ERROR")

                    # Notify stage failed
                    self._notify_stage_failed(card_id, stage_name, e)

                    # Cancel remaining futures
                    for f in future_to_stage:
                        f.cancel()

                    return self._build_failure_result(
                        total_completed + completed_count,
                        stage_name,
                        str(e),
                        results,
                        start_time
                    )

        return {
            "status": "success",
            "stages_completed": completed_count,
            "results": group_results
        }

    def _group_stages_by_dependencies(self, stages: List[PipelineStage]) -> List[List[PipelineStage]]:
        """
        Group stages by their dependencies.

        WHY: Identify parallelization opportunities.
        RESPONSIBILITY: Create stage groups where stages can run concurrently.

        Args:
            stages: List of all pipeline stages

        Returns:
            List of stage groups (inner lists can execute in parallel)
        """
        # Map stage names to stages
        stage_map = {self._get_stage_name(s): s for s in stages}

        groups = []

        # Group 1: Independent analysis stages
        group1 = [
            stage_map[name] for name in [STAGE_PROJECT_ANALYSIS, STAGE_DEPENDENCIES]
            if name in stage_map
        ]
        if group1:
            groups.append(group1)

        # Group 2: Architecture (needs analysis)
        if STAGE_ARCHITECTURE in stage_map:
            groups.append([stage_map[STAGE_ARCHITECTURE]])

        # Group 3: Development (needs architecture)
        if STAGE_DEVELOPMENT in stage_map:
            groups.append([stage_map[STAGE_DEVELOPMENT]])

        # Group 4: Code Review (needs development)
        if STAGE_CODE_REVIEW in stage_map:
            groups.append([stage_map[STAGE_CODE_REVIEW]])

        # Group 5: Validation and Integration (can run in parallel)
        group5 = [
            stage_map[name] for name in [STAGE_VALIDATION, STAGE_INTEGRATION]
            if name in stage_map
        ]
        if group5:
            groups.append(group5)

        # Group 6: Testing (needs validation/integration)
        if STAGE_TESTING in stage_map:
            groups.append([stage_map[STAGE_TESTING]])

        return groups

    def _get_stage_name(self, stage: PipelineStage) -> str:
        """
        Get normalized stage name.

        WHY: Consistent stage identification.
        RESPONSIBILITY: Extract stage name for grouping.

        Args:
            stage: Pipeline stage

        Returns:
            Normalized lowercase stage name
        """
        if hasattr(stage, 'name'):
            return stage.name.lower()
        return stage.__class__.__name__.replace('Stage', '').lower()

    def _build_failure_result(
        self,
        stages_completed: int,
        failed_stage: str,
        error: str,
        results: Dict[str, Any],
        start_time: datetime
    ) -> Dict[str, Any]:
        """
        Build failure result dict.

        WHY: Consistent failure reporting.
        RESPONSIBILITY: Create standardized failure result.

        Args:
            stages_completed: Number of stages completed
            failed_stage: Name of stage that failed
            error: Error message
            results: Accumulated results
            start_time: Execution start time

        Returns:
            Failure result dict
        """
        self._log(f"❌ Stage FAILED: {failed_stage}", "ERROR")

        return self.context_manager.build_failure_result(
            stages_completed=stages_completed,
            failed_stage=failed_stage,
            error=error,
            results=results,
            duration=(datetime.now() - start_time).total_seconds(),
            strategy="parallel"
        )

    def _build_success_result(
        self,
        total_stages: int,
        execution_groups: int,
        results: Dict[str, Any],
        start_time: datetime
    ) -> Dict[str, Any]:
        """
        Build success result dict.

        WHY: Consistent success reporting.
        RESPONSIBILITY: Create standardized success result.

        Args:
            total_stages: Total number of stages executed
            execution_groups: Number of execution groups
            results: All stage results
            start_time: Execution start time

        Returns:
            Success result dict
        """
        duration = (datetime.now() - start_time).total_seconds()

        self._log(f"⚡ PARALLEL pipeline COMPLETE! ({duration:.1f}s)", "SUCCESS")

        return self.context_manager.build_success_result(
            stages_completed=total_stages,
            results=results,
            duration=duration,
            strategy="parallel",
            execution_groups=execution_groups
        )
