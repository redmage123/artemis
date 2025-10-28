#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY WRAPPER

WHY: Maintain backward compatibility while routing module is modularized.

RESPONSIBILITY:
- Re-export all components from routing package
- Provide identical interface to original module
- Enable gradual migration to new package structure
- Prevent breaking changes to existing code

PATTERNS:
- Adapter Pattern: Maintains old interface while delegating to new implementation
- Deprecation Pattern: Allows gradual migration
- Re-export Pattern: Transparent forwarding to new location

MIGRATION PATH:
Old code:
    from intelligent_router import IntelligentRouter, StageDecision

New code (preferred):
    from routing import IntelligentRouter, StageDecision

This wrapper allows both imports to work during migration period.
"""

# Re-export all public components from routing package
from routing import (
    # Models
    StageDecision,
    TaskRequirements,
    RoutingDecision,

    # Components
    ComplexityClassifier,
    TaskAnalyzer,
    StageSelector,
    PolicyEnforcer,
    DecisionMaker,

    # Main Router
    IntelligentRouter,
)

__all__ = [
    # Models
    'StageDecision',
    'TaskRequirements',
    'RoutingDecision',

    # Components
    'ComplexityClassifier',
    'TaskAnalyzer',
    'StageSelector',
    'PolicyEnforcer',
    'DecisionMaker',

    # Main Router
    'IntelligentRouter',
]
