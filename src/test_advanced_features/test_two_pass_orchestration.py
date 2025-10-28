#!/usr/bin/env python3
"""
Module: test_advanced_features/test_two_pass_orchestration.py

WHY: Validates two-pass pipeline orchestration including comparison, rollback,
     and complete end-to-end execution flows.

RESPONSIBILITY:
- Test pass comparison and delta generation
- Test rollback manager and automatic rollback
- Test complete two-pass pipeline execution
- Test factory methods

PATTERNS:
- Integration testing
- State machine validation
- Guard clauses for decision logic
"""

import unittest
from pipeline_observer import PipelineObservable
from two_pass_pipeline import (
    TwoPassPipeline,
    TwoPassPipelineFactory,
    FirstPassStrategy,
    SecondPassStrategy,
    PassResult,
    PassDelta,
    PassMemento,
    PassComparator,
    RollbackManager
)
from test_advanced_features.mock_classes import MockObserver


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
