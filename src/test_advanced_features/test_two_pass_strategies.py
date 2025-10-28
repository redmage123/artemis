#!/usr/bin/env python3
"""
Module: test_advanced_features/test_two_pass_strategies.py

WHY: Validates first and second pass execution strategies to ensure proper
     learning extraction and application between passes.

RESPONSIBILITY:
- Test first pass execution and learning extraction
- Test second pass execution with learning application
- Test quality score calculation

PATTERNS:
- Strategy pattern testing
- Learning transfer validation
- Guard clauses for context validation
"""

import unittest
from pipeline_observer import PipelineObservable
from two_pass_pipeline import FirstPassStrategy, SecondPassStrategy
from test_advanced_features.mock_classes import MockObserver


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
