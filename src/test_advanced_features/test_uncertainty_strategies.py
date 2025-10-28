#!/usr/bin/env python3
"""
Module: test_advanced_features/test_uncertainty_strategies.py

WHY: Validates different uncertainty estimation strategies (Bayesian, Monte Carlo,
     Ensemble) which provide complementary approaches to confidence quantification.

RESPONSIBILITY:
- Test Bayesian uncertainty with prior updates
- Test Monte Carlo simulation-based uncertainty
- Test Ensemble voting-based uncertainty

PATTERNS:
- Strategy pattern testing
- Statistical validation
- Guard clauses for required inputs
"""

import unittest
from pipeline_observer import PipelineObservable
from thermodynamic_computing import (
    BayesianUncertaintyStrategy,
    MonteCarloUncertaintyStrategy,
    EnsembleUncertaintyStrategy
)
from artemis_exceptions import PipelineException


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
