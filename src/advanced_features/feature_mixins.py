#!/usr/bin/env python3
"""
Advanced Features Mixin Classes

WHY: Provides mixin pattern for sharing AI query capabilities across
multiple feature classes. Ensures DRY (Don't Repeat Yourself) by
centralizing common AI query patterns used by Thermodynamic Computing,
Two-Pass Pipeline, and Dynamic Pipeline features.

RESPONSIBILITY:
- Provide AdvancedFeaturesAIMixin for inheriting classes
- Ensure consistent AI query interface across features
- Manage AI capabilities instance lifecycle
- Provide backward-compatible API

PATTERNS:
- Mixin Pattern: Shared behavior across multiple classes
- Template Method: Common structure, specific implementations
- Dependency Injection: AI service provided by inheriting class
- Single Responsibility: Only provides AI query methods

USAGE:
    from advanced_features.feature_mixins import AdvancedFeaturesAIMixin

    class ThermodynamicComputing(AdvancedFeaturesAIMixin):
        def __init__(self, ai_service):
            self.ai_service = ai_service
            self.logger = logger

        def quantify_uncertainty(self, code):
            # Use mixin method
            return self.query_for_confidence(code, context="uncertainty")
"""

from typing import List, Dict, Any, Tuple, Optional
from abc import ABC

from advanced_features.ai_capabilities import AICapabilities
from advanced_features.models import (
    ConfidenceEstimate,
    RiskAssessment,
    QualityEvaluation
)


