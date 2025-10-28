"""
Module: two_pass/strategies/first_pass_strategy.py

WHY: Implements fast analysis pass strategy for two-pass pipeline.
RESPONSIBILITY: Provides rapid feedback, identifies obvious issues, creates execution plan for second pass.
PATTERNS: Strategy Pattern (concrete strategy), Guard Clauses, Dispatch Tables, Observer Pattern.

This module handles:
- FirstPassStrategy: Fast analysis and planning implementation
- Quick validation of inputs and requirements
- High-level analysis and planning
- Baseline quality metrics calculation
- Learning extraction for second pass

EXTRACTED FROM: two_pass/strategies.py (lines 194-441, 248 lines)
REDUCES: Monolithic strategies.py by separating first pass logic into dedicated module
PERFORMANCE: Optimizes for speed (seconds not minutes), minimal compute/API calls
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from two_pass.strategies.base_strategy import PassStrategy
from two_pass.models import PassResult
from two_pass.events import TwoPassEventType
from two_pass.exceptions import FirstPassException
from artemis_exceptions import wrap_exception


# Dispatch table for analysis types (Strategy Pattern - avoid if/elif chains)
ANALYSIS_TYPE_HANDLERS = {
    "validation": "_validate_inputs",
    "schema_check": "_check_schema",
    "dependency_scan": "_scan_dependencies"
}


class FirstPassStrategy(PassStrategy):
    """
    Strategy for first pass execution: fast analysis and planning.

    WHY: Provides rapid feedback on feasibility, identifies obvious issues,
    and creates execution plan for second pass. Optimizes for speed over thoroughness.

    RESPONSIBILITY: Fast validation, high-level analysis, baseline quality metrics.

    PATTERNS:
    - Strategy Pattern: Concrete strategy implementation for first pass
    - Guard Clauses: Early returns for validation failures
    - Dispatch Tables: No if/elif chains for analysis type selection
    - Observer Pattern: Event emission for monitoring

    Trade-offs:
    - Speed: Very fast (seconds not minutes)
    - Depth: Shallow analysis, may miss edge cases
    - Accuracy: Good enough for planning, not production
    - Resource usage: Minimal compute/API calls

    Example use cases:
    - Syntax validation without deep semantic analysis
    - API schema validation without full integration test
    - Quick code scan without exhaustive review
    - Dependency check without version conflict analysis
    """

    @wrap_exception(FirstPassException, "First pass execution failed")
    def execute(self, context: Dict[str, Any]) -> PassResult:
        """
        Execute first pass: fast analysis and planning.

        WHY: Provides rapid feedback and creates baseline for second pass.

        What it does:
        1. Emit start event for monitoring
        2. Validate inputs (guard clauses for early failure)
        3. Perform quick analysis
        4. Extract learnings and insights
        5. Calculate preliminary quality score
        6. Emit completion event

        Args:
            context: Execution context containing:
                - inputs: Data to analyze
                - config: First pass configuration
                - validators: Optional validation functions
                - analyzers: Optional analysis functions

        Returns:
            PassResult with analysis artifacts and learnings

        Raises:
            FirstPassException: On validation or analysis failure

        Design notes:
        - Uses guard clauses instead of nested ifs
        - Extracts analysis to _analyze() helper to avoid nested loops
        - Emits events at key points for observability
        """
        start_time = datetime.now()

        # Emit start event
        self.emit_event(
            TwoPassEventType.FIRST_PASS_STARTED,
            {"context_keys": list(context.keys())}
        )

        # Guard clause - validate required context
        if "inputs" not in context:
            raise FirstPassException("Missing 'inputs' in context")

        # Perform fast analysis - extracted to helper method
        artifacts = self._analyze(context["inputs"], context.get("config", {}))

        # Extract learnings from analysis
        learnings = self._extract_learnings(artifacts)

        # Calculate quality score
        quality_score = self._calculate_quality(artifacts)

        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()

        # Create result
        result = PassResult(
            pass_name=self.get_pass_name(),
            success=True,
            artifacts=artifacts,
            quality_score=quality_score,
            execution_time=execution_time,
            learnings=learnings,
            insights=self._extract_insights(artifacts),
            metadata={"pass_type": "fast_analysis"}
        )

        # Emit completion event
        self.emit_event(
            TwoPassEventType.FIRST_PASS_COMPLETED,
            {
                "quality_score": quality_score,
                "execution_time": execution_time,
                "learnings_count": len(learnings)
            }
        )

        return result

    def get_pass_name(self) -> str:
        """
        Get first pass name.

        WHY: Used for logging, events, and memento identification.

        Returns:
            "FirstPass"
        """
        return "FirstPass"

    def _analyze(self, inputs: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform fast analysis on inputs (extracted helper method).

        WHY: Avoids nesting analysis loop inside execute(). Follows
        Single Responsibility Principle - execute orchestrates, _analyze analyzes.

        Args:
            inputs: Data to analyze
            config: Analysis configuration

        Returns:
            Analysis artifacts

        Design note: Uses dispatch table instead of if/elif chain for extensibility
        """
        artifacts = {
            "analysis_type": "fast",
            "inputs_analyzed": len(inputs),
            "validation_results": {},
            "quick_checks": []
        }

        # Dispatch table for analysis types - NO elif chains
        analysis_type = config.get("analysis_type", "validation")
        handler_name = ANALYSIS_TYPE_HANDLERS.get(analysis_type, "_validate_inputs")
        handler = getattr(self, handler_name)
        artifacts["validation_results"] = handler(inputs)

        return artifacts

    def _validate_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate inputs (placeholder for actual validation).

        WHY: Basic input validation for first pass baseline.

        Args:
            inputs: Inputs to validate

        Returns:
            Validation results with pass/fail counts
        """
        return {
            "valid": True,
            "checks_passed": len(inputs),
            "checks_failed": 0
        }

    def _check_schema(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check schema (placeholder for actual schema validation).

        WHY: Quick schema validation without deep semantic checks.

        Args:
            inputs: Inputs to validate schema

        Returns:
            Schema validation results
        """
        return {
            "schema_valid": True,
            "fields_validated": len(inputs)
        }

    def _scan_dependencies(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scan dependencies (placeholder for actual dependency scan).

        WHY: Quick dependency check without version conflict analysis.

        Args:
            inputs: Inputs to scan for dependencies

        Returns:
            Dependency scan results
        """
        return {
            "dependencies_found": 0,
            "conflicts_detected": 0
        }

    def _extract_learnings(self, artifacts: Dict[str, Any]) -> List[str]:
        """
        Extract learnings from analysis artifacts.

        WHY: Captures insights from first pass to guide second pass.
        Learnings are actionable observations that improve second pass execution.

        Args:
            artifacts: Analysis results

        Returns:
            List of learning statements
        """
        learnings = []

        # Extract validation learnings
        validation = artifacts.get("validation_results", {})
        if validation.get("checks_passed", 0) > 0:
            learnings.append(f"Validated {validation['checks_passed']} inputs successfully")

        if validation.get("checks_failed", 0) > 0:
            learnings.append(f"Found {validation['checks_failed']} validation failures to address")

        return learnings

    def _extract_insights(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract insights from artifacts.

        WHY: Insights are structured data (not strings) that second pass
        can use programmatically. Unlike learnings (human-readable), insights are
        machine-readable.

        Args:
            artifacts: Analysis results

        Returns:
            Dictionary of insights
        """
        return {
            "analysis_type": artifacts.get("analysis_type"),
            "inputs_count": artifacts.get("inputs_analyzed", 0),
            "validation_passed": artifacts.get("validation_results", {}).get("valid", False)
        }

    def _calculate_quality(self, artifacts: Dict[str, Any]) -> float:
        """
        Calculate quality score from artifacts.

        WHY: Provides baseline for comparison with second pass.
        Quality score drives rollback decisions.

        Args:
            artifacts: Analysis results

        Returns:
            Quality score from 0.0 to 1.0

        Design note: Uses simple heuristic for first pass. Second pass uses
        more sophisticated quality calculation.
        """
        validation = artifacts.get("validation_results", {})

        # Guard clause - default to 0.5 if no validation results
        if not validation:
            return 0.5

        passed = validation.get("checks_passed", 0)
        failed = validation.get("checks_failed", 0)
        total = passed + failed

        # Guard clause - avoid division by zero
        if total == 0:
            return 0.5

        return passed / total


__all__ = ["FirstPassStrategy"]
