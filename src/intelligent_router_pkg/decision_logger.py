#!/usr/bin/env python3
"""
Decision Logger

WHAT: Logs enhanced routing decisions with feature recommendations.

WHY: Transparency into why advanced features were recommended helps with
debugging, tuning, and user trust.

RESPONSIBILITY:
    - Log routing decisions
    - Log feature recommendations
    - Log uncertainty analysis
    - Log risk factors
    - Format output for readability

PATTERNS:
    - Observer Pattern: Observes and logs routing decisions
    - Guard Clause Pattern: Early returns for missing data
"""

from typing import List
from intelligent_router_pkg.enhanced_routing_decision import EnhancedRoutingDecision
from intelligent_router_pkg.advanced_feature_recommendation import AdvancedFeatureRecommendation
from intelligent_router_pkg.uncertainty_analysis import UncertaintyAnalysis
from intelligent_router_pkg.risk_factor import RiskFactor


class DecisionLogger:
    """
    Logs enhanced routing decisions with feature recommendations.

    WHY: Provides transparency into why advanced features were recommended.
    """

    def __init__(self, logger, base_logger_func):
        """
        Initialize decision logger.

        Args:
            logger: Logger instance
            base_logger_func: Function to log base routing decisions
        """
        self.logger = logger
        self.base_logger_func = base_logger_func

    def log_enhanced_decision(self, decision: EnhancedRoutingDecision) -> None:
        """
        Log enhanced routing decision with advanced feature recommendations.

        Args:
            decision: Enhanced routing decision to log
        """
        if not self.logger:
            return

        # Log base routing decision
        self.base_logger_func(decision)

        # Log advanced feature recommendations
        self.logger.log("=" * 60, "INFO")
        self.logger.log("🚀 ADVANCED FEATURE RECOMMENDATIONS", "INFO")
        self.logger.log("=" * 60, "INFO")

        rec = decision.feature_recommendation
        self.logger.log(f"Recommended Mode: {rec.recommended_mode.value.upper()}", "INFO")
        self.logger.log(f"Confidence: {rec.confidence_in_recommendation:.0%}", "INFO")
        self.logger.log(f"Rationale: {rec.rationale}", "INFO")
        self.logger.log("", "INFO")

        self.logger.log("Features to Enable:", "INFO")
        self.logger.log(f"  Dynamic Pipeline: {'✓' if rec.use_dynamic_pipeline else '✗'}", "INFO")
        self.logger.log(f"  Two-Pass: {'✓' if rec.use_two_pass else '✗'}", "INFO")
        self.logger.log(f"  Thermodynamic: {'✓' if rec.use_thermodynamic else '✗'}", "INFO")
        self.logger.log("", "INFO")

        # Log expected benefits
        self._log_expected_benefits(rec)

        # Log uncertainty analysis
        self._log_uncertainty_analysis(decision.uncertainty_analysis)

        # Log risk factors
        self._log_risk_factors(decision.risk_factors)

        self.logger.log("=" * 60, "INFO")

    def _log_expected_benefits(self, rec: AdvancedFeatureRecommendation) -> None:
        """Log expected benefits - extracted to eliminate nested if."""
        if not rec.expected_benefits:
            return  # Early return guard

        self.logger.log("Expected Benefits:", "INFO")
        for benefit in rec.expected_benefits:
            self.logger.log(f"  • {benefit}", "INFO")
        self.logger.log("", "INFO")

    def _log_uncertainty_analysis(self, unc: UncertaintyAnalysis) -> None:
        """Log uncertainty analysis - extracted to eliminate nested if."""
        self.logger.log("Uncertainty Analysis:", "INFO")
        self.logger.log(f"  Overall: {unc.overall_uncertainty:.0%} ({unc.confidence_level})", "INFO")
        self.logger.log(f"  Similar Tasks: {unc.similar_task_history}", "INFO")

        if not unc.known_unknowns:
            self.logger.log("", "INFO")
            return  # Early return guard

        self.logger.log(f"  Known Unknowns:", "INFO")
        for unknown in unc.known_unknowns[:3]:  # Limit to 3
            self.logger.log(f"    - {unknown}", "INFO")
        self.logger.log("", "INFO")

    def _log_risk_factors(self, risk_factors: List[RiskFactor]) -> None:
        """Log risk factors - extracted to eliminate nested if."""
        if not risk_factors:
            return  # Early return guard

        self.logger.log(f"Risk Factors Identified: {len(risk_factors)}", "INFO")
        for risk in risk_factors:
            severity_level = "WARNING" if risk.severity in ['high', 'critical'] else "INFO"
            self.logger.log(
                f"  ⚠️  {risk.risk_type.upper()}: {risk.description} "
                f"(severity: {risk.severity}, probability: {risk.probability:.0%})",
                severity_level
            )
        self.logger.log("", "INFO")
