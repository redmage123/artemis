#!/usr/bin/env python3
"""
WHY: Handle WCAG accessibility evaluation logic
RESPONSIBILITY: Evaluate implementations for WCAG 2.1 AA compliance
PATTERNS: Facade pattern for WCAG evaluation, Guard clauses

This module handles accessibility evaluation by delegating to the WCAGEvaluator
and integrating with the Knowledge Graph for pattern retrieval.
"""

from typing import Dict, Optional, Any
from wcag_evaluator import WCAGEvaluator
from artemis_exceptions import WCAGEvaluationError, wrap_exception

# Import AIQueryService for KG-First accessibility pattern retrieval
try:
    from ai_query_service import QueryType
    AI_QUERY_SERVICE_AVAILABLE = True
except ImportError:
    AI_QUERY_SERVICE_AVAILABLE = False


class AccessibilityEvaluator:
    """
    WHY: Encapsulate WCAG accessibility evaluation logic
    RESPONSIBILITY: Perform WCAG checks and retrieve accessibility patterns
    PATTERNS: Facade pattern, Dependency injection

    Benefits:
    - Isolates WCAG evaluation logic
    - Integrates KG pattern retrieval
    - Clean error handling
    - Testable
    """

    def __init__(
        self,
        logger: Any,
        ai_service: Optional[Any] = None
    ):
        """
        WHY: Initialize with dependencies
        RESPONSIBILITY: Set up logger and AI service

        Args:
            logger: Logger interface
            ai_service: Optional AI Query Service for KG patterns
        """
        self.logger = logger
        self.ai_service = ai_service

    def query_accessibility_patterns(self, task_title: str) -> Optional[Dict]:
        """
        WHY: Query KG for similar UI/UX implementations and accessibility patterns
        RESPONSIBILITY: Retrieve proven patterns from Knowledge Graph
        PATTERNS: KG-First approach for pattern retrieval

        Uses AIQueryService for KG-First approach to find proven patterns.

        Args:
            task_title: Title of the task

        Returns:
            Dict with patterns found, or None if unavailable
        """
        # Guard clause: no AI service available
        if not self.ai_service:
            return None

        # Guard clause: AI service not available at import time
        if not AI_QUERY_SERVICE_AVAILABLE:
            return None

        try:
            result = self.ai_service.query(
                query_type=QueryType.UIUX_EVALUATION,
                prompt="",  # Not calling LLM, just getting KG patterns
                kg_query_params={
                    'task_title': task_title,
                    'file_types': ['html', 'css', 'javascript', 'typescript']
                },
                skip_llm_call=True  # Only get KG patterns
            )

            if result.kg_context and result.kg_context.pattern_count > 0:
                return {
                    'patterns_found': result.kg_context.patterns_found,
                    'pattern_count': result.kg_context.pattern_count,
                    'estimated_token_savings': result.kg_context.estimated_token_savings
                }
        except Exception as e:
            self.logger.log(f"⚠️  Could not query accessibility patterns: {e}", "WARNING")

        return None

    def evaluate_accessibility(
        self,
        developer_name: str,
        implementation_dir: str
    ) -> Dict:
        """
        WHY: Run WCAG 2.1 AA accessibility evaluation
        RESPONSIBILITY: Execute accessibility checks and handle errors
        PATTERNS: Guard clauses for error handling

        Args:
            developer_name: Name of the developer
            implementation_dir: Directory containing implementation

        Returns:
            Dict with WCAG evaluation results

        Raises:
            WCAGEvaluationError: If evaluation fails
        """
        self.logger.log("Running WCAG 2.1 AA accessibility checks...", "INFO")

        try:
            wcag_evaluator = WCAGEvaluator()
            wcag_results = wcag_evaluator.evaluate_directory(implementation_dir)
            return wcag_results

        except Exception as e:
            raise wrap_exception(
                e,
                WCAGEvaluationError,
                f"WCAG evaluation failed for {developer_name}",
                {"developer": developer_name, "implementation_dir": implementation_dir}
            )
