#!/usr/bin/env python3
"""
Advanced Features AI Capabilities

WHY: Provides core AI query functionality for advanced features. This module
coordinates between prompt building, AI service calls, and response parsing
to deliver structured results.

RESPONSIBILITY:
- Execute AI queries for confidence estimation
- Execute AI queries for risk assessment
- Execute AI queries for quality evaluation
- Execute AI queries for complexity estimation
- Coordinate prompt building, AI calls, and response parsing
- Handle AI service errors and retries

PATTERNS:
- Facade Pattern: Simplified interface to complex subsystems
- Dependency Injection: AI service provided by caller
- Guard Clauses: Early returns for invalid inputs
- Single Responsibility: Only handles AI query orchestration

USAGE:
    from advanced_features.ai_capabilities import AICapabilities

    capabilities = AICapabilities(ai_service)
    estimate = capabilities.query_for_confidence(
        code="def hello()...",
        context="uncertainty analysis"
    )
"""

from typing import List, Dict, Any, Tuple, Optional

from artemis_exceptions import LLMError, wrap_exception
from advanced_features.models import (
    ConfidenceEstimate,
    RiskAssessment,
    QualityEvaluation,
    ComplexityEstimate
)
from advanced_features.prompt_builder import PromptBuilder
from advanced_features.response_parser import ResponseParser


class AICapabilities:
    """
    Provides AI query capabilities for advanced features.

    WHY: Coordinates prompt building, AI service interaction, and response
    parsing to provide clean API for feature implementations.
    """

    def __init__(self, ai_service, logger=None):
        """
        Initialize AI capabilities.

        Args:
            ai_service: AIQueryService instance for making queries
            logger: Optional logger for debugging
        """
        self.ai_service = ai_service
        self.logger = logger
        self._prompt_builder = PromptBuilder()
        self._response_parser = ResponseParser()

        # Default query parameters
        self._default_temperature = 0.3  # Low temp for consistent evaluation
        self._default_max_tokens = 2048

    # ========================================================================
    # CONFIDENCE ESTIMATION
    # ========================================================================

    @wrap_exception(LLMError, "Confidence estimation failed")
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

        Raises:
            LLMError: If query or parsing fails
        """
        # Guard clause: empty code
        if not code or not code.strip():
            raise ValueError("Code cannot be empty")

        # Build prompt
        prompt = self._prompt_builder.build_confidence_prompt(
            code=code,
            context=context,
            requirements=requirements
        )

        # Query AI service
        result = self.ai_service.query(
            prompt=prompt,
            model=model,
            temperature=self._default_temperature,
            max_tokens=self._default_max_tokens
        )

        # Parse response
        return self._response_parser.parse_confidence_response(
            response=result.llm_response.content,
            model=model
        )

    # ========================================================================
    # RISK ASSESSMENT
    # ========================================================================

    @wrap_exception(LLMError, "Risk assessment failed")
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

        Raises:
            LLMError: If query or parsing fails
        """
        # Guard clause: empty code
        if not code or not code.strip():
            raise ValueError("Code cannot be empty")

        # Build prompt
        prompt = self._prompt_builder.build_risk_prompt(
            code=code,
            context=context
        )

        # Query AI service
        result = self.ai_service.query(
            prompt=prompt,
            model=model,
            temperature=self._default_temperature,
            max_tokens=self._default_max_tokens
        )

        # Parse response
        return self._response_parser.parse_risk_response(
            response=result.llm_response.content,
            model=model
        )

    # ========================================================================
    # QUALITY EVALUATION
    # ========================================================================

    @wrap_exception(LLMError, "Quality evaluation failed")
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

        Raises:
            LLMError: If query or parsing fails
        """
        # Guard clause: empty code
        if not code or not code.strip():
            raise ValueError("Code cannot be empty")

        # Build prompt
        prompt = self._prompt_builder.build_quality_prompt(
            code=code,
            requirements=requirements,
            previous_version=previous_version
        )

        # Query AI service with higher token limit for detailed evaluation
        result = self.ai_service.query(
            prompt=prompt,
            model=model,
            temperature=self._default_temperature,
            max_tokens=3072
        )

        # Parse response
        return self._response_parser.parse_quality_response(
            response=result.llm_response.content,
            model=model
        )

    # ========================================================================
    # COMPLEXITY ESTIMATION
    # ========================================================================

    @wrap_exception(LLMError, "Complexity estimation failed")
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

        Raises:
            LLMError: If query or parsing fails
        """
        # Guard clause: empty requirements
        if not requirements or not requirements.strip():
            raise ValueError("Requirements cannot be empty")

        # Build prompt
        prompt = self._prompt_builder.build_complexity_prompt(
            requirements=requirements,
            context=context
        )

        # Query AI service
        result = self.ai_service.query(
            prompt=prompt,
            model=model,
            temperature=self._default_temperature,
            max_tokens=self._default_max_tokens
        )

        # Parse response
        estimate = self._response_parser.parse_complexity_response(
            response=result.llm_response.content
        )

        # Convert to tuple format for backward compatibility
        details = {
            'reasoning': estimate.reasoning,
            'breakdown': estimate.breakdown,
            'parallelization_potential': estimate.parallelization_potential,
            'suggested_workers': estimate.suggested_workers
        }

        return (estimate.complexity_level, estimate.story_points, details)

    # ========================================================================
    # BATCH QUERIES
    # ========================================================================

    @wrap_exception(LLMError, "Batch query failed")
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

        Raises:
            LLMError: If query or parsing fails
        """
        # Guard clause: empty samples
        if not code_samples:
            raise ValueError("code_samples cannot be empty")

        # Build prompt
        prompt = self._prompt_builder.build_batch_confidence_prompt(
            code_samples=code_samples
        )

        # Query AI service with token limit scaled by number of samples
        result = self.ai_service.query(
            prompt=prompt,
            model=model,
            temperature=self._default_temperature,
            max_tokens=4096 * len(code_samples)
        )

        # Parse response
        return self._response_parser.parse_batch_confidence_response(
            response=result.llm_response.content,
            model=model
        )

    # ========================================================================
    # CONFIGURATION
    # ========================================================================

    def set_default_temperature(self, temperature: float) -> None:
        """
        Set default temperature for queries.

        Args:
            temperature: Temperature value (0.0-1.0)

        Raises:
            ValueError: If temperature is out of range
        """
        if not 0.0 <= temperature <= 1.0:
            raise ValueError(f"Temperature must be between 0.0 and 1.0, got {temperature}")
        self._default_temperature = temperature

    def set_default_max_tokens(self, max_tokens: int) -> None:
        """
        Set default max tokens for queries.

        Args:
            max_tokens: Maximum tokens for response

        Raises:
            ValueError: If max_tokens is invalid
        """
        if max_tokens <= 0:
            raise ValueError(f"max_tokens must be positive, got {max_tokens}")
        self._default_max_tokens = max_tokens
