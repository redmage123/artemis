#!/usr/bin/env python3
"""
Architecture Reviewer - Design Quality Analysis

WHY: Evaluate architecture design decisions for quality, scalability, and best practices
RESPONSIBILITY: Review architecture using LLM, score design patterns, security, maintainability
PATTERNS: Single Responsibility, Guard Clauses, Type Safety

This module provides architecture review functionality that assesses:
- Design patterns appropriateness
- Scalability considerations
- Security best practices
- Maintainability and code organization
- Performance implications
"""

import json
from typing import Dict, Any, Optional
from llm_client import LLMClient, LLMMessage


class ArchitectureReviewer:
    """
    Reviews architecture design using LLM analysis

    WHY: Centralize architecture quality assessment logic
    RESPONSIBILITY: Analyze architecture and provide structured feedback
    """

    def __init__(self, llm_client: LLMClient, logger: Any):
        """
        Initialize Architecture Reviewer

        Args:
            llm_client: LLM client for architecture analysis
            logger: Logger interface for diagnostics
        """
        if not llm_client:
            raise ValueError("LLM client is required for architecture review")
        if not logger:
            raise ValueError("Logger is required for architecture review")

        self.llm_client = llm_client
        self.logger = logger

    def review_architecture(self, architecture: Dict[str, Any], task_title: str) -> Dict[str, Any]:
        """
        Review architecture design using LLM

        WHY: Comprehensive architecture assessment using AI

        Args:
            architecture: Architecture design dictionary
            task_title: Title of the task being reviewed

        Returns:
            Dictionary with review scores, feedback, and recommendations
        """
        if not architecture:
            return self._create_empty_review()

        if not task_title:
            task_title = "Unknown Task"

        try:
            prompt = self._build_review_prompt(architecture, task_title)
            review_response = self._query_llm(prompt)
            return self._parse_review_response(review_response)

        except Exception as e:
            return self._create_error_review(e)

    def _create_empty_review(self) -> Dict[str, Any]:
        """Create review for missing architecture"""
        return {
            "status": "SKIPPED",
            "message": "Architecture stage was skipped",
            "score": 70,
            "recommendations": ["Consider adding architecture documentation if project grows in complexity"]
        }

    def _build_review_prompt(self, architecture: Dict[str, Any], task_title: str) -> str:
        """
        Build LLM review prompt

        WHY: Structured prompting for consistent reviews
        """
        arch_description = json.dumps(architecture, indent=2)

        return f"""Review this architecture design for: {task_title}

Architecture:
{arch_description}

Evaluate the following (rate 1-10 and provide feedback):

1. **Design Patterns**: Are appropriate patterns used?
2. **Scalability**: Can it handle growth?
3. **Security**: Are security best practices followed?
4. **Maintainability**: Is code organization clear?
5. **Performance**: Are there obvious bottlenecks?

Respond in JSON:
{{
    "design_patterns": {{"score": 8, "feedback": "Good use of MVC..."}},
    "scalability": {{"score": 6, "feedback": "Database may bottleneck..."}},
    "security": {{"score": 9, "feedback": "Good auth implementation..."}},
    "maintainability": {{"score": 7, "feedback": "Could improve modularity..."}},
    "performance": {{"score": 8, "feedback": "Good caching strategy..."}},
    "overall_recommendation": "APPROVE | REVISE | REJECT",
    "critical_issues": ["Issue 1", "Issue 2"],
    "suggestions": ["Suggestion 1", "Suggestion 2"]
}}
"""

    def _query_llm(self, prompt: str) -> str:
        """
        Query LLM for architecture review

        WHY: Centralize LLM interaction logic
        """
        messages = [
            LLMMessage(role="system", content="You are a senior architect reviewing project designs."),
            LLMMessage(role="user", content=prompt)
        ]

        llm_response = self.llm_client.complete(
            messages=messages,
            response_format={"type": "json_object"}
        )

        return llm_response.content

    def _parse_review_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM review response

        WHY: Safely extract structured review data
        """
        return json.loads(response)

    def _create_error_review(self, error: Exception) -> Dict[str, Any]:
        """
        Create review result for error cases

        WHY: Graceful degradation on failures
        """
        self.logger.log(f"Error reviewing architecture: {error}", "ERROR")

        return {
            "overall_recommendation": "REVISE",
            "critical_issues": [f"Review error: {error}"],
            "suggestions": ["Manual review required"]
        }
