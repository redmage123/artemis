#!/usr/bin/env python3
"""
Module: test_advanced_features/test_thermodynamic_computing.py

WHY: Validates ThermodynamicComputing facade and helper functions which provide
     unified interface for uncertainty quantification and risk assessment.

RESPONSIBILITY:
- Test ThermodynamicComputing facade operations
- Test confidence history tracking
- Test helper functions (threshold checking, risk assessment)

PATTERNS:
- Facade pattern testing
- History tracking validation
- Guard clauses for decision logic
"""

import unittest
from pipeline_observer import PipelineObservable
from thermodynamic_computing import (
    ThermodynamicComputing,
    BayesianUncertaintyStrategy,
    ConfidenceScore,
    check_confidence_threshold,
    assess_risk
)
from artemis_exceptions import PipelineException
from test_advanced_features.mock_classes import MockObserver


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
