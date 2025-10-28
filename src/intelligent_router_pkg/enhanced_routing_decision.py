#!/usr/bin/env python3
"""
Enhanced Routing Decision Model

WHAT: Extension of base RoutingDecision with advanced feature recommendations.

WHY: Extends base routing decision with information needed by advanced pipeline
features while maintaining backward compatibility with existing orchestrator.

RESPONSIBILITY:
    - Extend base RoutingDecision with advanced feature data
    - Store feature recommendations, uncertainty analysis, and risk factors
    - Provide context for each advanced feature
    - Maintain backward compatibility

PATTERNS:
    - Inheritance: Extends RoutingDecision
    - Decorator Pattern: Adds additional data to base decision
    - Composite Pattern: Composes multiple analysis results
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from intelligent_router import RoutingDecision
from intelligent_router_pkg.advanced_feature_recommendation import AdvancedFeatureRecommendation
from intelligent_router_pkg.uncertainty_analysis import UncertaintyAnalysis
from intelligent_router_pkg.risk_factor import RiskFactor


@dataclass
class EnhancedRoutingDecision(RoutingDecision):
    """
    Routing decision enhanced with advanced feature recommendations.

    WHY: Extends base RoutingDecision with information needed by
    advanced pipeline features. Maintains backward compatibility
    with existing orchestrator.

    Attributes:
        feature_recommendation: Advanced feature intensity recommendations
        uncertainty_analysis: Uncertainty analysis for Thermodynamic Computing
        risk_factors: Risk factors for Monte Carlo simulation
        thermodynamic_context: Context for Thermodynamic Computing
        dynamic_pipeline_context: Context for Dynamic Pipeline
        two_pass_context: Context for Two-Pass Pipeline
    """
    # Advanced feature recommendations
    feature_recommendation: AdvancedFeatureRecommendation = None

    # Uncertainty analysis for Thermodynamic Computing
    uncertainty_analysis: UncertaintyAnalysis = None

    # Risk factors for Monte Carlo simulation
    risk_factors: List[RiskFactor] = field(default_factory=list)

    # Context for advanced features
    thermodynamic_context: Dict[str, Any] = field(default_factory=dict)
    dynamic_pipeline_context: Dict[str, Any] = field(default_factory=dict)
    two_pass_context: Dict[str, Any] = field(default_factory=dict)
