"""
Module: thermodynamic/temperature_scheduler.py

WHY: Temperature-based annealing for exploration/exploitation tradeoff.
RESPONSIBILITY: Schedule temperature for simulated annealing, control exploration vs exploitation.
PATTERNS: Strategy Pattern (different schedules), Guard Clauses.

This module handles:
- Temperature scheduling (linear, exponential, cosine annealing)
- Boltzmann sampling with temperature
- Exploration/exploitation tradeoff control
- Temperature-based option selection

EXTRACTED FROM: thermodynamic_computing_original.py (lines 1510-1800, 291 lines)
"""

from typing import List, Any, Optional
import math
import random


class TemperatureScheduler:
    """
    Temperature-based annealing for exploration/exploitation tradeoff.

    Thermodynamic interpretation:
    - High T: System in high-energy state, random exploration
    - Low T: System in low-energy state, deterministic exploitation
    - Annealing: Gradual cooling to find global minimum
    """

    def __init__(
        self,
        initial_temp: float = 1.0,
        final_temp: float = 0.01,
        schedule_type: str = "exponential"
    ):
        """
        Initialize temperature scheduler.

        Args:
            initial_temp: Starting temperature (high = more exploration)
            final_temp: Ending temperature (low = more exploitation)
            schedule_type: Annealing schedule ("linear", "exponential", "cosine")
        """
        self.initial_temp = initial_temp
        self.final_temp = final_temp
        self.schedule_type = schedule_type

    def get_temperature(self, step: int, max_steps: int) -> float:
        """
        Get temperature at given step in schedule.

        Args:
            step: Current step number (0 to max_steps-1)
            max_steps: Total number of steps

        Returns:
            Temperature value for this step
        """
        # Guard: validate step bounds
        if step < 0:
            return self.initial_temp
        if step >= max_steps:
            return self.final_temp

        # Progress through schedule (0.0 to 1.0)
        progress = step / max_steps

        # Dispatch table for schedule types
        schedules = {
            "linear": self._linear_schedule,
            "exponential": self._exponential_schedule,
            "cosine": self._cosine_schedule
        }

        # Get schedule function, default to exponential
        schedule_fn = schedules.get(self.schedule_type, self._exponential_schedule)

        return schedule_fn(progress)

    def _linear_schedule(self, progress: float) -> float:
        """Linear temperature decay"""
        return self.initial_temp * (1.0 - progress) + self.final_temp * progress

    def _exponential_schedule(self, progress: float) -> float:
        """Exponential temperature decay (faster cooling)"""
        return self.initial_temp * math.exp(-5.0 * progress)

    def _cosine_schedule(self, progress: float) -> float:
        """Cosine annealing (smooth decay with periodic warmups)"""
        cos_inner = math.pi * progress
        return self.final_temp + (self.initial_temp - self.final_temp) * \
               0.5 * (1.0 + math.cos(cos_inner))

    def sample_with_temperature(
        self,
        options: List[Any],
        scores: List[float],
        temperature: float
    ) -> Any:
        """
        Sample option using Boltzmann distribution with temperature.

        Uses temperature to control randomness:
        - High T: Nearly uniform sampling (exploration)
        - Low T: Strongly favor high scores (exploitation)

        Formula: P(option_i) ∝ exp(score_i / T)

        Args:
            options: List of options to choose from
            scores: Scores for each option (higher = better)
            temperature: Current temperature

        Returns:
            Selected option
        """
        # Guard: validate inputs
        if not options:
            raise ValueError("Options list cannot be empty")
        if len(options) != len(scores):
            raise ValueError(f"Options ({len(options)}) and scores ({len(scores)}) length mismatch")

        # Guard: single option
        if len(options) == 1:
            return options[0]

        # Calculate Boltzmann probabilities
        # P(i) ∝ exp(score_i / T)
        exp_scores = [math.exp(score / max(temperature, 0.01)) for score in scores]
        total = sum(exp_scores)

        # Normalize to probabilities
        probabilities = [exp_score / total for exp_score in exp_scores]

        # Sample from distribution
        return random.choices(options, weights=probabilities, k=1)[0]

    def anneal_step(
        self,
        options: List[Any],
        scores: List[float],
        step: int,
        max_steps: int
    ) -> Any:
        """
        Perform one annealing step with automatic temperature scheduling.

        Convenience method that combines get_temperature() and sample_with_temperature().

        Args:
            options: List of options
            scores: Scores for each option
            step: Current step number
            max_steps: Total steps

        Returns:
            Selected option at current temperature
        """
        temperature = self.get_temperature(step, max_steps)
        return self.sample_with_temperature(options, scores, temperature)


__all__ = [
    "TemperatureScheduler"
]
