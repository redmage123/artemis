#!/usr/bin/env python3
"""
Intelligent Router Package - Enhanced Router with Advanced Features

WHAT: Modularized intelligent routing system with advanced feature integration.

WHY: Provides intelligent stage selection and advanced feature recommendations
(Dynamic Pipeline, Two-Pass, Thermodynamic Computing) based on task analysis.

ARCHITECTURE:
    - Data Models: Risk, Uncertainty, Recommendations, Decisions
    - Calculators: Uncertainty, Risk, Benefit calculation
    - Recommenders: Mode and intensity recommendation
    - Context: Context creation for advanced features
    - Prompts: Prompt generation for features
    - Logging: Decision logging and visualization
    - Router: Main enhanced router class

PATTERNS:
    - Facade: Simple interface to complex routing logic
    - Strategy: Different strategies for different task types
    - Factory: Creates routing decisions and recommendations
    - Observer: Logs routing decisions
"""

# Data Models
from intelligent_router_pkg.risk_factor import RiskFactor
from intelligent_router_pkg.uncertainty_analysis import UncertaintyAnalysis
from intelligent_router_pkg.advanced_feature_recommendation import AdvancedFeatureRecommendation
from intelligent_router_pkg.enhanced_routing_decision import EnhancedRoutingDecision

# Calculators and Identifiers
from intelligent_router_pkg.uncertainty_calculator import UncertaintyCalculator
from intelligent_router_pkg.risk_identifier import RiskIdentifier
from intelligent_router_pkg.benefit_calculator import BenefitCalculator

# Recommenders and Creators
from intelligent_router_pkg.mode_recommender import ModeRecommender
from intelligent_router_pkg.context_creator import ContextCreator
from intelligent_router_pkg.prompt_generator import PromptGenerator

# Logging
from intelligent_router_pkg.decision_logger import DecisionLogger

# Main Router
from intelligent_router_pkg.enhanced_router import IntelligentRouterEnhanced

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
