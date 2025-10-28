"""
Module: two_pass/pipeline/orchestrator.py

WHY: Main facade for two-pass pipeline - integrates all components.
RESPONSIBILITY: Coordinate executor, AI integration, and provide simple interface.
PATTERNS: Facade Pattern, Composition, Guard Clauses.

This module handles:
- Initialize all pipeline components
- Provide unified interface for pipeline execution
- Integrate router context for hybrid AI approach
- Expose execution and rollback history
- Delegate to specialized components
"""

from typing import Dict, Any, Optional, List

from two_pass.models import PassResult
from two_pass.strategies import PassStrategy
from two_pass.comparator import PassComparator
from two_pass.rollback import RollbackManager
from two_pass.pipeline.retry import RetryStrategy, RetryConfig
from two_pass.pipeline.executor import TwoPassExecutor
from two_pass.pipeline.ai_integration import AIIntegrationMixin, AIConfig
from artemis_exceptions import wrap_exception
from two_pass.exceptions import TwoPassPipelineException
from pipeline_observer import PipelineObservable


class TwoPassPipeline(AIIntegrationMixin):
    """
    Main facade for two-pass pipeline orchestration.

    Why it exists: Provides simple, unified interface for two-pass pipeline.
    Hides complexity of multiple components (executor, AI integration, retry).

    Design pattern: Facade + Composition
    Why this design:
    - Facade: Simplifies complex multi-component interaction
    - Composition: Delegates to specialized components
    - Mixin: Adds AI capabilities via AIIntegrationMixin

    Responsibilities:
    - Initialize all pipeline components
    - Provide clean execution interface
    - Integrate router context for cost efficiency
    - Expose execution history and rollback tracking
    - Delegate work to executor and AI integration

    Usage:
        # Basic usage
        pipeline = TwoPassPipeline(
            first_pass_strategy=first_pass,
            second_pass_strategy=second_pass,
            context={'intensity': 0.7}
        )
        result = pipeline.execute(context)

        # With AI integration
        quality = pipeline.assess_pass_quality_with_ai(
            code=implementation,
            requirements=task_spec
        )

    Thread-safety: Not thread-safe (assumes single-threaded execution)
    """

    def __init__(
        self,
        first_pass_strategy: PassStrategy,
        second_pass_strategy: PassStrategy,
        context: Optional[Dict[str, Any]] = None,
        observable: Optional[PipelineObservable] = None,
        auto_rollback: bool = True,
        rollback_threshold: float = -0.1,
        verbose: bool = True
    ):
        """
        Initialize two-pass pipeline orchestrator.

        Why needed: Sets up all components (strategies, comparator, rollback manager,
        executor, AI integration) and configures behavior (auto-rollback, threshold).

        NEW: Hybrid AI Approach - Accepts context from router with pre-computed analysis.

        Args:
            first_pass_strategy: Strategy for first pass execution
            second_pass_strategy: Strategy for second pass execution
            context: Router context with pre-computed analysis (intensity, guidance, etc.)
            observable: Event broadcaster for observer pattern
            auto_rollback: Automatically rollback if second pass degrades quality
            rollback_threshold: Quality degradation threshold for auto-rollback (-0.1 = 10% worse)
            verbose: Enable detailed logging
        """
        # Extract AI configuration from router context
        ai_config = self._extract_ai_config(context)

        # Initialize AI integration mixin
        super().__init__(ai_config)

        # Initialize core components
        self.comparator = PassComparator(observable=observable, verbose=verbose)
        self.rollback_manager = RollbackManager(observable=observable, verbose=verbose)
        self.retry_strategy = RetryStrategy(
            RetryConfig(max_retries=3, verbose=verbose)
        )

        # Initialize executor
        self.executor = TwoPassExecutor(
            first_pass_strategy=first_pass_strategy,
            second_pass_strategy=second_pass_strategy,
            comparator=self.comparator,
            rollback_manager=self.rollback_manager,
            retry_strategy=self.retry_strategy,
            observable=observable,
            auto_rollback=auto_rollback,
            rollback_threshold=rollback_threshold,
            verbose=verbose
        )

        # Store configuration
        self.observable = observable
        self.auto_rollback = auto_rollback
        self.rollback_threshold = rollback_threshold
        self.verbose = verbose
        self.context = context or {}

    def _extract_ai_config(self, context: Optional[Dict[str, Any]]) -> AIConfig:
        """
        Extract AI configuration from router context.

        Why extracted: Encapsulates context parsing logic. Provides defaults
        for missing values.

        Args:
            context: Router context with pre-computed analysis

        Returns:
            AIConfig with extracted or default values
        """
        # Guard clause - no context provided
        if not context:
            return AIConfig()

        return AIConfig(
            ai_service=context.get('ai_service'),
            router_intensity=context.get('intensity', 0.5),
            router_guidance=context.get('prompt', ''),
            quality_threshold=context.get('quality_threshold', 0.7),
            first_pass_timeout=context.get('first_pass_timeout', 30),
            second_pass_timeout=context.get('second_pass_timeout', 120),
            first_pass_guidance=context.get('first_pass_guidance', []),
            second_pass_guidance=context.get('second_pass_guidance', [])
        )

    @wrap_exception(TwoPassPipelineException, "Two-pass pipeline execution failed")
    def execute(self, context: Dict[str, Any]) -> PassResult:
        """
        Execute complete two-pass pipeline workflow.

        Delegates to executor for actual execution logic.

        Args:
            context: Execution context with inputs, config, etc.

        Returns:
            Final PassResult (second pass if successful, first pass if rolled back)

        Raises:
            TwoPassPipelineException: On critical failure
        """
        return self.executor.execute(context)

    def get_execution_history(self) -> List[Dict[str, Any]]:
        """
        Get execution history for audit trail.

        Delegates to executor.

        Returns:
            List of execution records with timestamps, quality scores, etc.
        """
        return self.executor.get_execution_history()

    def get_rollback_history(self) -> List[Dict[str, Any]]:
        """
        Get rollback history from rollback manager.

        Delegates to executor which delegates to rollback manager.

        Returns:
            List of rollback events with reasons and timestamps
        """
        return self.executor.get_rollback_history()


__all__ = ['TwoPassPipeline']
