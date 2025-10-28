#!/usr/bin/env python3
"""
Query Type Enumeration

WHY: Defines the types of AI queries that can be executed through the service.

RESPONSIBILITY:
- Enumerate all supported query types
- Provide type safety for query operations
- Enable query-specific routing and metrics

PATTERNS:
- Enum pattern for type safety
- No behavior, only type definitions
"""

from enum import Enum


class QueryType(Enum):
    """Type of AI query being performed"""
    REQUIREMENTS_PARSING = "requirements_parsing"
    ARCHITECTURE_DESIGN = "architecture_design"
    CODE_REVIEW = "code_review"
    CODE_GENERATION = "code_generation"
    PROJECT_ANALYSIS = "project_analysis"
    ERROR_RECOVERY = "error_recovery"
    RETROSPECTIVE = "retrospective"
    SPRINT_PLANNING = "sprint_planning"
    UIUX_EVALUATION = "uiux_evaluation"
