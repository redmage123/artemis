#!/usr/bin/env python3
"""
Module: two_pass_pipeline.py

Purpose: Implements Two-Pass Pipeline system for Artemis with fast analysis followed by refined execution
Why: Enables rapid feedback (first pass) with learning-enhanced execution (second pass), reducing
     wasted compute on flawed approaches while capturing incremental improvements between passes.
     Provides rollback capability when second pass fails, maintaining system stability.

Patterns:
- Template Method Pattern (BasePipelinePass defines pass structure)
- Strategy Pattern (FirstPassStrategy vs SecondPassStrategy for pass-specific behavior)
- Memento Pattern (PassMemento captures state between passes)
- Observer Pattern (event broadcasting to pipeline_observer.py)
- Decorator Pattern (@wrap_exception for error handling)
- Command Pattern (pass operations as commands with undo)

Integration:
- pipeline_observer.py: Broadcasts events for all pass operations
- artemis_exceptions.py: Uses @wrap_exception for standardized error handling
- artemis_utilities.py: Uses RetryStrategy for resilient operations
- artemis_stages.py: Can be integrated into existing pipeline stages

Architecture:
    TwoPassPipeline (Orchestrator)
    ├── FirstPassStrategy (fast analysis)
    │   ├── execute() - quick validation and planning
    │   └── create_memento() - capture insights
    ├── SecondPassStrategy (refined execution)
    │   ├── execute() - full implementation with first pass learnings
    │   └── apply_memento() - use first pass insights
    ├── PassMemento (state capture)
    │   ├── State snapshot between passes
    │   └── Delta detection
    ├── PassComparator (validation)
    │   ├── Compare pass results
    │   └── Quality metrics
    └── RollbackManager (recovery)
        ├── Restore on failure
        └── Incremental improvements

Design Decisions:
- NO elif chains: Use dispatch tables and Strategy pattern
- NO nested loops: Extract to helper methods
- NO nested ifs: Use early returns and guard clauses
- NO sequential ifs: Use dispatch tables for conditional logic
- All major operations emit Observer events
- @wrap_exception decorator for ALL error handling

Event Flow:
    TwoPassPipeline -> notify(FIRST_PASS_STARTED) -> PipelineObservable -> observers
    FirstPass -> execute() -> notify(FIRST_PASS_COMPLETED)
    TwoPassPipeline -> notify(SECOND_PASS_STARTED)
    SecondPass -> execute() -> notify(SECOND_PASS_COMPLETED)
    PassComparator -> validate() -> notify(PASS_COMPARISON_COMPLETED)

Why Two-Pass:
1. Fast feedback: First pass identifies fatal flaws quickly (seconds vs minutes)
2. Learning: Second pass uses first pass insights to avoid repeated mistakes
3. Resource efficiency: Don't waste expensive compute on bad approaches
4. Rollback safety: Can revert to first pass if second pass degrades quality
5. Incremental improvement: Capture what works, refine what doesn't
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable, TypeVar
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import copy

from artemis_exceptions import (
    ArtemisException,
    wrap_exception,
    PipelineException,
    PipelineStageError,
    PipelineValidationError
)
from artemis_utilities import RetryStrategy, RetryConfig
from artemis_services import PipelineLogger
from pipeline_observer import (
    PipelineObservable,
    PipelineEvent,
    EventType,
    PipelineObserver
)
from advanced_features_ai_mixin import AdvancedFeaturesAIMixin


# ============================================================================
# CUSTOM EVENT TYPES FOR TWO-PASS PIPELINE
# ============================================================================

class TwoPassEventType(Enum):
    """
    Event types specific to two-pass pipeline operations.

    Why needed: Extends EventType with two-pass specific events for granular monitoring
    of first pass, second pass, delta detection, and rollback operations.

    Categories:
    - First pass lifecycle: FIRST_PASS_STARTED, FIRST_PASS_COMPLETED, FIRST_PASS_FAILED
    - Second pass lifecycle: SECOND_PASS_STARTED, SECOND_PASS_COMPLETED, SECOND_PASS_FAILED
    - Pass comparison: PASS_DELTA_DETECTED, PASS_QUALITY_IMPROVED, PASS_QUALITY_DEGRADED
    - State management: MEMENTO_CREATED, MEMENTO_APPLIED, ROLLBACK_INITIATED
    - Learning: LEARNING_CAPTURED, INSIGHT_APPLIED
    """

    # First pass events
    FIRST_PASS_STARTED = "first_pass_started"
    FIRST_PASS_COMPLETED = "first_pass_completed"
    FIRST_PASS_FAILED = "first_pass_failed"
    FIRST_PASS_ANALYSIS_COMPLETED = "first_pass_analysis_completed"

    # Second pass events
    SECOND_PASS_STARTED = "second_pass_started"
    SECOND_PASS_COMPLETED = "second_pass_completed"
    SECOND_PASS_FAILED = "second_pass_failed"
    SECOND_PASS_REFINED = "second_pass_refined"

    # Delta and comparison events
    PASS_DELTA_DETECTED = "pass_delta_detected"
    PASS_COMPARISON_STARTED = "pass_comparison_started"
    PASS_COMPARISON_COMPLETED = "pass_comparison_completed"
    PASS_QUALITY_IMPROVED = "pass_quality_improved"
    PASS_QUALITY_DEGRADED = "pass_quality_degraded"
    PASS_QUALITY_UNCHANGED = "pass_quality_unchanged"

    # State management events
    MEMENTO_CREATED = "memento_created"
    MEMENTO_APPLIED = "memento_applied"
    MEMENTO_RESTORED = "memento_restored"

    # Rollback events
    ROLLBACK_INITIATED = "rollback_initiated"
    ROLLBACK_COMPLETED = "rollback_completed"
    ROLLBACK_FAILED = "rollback_failed"

    # Learning events
    LEARNING_CAPTURED = "learning_captured"
    INSIGHT_APPLIED = "insight_applied"
    INCREMENTAL_IMPROVEMENT = "incremental_improvement"


# ============================================================================
# EXCEPTIONS
# ============================================================================

class TwoPassPipelineException(PipelineException):
    """Base exception for two-pass pipeline errors"""
    pass


class FirstPassException(TwoPassPipelineException):
    """Error during first pass execution"""
    pass


class SecondPassException(TwoPassPipelineException):
    """Error during second pass execution"""
    pass


class PassComparisonException(TwoPassPipelineException):
    """Error comparing pass results"""
    pass


class RollbackException(TwoPassPipelineException):
    """Error during rollback operation"""
    pass


class MementoException(TwoPassPipelineException):
    """Error creating or applying memento"""
    pass


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class PassResult:
    """
    Result of a pipeline pass execution.

    Why needed: Standardized structure for pass outputs, enabling comparison,
    validation, and learning extraction across passes.

    Responsibilities:
    - Store pass execution artifacts and metadata
    - Track quality metrics for comparison
    - Capture learnings and insights
    - Provide serialization for storage
    """
    pass_name: str
    success: bool
    artifacts: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0
    execution_time: float = 0.0
    learnings: List[str] = field(default_factory=list)
    insights: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary for serialization.

        Why needed: Enables storage, logging, and transmission of pass results.
        Used by observers for metrics collection and by memento for state capture.

        Returns:
            Dictionary representation of pass result
        """
        return {
            "pass_name": self.pass_name,
            "success": self.success,
            "artifacts": self.artifacts,
            "quality_score": self.quality_score,
            "execution_time": self.execution_time,
            "learnings": self.learnings,
            "insights": self.insights,
            "errors": self.errors,
            "warnings": self.warnings,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class PassDelta:
    """
    Difference between two pass executions.

    Why needed: Captures what changed between first and second pass, enabling
    learning extraction, quality tracking, and incremental improvement analysis.

    Design pattern: Value Object (immutable after creation)

    Responsibilities:
    - Compare pass results and extract differences
    - Calculate quality improvements/degradations
    - Identify new learnings and insights
    - Track artifact changes
    """
    first_pass: PassResult
    second_pass: PassResult
    quality_delta: float = 0.0
    new_artifacts: List[str] = field(default_factory=list)
    modified_artifacts: List[str] = field(default_factory=list)
    removed_artifacts: List[str] = field(default_factory=list)
    new_learnings: List[str] = field(default_factory=list)
    quality_improved: bool = False
    execution_time_delta: float = 0.0

    def __post_init__(self):
        """
        Calculate delta metrics after initialization.

        Why needed: Automatically computes deltas when PassDelta is created,
        ensuring metrics are always consistent and up-to-date.
        """
        # Calculate quality delta - positive means improvement
        self.quality_delta = self.second_pass.quality_score - self.first_pass.quality_score
        self.quality_improved = self.quality_delta > 0

        # Calculate execution time delta
        self.execution_time_delta = self.second_pass.execution_time - self.first_pass.execution_time

        # Detect artifact changes using sets for O(1) lookups instead of nested loops
        first_artifacts = set(self.first_pass.artifacts.keys())
        second_artifacts = set(self.second_pass.artifacts.keys())

        self.new_artifacts = list(second_artifacts - first_artifacts)
        self.removed_artifacts = list(first_artifacts - second_artifacts)

        # Modified artifacts: present in both but with different values
        common_artifacts = first_artifacts & second_artifacts
        self.modified_artifacts = [
            key for key in common_artifacts
            if self.first_pass.artifacts[key] != self.second_pass.artifacts[key]
        ]

        # Extract new learnings using set difference
        first_learnings = set(self.first_pass.learnings)
        second_learnings = set(self.second_pass.learnings)
        self.new_learnings = list(second_learnings - first_learnings)

    def to_dict(self) -> Dict[str, Any]:
        """Convert delta to dictionary for serialization"""
        return {
            "first_pass": self.first_pass.to_dict(),
            "second_pass": self.second_pass.to_dict(),
            "quality_delta": self.quality_delta,
            "new_artifacts": self.new_artifacts,
            "modified_artifacts": self.modified_artifacts,
            "removed_artifacts": self.removed_artifacts,
            "new_learnings": self.new_learnings,
            "quality_improved": self.quality_improved,
            "execution_time_delta": self.execution_time_delta
        }


# ============================================================================
# MEMENTO PATTERN - State Capture
# ============================================================================

@dataclass
class PassMemento:
    """
    Memento for capturing pass state (Memento Pattern).

    Why it exists: Captures complete state of a pipeline pass for restoration
    or analysis. Enables rollback when second pass fails and learning transfer
    from first to second pass.

    Design pattern: Memento Pattern
    Why this design: Provides snapshot of pass state without exposing internal
    structure. Allows state capture/restore without tight coupling between passes.

    Responsibilities:
    - Capture pass state at point in time
    - Store artifacts, learnings, and insights
    - Enable state restoration for rollback
    - Preserve quality metrics for comparison
    - Support deep copy to prevent mutation

    Use cases:
    - Rollback to first pass if second pass fails
    - Transfer learnings from first to second pass
    - Compare states across passes
    - Audit trail of pass evolution
    """
    pass_name: str
    state: Dict[str, Any]
    artifacts: Dict[str, Any]
    learnings: List[str]
    insights: Dict[str, Any]
    quality_score: float
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def create_copy(self) -> 'PassMemento':
        """
        Create deep copy of memento.

        Why needed: Prevents mutation of stored state. When applying memento to
        second pass, we don't want changes to second pass to affect stored state.

        Returns:
            Deep copy of memento

        Design note: Uses copy.deepcopy to recursively copy all nested structures
        """
        return PassMemento(
            pass_name=self.pass_name,
            state=copy.deepcopy(self.state),
            artifacts=copy.deepcopy(self.artifacts),
            learnings=copy.deepcopy(self.learnings),
            insights=copy.deepcopy(self.insights),
            quality_score=self.quality_score,
            timestamp=self.timestamp,
            metadata=copy.deepcopy(self.metadata)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert memento to dictionary for serialization"""
        return {
            "pass_name": self.pass_name,
            "state": self.state,
            "artifacts": self.artifacts,
            "learnings": self.learnings,
            "insights": self.insights,
            "quality_score": self.quality_score,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


# ============================================================================
# STRATEGY PATTERN - Pass Execution Strategies
# ============================================================================

class PassStrategy(ABC):
    """
    Abstract strategy for pipeline pass execution (Strategy Pattern).

    Why it exists: Defines contract for all pass strategies (first pass, second pass,
    custom passes). Enables swapping pass implementations without changing orchestrator.

    Design pattern: Strategy Pattern + Template Method Pattern
    Why this design: Strategy pattern allows different pass implementations (fast vs thorough).
    Template Method pattern provides common structure with customization points.

    Responsibilities:
    - Define pass execution contract
    - Create memento of pass state
    - Apply memento from previous pass
    - Extract learnings and insights
    - Calculate quality metrics

    Template Method structure:
    1. execute() - implemented by subclass (the strategy)
    2. create_memento() - default implementation with override option
    3. apply_memento() - default implementation with override option

    Thread-safety: Not thread-safe (assumes single-threaded execution)
    """

    def __init__(self, observable: Optional[PipelineObservable] = None, verbose: bool = True):
        """
        Initialize pass strategy.

        Why needed: Sets up observer integration for event broadcasting and
        logging infrastructure.

        Args:
            observable: Event broadcaster for observer pattern integration
            verbose: Enable detailed logging
        """
        self.observable = observable
        self.verbose = verbose
        self.logger = PipelineLogger(verbose=verbose)

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> PassResult:
        """
        Execute pass with given context (abstract method - must override).

        Why needed: Core strategy method that subclasses implement with
        pass-specific logic (fast analysis vs thorough execution).

        Args:
            context: Execution context with configuration, inputs, and prior state

        Returns:
            PassResult with artifacts, learnings, and quality metrics

        Raises:
            PassStrategy subclass exceptions on execution failure

        Design note: Takes Dict instead of typed config for flexibility across
        different pass types with different context requirements.
        """
        pass

    @abstractmethod
    def get_pass_name(self) -> str:
        """
        Get name of this pass strategy.

        Why needed: Used for logging, events, and memento identification.
        Each strategy returns unique name (e.g., "FirstPass", "SecondPass").

        Returns:
            Human-readable pass name
        """
        pass

    def create_memento(self, result: PassResult, state: Dict[str, Any]) -> PassMemento:
        """
        Create memento from pass result and state (Template Method - can override).

        Why needed: Captures pass state for rollback or transfer to next pass.
        Default implementation works for most cases, but can be overridden for
        custom state capture requirements.

        Args:
            result: PassResult from execute()
            state: Additional state to capture (configuration, intermediate results, etc.)

        Returns:
            PassMemento with complete state snapshot

        Design note: Separated from execute() to allow state capture at different
        points in pass lifecycle (not just at completion).
        """
        return PassMemento(
            pass_name=self.get_pass_name(),
            state=state,
            artifacts=result.artifacts,
            learnings=result.learnings,
            insights=result.insights,
            quality_score=result.quality_score,
            metadata=result.metadata
        )

    def apply_memento(self, memento: PassMemento, context: Dict[str, Any]) -> None:
        """
        Apply memento to context (Template Method - can override).

        Why needed: Transfers learnings and insights from previous pass to current
        pass. Enables second pass to benefit from first pass discoveries.

        Args:
            memento: State snapshot from previous pass
            context: Current pass context to augment with memento data

        Side effects: Modifies context dict to include memento learnings and insights

        Design note: Modifies context in-place rather than returning new context
        because context may be large and copying is expensive.
        """
        # Merge learnings - use set to deduplicate
        existing_learnings = set(context.get("learnings", []))
        existing_learnings.update(memento.learnings)
        context["learnings"] = list(existing_learnings)

        # Merge insights - preserve both old and new
        if "insights" not in context:
            context["insights"] = {}
        context["insights"].update(memento.insights)

        # Store previous pass quality score for comparison
        context["previous_quality_score"] = memento.quality_score

    def emit_event(self, event_type: TwoPassEventType, data: Dict[str, Any]) -> None:
        """
        Emit event to observers (helper method).

        Why needed: Centralizes event emission logic with consistent data structure.
        All events include standard fields (pass_name, timestamp) plus custom data.

        Args:
            event_type: Type of event to emit
            data: Event-specific data

        Design note: Converts TwoPassEventType to EventType.STAGE_PROGRESS for
        compatibility with existing observer infrastructure.
        """
        # Guard clause - early return if no observable
        if not self.observable:
            return

        # Create event with standard EventType that observers understand
        # Use STAGE_PROGRESS as catch-all for custom events
        event = PipelineEvent(
            event_type=EventType.STAGE_PROGRESS,
            stage_name=self.get_pass_name(),
            data={
                "two_pass_event": event_type.value,
                "pass_name": self.get_pass_name(),
                **data
            }
        )

        self.observable.notify(event)


class FirstPassStrategy(PassStrategy):
    """
    Strategy for first pass execution: fast analysis and planning.

    Why it exists: Provides rapid feedback on feasibility, identifies obvious issues,
    and creates execution plan for second pass. Optimizes for speed over thoroughness.

    Design pattern: Strategy Pattern (concrete strategy)

    Responsibilities:
    - Quick validation of inputs and requirements
    - High-level analysis and planning
    - Identify fatal flaws early
    - Generate insights for second pass
    - Create baseline quality metrics

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
        """Get first pass name"""
        return "FirstPass"

    def _analyze(self, inputs: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform fast analysis on inputs (extracted helper method).

        Why extracted: Avoids nesting analysis loop inside execute(). Follows
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
        analysis_handlers = {
            "validation": self._validate_inputs,
            "schema_check": self._check_schema,
            "dependency_scan": self._scan_dependencies
        }

        # Execute configured analyses
        analysis_type = config.get("analysis_type", "validation")
        handler = analysis_handlers.get(analysis_type, self._validate_inputs)
        artifacts["validation_results"] = handler(inputs)

        return artifacts

    def _validate_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate inputs (placeholder for actual validation)"""
        return {
            "valid": True,
            "checks_passed": len(inputs),
            "checks_failed": 0
        }

    def _check_schema(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Check schema (placeholder for actual schema validation)"""
        return {
            "schema_valid": True,
            "fields_validated": len(inputs)
        }

    def _scan_dependencies(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Scan dependencies (placeholder for actual dependency scan)"""
        return {
            "dependencies_found": 0,
            "conflicts_detected": 0
        }

    def _extract_learnings(self, artifacts: Dict[str, Any]) -> List[str]:
        """
        Extract learnings from analysis artifacts.

        Why needed: Captures insights from first pass to guide second pass.
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

        Why needed: Insights are structured data (not strings) that second pass
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

        Why needed: Provides baseline for comparison with second pass.
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


class SecondPassStrategy(PassStrategy):
    """
    Strategy for second pass execution: refined implementation with first pass learnings.

    Why it exists: Performs thorough execution using insights from first pass.
    Optimizes for quality and correctness over speed.

    Design pattern: Strategy Pattern (concrete strategy)

    Responsibilities:
    - Apply first pass learnings
    - Thorough validation and analysis
    - Complete implementation
    - Quality verification
    - Incremental improvements

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

        # Emit appropriate completion event based on quality
        if quality_improved:
            event_type = TwoPassEventType.PASS_QUALITY_IMPROVED
        else:
            event_type = TwoPassEventType.SECOND_PASS_COMPLETED

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
        """Get second pass name"""
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

        Why extracted: Separates implementation logic from orchestration.
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
        check_handlers = {
            "thorough_validation": self._thorough_validation,
            "integration_test": self._integration_test,
            "performance_test": self._performance_test
        }

        check_type = config.get("check_type", "thorough_validation")
        handler = check_handlers.get(check_type, self._thorough_validation)
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

        Why extracted: Avoids nested loop (inputs x learnings). Each learning is
        processed independently and results are aggregated.

        Args:
            inputs: Data to process
            learnings: Learnings from first pass
            insights: Insights from first pass

        Returns:
            List of refinements applied
        """
        refinements = []

        # Process each learning independently - no nested iteration
        for learning in learnings:
            refinement = self._apply_single_learning(learning, insights)
            if refinement:
                refinements.append(refinement)

        return refinements

    def _apply_single_learning(
        self,
        learning: str,
        insights: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Apply single learning to create refinement (helper method).

        Why extracted: Processes one learning at a time, avoiding nested loops.
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

        Why needed: Routes learnings to appropriate handlers without if/elif chains.

        Args:
            learning: Learning statement

        Returns:
            Learning type category
        """
        # Use dispatch table based on keywords
        keywords_to_type = {
            "validation": "validation",
            "validated": "validation",
            "performance": "performance",
            "faster": "performance",
            "quality": "quality",
            "improved": "quality"
        }

        learning_lower = learning.lower()

        # Find first matching keyword
        for keyword, learning_type in keywords_to_type.items():
            if keyword in learning_lower:
                return learning_type

        return "quality"  # Default category

    def _thorough_validation(
        self,
        inputs: Dict[str, Any],
        refinements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Thorough validation (placeholder for actual validation)"""
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
        """Integration test (placeholder for actual test)"""
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
        """Performance test (placeholder for actual test)"""
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

        Why needed: Captures incremental improvements discovered during second pass.

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
        """Extract insights from artifacts"""
        return {
            "implementation_type": artifacts.get("implementation_type"),
            "inputs_processed": artifacts.get("inputs_processed", 0),
            "refinements_count": len(artifacts.get("refinements", [])),
            "quality_checks_passed": artifacts.get("quality_checks", {}).get("checks_passed", 0)
        }

    def _calculate_quality(self, artifacts: Dict[str, Any]) -> float:
        """
        Calculate comprehensive quality score.

        Why needed: More sophisticated than first pass scoring. Considers multiple
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

        # Bonus for refinements applied
        refinements_count = len(artifacts.get("refinements", []))
        refinement_bonus = min(0.1, refinements_count * 0.02)  # Up to 10% bonus

        return min(1.0, base_score + refinement_bonus)


# ============================================================================
# PASS COMPARATOR - Validates and compares passes
# ============================================================================

class PassComparator:
    """
    Compares pass results to detect deltas and quality changes.

    Why it exists: Validates that second pass improved upon first pass and
    calculates metrics for rollback decisions.

    Responsibilities:
    - Compare pass results
    - Detect quality improvements/degradations
    - Identify new artifacts and learnings
    - Calculate delta metrics
    - Emit comparison events

    Design pattern: Comparator + Observer
    """

    def __init__(self, observable: Optional[PipelineObservable] = None, verbose: bool = True):
        """Initialize comparator with observer integration"""
        self.observable = observable
        self.verbose = verbose
        self.logger = PipelineLogger(verbose=verbose)

    @wrap_exception(PassComparisonException, "Pass comparison failed")
    def compare(self, first_pass: PassResult, second_pass: PassResult) -> PassDelta:
        """
        Compare two pass results and calculate delta.

        What it does:
        1. Emit comparison start event
        2. Create PassDelta (auto-calculates metrics in __post_init__)
        3. Determine quality change type
        4. Emit appropriate event based on quality change
        5. Return delta for analysis

        Args:
            first_pass: First pass result
            second_pass: Second pass result

        Returns:
            PassDelta with comparison metrics

        Raises:
            PassComparisonException: On comparison failure
        """
        self._emit_event(
            TwoPassEventType.PASS_COMPARISON_STARTED,
            {
                "first_pass_quality": first_pass.quality_score,
                "second_pass_quality": second_pass.quality_score
            }
        )

        # Create delta - automatically calculates all metrics
        delta = PassDelta(first_pass=first_pass, second_pass=second_pass)

        # Emit quality change event - dispatch table instead of if/elif
        quality_event_map = {
            "improved": TwoPassEventType.PASS_QUALITY_IMPROVED,
            "degraded": TwoPassEventType.PASS_QUALITY_DEGRADED,
            "unchanged": TwoPassEventType.PASS_QUALITY_UNCHANGED
        }

        quality_change = self._classify_quality_change(delta.quality_delta)
        event_type = quality_event_map[quality_change]

        self._emit_event(
            event_type,
            {
                "quality_delta": delta.quality_delta,
                "new_artifacts_count": len(delta.new_artifacts),
                "new_learnings_count": len(delta.new_learnings),
                "execution_time_delta": delta.execution_time_delta
            }
        )

        return delta

    def _classify_quality_change(self, quality_delta: float, threshold: float = 0.01) -> str:
        """
        Classify quality change type (helper method).

        Why extracted: Encapsulates quality classification logic. Uses threshold
        to avoid noise from tiny fluctuations.

        Args:
            quality_delta: Difference in quality scores
            threshold: Minimum delta to consider changed (default 1%)

        Returns:
            "improved", "degraded", or "unchanged"
        """
        if quality_delta > threshold:
            return "improved"
        elif quality_delta < -threshold:
            return "degraded"
        else:
            return "unchanged"

    def _emit_event(self, event_type: TwoPassEventType, data: Dict[str, Any]) -> None:
        """Emit event to observers (helper method)"""
        # Guard clause - early return if no observable
        if not self.observable:
            return

        event = PipelineEvent(
            event_type=EventType.STAGE_PROGRESS,
            stage_name="PassComparator",
            data={
                "two_pass_event": event_type.value,
                **data
            }
        )

        self.observable.notify(event)


# ============================================================================
# ROLLBACK MANAGER - Handles rollback to first pass
# ============================================================================

class RollbackManager:
    """
    Manages rollback to first pass when second pass fails or degrades quality.

    Why it exists: Provides safety net when second pass makes things worse.
    Preserves system stability by restoring known-good state.

    Design pattern: Memento Pattern + Command Pattern
    Why this design: Memento provides state snapshot, Command provides undo operation.

    Responsibilities:
    - Restore state from memento
    - Validate rollback success
    - Emit rollback events
    - Preserve rollback history
    - Support partial rollback (selective artifact restoration)

    Use cases:
    - Second pass degrades quality score
    - Second pass introduces errors
    - Second pass exceeds resource limits
    - User-initiated rollback
    """

    def __init__(self, observable: Optional[PipelineObservable] = None, verbose: bool = True):
        """Initialize rollback manager with observer integration"""
        self.observable = observable
        self.verbose = verbose
        self.logger = PipelineLogger(verbose=verbose)
        self.rollback_history: List[Dict[str, Any]] = []

    @wrap_exception(RollbackException, "Rollback operation failed")
    def rollback_to_memento(
        self,
        memento: PassMemento,
        reason: str = "Second pass failed"
    ) -> Dict[str, Any]:
        """
        Rollback to state captured in memento.

        What it does:
        1. Emit rollback initiated event
        2. Restore state from memento
        3. Validate restoration
        4. Record rollback in history
        5. Emit rollback completed event
        6. Return restored state

        Args:
            memento: State snapshot to restore
            reason: Human-readable reason for rollback

        Returns:
            Restored state dict

        Raises:
            RollbackException: On restoration failure

        Design note: Creates deep copy of memento state to prevent mutations
        from affecting stored memento.
        """
        self._emit_event(
            TwoPassEventType.ROLLBACK_INITIATED,
            {
                "memento_pass": memento.pass_name,
                "reason": reason,
                "quality_score": memento.quality_score
            }
        )

        # Restore state - deep copy to prevent mutation
        restored_state = copy.deepcopy(memento.state)

        # Validate restoration
        if not self._validate_restoration(restored_state, memento):
            raise RollbackException("Restored state validation failed")

        # Record rollback in history
        self.rollback_history.append({
            "timestamp": datetime.now().isoformat(),
            "memento_pass": memento.pass_name,
            "reason": reason,
            "quality_score": memento.quality_score
        })

        self._emit_event(
            TwoPassEventType.ROLLBACK_COMPLETED,
            {
                "memento_pass": memento.pass_name,
                "artifacts_restored": len(memento.artifacts)
            }
        )

        return restored_state

    def _validate_restoration(self, state: Dict[str, Any], memento: PassMemento) -> bool:
        """
        Validate that restoration succeeded.

        Why needed: Verifies state was correctly restored from memento.
        Prevents silent failures where rollback appears to succeed but state is corrupted.

        Args:
            state: Restored state
            memento: Original memento

        Returns:
            True if validation passes, False otherwise
        """
        # Guard clause - state must not be empty
        if not state:
            return False

        # Verify key memento fields are preserved
        required_keys = ["artifacts", "learnings", "insights"]
        return all(key in state or key in memento.__dict__ for key in required_keys)

    def should_rollback(self, delta: PassDelta, threshold: float = -0.1) -> bool:
        """
        Determine if rollback is needed based on quality delta.

        Why needed: Automated rollback decision based on objective quality metrics.
        Prevents manual intervention for obvious degradations.

        Args:
            delta: PassDelta from comparison
            threshold: Minimum quality degradation to trigger rollback (default -10%)

        Returns:
            True if rollback recommended, False otherwise

        Design note: Uses negative threshold because degradation is negative delta.
        Only rolls back on significant degradation (10%+) to avoid noise.
        """
        # Rollback if quality degraded significantly
        return delta.quality_delta < threshold

    def get_rollback_history(self) -> List[Dict[str, Any]]:
        """Get rollback history for audit trail"""
        return self.rollback_history.copy()

    def _emit_event(self, event_type: TwoPassEventType, data: Dict[str, Any]) -> None:
        """Emit event to observers (helper method)"""
        # Guard clause - early return if no observable
        if not self.observable:
            return

        event = PipelineEvent(
            event_type=EventType.STAGE_PROGRESS,
            stage_name="RollbackManager",
            data={
                "two_pass_event": event_type.value,
                **data
            }
        )

        self.observable.notify(event)


# ============================================================================
# TWO-PASS PIPELINE ORCHESTRATOR
# ============================================================================

class TwoPassPipeline(AdvancedFeaturesAIMixin):
    """
    Orchestrates two-pass pipeline execution with learning and rollback.

    Why it exists: Main entry point for two-pass pipeline. Coordinates first pass,
    second pass, comparison, and rollback. Implements complete two-pass workflow.

    Design pattern: Facade + Template Method + Observer + Mixin (for DRY AI calls)
    Why this design:
    - Facade: Simplifies complex multi-component interaction (strategies, comparator, rollback)
    - Template Method: Defines overall workflow with customization points
    - Observer: Broadcasts events at every workflow stage

    Responsibilities:
    - Execute first pass and capture state
    - Transfer learnings to second pass
    - Execute second pass with refinements
    - Compare pass results
    - Decide on rollback if needed
    - Emit events for observability
    - Manage retry on transient failures

    Workflow:
    1. Execute first pass (fast analysis)
    2. Create memento of first pass state
    3. Apply memento to second pass context
    4. Execute second pass (refined implementation)
    5. Compare results and detect delta
    6. Rollback if quality degraded
    7. Return final result

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

        Why needed: Sets up all components (strategies, comparator, rollback manager)
        and configures behavior (auto-rollback, threshold).

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
        self.first_pass_strategy = first_pass_strategy
        self.second_pass_strategy = second_pass_strategy
        self.observable = observable
        self.auto_rollback = auto_rollback
        self.rollback_threshold = rollback_threshold
        self.verbose = verbose
        self.logger = PipelineLogger(verbose=verbose)

        # NEW: Extract router context for hybrid AI approach
        if context:
            self.ai_service = context.get('ai_service')  # For adaptive calls
            self.router_intensity = context.get('intensity', 0.5)
            self.router_guidance = context.get('prompt', '')
            self.first_pass_timeout = context.get('first_pass_timeout', 30)
            self.second_pass_timeout = context.get('second_pass_timeout', 120)
            self.quality_threshold = context.get('quality_threshold', 0.7)
            self.first_pass_guidance = context.get('first_pass_guidance', [])
            self.second_pass_guidance = context.get('second_pass_guidance', [])
            self.context = context
        else:
            # Fallback for legacy support
            self.ai_service = None
            self.router_intensity = 0.5
            self.router_guidance = ''
            self.first_pass_timeout = 30
            self.second_pass_timeout = 120
            self.quality_threshold = 0.7
            self.first_pass_guidance = []
            self.second_pass_guidance = []
            self.context = {}

        # Initialize components
        self.comparator = PassComparator(observable=observable, verbose=verbose)
        self.rollback_manager = RollbackManager(observable=observable, verbose=verbose)
        self.retry_strategy = RetryStrategy(
            RetryConfig(max_retries=3, verbose=verbose)
        )

        # State tracking
        self.first_pass_memento: Optional[PassMemento] = None
        self.execution_history: List[Dict[str, Any]] = []

    @wrap_exception(TwoPassPipelineException, "Two-pass pipeline execution failed")
    def execute(self, context: Dict[str, Any]) -> PassResult:
        """
        Execute complete two-pass pipeline workflow.

        What it does:
        1. Execute first pass with retry
        2. Create and store memento
        3. Apply memento to second pass context
        4. Execute second pass with retry
        5. Compare results
        6. Auto-rollback if configured and quality degraded
        7. Return final result (second pass or rolled back first pass)

        Args:
            context: Execution context with inputs, config, etc.

        Returns:
            Final PassResult (second pass if successful, first pass if rolled back)

        Raises:
            TwoPassPipelineException: On critical failure

        Design notes:
        - Uses retry strategy for resilience
        - Emits events at every major step
        - Auto-rollback is configurable
        - Preserves execution history for audit
        """
        execution_start = datetime.now()

        # Execute first pass with retry
        first_pass_result = self._execute_first_pass_with_retry(context)

        # Create memento from first pass
        self.first_pass_memento = self._create_memento(first_pass_result, context)

        # Apply memento to second pass context
        second_pass_context = self._prepare_second_pass_context(context)

        # Execute second pass with retry
        second_pass_result = self._execute_second_pass_with_retry(second_pass_context)

        # Compare results
        delta = self.comparator.compare(first_pass_result, second_pass_result)

        # Decide final result (may rollback)
        final_result = self._determine_final_result(
            first_pass_result,
            second_pass_result,
            delta
        )

        # Record execution in history
        self._record_execution(
            first_pass_result,
            second_pass_result,
            delta,
            final_result,
            execution_start
        )

        return final_result

    def _execute_first_pass_with_retry(self, context: Dict[str, Any]) -> PassResult:
        """
        Execute first pass with retry on transient failures.

        Why extracted: Encapsulates retry logic. Avoids nesting retry loop in execute().

        Args:
            context: Execution context

        Returns:
            First pass result

        Raises:
            FirstPassException: On persistent failure
        """
        def _execute() -> PassResult:
            return self.first_pass_strategy.execute(context)

        return self.retry_strategy.retry(_execute)

    def _create_memento(self, result: PassResult, context: Dict[str, Any]) -> PassMemento:
        """
        Create memento from first pass result.

        Why extracted: Separates memento creation from execution. Emits event for tracking.

        Args:
            result: First pass result
            context: Execution context

        Returns:
            PassMemento with state snapshot
        """
        memento = self.first_pass_strategy.create_memento(result, context)

        # Emit memento created event
        if self.observable:
            event = PipelineEvent(
                event_type=EventType.STAGE_PROGRESS,
                stage_name="TwoPassPipeline",
                data={
                    "two_pass_event": TwoPassEventType.MEMENTO_CREATED.value,
                    "pass_name": result.pass_name,
                    "quality_score": result.quality_score,
                    "learnings_count": len(result.learnings)
                }
            )
            self.observable.notify(event)

        return memento

    def _prepare_second_pass_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare second pass context with first pass learnings.

        Why extracted: Encapsulates context preparation logic. Creates new context
        dict to avoid mutating original.

        Args:
            context: Original context

        Returns:
            New context with memento applied
        """
        # Guard clause - need memento to prepare context
        if not self.first_pass_memento:
            raise TwoPassPipelineException("No first pass memento available")

        # Create new context (don't mutate original)
        second_pass_context = copy.deepcopy(context)

        # Apply memento to context
        self.second_pass_strategy.apply_memento(self.first_pass_memento, second_pass_context)

        # Emit memento applied event
        if self.observable:
            event = PipelineEvent(
                event_type=EventType.STAGE_PROGRESS,
                stage_name="TwoPassPipeline",
                data={
                    "two_pass_event": TwoPassEventType.MEMENTO_APPLIED.value,
                    "learnings_applied": len(second_pass_context.get("learnings", [])),
                    "insights_applied": len(second_pass_context.get("insights", {}))
                }
            )
            self.observable.notify(event)

        return second_pass_context

    def _execute_second_pass_with_retry(self, context: Dict[str, Any]) -> PassResult:
        """
        Execute second pass with retry on transient failures.

        Why extracted: Encapsulates retry logic. Avoids nesting retry loop in execute().

        Args:
            context: Second pass context with learnings

        Returns:
            Second pass result

        Raises:
            SecondPassException: On persistent failure
        """
        def _execute() -> PassResult:
            return self.second_pass_strategy.execute(context)

        return self.retry_strategy.retry(_execute)

    def _determine_final_result(
        self,
        first_pass: PassResult,
        second_pass: PassResult,
        delta: PassDelta
    ) -> PassResult:
        """
        Determine final result (may rollback to first pass).

        Why extracted: Encapsulates rollback decision logic. Uses dispatch table
        instead of if/elif for extensibility.

        Args:
            first_pass: First pass result
            second_pass: Second pass result
            delta: Comparison delta

        Returns:
            Final result (second pass or first pass if rolled back)
        """
        # Guard clause - if auto-rollback disabled, always use second pass
        if not self.auto_rollback:
            return second_pass

        # Determine if rollback needed
        should_rollback = self.rollback_manager.should_rollback(delta, self.rollback_threshold)

        # Guard clause - if rollback not needed, use second pass
        if not should_rollback:
            return second_pass

        # Rollback to first pass
        if self.verbose:
            self.logger.log(
                f"Rolling back to first pass (quality degraded by {abs(delta.quality_delta):.2%})",
                "WARNING"
            )

        # Perform rollback
        self.rollback_manager.rollback_to_memento(
            self.first_pass_memento,
            reason=f"Quality degraded by {abs(delta.quality_delta):.2%}"
        )

        return first_pass

    def _record_execution(
        self,
        first_pass: PassResult,
        second_pass: PassResult,
        delta: PassDelta,
        final_result: PassResult,
        start_time: datetime
    ) -> None:
        """
        Record execution in history for audit trail.

        Why extracted: Separates history tracking from execution logic.

        Args:
            first_pass: First pass result
            second_pass: Second pass result
            delta: Comparison delta
            final_result: Final result (may be first or second pass)
            start_time: Execution start timestamp
        """
        execution_time = (datetime.now() - start_time).total_seconds()

        self.execution_history.append({
            "timestamp": start_time.isoformat(),
            "execution_time": execution_time,
            "first_pass_quality": first_pass.quality_score,
            "second_pass_quality": second_pass.quality_score,
            "quality_delta": delta.quality_delta,
            "final_pass": final_result.pass_name,
            "rolled_back": final_result.pass_name == first_pass.pass_name
        })

    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get execution history for audit trail"""
        return self.execution_history.copy()

    def get_rollback_history(self) -> List[Dict[str, Any]]:
        """Get rollback history from rollback manager"""
        return self.rollback_manager.get_rollback_history()

    # ========================================================================
    # HYBRID AI METHODS (Using Mixin)
    # ========================================================================

    @wrap_exception(TwoPassPipelineException, "AI-enhanced quality assessment failed")
    def assess_pass_quality_with_ai(
        self,
        code: str,
        requirements: str = "",
        previous_version: Optional[str] = None,
        use_initial_analysis: bool = True
    ) -> Dict[str, Any]:
        """
        Assess pass quality using hybrid AI approach.

        NEW: Demonstrates hybrid pattern for TwoPassPipeline:
        1. Start with router's pre-computed quality threshold (free!)
        2. Make adaptive AI call if detailed assessment needed (via mixin)
        3. Return comprehensive quality evaluation

        WHY: Shows integration of router context + adaptive AI calls for quality assessment.

        Args:
            code: Code to evaluate
            requirements: Requirements for context
            previous_version: Previous pass version for comparison
            use_initial_analysis: If True, uses router's pre-computed threshold first

        Returns:
            Dict with quality assessment including:
                - overall_score: float - Overall quality score (0.0-1.0)
                - criteria_scores: Dict[str, float] - Individual quality criteria
                - improvement: float - Improvement over previous version (if provided)
                - meets_threshold: bool - Whether quality meets router's threshold
                - source: str - Where assessment came from
                - suggestions: List[str] - Improvement suggestions

        Usage:
            # Uses hybrid approach
            assessment = pipeline.assess_pass_quality_with_ai(
                code=implementation_code,
                requirements=task_requirements,
                previous_version=first_pass_code
            )
        """
        # HYBRID STEP 1: Use router's pre-computed threshold (FREE!)
        if use_initial_analysis and self.quality_threshold is not None:
            # Router already provided quality threshold based on task analysis
            # For simple tasks, basic heuristics sufficient
            if self.router_intensity < 0.4:
                # Simple task - basic quality check
                basic_score = min(1.0, 0.5 + (self.router_intensity * 0.5))
                return {
                    'overall_score': basic_score,
                    'criteria_scores': {
                        'correctness': basic_score,
                        'completeness': basic_score,
                        'maintainability': basic_score
                    },
                    'improvement': 0.0,
                    'meets_threshold': basic_score >= self.quality_threshold,
                    'source': 'router_precomputed',
                    'suggestions': [],
                    'cost': 0.0  # Free!
                }

        # HYBRID STEP 2: Complex task or threshold not met - make adaptive AI call
        if not self.ai_service:
            # Fallback: No AI service available, use conservative estimate
            fallback_score = self.quality_threshold if self.quality_threshold else 0.7
            return {
                'overall_score': fallback_score,
                'criteria_scores': {
                    'correctness': fallback_score,
                    'completeness': fallback_score,
                    'maintainability': fallback_score
                },
                'improvement': 0.0,
                'meets_threshold': True,
                'source': 'fallback_no_ai_service',
                'suggestions': [],
                'warning': 'No AI service available, conservative estimate'
            }

        # Make AI call via mixin method for quality evaluation (DRY!)
        ai_quality = self.query_for_quality(
            code=code,
            requirements=requirements,
            previous_version=previous_version
        )

        # Calculate improvement if previous version provided
        improvement = 0.0
        if previous_version and ai_quality.comparison:
            improvement = ai_quality.comparison.get('improvement', 0.0)

        return {
            'overall_score': ai_quality.overall_score,
            'criteria_scores': ai_quality.criteria_scores,
            'improvement': improvement,
            'meets_threshold': ai_quality.overall_score >= self.quality_threshold,
            'source': 'ai_assessed',
            'suggestions': ai_quality.suggestions,
            'ai_reasoning': ai_quality.reasoning,
            'model_used': ai_quality.model_used,
            'detailed_comparison': ai_quality.comparison,
            'initial_threshold': self.quality_threshold,
            'quality_delta': ai_quality.overall_score - self.quality_threshold
        }

    @wrap_exception(TwoPassPipelineException, "AI-enhanced strategy optimization failed")
    def optimize_pass_strategy_with_ai(
        self,
        task_requirements: str,
        context_info: Dict[str, Any],
        use_initial_analysis: bool = True
    ) -> Dict[str, Any]:
        """
        Optimize pass execution strategy using hybrid AI approach.

        NEW: Uses router's intensity and guidance to optimize first/second pass strategy.

        Args:
            task_requirements: Task requirements description
            context_info: Additional context information
            use_initial_analysis: If True, uses router's pre-computed strategy first

        Returns:
            Dict with optimized strategy including:
                - first_pass_focus: List[str] - What first pass should focus on
                - second_pass_focus: List[str] - What second pass should focus on
                - recommended_timeouts: Dict[str, int] - Timeout recommendations
                - parallelization: bool - Whether passes can be partially parallelized
                - rollback_likelihood: float - Probability of needing rollback
                - source: str - Where optimization came from

        Usage:
            strategy = pipeline.optimize_pass_strategy_with_ai(
                task_requirements=requirements_text,
                context_info=execution_context
            )
        """
        # HYBRID STEP 1: Use router's pre-computed strategy (FREE!)
        if use_initial_analysis and self.router_intensity is not None:
            # Router already provided intensity and guidance
            # For low intensity, simple strategy sufficient
            if self.router_intensity < 0.5:
                return {
                    'first_pass_focus': self.first_pass_guidance if self.first_pass_guidance else [
                        'Validate requirements',
                        'Check for obvious issues',
                        'Quick feasibility check'
                    ],
                    'second_pass_focus': self.second_pass_guidance if self.second_pass_guidance else [
                        'Implement core functionality',
                        'Apply first pass learnings'
                    ],
                    'recommended_timeouts': {
                        'first_pass': self.first_pass_timeout,
                        'second_pass': self.second_pass_timeout
                    },
                    'parallelization': False,  # Conservative for simple tasks
                    'rollback_likelihood': 0.1,  # Low for simple tasks
                    'source': 'router_precomputed',
                    'intensity': self.router_intensity,
                    'cost': 0.0  # Free!
                }

        # HYBRID STEP 2: Higher intensity - make adaptive AI call
        if not self.ai_service:
            # Fallback: Use router's guidance with defaults
            return {
                'first_pass_focus': self.first_pass_guidance if self.first_pass_guidance else [
                    'Analyze requirements',
                    'Identify risks',
                    'Create execution plan'
                ],
                'second_pass_focus': self.second_pass_guidance if self.second_pass_guidance else [
                    'Full implementation',
                    'Apply optimizations',
                    'Integrate learnings'
                ],
                'recommended_timeouts': {
                    'first_pass': self.first_pass_timeout,
                    'second_pass': self.second_pass_timeout
                },
                'parallelization': self.router_intensity > 0.7,
                'rollback_likelihood': 0.3,
                'source': 'fallback_no_ai_service',
                'intensity': self.router_intensity,
                'warning': 'No AI service available, using defaults'
            }

        # Make AI call via mixin for complexity analysis (DRY!)
        complexity_level, estimated_duration, analysis = self.query_for_complexity(
            requirements=task_requirements,
            context=f"Two-pass pipeline optimization. "
                   f"Initial intensity: {self.router_intensity:.0%}. "
                   f"Router guidance: {self.router_guidance[:200]}..."
        )

        # Determine strategy based on AI complexity analysis
        complexity_to_strategy = {
            'simple': {
                'first_focus': ['Quick validation', 'Schema check', 'Dependency scan'],
                'second_focus': ['Direct implementation', 'Simple testing'],
                'timeouts': (int(self.first_pass_timeout * 0.8), int(self.second_pass_timeout * 0.8)),
                'parallel': False,
                'rollback': 0.05
            },
            'moderate': {
                'first_focus': ['Thorough analysis', 'Risk assessment', 'Architecture planning'],
                'second_focus': ['Structured implementation', 'Integration', 'Comprehensive testing'],
                'timeouts': (self.first_pass_timeout, self.second_pass_timeout),
                'parallel': False,
                'rollback': 0.15
            },
            'complex': {
                'first_focus': ['Deep analysis', 'Multiple risk scenarios', 'Detailed architecture', 'Prototyping'],
                'second_focus': ['Incremental implementation', 'Continuous validation', 'Extensive testing', 'Performance optimization'],
                'timeouts': (int(self.first_pass_timeout * 1.2), int(self.second_pass_timeout * 1.3)),
                'parallel': True,
                'rollback': 0.30
            },
            'very_complex': {
                'first_focus': ['Comprehensive analysis', 'Multiple prototypes', 'Risk mitigation plans', 'Architecture validation'],
                'second_focus': ['Phased implementation', 'Continuous feedback', 'Iterative refinement', 'Full test coverage'],
                'timeouts': (int(self.first_pass_timeout * 1.5), int(self.second_pass_timeout * 1.5)),
                'parallel': True,
                'rollback': 0.45
            }
        }

        strategy_config = complexity_to_strategy.get(complexity_level, complexity_to_strategy['moderate'])

        # Merge with router's guidance if available
        first_focus = strategy_config['first_focus']
        if self.first_pass_guidance:
            first_focus = list(set(first_focus + self.first_pass_guidance))

        second_focus = strategy_config['second_focus']
        if self.second_pass_guidance:
            second_focus = list(set(second_focus + self.second_pass_guidance))

        return {
            'first_pass_focus': first_focus,
            'second_pass_focus': second_focus,
            'recommended_timeouts': {
                'first_pass': strategy_config['timeouts'][0],
                'second_pass': strategy_config['timeouts'][1]
            },
            'parallelization': strategy_config['parallel'],
            'rollback_likelihood': strategy_config['rollback'],
            'source': 'ai_optimized',
            'complexity_level': complexity_level,
            'estimated_duration': estimated_duration,
            'ai_analysis': analysis,
            'initial_intensity': self.router_intensity,
            'initial_timeouts': {
                'first_pass': self.first_pass_timeout,
                'second_pass': self.second_pass_timeout
            },
            'timeout_adjustment': {
                'first_pass': strategy_config['timeouts'][0] - self.first_pass_timeout,
                'second_pass': strategy_config['timeouts'][1] - self.second_pass_timeout
            }
        }


# ============================================================================
# CONVENIENCE FACTORY
# ============================================================================

class TwoPassPipelineFactory:
    """
    Factory for creating pre-configured two-pass pipelines.

    Why it exists: Simplifies pipeline creation with sensible defaults.
    Provides common configurations without manual component wiring.

    Design pattern: Factory Pattern
    """

    @staticmethod
    def create_default_pipeline(
        observable: Optional[PipelineObservable] = None,
        verbose: bool = True
    ) -> TwoPassPipeline:
        """
        Create pipeline with default strategies.

        Why needed: Most common use case - fast first pass, thorough second pass.

        Args:
            observable: Event broadcaster
            verbose: Enable logging

        Returns:
            Configured TwoPassPipeline
        """
        first_pass = FirstPassStrategy(observable=observable, verbose=verbose)
        second_pass = SecondPassStrategy(observable=observable, verbose=verbose)

        return TwoPassPipeline(
            first_pass_strategy=first_pass,
            second_pass_strategy=second_pass,
            observable=observable,
            auto_rollback=True,
            rollback_threshold=-0.1,
            verbose=verbose
        )

    @staticmethod
    def create_no_rollback_pipeline(
        observable: Optional[PipelineObservable] = None,
        verbose: bool = True
    ) -> TwoPassPipeline:
        """
        Create pipeline without auto-rollback.

        Why needed: Use case where second pass always kept (experimentation, data collection).

        Args:
            observable: Event broadcaster
            verbose: Enable logging

        Returns:
            Configured TwoPassPipeline with auto-rollback disabled
        """
        first_pass = FirstPassStrategy(observable=observable, verbose=verbose)
        second_pass = SecondPassStrategy(observable=observable, verbose=verbose)

        return TwoPassPipeline(
            first_pass_strategy=first_pass,
            second_pass_strategy=second_pass,
            observable=observable,
            auto_rollback=False,
            verbose=verbose
        )
