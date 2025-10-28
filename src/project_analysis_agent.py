#!/usr/bin/env python3
"""
WHY: Backward compatibility wrapper for project_analysis_agent module
RESPONSIBILITY: Re-export all components from refactored package
PATTERNS: Facade pattern, deprecation path

BACKWARD COMPATIBILITY WRAPPER
===============================
This module maintains backward compatibility with existing code that imports
from project_analysis_agent.py. All functionality has been refactored into
the project_analysis/ package following SOLID principles.

Original file: 1,080 lines (monolithic)
Refactored: 6 modules with clear separation of concerns

Migration Guide:
---------------
Old import:
    from project_analysis_agent import ProjectAnalysisEngine, analyze_project

New import (recommended):
    from project_analysis import ProjectAnalysisEngine, analyze_project

Or use specific imports:
    from project_analysis.engine import ProjectAnalysisEngine
    from project_analysis.models import Severity, Issue, AnalysisResult
    from project_analysis.analyzers import ScopeAnalyzer, SecurityAnalyzer

Module Structure:
----------------
project_analysis/
├── __init__.py                    # Public API
├── models.py                      # Data classes and enums (95 lines)
├── interfaces.py                  # Abstract base class (51 lines)
├── engine.py                      # Analysis orchestration (221 lines)
├── approval_handler.py            # User approval logic (121 lines)
└── analyzers/
    ├── __init__.py               # Analyzer exports
    ├── rule_based.py             # Rule-based analyzers (314 lines)
    └── llm_powered.py            # LLM-powered analyzer (388 lines)

Benefits:
---------
✓ Single Responsibility: Each module has one clear purpose
✓ Open/Closed: Add new analyzers without modifying existing code
✓ Liskov Substitution: All analyzers implement DimensionAnalyzer interface
✓ Interface Segregation: Minimal, focused interfaces
✓ Dependency Inversion: Depends on abstractions, not concrete implementations
✓ Guard Clauses: Max 1 level nesting throughout
✓ Type Hints: Full type annotations (List, Dict, Any, Optional, Callable)
✓ Testability: Each component can be tested independently
"""

# Re-export all public components from refactored package
from project_analysis import (
    # Models
    Severity,
    Issue,
    AnalysisResult,
    ApprovalOptions,
    # Interfaces
    DimensionAnalyzer,
    # Engine
    ProjectAnalysisEngine,
    analyze_project,
    # Analyzers
    ScopeAnalyzer,
    SecurityAnalyzer,
    PerformanceAnalyzer,
    TestingAnalyzer,
    ErrorHandlingAnalyzer,
    LLMPoweredAnalyzer,
    # Approval Handler
    UserApprovalHandler,
)

# Maintain backward compatibility with original module
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
    # Approval Handler
    "UserApprovalHandler",
]

# Example usage (for backward compatibility)
if __name__ == "__main__":
    print("Project Analysis Agent - Example")
    print("=" * 60)

    # Sample task
    card = {
        "card_id": "test-001",
        "title": "Add user authentication",
        "description": "Add login functionality",
        "priority": "high",
        "points": 8
    }

    # Run analysis
    analysis = analyze_project(card)

    # Present findings
    handler = UserApprovalHandler()
    presentation = handler.present_findings(analysis)
    print(presentation)
