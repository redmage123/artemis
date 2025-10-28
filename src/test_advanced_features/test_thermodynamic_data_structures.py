#!/usr/bin/env python3
"""
Module: test_advanced_features/test_thermodynamic_data_structures.py

WHY: Validates ConfidenceScore data structure and calculations which are
     fundamental to uncertainty quantification.

RESPONSIBILITY:
- Test ConfidenceScore creation and validation
- Test standard error calculation
- Test confidence interval calculation

PATTERNS:
- Mathematical validation testing
- Boundary value testing
- Guard clauses for probability validation
"""

import unittest
from thermodynamic_computing import ConfidenceScore


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
