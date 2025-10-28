#!/usr/bin/env python3
"""
AI-Powered Orchestration Planning Package

WHY:
Provides AI-powered and rule-based orchestration planning for pipeline execution,
using industry-standard algorithms (DAG, Topological Sort, Critical Path Method,
Dynamic Programming) to optimize stage ordering, resource allocation, and duration estimation.

RESPONSIBILITY:
- Export all orchestration planning components
- Provide unified interface for external modules
- Maintain backward compatibility

PATTERNS:
- Package Pattern: Organized module structure
- Facade Pattern: Simplified interface to complex subsystem
- Strategy Pattern: Multiple planning strategies
- Factory Pattern: Planner creation

ALGORITHMS:
- Directed Acyclic Graph (DAG): Stage dependencies
- Topological Sort (Kahn's Algorithm): O(V+E) stage ordering
- Critical Path Method (CPM): O(V+E) duration estimation
- Dynamic Programming: O(1) resource optimization
- Hash-based Caching: O(1) plan retrieval

EXPORTS:
Enums:
- Complexity: Task complexity levels (SIMPLE, MEDIUM, COMPLEX)
- ExecutionStrategy: Execution strategies (SEQUENTIAL, PARALLEL)

Constants:
- VALID_STAGES: Set of valid pipeline stages
- STAGE_DEPENDENCIES: DAG adjacency list
- STAGE_ESTIMATED_DURATIONS: Stage duration map
- VALID_COMPLEXITIES: Valid complexity values
- VALID_EXECUTION_STRATEGIES: Valid strategy values

Data Structures:
- OrchestrationPlan: Immutable plan data structure

Algorithms:
- StageDAG: Topological sort + critical path
- ResourceOptimizer: Dynamic programming resource allocation
- PlanCache: Hash-based plan caching

Planners:
- OrchestrationPlannerInterface: Abstract interface
- AIOrchestrationPlanner: AI-powered planner
- RuleBasedOrchestrationPlanner: Rule-based planner
- OrchestrationPlannerFactory: Planner factory
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Enums
from ai_orchestration.enums import (
    Complexity,
    ExecutionStrategy,
    VALID_COMPLEXITIES,
    VALID_EXECUTION_STRATEGIES,
)

# Constants
from ai_orchestration.constants import (
    JSON_CODE_BLOCK_PATTERN,
    JSON_INLINE_PATTERN,
    VALID_STAGES,
    STAGE_DEPENDENCIES,
    STAGE_ESTIMATED_DURATIONS,
)

# Core classes
from ai_orchestration.orchestration_plan import OrchestrationPlan
from ai_orchestration.stage_dag import StageDAG
from ai_orchestration.resource_optimizer import ResourceOptimizer
from ai_orchestration.plan_cache import PlanCache

# Planner interface and implementations
from ai_orchestration.planner_interface import OrchestrationPlannerInterface
from ai_orchestration.ai_planner import AIOrchestrationPlanner
from ai_orchestration.rule_based_planner import RuleBasedOrchestrationPlanner
from ai_orchestration.planner_factory import OrchestrationPlannerFactory

__all__ = [
    # Enums
    'Complexity',
    'ExecutionStrategy',
    'VALID_COMPLEXITIES',
    'VALID_EXECUTION_STRATEGIES',
    # Constants
    'JSON_CODE_BLOCK_PATTERN',
    'JSON_INLINE_PATTERN',
    'VALID_STAGES',
    'STAGE_DEPENDENCIES',
    'STAGE_ESTIMATED_DURATIONS',
    # Core classes
    'OrchestrationPlan',
    'StageDAG',
    'ResourceOptimizer',
    'PlanCache',
    # Planners
    'OrchestrationPlannerInterface',
    'AIOrchestrationPlanner',
    'RuleBasedOrchestrationPlanner',
    'OrchestrationPlannerFactory',
]
