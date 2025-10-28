#!/usr/bin/env python3
"""
Module: project_complexity.py

WHY: Project complexity directly impacts pipeline stage selection, validation depth,
     and resource allocation decisions.

RESPONSIBILITY: Define complexity levels with clear indicators for pipeline configuration.

PATTERNS:
    - Strategy Selection: Used to select appropriate pipeline strategies
    - Configuration: Drives stage filtering and validation intensity
"""

from enum import Enum


class ProjectComplexity(Enum):
    """
    Project complexity levels for stage selection.

    Why needed: Determines which stages to include and how much validation
    to perform. Simple projects skip expensive validation, complex projects
    include all quality gates.

    Complexity indicators:
        SIMPLE: <100 LOC, no dependencies, single file
        MODERATE: <1000 LOC, few dependencies, multiple files
        COMPLEX: >1000 LOC, many dependencies, microservices
        ENTERPRISE: >10K LOC, multiple repos, infrastructure
    """
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    ENTERPRISE = "enterprise"
