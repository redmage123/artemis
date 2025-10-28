#!/usr/bin/env python3
"""
Intelligent Router Enhanced - Backward Compatibility Wrapper

WHAT: Backward compatibility wrapper that re-exports the modularized
intelligent_router package components.

WHY: Maintains existing import paths while using the new modular structure.
Allows gradual migration of dependent code.

MIGRATION: This is a compatibility shim. New code should import from:
    from intelligent_router import IntelligentRouterEnhanced

DEPRECATED: This wrapper will be removed in a future version.
Update imports to use the intelligent_router package directly.
"""

# Re-export all public components from the intelligent_router package
from intelligent_router_pkg import (
    # Data Models
    RiskFactor,
    UncertaintyAnalysis,
    AdvancedFeatureRecommendation,
    EnhancedRoutingDecision,

    # Calculators and Identifiers
    UncertaintyCalculator,
    RiskIdentifier,
    BenefitCalculator,

    # Recommenders and Creators
    ModeRecommender,
    ContextCreator,
    PromptGenerator,

    # Logging
    DecisionLogger,

    # Main Router
    IntelligentRouterEnhanced,
)

__all__ = [
    # Data Models
    'RiskFactor',
    'UncertaintyAnalysis',
    'AdvancedFeatureRecommendation',
    'EnhancedRoutingDecision',

    # Calculators and Identifiers
    'UncertaintyCalculator',
    'RiskIdentifier',
    'BenefitCalculator',

    # Recommenders and Creators
    'ModeRecommender',
    'ContextCreator',
    'PromptGenerator',

    # Logging
    'DecisionLogger',

    # Main Router
    'IntelligentRouterEnhanced',
]
