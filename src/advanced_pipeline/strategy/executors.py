#!/usr/bin/env python3
"""
Module: executors.py

WHY this module exists:
    Implements mode-specific execution strategies (standard, dynamic, two-pass,
    adaptive, full) for advanced pipeline.

RESPONSIBILITY:
    - Execute pipeline in different modes
    - Integrate mode-specific features (dynamic selection, two-pass, thermodynamic)
    - Convert between result formats
    - Handle execution errors

PATTERNS:
    - Strategy Pattern for mode-specific execution
    - Adapter Pattern for result format conversion
    - Guard clauses for optional features
"""

from typing import Dict, Any, List, Optional
from artemis_stage_interface import PipelineStage
from artemis_services import PipelineLogger
from advanced_pipeline.pipeline_config import AdvancedPipelineConfig
from advanced_pipeline.strategy.confidence_quantifier import ConfidenceQuantifier
from advanced_pipeline.strategy.complexity_analyzer import ComplexityAnalyzer
from pipeline_observer import PipelineObservable
from dynamic_pipeline import DynamicPipelineBuilder, ComplexityBasedSelector
from two_pass_pipeline import TwoPassPipelineFactory
from thermodynamic_computing import check_confidence_threshold, assess_risk


class StandardExecutor:
    """
    Executes standard sequential pipeline.

    WHY: Fallback mode for simple tasks or when advanced features disabled.
    Minimal overhead, proven reliability.

    RESPONSIBILITY: Sequential stage execution with optional uncertainty tracking

    PATTERNS: Sequential execution, Guard clauses
    """

    def __init__(
        self,
        confidence_quantifier: Optional[ConfidenceQuantifier] = None,
        verbose: bool = False
    ):
        """
        Initialize standard executor.

        Args:
            confidence_quantifier: Optional confidence quantifier
            verbose: Enable detailed logging
        """
        self.confidence_quantifier = confidence_quantifier
        self.logger = PipelineLogger(verbose=verbose)

    def execute(
        self,
        stages: List[PipelineStage],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute standard sequential pipeline.

        Args:
            stages: Pipeline stages
            context: Execution context

        Returns:
            Execution results
        """
        results = {}

        # Execute stages sequentially
        for stage in stages:
            # Check if should execute
            if not stage.should_execute(context):
                continue

            # Execute stage
            try:
                stage_result = stage.execute(context)
                results[stage.name] = stage_result

                # Add uncertainty tracking if available
                if self.confidence_quantifier:
                    confidence = self.confidence_quantifier.quantify_stage_confidence(
                        stage, stage_result, context
                    )
                    if confidence:
                        stage_result["confidence_score"] = confidence

                # Update context with stage result
                context[f"{stage.name}_result"] = stage_result

            except Exception as e:
                # Stage failed - stop execution
                results[stage.name] = {"status": "failed", "error": str(e)}
                return {
                    "status": "failed",
                    "results": results,
                    "error": f"Stage {stage.name} failed: {e}"
                }

        return {
            "status": "success",
            "results": results
        }


class DynamicExecutor:
    """
    Executes dynamic pipeline with adaptive stage selection.

    WHY: Reduces execution time for simple tasks while maintaining thorough
    validation for complex tasks.

    RESPONSIBILITY: Dynamic stage selection based on complexity

    PATTERNS: Strategy pattern, Builder pattern
    """

    def __init__(
        self,
        config: AdvancedPipelineConfig,
        complexity_analyzer: ComplexityAnalyzer,
        observable: Optional[PipelineObservable] = None,
        verbose: bool = False
    ):
        """
        Initialize dynamic executor.

        Args:
            config: Pipeline configuration
            complexity_analyzer: Complexity analyzer
            observable: Optional observable for events
            verbose: Enable detailed logging
        """
        self.config = config
        self.complexity_analyzer = complexity_analyzer
        self.observable = observable
        self.logger = PipelineLogger(verbose=verbose)

    def execute(
        self,
        stages: List[PipelineStage],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute dynamic pipeline with adaptive stage selection.

        Args:
            stages: Available pipeline stages
            context: Execution context

        Returns:
            Execution results
        """
        # Guard clause: if dynamic disabled, fall back
        if not self.config.enable_dynamic_pipeline:
            return {"status": "failed", "error": "Dynamic pipeline disabled"}

        # Determine complexity
        complexity = self.complexity_analyzer.analyze(context)

        # Build dynamic pipeline with complexity-based selection
        pipeline = (DynamicPipelineBuilder()
            .with_name(f"dynamic-{context.get('card_id', 'unknown')}")
            .add_stages(stages)
            .with_strategy(ComplexityBasedSelector())
            .with_context({"complexity": complexity})
            .with_observable(self.observable)
            .with_parallelism(
                enabled=self.config.parallel_execution_enabled,
                max_workers=self.config.max_parallel_workers
            )
            .build())

        # Execute dynamic pipeline
        card_id = context.get("card_id", "unknown")
        results_dict = pipeline.execute(card_id)

        # Convert StageResult objects to dicts
        results = {
            name: {
                "status": "success" if result.is_success() else "failed",
                "data": result.data,
                "duration": result.duration,
                "skipped": result.skipped,
                "error": str(result.error) if result.error else None
            }
            for name, result in results_dict.items()
        }

        # Check for failures
        failures = [r for r in results_dict.values() if not r.is_success()]

        return {
            "status": "success" if not failures else "failed",
            "results": results,
            "dynamic_stats": {
                "stages_selected": len(results),
                "stages_available": len(stages),
                "complexity": complexity.value
            }
        }


class TwoPassExecutor:
    """
    Executes two-pass pipeline (fast analysis -> refined implementation).

    WHY: Provides fast feedback while still achieving quality. Rollback
    ensures stability when second pass degrades quality.

    RESPONSIBILITY: Two-pass execution with rollback

    PATTERNS: Two-pass pattern, Rollback pattern
    """

    def __init__(
        self,
        config: AdvancedPipelineConfig,
        observable: Optional[PipelineObservable] = None,
        verbose: bool = False
    ):
        """
        Initialize two-pass executor.

        Args:
            config: Pipeline configuration
            observable: Optional observable for events
            verbose: Enable detailed logging
        """
        self.config = config
        self.observable = observable
        self.verbose = verbose

    def execute(
        self,
        stages: List[PipelineStage],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute two-pass pipeline.

        Args:
            stages: Pipeline stages
            context: Execution context

        Returns:
            Execution results with both passes
        """
        # Guard clause: if two-pass disabled, fall back
        if not self.config.enable_two_pass:
            return {"status": "failed", "error": "Two-pass pipeline disabled"}

        # Create two-pass pipeline
        two_pass = TwoPassPipelineFactory.create_default_pipeline(
            observable=self.observable,
            verbose=self.verbose
        )

        # Configure rollback behavior
        two_pass.auto_rollback = self.config.two_pass_auto_rollback
        two_pass.rollback_threshold = self.config.rollback_degradation_threshold

        # Adapt context to two-pass format
        two_pass_context = {
            "inputs": context,
            "config": {"stages": stages}
        }

        final_result = two_pass.execute(two_pass_context)

        # Convert PassResult to standard result format
        return {
            "status": "success" if final_result.success else "failed",
            "results": final_result.artifacts,
            "two_pass_stats": {
                "pass_name": final_result.pass_name,
                "quality_score": final_result.quality_score,
                "execution_time": final_result.execution_time,
                "learnings": final_result.learnings
            }
        }


class AdaptiveExecutor:
    """
    Executes with thermodynamic uncertainty quantification.

    WHY: Quantifies confidence in predictions, enabling risk-aware execution.

    RESPONSIBILITY: Standard execution with uncertainty tracking

    PATTERNS: Decorator pattern (adds uncertainty to standard execution)
    """

    def __init__(
        self,
        config: AdvancedPipelineConfig,
        confidence_quantifier: ConfidenceQuantifier,
        observable: Optional[PipelineObservable] = None,
        verbose: bool = False
    ):
        """
        Initialize adaptive executor.

        Args:
            config: Pipeline configuration
            confidence_quantifier: Confidence quantifier
            observable: Optional observable for events
            verbose: Enable detailed logging
        """
        self.config = config
        self.confidence_quantifier = confidence_quantifier
        self.observable = observable
        self.logger = PipelineLogger(verbose=verbose)

    def execute(
        self,
        stages: List[PipelineStage],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute with thermodynamic uncertainty quantification.

        Args:
            stages: Pipeline stages
            context: Execution context

        Returns:
            Execution results with confidence scores
        """
        results = {}

        for stage in stages:
            # Check if should execute
            if not stage.should_execute(context):
                continue

            # Execute stage
            try:
                stage_result = stage.execute(context)

                # Quantify uncertainty
                confidence = self.confidence_quantifier.quantify_stage_confidence(
                    stage, stage_result, context
                )

                # Check confidence threshold
                if confidence and not check_confidence_threshold(
                    confidence,
                    self.config.confidence_threshold,
                    self.observable,
                    context
                ):
                    # Low confidence - emit warning
                    self.logger.log(
                        f"Stage {stage.name} has low confidence "
                        f"({confidence.confidence:.2f} < {self.config.confidence_threshold})",
                        "WARNING"
                    )

                # Assess risk
                risk = assess_risk(confidence, observable=self.observable, context=context) if confidence else "unknown"

                # Store results with uncertainty
                results[stage.name] = {
                    "status": "success",
                    "data": stage_result,
                    "confidence": confidence.to_dict() if confidence else None,
                    "risk": risk
                }

                # Update context
                context[f"{stage.name}_result"] = stage_result

            except Exception as e:
                results[stage.name] = {"status": "failed", "error": str(e)}
                return {
                    "status": "failed",
                    "results": results,
                    "error": f"Stage {stage.name} failed: {e}"
                }

        return {
            "status": "success",
            "results": results
        }


class FullExecutor:
    """
    Executes with all advanced features enabled.

    WHY: Complex, high-risk tasks benefit from all advanced features.

    RESPONSIBILITY: Orchestrate all advanced features

    PATTERNS: Composite pattern (combines multiple features)
    """

    def __init__(
        self,
        config: AdvancedPipelineConfig,
        complexity_analyzer: ComplexityAnalyzer,
        confidence_quantifier: ConfidenceQuantifier,
        observable: Optional[PipelineObservable] = None,
        verbose: bool = False
    ):
        """
        Initialize full executor.

        Args:
            config: Pipeline configuration
            complexity_analyzer: Complexity analyzer
            confidence_quantifier: Confidence quantifier
            observable: Optional observable for events
            verbose: Enable detailed logging
        """
        self.config = config
        self.complexity_analyzer = complexity_analyzer
        self.confidence_quantifier = confidence_quantifier
        self.observable = observable
        self.logger = PipelineLogger(verbose=verbose)

    def execute(
        self,
        stages: List[PipelineStage],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute with all advanced features enabled.

        Args:
            stages: Pipeline stages
            context: Execution context

        Returns:
            Execution results with all features
        """
        # Determine complexity
        complexity = self.complexity_analyzer.analyze(context)

        # Build dynamic pipeline
        dynamic_pipeline = (DynamicPipelineBuilder()
            .with_name(f"full-{context.get('card_id', 'unknown')}")
            .add_stages(stages)
            .with_strategy(ComplexityBasedSelector())
            .with_context({"complexity": complexity})
            .with_observable(self.observable)
            .with_parallelism(
                enabled=self.config.parallel_execution_enabled,
                max_workers=self.config.max_parallel_workers
            )
            .build())

        # Execute dynamic pipeline
        card_id = context.get("card_id", "unknown")
        results_dict = dynamic_pipeline.execute(card_id)

        # Add uncertainty tracking to all results
        enhanced_results = {}
        for name, result in results_dict.items():
            confidence = self.confidence_quantifier.quantify_from_result(
                name, result, context
            )

            enhanced_results[name] = {
                "status": "success" if result.is_success() else "failed",
                "data": result.data,
                "duration": result.duration,
                "confidence": confidence.to_dict() if confidence else None,
                "risk": assess_risk(confidence).get("risk_level") if confidence else "unknown"
            }

        return {
            "status": "success" if all(r.is_success() for r in results_dict.values()) else "failed",
            "results": enhanced_results,
            "mode_features": ["dynamic", "thermodynamic"]
        }
