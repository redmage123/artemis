#!/usr/bin/env python3
"""
Module: strategy_facade.py

WHY this module exists:
    Provides unified facade for advanced pipeline strategy execution,
    orchestrating all components (executors, trackers, analyzers).

RESPONSIBILITY:
    - Orchestrate mode selection and execution
    - Coordinate between executors, trackers, and analyzers
    - Provide single entry point for pipeline execution
    - Track performance and emit events

PATTERNS:
    - Facade Pattern: Simplifies complex subsystem interactions
    - Strategy Pattern: Delegates execution based on mode
    - Adapter Pattern: Adapts to PipelineStrategy interface
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from pipeline_observer import PipelineObservable
from artemis_exceptions import PipelineException, wrap_exception
from artemis_services import PipelineLogger
from artemis_stage_interface import PipelineStage
from thermodynamic_computing import ThermodynamicComputing

from advanced_pipeline.pipeline_mode import PipelineMode
from advanced_pipeline.pipeline_config import AdvancedPipelineConfig
from advanced_pipeline.configuration_manager import ConfigurationManager
from advanced_pipeline.mode_selector import ModeSelector

from advanced_pipeline.strategy.executors import (
    StandardExecutor,
    DynamicExecutor,
    TwoPassExecutor,
    AdaptiveExecutor,
    FullExecutor
)
from advanced_pipeline.strategy.performance_tracker import PerformanceTracker
from advanced_pipeline.strategy.event_emitter import EventEmitter
from advanced_pipeline.strategy.complexity_analyzer import ComplexityAnalyzer
from advanced_pipeline.strategy.confidence_quantifier import ConfidenceQuantifier


class AdvancedPipelineStrategyFacade:
    """
    Facade that orchestrates advanced pipeline strategy execution.

    WHY: Simplifies interaction with complex subsystem of executors, trackers,
    and analyzers. Provides single entry point for advanced pipeline features.

    RESPONSIBILITY: Orchestrate all advanced pipeline components

    PATTERNS:
        - Facade: Simplifies subsystem interactions
        - Strategy: Delegates execution based on mode
        - Adapter: Adapts to PipelineStrategy interface
    """

    def __init__(
        self,
        config: Optional[AdvancedPipelineConfig] = None,
        observable: Optional[PipelineObservable] = None,
        verbose: bool = True
    ):
        """
        Initialize advanced pipeline strategy facade.

        Args:
            config: Pipeline configuration (creates default if None)
            observable: Pipeline observable for events
            verbose: Enable detailed logging
        """
        self.verbose = verbose
        self.logger = PipelineLogger(verbose=verbose)

        # Initialize configuration manager
        self.config_manager = ConfigurationManager(config, observable)
        self.config = self.config_manager.config

        # Initialize mode selector
        self.mode_selector = ModeSelector(self.config, observable=observable)

        # Initialize components
        self._initialize_components(observable)

        # Initialize executors
        self._initialize_executors(observable)

        # Store observable
        self.observable = observable

    def _initialize_components(self, observable: Optional[PipelineObservable]) -> None:
        """
        Initialize shared components.

        Args:
            observable: Pipeline observable
        """
        # Initialize thermodynamic computing (if enabled)
        self.thermodynamic = None
        if self.config.enable_thermodynamic and ThermodynamicComputing is not None:
            try:
                self.thermodynamic = ThermodynamicComputing(
                    observable=observable,
                    default_strategy=self.config.default_uncertainty_strategy
                )
            except Exception as e:
                self.logger.log(
                    f"Failed to initialize ThermodynamicComputing: {e}. "
                    f"Thermodynamic features will be disabled.",
                    "WARNING"
                )
                self.thermodynamic = None

        # Initialize helper components
        self.confidence_quantifier = ConfidenceQuantifier(
            thermodynamic=self.thermodynamic,
            verbose=self.verbose
        )

        self.complexity_analyzer = ComplexityAnalyzer(
            simple_threshold=self.config.simple_task_max_story_points,
            complex_threshold=self.config.complex_task_min_story_points
        )

        self.performance_tracker = PerformanceTracker(
            window_size=self.config.performance_metrics_window,
            enabled=self.config.enable_performance_tracking
        )

        self.event_emitter = EventEmitter(observable=observable)

    def _initialize_executors(self, observable: Optional[PipelineObservable]) -> None:
        """
        Initialize mode-specific executors.

        WHY: Uses dispatch table pattern instead of if/elif chains.

        Args:
            observable: Pipeline observable
        """
        # Initialize standard executor
        self.standard_executor = StandardExecutor(
            confidence_quantifier=self.confidence_quantifier,
            verbose=self.verbose
        )

        # Initialize dynamic executor
        self.dynamic_executor = DynamicExecutor(
            config=self.config,
            complexity_analyzer=self.complexity_analyzer,
            observable=observable,
            verbose=self.verbose
        )

        # Initialize two-pass executor
        self.two_pass_executor = TwoPassExecutor(
            config=self.config,
            observable=observable,
            verbose=self.verbose
        )

        # Initialize adaptive executor
        self.adaptive_executor = AdaptiveExecutor(
            config=self.config,
            confidence_quantifier=self.confidence_quantifier,
            observable=observable,
            verbose=self.verbose
        )

        # Initialize full executor
        self.full_executor = FullExecutor(
            config=self.config,
            complexity_analyzer=self.complexity_analyzer,
            confidence_quantifier=self.confidence_quantifier,
            observable=observable,
            verbose=self.verbose
        )

        # Build executor dispatch table
        # WHY dispatch table: Declarative, easy to extend with new modes
        self.executors = {
            PipelineMode.STANDARD: self.standard_executor,
            PipelineMode.DYNAMIC: self.dynamic_executor,
            PipelineMode.TWO_PASS: self.two_pass_executor,
            PipelineMode.ADAPTIVE: self.adaptive_executor,
            PipelineMode.FULL: self.full_executor
        }

    @wrap_exception(PipelineException, "Advanced pipeline execution failed")
    def execute(
        self,
        stages: List[PipelineStage],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute pipeline with advanced features based on selected mode.

        WHY: Single entry point for all execution modes. Handles complexity
        of mode selection, feature configuration, and result aggregation.

        Args:
            stages: List of pipeline stages to execute
            context: Execution context with task details

        Returns:
            Dict with execution results including status, mode, and metrics

        Raises:
            PipelineException: On execution failure
        """
        execution_start = datetime.now()

        # Select execution mode
        mode = self.mode_selector.select_mode(context)

        self.logger.log(
            f"Executing pipeline in {mode.value} mode with {len(stages)} stages",
            "INFO"
        )

        # Emit execution start event
        self.event_emitter.emit_execution_started(mode, context)

        try:
            # Execute based on mode using dispatch table
            executor = self.executors.get(mode, self.standard_executor)
            result = executor.execute(stages, context)

            # Add execution metadata
            result["mode"] = mode.value
            result["execution_time"] = (datetime.now() - execution_start).total_seconds()

            # Track performance metrics
            self.performance_tracker.track(result, mode)

            # Emit execution complete event
            self.event_emitter.emit_execution_completed(mode, context, result)

            return result

        except Exception as e:
            # Emit execution failed event
            self.event_emitter.emit_execution_failed(mode, context, str(e))

            # Re-raise wrapped exception
            raise

    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get performance summary across recent executions.

        WHY: Provides aggregate metrics for evaluating advanced features impact.

        Returns:
            Dict with performance summary
        """
        return self.performance_tracker.get_summary()
