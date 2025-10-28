#!/usr/bin/env python3
"""
Advanced Features Prompt Builder

WHY: Centralizes prompt construction for AI queries. Separates prompt
engineering from query logic to enable easy prompt refinement without
changing core functionality.

RESPONSIBILITY:
- Build structured prompts for confidence estimation
- Build structured prompts for risk assessment
- Build structured prompts for quality evaluation
- Build structured prompts for complexity estimation
- Support batch and single-item queries

PATTERNS:
- Builder Pattern: Constructs complex prompts step-by-step
- Template Method: Common structure, specific variations
- Strategy Pattern: Different prompt strategies via dispatch table
- Single Responsibility: Only handles prompt construction

USAGE:
    from advanced_features.prompt_builder import PromptBuilder

    builder = PromptBuilder()
    prompt = builder.build_confidence_prompt(
        code="def hello()...",
        context="uncertainty analysis",
        requirements="Must greet user"
    )
"""

from typing import Optional, List, Dict, Callable


class PromptBuilder:
    """
    Builds structured prompts for advanced AI features.

    WHY: Prompt engineering should be separate from query logic.
    This allows prompt refinement without touching core functionality.
    """

    def __init__(self):
        """Initialize prompt builder with dispatch table"""
        self._prompt_builders: Dict[str, Callable] = {
            'confidence': self.build_confidence_prompt,
            'risk': self.build_risk_prompt,
            'quality': self.build_quality_prompt,
            'complexity': self.build_complexity_prompt,
            'batch_confidence': self.build_batch_confidence_prompt
        }

    def build_prompt(self, prompt_type: str, **kwargs) -> str:
        """
        Build prompt using dispatch table.

        WHY: Dispatch table eliminates elif chains and makes adding
        new prompt types straightforward.

        Args:
            prompt_type: Type of prompt to build
            **kwargs: Arguments for specific prompt builder

        Returns:
            Constructed prompt string

        Raises:
            ValueError: If prompt type is not supported
        """
        builder = self._prompt_builders.get(prompt_type)
        if not builder:
            raise ValueError(f"Unknown prompt type: {prompt_type}")

        return builder(**kwargs)

    def build_confidence_prompt(
        self,
        code: str,
        context: str = "",
        requirements: Optional[str] = None
    ) -> str:
        """
        Build prompt for confidence estimation.

        WHY: Thermodynamic Computing needs confidence scores to quantify
        uncertainty in generated code.

        Args:
            code: Code to evaluate
            context: Additional context for evaluation
            requirements: Original requirements for comparison

        Returns:
            Structured prompt for confidence estimation
        """
        context_section = context if context else "General code quality assessment"
        requirements_section = requirements if requirements else "No specific requirements provided"

        return f"""# Task: Estimate Confidence in Code Implementation

## Context
{context_section}

## Requirements
{requirements_section}

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

    def build_risk_prompt(
        self,
        code: str,
        context: str = ""
    ) -> str:
        """
        Build prompt for risk assessment.

        WHY: All advanced features need risk assessment for decision-making.

        Args:
            code: Code to assess
            context: Additional context

        Returns:
            Structured prompt for risk assessment
        """
        return f"""# Task: Assess Risks in Code

## Context
{context if context else "General risk assessment"}

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

    def build_quality_prompt(
        self,
        code: str,
        requirements: str = "",
        previous_version: Optional[str] = None
    ) -> str:
        """
        Build prompt for quality evaluation.

        WHY: Two-Pass Pipeline needs quality comparison between passes.

        Args:
            code: Code to evaluate
            requirements: Requirements to check against
            previous_version: Previous version for comparison

        Returns:
            Structured prompt for quality evaluation
        """
        # Build comparison section if previous version exists
        comparison_section = ""
        if previous_version:
            comparison_section = f"""
## Previous Version
```
{previous_version}
```

Compare the current version to the previous version and note improvements or regressions.
"""

        return f"""# Task: Evaluate Code Quality

## Requirements
{requirements if requirements else "No specific requirements provided"}

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

    def build_complexity_prompt(
        self,
        requirements: str,
        context: str = ""
    ) -> str:
        """
        Build prompt for complexity estimation.

        WHY: Dynamic Pipeline needs complexity to configure parallelization.

        Args:
            requirements: Requirements to estimate
            context: Additional context

        Returns:
            Structured prompt for complexity estimation
        """
        return f"""# Task: Estimate Task Complexity

## Requirements
{requirements}

## Context
{context if context else "General complexity assessment"}

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

    def build_batch_confidence_prompt(
        self,
        code_samples: List[Dict[str, str]]
    ) -> str:
        """
        Build prompt for batch confidence estimation.

        WHY: Thermodynamic Computing may need to evaluate multiple code
        paths simultaneously for Monte Carlo simulations.

        Args:
            code_samples: List of dicts with 'code' and 'context' keys

        Returns:
            Structured prompt for batch confidence estimation
        """
        # Guard clause: empty samples
        if not code_samples:
            raise ValueError("code_samples cannot be empty")

        # Build samples section
        samples_text = "\n\n".join([
            f"## Sample {i+1}\n**Context**: {s.get('context', 'N/A')}\n```\n{s['code']}\n```"
            for i, s in enumerate(code_samples)
        ])

        return f"""# Task: Batch Confidence Estimation

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

    def get_available_prompt_types(self) -> List[str]:
        """Get list of available prompt types"""
        return list(self._prompt_builders.keys())
