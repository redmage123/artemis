#!/usr/bin/env python3
"""
Advanced Features AI Mixin - DRY AI Query Pattern

Purpose: Provides shared AI query methods for Thermodynamic Computing,
Dynamic Pipeline, and Two-Pass Pipeline features.

Why DRY: All three features need AI calls with similar patterns:
- Confidence estimation
- Code analysis
- Risk assessment
- Quality evaluation

Instead of duplicating AI query logic in each feature, this mixin
provides reusable query methods following the same patterns.

Design Patterns:
- Mixin Pattern: Shared behavior across multiple classes
- Template Method: Common query structure, specific prompt generation
- Strategy Pattern: Different query types via dispatch table
- DRY: Single source of truth for AI interactions

SOLID Principles:
- Single Responsibility: Only handles AI queries for advanced features
- Open/Closed: Extensible via new query methods
- Dependency Inversion: Depends on AIQueryService abstraction

Usage:
    class ThermodynamicComputing(AdvancedFeaturesAIMixin):
        def __init__(self, ai_service, ...):
            self.ai_service = ai_service

        def quantify_uncertainty(self, code):
            # Use mixin method
            return self.query_for_confidence(code, context="uncertainty")
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from abc import ABC

from artemis_exceptions import (
    ArtemisException,
    LLMError,
    wrap_exception
)


# ============================================================================
# DATA CLASSES FOR AI RESPONSES
# ============================================================================

@dataclass
class ConfidenceEstimate:
    """AI-generated confidence estimate for code/decision"""
    score: float  # 0.0-1.0
    reasoning: str
    uncertainty_sources: List[str]
    suggestions: List[str]
    model_used: str


@dataclass
class RiskAssessment:
    """AI-generated risk assessment"""
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    probability: float  # 0.0-1.0
    impact: str
    mitigations: List[str]
    model_used: str


@dataclass
class QualityEvaluation:
    """AI-generated quality evaluation"""
    quality_score: float  # 0.0-1.0
    issues: List[Dict[str, str]]
    strengths: List[str]
    improvement_suggestions: List[str]
    model_used: str


# ============================================================================
# ADVANCED FEATURES AI MIXIN
# ============================================================================

class AdvancedFeaturesAIMixin(ABC):
    """
    Mixin providing DRY AI query methods for advanced features.

    WHY Mixin: All three advanced features need AI queries. This mixin
    prevents code duplication and ensures consistent AI interaction patterns.

    Inheriting classes must have:
        - self.ai_service: Reference to AIQueryService
        - self.logger: Logger instance (optional)

    Provides methods for:
        - Confidence estimation (Thermodynamic Computing)
        - Code quality evaluation (Two-Pass Pipeline)
        - Risk assessment (all features)
        - Complexity estimation (Dynamic Pipeline)
    """

    # ========================================================================
    # CONFIDENCE ESTIMATION (Thermodynamic Computing Primary Use)
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
        """
        prompt = self._build_confidence_prompt(code, context, requirements)

        result = self.ai_service.query(
            prompt=prompt,
            model=model,
            temperature=0.3,  # Low temp for consistent evaluation
            max_tokens=2048
        )

        return self._parse_confidence_response(result.llm_response.content, model)

    def _build_confidence_prompt(
        self,
        code: str,
        context: str,
        requirements: Optional[str]
    ) -> str:
        """
        Build prompt for confidence estimation.

        WHY Template Method: Common structure, specific details vary by context.
        """
        base_prompt = f"""# Task: Estimate Confidence in Code Implementation

## Context
{context if context else "General code quality assessment"}

## Requirements
{requirements if requirements else "No specific requirements provided"}

## Code to Evaluate
```
{code}
```

## Your Task
Provide a confidence estimate (0.0-1.0) for this code with detailed reasoning.

Consider:
1. Correctness: Does it meet requirements?
2. Completeness: Is anything missing?
3. Quality: Is it well-structured and maintainable?
4. Robustness: Does it handle edge cases?

## Output Format (JSON)
{{
    "confidence_score": 0.85,
    "reasoning": "Code correctly implements OAuth2 flow with proper error handling...",
    "uncertainty_sources": [
        "Token refresh logic not fully tested",
        "Edge case handling for expired tokens unclear"
    ],
    "suggestions": [
        "Add unit tests for token refresh",
        "Add timeout handling for API calls"
    ]
}}
"""
        return base_prompt

    def _parse_confidence_response(self, response: str, model: str) -> ConfidenceEstimate:
        """
        Parse AI response into ConfidenceEstimate.

        WHY: Centralized parsing ensures consistent handling across features.
        """
        import json
        import re

        # Extract JSON from response (handles markdown code blocks)
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if not json_match:
            raise LLMError(f"Could not parse confidence response: {response[:200]}")

        try:
            data = json.loads(json_match.group(0))
            return ConfidenceEstimate(
                score=float(data.get('confidence_score', 0.5)),
                reasoning=data.get('reasoning', ''),
                uncertainty_sources=data.get('uncertainty_sources', []),
                suggestions=data.get('suggestions', []),
                model_used=model
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise LLMError(f"Failed to parse confidence estimate: {e}")

    # ========================================================================
    # RISK ASSESSMENT (All Features)
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
        """
        prompt = f"""# Task: Assess Risks in Code

## Context
{context}

## Code to Assess
```
{code}
```

## Your Task
Identify risks in this code and suggest mitigations.

Consider:
1. Security risks (injection, auth, data exposure)
2. Performance risks (scalability, memory, latency)
3. Reliability risks (error handling, edge cases)
4. Integration risks (external dependencies)

## Output Format (JSON)
{{
    "risk_level": "medium",
    "probability": 0.35,
    "impact": "Moderate - could cause auth failures",
    "mitigations": [
        "Add rate limiting",
        "Implement retry logic",
        "Add circuit breaker"
    ]
}}
"""

        result = self.ai_service.query(
            prompt=prompt,
            model=model,
            temperature=0.3,
            max_tokens=2048
        )

        return self._parse_risk_response(result.llm_response.content, model)

    def _parse_risk_response(self, response: str, model: str) -> RiskAssessment:
        """Parse AI response into RiskAssessment"""
        import json
        import re

        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if not json_match:
            raise LLMError(f"Could not parse risk response: {response[:200]}")

        try:
            data = json.loads(json_match.group(0))
            return RiskAssessment(
                risk_level=data.get('risk_level', 'unknown'),
                probability=float(data.get('probability', 0.5)),
                impact=data.get('impact', ''),
                mitigations=data.get('mitigations', []),
                model_used=model
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise LLMError(f"Failed to parse risk assessment: {e}")

    # ========================================================================
    # QUALITY EVALUATION (Two-Pass Pipeline Primary Use)
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
        """
        comparison_section = ""
        if previous_version:
            comparison_section = f"""
## Previous Version
```
{previous_version}
```

Compare the current version to the previous version and note improvements or regressions.
"""

        prompt = f"""# Task: Evaluate Code Quality

## Requirements
{requirements}

## Code to Evaluate
```
{code}
```

{comparison_section}

## Your Task
Evaluate code quality holistically.

Criteria:
1. Correctness (meets requirements)
2. Maintainability (clean, documented)
3. Performance (efficient algorithms)
4. Robustness (error handling)
5. Security (no vulnerabilities)

## Output Format (JSON)
{{
    "quality_score": 0.85,
    "issues": [
        {{"severity": "medium", "description": "Missing error handling for API timeout"}},
        {{"severity": "low", "description": "Magic number should be constant"}}
    ],
    "strengths": [
        "Well-structured OAuth2 flow",
        "Comprehensive token validation"
    ],
    "improvement_suggestions": [
        "Add unit tests for edge cases",
        "Extract configuration to constants"
    ]
}}
"""

        result = self.ai_service.query(
            prompt=prompt,
            model=model,
            temperature=0.3,
            max_tokens=3072
        )

        return self._parse_quality_response(result.llm_response.content, model)

    def _parse_quality_response(self, response: str, model: str) -> QualityEvaluation:
        """Parse AI response into QualityEvaluation"""
        import json
        import re

        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if not json_match:
            raise LLMError(f"Could not parse quality response: {response[:200]}")

        try:
            data = json.loads(json_match.group(0))
            return QualityEvaluation(
                quality_score=float(data.get('quality_score', 0.5)),
                issues=data.get('issues', []),
                strengths=data.get('strengths', []),
                improvement_suggestions=data.get('improvement_suggestions', []),
                model_used=model
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise LLMError(f"Failed to parse quality evaluation: {e}")

    # ========================================================================
    # COMPLEXITY ESTIMATION (Dynamic Pipeline Primary Use)
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
        """
        prompt = f"""# Task: Estimate Task Complexity

## Requirements
{requirements}

## Context
{context}

## Your Task
Estimate the complexity and effort for these requirements.

Consider:
1. Technical complexity (algorithms, integrations)
2. Scope (number of components affected)
3. Unknowns (research needed, new technologies)
4. Dependencies (external APIs, databases)

## Output Format (JSON)
{{
    "complexity": "complex",
    "story_points": 13,
    "reasoning": "OAuth2 integration requires...",
    "breakdown": {{
        "research": 2,
        "design": 3,
        "implementation": 5,
        "testing": 3
    }},
    "parallelization_potential": "high",
    "suggested_workers": 4
}}
"""

        result = self.ai_service.query(
            prompt=prompt,
            model=model,
            temperature=0.3,
            max_tokens=2048
        )

        return self._parse_complexity_response(result.llm_response.content)

    def _parse_complexity_response(self, response: str) -> Tuple[str, int, Dict[str, Any]]:
        """Parse AI response into complexity tuple"""
        import json
        import re

        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if not json_match:
            raise LLMError(f"Could not parse complexity response: {response[:200]}")

        try:
            data = json.loads(json_match.group(0))
            complexity = data.get('complexity', 'medium')
            story_points = int(data.get('story_points', 5))
            details = {
                'reasoning': data.get('reasoning', ''),
                'breakdown': data.get('breakdown', {}),
                'parallelization_potential': data.get('parallelization_potential', 'low'),
                'suggested_workers': int(data.get('suggested_workers', 1))
            }
            return (complexity, story_points, details)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise LLMError(f"Failed to parse complexity estimate: {e}")

    # ========================================================================
    # BATCH QUERIES (Optimization)
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
        """
        # Build batch prompt
        samples_text = "\n\n".join([
            f"## Sample {i+1}\n**Context**: {s.get('context', 'N/A')}\n```\n{s['code']}\n```"
            for i, s in enumerate(code_samples)
        ])

        prompt = f"""# Task: Batch Confidence Estimation

Evaluate confidence for multiple code samples.

{samples_text}

## Output Format (JSON Array)
[
    {{
        "sample_id": 1,
        "confidence_score": 0.85,
        "reasoning": "...",
        "uncertainty_sources": [...],
        "suggestions": [...]
    }},
    ...
]
"""

        result = self.ai_service.query(
            prompt=prompt,
            model=model,
            temperature=0.3,
            max_tokens=4096 * len(code_samples)
        )

        return self._parse_batch_confidence_response(
            result.llm_response.content,
            model
        )

    def _parse_batch_confidence_response(
        self,
        response: str,
        model: str
    ) -> List[ConfidenceEstimate]:
        """Parse batch response into list of ConfidenceEstimate"""
        import json
        import re

        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if not json_match:
            raise LLMError(f"Could not parse batch response: {response[:200]}")

        try:
            data_list = json.loads(json_match.group(0))
            return [
                ConfidenceEstimate(
                    score=float(item.get('confidence_score', 0.5)),
                    reasoning=item.get('reasoning', ''),
                    uncertainty_sources=item.get('uncertainty_sources', []),
                    suggestions=item.get('suggestions', []),
                    model_used=model
                )
                for item in data_list
            ]
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise LLMError(f"Failed to parse batch confidence estimates: {e}")


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

"""
Example 1: Thermodynamic Computing

class ThermodynamicComputing(AdvancedFeaturesAIMixin):
    def __init__(self, ai_service, observable=None):
        self.ai_service = ai_service
        self.logger = logger
        self.observable = observable

    def quantify_uncertainty(self, code, context):
        # Use DRY mixin method
        estimate = self.query_for_confidence(code, context=context)

        # Convert to internal ConfidenceScore
        return ConfidenceScore(
            mean=estimate.score,
            confidence_interval=(estimate.score - 0.1, estimate.score + 0.1),
            sources=estimate.uncertainty_sources
        )


Example 2: Two-Pass Pipeline

class TwoPassPipeline(AdvancedFeaturesAIMixin):
    def __init__(self, ai_service, config):
        self.ai_service = ai_service
        self.logger = logger
        self.config = config

    def should_accept_second_pass(self, first_code, second_code, requirements):
        # Use DRY mixin method for comparison
        second_quality = self.query_for_quality(
            code=second_code,
            requirements=requirements,
            previous_version=first_code
        )

        return second_quality.quality_score > self.config.quality_threshold


Example 3: Dynamic Pipeline

class DynamicPipeline(AdvancedFeaturesAIMixin):
    def __init__(self, ai_service, config):
        self.ai_service = ai_service
        self.logger = logger
        self.config = config

    def configure_parallelization(self, requirements):
        # Use DRY mixin method
        complexity, points, details = self.query_for_complexity(requirements)

        # Configure based on estimate
        self.max_workers = details['suggested_workers']
        self.parallelization_enabled = (
            details['parallelization_potential'] in ['high', 'medium']
        )
"""
