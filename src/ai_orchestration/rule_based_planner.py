#!/usr/bin/env python3
"""
Rule-based orchestration planner (fallback when AI unavailable)

WHY:
Provides deterministic, fast orchestration planning without requiring LLM access.
Essential fallback for offline scenarios, CI/CD pipelines, or when AI costs are prohibitive.

RESPONSIBILITY:
- Analyze task complexity using keyword matching
- Determine task type from description patterns
- Select appropriate stages based on task characteristics
- Apply same algorithms as AI planner (DAG, CPM, DP)

PATTERNS:
- Strategy Pattern: Implements OrchestrationPlannerInterface
- Rule Engine: Keyword-based classification
- Early Return: Guard clauses for clear logic flow

ALGORITHMS:
- Keyword Matching: Set intersection for O(n) complexity analysis
- Topological Sort: O(V+E) stage ordering
- Critical Path Method: O(V+E) duration calculation
- Dynamic Programming: O(1) resource optimization
"""

from typing import Dict, List, Optional, Any, Tuple, Set
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_orchestration.planner_interface import OrchestrationPlannerInterface
from ai_orchestration.orchestration_plan import OrchestrationPlan
from ai_orchestration.stage_dag import StageDAG
from ai_orchestration.resource_optimizer import ResourceOptimizer
from ai_orchestration.plan_cache import PlanCache


