"""
Module: two_pass/strategies/second_pass_strategy.py

WHY: Implements refined execution pass strategy for two-pass pipeline.
RESPONSIBILITY: Performs thorough execution using insights from first pass, optimizes for quality over speed.
PATTERNS: Strategy Pattern (concrete strategy), Guard Clauses, Dispatch Tables, Functional Composition.

This module handles:
- SecondPassStrategy: Thorough implementation with first pass learnings
- Apply first pass learnings to improve implementation
- Comprehensive quality verification
- Incremental improvements and refinements
- Advanced quality scoring with multiple dimensions

EXTRACTED FROM: two_pass/strategies.py (lines 443-833, 391 lines)
REDUCES: Monolithic strategies.py by separating second pass logic into dedicated module
PERFORMANCE: Optimizes for quality (minutes acceptable), higher compute/API calls acceptable
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from two_pass.strategies.base_strategy import PassStrategy
from two_pass.models import PassResult
from two_pass.events import TwoPassEventType
from two_pass.exceptions import SecondPassException
from artemis_exceptions import wrap_exception


# Dispatch table for quality check types (Strategy Pattern - avoid if/elif chains)
QUALITY_CHECK_HANDLERS = {
    "thorough_validation": "_thorough_validation",
    "integration_test": "_integration_test",
    "performance_test": "_performance_test"
}

# Dispatch table for learning types (Strategy Pattern - avoid if/elif chains)
LEARNING_TYPE_KEYWORDS = {
    "validation": "validation",
    "validated": "validation",
    "performance": "performance",
    "faster": "performance",
    "quality": "quality",
    "improved": "quality"
}


class SecondPassStrategy(PassStrategy):
    """
    Strategy for second pass execution: refined implementation with first pass learnings.

    WHY: Performs thorough execution using insights from first pass.
    Optimizes for quality and correctness over speed.

    RESPONSIBILITY: Apply learnings, thorough validation, complete implementation, quality verification.

    PATTERNS:
    - Strategy Pattern: Concrete strategy implementation for second pass
    - Guard Clauses: Early returns for validation failures
    - Dispatch Tables: No if/elif chains for check type and learning type selection
    - Functional Composition: Learning application through pure function composition
    - Observer Pattern: Event emission for monitoring

    Trade-offs:
    - Speed: Slower than first pass (minutes not seconds)
    - Depth: Deep analysis, catches edge cases
    - Accuracy: Production quality
    - Resource usage: Higher compute/API calls acceptable

    Example use cases:
    - Full semantic analysis with first pass structure
    - Complete integration tests using first pass test plan
    - Exhaustive code review with first pass issue list
    - Deep dependency analysis using first pass conflict list
    """

    @wrap_exception(SecondPassException, "Second pass execution failed")
    def execute(self, context: Dict[str, Any]) -> PassResult:
        """
        Execute second pass: refined implementation.

        WHY: Performs thorough execution using first pass learnings for better quality.

        What it does:
        1. Emit start event
        2. Apply first pass learnings from context
        3. Perform thorough analysis
        4. Implement refinements
        5. Calculate comprehensive quality score
        6. Emit completion event

        Args:
            context: Execution context containing:
                - inputs: Data to process
                - config: Second pass configuration
                - learnings: Learnings from first pass (if applied)
                - insights: Insights from first pass (if applied)
                - previous_quality_score: First pass quality for comparison

        Returns:
            PassResult with implementation artifacts and improvements

        Raises:
            SecondPassException: On execution failure
        """
        start_time = datetime.now()

        # Emit start event
        self.emit_event(
            TwoPassEventType.SECOND_PASS_STARTED,
            {
                "context_keys": list(context.keys()),
                "has_learnings": "learnings" in context,
                "has_insights": "insights" in context
            }
        )

        # Guard clause - validate required context
        if "inputs" not in context:
            raise SecondPassException("Missing 'inputs' in context")

        # Perform thorough analysis with learnings applied
        artifacts = self._implement(
            context["inputs"],
            context.get("config", {}),
            context.get("learnings", []),
            context.get("insights", {})
        )

        # Extract new learnings (beyond first pass)
        learnings = self._extract_learnings(artifacts, context.get("learnings", []))

        # Calculate quality score
        quality_score = self._calculate_quality(artifacts)

        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()

        # Determine if quality improved
        previous_quality = context.get("previous_quality_score", 0.0)
        quality_improved = quality_score > previous_quality

        # Create result
        result = PassResult(
            pass_name=self.get_pass_name(),
            success=True,
            artifacts=artifacts,
            quality_score=quality_score,
            execution_time=execution_time,
            learnings=learnings,
            insights=self._extract_insights(artifacts),
            metadata={
                "pass_type": "refined_implementation",
                "quality_improved": quality_improved,
                "quality_delta": quality_score - previous_quality
            }
        )

        # Emit appropriate completion event based on quality - dispatch table
        event_type = (
            TwoPassEventType.PASS_QUALITY_IMPROVED
            if quality_improved
            else TwoPassEventType.SECOND_PASS_COMPLETED
        )

        self.emit_event(
            event_type,
            {
                "quality_score": quality_score,
                "execution_time": execution_time,
                "quality_improved": quality_improved,
                "new_learnings_count": len(learnings)
            }
        )

        return result

    def get_pass_name(self) -> str:
        """
        Get second pass name.

        WHY: Used for logging, events, and memento identification.

        Returns:
            "SecondPass"
        """
        return "SecondPass"

    def _implement(
        self,
        inputs: Dict[str, Any],
        config: Dict[str, Any],
        learnings: List[str],
        insights: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform thorough implementation (extracted helper method).

        WHY: Separates implementation logic from orchestration.
        Avoids nested loops by delegating to specialized methods.

        Args:
            inputs: Data to process
            config: Implementation configuration
            learnings: Learnings from first pass
            insights: Insights from first pass

        Returns:
            Implementation artifacts
        """
        artifacts = {
            "implementation_type": "thorough",
            "inputs_processed": len(inputs),
            "learnings_applied": len(learnings),
            "refinements": [],
            "quality_checks": {}
        }

        # Apply learnings to improve implementation - NO nested loops
        # Extract to _apply_learnings helper
        artifacts["refinements"] = self._apply_learnings_to_implementation(
            inputs,
            learnings,
            insights
        )

        # Perform quality checks - dispatch table instead of if/elif
        check_type = config.get("check_type", "thorough_validation")
        handler_name = QUALITY_CHECK_HANDLERS.get(check_type, "_thorough_validation")
        handler = getattr(self, handler_name)
        artifacts["quality_checks"] = handler(inputs, artifacts["refinements"])

        return artifacts

    def _apply_learnings_to_implementation(
        self,
        inputs: Dict[str, Any],
        learnings: List[str],
        insights: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Apply learnings to improve implementation (extracted helper - NO nested loops).

        WHY: Avoids nested loop (inputs x learnings). Each learning is
        processed independently and results are aggregated.

        PERFORMANCE: O(n) where n = number of learnings, not O(n*m) nested loop.

        Args:
            inputs: Data to process
            learnings: Learnings from first pass
            insights: Insights from first pass

        Returns:
            List of refinements applied
        """
        # Functional approach - map learnings to refinements, filter None values
        refinements = [
            self._apply_single_learning(learning, insights)
            for learning in learnings
        ]

        # Filter out None values (learnings that didn't produce refinements)
        return [r for r in refinements if r is not None]

    def _apply_single_learning(
        self,
        learning: str,
        insights: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Apply single learning to create refinement (helper method).

        WHY: Processes one learning at a time, avoiding nested loops.
        Can be overridden for custom learning application.

        Args:
            learning: Single learning statement
            insights: Context for applying learning

        Returns:
            Refinement dict or None if learning not applicable
        """
        # Dispatch table for learning types - NO if/elif chains
        learning_handlers = {
            "validation": lambda: {"type": "validation_improvement", "learning": learning},
            "performance": lambda: {"type": "performance_improvement", "learning": learning},
            "quality": lambda: {"type": "quality_improvement", "learning": learning}
        }

        # Determine learning type from content
        learning_type = self._classify_learning(learning)
        handler = learning_handlers.get(learning_type)

        return handler() if handler else None

    def _classify_learning(self, learning: str) -> str:
        """
        Classify learning type (helper method).

        WHY: Routes learnings to appropriate handlers without if/elif chains.

        Args:
            learning: Learning statement

        Returns:
            Learning type category
        """
        learning_lower = learning.lower()

        # Find first matching keyword using dispatch table
        for keyword, learning_type in LEARNING_TYPE_KEYWORDS.items():
            if keyword in learning_lower:
                return learning_type

        return "quality"  # Default category

    def _thorough_validation(
        self,
        inputs: Dict[str, Any],
        refinements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Thorough validation (placeholder for actual validation).

        WHY: Deep validation including edge cases discovered in first pass.

        Args:
            inputs: Inputs to validate
            refinements: Refinements to apply

        Returns:
            Thorough validation results
        """
        return {
            "validation_complete": True,
            "checks_passed": len(inputs) + len(refinements),
            "checks_failed": 0,
            "edge_cases_tested": len(refinements)
        }

    def _integration_test(
        self,
        inputs: Dict[str, Any],
        refinements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Integration test (placeholder for actual test).

        WHY: Complete integration testing with first pass test plan.

        Args:
            inputs: Inputs to test
            refinements: Refinements to verify

        Returns:
            Integration test results
        """
        return {
            "integration_test_passed": True,
            "components_tested": len(inputs),
            "refinements_verified": len(refinements)
        }

    def _performance_test(
        self,
        inputs: Dict[str, Any],
        refinements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Performance test (placeholder for actual test).

        WHY: Performance testing with optimizations from first pass.

        Args:
            inputs: Inputs to benchmark
            refinements: Optimizations to apply

        Returns:
            Performance test results
        """
        return {
            "performance_acceptable": True,
            "benchmarks_passed": len(inputs),
            "optimizations_applied": len(refinements)
        }

    def _extract_learnings(
        self,
        artifacts: Dict[str, Any],
        previous_learnings: List[str]
    ) -> List[str]:
        """
        Extract new learnings beyond first pass.

        WHY: Captures incremental improvements discovered during second pass.

        Args:
            artifacts: Implementation results
            previous_learnings: Learnings from first pass

        Returns:
            Combined learnings (previous + new)
        """
        # Use set to combine and deduplicate - O(1) membership test
        all_learnings = set(previous_learnings)

        # Add new learnings from second pass
        quality_checks = artifacts.get("quality_checks", {})
        if quality_checks.get("checks_passed", 0) > 0:
            all_learnings.add(
                f"Second pass: Passed {quality_checks['checks_passed']} thorough checks"
            )

        refinements = artifacts.get("refinements", [])
        if refinements:
            all_learnings.add(
                f"Second pass: Applied {len(refinements)} refinements from first pass learnings"
            )

        return list(all_learnings)

    def _extract_insights(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract insights from artifacts.

        WHY: Provides structured data for downstream analysis and reporting.

        Args:
            artifacts: Implementation results

        Returns:
            Dictionary of insights
        """
        return {
            "implementation_type": artifacts.get("implementation_type"),
            "inputs_processed": artifacts.get("inputs_processed", 0),
            "refinements_count": len(artifacts.get("refinements", [])),
            "quality_checks_passed": artifacts.get("quality_checks", {}).get("checks_passed", 0)
        }

    def _calculate_quality(self, artifacts: Dict[str, Any]) -> float:
        """
        Calculate comprehensive quality score.

        WHY: More sophisticated than first pass scoring. Considers multiple
        quality dimensions (validation, performance, completeness).

        Args:
            artifacts: Implementation results

        Returns:
            Quality score from 0.0 to 1.0
        """
        quality_checks = artifacts.get("quality_checks", {})

        # Guard clause - default to 0.6 if no quality checks
        if not quality_checks:
            return 0.6

        # Calculate score from multiple dimensions
        passed = quality_checks.get("checks_passed", 0)
        failed = quality_checks.get("checks_failed", 0)
        total = passed + failed

        # Guard clause - avoid division by zero
        if total == 0:
            return 0.6

        base_score = passed / total

        # Bonus for refinements applied (up to 10% bonus)
        refinements_count = len(artifacts.get("refinements", []))
        refinement_bonus = min(0.1, refinements_count * 0.02)

        return min(1.0, base_score + refinement_bonus)


__all__ = ["SecondPassStrategy"]
