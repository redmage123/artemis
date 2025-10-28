#!/usr/bin/env python3
"""
Constants for orchestration planning

WHY:
Centralizes pipeline stage definitions, dependencies, and durations as immutable constants,
providing O(1) lookup performance and a single source of truth for pipeline configuration.

RESPONSIBILITY:
- Define valid pipeline stages
- Define stage dependency graph (DAG structure)
- Define estimated durations for Critical Path Method

PATTERNS:
- Constants Pattern: Immutable configuration data
- DAG Structure: Adjacency list for dependency graph
- O(1) Lookups: Sets and dicts for optimal performance
"""

import re
from typing import Dict, Set


# Performance: Pre-compiled regex patterns (O(1) pattern access)
JSON_CODE_BLOCK_PATTERN = re.compile(r'```(?:json)?\s*(\{.*?\})\s*```', re.DOTALL)
JSON_INLINE_PATTERN = re.compile(r'(\{.*\})', re.DOTALL)

# Performance: O(1) validation set instead of O(n) list searches
VALID_STAGES = {
    'requirements_parsing', 'ssd_generation', 'sprint_planning',
    'project_analysis', 'architecture', 'project_review',
    'dependencies', 'development', 'arbitration', 'code_review',
    'uiux', 'validation', 'integration', 'testing'
}

# Performance: O(1) stage dependency lookup using DAG adjacency list
# Industry Algorithm: Directed Acyclic Graph for stage dependencies
STAGE_DEPENDENCIES: Dict[str, Set[str]] = {
    'requirements_parsing': set(),  # No dependencies
    'ssd_generation': {'requirements_parsing'},
    'sprint_planning': {'requirements_parsing'},
    'project_analysis': {'requirements_parsing'},
    'architecture': {'project_analysis'},
    'project_review': {'architecture'},
    'dependencies': {'project_review'},
    'development': {'dependencies', 'architecture'},
    'arbitration': {'development'},  # Only if multiple developers
    'code_review': {'development', 'arbitration'},
    'uiux': {'development'},
    'validation': {'development', 'code_review'},
    'integration': {'validation'},
    'testing': {'integration'}
}

# Performance: O(1) estimated duration lookup
# Used for Critical Path Method calculation
STAGE_ESTIMATED_DURATIONS: Dict[str, int] = {
    'requirements_parsing': 5,  # minutes
    'ssd_generation': 10,
    'sprint_planning': 8,
    'project_analysis': 5,
    'architecture': 10,
    'project_review': 8,
    'dependencies': 3,
    'development': 30,  # Most time-consuming
    'arbitration': 5,
    'code_review': 15,
    'uiux': 12,
    'validation': 10,
    'integration': 8,
    'testing': 15
}
