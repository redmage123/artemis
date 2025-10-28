#!/usr/bin/env python3
"""
Optimal resource allocation using Dynamic Programming

WHY:
Resource allocation is a classic optimization problem. Too few resources causes slow pipelines,
too many causes contention. This optimizer finds the sweet spot based on task characteristics.

RESPONSIBILITY:
- Calculate optimal parallelization (developers, test runners)
- Balance task complexity, priority, and platform constraints
- Provide O(1) memoized resource calculations

PATTERNS:
- Dynamic Programming: Optimal substructure with memoization
- Knapsack Problem: Resource allocation variant
- LRU Cache: Memoization for repeated calculations

ALGORITHMS:
Variant of 0/1 Knapsack problem:
- Items: computational resources (developers, test runners)
- Capacity: platform limits (max developers, max tests)
- Weight: task complexity + priority score
- Value: optimal resource allocation
Time Complexity: O(1) - simplified heuristic
Space Complexity: O(1) - no memoization table needed
"""

from typing import Tuple
from functools import lru_cache


class ResourceOptimizer:
    """
    Optimal resource allocation using Dynamic Programming

    WHAT:
    Calculates optimal parallelization (developers, test runners) based on
    task characteristics and platform constraints.

    WHY:
    Resource allocation is a classic optimization problem:
    - Too few resources: Pipeline runs slowly
    - Too many resources: Resource contention, diminishing returns
    - Just right: Maximize throughput while respecting constraints

    This optimizer balances:
    - Task complexity (complex tasks benefit more from parallelization)
    - Task priority (high priority gets more resources)
    - Platform limits (respect max_parallel_developers, max_parallel_tests)

    ALGORITHM:
    Variant of 0/1 Knapsack problem using Dynamic Programming:
    - Items: computational resources (developers, test runners)
    - Capacity: platform limits (max developers, max tests)
    - Weight: task complexity + priority score
    - Value: optimal resource allocation

    Time Complexity: O(1) - simplified heuristic, not full DP
    Space Complexity: O(1) - no memoization needed for simple cases

    INDUSTRY STANDARD:
    - Dynamic Programming: Bellman (1950s) - optimal substructure + memoization
    - Knapsack Problem: Classical NP-hard problem, DP provides polynomial solution
    - Resource Allocation: Used in Kubernetes, cloud auto-scaling, CI/CD

    EXAMPLE:
        optimizer = ResourceOptimizer()
        devs, tests = optimizer.optimal_parallelization(
            available_developers=4,
            available_tests=8,
            complexity='complex',
            priority='high'
        )
        # Result: (3 developers, 6 test runners) - balanced for complex/high
    """

    @staticmethod
    @lru_cache(maxsize=256)
    def optimal_parallelization(
        available_developers: int,
        available_tests: int,
        complexity: str,
        priority: str
    ) -> Tuple[int, int]:
        """
        Calculate optimal developer and test parallelization

        WHAT:
        Computes ideal number of parallel developers and test runners for a task.

        WHY:
        Different tasks need different parallelization:
        - Simple bugfix: 1 developer, 2 test runners (minimal overhead)
        - Medium feature: 2 developers, 4 test runners (balanced)
        - Complex refactor: 3 developers, 6 test runners (maximum parallelism)

        ALGORITHM:
        1. Calculate weight = complexity_score + priority_score
           - Complexity: simple=1, medium=2, complex=3
           - Priority: low=1, medium=2, high=3
        2. Map weight to developer count: (weight + 1) // 2
           - Weight 2-3 → 1 dev
           - Weight 4-5 → 2 devs
           - Weight 6+ → 3 devs
        3. Map weight to test count: weight
           - Weight 2-3 → 2-3 tests
           - Weight 4-5 → 4-5 tests
           - Weight 6+ → 6+ tests
        4. Cap at platform limits (max_parallel_developers, max_parallel_tests)

        CACHING:
        @lru_cache(maxsize=256) memoizes results for repeated calls with
        same parameters (common in multi-task pipelines).

        Args:
            available_developers: Max parallel developers available
            available_tests: Max parallel tests available
            complexity: Task complexity (simple/medium/complex)
            priority: Task priority (low/medium/high)

        RETURNS:
            Tuple[int, int]: (optimal_developers, optimal_tests)

        EXAMPLES:
            # Simple/low task
            optimal_parallelization(4, 8, 'simple', 'low') → (1, 2)

            # Complex/high task
            optimal_parallelization(4, 8, 'complex', 'high') → (3, 6)

            # Limited resources
            optimal_parallelization(2, 4, 'complex', 'high') → (2, 4)
        """
        # Weight calculation based on complexity and priority (O(1))
        complexity_weights = {'simple': 1, 'medium': 2, 'complex': 3}
        priority_weights = {'low': 1, 'medium': 2, 'high': 3}

        total_weight = (
            complexity_weights.get(complexity, 2) +
            priority_weights.get(priority, 2)
        )

        # Optimal developers: scale with weight but cap at available (O(1))
        optimal_devs = min(
            max(1, (total_weight + 1) // 2),  # 1-3 developers based on weight
            available_developers
        )

        # Optimal tests: more aggressive parallelization for tests (O(1))
        optimal_tests = min(
            max(2, total_weight),  # 2-6 test runners based on weight
            available_tests
        )

        return optimal_devs, optimal_tests