class AdvancedFeaturesAIMixin(ABC):
    """
    Mixin providing DRY AI query methods for advanced features.

    WHY: All three advanced features need AI queries. This mixin
    prevents code duplication and ensures consistent AI interaction patterns.

    Inheriting classes must have:
        - self.ai_service: Reference to AIQueryService
        - self.logger: Logger instance (optional)

    Provides methods for:
        - Confidence estimation (Thermodynamic Computing)
        - Code quality evaluation (Two-Pass Pipeline)
        - Risk assessment (all features)
        - Complexity estimation (Dynamic Pipeline)

    USAGE PATTERN:
        class YourFeature(AdvancedFeaturesAIMixin):
            def __init__(self, ai_service):
                self.ai_service = ai_service
                self.logger = logger  # optional

            def your_method(self):
                estimate = self.query_for_confidence(code, context)
                # Use estimate...
    """

    @property
    def _ai_capabilities(self) -> AICapabilities:
        """
        Lazy-load AI capabilities instance.

        WHY: Creates capabilities on-demand, avoiding initialization
        order issues in inheriting classes.

        Returns:
            AICapabilities instance

        Raises:
            AttributeError: If ai_service is not set on inheriting class
        """
        if not hasattr(self, '_capabilities_cache'):
            if not hasattr(self, 'ai_service'):
                raise AttributeError(
                    "Inheriting class must set self.ai_service before using mixin methods"
                )

            logger = getattr(self, 'logger', None)
            self._capabilities_cache = AICapabilities(self.ai_service, logger)

        return self._capabilities_cache

    # ========================================================================
    # CONFIDENCE ESTIMATION (Thermodynamic Computing Primary Use)
    # ========================================================================

    def query_for_confidence(
        self,
        code: str,
        context: str = "",
        requirements: Optional[str] = None,
        model: str = "sonnet"
    ) -> ConfidenceEstimate:
        """
        Query AI for confidence estimate of code quality/correctness.

        WHY: Thermodynamic Computing needs confidence scores to quantify
        uncertainty. Centralized here for DRY across all features.

        Args:
            code: Code to evaluate
            context: Additional context (e.g., "uncertainty", "risk")
            requirements: Original requirements for comparison
            model: LLM model to use

        Returns:
            ConfidenceEstimate with score and reasoning

        Example:
            estimate = self.query_for_confidence(
                code="def hello(): return 'hi'",
                context="uncertainty analysis",
                requirements="Function must greet user"
            )
            print(f"Confidence: {estimate.score}")
        """
        return self._ai_capabilities.query_for_confidence(
            code=code,
            context=context,
            requirements=requirements,
            model=model
        )

    # ========================================================================
    # RISK ASSESSMENT (All Features)
    # ========================================================================

    def query_for_risk_assessment(
        self,
        code: str,
        context: str = "",
        model: str = "sonnet"
    ) -> RiskAssessment:
        """
        Query AI for risk assessment of code/approach.

        WHY: All three features need risk assessment:
        - Thermodynamic: For Monte Carlo simulations
        - Two-Pass: For deciding rollback
        - Dynamic: For retry policies

        Args:
            code: Code to assess
            context: Additional context
            model: LLM model to use

        Returns:
            RiskAssessment with level and mitigations

        Example:
            assessment = self.query_for_risk_assessment(
                code="api_call()",
                context="External API dependency"
            )
            if assessment.is_critical_risk():
                # Handle critical risk
                pass
        """
        return self._ai_capabilities.query_for_risk_assessment(
            code=code,
            context=context,
            model=model
        )

    # ========================================================================
    # QUALITY EVALUATION (Two-Pass Pipeline Primary Use)
    # ========================================================================

    def query_for_quality(
        self,
        code: str,
        requirements: str = "",
        previous_version: Optional[str] = None,
        model: str = "sonnet"
    ) -> QualityEvaluation:
        """
        Query AI for code quality evaluation.

        WHY: Two-Pass Pipeline needs quality comparison between passes.
        Centralized for use by all features.

        Args:
            code: Code to evaluate
            requirements: Requirements to check against
            previous_version: Previous version for comparison
            model: LLM model to use

        Returns:
            QualityEvaluation with score and suggestions

        Example:
            evaluation = self.query_for_quality(
                code=second_pass_code,
                requirements=original_requirements,
                previous_version=first_pass_code
            )
            if evaluation.is_high_quality():
                # Accept second pass
                pass
        """
        return self._ai_capabilities.query_for_quality(
            code=code,
            requirements=requirements,
            previous_version=previous_version,
            model=model
        )

    # ========================================================================
    # COMPLEXITY ESTIMATION (Dynamic Pipeline Primary Use)
    # ========================================================================

    def query_for_complexity(
        self,
        requirements: str,
        context: str = "",
        model: str = "sonnet"
    ) -> Tuple[str, int, Dict[str, Any]]:
        """
        Query AI for complexity estimation.

        WHY: Dynamic Pipeline needs complexity to configure parallelization.
        Centralized for consistency.

        Args:
            requirements: Requirements to estimate
            context: Additional context
            model: LLM model to use

        Returns:
            Tuple of (complexity_level, story_points, details_dict)

        Example:
            complexity, points, details = self.query_for_complexity(
                requirements="Implement OAuth2 flow"
            )
            workers = details['suggested_workers']
            if complexity in ['complex', 'very_complex']:
                # Enable parallelization
                pass
        """
        return self._ai_capabilities.query_for_complexity(
            requirements=requirements,
            context=context,
            model=model
        )

    # ========================================================================
    # BATCH QUERIES (Optimization)
    # ========================================================================

    def batch_query_confidence(
        self,
        code_samples: List[Dict[str, str]],
        model: str = "sonnet"
    ) -> List[ConfidenceEstimate]:
        """
        Batch query for confidence estimates (more efficient).

        WHY: Thermodynamic Computing may need to evaluate multiple
        code paths. Batching reduces API calls.

        Args:
            code_samples: List of dicts with 'code' and 'context' keys
            model: LLM model to use

        Returns:
            List of ConfidenceEstimate objects

        Example:
            samples = [
                {'code': 'def a(): pass', 'context': 'Function A'},
                {'code': 'def b(): pass', 'context': 'Function B'}
            ]
            estimates = self.batch_query_confidence(samples)
            avg_confidence = sum(e.score for e in estimates) / len(estimates)
        """
        return self._ai_capabilities.batch_query_confidence(
            code_samples=code_samples,
            model=model
        )

    # ========================================================================
    # PRIVATE METHODS FOR BACKWARD COMPATIBILITY
    # ========================================================================

    def _build_confidence_prompt(
        self,
        code: str,
        context: str,
        requirements: Optional[str]
    ) -> str:
        """
        DEPRECATED: Provided for backward compatibility.
        Use PromptBuilder directly instead.
        """
        return self._ai_capabilities._prompt_builder.build_confidence_prompt(
            code=code,
            context=context,
            requirements=requirements
        )

    def _parse_confidence_response(
        self,
        response: str,
        model: str
    ) -> ConfidenceEstimate:
        """
        DEPRECATED: Provided for backward compatibility.
        Use ResponseParser directly instead.
        """
        return self._ai_capabilities._response_parser.parse_confidence_response(
            response=response,
            model=model
        )

    def _parse_risk_response(
        self,
        response: str,
        model: str
    ) -> RiskAssessment:
        """
        DEPRECATED: Provided for backward compatibility.
        Use ResponseParser directly instead.
        """
        return self._ai_capabilities._response_parser.parse_risk_response(
            response=response,
            model=model
        )

    def _parse_quality_response(
        self,
        response: str,
        model: str
    ) -> QualityEvaluation:
        """
        DEPRECATED: Provided for backward compatibility.
        Use ResponseParser directly instead.
        """
        return self._ai_capabilities._response_parser.parse_quality_response(
            response=response,
            model=model
        )

    def _parse_complexity_response(
        self,
        response: str
    ) -> Tuple[str, int, Dict[str, Any]]:
        """
        DEPRECATED: Provided for backward compatibility.
        Use ResponseParser directly instead.
        """
        estimate = self._ai_capabilities._response_parser.parse_complexity_response(
            response=response
        )
        details = {
            'reasoning': estimate.reasoning,
            'breakdown': estimate.breakdown,
            'parallelization_potential': estimate.parallelization_potential,
            'suggested_workers': estimate.suggested_workers
        }
        return (estimate.complexity_level, estimate.story_points, details)

    def _parse_batch_confidence_response(
        self,
        response: str,
        model: str
    ) -> List[ConfidenceEstimate]:
        """
        DEPRECATED: Provided for backward compatibility.
        Use ResponseParser directly instead.
        """
        return self._ai_capabilities._response_parser.parse_batch_confidence_response(
            response=response,
            model=model
        )