class RuleBasedOrchestrationPlanner(OrchestrationPlannerInterface):
    """
    Rule-based orchestration planner (fallback when AI unavailable)

    Single Responsibility: Generate orchestration plans using deterministic rules
    """

    # Performance: O(1) complexity config lookup using dict
    COMPLEXITY_CONFIG = {
        'complex': {
            'parallel_developers': 3,
            'execution_strategy': 'parallel',
            'estimated_duration': 60
        },
        'medium': {
            'parallel_developers': 2,
            'execution_strategy': 'parallel',
            'estimated_duration': 30
        },
        'simple': {
            'parallel_developers': 1,
            'execution_strategy': 'sequential',
            'estimated_duration': 15
        }
    }

    # Performance: Pre-defined keyword sets for O(1) membership checks
    COMPLEX_KEYWORDS: Set[str] = {
        'integrate', 'architecture', 'refactor', 'migrate',
        'performance', 'scalability', 'distributed', 'api'
    }

    SIMPLE_KEYWORDS: Set[str] = {
        'fix', 'update', 'small', 'minor', 'simple', 'quick'
    }

    TASK_TYPE_KEYWORDS: Dict[str, Set[str]] = {
        'bugfix': {'bug', 'fix', 'error', 'issue'},
        'refactor': {'refactor', 'restructure', 'cleanup'},
        'documentation': {'docs', 'documentation', 'readme'},
        'feature': {'feature', 'implement', 'add', 'create'}
    }

    def __init__(self, logger: Optional[Any] = None):
        """
        Initialize rule-based planner

        Args:
            logger: Optional logger instance
        """
        self.logger = logger

        # Industry algorithms (same as AI planner)
        self.dag = StageDAG()
        self.optimizer = ResourceOptimizer()
        self.cache = PlanCache(max_size=100)

    def create_plan(
        self,
        card: Dict,
        platform_info: Any,
        resource_allocation: Any
    ) -> OrchestrationPlan:
        """
        Generate orchestration plan using deterministic rules with optimization

        Industry Algorithms Applied:
        1. Hash-based caching (O(1) cache lookup)
        2. Topological sort for stage ordering (O(V+E))
        3. Critical Path Method for duration (O(V+E))
        4. Dynamic Programming for resource allocation
        """
        # Industry Algorithm: Hash-based caching - O(1) lookup
        cached_plan = self.cache.get(card, platform_info.platform_hash)
        if cached_plan:
            return cached_plan

        complexity = self._analyze_complexity(card)
        task_type = self._determine_task_type(card)

        # Build stages list
        stages, skip_stages, reasoning = self._determine_stages(
            task_type,
            complexity,
            1  # Temporary, will be optimized below
        )

        # Industry Algorithm 1: Topological Sort - O(V+E)
        sorted_stages = self.dag.topological_sort(tuple(stages))

        # Industry Algorithm 2: Critical Path Method - O(V+E)
        critical_path, estimated_duration = self.dag.critical_path(tuple(sorted_stages))

        # Industry Algorithm 3: Dynamic Programming for Resource Optimization
        priority = card.get('priority', 'medium')
        optimal_devs, optimal_tests = self.optimizer.optimal_parallelization(
            available_developers=resource_allocation.max_parallel_developers,
            available_tests=resource_allocation.max_parallel_tests,
            complexity=complexity,
            priority=priority
        )

        # Determine execution strategy based on parallelization
        execution_strategy = 'parallel' if optimal_devs > 1 else 'sequential'

        plan = OrchestrationPlan(
            complexity=complexity,
            task_type=task_type,
            stages=sorted_stages,  # Topologically sorted
            skip_stages=skip_stages,
            parallel_developers=optimal_devs,  # DP-optimized
            max_parallel_tests=optimal_tests,  # DP-optimized
            execution_strategy=execution_strategy,
            estimated_duration_minutes=estimated_duration,  # CPM-calculated
            reasoning=reasoning + [
                f"Stage ordering: Topological sort (O(V+E))",
                f"Duration estimate: Critical Path Method = {estimated_duration} min",
                f"Resource allocation: Dynamic Programming = {optimal_devs} devs, {optimal_tests} tests"
            ]
        )

        plan.validate()

        # Cache the plan - O(1) insertion
        self.cache.put(card, platform_info.platform_hash, plan)

        return plan

    def _analyze_complexity(self, card: Dict) -> str:
        """
        Analyze task complexity using keyword matching

        Performance: O(n+m) where n=description length, m=keyword set size
                    Uses set intersection for efficient matching
        """
        description = card.get('description', '').lower()
        priority = card.get('priority', 'medium')
        points = card.get('points', 5)

        # Priority contribution (O(1) dict lookup)
        priority_scores = {'high': 2, 'medium': 1, 'low': 0}
        complexity_score = priority_scores.get(priority, 1)

        # Story points contribution (O(1) comparisons)
        # Early return pattern: use dictionary dispatch to avoid nested if/elif
        points_ranges = [(13, 3), (8, 2), (5, 1)]
        for threshold, score in points_ranges:
            if points >= threshold:
                complexity_score += score
                break

        # Keyword matching using set operations (O(n) where n=words in description)
        description_words = set(description.split())
        complex_count = len(description_words & self.COMPLEX_KEYWORDS)
        simple_count = len(description_words & self.SIMPLE_KEYWORDS)

        complexity_score += min(complex_count, 3) - min(simple_count, 2)

        # Determine complexity level (O(1) comparisons)
        # Early return pattern: check conditions from highest to lowest
        if complexity_score >= 6:
            return 'complex'
        if complexity_score >= 3:
            return 'medium'
        return 'simple'

    def _determine_task_type(self, card: Dict) -> str:
        """
        Determine task type using keyword matching

        Performance: O(n*m) where n=words, m=task types (small constant)
                    Early exit on first match
        """
        description = card.get('description', '').lower()
        title = card.get('title', '').lower()
        combined = f"{title} {description}"

        # Performance: O(1) per keyword check using set membership
        for task_type, keywords in self.TASK_TYPE_KEYWORDS.items():
            if any(kw in combined for kw in keywords):
                return task_type

        return 'other'

    def _determine_stages(
        self,
        task_type: str,
        complexity: str,
        parallel_developers: int
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        Determine which stages to run/skip with guard clauses

        WHY: Guard clauses make stage selection logic clearer - check conditions
        and return early when appropriate, avoiding nested if/else logic.

        Returns:
            Tuple of (stages, skip_stages, reasoning)
        """
        stages = [
            'requirements_parsing', 'project_analysis', 'architecture',
            'dependencies', 'development', 'code_review',
            'validation', 'integration'
        ]
        skip_stages = ['arbitration']
        reasoning = []

        # Guard clause: Add arbitration if multiple developers
        if parallel_developers > 1:
            stages.insert(-1, 'arbitration')
            skip_stages.remove('arbitration')
        else:
            reasoning.append("Skipping arbitration (only one developer)")

        # Guard clause: Add testing unless documentation
        if task_type == 'documentation':
            reasoning.append("Skipping testing (documentation task)")
            return stages, skip_stages, reasoning

        # Add testing for non-documentation tasks
        stages.append('testing')
        return stages, skip_stages, reasoning
