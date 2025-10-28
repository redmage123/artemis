#!/usr/bin/env python3
"""
WHY: Provide backward-compatible ValidationPipeline interface.

RESPONSIBILITY: Wrap new modular validators with original API for seamless
backward compatibility.

PATTERNS:
- Facade pattern to hide modular complexity
- Adapter pattern for API compatibility
- Delegation to modular components
"""

from typing import Dict, List, Optional, Tuple, Any

from .models import ValidationStage, StageValidationResult, ValidationContext
from .pipeline_executor import PipelineExecutor
from .result_aggregator import ResultAggregator


class ValidationPipeline:
    """
    WHY: Backward-compatible facade for validation pipeline.

    RESPONSIBILITY: Maintain original ValidationPipeline API while delegating
    to new modular components.

    This class provides the same interface as the original validation_pipeline.py
    file, ensuring existing code continues to work without modification.

    Usage:
        pipeline = ValidationPipeline(llm_client=llm, logger=logger)
        result = pipeline.validate_stage(code, ValidationStage.IMPORTS)

        if not result.passed:
            feedback = pipeline.get_regeneration_prompt(result)
    """

    def __init__(
        self,
        llm_client: Optional[Any] = None,
        logger: Optional[Any] = None,
        strict_mode: bool = True
    ):
        """
        WHY: Initialize pipeline with same signature as original.

        Args:
            llm_client: LLM client for regeneration (optional)
            logger: ArtemisLogger instance
            strict_mode: If True, fail on any error; if False, allow warnings
        """
        # Delegate to modular components
        self.executor = PipelineExecutor(
            llm_client=llm_client,
            logger=logger,
            strict_mode=strict_mode
        )
        self.aggregator = ResultAggregator()

        # Maintain original attributes for compatibility
        self.llm_client = llm_client
        self.logger = logger
        self.strict_mode = strict_mode
        self.validation_history: List[StageValidationResult] = []

    def validate_stage(
        self,
        code: str,
        stage: ValidationStage,
        context: Optional[Dict] = None
    ) -> StageValidationResult:
        """
        WHY: Validate code at specific stage (original API).

        Args:
            code: Current generated code
            stage: Which stage we're validating
            context: Additional context (task requirements, imports needed, etc.)

        Returns:
            StageValidationResult with pass/fail and specific feedback
        """
        # Delegate to executor
        result = self.executor.validate_stage(code, stage, context)

        # Maintain history for compatibility
        self.validation_history = self.executor.validation_history

        # Track in aggregator
        self.aggregator.add_result(result)

        return result

    def get_regeneration_prompt(self, result: StageValidationResult) -> str:
        """
        WHY: Generate prompt for LLM regeneration (original API).

        Args:
            result: Failed validation result

        Returns:
            Prompt string to send to LLM
        """
        return self.executor.get_regeneration_prompt(result)

    def generate_with_validation(
        self,
        task: str,
        stages: List[ValidationStage],
        max_retries: int = 2
    ) -> Tuple[str, bool]:
        """
        WHY: Generate code with continuous validation (original API).

        Args:
            task: Task description for the LLM
            stages: Stages to validate (in order)
            max_retries: Max retries per stage

        Returns:
            Tuple of (generated_code, success)
        """
        code, success = self.executor.generate_with_validation(
            task, stages, max_retries
        )

        # Sync history
        self.validation_history = self.executor.validation_history

        return code, success

    def get_validation_summary(self) -> Dict:
        """
        WHY: Get validation summary (original API).

        Returns:
            Dictionary with validation statistics
        """
        summary = self.aggregator.get_summary()

        # Convert to original format
        return {
            'total_validations': summary.total_validations,
            'passed': summary.passed,
            'failed': summary.failed,
            'pass_rate': summary.pass_rate,
            'by_stage': summary.by_stage,
            'history': summary.history
        }

    def reset(self) -> None:
        """
        WHY: Clear validation history (original API).

        Resets both executor and aggregator state.
        """
        self.executor.reset()
        self.aggregator.clear()
        self.validation_history = []


# Convenience functions (original API)

def validate_python_code(code: str, strict: bool = True) -> StageValidationResult:
    """
    WHY: Quick validation of Python code (original API).

    Args:
        code: Python code to validate
        strict: If True, fail on any issue

    Returns:
        Validation result
    """
    pipeline = ValidationPipeline(strict_mode=strict)
    return pipeline.validate_stage(code, ValidationStage.FULL_CODE)


def validate_incrementally(
    code_segments: List[Tuple[str, ValidationStage]],
    strict: bool = True
) -> List[StageValidationResult]:
    """
    WHY: Validate code incrementally through multiple stages (original API).

    Args:
        code_segments: List of (code, stage) tuples
        strict: If True, fail on any issue

    Returns:
        List of validation results
    """
    pipeline = ValidationPipeline(strict_mode=strict)
    results = []

    for code, stage in code_segments:
        result = pipeline.validate_stage(code, stage)
        results.append(result)

        # Guard: Stop on first failure in strict mode
        if not result.passed and strict:
            break

    return results
