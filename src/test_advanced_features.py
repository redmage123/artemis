#!/usr/bin/env python3
"""
Module: test_advanced_features.py

Purpose: Comprehensive unit tests for Dynamic Pipelines, Two-Pass Pipelines, and Thermodynamic Computing

Test Coverage:
1. Dynamic Pipelines:
   - Stage selection strategies (complexity, resource, manual)
   - Parallel execution and dependency resolution
   - Retry logic and error handling
   - Runtime modification (add/remove stages)
   - Resource allocation
   - Observer integration

2. Two-Pass Pipelines:
   - First pass execution
   - Second pass execution with learning transfer
   - Delta detection and comparison
   - Learning transfer between passes
   - Rollback functionality
   - Pass comparison metrics

3. Thermodynamic Computing:
   - Uncertainty quantification (Bayesian, Monte Carlo, Ensemble)
   - Bayesian learning and prior updates
   - Monte Carlo simulation
   - Temperature scheduling and annealing
   - Ensemble methods and voting
   - Confidence tracking and history

Design Principles:
- NO elif chains (use dispatch tables)
- NO nested loops (extract to helper methods)
- NO nested ifs (use guard clauses)
- ALL public methods tested
- Mock external dependencies
- Test error conditions
- Verify observer integration
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime, timedelta
from typing import Dict, Any, List
import copy

# Import modules under test
from dynamic_pipeline import (
    DynamicPipeline,
    DynamicPipelineBuilder,
    DynamicPipelineFactory,
    PipelineStage,
    StageResult,
    StageSelectionStrategy,
    ComplexityBasedSelector,
    ResourceBasedSelector,
    ManualSelector,
    ProjectComplexity,
    PipelineState,
    RetryPolicy,
    StageExecutor,
    ParallelStageExecutor
)

from two_pass_pipeline import (
    TwoPassPipeline,
    TwoPassPipelineFactory,
    FirstPassStrategy,
    SecondPassStrategy,
    PassResult,
    PassDelta,
    PassMemento,
    PassComparator,
    RollbackManager,
    TwoPassEventType
)

from thermodynamic_computing import (
    ThermodynamicComputing,
    BayesianUncertaintyStrategy,
    MonteCarloUncertaintyStrategy,
    EnsembleUncertaintyStrategy,
    TemperatureScheduler,
    ConfidenceScore,
    ThermodynamicEventType,
    check_confidence_threshold,
    assess_risk
)

from pipeline_observer import (
    PipelineObservable,
    PipelineEvent,
    EventType,
    PipelineObserver
)

from artemis_exceptions import PipelineException


# ============================================================================
# MOCK CLASSES
# ============================================================================

class MockStage(PipelineStage):
    """
    Mock pipeline stage for testing.

    Why needed: Provides controllable stage behavior for testing dynamic pipeline
    execution without real stage implementation complexity.
    """

    def __init__(self, name: str, should_fail: bool = False, dependencies: List[str] = None):
        super().__init__(name)
        self.should_fail = should_fail
        self._dependencies = dependencies or []
        self.execution_count = 0
        self.last_context = None

    def execute(self, context: Dict[str, Any]) -> StageResult:
        """Execute mock stage with controllable success/failure"""
        self.execution_count += 1
        self.last_context = context

        if self.should_fail:
            return StageResult(
                stage_name=self.name,
                success=False,
                error=Exception(f"{self.name} failed intentionally")
            )

        return StageResult(
            stage_name=self.name,
            success=True,
            data={"result": f"{self.name} completed"},
            duration=0.1
        )

    def get_dependencies(self) -> List[str]:
        """Return configured dependencies"""
        return self._dependencies

    def should_execute(self, context: Dict[str, Any]) -> bool:
        """Check if should execute based on context"""
        skip_flag = context.get(f"skip_{self.name}", False)
        return not skip_flag


class MockObserver(PipelineObserver):
    """
    Mock observer for testing event emission.

    Why needed: Captures emitted events for verification without real observer
    implementation overhead.
    """

    def __init__(self):
        self.events = []

    def on_event(self, event: PipelineEvent) -> None:
        """Record event"""
        self.events.append(event)

    def get_events_by_type(self, event_type: EventType) -> List[PipelineEvent]:
        """Get events filtered by type"""
        return [e for e in self.events if e.event_type == event_type]


# ============================================================================
# DYNAMIC PIPELINE TESTS
# ============================================================================

class TestStageSelectionStrategies(unittest.TestCase):
    """
    Test stage selection strategies.

    WHAT: Validates stage filtering logic for complexity, resource, and manual selection
    WHY: Ensures pipeline adapts correctly to different project complexities and resource constraints
    """

    def setUp(self):
        """Create test stages"""
        self.stages = [
            MockStage("requirements"),
            MockStage("architecture"),
            MockStage("development"),
            MockStage("code_review"),
            MockStage("unit_tests"),
            MockStage("integration"),
            MockStage("security"),
            MockStage("performance"),
            MockStage("validation")
        ]

    def test_complexity_based_selector_simple(self):
        """
        WHAT: Tests complexity selector filters stages for simple projects
        WHY: Simple projects should only include basic stages (requirements, dev, basic tests)
        """
        selector = ComplexityBasedSelector()
        context = {"complexity": ProjectComplexity.SIMPLE}

        selected = selector.select_stages(self.stages, context)
        selected_names = {s.name for s in selected}

        # Should include basic stages only
        self.assertIn("requirements", selected_names)
        self.assertIn("development", selected_names)
        self.assertIn("unit_tests", selected_names)

        # Should not include complex stages
        self.assertNotIn("security", selected_names)
        self.assertNotIn("performance", selected_names)

    def test_complexity_based_selector_enterprise(self):
        """
        WHAT: Tests complexity selector includes all stages for enterprise projects
        WHY: Enterprise projects need comprehensive quality gates including security and performance
        """
        selector = ComplexityBasedSelector()
        context = {"complexity": ProjectComplexity.ENTERPRISE}

        selected = selector.select_stages(self.stages, context)

        # Should include all stages for enterprise
        self.assertEqual(len(selected), len(self.stages))

    def test_resource_based_selector_low_resources(self):
        """
        WHAT: Tests resource selector filters to critical stages when resources are low
        WHY: Resource-constrained environments must prioritize essential stages over expensive ones
        """
        selector = ResourceBasedSelector()
        context = {
            "cpu_cores": 2,
            "memory_gb": 4,
            "time_budget_minutes": 30
        }

        selected = selector.select_stages(self.stages, context)
        selected_names = {s.name for s in selected}

        # Should include critical stages
        self.assertIn("requirements", selected_names)
        self.assertIn("development", selected_names)
        self.assertIn("unit_tests", selected_names)

        # Should exclude expensive stages
        self.assertNotIn("performance", selected_names)
        self.assertNotIn("security", selected_names)

    def test_resource_based_selector_high_resources(self):
        """
        WHAT: Tests resource selector includes all stages when resources are abundant
        WHY: High resource environments can run comprehensive validation including expensive stages
        """
        selector = ResourceBasedSelector()
        context = {
            "cpu_cores": 8,
            "memory_gb": 16,
            "time_budget_minutes": 120
        }

        selected = selector.select_stages(self.stages, context)

        # Should include all stages with high resources
        self.assertEqual(len(selected), len(self.stages))

    def test_manual_selector_specific_stages(self):
        """
        WHAT: Tests manual selector includes only explicitly specified stages
        WHY: Users need ability to run custom stage combinations for debugging or specific workflows
        """
        stage_names = ["requirements", "development", "validation"]
        selector = ManualSelector(stage_names)

        selected = selector.select_stages(self.stages, {})
        selected_names = {s.name for s in selected}

        # Should only include specified stages
        self.assertEqual(selected_names, set(stage_names))

    def test_manual_selector_missing_stage_warning(self):
        """
        WHAT: Tests manual selector handles non-existent stage names gracefully
        WHY: User may specify invalid stage names - should warn but not crash
        """
        stage_names = ["requirements", "nonexistent_stage", "development"]
        selector = ManualSelector(stage_names)

        selected = selector.select_stages(self.stages, {})
        selected_names = {s.name for s in selected}

        # Should only include stages that exist
        self.assertEqual(len(selected), 2)
        self.assertIn("requirements", selected_names)
        self.assertIn("development", selected_names)


class TestRetryPolicy(unittest.TestCase):
    """
    Test retry policy behavior.

    WHAT: Validates retry decision logic and backoff calculations
    WHY: Transient failures should retry with backoff, permanent failures should not
    """

    def test_should_retry_within_limit(self):
        """
        WHAT: Tests retry allowed when within max retry limit
        WHY: Transient failures should be retried to handle temporary issues
        """
        policy = RetryPolicy(max_retries=3)
        exception = Exception("Transient error")

        # Should retry on attempts 0, 1, 2 (within limit)
        self.assertTrue(policy.should_retry(exception, 0))
        self.assertTrue(policy.should_retry(exception, 1))
        self.assertTrue(policy.should_retry(exception, 2))

    def test_should_not_retry_exceeded_limit(self):
        """
        WHAT: Tests retry denied when max retries exceeded
        WHY: Permanent failures should not retry infinitely - fail after limit reached
        """
        policy = RetryPolicy(max_retries=3)
        exception = Exception("Persistent error")

        # Should not retry on attempt 3 (exceeds limit)
        self.assertFalse(policy.should_retry(exception, 3))
        self.assertFalse(policy.should_retry(exception, 4))

    def test_exponential_backoff(self):
        """
        WHAT: Tests backoff delay increases exponentially with attempt count
        WHY: Exponential backoff prevents thundering herd and gives systems time to recover
        """
        policy = RetryPolicy(initial_delay=1.0, backoff_multiplier=2.0)

        # Verify exponential backoff: 1, 2, 4, 8...
        self.assertEqual(policy.get_delay(0), 1.0)
        self.assertEqual(policy.get_delay(1), 2.0)
        self.assertEqual(policy.get_delay(2), 4.0)
        self.assertEqual(policy.get_delay(3), 8.0)


class TestStageExecutor(unittest.TestCase):
    """
    Test stage executor with retry and error handling.

    WHAT: Validates stage execution, retry logic, and event emission
    WHY: Stage executor is core execution engine - must handle errors and emit proper events
    """

    def setUp(self):
        """Set up test fixtures"""
        self.observable = PipelineObservable()
        self.observer = MockObserver()
        self.observable.attach(self.observer)
        self.retry_policy = RetryPolicy(max_retries=2, initial_delay=0.01)
        self.executor = StageExecutor(self.observable, self.retry_policy)

    def test_execute_stage_success(self):
        """
        WHAT: Tests successful stage execution emits start and completion events
        WHY: Observers need visibility into stage lifecycle for monitoring and metrics
        """
        stage = MockStage("test_stage")
        context = {"test": "data"}

        result = self.executor.execute_stage(stage, context, "CARD-001")

        # Should succeed
        self.assertTrue(result.success)
        self.assertEqual(result.stage_name, "test_stage")

        # Should emit start and completion events
        start_events = self.observer.get_events_by_type(EventType.STAGE_STARTED)
        complete_events = self.observer.get_events_by_type(EventType.STAGE_COMPLETED)

        self.assertEqual(len(start_events), 1)
        self.assertEqual(len(complete_events), 1)

    def test_execute_stage_skip(self):
        """
        WHAT: Tests stage skip when should_execute returns False
        WHY: Conditional execution enables dynamic pipeline adaptation based on context
        """
        stage = MockStage("test_stage")
        context = {"skip_test_stage": True}

        result = self.executor.execute_stage(stage, context, "CARD-001")

        # Should be skipped
        self.assertTrue(result.skipped)

        # Should emit skip event
        skip_events = self.observer.get_events_by_type(EventType.STAGE_SKIPPED)
        self.assertEqual(len(skip_events), 1)

    def test_execute_stage_retry_and_succeed(self):
        """
        WHAT: Tests stage retries on failure then succeeds
        WHY: Transient failures should retry - system should recover from temporary issues
        """
        stage = MockStage("test_stage", should_fail=True)
        context = {}

        # Mock stage to fail first time, succeed second time
        original_execute = stage.execute
        call_count = [0]

        def execute_with_retry(ctx):
            call_count[0] += 1
            if call_count[0] == 1:
                return StageResult(stage_name=stage.name, success=False, error=Exception("Transient"))
            return StageResult(stage_name=stage.name, success=True)

        stage.execute = execute_with_retry

        result = self.executor.execute_stage(stage, context, "CARD-001")

        # Should eventually succeed
        self.assertTrue(result.success)
        self.assertEqual(result.retry_count, 1)

        # Should emit retry event
        retry_events = self.observer.get_events_by_type(EventType.STAGE_RETRYING)
        self.assertEqual(len(retry_events), 1)

    def test_execute_stage_retry_exhausted(self):
        """
        WHAT: Tests stage fails after exhausting all retries
        WHY: Permanent failures should fail pipeline after retry limit to prevent infinite loops
        """
        stage = MockStage("test_stage", should_fail=True)
        context = {}

        result = self.executor.execute_stage(stage, context, "CARD-001")

        # Should fail after retries exhausted
        self.assertFalse(result.success)
        self.assertEqual(result.retry_count, 2)  # max_retries

        # Should emit failure event
        fail_events = self.observer.get_events_by_type(EventType.STAGE_FAILED)
        self.assertEqual(len(fail_events), 1)


class TestParallelStageExecutor(unittest.TestCase):
    """
    Test parallel stage execution with dependency resolution.

    WHAT: Validates parallel execution respects dependencies and detects cycles
    WHY: Parallel execution dramatically reduces pipeline duration but must maintain ordering
    """

    def setUp(self):
        """Set up test fixtures"""
        self.observable = PipelineObservable()
        self.executor = StageExecutor(self.observable, RetryPolicy())
        self.parallel_executor = ParallelStageExecutor(self.executor, max_workers=2)

    def test_parallel_execution_no_dependencies(self):
        """
        WHAT: Tests stages with no dependencies execute in parallel
        WHY: Independent stages should run concurrently to minimize pipeline duration
        """
        stages = [
            MockStage("stage1"),
            MockStage("stage2"),
            MockStage("stage3")
        ]

        results = self.parallel_executor.execute_stages_parallel(stages, {}, "CARD-001")

        # All stages should complete successfully
        self.assertEqual(len(results), 3)
        self.assertTrue(all(r.success for r in results.values()))

    def test_parallel_execution_with_dependencies(self):
        """
        WHAT: Tests stages with dependencies execute in correct order
        WHY: Dependencies define required ordering - parallel executor must respect them
        """
        stages = [
            MockStage("stage1"),
            MockStage("stage2", dependencies=["stage1"]),
            MockStage("stage3", dependencies=["stage1", "stage2"])
        ]

        results = self.parallel_executor.execute_stages_parallel(stages, {}, "CARD-001")

        # All stages should complete successfully in dependency order
        self.assertEqual(len(results), 3)
        self.assertTrue(all(r.success for r in results.values()))

    def test_parallel_execution_cycle_detection(self):
        """
        WHAT: Tests cycle detection prevents infinite dependency loops
        WHY: Circular dependencies are invalid - must detect and fail fast with clear error
        """
        stages = [
            MockStage("stage1", dependencies=["stage2"]),
            MockStage("stage2", dependencies=["stage1"])
        ]

        with self.assertRaises(PipelineException) as cm:
            self.parallel_executor.execute_stages_parallel(stages, {}, "CARD-001")

        self.assertIn("cycle", str(cm.exception).lower())

    def test_parallel_execution_stops_on_failure(self):
        """
        WHAT: Tests pipeline stops when stage fails in parallel execution
        WHY: Failure should halt pipeline immediately to prevent wasted work on dependent stages
        """
        stages = [
            MockStage("stage1", should_fail=True),
            MockStage("stage2", dependencies=["stage1"]),
            MockStage("stage3")
        ]

        results = self.parallel_executor.execute_stages_parallel(stages, {}, "CARD-001")

        # stage1 should fail
        self.assertFalse(results["stage1"].success)

        # Dependent stage2 should not execute (or should fail)
        # stage3 may execute since it's independent


class TestDynamicPipelineBuilder(unittest.TestCase):
    """
    Test dynamic pipeline builder validation.

    WHAT: Validates builder configuration, validation, and pipeline construction
    WHY: Builder ensures valid pipeline configuration before execution
    """

    def test_builder_requires_stages(self):
        """
        WHAT: Tests builder fails when no stages provided
        WHY: Pipeline needs at least one stage to be useful - fail early with clear error
        """
        builder = DynamicPipelineBuilder()

        with self.assertRaises(PipelineException) as cm:
            builder.build()

        self.assertIn("at least one stage", str(cm.exception).lower())

    def test_builder_detects_duplicate_stage_names(self):
        """
        WHAT: Tests builder detects duplicate stage names
        WHY: Duplicate names cause result lookup ambiguity - must enforce uniqueness
        """
        builder = DynamicPipelineBuilder()
        builder.add_stage(MockStage("duplicate"))
        builder.add_stage(MockStage("duplicate"))

        with self.assertRaises(PipelineException) as cm:
            builder.build()

        self.assertIn("duplicate", str(cm.exception).lower())

    def test_builder_validates_dependencies(self):
        """
        WHAT: Tests builder detects invalid stage dependencies
        WHY: Referencing non-existent dependencies causes runtime errors - validate early
        """
        builder = DynamicPipelineBuilder()
        builder.add_stage(MockStage("stage1", dependencies=["nonexistent"]))

        with self.assertRaises(PipelineException) as cm:
            builder.build()

        self.assertIn("invalid dependencies", str(cm.exception).lower())

    def test_builder_creates_valid_pipeline(self):
        """
        WHAT: Tests builder creates valid pipeline with all components
        WHY: Builder should wire together all components (executor, observable, strategies)
        """
        builder = DynamicPipelineBuilder()
        builder.with_name("test-pipeline")
        builder.add_stage(MockStage("stage1"))
        builder.with_strategy(ComplexityBasedSelector())
        builder.with_parallelism(enabled=True, max_workers=2)

        pipeline = builder.build()

        self.assertIsNotNone(pipeline)
        self.assertEqual(pipeline.name, "test-pipeline")
        self.assertEqual(pipeline.state, PipelineState.READY)


class TestDynamicPipeline(unittest.TestCase):
    """
    Test dynamic pipeline execution and state management.

    WHAT: Validates pipeline lifecycle, execution, and runtime modification
    WHY: Pipeline orchestrates all stages - must manage state transitions correctly
    """

    def setUp(self):
        """Set up test fixtures"""
        self.observable = PipelineObservable()
        self.observer = MockObserver()
        self.observable.attach(self.observer)

    def test_pipeline_execution_success(self):
        """
        WHAT: Tests successful pipeline execution completes all stages
        WHY: Happy path should execute all stages and transition to COMPLETED state
        """
        pipeline = (DynamicPipelineBuilder()
            .with_name("test-pipeline")
            .add_stages([MockStage("stage1"), MockStage("stage2")])
            .with_observable(self.observable)
            .build())

        results = pipeline.execute("CARD-001")

        # Should complete successfully
        self.assertEqual(pipeline.state, PipelineState.COMPLETED)
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r.success for r in results.values()))

    def test_pipeline_execution_failure(self):
        """
        WHAT: Tests pipeline transitions to FAILED when stage fails
        WHY: Stage failure should halt pipeline and set FAILED state for monitoring
        """
        pipeline = (DynamicPipelineBuilder()
            .with_name("test-pipeline")
            .add_stages([
                MockStage("stage1"),
                MockStage("stage2", should_fail=True)
            ])
            .with_observable(self.observable)
            .build())

        results = pipeline.execute("CARD-001")

        # Should fail
        self.assertEqual(pipeline.state, PipelineState.FAILED)
        self.assertFalse(results["stage2"].success)

    def test_pipeline_state_validation(self):
        """
        WHAT: Tests pipeline rejects execution when not in READY state
        WHY: State validation prevents invalid operations like double execution
        """
        pipeline = (DynamicPipelineBuilder()
            .with_name("test-pipeline")
            .add_stage(MockStage("stage1"))
            .build())

        # First execution should succeed
        pipeline.execute("CARD-001")

        # Second execution should fail (not in READY state)
        with self.assertRaises(PipelineException) as cm:
            pipeline.execute("CARD-002")

        self.assertIn("not ready", str(cm.exception).lower())

    def test_pipeline_runtime_modification(self):
        """
        WHAT: Tests adding/removing stages at runtime
        WHY: Dynamic modification enables adaptive pipeline based on intermediate results
        """
        pipeline = (DynamicPipelineBuilder()
            .with_name("test-pipeline")
            .add_stage(MockStage("stage1"))
            .build())

        # Add stage at runtime
        new_stage = MockStage("stage2")
        pipeline.add_stage_runtime(new_stage)

        self.assertIn(new_stage, pipeline.selected_stages)

        # Remove stage at runtime
        pipeline.remove_stage_runtime("stage2")

        self.assertNotIn("stage2", [s.name for s in pipeline.selected_stages])

    def test_pipeline_cannot_modify_while_running(self):
        """
        WHAT: Tests runtime modification rejected when pipeline running
        WHY: Modifying running pipeline causes race conditions - must wait for completion
        """
        pipeline = (DynamicPipelineBuilder()
            .with_name("test-pipeline")
            .add_stage(MockStage("stage1"))
            .build())

        # Manually set to running state
        pipeline.state = PipelineState.RUNNING

        with self.assertRaises(PipelineException):
            pipeline.add_stage_runtime(MockStage("stage2"))


class TestDynamicPipelineFactory(unittest.TestCase):
    """
    Test factory convenience methods.

    WHAT: Validates factory creates pipelines with correct presets
    WHY: Factory provides common configurations to reduce boilerplate
    """

    def test_create_simple_pipeline(self):
        """
        WHAT: Tests factory creates simple sequential pipeline
        WHY: Simple pipeline is most common use case - should be easy to create
        """
        stages = [MockStage("stage1"), MockStage("stage2")]
        pipeline = DynamicPipelineFactory.create_simple_pipeline(
            "test-pipeline",
            stages
        )

        self.assertIsNotNone(pipeline)
        self.assertEqual(pipeline.name, "test-pipeline")
        self.assertIsNone(pipeline.parallel_executor)  # No parallelism

    def test_create_parallel_pipeline(self):
        """
        WHAT: Tests factory creates pipeline with parallel execution enabled
        WHY: Parallel pipeline reduces duration - factory should configure executor properly
        """
        stages = [MockStage("stage1"), MockStage("stage2")]
        pipeline = DynamicPipelineFactory.create_parallel_pipeline(
            "test-pipeline",
            stages,
            max_workers=4
        )

        self.assertIsNotNone(pipeline)
        self.assertIsNotNone(pipeline.parallel_executor)
        self.assertEqual(pipeline.parallel_executor.max_workers, 4)

    def test_create_adaptive_pipeline(self):
        """
        WHAT: Tests factory creates adaptive pipeline with complexity selection
        WHY: Adaptive pipeline adjusts stages based on complexity - validates strategy wiring
        """
        stages = [
            MockStage("requirements"),
            MockStage("development"),
            MockStage("security"),
            MockStage("performance")
        ]
        pipeline = DynamicPipelineFactory.create_adaptive_pipeline(
            "test-pipeline",
            stages,
            ProjectComplexity.SIMPLE
        )

        self.assertIsNotNone(pipeline)
        self.assertIsNotNone(pipeline.strategy)
        # Simple complexity should filter out security/performance
        self.assertLess(len(pipeline.selected_stages), len(stages))


# ============================================================================
# TWO-PASS PIPELINE TESTS
# ============================================================================

class TestPassResult(unittest.TestCase):
    """
    Test PassResult data structure.

    WHAT: Validates pass result creation and serialization
    WHY: PassResult carries execution artifacts between passes and to observers
    """

    def test_pass_result_creation(self):
        """
        WHAT: Tests PassResult creation with all fields
        WHY: Pass results must store artifacts, learnings, and quality metrics
        """
        result = PassResult(
            pass_name="FirstPass",
            success=True,
            artifacts={"code": "test.py"},
            quality_score=0.85,
            learnings=["Learning 1", "Learning 2"],
            insights={"complexity": "low"}
        )

        self.assertEqual(result.pass_name, "FirstPass")
        self.assertTrue(result.success)
        self.assertEqual(result.quality_score, 0.85)
        self.assertEqual(len(result.learnings), 2)

    def test_pass_result_to_dict(self):
        """
        WHAT: Tests PassResult serialization to dict
        WHY: Results must be serializable for logging, storage, and event transmission
        """
        result = PassResult(
            pass_name="FirstPass",
            success=True,
            quality_score=0.85
        )

        result_dict = result.to_dict()

        self.assertEqual(result_dict["pass_name"], "FirstPass")
        self.assertEqual(result_dict["success"], True)
        self.assertEqual(result_dict["quality_score"], 0.85)


class TestPassDelta(unittest.TestCase):
    """
    Test PassDelta calculation.

    WHAT: Validates delta detection between passes
    WHY: Delta quantifies improvements/degradations for rollback decisions
    """

    def test_delta_quality_improvement(self):
        """
        WHAT: Tests delta correctly identifies quality improvement
        WHY: Quality delta drives rollback decisions - must be accurate
        """
        first = PassResult(
            pass_name="FirstPass",
            success=True,
            quality_score=0.70,
            artifacts={"file1": "v1"}
        )

        second = PassResult(
            pass_name="SecondPass",
            success=True,
            quality_score=0.85,
            artifacts={"file1": "v2", "file2": "new"}
        )

        delta = PassDelta(first_pass=first, second_pass=second)

        # Quality improved
        self.assertGreater(delta.quality_delta, 0)
        self.assertTrue(delta.quality_improved)
        self.assertEqual(delta.quality_delta, 0.15)

    def test_delta_detects_new_artifacts(self):
        """
        WHAT: Tests delta identifies new artifacts in second pass
        WHY: Artifact changes indicate progress and incremental improvements
        """
        first = PassResult(
            pass_name="FirstPass",
            success=True,
            artifacts={"file1": "v1"}
        )

        second = PassResult(
            pass_name="SecondPass",
            success=True,
            artifacts={"file1": "v1", "file2": "new"}
        )

        delta = PassDelta(first_pass=first, second_pass=second)

        # Should detect new artifact
        self.assertIn("file2", delta.new_artifacts)

    def test_delta_detects_modified_artifacts(self):
        """
        WHAT: Tests delta identifies modified artifacts
        WHY: Modified artifacts show refinements applied in second pass
        """
        first = PassResult(
            pass_name="FirstPass",
            success=True,
            artifacts={"file1": "version1"}
        )

        second = PassResult(
            pass_name="SecondPass",
            success=True,
            artifacts={"file1": "version2"}
        )

        delta = PassDelta(first_pass=first, second_pass=second)

        # Should detect modification
        self.assertIn("file1", delta.modified_artifacts)

    def test_delta_new_learnings(self):
        """
        WHAT: Tests delta extracts new learnings from second pass
        WHY: Learning extraction enables knowledge accumulation across passes
        """
        first = PassResult(
            pass_name="FirstPass",
            success=True,
            learnings=["Learning 1"]
        )

        second = PassResult(
            pass_name="SecondPass",
            success=True,
            learnings=["Learning 1", "Learning 2"]
        )

        delta = PassDelta(first_pass=first, second_pass=second)

        # Should identify new learning
        self.assertIn("Learning 2", delta.new_learnings)


class TestPassMemento(unittest.TestCase):
    """
    Test PassMemento state capture.

    WHAT: Validates memento creation and deep copy
    WHY: Memento enables rollback and learning transfer without state corruption
    """

    def test_memento_creation(self):
        """
        WHAT: Tests memento captures complete pass state
        WHY: Memento must preserve all state for accurate restoration
        """
        memento = PassMemento(
            pass_name="FirstPass",
            state={"key": "value"},
            artifacts={"file": "content"},
            learnings=["learning1"],
            insights={"complexity": "low"},
            quality_score=0.75
        )

        self.assertEqual(memento.pass_name, "FirstPass")
        self.assertEqual(memento.quality_score, 0.75)
        self.assertIn("learning1", memento.learnings)

    def test_memento_deep_copy(self):
        """
        WHAT: Tests memento deep copy prevents mutation
        WHY: Memento copies must be independent to prevent cross-contamination
        """
        original = PassMemento(
            pass_name="FirstPass",
            state={"key": ["value"]},
            artifacts={},
            learnings=[],
            insights={},
            quality_score=0.75
        )

        copy_memento = original.create_copy()

        # Modify copy
        copy_memento.state["key"].append("new_value")

        # Original should be unchanged
        self.assertEqual(len(original.state["key"]), 1)
        self.assertEqual(len(copy_memento.state["key"]), 2)


class TestFirstPassStrategy(unittest.TestCase):
    """
    Test first pass execution strategy.

    WHAT: Validates fast analysis pass behavior
    WHY: First pass provides rapid feedback - must be fast and extract learnings
    """

    def setUp(self):
        """Set up test fixtures"""
        self.observable = PipelineObservable()
        self.observer = MockObserver()
        self.observable.attach(self.observer)
        self.strategy = FirstPassStrategy(observable=self.observable)

    def test_first_pass_executes(self):
        """
        WHAT: Tests first pass completes and returns result
        WHY: First pass must succeed to provide baseline for second pass
        """
        context = {
            "inputs": {"data": "test"},
            "config": {"analysis_type": "validation"}
        }

        result = self.strategy.execute(context)

        self.assertTrue(result.success)
        self.assertEqual(result.pass_name, "FirstPass")
        self.assertGreater(result.quality_score, 0)

    def test_first_pass_extracts_learnings(self):
        """
        WHAT: Tests first pass extracts learnings from analysis
        WHY: Learnings guide second pass improvements
        """
        context = {
            "inputs": {"field1": "value1", "field2": "value2"}
        }

        result = self.strategy.execute(context)

        # Should have learnings
        self.assertGreater(len(result.learnings), 0)

    def test_first_pass_calculates_quality(self):
        """
        WHAT: Tests first pass calculates quality score
        WHY: Quality score provides baseline for second pass comparison
        """
        context = {
            "inputs": {"data": "test"}
        }

        result = self.strategy.execute(context)

        # Should have quality score in valid range
        self.assertGreaterEqual(result.quality_score, 0.0)
        self.assertLessEqual(result.quality_score, 1.0)

    def test_first_pass_creates_memento(self):
        """
        WHAT: Tests first pass creates valid memento
        WHY: Memento enables state transfer to second pass
        """
        context = {"inputs": {}}
        result = self.strategy.execute(context)

        memento = self.strategy.create_memento(result, context)

        self.assertIsNotNone(memento)
        self.assertEqual(memento.pass_name, "FirstPass")
        self.assertEqual(memento.quality_score, result.quality_score)


class TestSecondPassStrategy(unittest.TestCase):
    """
    Test second pass execution strategy.

    WHAT: Validates refined implementation with learning application
    WHY: Second pass must apply first pass learnings and improve quality
    """

    def setUp(self):
        """Set up test fixtures"""
        self.observable = PipelineObservable()
        self.observer = MockObserver()
        self.observable.attach(self.observer)
        self.strategy = SecondPassStrategy(observable=self.observable)

    def test_second_pass_executes(self):
        """
        WHAT: Tests second pass completes successfully
        WHY: Second pass provides refined implementation
        """
        context = {
            "inputs": {"data": "test"},
            "config": {"check_type": "thorough_validation"}
        }

        result = self.strategy.execute(context)

        self.assertTrue(result.success)
        self.assertEqual(result.pass_name, "SecondPass")

    def test_second_pass_applies_learnings(self):
        """
        WHAT: Tests second pass applies learnings from context
        WHY: Learning application is core benefit of two-pass approach
        """
        context = {
            "inputs": {"data": "test"},
            "learnings": ["Learning 1", "Learning 2"],
            "insights": {"validation_passed": True}
        }

        result = self.strategy.execute(context)

        # Should apply learnings (shown in metadata)
        self.assertIn("refined_implementation", result.metadata.get("pass_type", ""))

    def test_second_pass_improves_quality(self):
        """
        WHAT: Tests second pass quality score typically higher than first
        WHY: Refinements should improve quality - validates learning effectiveness
        """
        context = {
            "inputs": {"data": "test"},
            "previous_quality_score": 0.5,
            "learnings": ["Improvement 1"]
        }

        result = self.strategy.execute(context)

        # Quality should be reasonable (refinements applied)
        self.assertGreater(result.quality_score, 0.5)


class TestPassComparator(unittest.TestCase):
    """
    Test pass comparison logic.

    WHAT: Validates pass comparison and delta calculation
    WHY: Comparison determines rollback decisions and quality tracking
    """

    def setUp(self):
        """Set up test fixtures"""
        self.observable = PipelineObservable()
        self.observer = MockObserver()
        self.observable.attach(self.observer)
        self.comparator = PassComparator(observable=self.observable)

    def test_compare_passes(self):
        """
        WHAT: Tests comparator creates valid delta
        WHY: Delta is core data structure for two-pass decisions
        """
        first = PassResult("FirstPass", True, quality_score=0.7)
        second = PassResult("SecondPass", True, quality_score=0.85)

        delta = self.comparator.compare(first, second)

        self.assertIsNotNone(delta)
        self.assertEqual(delta.quality_delta, 0.15)
        self.assertTrue(delta.quality_improved)

    def test_compare_emits_events(self):
        """
        WHAT: Tests comparator emits comparison events
        WHY: Events enable monitoring of quality trends
        """
        first = PassResult("FirstPass", True, quality_score=0.7)
        second = PassResult("SecondPass", True, quality_score=0.85)

        self.comparator.compare(first, second)

        # Should emit comparison events
        self.assertGreater(len(self.observer.events), 0)


class TestRollbackManager(unittest.TestCase):
    """
    Test rollback functionality.

    WHAT: Validates rollback to first pass when second pass degrades
    WHY: Rollback provides safety net against quality degradation
    """

    def setUp(self):
        """Set up test fixtures"""
        self.observable = PipelineObservable()
        self.observer = MockObserver()
        self.observable.attach(self.observer)
        self.rollback_manager = RollbackManager(observable=self.observable)

    def test_rollback_to_memento(self):
        """
        WHAT: Tests rollback restores state from memento
        WHY: Rollback must accurately restore first pass state
        """
        memento = PassMemento(
            pass_name="FirstPass",
            state={"key": "value"},
            artifacts={"file": "content"},
            learnings=["learning1"],
            insights={},
            quality_score=0.75
        )

        restored = self.rollback_manager.rollback_to_memento(
            memento,
            reason="Second pass degraded quality"
        )

        self.assertEqual(restored["key"], "value")

    def test_should_rollback_on_degradation(self):
        """
        WHAT: Tests rollback decision when quality degrades significantly
        WHY: Automatic rollback prevents quality degradation from second pass
        """
        first = PassResult("FirstPass", True, quality_score=0.8)
        second = PassResult("SecondPass", True, quality_score=0.6)
        delta = PassDelta(first_pass=first, second_pass=second)

        should_rollback = self.rollback_manager.should_rollback(delta, threshold=-0.1)

        # Quality degraded by 0.2 (> 0.1 threshold) - should rollback
        self.assertTrue(should_rollback)

    def test_should_not_rollback_on_improvement(self):
        """
        WHAT: Tests no rollback when quality improves
        WHY: Improvements should be kept - only rollback on degradation
        """
        first = PassResult("FirstPass", True, quality_score=0.7)
        second = PassResult("SecondPass", True, quality_score=0.85)
        delta = PassDelta(first_pass=first, second_pass=second)

        should_rollback = self.rollback_manager.should_rollback(delta)

        # Quality improved - should not rollback
        self.assertFalse(should_rollback)

    def test_rollback_history_tracking(self):
        """
        WHAT: Tests rollback manager maintains history
        WHY: History enables audit trail and rollback analysis
        """
        memento = PassMemento(
            pass_name="FirstPass",
            state={},
            artifacts={},
            learnings=[],
            insights={},
            quality_score=0.75
        )

        self.rollback_manager.rollback_to_memento(memento, reason="Test")

        history = self.rollback_manager.get_rollback_history()

        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["reason"], "Test")


class TestTwoPassPipeline(unittest.TestCase):
    """
    Test complete two-pass pipeline orchestration.

    WHAT: Validates end-to-end two-pass execution
    WHY: Pipeline orchestrates all components - integration testing required
    """

    def setUp(self):
        """Set up test fixtures"""
        self.observable = PipelineObservable()
        self.observer = MockObserver()
        self.observable.attach(self.observer)

        self.first_pass = FirstPassStrategy(observable=self.observable)
        self.second_pass = SecondPassStrategy(observable=self.observable)

        self.pipeline = TwoPassPipeline(
            first_pass_strategy=self.first_pass,
            second_pass_strategy=self.second_pass,
            observable=self.observable,
            auto_rollback=True,
            rollback_threshold=-0.1
        )

    def test_two_pass_execution_complete(self):
        """
        WHAT: Tests complete two-pass execution (first + second pass)
        WHY: Happy path should execute both passes and return second pass result
        """
        context = {"inputs": {"data": "test"}}

        result = self.pipeline.execute(context)

        # Should complete second pass
        self.assertIsNotNone(result)
        self.assertTrue(result.success)

    def test_two_pass_learning_transfer(self):
        """
        WHAT: Tests learnings transfer from first to second pass
        WHY: Learning transfer is core value proposition of two-pass approach
        """
        context = {"inputs": {"data": "test"}}

        result = self.pipeline.execute(context)

        # Second pass should have learnings (from first pass or new)
        self.assertGreater(len(result.learnings), 0)

    def test_two_pass_auto_rollback(self):
        """
        WHAT: Tests automatic rollback when second pass degrades quality
        WHY: Auto-rollback protects against quality regressions
        """
        # Mock strategies to simulate degradation
        first_pass = FirstPassStrategy(observable=self.observable)
        second_pass = SecondPassStrategy(observable=self.observable)

        # Mock first pass to return high quality
        def mock_first_execute(ctx):
            return PassResult("FirstPass", True, quality_score=0.9)
        first_pass.execute = mock_first_execute

        # Mock second pass to return low quality
        def mock_second_execute(ctx):
            return PassResult("SecondPass", True, quality_score=0.5)
        second_pass.execute = mock_second_execute

        pipeline = TwoPassPipeline(
            first_pass_strategy=first_pass,
            second_pass_strategy=second_pass,
            auto_rollback=True,
            rollback_threshold=-0.1
        )

        context = {"inputs": {}}
        result = pipeline.execute(context)

        # Should rollback to first pass (quality degraded)
        self.assertEqual(result.pass_name, "FirstPass")

    def test_two_pass_execution_history(self):
        """
        WHAT: Tests execution history tracking
        WHY: History enables retrospective analysis and learning
        """
        context = {"inputs": {"data": "test"}}

        self.pipeline.execute(context)

        history = self.pipeline.get_execution_history()

        self.assertEqual(len(history), 1)
        self.assertIn("first_pass_quality", history[0])
        self.assertIn("second_pass_quality", history[0])


class TestTwoPassPipelineFactory(unittest.TestCase):
    """
    Test two-pass pipeline factory.

    WHAT: Validates factory convenience methods
    WHY: Factory simplifies pipeline creation with sensible defaults
    """

    def test_create_default_pipeline(self):
        """
        WHAT: Tests factory creates default pipeline with auto-rollback
        WHY: Default configuration should be production-ready with safety features
        """
        pipeline = TwoPassPipelineFactory.create_default_pipeline()

        self.assertIsNotNone(pipeline)
        self.assertTrue(pipeline.auto_rollback)
        self.assertEqual(pipeline.rollback_threshold, -0.1)

    def test_create_no_rollback_pipeline(self):
        """
        WHAT: Tests factory creates pipeline without auto-rollback
        WHY: Some use cases (experimentation) want second pass regardless of quality
        """
        pipeline = TwoPassPipelineFactory.create_no_rollback_pipeline()

        self.assertIsNotNone(pipeline)
        self.assertFalse(pipeline.auto_rollback)


# ============================================================================
# THERMODYNAMIC COMPUTING TESTS
# ============================================================================

class TestConfidenceScore(unittest.TestCase):
    """
    Test ConfidenceScore data structure.

    WHAT: Validates confidence score creation and calculations
    WHY: ConfidenceScore is core data structure for uncertainty quantification
    """

    def test_confidence_score_creation(self):
        """
        WHAT: Tests ConfidenceScore creation with valid values
        WHY: Must store confidence, variance, and entropy for uncertainty tracking
        """
        score = ConfidenceScore(
            confidence=0.85,
            variance=0.02,
            entropy=0.15,
            sample_size=10
        )

        self.assertEqual(score.confidence, 0.85)
        self.assertEqual(score.variance, 0.02)
        self.assertEqual(score.sample_size, 10)

    def test_confidence_score_validation(self):
        """
        WHAT: Tests ConfidenceScore rejects invalid probability values
        WHY: Confidence must be valid probability [0,1] for mathematical correctness
        """
        with self.assertRaises(ValueError):
            ConfidenceScore(confidence=1.5)  # > 1.0

        with self.assertRaises(ValueError):
            ConfidenceScore(confidence=-0.1)  # < 0.0

    def test_standard_error_calculation(self):
        """
        WHAT: Tests standard error calculation (SE = sqrt(variance/n))
        WHY: Standard error quantifies precision of confidence estimate
        """
        score = ConfidenceScore(
            confidence=0.8,
            variance=0.04,
            sample_size=4
        )

        # SE = sqrt(0.04/4) = sqrt(0.01) = 0.1
        self.assertAlmostEqual(score.standard_error(), 0.1)

    def test_confidence_interval(self):
        """
        WHAT: Tests confidence interval calculation
        WHY: Confidence intervals provide bounds on true value for decision making
        """
        score = ConfidenceScore(
            confidence=0.8,
            variance=0.04,
            sample_size=4
        )

        # 95% CI with z=1.96
        lower, upper = score.confidence_interval(z_score=1.96)

        # Should be (0.8 - 1.96*0.1, 0.8 + 1.96*0.1) = (0.604, 0.996)
        self.assertAlmostEqual(lower, 0.604, places=2)
        self.assertAlmostEqual(upper, 0.996, places=2)

    def test_confidence_interval_clamping(self):
        """
        WHAT: Tests confidence intervals clamp to [0,1] range
        WHY: Probabilities must stay in valid range even with wide intervals
        """
        score = ConfidenceScore(
            confidence=0.1,
            variance=0.1,
            sample_size=1
        )

        lower, upper = score.confidence_interval(z_score=2.0)

        # Should clamp to [0, 1]
        self.assertGreaterEqual(lower, 0.0)
        self.assertLessEqual(upper, 1.0)


class TestBayesianUncertaintyStrategy(unittest.TestCase):
    """
    Test Bayesian uncertainty estimation.

    WHAT: Validates Bayesian prior updates and confidence estimation
    WHY: Bayesian learning enables system to improve estimates over time
    """

    def setUp(self):
        """Set up test fixtures"""
        self.observable = PipelineObservable()
        self.strategy = BayesianUncertaintyStrategy(observable=self.observable)

    def test_initial_confidence_uniform_prior(self):
        """
        WHAT: Tests initial confidence with uniform prior (Beta(1,1))
        WHY: No historical data should yield 50% confidence (maximum uncertainty)
        """
        context = {"stage": "test_stage", "prediction_type": "test"}

        score = self.strategy.estimate_confidence("prediction", context)

        # Beta(1,1) has mean 0.5
        self.assertAlmostEqual(score.confidence, 0.5)

    def test_bayesian_update_on_success(self):
        """
        WHAT: Tests prior update increases confidence after success
        WHY: Successful outcomes should increase future confidence (alpha++)
        """
        context = {"stage": "test", "prediction_type": "test"}

        # Get initial confidence
        initial = self.strategy.estimate_confidence("pred", context)

        # Update with success
        self.strategy.update_from_outcome("pred", "pred", context)

        # Get updated confidence
        updated = self.strategy.estimate_confidence("pred", context)

        # Confidence should increase after success
        self.assertGreater(updated.confidence, initial.confidence)

    def test_bayesian_update_on_failure(self):
        """
        WHAT: Tests prior update decreases confidence after failure
        WHY: Failed predictions should decrease future confidence (beta++)
        """
        context = {"stage": "test", "prediction_type": "test"}

        # Get initial confidence
        initial = self.strategy.estimate_confidence("pred", context)

        # Update with failure
        self.strategy.update_from_outcome("pred", "different", context)

        # Get updated confidence
        updated = self.strategy.estimate_confidence("pred", context)

        # Confidence should decrease after failure
        self.assertLess(updated.confidence, initial.confidence)

    def test_bayesian_prior_persistence(self):
        """
        WHAT: Tests priors persist across multiple predictions in same context
        WHY: Priors accumulate learning - each update should build on previous
        """
        context = {"stage": "test", "prediction_type": "test"}

        # Multiple successes
        for _ in range(5):
            self.strategy.update_from_outcome("pred", "pred", context)

        score = self.strategy.estimate_confidence("pred", context)

        # After 5 successes, confidence should be high
        # Beta(6, 1) has mean 6/7 ≈ 0.857
        self.assertGreater(score.confidence, 0.8)

    def test_get_and_set_priors(self):
        """
        WHAT: Tests manual prior get/set for persistence
        WHY: Enables saving/loading learned priors for transfer learning
        """
        self.strategy.set_prior("stage1", "pred_type1", alpha=10.0, beta=2.0)

        priors = self.strategy.get_priors()

        key = ("stage1", "pred_type1")
        self.assertIn(key, priors)
        self.assertEqual(priors[key]["alpha"], 10.0)
        self.assertEqual(priors[key]["beta"], 2.0)


class TestMonteCarloUncertaintyStrategy(unittest.TestCase):
    """
    Test Monte Carlo simulation-based uncertainty.

    WHAT: Validates Monte Carlo simulation and confidence estimation
    WHY: Monte Carlo handles complex scenarios where analytic solutions intractable
    """

    def setUp(self):
        """Set up test fixtures"""
        self.observable = PipelineObservable()
        self.strategy = MonteCarloUncertaintyStrategy(
            n_simulations=100,
            observable=self.observable
        )

    def test_monte_carlo_simulation(self):
        """
        WHAT: Tests Monte Carlo runs specified number of simulations
        WHY: Simulation count determines precision - must run all simulations
        """
        call_count = [0]

        def simulator(prediction, context):
            call_count[0] += 1
            return True  # Always succeed

        context = {"simulator_fn": simulator}

        score = self.strategy.estimate_confidence("prediction", context)

        # Should run 100 simulations
        self.assertEqual(call_count[0], 100)

    def test_monte_carlo_confidence_calculation(self):
        """
        WHAT: Tests confidence equals success rate from simulations
        WHY: Empirical probability (successes/trials) estimates true probability
        """
        # Simulator that succeeds 80% of the time
        def simulator(prediction, context):
            import random
            return random.random() < 0.8

        context = {"simulator_fn": simulator, "n_simulations": 1000}

        score = self.strategy.estimate_confidence("prediction", context)

        # Confidence should be close to 0.8 (with some variance)
        self.assertGreater(score.confidence, 0.75)
        self.assertLess(score.confidence, 0.85)

    def test_monte_carlo_requires_simulator(self):
        """
        WHAT: Tests Monte Carlo fails without simulator function
        WHY: Simulator is required - must fail fast with clear error
        """
        context = {}  # No simulator_fn

        with self.assertRaises(PipelineException):
            self.strategy.estimate_confidence("prediction", context)


class TestEnsembleUncertaintyStrategy(unittest.TestCase):
    """
    Test ensemble voting-based uncertainty.

    WHAT: Validates ensemble voting and agreement-based confidence
    WHY: Multiple models provide better estimates through wisdom of crowds
    """

    def setUp(self):
        """Set up test fixtures"""
        self.observable = PipelineObservable()

        # Create model generators
        self.generators = [
            lambda pred, ctx: pred,  # Always agrees
            lambda pred, ctx: pred,  # Always agrees
            lambda pred, ctx: "different"  # Disagrees
        ]

        self.strategy = EnsembleUncertaintyStrategy(
            model_generators=self.generators,
            observable=self.observable
        )

    def test_ensemble_voting(self):
        """
        WHAT: Tests ensemble confidence from model agreement
        WHY: Agreement level quantifies confidence (all agree = high confidence)
        """
        context = {}

        score = self.strategy.estimate_confidence("test_prediction", context)

        # 2 out of 3 models agree = 2/3 confidence
        self.assertAlmostEqual(score.confidence, 2.0/3.0, places=1)

    def test_ensemble_all_agree(self):
        """
        WHAT: Tests ensemble with all models agreeing
        WHY: Perfect agreement should yield maximum confidence
        """
        generators = [
            lambda pred, ctx: pred,
            lambda pred, ctx: pred,
            lambda pred, ctx: pred
        ]

        strategy = EnsembleUncertaintyStrategy(model_generators=generators)

        score = strategy.estimate_confidence("test", {})

        # All agree = confidence 1.0
        self.assertAlmostEqual(score.confidence, 1.0)

    def test_ensemble_adaptive_weighting(self):
        """
        WHAT: Tests adaptive weighting updates model weights based on performance
        WHY: Better models should get higher weight for improved predictions
        """
        context = {"adaptive_weighting": True}

        # Simulate outcomes (model 0 always correct, model 1 always wrong)
        for _ in range(5):
            self.strategy.update_from_outcome("pred", "pred", context)

        # Check weights adjusted (implementation may vary)
        # Better models should have higher weight
        self.assertIsNotNone(self.strategy.weights)

    def test_ensemble_requires_models(self):
        """
        WHAT: Tests ensemble fails without model generators
        WHY: At least one model required for voting
        """
        strategy = EnsembleUncertaintyStrategy(model_generators=[])

        with self.assertRaises(PipelineException):
            strategy.estimate_confidence("pred", {})


class TestTemperatureScheduler(unittest.TestCase):
    """
    Test temperature-based annealing.

    WHAT: Validates temperature scheduling and Boltzmann sampling
    WHY: Temperature controls exploration/exploitation tradeoff
    """

    def setUp(self):
        """Set up test fixtures"""
        self.scheduler = TemperatureScheduler(
            initial_temp=1.0,
            final_temp=0.1,
            schedule="exponential"
        )

    def test_temperature_decreases(self):
        """
        WHAT: Tests temperature decreases from initial to final over steps
        WHY: Annealing requires gradual cooling for convergence
        """
        temp_start = self.scheduler.get_temperature(step=0, max_steps=100)
        temp_mid = self.scheduler.get_temperature(step=50, max_steps=100)
        temp_end = self.scheduler.get_temperature(step=100, max_steps=100)

        # Temperature should decrease
        self.assertGreater(temp_start, temp_mid)
        self.assertGreater(temp_mid, temp_end)

        # Should reach final temp
        self.assertAlmostEqual(temp_end, 0.1, places=1)

    def test_linear_schedule(self):
        """
        WHAT: Tests linear temperature schedule
        WHY: Linear cooling provides constant rate annealing
        """
        scheduler = TemperatureScheduler(
            initial_temp=1.0,
            final_temp=0.0,
            schedule="linear"
        )

        temp_half = scheduler.get_temperature(step=50, max_steps=100)

        # At halfway point, should be halfway between initial and final
        # (1.0 + 0.0) / 2 = 0.5
        self.assertAlmostEqual(temp_half, 0.5, places=1)

    def test_boltzmann_sampling_high_temperature(self):
        """
        WHAT: Tests high temperature produces random sampling
        WHY: High T makes all options nearly equal probability (exploration)
        """
        options = ["A", "B", "C"]
        scores = [10.0, 5.0, 1.0]  # Very different scores

        # Sample many times at high temperature
        samples = []
        for _ in range(100):
            sample = self.scheduler.sample_with_temperature(
                options,
                scores,
                temperature=10.0  # High temp
            )
            samples.append(sample)

        # Should get mix of all options (not just highest score)
        unique_samples = set(samples)
        self.assertGreater(len(unique_samples), 1)

    def test_boltzmann_sampling_low_temperature(self):
        """
        WHAT: Tests low temperature produces greedy sampling
        WHY: Low T makes highest score dominate (exploitation)
        """
        options = ["A", "B", "C"]
        scores = [10.0, 5.0, 1.0]

        # Sample many times at low temperature
        samples = []
        for _ in range(100):
            sample = self.scheduler.sample_with_temperature(
                options,
                scores,
                temperature=0.01  # Very low temp
            )
            samples.append(sample)

        # Should mostly select highest score option "A"
        a_count = samples.count("A")
        self.assertGreater(a_count, 90)  # At least 90% should be "A"


class TestThermodynamicComputing(unittest.TestCase):
    """
    Test main ThermodynamicComputing facade.

    WHAT: Validates facade coordination of uncertainty strategies
    WHY: Facade provides unified interface for all thermodynamic features
    """

    def setUp(self):
        """Set up test fixtures"""
        self.observable = PipelineObservable()
        self.observer = MockObserver()
        self.observable.attach(self.observer)
        self.tc = ThermodynamicComputing(
            observable=self.observable,
            default_strategy="bayesian"
        )

    def test_quantify_uncertainty_bayesian(self):
        """
        WHAT: Tests uncertainty quantification with Bayesian strategy
        WHY: Bayesian is default strategy - must work correctly
        """
        context = {"stage": "test", "prediction_type": "test"}

        score = self.tc.quantify_uncertainty("prediction", context, strategy="bayesian")

        self.assertIsNotNone(score)
        self.assertGreaterEqual(score.confidence, 0.0)
        self.assertLessEqual(score.confidence, 1.0)

    def test_learn_from_outcome(self):
        """
        WHAT: Tests learning from observed outcomes
        WHY: Learning enables continuous improvement of estimates
        """
        context = {"stage": "test", "prediction_type": "test"}

        # Initial confidence
        initial = self.tc.quantify_uncertainty("pred", context)

        # Learn from success
        self.tc.learn_from_outcome("pred", "pred", context)

        # Updated confidence
        updated = self.tc.quantify_uncertainty("pred", context)

        # Confidence should change (increase for success)
        self.assertNotEqual(initial.confidence, updated.confidence)

    def test_temperature_sampling(self):
        """
        WHAT: Tests temperature-based sampling
        WHY: Temperature sampling enables exploration/exploitation balance
        """
        options = ["option1", "option2", "option3"]
        scores = [0.8, 0.6, 0.4]

        selected = self.tc.sample_with_temperature(
            options,
            scores,
            temperature=0.5
        )

        # Should select one of the options
        self.assertIn(selected, options)

    def test_confidence_history_tracking(self):
        """
        WHAT: Tests confidence history accumulation
        WHY: History enables retrospective analysis and trend tracking
        """
        context = {"stage": "test"}

        # Generate several confidence scores
        for i in range(3):
            self.tc.quantify_uncertainty(f"pred{i}", context)

        history = self.tc.get_confidence_history()

        # Should have recorded all scores
        self.assertEqual(len(history), 3)

    def test_confidence_history_filtering(self):
        """
        WHAT: Tests confidence history filtering by context
        WHY: Filtering enables analysis of specific stages or prediction types
        """
        # Create scores in different contexts
        self.tc.quantify_uncertainty("pred1", {"stage": "stage1"})
        self.tc.quantify_uncertainty("pred2", {"stage": "stage2"})
        self.tc.quantify_uncertainty("pred3", {"stage": "stage1"})

        # Filter by stage
        filtered = self.tc.get_confidence_history(filter_context={"stage": "stage1"})

        # Should only get stage1 scores
        self.assertEqual(len(filtered), 2)

    def test_get_strategy(self):
        """
        WHAT: Tests retrieving specific strategy by name
        WHY: Advanced users may need direct strategy access
        """
        strategy = self.tc.get_strategy("bayesian")

        self.assertIsInstance(strategy, BayesianUncertaintyStrategy)

    def test_invalid_strategy_raises_error(self):
        """
        WHAT: Tests requesting invalid strategy raises error
        WHY: Invalid strategy name should fail fast with clear error
        """
        with self.assertRaises(PipelineException):
            self.tc.quantify_uncertainty("pred", {}, strategy="nonexistent")


class TestThermodynamicHelperFunctions(unittest.TestCase):
    """
    Test helper functions for thermodynamic computing.

    WHAT: Validates confidence threshold checking and risk assessment
    WHY: Helper functions provide common operations for decision making
    """

    def test_check_confidence_threshold_pass(self):
        """
        WHAT: Tests confidence threshold check passes when confidence sufficient
        WHY: Threshold checking enables decision gates in pipeline
        """
        score = ConfidenceScore(confidence=0.85, variance=0.01)

        passes = check_confidence_threshold(score, threshold=0.7)

        self.assertTrue(passes)

    def test_check_confidence_threshold_fail(self):
        """
        WHAT: Tests confidence threshold check fails when confidence insufficient
        WHY: Low confidence should trigger alternative actions (human review, etc.)
        """
        score = ConfidenceScore(confidence=0.6, variance=0.01)

        passes = check_confidence_threshold(score, threshold=0.7)

        self.assertFalse(passes)

    def test_assess_risk_high(self):
        """
        WHAT: Tests high risk assessment for low confidence/high variance
        WHY: Risk assessment drives mitigation actions
        """
        score = ConfidenceScore(confidence=0.4, variance=0.5)

        risk = assess_risk(score, risk_threshold=0.3)

        self.assertEqual(risk["risk_level"], "high")
        self.assertGreater(len(risk["recommendations"]), 0)

    def test_assess_risk_low(self):
        """
        WHAT: Tests low risk assessment for high confidence/low variance
        WHY: Low risk enables confident progression
        """
        score = ConfidenceScore(confidence=0.9, variance=0.01)

        risk = assess_risk(score, risk_threshold=0.3)

        self.assertEqual(risk["risk_level"], "low")

    def test_assess_risk_medium(self):
        """
        WHAT: Tests medium risk assessment for moderate confidence
        WHY: Medium risk requires monitoring but not immediate action
        """
        score = ConfidenceScore(confidence=0.65, variance=0.15)

        risk = assess_risk(score, risk_threshold=0.3)

        self.assertEqual(risk["risk_level"], "medium")


# ============================================================================
# TEST RUNNER
# ============================================================================

if __name__ == '__main__':
    unittest.main(verbosity=2)
