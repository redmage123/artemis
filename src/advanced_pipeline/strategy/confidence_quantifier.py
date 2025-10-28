#!/usr/bin/env python3
"""
Module: confidence_quantifier.py

WHY this module exists:
    Quantifies uncertainty in stage results using thermodynamic computing
    for risk-aware execution.

RESPONSIBILITY:
    - Quantify confidence in stage results
    - Track uncertainty across pipeline execution
    - Integrate with thermodynamic computing system

PATTERNS:
    - Adapter Pattern for thermodynamic computing integration
    - Guard clauses for optional feature
"""

from typing import Dict, Any, Optional
from artemis_stage_interface import PipelineStage
from artemis_services import PipelineLogger
from thermodynamic_computing import ThermodynamicComputing, ConfidenceScore


class ConfidenceQuantifier:
    """
    Quantifies uncertainty in pipeline stage results.

    WHY: Enables risk-aware execution by tracking confidence levels.
    Low confidence can trigger human review, high confidence enables automation.

    RESPONSIBILITY: Quantify and track uncertainty across stages

    PATTERNS: Adapter pattern for thermodynamic computing
    """

    def __init__(
        self,
        thermodynamic: Optional[ThermodynamicComputing] = None,
        verbose: bool = False
    ):
        """
        Initialize confidence quantifier.

        Args:
            thermodynamic: Optional thermodynamic computing instance
            verbose: Enable detailed logging
        """
        self.thermodynamic = thermodynamic
        self.logger = PipelineLogger(verbose=verbose)

    def quantify_stage_confidence(
        self,
        stage: PipelineStage,
        result: Any,
        context: Dict[str, Any]
    ) -> Optional[ConfidenceScore]:
        """
        Quantify uncertainty in stage result.

        WHY: Separates uncertainty quantification from execution logic.
        Enables consistent confidence tracking across all stages.

        Args:
            stage: Pipeline stage
            result: Stage execution result
            context: Execution context

        Returns:
            ConfidenceScore or None if thermodynamic disabled
        """
        # Guard clause: check if thermodynamic enabled
        if not self.thermodynamic:
            return None

        try:
            # Quantify uncertainty using default strategy
            confidence = self.thermodynamic.quantify_uncertainty(
                prediction=result,
                context={
                    **context,
                    "stage": stage.name,
                    "prediction_type": "stage_result"
                }
            )

            return confidence

        except Exception as e:
            self.logger.log(
                f"Failed to quantify confidence for stage {stage.name}: {e}",
                "WARNING"
            )
            return None

    def quantify_from_result(
        self,
        stage_name: str,
        result: Any,
        context: Dict[str, Any]
    ) -> Optional[ConfidenceScore]:
        """
        Quantify confidence from StageResult object.

        WHY: Dynamic pipeline returns StageResult objects instead of
        raw results. Need to extract data for uncertainty quantification.

        Args:
            stage_name: Name of stage
            result: StageResult object
            context: Execution context

        Returns:
            ConfidenceScore or None
        """
        # Guard clause: check if thermodynamic enabled
        if not self.thermodynamic:
            return None

        try:
            # Extract data from StageResult if available
            result_data = result.data if hasattr(result, 'data') else result

            confidence = self.thermodynamic.quantify_uncertainty(
                prediction=result_data,
                context={
                    **context,
                    "stage": stage_name,
                    "prediction_type": "stage_result"
                }
            )

            return confidence

        except Exception as e:
            self.logger.log(
                f"Failed to quantify confidence for stage {stage_name}: {e}",
                "WARNING"
            )
            return None
