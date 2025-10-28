"""
Module: orchestrator/workflow_planner.py

WHY: Analyze task characteristics and generate optimal workflow execution plans.
RESPONSIBILITY: Map task complexity/type to resource allocation and execution strategy.
PATTERNS: Strategy Pattern (complexity-based strategies), Builder Pattern (plan construction).

This module handles:
- Task complexity analysis (simple/medium/complex)
- Task type detection (feature/bugfix/refactor/documentation)
- Workflow plan generation (stages, resources, strategy)
- Platform-aware resource allocation

EXTRACTED FROM: artemis_orchestrator.py (lines 107-328, 220 lines)
"""

from typing import Dict, Optional
from platform_detector import ResourceAllocation


class WorkflowPlanner:
    """
    Dynamic Workflow Planner (Already SOLID-compliant)

    WHAT:
    Analyzes task characteristics (complexity, type, priority) and generates optimal
    workflow execution plans with appropriate resource allocation.

    WHY:
    Different tasks require different execution strategies. A simple bugfix doesn't need
    3 parallel developers, while a complex architecture refactor does. This class
    analyzes task metadata and determines the optimal workflow configuration.

    PATTERNS:
    - Strategy Pattern: Different complexity levels use different execution strategies
    - Builder Pattern: Constructs workflow plans incrementally
    - Configuration Pattern: Maps complexity → execution parameters

    INTEGRATION:
    - Used by: ArtemisOrchestrator (creates plans before pipeline execution)
    - Uses: PlatformDetector via ResourceAllocation (respects platform limits)
    - Output: Dict consumed by pipeline execution strategies

    ATTRIBUTES:
        card: Kanban card with task details (title, description, priority, points)
        verbose: Whether to log detailed analysis
        resource_allocation: Platform resource limits (max developers, tests)
        complexity: Calculated task complexity (simple/medium/complex)
        task_type: Inferred task type (feature/bugfix/refactor/documentation)
    """

    def __init__(self, card: Dict, verbose: bool = True, resource_allocation: Optional['ResourceAllocation'] = None):
        self.card = card
        self.verbose = verbose
        self.resource_allocation = resource_allocation
        self.complexity = self._analyze_complexity()
        self.task_type = self._determine_task_type()

    def _analyze_complexity(self) -> str:
        """
        Analyze task complexity using multi-factor scoring algorithm

        WHAT:
        Computes complexity score by weighing priority, story points, and keyword presence,
        then maps score to complexity level (simple/medium/complex).

        WHY:
        Task complexity determines resource allocation. Complex tasks need more developers,
        longer timeouts, and parallel execution. This algorithm provides consistent,
        data-driven complexity assessment.

        ALGORITHM:
        1. Priority contribution: high=2, medium=1, low=0
        2. Story points contribution: ≥13 → +3, ≥8 → +2, ≥5 → +1
        3. Keyword analysis: complex keywords (+1 each, max 3), simple keywords (-1 each, max 2)
        4. Final mapping: score ≥6 → complex, ≥3 → medium, else simple

        RETURNS:
            str: Complexity level ('simple', 'medium', or 'complex')
        """
        # Calculate complexity score using configuration
        priority_scores = {'high': 2, 'medium': 1, 'low': 0}
        points_thresholds = [(13, 3), (8, 2), (5, 1)]
        complexity_thresholds = [(6, 'complex'), (3, 'medium'), (0, 'simple')]

        complexity_score = 0

        # Priority contribution
        priority = self.card.get('priority', 'medium')
        complexity_score += priority_scores.get(priority, 1)

        # Story points contribution
        points = self.card.get('points', 5)
        complexity_score += next((score for threshold, score in points_thresholds if points >= threshold), 0)

        # Keywords contribution
        description = self.card.get('description', '').lower()
        complex_keywords = ['integrate', 'architecture', 'refactor', 'migrate',
                           'performance', 'scalability', 'distributed', 'api']
        simple_keywords = ['fix', 'update', 'small', 'minor', 'simple', 'quick']

        complex_count = sum(1 for kw in complex_keywords if kw in description)
        simple_count = sum(1 for kw in simple_keywords if kw in description)

        complexity_score += min(complex_count, 3) - min(simple_count, 2)

        # Determine complexity level
        return next(level for threshold, level in complexity_thresholds if complexity_score >= threshold)

    def _determine_task_type(self) -> str:
        """
        Determine task type using keyword matching

        WHAT:
        Scans title and description for type-specific keywords to classify task.

        WHY:
        Task type affects stage selection. Documentation tasks skip testing,
        bugfixes need validation, refactors need architecture review. Accurate
        type detection enables optimal stage filtering.

        ALGORITHM:
        Priority-ordered keyword matching:
        1. 'bugfix': bug, fix, error, issue
        2. 'refactor': refactor, restructure, cleanup
        3. 'documentation': docs, documentation, readme
        4. 'feature': feature, implement, add, create
        5. 'other': default if no matches

        RETURNS:
            str: Task type ('bugfix', 'refactor', 'documentation', 'feature', or 'other')
        """
        description = self.card.get('description', '').lower()
        title = self.card.get('title', '').lower()
        combined = f"{title} {description}"

        # Define task type keywords in priority order
        task_type_keywords = [
            ('bugfix', ['bug', 'fix', 'error', 'issue']),
            ('refactor', ['refactor', 'restructure', 'cleanup']),
            ('documentation', ['docs', 'documentation', 'readme']),
            ('feature', ['feature', 'implement', 'add', 'create'])
        ]

        # Return first matching task type or 'other'
        return next(
            (task_type for task_type, keywords in task_type_keywords if any(kw in combined for kw in keywords)),
            'other'
        )

    def create_workflow_plan(self) -> Dict:
        """
        Create workflow plan based on complexity

        WHAT:
        Generates complete workflow execution plan including stage list, resource
        allocation, execution strategy, and reasoning for decisions.

        WHY:
        Pipeline orchestrator needs explicit instructions on which stages to run,
        how many parallel workers to use, and what execution strategy to employ.
        This method translates task analysis into actionable workflow configuration.

        LOGIC:
        1. Start with full stage list (requirements → testing)
        2. Determine parallel developers from complexity (complex=3, medium=2, simple=1)
        3. Cap parallelization based on platform resources (respects max_parallel_developers)
        4. Set max_parallel_tests from platform allocation
        5. Add arbitration stage only if multiple developers
        6. Skip testing for documentation tasks
        7. Choose execution strategy (parallel if >1 developer, else sequential)

        RETURNS:
            Dict: Workflow plan with keys:
                - complexity: str (simple/medium/complex)
                - task_type: str (feature/bugfix/etc)
                - stages: List[str] (ordered stage names)
                - skip_stages: List[str] (stages to skip)
                - parallel_developers: int (1-N)
                - max_parallel_tests: int (platform-dependent)
                - execution_strategy: str (sequential/parallel)
                - reasoning: List[str] (human-readable decisions)
        """
        plan = {
            'complexity': self.complexity,
            'task_type': self.task_type,
            'stages': ['requirements_parsing', 'project_analysis', 'architecture', 'dependencies', 'development', 'code_review', 'validation', 'integration'],
            'parallel_developers': 1,
            'max_parallel_tests': 4,  # Default for backward compatibility
            'skip_stages': ['arbitration'],
            'execution_strategy': 'sequential',
            'reasoning': []
        }

        # Determine parallel developers using configuration mapping
        complexity_config = {
            'complex': {'parallel_developers': 3, 'execution_strategy': 'parallel'},
            'medium': {'parallel_developers': 2, 'execution_strategy': 'parallel'},
            'simple': {'parallel_developers': 1, 'execution_strategy': 'sequential'}
        }

        config = complexity_config.get(self.complexity, complexity_config['simple'])
        desired_parallel_developers = config['parallel_developers']

        # Cap parallel developers based on platform resource allocation
        if not self.resource_allocation:
            plan['parallel_developers'] = desired_parallel_developers
        else:
            plan['parallel_developers'] = min(
                desired_parallel_developers,
                self.resource_allocation.max_parallel_developers
            )
            if plan['parallel_developers'] < desired_parallel_developers:
                plan['reasoning'].append(
                    f"Limited parallel developers to {plan['parallel_developers']} "
                    f"(platform resources: {self.resource_allocation.max_parallel_developers} max)"
                )

        plan['execution_strategy'] = config.get('execution_strategy', 'sequential')

        # Set max parallel tests based on platform resource allocation
        if self.resource_allocation:
            plan['max_parallel_tests'] = self.resource_allocation.max_parallel_tests
            plan['reasoning'].append(
                f"Max parallel tests set to {plan['max_parallel_tests']} based on platform resources"
            )

        # Skip arbitration if only one developer
        if plan['parallel_developers'] == 1:
            plan['reasoning'].append("Skipping arbitration (only one developer)")
        else:
            plan['stages'].insert(-1, 'arbitration')  # Insert before integration
            plan['skip_stages'].remove('arbitration')

        # Add testing unless documentation
        if self.task_type != 'documentation':
            plan['stages'].append('testing')
        else:
            plan['skip_stages'].append('testing')

        return plan


__all__ = [
    "WorkflowPlanner"
]
