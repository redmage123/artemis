#!/usr/bin/env python3
"""
WHY: Routing package for intelligent pipeline stage selection.

RESPONSIBILITY:
- Export all public routing classes and models
- Provide clean package interface
- Enable easy imports from routing package

PATTERNS:
- Facade Pattern: Single entry point to routing subsystem
- Explicit Exports: __all__ defines public interface
"""

from routing.models import (
    StageDecision,
    TaskRequirements,
    RoutingDecision
)

from routing.complexity_classifier import ComplexityClassifier
from routing.task_analyzer import TaskAnalyzer
from routing.stage_selector import StageSelector
from routing.policy_enforcer import PolicyEnforcer
from routing.decision_maker import DecisionMaker
from routing.intelligent_router import IntelligentRouter


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
