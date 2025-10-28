#!/usr/bin/env python3
"""
Directed Acyclic Graph for stage dependencies

WHY:
Pipeline stages have dependencies (e.g., development requires architecture, testing requires development).
DAG ensures stages execute in valid dependency order, enables parallel execution, and identifies critical paths.

RESPONSIBILITY:
- Manage stage dependencies as a DAG
- Provide topological sorting (Kahn's Algorithm) for valid stage ordering
- Calculate critical path using Critical Path Method (CPM)
- Detect cycles in dependency graphs

PATTERNS:
- DAG Pattern: Models dependencies as directed acyclic graph
- Topological Sort: Kahn's Algorithm (1962) - O(V+E)
- Critical Path Method: CPM for project duration estimation - O(V+E)
- Memoization: LRU cache for performance optimization

ALGORITHMS:
1. Topological Sort (Kahn's Algorithm) - O(V+E)
   - Orders stages respecting dependencies
   - Detects cycles (invalid dependency graphs)
2. Critical Path Method (CPM) - O(V+E)
   - Calculates longest path through DAG
   - Identifies minimum project duration
"""

from typing import List, Tuple, Set, Dict
from collections import deque, defaultdict
from functools import lru_cache

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from artemis_exceptions import PipelineConfigurationError
from ai_orchestration.constants import STAGE_DEPENDENCIES, STAGE_ESTIMATED_DURATIONS


class StageDAG:
    """
    Directed Acyclic Graph for stage dependencies

    WHAT:
    Manages pipeline stage dependencies as a directed acyclic graph (DAG),
    providing topological sorting and critical path calculation.

    WHY:
    Pipeline stages have dependencies (e.g., development requires architecture,
    testing requires development). DAG ensures:
    - Stages execute in valid dependency order
    - Parallel execution respects dependencies
    - Critical path identifies minimum pipeline duration
    - Cycle detection prevents infinite loops

    ALGORITHMS:
    1. Topological Sort (Kahn's Algorithm) - O(V+E)
       - Orders stages respecting dependencies
       - Detects cycles (invalid dependency graphs)
    2. Critical Path Method (CPM) - O(V+E)
       - Calculates longest path through DAG
       - Identifies minimum project duration
       - Used for duration estimation

    INDUSTRY STANDARDS:
    - DAG: Computer science fundamental (scheduling, build systems, package managers)
    - Topological Sort: Kahn's algorithm (1962) - industry standard
    - CPM: Project management standard since 1950s (construction, software)

    INTEGRATION:
    - Used by: AIOrchestrationPlanner, RuleBasedOrchestrationPlanner
    - Data: STAGE_DEPENDENCIES dict, STAGE_ESTIMATED_DURATIONS dict
    - Output: Ordered stage lists, duration estimates
    """

    def __init__(self):
        """
        Initialize DAG with predefined stage dependencies

        WHAT:
        Copies global dependency graph and duration estimates into instance.

        WHY:
        Instance-level copies allow modification without affecting global state.
        Enables testing with custom dependency graphs.
        """
        self.graph = STAGE_DEPENDENCIES.copy()
        self.durations = STAGE_ESTIMATED_DURATIONS.copy()

    @lru_cache(maxsize=128)
    def topological_sort(self, stages_tuple: Tuple[str, ...]) -> List[str]:
        """
        Topological sort of stages using Kahn's algorithm

        Industry Algorithm: Kahn's algorithm for topological sort
        Time Complexity: O(V + E) where V=vertices (stages), E=edges (dependencies)
        Space Complexity: O(V)

        Args:
            stages_tuple: Tuple of stages to order (tuple for hashability/caching)

        Returns:
            Topologically sorted stage list

        Raises:
            PipelineConfigurationError: If cycle detected
        """
        stages = set(stages_tuple)

        # Build in-degree map (O(V))
        in_degree: Dict[str, int] = defaultdict(int)
        for stage in stages:
            in_degree[stage] = 0

        # Calculate in-degrees (O(E))
        for stage in stages:
            for dep in self.graph.get(stage, set()):
                if dep in stages:  # Only count dependencies that are included
                    in_degree[stage] += 1

        # Initialize queue with zero in-degree stages (O(V))
        queue: deque = deque([stage for stage in stages if in_degree[stage] == 0])
        result: List[str] = []

        # Process queue (O(V + E))
        while queue:
            stage = queue.popleft()
            result.append(stage)

            # Decrease in-degree for dependent stages
            for dependent in stages:
                if stage not in self.graph.get(dependent, set()):
                    continue

                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        # Check for cycles (O(1))
        if len(result) != len(stages):
            raise PipelineConfigurationError(
                "Cycle detected in stage dependencies",
                context={'stages': list(stages), 'sorted': result}
            )

        return result

    @lru_cache(maxsize=128)
    def critical_path(self, stages_tuple: Tuple[str, ...]) -> Tuple[List[str], int]:
        """
        Calculate critical path using Critical Path Method (CPM)

        Industry Algorithm: Critical Path Method
        Time Complexity: O(V + E)
        Space Complexity: O(V)

        The critical path is the longest path through the DAG,
        determining the minimum project duration.

        Args:
            stages_tuple: Tuple of stages (tuple for hashability/caching)

        Returns:
            Tuple of (critical_path_stages, total_duration_minutes)
        """
        stages = list(stages_tuple)

        # Get topological order (O(V + E))
        topo_order = self.topological_sort(stages_tuple)

        # Calculate earliest start times using DP (O(V + E))
        earliest_start: Dict[str, int] = {}
        for stage in topo_order:
            # Guard clause: Stage with no dependencies starts at time 0
            deps = self.graph.get(stage, set()) & set(stages)
            if not deps:
                earliest_start[stage] = 0
                continue

            # Calculate max predecessor finish time
            earliest_start[stage] = max(
                earliest_start.get(dep, 0) + self.durations.get(dep, 0)
                for dep in deps
            )

        # Calculate latest start times (backward pass) (O(V + E))
        latest_start: Dict[str, int] = {}
        total_duration = max(
            earliest_start.get(stage, 0) + self.durations.get(stage, 0)
            for stage in stages
        )

        for stage in reversed(topo_order):
            # Guard clause: Stage with no dependents is on the critical path end
            dependents = [s for s in stages if stage in self.graph.get(s, set())]
            if not dependents:
                latest_start[stage] = total_duration - self.durations.get(stage, 0)
                continue

            # Calculate min dependent start time
            latest_start[stage] = min(
                latest_start.get(dep, total_duration) - self.durations.get(stage, 0)
                for dep in dependents
            )

        # Critical path consists of stages where earliest_start == latest_start (O(V))
        critical_path_stages = [
            stage for stage in topo_order
            if earliest_start.get(stage, 0) == latest_start.get(stage, float('inf'))
        ]

        return critical_path_stages, total_duration
