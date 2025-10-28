#!/usr/bin/env python3
"""
WHY: Project analysis package for pre-implementation task validation
RESPONSIBILITY: Export public API for project analysis functionality
PATTERNS: Package initialization, clean API surface

Project Analysis Package - Analyzes tasks BEFORE implementation across 8 dimensions
to identify issues, suggest improvements, and get user approval.

Public API:
- Models: Severity, Issue, AnalysisResult, ApprovalOptions
- Interfaces: DimensionAnalyzer
- Engine: ProjectAnalysisEngine, analyze_project
- Analyzers: ScopeAnalyzer, SecurityAnalyzer, PerformanceAnalyzer, etc.
- Approval: UserApprovalHandler
"""

# Models
from project_analysis.models import (
    AnalysisResult,
    ApprovalOptions,
    Issue,
    Severity,
)

# Interfaces
from project_analysis.interfaces import DimensionAnalyzer

# Engine
from project_analysis.engine import ProjectAnalysisEngine, analyze_project

# Analyzers
from project_analysis.analyzers.rule_based import (
    ErrorHandlingAnalyzer,
    PerformanceAnalyzer,
    ScopeAnalyzer,
    SecurityAnalyzer,
    TestingAnalyzer,
)
from project_analysis.analyzers.llm_powered import LLMPoweredAnalyzer

# Approval Handler
from project_analysis.approval_handler import UserApprovalHandler

__all__ = [
    # Models
    "Severity",
    "Issue",
    "AnalysisResult",
    "ApprovalOptions",
    # Interfaces
    "DimensionAnalyzer",
    # Engine
    "ProjectAnalysisEngine",
    "analyze_project",
    # Analyzers
    "ScopeAnalyzer",
    "SecurityAnalyzer",
    "PerformanceAnalyzer",
    "TestingAnalyzer",
    "ErrorHandlingAnalyzer",
    "LLMPoweredAnalyzer",
    # Approval
    "UserApprovalHandler",
]
