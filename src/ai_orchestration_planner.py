#!/usr/bin/env python3
"""
AI-Powered Orchestration Planner - Backward Compatibility Wrapper

This module maintains backward compatibility by re-exporting all components from
the ai_orchestration package. All implementation has been moved to dedicated modules.

MIGRATION PATH:
Old: from ai_orchestration_planner import AIOrchestrationPlanner
New: from ai_orchestration import AIOrchestrationPlanner

Both imports work identically. Update imports gradually to use the new package structure.

SOLID Principles Applied:
- Single Responsibility: Each class has one clear purpose
- Open/Closed: Can add new planning strategies without modifying existing code
- Liskov Substitution: All planners implement OrchestrationPlannerInterface
- Interface Segregation: Minimal, focused interfaces
- Dependency Inversion: Depends on abstractions (interfaces), not concretions

Design Patterns:
- Strategy Pattern: Multiple planning strategies (AI, Rule-based, Hybrid)
- Factory Pattern: PlannerFactory creates appropriate planner instances
- Template Method: Base class defines algorithm structure, subclasses fill in details
- Singleton (for caching): PromptTemplate cache to avoid rebuilding prompts
- Memento Pattern: Caching of previously generated plans

Performance Optimizations:
- O(1) stage lookup using sets and dicts instead of O(n) list operations
- Pre-compiled regex patterns for JSON extraction
- Cached prompt templates to avoid string rebuilding
- Single-pass validation instead of multiple iterations
- Memoization of plan generation for identical inputs

Industry-Standard Algorithms:
- DAG (Directed Acyclic Graph): Models stage dependencies for topological ordering
- Topological Sort: O(V+E) optimal stage execution order
- Critical Path Method (CPM): O(V+E) identifies longest path determining min duration
- Dynamic Programming: O(n*capacity) optimal resource allocation with memoization
- Hash-based caching: O(1) plan retrieval for repeated tasks
"""

# Re-export all components from ai_orchestration package
from ai_orchestration import (
    # Enums
    Complexity,
    ExecutionStrategy,
    VALID_COMPLEXITIES,
    VALID_EXECUTION_STRATEGIES,
    # Constants
    JSON_CODE_BLOCK_PATTERN,
    JSON_INLINE_PATTERN,
    VALID_STAGES,
    STAGE_DEPENDENCIES,
    STAGE_ESTIMATED_DURATIONS,
    # Core classes
    OrchestrationPlan,
    StageDAG,
    ResourceOptimizer,
    PlanCache,
    # Planners
    OrchestrationPlannerInterface,
    AIOrchestrationPlanner,
    RuleBasedOrchestrationPlanner,
    OrchestrationPlannerFactory,
)

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
