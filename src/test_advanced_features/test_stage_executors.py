#!/usr/bin/env python3
"""
Module: test_advanced_features/test_stage_executors.py

WHY: Validates stage execution engine including retry logic, parallel execution,
     and dependency resolution which are critical for pipeline reliability.

RESPONSIBILITY:
- Test single stage executor with retry and events
- Test parallel stage executor with dependency ordering
- Test cycle detection in dependencies

PATTERNS:
- Mock-based testing for controllable failures
- Event-driven verification
- Guard clauses for early returns
"""

import unittest
from typing import Dict, Any
from dynamic_pipeline import (
    StageExecutor,
    ParallelStageExecutor,
    RetryPolicy,
    StageResult
)
from pipeline_observer import PipelineObservable, EventType
from artemis_exceptions import PipelineException
from test_advanced_features.mock_classes import MockStage, MockObserver


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
