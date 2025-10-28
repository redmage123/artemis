#!/usr/bin/env python3
"""
Module: test_advanced_features/test_dynamic_pipeline.py

WHY: Validates complete dynamic pipeline orchestration including execution,
     state management, and runtime modification.

RESPONSIBILITY:
- Test pipeline execution (success and failure paths)
- Test state validation and transitions
- Test runtime stage modification

PATTERNS:
- State machine testing
- Guard clauses for state validation
- Event-driven verification
"""

import unittest
from dynamic_pipeline import (
    DynamicPipelineBuilder,
    DynamicPipelineFactory,
    PipelineState,
    ProjectComplexity
)
from pipeline_observer import PipelineObservable
from artemis_exceptions import PipelineException
from test_advanced_features.mock_classes import MockStage, MockObserver


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
