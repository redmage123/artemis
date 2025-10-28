"""
Module: thermodynamic/ensemble_strategy.py

WHY: Ensemble-based uncertainty via multiple model voting.
RESPONSIBILITY: Aggregate predictions from multiple models, calculate confidence from agreement.
PATTERNS: Strategy Pattern, Composite Pattern, Guard Clauses.

This module handles:
- Generate predictions from multiple models
- Aggregate via voting (classification) or averaging (regression)
- Calculate confidence from agreement level
- Track model performance for adaptive weighting

EXTRACTED FROM: thermodynamic_computing_original.py (lines 1086-1509, 424 lines)
"""

from typing import Any, Dict, List, Optional, Callable
import math
from collections import Counter

from thermodynamic.uncertainty_strategy import UncertaintyStrategy
from thermodynamic.models import ConfidenceScore
from thermodynamic.events import ThermodynamicEventType
from pipeline_observer import PipelineObservable, PipelineEvent, EventType
from artemis_exceptions import PipelineException, wrap_exception


class EnsembleUncertaintyStrategy(UncertaintyStrategy):
    """
    Ensemble-based uncertainty via multiple model voting.

    Wisdom of crowds: multiple independent models often outperform single model.
    Disagreement between models indicates uncertainty. Agreement indicates confidence.

    Ensemble reduces variance: Average of N models has variance σ²/N
    """

    def __init__(
        self,
        model_generators: List[Callable] = None,
        weights: Optional[List[float]] = None,
        observable: Optional[PipelineObservable] = None
    ):
        """
        Initialize ensemble strategy.

        Args:
            model_generators: List of callables that generate predictions
            weights: Optional weights for each model (default: equal)
            observable: Pipeline observable for events
        """
        self.model_generators = model_generators or []
        self.weights = weights

        # Guard: validate weights match generators
        if self.weights is not None:
            if len(self.weights) != len(self.model_generators):
                raise ValueError(
                    f"Weights length ({len(self.weights)}) must match "
                    f"generators length ({len(self.model_generators)})"
                )

        # Default to equal weighting
        if self.weights is None and self.model_generators:
            self.weights = [1.0 / len(self.model_generators)] * len(self.model_generators)

        self.observable = observable

        # Track model performance for adaptive weighting
        self._model_performance: List[Dict[str, int]] = [
            {"correct": 0, "total": 0} for _ in self.model_generators
        ]

    @wrap_exception(PipelineException, "Ensemble confidence estimation failed")
    def estimate_confidence(
        self,
        prediction: Any,
        context: Dict[str, Any]
    ) -> ConfidenceScore:
        """
        Estimate confidence via ensemble voting.

        Generates predictions from all models, calculates agreement.

        Args:
            prediction: Reference prediction to compare against
            context: Context for model generators

        Returns:
            ConfidenceScore with ensemble statistics
        """
        # Guard: require at least one model
        if not self.model_generators:
            raise PipelineException(
                "Ensemble requires at least one model generator",
                context=context
            )

        # Emit ensemble start event
        self._emit_ensemble_event(
            ThermodynamicEventType.ENSEMBLE_GENERATED,
            context,
            {"n_models": len(self.model_generators)}
        )

        # Generate predictions from all models
        predictions = []
        for i, generator in enumerate(self.model_generators):
            try:
                pred = generator(prediction, context)
                predictions.append(pred)
            except Exception as e:
                # Skip failed model, log but continue
                if self.logger:
                    self.logger.log(f"Model {i} failed: {e}", "WARNING")
                predictions.append(None)

        # Filter out failed predictions
        valid_predictions = [p for p in predictions if p is not None]

        # Guard: require at least one valid prediction
        if not valid_predictions:
            raise PipelineException(
                "All ensemble models failed",
                context=context
            )

        # Calculate agreement with reference prediction
        agreements = [p == prediction for p in valid_predictions]
        agreement_count = sum(agreements)

        # Calculate confidence as agreement percentage
        confidence = agreement_count / len(valid_predictions)

        # Calculate variance (Bernoulli)
        variance = confidence * (1 - confidence)

        # Calculate entropy from prediction distribution
        entropy = self._calculate_distribution_entropy(valid_predictions)

        # Emit voting event
        self._emit_ensemble_event(
            ThermodynamicEventType.ENSEMBLE_VOTED,
            context,
            {
                "confidence": confidence,
                "agreement_count": agreement_count,
                "total_predictions": len(valid_predictions)
            }
        )

        return ConfidenceScore(
            confidence=confidence,
            variance=variance,
            entropy=entropy,
            evidence={
                "agreement_count": agreement_count,
                "total_predictions": len(valid_predictions),
                "method": "ensemble_voting"
            },
            sample_size=len(valid_predictions),
            context=context
        )

    def update_from_outcome(
        self,
        prediction: Any,
        actual: Any,
        context: Dict[str, Any]
    ) -> None:
        """
        Update model performance tracking from outcome.

        Updates performance statistics for each model in ensemble.

        Args:
            prediction: What was predicted
            actual: What actually happened
            context: Context with individual model predictions
        """
        # Guard: check if we have model predictions in context
        model_predictions = context.get("model_predictions", [])
        if not model_predictions:
            return

        # Update each model's performance
        for i, model_pred in enumerate(model_predictions):
            # Guard: check index bounds
            if i >= len(self._model_performance):
                continue

            # Track if this model was correct
            correct = (model_pred == actual)
            self._model_performance[i]["total"] += 1
            if correct:
                self._model_performance[i]["correct"] += 1

        # Optionally update weights based on performance
        if context.get("adaptive_weighting", False):
            self._update_weights_from_performance()

    def _calculate_distribution_entropy(self, predictions: List[Any]) -> float:
        """
        Calculate entropy of prediction distribution.

        Args:
            predictions: List of predictions from models

        Returns:
            Entropy (0 = all agree, higher = more disagreement)
        """
        # Guard: empty predictions
        if not predictions:
            return 0.0

        # Count frequency of each prediction
        counts = Counter(predictions)
        total = len(predictions)

        # Calculate Shannon entropy
        entropy = 0.0
        for count in counts.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)

        # Normalize to [0, 1] range
        max_entropy = math.log2(total) if total > 1 else 1.0
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0

        return normalized_entropy

    def _update_weights_from_performance(self) -> None:
        """Update model weights based on historical performance"""
        # Guard: check if we have performance data
        total_predictions = sum(p["total"] for p in self._model_performance)
        if total_predictions == 0:
            return

        # Calculate accuracy for each model
        accuracies = []
        for perf in self._model_performance:
            if perf["total"] > 0:
                accuracy = perf["correct"] / perf["total"]
            else:
                accuracy = 0.5  # Default for models with no data
            accuracies.append(accuracy)

        # Normalize to weights that sum to 1.0
        total_accuracy = sum(accuracies)
        if total_accuracy > 0:
            self.weights = [acc / total_accuracy for acc in accuracies]

    def _emit_ensemble_event(
        self,
        event_type: ThermodynamicEventType,
        context: Dict[str, Any],
        data: Dict[str, Any]
    ) -> None:
        """Emit ensemble event"""
        # Guard: check if observable configured
        if not self.observable:
            return

        event_data = {
            "thermodynamic_event": event_type.value,
            "strategy": "ensemble",
            **data
        }

        event = PipelineEvent(
            event_type=EventType.STAGE_PROGRESS,
            card_id=context.get("card_id"),
            stage_name=context.get("stage"),
            data=event_data
        )

        self.observable.notify(event)

    def get_model_performance(self) -> List[Dict[str, int]]:
        """Get performance statistics for all models"""
        return self._model_performance.copy()

    def add_model(self, generator: Callable, weight: float = None) -> None:
        """
        Add new model to ensemble.

        Args:
            generator: Callable that generates predictions
            weight: Optional weight for this model
        """
        self.model_generators.append(generator)
        self._model_performance.append({"correct": 0, "total": 0})

        # Update weights
        if weight is not None:
            if self.weights is None:
                self.weights = []
            self.weights.append(weight)
        else:
            # Recalculate equal weights
            n = len(self.model_generators)
            self.weights = [1.0 / n] * n


__all__ = [
    "EnsembleUncertaintyStrategy"
]
