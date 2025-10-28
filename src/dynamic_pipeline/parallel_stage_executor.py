#!/usr/bin/env python3
"""
Module: parallel_stage_executor.py

WHY: Sequential execution wastes time when stages are independent. Parallel execution
     dramatically reduces pipeline duration by running independent stages concurrently.

RESPONSIBILITY: Execute pipeline stages in parallel while respecting dependencies.

PATTERNS:
    - Executor Pattern: Manages concurrent execution with ThreadPoolExecutor
    - Dependency Resolution: Builds dependency graph and executes in topological order
    - Level-based Execution: Processes stages in waves based on dependency depth
    - Guard Clauses: Early validation and failure detection
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List, Set, Optional

from artemis_exceptions import PipelineException, wrap_exception
from artemis_services import PipelineLogger
from dynamic_pipeline.pipeline_stage import PipelineStage
from dynamic_pipeline.stage_result import StageResult
from dynamic_pipeline.stage_executor import StageExecutor


class ParallelStageExecutor:
    """
    Executes stages in parallel where dependencies allow.

    Why it exists: Sequential execution wastes time when stages are independent.
    Parallel execution can dramatically reduce pipeline duration.

    Design pattern: Executor + Dependency Resolution

    Responsibilities:
    - Build dependency graph from stage dependencies
    - Identify parallelizable stage groups
    - Execute independent stages concurrently
    - Wait for dependencies before starting dependent stages
    - Aggregate results from parallel executions

    Execution algorithm:
    1. Build dependency graph (directed acyclic graph)
    2. Identify stages with no dependencies (level 0)
    3. Execute level 0 stages in parallel
    4. Once complete, identify next level (dependencies met)
    5. Repeat until all stages executed

    Thread safety: Uses ThreadPoolExecutor for parallel execution with
    proper result aggregation. Stage execution must be thread-safe.
    """

    def __init__(
        self,
        executor: StageExecutor,
        max_workers: int = 4,
        logger: Optional[PipelineLogger] = None
    ):
        self.executor = executor
        self.max_workers = max_workers
        self.logger = logger or PipelineLogger(verbose=True)

    @wrap_exception(PipelineException, "Failed to execute stages in parallel")
    def execute_stages_parallel(
        self,
        stages: List[PipelineStage],
        context: Dict[str, Any],
        card_id: str
    ) -> Dict[str, StageResult]:
        """
        Execute stages in parallel respecting dependencies.

        Why needed: Reduces pipeline duration by running independent stages
        concurrently while ensuring dependency order is preserved.

        Args:
            stages: Stages to execute
            context: Shared execution context
            card_id: Card ID for tracking

        Returns:
            Dict mapping stage name to StageResult

        Raises:
            PipelineException: If dependency cycle detected or stage fails
        """
        # Build dependency graph using helper method
        dep_graph = self._build_dependency_graph(stages)

        # Detect cycles using helper method
        if self._has_cycle(dep_graph):
            raise PipelineException(
                "Dependency cycle detected in pipeline stages",
                context={"stages": [s.name for s in stages]}
            )

        # Execute stages level by level
        return self._execute_by_levels(stages, dep_graph, context, card_id)

    def _build_dependency_graph(
        self,
        stages: List[PipelineStage]
    ) -> Dict[str, Set[str]]:
        """
        Build dependency graph from stage dependencies.

        Why helper method: Separates graph building logic, makes it testable.
        Uses set for O(1) dependency lookups.

        Args:
            stages: List of pipeline stages

        Returns:
            Dict mapping stage name to set of dependency names
        """
        return {
            stage.name: set(stage.get_dependencies())
            for stage in stages
        }

    def _has_cycle(self, dep_graph: Dict[str, Set[str]]) -> bool:
        """
        Detect cycles in dependency graph using DFS.

        Why helper method: Separates cycle detection logic, improves
        readability and testability. Uses standard DFS algorithm.

        Args:
            dep_graph: Dependency graph (adjacency list)

        Returns:
            True if cycle exists, False otherwise
        """
        visited = set()
        rec_stack = set()

        def has_cycle_dfs(node: str) -> bool:
            """DFS helper for cycle detection"""
            # Guard clause: Already processed
            if node in visited:
                return False

            # Guard clause: In recursion stack (cycle!)
            if node in rec_stack:
                return True

            # Mark as visiting
            rec_stack.add(node)

            # Visit dependencies
            for dep in dep_graph.get(node, set()):
                if has_cycle_dfs(dep):
                    return True

            # Mark as visited
            rec_stack.remove(node)
            visited.add(node)
            return False

        # Check each node
        return any(has_cycle_dfs(node) for node in dep_graph if node not in visited)

    def _execute_by_levels(
        self,
        stages: List[PipelineStage],
        dep_graph: Dict[str, Set[str]],
        context: Dict[str, Any],
        card_id: str
    ) -> Dict[str, StageResult]:
        """
        Execute stages level by level based on dependencies.

        Why helper method: Extracts level-based execution logic from main
        method. Avoids nested loops by extracting level processing.

        Args:
            stages: Stages to execute
            dep_graph: Dependency graph
            context: Execution context
            card_id: Card ID for tracking

        Returns:
            Dict of stage results
        """
        stage_map = {stage.name: stage for stage in stages}
        results: Dict[str, StageResult] = {}
        completed = set()

        # Process stages level by level
        while len(completed) < len(stages):
            # Find next level (stages with all dependencies met)
            next_level = self._find_next_level(dep_graph, completed)

            # Guard clause: No progress (shouldn't happen if no cycles)
            if not next_level:
                break

            # Execute level in parallel
            level_results = self._execute_level(
                [stage_map[name] for name in next_level],
                context,
                card_id
            )

            # Update results and completed set
            results.update(level_results)
            completed.update(next_level)

            # Guard clause: Any stage failed
            if any(not r.is_success() for r in level_results.values()):
                self.logger.log(
                    "Stage failure in parallel execution, stopping pipeline",
                    "ERROR"
                )
                break

        return results

    def _find_next_level(
        self,
        dep_graph: Dict[str, Set[str]],
        completed: Set[str]
    ) -> List[str]:
        """
        Find stages ready to execute (all dependencies completed).

        Why helper method: Extracts next level finding logic, avoids
        nested loops in main execution method.

        Args:
            dep_graph: Dependency graph
            completed: Set of completed stage names

        Returns:
            List of stage names ready to execute
        """
        return [
            stage_name
            for stage_name, deps in dep_graph.items()
            if stage_name not in completed and deps.issubset(completed)
        ]

    def _execute_level(
        self,
        stages: List[PipelineStage],
        context: Dict[str, Any],
        card_id: str
    ) -> Dict[str, StageResult]:
        """
        Execute single level of stages in parallel.

        Why helper method: Separates parallel execution logic from level
        iteration. Encapsulates ThreadPoolExecutor usage.

        Args:
            stages: Stages to execute in parallel
            context: Execution context
            card_id: Card ID for tracking

        Returns:
            Dict of stage results
        """
        # Guard clause: Single stage (no parallelism needed)
        if len(stages) == 1:
            stage = stages[0]
            result = self.executor.execute_stage(stage, context, card_id)
            return {stage.name: result}

        # Parallel execution using ThreadPoolExecutor
        self.logger.log(
            f"Executing {len(stages)} stages in parallel: {[s.name for s in stages]}",
            "INFO"
        )

        results = {}
        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            # Submit all stages
            future_to_stage = {
                pool.submit(self.executor.execute_stage, stage, context, card_id): stage
                for stage in stages
            }

            # Collect results as they complete
            for future in as_completed(future_to_stage):
                stage = future_to_stage[future]
                result = future.result()
                results[stage.name] = result

        return results
