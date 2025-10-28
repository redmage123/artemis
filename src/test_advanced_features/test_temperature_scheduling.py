#!/usr/bin/env python3
"""
Module: test_advanced_features/test_temperature_scheduling.py

WHY: Validates temperature-based annealing and Boltzmann sampling which control
     exploration/exploitation tradeoff in decision making.

RESPONSIBILITY:
- Test temperature schedule (exponential, linear)
- Test Boltzmann sampling at different temperatures
- Test annealing behavior

PATTERNS:
- Statistical testing with sampling
- Boundary value testing
- Guard clauses for valid temperatures
"""

import unittest
from thermodynamic_computing import TemperatureScheduler


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
